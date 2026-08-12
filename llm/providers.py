import json

from google import genai
from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
    AuthenticationError,
    RateLimitError,
)


# ============================================================
# CLASSE BASE
# ============================================================

class LLMProvider:
    def gerar_sql(self, prompt: str) -> str:
        raise NotImplementedError(
            "As subclasses devem implementar este método."
        )


# ============================================================
# FUNÇÃO AUXILIAR PARA ERROS TÉCNICOS
# ============================================================

def _provider_error(message: str, error_type: str = "PROVIDER_ERROR") -> str:
    """
    Gera uma resposta JSON padronizada para falhas técnicas
    relacionadas ao provedor de Inteligência Artificial.

    PROVIDER_ERROR NÃO significa que os dados são insuficientes.
    É um erro técnico de infraestrutura/comunicação.
    """
    return json.dumps(
        {
            "status": error_type,
            "sql": None,
            "message": message,
        },
        ensure_ascii=False,
    )


# ============================================================
# OPENAI
# ============================================================

class OpenAILLM(LLMProvider):
    """
    Provedor principal do MVP do Ágora.

    Utiliza a Responses API da OpenAI.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5.6-luna",
    ):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def gerar_sql(self, prompt: str) -> str:
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
            )

            return response.output_text

        except RateLimitError:
            return _provider_error(
                "O provedor de Inteligência Artificial atingiu "
                "temporariamente o limite de requisições ou de cota."
            )

        except AuthenticationError:
            return _provider_error(
                "Falha de autenticação no provedor de Inteligência Artificial."
            )

        except APITimeoutError:
            return _provider_error(
                "O provedor de Inteligência Artificial excedeu "
                "o tempo limite de resposta."
            )

        except APIConnectionError:
            return _provider_error(
                "Não foi possível estabelecer comunicação com "
                "o provedor de Inteligência Artificial."
            )

        except APIStatusError as exc:
            return _provider_error(
                f"O provedor de Inteligência Artificial retornou "
                f"um erro HTTP {exc.status_code}."
            )

        except Exception:
            return _provider_error(
                "Ocorreu um erro inesperado ao acessar "
                "o provedor de Inteligência Artificial."
            )


# ============================================================
# GEMINI
# ============================================================

class GeminiLLM(LLMProvider):
    """
    Provedor alternativo do Ágora.

    Mantido para permitir independência de fornecedor.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.5-flash",
    ):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def gerar_sql(self, prompt: str) -> str:
        try:
            interaction = self.client.interactions.create(
                model=self.model,
                input=prompt,
            )

            return interaction.output_text

        except Exception as exc:
            erro_str = str(exc)

            if "429" in erro_str or "Quota exceeded" in erro_str:
                return _provider_error(
                    "O provedor de Inteligência Artificial atingiu "
                    "temporariamente o limite de requisições ou de cota."
                )

            return _provider_error(
                "Erro de comunicação com o provedor "
                "de Inteligência Artificial."
            )
