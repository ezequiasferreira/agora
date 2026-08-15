import json
import os

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

        # Perfil semântico ativo
        self.semantic_profile = os.getenv(
            "SEMANTIC_PROFILE",
            "",
        ).strip()

        # Carrega catálogo, glossário e prompt uma única vez
        self.catalogo_str = self._carregar_catalogo(
            nome_catalogo
        )

        self.glossario_str = self._carregar_glossario()

        self.system_prompt = (
            self._carregar_system_prompt()
        )

    def _carregar_json(
        self,
        caminho_completo: str,
        descricao: str,
    ) -> str:
        try:
            with open(
                caminho_completo,
                "r",
                encoding="utf-8",
            ) as arquivo:
                conteudo = json.load(
                    arquivo
                )

            return json.dumps(
                conteudo,
                indent=2,
                ensure_ascii=False,
            )

        except FileNotFoundError:
            raise FileNotFoundError(
                f"{descricao} não encontrado: "
                f"{caminho_completo}"
            )

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{descricao} contém JSON inválido: "
                f"{caminho_completo}"
            ) from exc

    def _carregar_catalogo(
        self,
        nome_arquivo: str,
    ) -> str:
        caminho_completo = os.path.join(
            self.diretorio_raiz,
            "catalog",
            nome_arquivo,
        )

        return self._carregar_json(
            caminho_completo,
            "Catálogo",
        )

    def _carregar_glossario(
        self,
    ) -> str:
        """
        Carrega o glossário institucional do perfil
        semântico configurado.

        O perfil não faz parte do núcleo do Ágora.
        Cada organização ou domínio pode possuir seu
        próprio glossário em semantic/profiles/.
        """

        if not self.semantic_profile:
            return json.dumps(
                {
                    "profile": None,
                    "concepts": [],
                },
                indent=2,
                ensure_ascii=False,
            )

        caminho_completo = os.path.join(
            self.diretorio_raiz,
            "semantic",
            "profiles",
            self.semantic_profile,
            "glossary.json",
        )

        return self._carregar_json(
            caminho_completo,
            (
                "Glossário do perfil semântico "
                f"'{self.semantic_profile}'"
            ),
        )

    def _carregar_system_prompt(
        self,
        caminho_relativo=(
            "prompts/system_prompt.md"
        ),
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
                "Arquivo de regras não encontrado: "
                f"{caminho_completo}"
            )

    def processar_pergunta(
        self,
        pergunta: str,
    ) -> dict:
        prompt_completo = f"""
{self.system_prompt}

FORMATO DE SAÍDA OBRIGATÓRIO (JSON):
{{
  "status": "QUERY | NOT_ANSWERABLE | NEEDS_CLARIFICATION",
  "sql": "Comando SQL completo ou null",
  "message": "Explicação ou null"
}}

CATÁLOGO AUTOMÁTICO DE DADOS:
{self.catalogo_str}

GLOSSÁRIO INSTITUCIONAL DO PERFIL ATIVO:
{self.glossario_str}

PERGUNTA DO USUÁRIO:
{pergunta}
"""

        resposta_bruta = (
            self.llm.gerar_sql(
                prompt_completo
            )
        )

        if not resposta_bruta:
            return {
                "status": "PROVIDER_ERROR",
                "sql": None,
                "message": (
                    "O provedor de Inteligência "
                    "Artificial não retornou conteúdo."
                ),
            }

        json_limpo = (
            resposta_bruta
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            resultado = json.loads(
                json_limpo
            )

        except json.JSONDecodeError:
            return {
                "status": "FORMAT_ERROR",
                "sql": None,
                "message": (
                    "A resposta do provedor de "
                    "Inteligência Artificial não "
                    "possui formato JSON válido."
                ),
            }

        if (
            resultado.get("status")
            == "PROVIDER_ERROR"
        ):
            return resultado

        status = resultado.get(
            "status"
        )

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
                    "A resposta da LLM contém "
                    "um status não reconhecido "
                    "pelo Ágora."
                ),
            }

        if (
            status == "QUERY"
            and not resultado.get("sql")
        ):
            return {
                "status": "FORMAT_ERROR",
                "sql": None,
                "message": (
                    "A LLM retornou QUERY sem "
                    "uma instrução SQL."
                ),
            }

        return resultado
