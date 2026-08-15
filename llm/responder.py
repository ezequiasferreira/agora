import json
import os
from decimal import Decimal


def _json_default(valor):
    """
    Converte tipos retornados pelo banco que não são
    serializáveis nativamente pelo módulo json.
    """

    if isinstance(valor, Decimal):
        return float(valor)

    raise TypeError(
        f"Objeto do tipo {type(valor).__name__} "
        "não é serializável em JSON."
    )


class Respondedor:
    """
    Converte o resultado estruturado da API em uma resposta
    final em linguagem natural para o usuário.

    A resposta deve ser construída exclusivamente a partir:
    - da pergunta original;
    - das colunas retornadas pela API;
    - das linhas retornadas pela API;
    - das regras semânticas de apresentação do perfil ativo.

    Nenhuma nova consulta ao banco é realizada aqui.
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

        self.diretorio_base = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.diretorio_raiz = os.path.dirname(
            self.diretorio_base
        )

        self.semantic_profile = os.getenv(
            "SEMANTIC_PROFILE",
            "",
        ).strip()

        self.formatacao_semantica = (
            self._carregar_formatacao_semantica()
        )

    def _carregar_formatacao_semantica(
        self,
    ) -> list[dict]:
        """
        Carrega somente os conceitos do glossário que
        possuem instruções explícitas de apresentação.

        O núcleo do respondedor permanece independente
        de organização, moeda ou domínio específico.
        """

        if not self.semantic_profile:
            return []

        caminho_glossario = os.path.join(
            self.diretorio_raiz,
            "semantic",
            "profiles",
            self.semantic_profile,
            "glossary.json",
        )

        try:
            with open(
                caminho_glossario,
                "r",
                encoding="utf-8",
            ) as arquivo:
                glossario = json.load(
                    arquivo
                )

        except FileNotFoundError:
            return []

        except json.JSONDecodeError:
            return []

        conceitos_formataveis = []

        for conceito in glossario.get(
            "concepts",
            [],
        ):
            display = conceito.get(
                "display"
            )

            if not display:
                continue

            conceitos_formataveis.append(
                {
                    "id": conceito.get(
                        "id"
                    ),
                    "business_name": conceito.get(
                        "business_name"
                    ),
                    "synonyms": conceito.get(
                        "synonyms",
                        [],
                    ),
                    "targets": conceito.get(
                        "targets",
                        [],
                    ),
                    "display": display,
                }
            )

        return conceitos_formataveis

    def gerar_resposta(
        self,
        pergunta: str,
        resposta_api: dict,
    ) -> dict:
        """
        Gera uma resposta final em linguagem natural.

        Retornos possíveis:

        {
            "status": "ANSWER",
            "message": "..."
        }

        {
            "status": "API_ERROR",
            "message": "..."
        }

        {
            "status": "NO_DATA",
            "message": "..."
        }

        {
            "status": "PROVIDER_ERROR",
            "message": "..."
        }

        {
            "status": "FORMAT_ERROR",
            "message": "..."
        }
        """

        if not resposta_api:
            return {
                "status": "API_ERROR",
                "message": (
                    "A API não retornou uma resposta válida."
                ),
            }

        if not resposta_api.get("success"):
            return {
                "status": "API_ERROR",
                "message": resposta_api.get(
                    "message",
                    "Falha ao executar a consulta.",
                ),
            }

        colunas = resposta_api.get(
            "columns",
            [],
        )

        linhas = resposta_api.get(
            "rows",
            [],
        )

        if not linhas:
            return {
                "status": "NO_DATA",
                "message": (
                    "Não foram encontrados dados para "
                    "responder à pergunta."
                ),
            }

        dados = {
            "columns": colunas,
            "rows": linhas,
        }

        dados_json = json.dumps(
            dados,
            ensure_ascii=False,
            indent=2,
            default=_json_default,
        )

        formatacao_json = json.dumps(
            self.formatacao_semantica,
            ensure_ascii=False,
            indent=2,
        )

        prompt = f"""
Você é o módulo de resposta final do Ágora.

Sua função é transformar resultados estruturados de banco
de dados em uma resposta clara, objetiva e natural para o
usuário.

REGRAS OBRIGATÓRIAS:

1. Utilize SOMENTE os dados fornecidos abaixo.
2. Não invente informações.
3. Não faça novas suposições sobre os dados.
4. Preserve o significado e a magnitude dos valores numéricos.
5. Não crie explicações que não estejam sustentadas pelos dados.
6. Não mencione SQL, banco de dados, API ou detalhes técnicos,
   a menos que a pergunta do usuário seja técnica.
7. Responda diretamente à pergunta.
8. Se houver apenas um valor agregado, apresente-o de forma
   simples e natural.
9. Se houver várias linhas, faça um resumo objetivo.
10. Preserve nomes e categorias existentes nos dados.

REGRAS DE APRESENTAÇÃO:

11. As regras semânticas de apresentação abaixo são confiáveis
    e pertencem ao perfil institucional ativo.

12. Quando o conceito correspondente aos dados possuir
    configuração "display", utilize-a somente para FORMATAÇÃO
    da resposta.

13. A formatação pode:
    - aplicar símbolo monetário;
    - aplicar separadores conforme o locale;
    - limitar casas decimais para apresentação;
    - representar percentuais ou outros formatos declarados.

14. A formatação nunca pode modificar o significado do dado.

15. Para valores monetários, arredondar para o número de casas
    decimais informado em "decimal_places" é permitido apenas
    para apresentação ao usuário.

16. Não presuma moeda, locale ou formato quando isso não estiver
    declarado nas regras semânticas disponíveis.

17. Se nenhuma regra de apresentação for aplicável, apresente
    o valor de forma objetiva, preservando seu conteúdo.

FORMATO DE SAÍDA OBRIGATÓRIO:

{{
  "status": "ANSWER",
  "message": "Resposta final ao usuário"
}}

PERGUNTA ORIGINAL:

{pergunta}

DADOS RETORNADOS:

{dados_json}

REGRAS SEMÂNTICAS DE APRESENTAÇÃO DISPONÍVEIS:

{formatacao_json}
"""

        resposta_bruta = self.llm.gerar_sql(
            prompt
        )

        if not resposta_bruta:
            return {
                "status": "PROVIDER_ERROR",
                "message": (
                    "O provedor de Inteligência Artificial "
                    "não retornou uma resposta final."
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
                "message": (
                    "A resposta final da Inteligência "
                    "Artificial não possui formato JSON válido."
                ),
            }

        if (
            resultado.get("status")
            == "PROVIDER_ERROR"
        ):
            return resultado

        if (
            resultado.get("status")
            != "ANSWER"
        ):
            return {
                "status": "FORMAT_ERROR",
                "message": (
                    "A resposta final possui um status "
                    "não reconhecido pelo Ágora."
                ),
            }

        mensagem = resultado.get(
            "message"
        )

        if not mensagem:
            return {
                "status": "FORMAT_ERROR",
                "message": (
                    "A resposta final não contém mensagem."
                ),
            }

        return {
            "status": "ANSWER",
            "message": mensagem,
        }
