import json


class Respondedor:
    """
    Converte o resultado estruturado da API em uma resposta
    final em linguagem natural para o usuário.

    A resposta deve ser construída exclusivamente a partir:
    - da pergunta original;
    - das colunas retornadas pela API;
    - das linhas retornadas pela API.

    Nenhuma nova consulta ao banco é realizada aqui.
    """

    def __init__(self, llm_provider):
        self.llm = llm_provider

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

        prompt = f"""
Você é o módulo de resposta final do Ágora.

Sua função é transformar resultados estruturados de banco
de dados em uma resposta clara, objetiva e natural para o
usuário.

REGRAS OBRIGATÓRIAS:

1. Utilize SOMENTE os dados fornecidos abaixo.
2. Não invente informações.
3. Não faça novas suposições sobre os dados.
4. Não altere valores numéricos.
5. Não crie explicações que não estejam sustentadas pelos dados.
6. Não mencione SQL, banco de dados, API ou detalhes técnicos,
   a menos que a pergunta do usuário seja técnica.
7. Responda diretamente à pergunta.
8. Se houver apenas um valor agregado, apresente-o de forma
   simples e natural.
9. Se houver várias linhas, faça um resumo objetivo.
10. Preserve nomes e categorias existentes nos dados.

FORMATO DE SAÍDA OBRIGATÓRIO:

{{
  "status": "ANSWER",
  "message": "Resposta final ao usuário"
}}

PERGUNTA ORIGINAL:

{pergunta}

DADOS RETORNADOS:

{json.dumps(
    dados,
    ensure_ascii=False,
    indent=2,
)}
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

        if resultado.get("status") == "PROVIDER_ERROR":
            return resultado

        if resultado.get("status") != "ANSWER":
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
