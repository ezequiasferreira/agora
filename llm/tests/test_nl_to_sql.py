import os
import sys

import pytest
from dotenv import load_dotenv


# ============================================================
# AJUSTE DE CAMINHO PARA IMPORTAR O MÓDULO LLM
# ============================================================

DIRETORIO_LLM = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
    )
)

sys.path.insert(0, DIRETORIO_LLM)


# ============================================================
# IMPORTAÇÕES DO ÁGORA
# ============================================================

from providers import OpenAILLM, GeminiLLM
from translator import TradutorNL2SQL


# ============================================================
# CONFIGURAÇÃO DO AMBIENTE
# ============================================================

CAMINHO_ENV = os.path.join(
    DIRETORIO_LLM,
    ".env",
)

load_dotenv(CAMINHO_ENV)

LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "openai",
).strip().lower()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna",
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash",
)


# ============================================================
# FIXTURE DO PROVEDOR
# ============================================================

@pytest.fixture(scope="module")
def tradutor():
    """
    Inicializa o tradutor uma única vez para todos os testes.

    O provedor padrão do MVP é OpenAI.

    Gemini pode ser utilizado como alternativa através de:

    LLM_PROVIDER=gemini
    """

    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            pytest.skip(
                "OPENAI_API_KEY não encontrada. "
                "Pulando testes com OpenAI."
            )

        llm = OpenAILLM(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
        )

    elif LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            pytest.skip(
                "GEMINI_API_KEY não encontrada. "
                "Pulando testes com Gemini."
            )

        llm = GeminiLLM(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
        )

    else:
        pytest.fail(
            f"LLM_PROVIDER inválido: {LLM_PROVIDER}. "
            "Utilize 'openai' ou 'gemini'."
        )

    return TradutorNL2SQL(
        llm_provider=llm
    )


# ============================================================
# TESTE 1 — CONTAGEM SIMPLES
# ============================================================

def test_deve_retornar_query_para_contagem_simples(
    tradutor,
):
    pergunta = (
        "Quantos registros de remuneração existem "
        "em janeiro de 2025?"
    )

    resultado = tradutor.processar_pergunta(
        pergunta
    )

    assert resultado.get("status") == "QUERY", (
        f"Esperado QUERY, mas retornou {resultado}"
    )

    assert "sql" in resultado, (
        "A chave 'sql' está faltando na resposta."
    )

    assert "SELECT" in resultado.get(
        "sql",
        "",
    ).upper(), (
        "O SQL gerado é inválido."
    )


# ============================================================
# TESTE 2 — AGREGAÇÃO
# ============================================================

def test_deve_retornar_query_para_agregacao(
    tradutor,
):
    pergunta = (
        "Qual foi o total de rendimento líquido "
        "em junho de 2025?"
    )

    resultado = tradutor.processar_pergunta(
        pergunta
    )

    assert resultado.get("status") == "QUERY", (
        f"Esperado QUERY, mas retornou {resultado}"
    )

    assert resultado.get("sql"), (
        "Esperado SQL para consulta de agregação."
    )


# ============================================================
# TESTE 3 — LIMITAÇÃO SEMÂNTICA DO CATÁLOGO
# ============================================================

def test_deve_retornar_not_answerable_quando_catalogo_nao_informa_dominio(
    tradutor,
):
    """
    O catálogo estrutural atual informa a existência da coluna
    grau_jurisdicao, mas não informa os valores existentes nela.

    Portanto, a LLM não deve inventar quais valores representam
    unidades judiciárias de primeiro e segundo graus.

    Quando o catálogo passar a fornecer distinct_values ou outro
    enriquecimento semântico equivalente, este teste deverá ser
    revisado para esperar QUERY.
    """

    pergunta = (
        "Quantos servidores pertencem às unidades "
        "judiciárias de primeiro e segundo graus?"
    )

    resultado = tradutor.processar_pergunta(
        pergunta
    )

    assert resultado.get(
        "status"
    ) == "NOT_ANSWERABLE", (
        f"Esperado NOT_ANSWERABLE, "
        f"mas retornou {resultado}"
    )

    assert resultado.get("sql") is None, (
        "A consulta não deve gerar SQL enquanto os valores "
        "de domínio não estiverem disponíveis no catálogo."
    )

    assert resultado.get("message") is not None, (
        "A resposta deve explicar a limitação dos dados."
    )


# ============================================================
# TESTE 4 — INFORMAÇÃO INEXISTENTE
# ============================================================

def test_deve_retornar_not_answerable_para_limitacao_de_dados(
    tradutor,
):
    pergunta = (
        "Qual é a formação acadêmica dos servidores?"
    )

    resultado = tradutor.processar_pergunta(
        pergunta
    )

    assert resultado.get(
        "status"
    ) == "NOT_ANSWERABLE", (
        f"Esperado NOT_ANSWERABLE, "
        f"mas retornou {resultado}"
    )

    assert resultado.get("message") is not None, (
        "A mensagem explicativa está faltando."
    )

    assert resultado.get("sql") is None, (
        "NOT_ANSWERABLE não deve gerar SQL."
    )


# ============================================================
# TESTE 5 — AMBIGUIDADE
# ============================================================

def test_deve_retornar_needs_clarification_para_ambiguidade(
    tradutor,
):
    pergunta = (
        "Qual foi a maior remuneração?"
    )

    resultado = tradutor.processar_pergunta(
        pergunta
    )

    assert resultado.get(
        "status"
    ) == "NEEDS_CLARIFICATION", (
        f"Esperado NEEDS_CLARIFICATION, "
        f"mas retornou {resultado}"
    )

    assert resultado.get("message") is not None, (
        "A mensagem de esclarecimento está faltando."
    )

    assert resultado.get("sql") is None, (
        "NEEDS_CLARIFICATION não deve gerar SQL."
    )
