import os
import json

try:
    from .providers import LLMProvider
except ImportError:
    from providers import LLMProvider


class TradutorNL2SQL:
    def __init__(
        self,
        llm_provider: LLMProvider,
        nome_catalogo="data_catalog.json",
    ):
        self.llm = llm_provider

        # Diretório da pasta llm/
        self.diretorio_base = os.path.dirname(
            os.path.abspath(__file__)
        )

        # Diretório raiz do projeto
        self.diretorio_raiz = os.path.dirname(
            self.diretorio_base
        )

        # Carrega catálogo e prompt uma única vez
        self.catalogo_str = self._carregar_catalogo(
            nome_catalogo
        )
        self.system_prompt = self._carregar_system_prompt()

    def _carregar_catalogo(self, nome_arquivo):
        caminho_completo = os.path.join(
            self.diretorio_raiz,
            "catalog",
            nome_arquivo,
        )

        try:
            with open(
                caminho_completo,
                "r",
                encoding="utf-8",
            ) as arquivo:
                catalogo = json.load(arquivo)

            return json.dumps(
                catalogo,
                indent=2,
                ensure_ascii=False,
            )

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Catálogo não encontrado: {caminho_completo}"
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Catálogo JSON inválido: {caminho_completo}"
            ) from exc

    def _carregar_system_prompt(
        self,
        caminho_relativo="prompts/system_prompt.md",
    ):
        caminho_completo = os.path.join(
            self.diretorio_base,
            caminho_relativo,
        )

        try:
            with open(
                caminho_completo,
                "r",
                encoding="utf-8",
            ) as arquivo:
                return arquivo.read()

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Arquivo de regras não encontrado: "
                f"{caminho_completo}"
            )

    def processar_pergunta(self, pergunta: str) -> dict:
        prompt_completo = f"""{self.system_prompt}

FORMATO DE SAÍDA OBRIGATÓRIO (JSON):
{{
  "status": "QUERY | NOT_ANSWERABLE | NEEDS_CLARIFICATION",
  "sql": "Comando SQL completo ou null",
  "message": "Explicação ou null"
}}

CATÁLOGO DE DADOS DISPONÍVEIS:
{self.catalogo_str}

PERGUNTA DO USUÁRIO:
{pergunta}
"""

        resposta_bruta = self.llm.gerar_sql(
            prompt_completo
        )

        if not resposta_bruta:
            return {
                "status": "PROVIDER_ERROR",
                "sql": None,
                "message": (
                    "O provedor de Inteligência Artificial "
                    "não retornou conteúdo."
                ),
            }

        json_limpo = (
            resposta_bruta
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            resultado = json.loads(json_limpo)

        except json.JSONDecodeError:
            return {
                "status": "FORMAT_ERROR",
                "sql": None,
                "message": (
                    "A resposta do provedor de Inteligência "
                    "Artificial não possui formato JSON válido."
                ),
            }

        # Erros técnicos produzidos pelo próprio provider
        if resultado.get("status") == "PROVIDER_ERROR":
            return resultado

        status = resultado.get("status")

        estados_validos = {
            "QUERY",
            "NOT_ANSWERABLE",
            "NEEDS_CLARIFICATION",
        }

        if status not in estados_validos:
            return {
                "status": "FORMAT_ERROR",
                "sql": None,
                "message": (
                    "A resposta da LLM contém um status "
                    "não reconhecido pelo Ágora."
                ),
            }

        # QUERY obrigatoriamente precisa possuir SQL
        if status == "QUERY" and not resultado.get("sql"):
            return {
                "status": "FORMAT_ERROR",
                "sql": None,
                "message": (
                    "A LLM retornou QUERY sem uma "
                    "instrução SQL."
                ),
            }

        return resultado
