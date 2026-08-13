import os
import json

from dotenv import load_dotenv

try:
    from .providers import OpenAILLM, GeminiLLM
    from .translator import TradutorNL2SQL
    from .api_client import executar_sql_na_api
    from .responder import Respondedor
except ImportError:
    from providers import OpenAILLM, GeminiLLM
    from translator import TradutorNL2SQL
    from api_client import executar_sql_na_api
    from responder import Respondedor


# ============================================================
# CONFIGURAÇÃO
# ============================================================

DIRETORIO_BASE = os.path.dirname(
    os.path.abspath(__file__)
)

# Carrega especificamente o .env existente dentro de llm/
CAMINHO_ENV = os.path.join(
    DIRETORIO_BASE,
    ".env",
)

load_dotenv(CAMINHO_ENV)

# Provedor padrão do MVP
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
                "OPENAI_API_KEY não encontrada "
                "no arquivo llm/.env."
            )

        return OpenAILLM(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
        )

    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY não encontrada "
                "no arquivo llm/.env."
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
# EXECUÇÃO INTERATIVA
# ============================================================

def main():
    provedor = criar_provedor()

    tradutor = TradutorNL2SQL(
        llm_provider=provedor
    )

    respondedor = Respondedor(
        llm_provider=provedor
    )

    print("Ágora — Consulta Inteligente")
    print(f"Provedor: {LLM_PROVIDER}")

    if LLM_PROVIDER == "openai":
        print(f"Modelo: {OPENAI_MODEL}")
    else:
        print(f"Modelo: {GEMINI_MODEL}")

    print("Digite 'sair' para encerrar.")
    print("-" * 60)

    while True:
        pergunta = input(
            "\nDigite sua pergunta: "
        ).strip()

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
            "final_response": None,
            "error": None,
        }

        print(
            "\nProcessando pergunta..."
        )

        resultado_llm = (
            tradutor.processar_pergunta(
                pergunta
            )
        )

        status = resultado_llm.get(
            "status"
        )

        log_execucao[
            "status_llm"
        ] = status

        # ====================================================
        # QUERY
        # ====================================================

        if status == "QUERY":
            query_string = (
                resultado_llm.get("sql")
            )

            if not query_string:
                mensagem = (
                    "A LLM retornou QUERY sem "
                    "uma instrução SQL."
                )

                log_execucao[
                    "error"
                ] = mensagem

                print(
                    f"\n[FORMAT_ERROR] "
                    f"{mensagem}"
                )

            else:
                log_execucao[
                    "generated_sql"
                ] = query_string

                print(
                    "\nConsulta compreendida."
                )

                print(
                    "Consultando os dados..."
                )

                resposta_api = (
                    executar_sql_na_api(
                        query_string
                    )
                )

                log_execucao[
                    "api_response"
                ] = resposta_api

                if not resposta_api.get(
                    "success"
                ):
                    mensagem = (
                        resposta_api.get(
                            "message",
                            (
                                "Não foi possível "
                                "executar a consulta."
                            ),
                        )
                    )

                    log_execucao[
                        "error"
                    ] = mensagem

                    print(
                        f"\n[API_ERROR] "
                        f"{mensagem}"
                    )

                else:
                    print(
                        "Preparando resposta..."
                    )

                    resposta_final = (
                        respondedor.gerar_resposta(
                            pergunta=pergunta,
                            resposta_api=resposta_api,
                        )
                    )

                    log_execucao[
                        "final_response"
                    ] = resposta_final

                    status_final = (
                        resposta_final.get(
                            "status"
                        )
                    )

                    mensagem_final = (
                        resposta_final.get(
                            "message"
                        )
                    )

                    if status_final == "ANSWER":
                        print(
                            "\nÁgora:"
                        )

                        print(
                            mensagem_final
                        )

                    elif status_final == "NO_DATA":
                        print(
                            "\nÁgora:"
                        )

                        print(
                            mensagem_final
                        )

                    else:
                        log_execucao[
                            "error"
                        ] = mensagem_final

                        print(
                            f"\n[{status_final}] "
                            f"{mensagem_final}"
                        )

        # ====================================================
        # LIMITAÇÃO DOS DADOS
        # ====================================================

        elif status == "NOT_ANSWERABLE":
            mensagem = (
                resultado_llm.get(
                    "message"
                )
            )

            log_execucao[
                "error"
            ] = mensagem

            print(
                "\nÁgora:"
            )

            print(
                mensagem
            )

        # ====================================================
        # AMBIGUIDADE
        # ====================================================

        elif status == "NEEDS_CLARIFICATION":
            mensagem = (
                resultado_llm.get(
                    "message"
                )
            )

            log_execucao[
                "error"
            ] = mensagem

            print(
                "\nÁgora:"
            )

            print(
                mensagem
            )

        # ====================================================
        # ERRO DO PROVEDOR
        # ====================================================

        elif status == "PROVIDER_ERROR":
            mensagem = (
                resultado_llm.get(
                    "message"
                )
            )

            log_execucao[
                "error"
            ] = mensagem

            print(
                f"\n[{status}] "
                f"{mensagem}"
            )

        # ====================================================
        # ERRO DE FORMATO
        # ====================================================

        elif status == "FORMAT_ERROR":
            mensagem = (
                resultado_llm.get(
                    "message"
                )
            )

            log_execucao[
                "error"
            ] = mensagem

            print(
                f"\n[{status}] "
                f"{mensagem}"
            )

        # ====================================================
        # STATUS DESCONHECIDO
        # ====================================================

        else:
            mensagem = (
                f"Status não reconhecido: "
                f"{status}"
            )

            log_execucao[
                "error"
            ] = mensagem

            print(
                f"\n[INTERNAL_ERROR] "
                f"{mensagem}"
            )

        # ====================================================
        # LOG TÉCNICO
        # ====================================================

        print(
            "\n--- LOG DE EXECUÇÃO ---"
        )

        print(
            json.dumps(
                log_execucao,
                indent=2,
                ensure_ascii=False,
            )
        )

        print(
            "-" * 60
        )


if __name__ == "__main__":
    main()
