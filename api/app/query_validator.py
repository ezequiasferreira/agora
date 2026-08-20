import re


# ============================================================
# PALAVRAS-CHAVE PROIBIDAS
# ============================================================

# Qualquer ocorrência destas palavras como token SQL,
# fora de strings, comentários e identificadores citados,
# torna a consulta inválida.
BLOCKED_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "COPY",
    "VACUUM",
    "COMMENT",
    "MERGE",
    "INTO",
    "CALL",
    "DO",
    "SET",
    "RESET",
    "EXPLAIN",
    "ANALYZE",
    "NOTIFY",
    "LISTEN",
    "UNLISTEN",
    "LOAD",
    "LOCK",
    "REFRESH",
    "REINDEX",
    "SECURITY",
    "IMPORT",
}


# ============================================================
# EXCEÇÃO DE VALIDAÇÃO
# ============================================================

class QueryValidationError(Exception):
    def __init__(
        self,
        error_type: str,
        message: str,
    ):
        super().__init__(message)

        self.error_type = error_type
        self.message = message


# ============================================================
# LEITURA LÉXICA BÁSICA DO SQL
# ============================================================

def _eh_inicio_dollar_quote(
    sql: str,
    posicao: int,
) -> str | None:
    """
    Detecta início de string PostgreSQL com dollar quoting.

    Exemplos:

    $$
    $tag$
    $abc_123$
    """

    if sql[posicao] != "$":
        return None

    correspondencia = re.match(
        r"\$[A-Za-z_][A-Za-z0-9_]*\$|\$\$",
        sql[posicao:],
    )

    if correspondencia is None:
        return None

    return correspondencia.group(0)


def _mascarar_conteudo_nao_executavel(
    sql: str,
) -> str:
    """
    Substitui por espaços o conteúdo de:

    - strings simples;
    - identificadores entre aspas duplas;
    - strings PostgreSQL com dollar quoting;
    - comentários de linha;
    - comentários de bloco.

    Mantém os caracteres SQL executáveis fora desses contextos.

    Isso permite analisar:
    - palavras-chave;
    - ponto e vírgula;
    - comando inicial;

    sem confundir texto literal com código SQL.
    """

    resultado = []
    i = 0
    tamanho = len(sql)

    while i < tamanho:

        caractere = sql[i]

        # ----------------------------------------------------
        # STRING COM ASPAS SIMPLES
        # ----------------------------------------------------

        if caractere == "'":
            resultado.append(" ")
            i += 1

            while i < tamanho:
                if sql[i] == "'":

                    # Escape SQL padrão:
                    # 'João''s'
                    if (
                        i + 1 < tamanho
                        and sql[i + 1] == "'"
                    ):
                        resultado.extend(
                            [" ", " "]
                        )
                        i += 2
                        continue

                    resultado.append(" ")
                    i += 1
                    break

                resultado.append(" ")
                i += 1

            continue

        # ----------------------------------------------------
        # IDENTIFICADOR COM ASPAS DUPLAS
        # ----------------------------------------------------

        if caractere == '"':
            resultado.append(" ")
            i += 1

            while i < tamanho:
                if sql[i] == '"':

                    # Escape:
                    # "nome""especial"
                    if (
                        i + 1 < tamanho
                        and sql[i + 1] == '"'
                    ):
                        resultado.extend(
                            [" ", " "]
                        )
                        i += 2
                        continue

                    resultado.append(" ")
                    i += 1
                    break

                resultado.append(" ")
                i += 1

            continue

        # ----------------------------------------------------
        # DOLLAR QUOTING DO POSTGRESQL
        # ----------------------------------------------------

        if caractere == "$":
            marcador = _eh_inicio_dollar_quote(
                sql,
                i,
            )

            if marcador is not None:
                resultado.extend(
                    " " * len(marcador)
                )

                i += len(marcador)

                fim = sql.find(
                    marcador,
                    i,
                )

                if fim == -1:
                    resultado.extend(
                        " " * (
                            tamanho - i
                        )
                    )
                    i = tamanho
                    continue

                resultado.extend(
                    " " * (
                        fim - i
                    )
                )

                resultado.extend(
                    " " * len(marcador)
                )

                i = (
                    fim
                    + len(marcador)
                )

                continue

        # ----------------------------------------------------
        # COMENTÁRIO DE LINHA
        # ----------------------------------------------------

        if (
            caractere == "-"
            and i + 1 < tamanho
            and sql[i + 1] == "-"
        ):
            resultado.extend(
                [" ", " "]
            )
            i += 2

            while (
                i < tamanho
                and sql[i] != "\n"
            ):
                resultado.append(" ")
                i += 1

            if i < tamanho:
                resultado.append(
                    "\n"
                )
                i += 1

            continue

        # ----------------------------------------------------
        # COMENTÁRIO DE BLOCO
        # ----------------------------------------------------

        if (
            caractere == "/"
            and i + 1 < tamanho
            and sql[i + 1] == "*"
        ):
            resultado.extend(
                [" ", " "]
            )
            i += 2

            profundidade = 1

            while (
                i < tamanho
                and profundidade > 0
            ):

                if (
                    i + 1 < tamanho
                    and sql[i] == "/"
                    and sql[i + 1] == "*"
                ):
                    resultado.extend(
                        [" ", " "]
                    )
                    profundidade += 1
                    i += 2
                    continue

                if (
                    i + 1 < tamanho
                    and sql[i] == "*"
                    and sql[i + 1] == "/"
                ):
                    resultado.extend(
                        [" ", " "]
                    )
                    profundidade -= 1
                    i += 2
                    continue

                if sql[i] == "\n":
                    resultado.append(
                        "\n"
                    )
                else:
                    resultado.append(
                        " "
                    )

                i += 1

            continue

        # ----------------------------------------------------
        # SQL EXECUTÁVEL
        # ----------------------------------------------------

        resultado.append(
            caractere
        )

        i += 1

    return "".join(
        resultado
    )


# ============================================================
# LIMPEZA DO SQL
# ============================================================

def limpar_sql(
    sql: str,
) -> str:
    """
    Normaliza espaços do SQL mantendo strings intactas.

    Remove somente o ponto e vírgula terminal real,
    quando ele estiver fora de strings e comentários.
    """

    sql = sql.strip()

    if not sql:
        return ""

    analisavel = (
        _mascarar_conteudo_nao_executavel(
            sql
        )
    )

    # --------------------------------------------------------
    # REMOVE SOMENTE ; TERMINAL REAL
    # --------------------------------------------------------

    ultimo_nao_espaco = None

    for indice in range(
        len(analisavel) - 1,
        -1,
        -1,
    ):
        if not analisavel[indice].isspace():
            ultimo_nao_espaco = indice
            break

    if (
        ultimo_nao_espaco is not None
        and analisavel[
            ultimo_nao_espaco
        ] == ";"
    ):
        sql = (
            sql[:ultimo_nao_espaco]
            + sql[
                ultimo_nao_espaco + 1:
            ]
        )

    # --------------------------------------------------------
    # NORMALIZA ESPAÇOS SOMENTE FORA DE LITERAIS
    #
    # Mantemos o SQL original nas strings.
    # Para execução, apenas strip já é suficiente.
    # --------------------------------------------------------

    return sql.strip()


# ============================================================
# TOKENS SQL
# ============================================================

def _obter_tokens(
    sql: str,
) -> set[str]:
    """
    Extrai tokens SQL alfabéticos em maiúsculas,
    ignorando:

    - strings;
    - comentários;
    - identificadores citados;
    - dollar quoted strings.
    """

    analisavel = (
        _mascarar_conteudo_nao_executavel(
            sql
        )
    )

    return set(
        re.findall(
            r"\b[A-Za-z_]+\b",
            analisavel.upper(),
        )
    )


# ============================================================
# MÚLTIPLAS INSTRUÇÕES
# ============================================================

def _validar_instrucao_unica(
    sql: str,
):
    """
    Impede múltiplas instruções SQL.

    Ponto e vírgula dentro de:
    - strings;
    - comentários;
    - identificadores;
    - dollar quoting;

    NÃO é considerado separador de comandos.
    """

    analisavel = (
        _mascarar_conteudo_nao_executavel(
            sql
        )
    )

    posicoes = [
        indice
        for indice, caractere
        in enumerate(analisavel)
        if caractere == ";"
    ]

    if not posicoes:
        return

    # Após limpar_sql(), um único ponto e vírgula
    # terminal já foi removido.
    #
    # Portanto, qualquer ; restante fora de
    # conteúdo mascarado representa tentativa
    # de múltiplas instruções.
    raise QueryValidationError(
        "MULTIPLE_STATEMENTS_ERROR",
        (
            "Múltiplas instruções "
            "não são permitidas."
        ),
    )


# ============================================================
# COMANDO INICIAL
# ============================================================

def _validar_comando_inicial(
    sql: str,
):
    """
    Permite apenas consultas que iniciem por:

    SELECT ...
    ou
    WITH ... SELECT ...

    WITH é aceito exclusivamente para CTEs de leitura.
    """

    analisavel = (
        _mascarar_conteudo_nao_executavel(
            sql
        )
    ).strip()

    correspondencia = re.match(
        r"([A-Za-z_]+)",
        analisavel,
    )

    if correspondencia is None:
        raise QueryValidationError(
            "SQL_VALIDATION_ERROR",
            (
                "Não foi possível identificar "
                "o comando SQL inicial."
            ),
        )

    primeira_palavra = (
        correspondencia
        .group(1)
        .upper()
    )

    if primeira_palavra not in {
        "SELECT",
        "WITH",
    }:
        raise QueryValidationError(
            "SQL_VALIDATION_ERROR",
            (
                "Somente consultas de leitura "
                "(SELECT ou WITH ... SELECT) "
                "são permitidas."
            ),
        )

    if primeira_palavra == "WITH":
        tokens = _obter_tokens(
            sql
        )

        if "SELECT" not in tokens:
            raise QueryValidationError(
                "SQL_VALIDATION_ERROR",
                (
                    "CTEs são permitidas somente "
                    "quando resultam em uma "
                    "consulta SELECT."
                ),
            )


# ============================================================
# VALIDAÇÃO PRINCIPAL
# ============================================================

def validar_sql(
    sql: str,
) -> str:
    if (
        not sql
        or not sql.strip()
    ):
        raise QueryValidationError(
            "SQL_VALIDATION_ERROR",
            "Consulta vazia não é permitida.",
        )

    limpo = limpar_sql(
        sql
    )

    # --------------------------------------------------------
    # 1. IMPEDE MÚLTIPLAS INSTRUÇÕES
    # --------------------------------------------------------

    _validar_instrucao_unica(
        limpo
    )

    # --------------------------------------------------------
    # 2. BLOQUEIA COMANDOS PERIGOSOS
    #
    # A análise ignora palavras que aparecem somente
    # dentro de strings e comentários.
    #
    # Exemplo permitido:
    #
    # SELECT 'COMMENT; DROP; DELETE'
    #
    # pois são apenas dados textuais.
    # --------------------------------------------------------

    tokens = _obter_tokens(
        limpo
    )

    presentes = sorted(
        BLOCKED_KEYWORDS
        & tokens
    )

    if presentes:
        raise QueryValidationError(
            "SQL_VALIDATION_ERROR",
            (
                "Consulta não permitida. "
                "Comando(s) bloqueado(s): "
                f"{', '.join(presentes)}."
            ),
        )

    # --------------------------------------------------------
    # 3. VALIDA SELECT OU CTE DE LEITURA
    # --------------------------------------------------------

    _validar_comando_inicial(
        limpo
    )

    return limpo
