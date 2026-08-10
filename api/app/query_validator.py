import re

# Palavras-chave proibidas — qualquer ocorrência como token torna a consulta inválida.
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

_COMMENT_BLOCK = re.compile(r"/\*.*?\*/", re.DOTALL)
_COMMENT_LINE = re.compile(r"--[^\n]*")


class QueryValidationError(Exception):
    def __init__(self, error_type: str, message: str):
        super().__init__(message)
        self.error_type = error_type
        self.message = message


def limpar_sql(sql: str) -> str:
    """Remove comentários e normaliza espaços, mantendo o SQL executável."""
    sem_bloco = _COMMENT_BLOCK.sub(" ", sql)
    sem_linha = _COMMENT_LINE.sub(" ", sem_bloco)
    colsado = re.sub(r"\s+", " ", sem_linha)
    limpo = colsado.strip()
    while limpo.endswith(";"):
        limpo = limpo[:-1].rstrip()
    return limpo


def validar_sql(sql: str) -> str:
    if not sql or not sql.strip():
        raise QueryValidationError(
            "SQL_VALIDATION_ERROR",
            "Consulta vazia não é permitida.",
        )

    limpo = limpar_sql(sql)

    # 1. Primeiro comando precisa ser SELECT.
    primeira_palavra = limpo.split(" ", 1)[0].upper()
    if primeira_palavra != "SELECT":
        raise QueryValidationError(
            "SQL_VALIDATION_ERROR",
            "Somente consultas de leitura (SELECT) são permitidas.",
        )

    # 2. Impede múltiplas instruções separadas por ';'.
    partes = [p for p in limpo.split(";") if p.strip()]
    if len(partes) > 1:
        raise QueryValidationError(
            "MULTIPLE_STATEMENTS_ERROR",
            "Múltiplas instruções não são permitidas.",
        )

    # 3. Bloqueia comandos perigosos por token.
    tokens = set(re.findall(r"\b[A-Za-z_]+\b", limpo.upper()))
    presentes = sorted(BLOCKED_KEYWORDS & tokens)
    if presentes:
        raise QueryValidationError(
            "SQL_VALIDATION_ERROR",
            f"Consulta não permitida. Comando(s) bloqueado(s): "
            f"{', '.join(presentes)}.",
        )

    return limpo