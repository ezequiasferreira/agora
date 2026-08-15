import re


# Palavras-chave proibidas — qualquer ocorrência como token
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


_COMMENT_BLOCK = re.compile(
    r"/\*.*?\*/",
    re.DOTALL,
)

_COMMENT_LINE = re.compile(
    r"--[^\n]*"
)


class QueryValidationError(Exception):
    def __init__(
        self,
        error_type: str,
        message: str,
    ):
        super().__init__(message)

        self.error_type = error_type
        self.message = message


def limpar_sql(
    sql: str,
) -> str:
    """
    Remove comentários e normaliza espaços,
    mantendo o SQL executável.
    """

    sem_bloco = _COMMENT_BLOCK.sub(
        " ",
        sql,
    )

    sem_linha = _COMMENT_LINE.sub(
        " ",
        sem_bloco,
    )

    colapsado = re.sub(
        r"\s+",
        " ",
        sem_linha,
    )

    limpo = colapsado.strip()

    while limpo.endswith(";"):
        limpo = limpo[:-1].rstrip()

    return limpo


def _obter_tokens(
    sql: str,
) -> set[str]:
    """
    Extrai tokens alfabéticos do SQL em maiúsculas.
    """

    return set(
        re.findall(
            r"\b[A-Za-z_]+\b",
            sql.upper(),
        )
    )


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

    primeira_palavra = (
        sql.split(
            " ",
            1,
        )[0]
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
                    "quando resultam em uma consulta SELECT."
                ),
            )


def validar_sql(
    sql: str,
) -> str:
    if not sql or not sql.strip():
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

    partes = [
        parte
        for parte in limpo.split(";")
        if parte.strip()
    ]

    if len(partes) > 1:
        raise QueryValidationError(
            "MULTIPLE_STATEMENTS_ERROR",
            "Múltiplas instruções não são permitidas.",
        )

    # --------------------------------------------------------
    # 2. BLOQUEIA COMANDOS PERIGOSOS
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
