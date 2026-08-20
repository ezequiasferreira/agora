import json
import re


class Respondedor:
    """
    Responsável por transformar o resultado estruturado
    da consulta em uma resposta natural para o usuário.

    O respondedor não altera os dados retornados pelo banco.
    Ele apenas apresenta os resultados de forma clara e fiel.
    """

    def __init__(
        self,
        llm_provider,
    ):
        self.llm_provider = llm_provider

    # ========================================================
    # AUXILIARES
    # ========================================================

    @staticmethod
    def _nomes_distintos(
        resposta_api: dict,
    ) -> list[str]:
        """
        Extrai nomes distintos retornados pela consulta,
        preservando exatamente a grafia existente na base.
        """

        colunas = resposta_api.get(
            "columns",
            [],
        )

        linhas = resposta_api.get(
            "rows",
            [],
        )

        if not colunas or not linhas:
            return []

        candidatos_coluna_nome = [
            "nome",
            "nome_servidor",
            "servidor",
            "nome_completo",
        ]

        indice_nome = None

        for candidato in candidatos_coluna_nome:
            if candidato in colunas:
                indice_nome = colunas.index(
                    candidato
                )
                break

        if indice_nome is None:
            return []

        nomes = []

        for linha in linhas:
            if indice_nome >= len(linha):
                continue

            valor = linha[indice_nome]

            if valor is None:
                continue

            nome = str(valor).strip()

            if (
                nome
                and nome not in nomes
            ):
                nomes.append(nome)

        return nomes

    @staticmethod
    def _formatar_dados_para_prompt(
        resposta_api: dict,
    ) -> str:
        """
        Serializa os dados retornados pelo banco
        para envio ao modelo.
        """

        estrutura = {
            "columns": resposta_api.get(
                "columns",
                [],
            ),
            "rows": resposta_api.get(
                "rows",
                [],
            ),
            "row_count": resposta_api.get(
                "row_count",
                0,
            ),
            "execution_time_ms": resposta_api.get(
                "execution_time_ms",
            ),
        }

        return json.dumps(
            estrutura,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _extrair_json(
        texto: str,
    ) -> dict | None:
        """
        Tenta interpretar a resposta do modelo como JSON.

        Aceita:
        - JSON puro;
        - JSON dentro de bloco ```json ... ```;
        - texto contendo um único objeto JSON.
        """

        if not texto:
            return None

        texto = texto.strip()

        # ----------------------------------------------------
        # 1. JSON puro
        # ----------------------------------------------------

        try:
            return json.loads(
                texto
            )

        except json.JSONDecodeError:
            pass

        # ----------------------------------------------------
        # 2. Bloco Markdown ```json ... ```
        # ----------------------------------------------------

        bloco = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```",
            texto,
            flags=(
                re.IGNORECASE
                | re.DOTALL
            ),
        )

        if bloco:
            try:
                return json.loads(
                    bloco.group(1)
                )

            except json.JSONDecodeError:
                pass

        # ----------------------------------------------------
        # 3. Primeiro objeto JSON encontrado no texto
        # ----------------------------------------------------

        inicio = texto.find("{")
        fim = texto.rfind("}")

        if (
            inicio != -1
            and fim != -1
            and fim > inicio
        ):
            candidato = texto[
                inicio:fim + 1
            ]

            try:
                return json.loads(
                    candidato
                )

            except json.JSONDecodeError:
                pass

        return None

    @staticmethod
    def _montar_prompt(
        pergunta: str,
        resposta_api: dict,
        nomes: list[str],
    ) -> str:
        """
        Monta o prompt completo utilizado para transformar
        os dados estruturados em resposta natural.
        """

        dados_json = (
            Respondedor
            ._formatar_dados_para_prompt(
                resposta_api
            )
        )

        contexto_nome = ""

        if len(nomes) == 1:
            contexto_nome = f"""
A consulta retornou exatamente uma pessoa distinta.

NOME COMPLETO RETORNADO PELA BASE:
{nomes[0]}

REGRA OBRIGATÓRIA:
Use explicitamente esse nome completo na resposta.
Não utilize apenas o fragmento de nome escrito pelo usuário.
"""

        elif len(nomes) > 1:
            nomes_formatados = "\n".join(
                f"- {nome}"
                for nome in nomes
            )

            contexto_nome = f"""
A consulta retornou várias pessoas distintas:

{nomes_formatados}

REGRA OBRIGATÓRIA:
Não trate esses registros como se pertencessem
a uma única pessoa.
Preserve os nomes individualmente.
"""

        return f"""
Você é o componente responsável pela resposta final do Ágora.

Sua função é transformar o resultado já consultado no banco
em uma resposta natural, objetiva e fiel aos dados.

============================================================
REGRAS OBRIGATÓRIAS
============================================================

1. Utilize somente os dados apresentados abaixo.

2. Não invente:
   - nomes;
   - valores;
   - datas;
   - cargos;
   - unidades;
   - categorias;
   - conclusões ausentes dos dados.

3. Quando houver um nome de pessoa retornado pelo banco,
   utilize o nome exatamente como ele aparece nos dados.

4. Se o usuário escreveu apenas parte de um nome,
   mas a consulta retornou o nome completo,
   a resposta deve mostrar o nome completo retornado pela base.

5. Nunca prefira o fragmento digitado pelo usuário
   ao nome completo existente no resultado.

6. Se houver exatamente uma pessoa distinta,
   identifique-a explicitamente pelo nome completo.

7. Se houver várias pessoas distintas,
   não atribua os dados a uma única pessoa.

8. Preserve os filtros da pergunta:
   - período;
   - pessoa;
   - cargo;
   - unidade;
   - medida;
   - demais critérios efetivamente presentes.

9. Valores monetários devem ser apresentados,
   quando aplicável, no padrão brasileiro.

Exemplo:

11122.04

deve ser apresentado como:

R$ 11.122,04

10. Se houver um único resultado simples,
    responda de forma direta.

11. Se houver vários registros e uma tabela facilitar
    a compreensão, utilize tabela Markdown.

12. Não mencione:
    - SQL;
    - tokens;
    - custo;
    - arquitetura interna;
    - detalhes técnicos do processamento.

13. Não diga que encontrou algo que não esteja
    efetivamente presente nos dados.

14. Responda em português do Brasil.

15. ZERO É UM RESULTADO VÁLIDO.

    Se uma consulta agregada retornar valores como:

    - quantidade = 0;
    - total = 0;
    - impacto financeiro = 0;
    - média = 0;

    isso NÃO significa ausência de dados.

    Nesse caso, retorne status ANSWER e explique
    objetivamente que o resultado encontrado foi zero.

16. Utilize NO_DATA somente quando o banco não retornar
    nenhuma linha para os critérios consultados.

17. Uma linha agregada contendo COUNT(*) = 0 representa
    uma resposta analítica válida.

18. Se a população analisada for zero e o impacto financeiro
    retornado também for zero, informe explicitamente:

    - que não foram identificados registros na condição;
    - que o impacto financeiro total observado foi R$ 0,00,
      quando esse valor estiver presente nos dados.

19. Não use expressões como "informação não disponível"
    ou "nenhum resultado encontrado" quando a consulta tiver
    retornado uma linha válida contendo valores iguais a zero.

============================================================
PERGUNTA ORIGINAL
============================================================

{pergunta}

============================================================
DADOS RETORNADOS PELO BANCO
============================================================

{dados_json}

============================================================
CONTEXTO DE IDENTIFICAÇÃO
============================================================

{contexto_nome}

============================================================
FORMATO OBRIGATÓRIO
============================================================

Retorne SOMENTE JSON válido.

Não use Markdown em volta do JSON.

Formato:

{{
  "status": "ANSWER",
  "message": "texto final para o usuário"
}}

Use NO_DATA somente se nenhuma linha tiver sido retornada:

{{
  "status": "NO_DATA",
  "message": "Não foram encontrados dados para os critérios informados."
}}
""".strip()

    # ========================================================
    # RESPOSTA
    # ========================================================

    def gerar_resposta(
        self,
        pergunta: str,
        resposta_api: dict,
    ) -> dict:
        """
        Converte o resultado da consulta em resposta natural.
        """

        linhas = resposta_api.get(
            "rows",
            [],
        )

        row_count = resposta_api.get(
            "row_count",
            len(linhas),
        )

        # ----------------------------------------------------
        # SEM LINHAS
        #
        # Esta é a única situação em que NO_DATA deve ser
        # retornado diretamente pelo respondedor.
        # ----------------------------------------------------

        if (
            not linhas
            or row_count == 0
        ):
            return {
                "status": "NO_DATA",
                "message": (
                    "Não foram encontrados dados "
                    "para os critérios informados."
                ),
            }

        # ----------------------------------------------------
        # IDENTIFICAÇÃO DOS NOMES
        # ----------------------------------------------------

        nomes = self._nomes_distintos(
            resposta_api
        )

        # ----------------------------------------------------
        # PROMPT FINAL
        # ----------------------------------------------------

        prompt = self._montar_prompt(
            pergunta=pergunta,
            resposta_api=resposta_api,
            nomes=nomes,
        )

        # ----------------------------------------------------
        # CHAMADA AO PROVEDOR
        #
        # A interface existente do Ágora utiliza gerar_sql()
        # como método genérico de envio de prompt ao LLM.
        # ----------------------------------------------------

        try:
            texto_resposta = (
                self.llm_provider.gerar_sql(
                    prompt
                )
            )

        except Exception:
            return {
                "status": "FORMAT_ERROR",
                "message": (
                    "Não foi possível gerar "
                    "a resposta final."
                ),
            }

        # ----------------------------------------------------
        # INTERPRETAÇÃO DO JSON
        # ----------------------------------------------------

        resultado = self._extrair_json(
            texto_resposta
        )

        if resultado is None:
            return {
                "status": "FORMAT_ERROR",
                "message": (
                    "O módulo de resposta retornou "
                    "um formato inválido."
                ),
            }

        status_resposta = resultado.get(
            "status"
        )

        mensagem = resultado.get(
            "message"
        )

        # ----------------------------------------------------
        # ERROS DO PROVEDOR
        # ----------------------------------------------------

        if status_resposta in {
            "PROVIDER_ERROR",
            "FORMAT_ERROR",
        }:
            return {
                "status": status_resposta,
                "message": (
                    mensagem
                    or
                    "Não foi possível gerar "
                    "a resposta final."
                ),
            }

        # ----------------------------------------------------
        # PROTEÇÃO CONTRA FALSO NO_DATA
        #
        # Se o banco retornou uma ou mais linhas, inclusive
        # linhas agregadas contendo zero, existe resultado.
        #
        # Nesse caso não permitimos que o modelo transforme
        # uma resposta válida em NO_DATA.
        # ----------------------------------------------------

        if (
            status_resposta == "NO_DATA"
            and row_count > 0
        ):
            status_resposta = "ANSWER"

            if not mensagem:
                mensagem = (
                    "A consulta retornou um resultado "
                    "válido para os critérios informados."
                )

        # ----------------------------------------------------
        # STATUS VÁLIDOS
        # ----------------------------------------------------

        if status_resposta not in {
            "ANSWER",
            "NO_DATA",
        }:
            return {
                "status": "FORMAT_ERROR",
                "message": (
                    "O módulo de resposta retornou "
                    "um estado inválido."
                ),
            }

        if not mensagem:
            return {
                "status": "FORMAT_ERROR",
                "message": (
                    "O módulo de resposta não gerou "
                    "uma mensagem válida."
                ),
            }

        return {
            "status": status_resposta,
            "message": mensagem,
        }
