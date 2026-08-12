import os
import json

from dotenv import load_dotenv

try:
    from .providers import OpenAILLM, GeminiLLM
    from .translator import TradutorNL2SQL
    from .api_client import executar_sql_na_api
except ImportError:
    from providers import OpenAILLM, GeminiLLM
    from translator import TradutorNL2SQL
    from api_client import executar_sql_na_api


# ============================================================
# CONFIGURAÇÃO
# ============================================================

DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))

# Carrega especificamente o .env existente dentro de llm/
CAMINHO_ENV = os.path.join(DIRETORIO_BASE, ".env")
load_dotenv(CAMINHO_ENV)

# Provedor padrão do MVP
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").strip().lower()

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
# CRIAÇÃO DO PROVEDOR
# ============================================================

def criar_provedor():
    """
    Cria o provedor de LLM definido na variável LLM_PROVIDER.

    Valores aceitos:
    - openai
    - gemini
    """

    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY não encontrada no arquivo llm/.env."
            )

        return OpenAILLM(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
        )

    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY não encontrada no arquivo llm/.env."
            )

        return GeminiLLM(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
        )

    raise ValueError(
        f"LLM_PROVIDER inválido: {LLM_PROVIDER}. "
        "Utilize 'openai' ou 'gemini'."
    )


# ============================================================
# INICIALIZAÇÃO
# ============================================================

provedor = criar_provedor()

tradutor = TradutorNL2SQL(
    llm_provider=provedor
)

print("Ágora — Módulo NL → SQL")
print(f"Provedor: {LLM_PROVIDER}")

if LLM_PROVIDER == "openai":
    print(f"Modelo: {OPENAI_MODEL}")
else:
    print(f"Modelo: {GEMINI_MODEL}")

print("Digite 'sair' para encerrar.")
print("-" * 60)


# ============================================================
# LOOP INTERATIVO
# ============================================================

while True:
    pergunta = input("\nDigite sua pergunta: ").strip()

    if pergunta.lower() in {
        "sair",
        "exit",
        "quit",
        "0",
    }:
        break

    if not pergunta:
        continue

    log_execucao = {
        "question": pergunta,
        "provider": LLM_PROVIDER,
        "status_llm": None,
        "generated_sql": None,
        "api_response": None,
        "error": None,
    }

    print("\nProcessando com a LLM...")

    resultado_llm = tradutor.processar_pergunta(
        pergunta
    )

    status = resultado_llm.get("status")
    log_execucao["status_llm"] = status

    # ========================================================
    # QUERY
    # ========================================================

    if status == "QUERY":
        query_string = resultado_llm.get("sql")

        if not query_string:
            log_execucao["error"] = (
                "A LLM retornou QUERY sem uma instrução SQL."
            )

            print(
                "[FORMAT_ERROR] "
                "A LLM não retornou uma instrução SQL."
            )

        else:
            log_execucao["generated_sql"] = (
                query_string
            )

            print(
                f"\n[{status}] SQL gerado:"
            )
            print(query_string)

            print(
                "\nEnviando consulta para "
                "POST /query..."
            )

            try:
                resposta_api = executar_sql_na_api(
                    query_string
                )

                log_execucao["api_response"] = (
                    resposta_api
                )

                print("\nResposta da API:")
                print(
                    json.dumps(
                        resposta_api,
                        indent=2,
                        ensure_ascii=False,
                    )
                )

            except Exception as exc:
                log_execucao["error"] = str(exc)

                print(
                    "[API_ERROR] "
                    "Falha ao consultar a API do Ágora."
                )

    # ========================================================
    # LIMITAÇÃO DOS DADOS
    # ========================================================

    elif status == "NOT_ANSWERABLE":
        mensagem = resultado_llm.get(
            "message"
        )

        log_execucao["error"] = mensagem

        print(
            f"\n[{status}] {mensagem}"
        )

    # ========================================================
    # AMBIGUIDADE
    # ========================================================

    elif status == "NEEDS_CLARIFICATION":
        mensagem = resultado_llm.get(
            "message"
        )

        log_execucao["error"] = mensagem

        print(
            f"\n[{status}] {mensagem}"
        )

    # ========================================================
    # ERRO DO PROVEDOR
    # ========================================================

    elif status == "PROVIDER_ERROR":
        mensagem = resultado_llm.get(
            "message"
        )

        log_execucao["error"] = mensagem

        print(
            f"\n[{status}] {mensagem}"
        )

    # ========================================================
    # ERRO DE FORMATO
    # ========================================================

    elif status == "FORMAT_ERROR":
        mensagem = resultado_llm.get(
            "message"
        )

        log_execucao["error"] = mensagem

        print(
            f"\n[{status}] {mensagem}"
        )

    # ========================================================
    # STATUS DESCONHECIDO
    # ========================================================

    else:
        mensagem = (
            f"Status não reconhecido: {status}"
        )

        log_execucao["error"] = mensagem

        print(
            f"\n[INTERNAL_ERROR] {mensagem}"
        )

    # ========================================================
    # LOG
    # ========================================================

    print("\n--- LOG DE EXECUÇÃO ---")

    print(
        json.dumps(
            log_execucao,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("-" * 60)
