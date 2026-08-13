import os
import sys

import pytest
from dotenv import load_dotenv


# ============================================================
# AJUSTE DE CAMINHO
# ============================================================

DIRETORIO_RAIZ = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

DIRETORIO_LLM = os.path.join(
    DIRETORIO_RAIZ,
    "llm",
)

sys.path.insert(
    0,
    DIRETORIO_LLM,
)


# ============================================================
# IMPORTAÇÕES DO ÁGORA
# ============================================================

from providers import OpenAILLM, GeminiLLM
from translator import TradutorNL2SQL
from api_client import executar_sql_na_api
from responder import Respondedor


# ============================================================
# CONFIGURAÇÃO DO AMBIENTE
# ============================================================

CAMINHO_ENV_LLM = os.path.join(
    DIRETORIO_LLM,
    ".env",
)

load_dotenv(
    CAMINHO_ENV_LLM
)

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "openai",
).strip().lower()

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna",
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash",
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture(scope="module")
def provedor():
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            pytest.skip(
                "OPENAI_API_KEY não encontrada."
            )

        return OpenAILLM(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
        )

    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            pytest.skip(
                "GEMINI_API_KEY não encontrada."
            )

        return GeminiLLM(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
        )

    pytest.fail(
        f"LLM_PROVIDER inválido: {LLM_PROVIDER}"
    )


@pytest.fixture(scope="module")
def tradutor(provedor):
    return TradutorNL2SQL(
        llm_provider=provedor
    )


@pytest.fixture(scope="module")
def respondedor(provedor):
    return Respondedor(
        llm_provider=provedor
    )


# ============================================================
# TESTE END-TO-END
# ============================================================

def test_fluxo_completo_contagem_remuneracoes_janeiro(
    tradutor,
    respondedor,
):
    pergunta = (
        "Quantos registros de remuneração existem "
        "em janeiro de 2025?"
    )

    # --------------------------------------------------------
    # 1. LINGUAGEM NATURAL → SQL
    # --------------------------------------------------------

    resultado_llm = tradutor.processar_pergunta(
        pergunta
    )

    assert resultado_llm.get(
        "status"
    ) == "QUERY", (
        f"Esperado QUERY, "
        f"mas retornou {resultado_llm}"
    )

    sql_gerado = resultado_llm.get(
        "sql"
    )

    assert sql_gerado, (
        "A LLM não gerou SQL."
    )

    # --------------------------------------------------------
    # 2. SQL → API → POSTGRESQL
    # --------------------------------------------------------

    resposta_api = executar_sql_na_api(
        sql_gerado
    )

    assert resposta_api.get(
        "success"
    ) is True, (
        f"A API falhou: {resposta_api}"
    )

    assert resposta_api.get(
        "columns"
    ) == ["count"], (
        "A consulta deveria retornar "
        "uma coluna de contagem."
    )

    assert resposta_api.get(
        "rows"
    ) == [[1338]], (
        "A quantidade esperada para "
        "janeiro de 2025 é 1338."
    )

    # --------------------------------------------------------
    # 3. RESULTADO → RESPOSTA NATURAL
    # --------------------------------------------------------

    resposta_final = (
        respondedor.gerar_resposta(
            pergunta=pergunta,
            resposta_api=resposta_api,
        )
    )

    assert resposta_final.get(
        "status"
    ) == "ANSWER", (
        f"Esperado ANSWER, "
        f"mas retornou {resposta_final}"
    )

    mensagem = resposta_final.get(
        "message",
        "",
    )

    assert mensagem, (
        "A resposta final não possui mensagem."
    )

    assert "1338" in mensagem.replace(
        ".",
        "",
    ), (
        "A resposta final deve informar "
        "a quantidade de 1338 registros."
    )
