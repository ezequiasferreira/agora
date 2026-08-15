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
    def __init__(self):
        self.last_usage = None

    def gerar_sql(self, prompt: str) -> str:
        raise NotImplementedError(
            "As subclasses devem implementar este método."
        )

    def obter_ultimo_uso(self) -> dict | None:
        """
        Retorna os metadados da última chamada ao provedor.

        O formato esperado é:

        {
            "model": "...",
            "input_tokens": 0,
            "cached_input_tokens": 0,
            "output_tokens": 0,
            "reasoning_tokens": 0,
            "total_tokens": 0
        }
        """

        return self.last_usage


# ============================================================
# FUNÇÃO AUXILIAR PARA ERROS TÉCNICOS
# ============================================================

def _provider_error(
    message: str,
    error_type: str = "PROVIDER_ERROR",
) -> str:
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
        super().__init__()

        self.client = OpenAI(
            api_key=api_key
        )

        self.model = model

    def _registrar_uso(
        self,
        response,
    ):
        """
        Captura os metadados de uso retornados
        pela Responses API.
        """

        usage = getattr(
            response,
            "usage",
            None,
        )

        if usage is None:
            self.last_usage = {
                "model": self.model,
                "input_tokens": 0,
                "cached_input_tokens": 0,
                "output_tokens": 0,
                "reasoning_tokens": 0,
                "total_tokens": 0,
            }

            return

        input_details = getattr(
            usage,
            "input_tokens_details",
            None,
        )

        output_details = getattr(
            usage,
            "output_tokens_details",
            None,
        )

        cached_input_tokens = 0
        reasoning_tokens = 0

        if input_details is not None:
            cached_input_tokens = (
                getattr(
                    input_details,
                    "cached_tokens",
                    0,
                )
                or 0
            )

        if output_details is not None:
            reasoning_tokens = (
                getattr(
                    output_details,
                    "reasoning_tokens",
                    0,
                )
                or 0
            )

        self.last_usage = {
            "model": (
                getattr(
                    response,
                    "model",
                    None,
                )
                or self.model
            ),
            "input_tokens": (
                getattr(
                    usage,
                    "input_tokens",
                    0,
                )
                or 0
            ),
            "cached_input_tokens": (
                cached_input_tokens
            ),
            "output_tokens": (
                getattr(
                    usage,
                    "output_tokens",
                    0,
                )
                or 0
            ),
            "reasoning_tokens": (
                reasoning_tokens
            ),
            "total_tokens": (
                getattr(
                    usage,
                    "total_tokens",
                    0,
                )
                or 0
            ),
        }

    def gerar_sql(
        self,
        prompt: str,
    ) -> str:
        self.last_usage = None

        try:
            response = (
                self.client.responses.create(
                    model=self.model,
                    input=prompt,
                )
            )

            self._registrar_uso(
                response
            )

            return response.output_text

        except RateLimitError:
            return _provider_error(
                "O provedor de Inteligência Artificial "
                "atingiu temporariamente o limite de "
                "requisições ou de cota."
            )

        except AuthenticationError:
            return _provider_error(
                "Falha de autenticação no provedor "
                "de Inteligência Artificial."
            )

        except APITimeoutError:
            return _provider_error(
                "O provedor de Inteligência Artificial "
                "excedeu o tempo limite de resposta."
            )

        except APIConnectionError:
            return _provider_error(
                "Não foi possível estabelecer comunicação "
                "com o provedor de Inteligência Artificial."
            )

        except APIStatusError as exc:
            return _provider_error(
                "O provedor de Inteligência Artificial "
                f"retornou um erro HTTP {exc.status_code}."
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
        super().__init__()

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    def gerar_sql(
        self,
        prompt: str,
    ) -> str:
        self.last_usage = None

        try:
            interaction = (
                self.client.interactions.create(
                    model=self.model,
                    input=prompt,
                )
            )

            return interaction.output_text

        except Exception as exc:
            erro_str = str(exc)

            if (
                "429" in erro_str
                or "Quota exceeded" in erro_str
            ):
                return _provider_error(
                    "O provedor de Inteligência Artificial "
                    "atingiu temporariamente o limite de "
                    "requisições ou de cota."
                )

            return _provider_error(
                "Erro de comunicação com o provedor "
                "de Inteligência Artificial."
            )
