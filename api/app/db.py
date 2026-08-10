import time

import psycopg2
from psycopg2.pool import ThreadedConnectionPool

from app.config import settings

_pool: ThreadedConnectionPool | None = None


def build_dsn(*, connect_timeout: int = 2) -> str:
    return (
        f"host={settings.db_host} port={settings.db_port} "
        f"dbname={settings.db_name} user={settings.db_user} "
        f"password={settings.db_password} "
        f"connect_timeout={connect_timeout} "
        f"options='-c statement_timeout={settings.query_timeout_ms}'"
    )


def criar_pool() -> ThreadedConnectionPool:
    return ThreadedConnectionPool(1, settings.pool_max, build_dsn())


def verificar_conexao() -> bool:
    try:
        conn = psycopg2.connect(build_dsn())
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        finally:
            conn.close()
        return True
    except Exception:
        return False


def configurar_pool() -> None:
    global _pool
    _pool = criar_pool()


def fechar_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None


def executar_consulta(
    sql: str,
) -> tuple[list[str], list[list], int]:
    if _pool is None:
        configurar_pool()
    conn = _pool.getconn()
    inicio = time.perf_counter()
    try:
        conn.set_session(autocommit=True, readonly=True)
        with conn.cursor() as cur:
            cur.execute(sql)
            if cur.description is None:
                colunas: list[str] = []
                linhas: list[list] = []
            else:
                colunas = [desc.name for desc in cur.description]
                linhas = cur.fetchmany(settings.max_rows)
        duracao = int((time.perf_counter() - inicio) * 1000)
    except Exception:
        _pool.putconn(conn, close=True)
        raise
    else:
        _pool.putconn(conn)
        return colunas, linhas, duracao