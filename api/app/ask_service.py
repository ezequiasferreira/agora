import os
import sys

import psycopg2
from dotenv import load_dotenv

from app import db
from app.query_validator import (
    QueryValidationError,
    validar_sql,
)


# ============================================================
# CAMINHOS DO PROJETO
# ============================================================

DIRETORIO_APP = os.path.dirname(
    os.path.abspath(__file__)
)

DIRETORIO_API = os.path.dirname(
    DIRETORIO_APP
)

DIRETORIO_RAIZ = os.path.dirname(
    DIRETORIO_API
)

DIRETORIO_LLM = os.path.join(
    DIRETORIO_RAIZ,
    "llm",
)

if DIRETORIO_LLM not in sys.path:
    sys.path.insert(
        0,
        DIRETORIO_LLM,
    )


# ============================================================
# IMPORTAÇÕES DO MÓDULO LLM
# ============================================================

from providers import OpenAILLM, GeminiLLM
from translator import TradutorNL2SQL
from responder import Respondedor


# ============================================================
# CONFIGURAÇÃO DO LLM
# ============================================================

CAMINHO_ENV_LLM = os.path.join(
    DIRETORIO_LLM,
    ".env",
)

load_dotenv(
    CAMINHO_ENV_LLM,
    override=False,
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
# CONFIGURAÇÃO DE CUSTOS
# ============================================================

OPENAI_INPUT_COST_PER_1M = float(
    os.getenv(
        "OPENAI_INPUT_COST_PER_1M",
        "0",
    )
)

OPENAI_CACHED_INPUT_COST_PER_1M = float(
    os.getenv(
        "OPENAI_CACHED_INPUT_COST_PER_1M",
        "0",
    )
)

OPENAI_OUTPUT_COST_PER_1M = float(
    os.getenv(
        "OPENAI_OUTPUT_COST_PER_1M",
        "0",
    )
)


# ============================================================
# INSTÂNCIAS REUTILIZÁVEIS
# ============================================================

_provedor = None
_tradutor = None
_respondedor = None


def _criar_provedor():
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY não encontrada "
                "no arquivo llm/.env."
            )

        return OpenAILLM(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
        )

    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY não encontrada "
                "no arquivo llm/.env."
            )

        return GeminiLLM(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
        )

    raise RuntimeError(
        f"LLM_PROVIDER inválido: {LLM_PROVIDER}. "
        "Utilize 'openai' ou 'gemini'."
    )


def _obter_componentes():
    global _provedor
    global _tradutor
    global _respondedor

    if _provedor is None:
        _provedor = _criar_provedor()

    if _tradutor is None:
        _tradutor = TradutorNL2SQL(
            llm_provider=_provedor
        )

    if _respondedor is None:
        _respondedor = Respondedor(
            llm_provider=_provedor
        )

    return (
        _provedor,
        _tradutor,
        _respondedor,
    )


# ============================================================
# USO DE TOKENS
# ============================================================

def _uso_vazio() -> dict:
    return {
        "model": None,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "total_tokens": 0,
    }


def _normalizar_uso(
    uso: dict | None,
) -> dict:
    if not uso:
        return _uso_vazio()

    return {
        "model": uso.get("model"),
        "input_tokens": uso.get(
            "input_tokens",
            0,
        ),
        "cached_input_tokens": uso.get(
            "cached_input_tokens",
            0,
        ),
        "output_tokens": uso.get(
            "output_tokens",
            0,
        ),
        "reasoning_tokens": uso.get(
            "reasoning_tokens",
            0,
        ),
        "total_tokens": uso.get(
            "total_tokens",
            0,
        ),
    }


def _calcular_custo_openai(
    uso: dict,
) -> dict:
    """
    Calcula o custo estimado da chamada em dólares.

    Tokens de entrada em cache são descontados
    do total de entrada normal para evitar
    cobrança duplicada.
    """

    input_tokens = uso.get(
        "input_tokens",
        0,
    )

    cached_input_tokens = uso.get(
        "cached_input_tokens",
        0,
    )

    output_tokens = uso.get(
        "output_tokens",
        0,
    )

    input_tokens_nao_cacheados = max(
        input_tokens - cached_input_tokens,
        0,
    )

    custo_input = (
        input_tokens_nao_cacheados
        / 1_000_000
        * OPENAI_INPUT_COST_PER_1M
    )

    custo_input_cacheado = (
        cached_input_tokens
        / 1_000_000
        * OPENAI_CACHED_INPUT_COST_PER_1M
    )

    custo_output = (
        output_tokens
        / 1_000_000
        * OPENAI_OUTPUT_COST_PER_1M
    )

    custo_total = (
        custo_input
        + custo_input_cacheado
        + custo_output
    )

    return {
        "currency": "USD",
        "input_cost_usd": round(
            custo_input,
            8,
        ),
        "cached_input_cost_usd": round(
            custo_input_cacheado,
            8,
        ),
        "output_cost_usd": round(
            custo_output,
            8,
        ),
        "total_cost_usd": round(
            custo_total,
            8,
        ),
    }


def _calcular_custo(
    uso: dict,
) -> dict | None:
    if LLM_PROVIDER == "openai":
        return _calcular_custo_openai(
            uso
        )

    return None


def _somar_usos(
    uso_sql: dict | None,
    uso_resposta: dict | None,
) -> dict:
    uso_sql = _normalizar_uso(
        uso_sql
    )

    uso_resposta = _normalizar_uso(
        uso_resposta
    )

    modelo = (
        uso_resposta.get("model")
        or uso_sql.get("model")
    )

    uso_total = {
        "model": modelo,
        "input_tokens": (
            uso_sql["input_tokens"]
            + uso_resposta["input_tokens"]
        ),
        "cached_input_tokens": (
            uso_sql["cached_input_tokens"]
            + uso_resposta["cached_input_tokens"]
        ),
        "output_tokens": (
            uso_sql["output_tokens"]
            + uso_resposta["output_tokens"]
        ),
        "reasoning_tokens": (
            uso_sql["reasoning_tokens"]
            + uso_resposta["reasoning_tokens"]
        ),
        "total_tokens": (
            uso_sql["total_tokens"]
            + uso_resposta["total_tokens"]
        ),
        "steps": {
            "sql_generation": uso_sql,
            "final_answer": uso_resposta,
        },
    }

    uso_total["cost"] = _calcular_custo(
        uso_total
    )

    return uso_total


# ============================================================
# ORQUESTRAÇÃO DA PERGUNTA
# ============================================================

def processar_pergunta(
    pergunta: str,
) -> dict:
    """
    Executa o fluxo completo do Ágora.
    """

    provedor, tradutor, respondedor = (
        _obter_componentes()
    )

    # --------------------------------------------------------
    # 1. LINGUAGEM NATURAL → SQL
    # --------------------------------------------------------

    resultado_llm = (
        tradutor.processar_pergunta(
            pergunta
        )
    )

    uso_sql = provedor.obter_ultimo_uso()

    status_llm = resultado_llm.get(
        "status"
    )

    # --------------------------------------------------------
    # 2. PERGUNTA NÃO RESPONDÍVEL
    # --------------------------------------------------------

    if status_llm == "NOT_ANSWERABLE":
        return {
            "success": True,
            "status": "NOT_ANSWERABLE",
            "answer": resultado_llm.get(
                "message"
            ),
            "usage": _somar_usos(
                uso_sql,
                None,
            ),
        }

    # --------------------------------------------------------
    # 3. PERGUNTA AMBÍGUA
    # --------------------------------------------------------

    if status_llm == "NEEDS_CLARIFICATION":
        return {
            "success": True,
            "status": "NEEDS_CLARIFICATION",
            "answer": resultado_llm.get(
                "message"
            ),
            "usage": _somar_usos(
                uso_sql,
                None,
            ),
        }

    # --------------------------------------------------------
    # 4. ERROS DO LLM
    # --------------------------------------------------------

    if status_llm in {
        "PROVIDER_ERROR",
        "FORMAT_ERROR",
    }:
        return {
            "success": False,
            "status": status_llm,
            "answer": resultado_llm.get(
                "message"
            ),
            "usage": _somar_usos(
                uso_sql,
                None,
            ),
        }

    if status_llm != "QUERY":
        return {
            "success": False,
            "status": "INTERNAL_ERROR",
            "answer": (
                "O Ágora recebeu um estado "
                "não reconhecido do módulo de IA."
            ),
            "usage": _somar_usos(
                uso_sql,
                None,
            ),
        }

    sql_gerado = resultado_llm.get(
        "sql"
    )

    if not sql_gerado:
        return {
            "success": False,
            "status": "FORMAT_ERROR",
            "answer": (
                "O módulo de IA não gerou "
                "uma consulta válida."
            ),
            "usage": _somar_usos(
                uso_sql,
                None,
            ),
        }

    # --------------------------------------------------------
    # 5. VALIDAÇÃO SEGURA DO SQL
    # --------------------------------------------------------

    try:
        sql_validado = validar_sql(
            sql_gerado
        )

    except QueryValidationError as erro:
        return {
            "success": False,
            "status": erro.error_type,
            "answer": erro.message,
            "generated_sql": sql_gerado,
            "usage": _somar_usos(
                uso_sql,
                None,
            ),
        }

    # --------------------------------------------------------
    # 6. EXECUÇÃO NO POSTGRESQL
    # --------------------------------------------------------

    try:
        colunas, linhas, duracao = (
            db.executar_consulta(
                sql_validado
            )
        )

    except psycopg2.Error as erro:
        texto_erro = str(erro)

        if (
            "canceling statement due to "
            "statement timeout"
        ) in texto_erro:
            return {
                "success": False,
                "status": "QUERY_TIMEOUT",
                "answer": (
                    "A consulta excedeu o tempo "
                    "máximo de execução."
                ),
                "generated_sql": sql_validado,
                "usage": _somar_usos(
                    uso_sql,
                    None,
                ),
            }

        return {
            "success": False,
            "status": "DB_QUERY_ERROR",
            "answer": (
                "Não foi possível executar "
                "a consulta nos dados."
            ),
            "generated_sql": sql_validado,
            "usage": _somar_usos(
                uso_sql,
                None,
            ),
        }

    except Exception:
        return {
            "success": False,
            "status": "INTERNAL_ERROR",
            "answer": (
                "Ocorreu um erro interno ao "
                "processar a consulta."
            ),
            "generated_sql": sql_validado,
            "usage": _somar_usos(
                uso_sql,
                None,
            ),
        }

    # --------------------------------------------------------
    # 7. ESTRUTURA COMPATÍVEL COM O RESPONDEDOR
    # --------------------------------------------------------

    resposta_dados = {
        "success": True,
        "columns": colunas,
        "rows": linhas,
        "row_count": len(linhas),
        "execution_time_ms": duracao,
        "executed_sql": sql_validado,
    }

    # --------------------------------------------------------
    # 8. RESULTADO → RESPOSTA NATURAL
    # --------------------------------------------------------

    resposta_final = (
        respondedor.gerar_resposta(
            pergunta=pergunta,
            resposta_api=resposta_dados,
        )
    )

    uso_resposta = (
        provedor.obter_ultimo_uso()
    )

    uso_total = _somar_usos(
        uso_sql,
        uso_resposta,
    )

    status_final = resposta_final.get(
        "status"
    )

    mensagem_final = resposta_final.get(
        "message"
    )

    if status_final not in {
        "ANSWER",
        "NO_DATA",
    }:
        return {
            "success": False,
            "status": status_final,
            "answer": mensagem_final,
            "generated_sql": sql_validado,
            "columns": colunas,
            "rows": linhas,
            "row_count": len(linhas),
            "execution_time_ms": duracao,
            "usage": uso_total,
        }

    # --------------------------------------------------------
    # 9. RESPOSTA FINAL DO /ask
    # --------------------------------------------------------

    return {
        "success": True,
        "status": status_final,
        "answer": mensagem_final,
        "generated_sql": sql_validado,
        "columns": colunas,
        "rows": linhas,
        "row_count": len(linhas),
        "execution_time_ms": duracao,
        "usage": uso_total,
    }
