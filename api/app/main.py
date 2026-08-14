from contextlib import asynccontextmanager

import psycopg2
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import db
from app.ask_service import processar_pergunta
from app.query_validator import (
    QueryValidationError,
    validar_sql,
)
from app.schemas import (
    AskRequest,
    AskResponse,
    ErrorResponse,
    QueryRequest,
    QueryResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.configurar_pool()
    yield
    db.fechar_pool()


app = FastAPI(
    title="Ágora API",
    description=(
        "API segura de consultas e perguntas "
        "em linguagem natural sobre os dados do Ágora."
    ),
    version="0.2.0",
    lifespan=lifespan,
)


# ============================================================
# CORS — INTERFACE WEB DO MVP
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    banco = db.verificar_conexao()

    if banco:
        return {
            "status": "ok",
            "database": "ok",
        }

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "degraded",
            "database": "error",
        },
    )


# ============================================================
# CLASSIFICAÇÃO DE ERROS DO BANCO
# ============================================================

def _classificar_erro_banco(
    exc: Exception,
) -> ErrorResponse:
    texto = str(exc)

    if (
        "canceling statement due to "
        "statement timeout"
    ) in texto:
        return ErrorResponse(
            error_type="QUERY_TIMEOUT",
            message=(
                "A consulta excedeu o tempo "
                "máximo de execução."
            ),
        )

    if (
        "read-only transaction" in texto
        or "cannot execute" in texto
    ):
        return ErrorResponse(
            error_type="SQL_VALIDATION_ERROR",
            message=(
                "Consulta não permitida no banco "
                "somente leitura."
            ),
        )

    return ErrorResponse(
        error_type="DB_QUERY_ERROR",
        message=(
            f"Erro ao executar a consulta: {exc}"
        ),
    )


# ============================================================
# QUERY — SQL SEGURO
# ============================================================

@app.post(
    "/query",
    response_model=QueryResponse,
)
def executar_query(
    requisicao: QueryRequest,
):
    try:
        sql_limpo = validar_sql(
            requisicao.sql
        )

    except QueryValidationError as erro:
        return JSONResponse(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            content=ErrorResponse(
                error_type=erro.error_type,
                message=erro.message,
            ).model_dump(),
        )

    try:
        colunas, linhas, duracao = (
            db.executar_consulta(
                sql_limpo
            )
        )

    except psycopg2.Error as erro:
        resposta_erro = (
            _classificar_erro_banco(
                erro
            )
        )

        status_code = (
            status.HTTP_504_GATEWAY_TIMEOUT
        )

        if (
            resposta_erro.error_type
            != "QUERY_TIMEOUT"
        ):
            status_code = (
                status.HTTP_400_BAD_REQUEST
            )

            if (
                resposta_erro.error_type
                != "SQL_VALIDATION_ERROR"
            ):
                status_code = (
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return JSONResponse(
            status_code=status_code,
            content=(
                resposta_erro.model_dump()
            ),
        )

    except Exception as erro:
        return JSONResponse(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            content=ErrorResponse(
                error_type="INTERNAL_ERROR",
                message=str(erro),
            ).model_dump(),
        )

    return QueryResponse(
        success=True,
        columns=colunas,
        rows=linhas,
        row_count=len(linhas),
        execution_time_ms=duracao,
        executed_sql=sql_limpo,
    )


# ============================================================
# ASK — PERGUNTA EM LINGUAGEM NATURAL
# ============================================================

@app.post(
    "/ask",
    response_model=AskResponse,
)
def perguntar(
    requisicao: AskRequest,
):
    try:
        resultado = processar_pergunta(
            requisicao.question
        )

    except Exception:
        return JSONResponse(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            content=AskResponse(
                success=False,
                status="INTERNAL_ERROR",
                answer=(
                    "Ocorreu um erro interno ao "
                    "processar a pergunta."
                ),
            ).model_dump(),
        )

    if not resultado.get(
        "success"
    ):
        return JSONResponse(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            content=AskResponse(
                success=False,
                status=resultado.get(
                    "status",
                    "INTERNAL_ERROR",
                ),
                answer=resultado.get(
                    "answer"
                ),
                generated_sql=resultado.get(
                    "generated_sql"
                ),
                columns=resultado.get(
                    "columns"
                ),
                rows=resultado.get(
                    "rows"
                ),
                row_count=resultado.get(
                    "row_count"
                ),
                execution_time_ms=resultado.get(
                    "execution_time_ms"
                ),
            ).model_dump(),
        )

    return AskResponse(
        success=True,
        status=resultado.get(
            "status",
            "ANSWER",
        ),
        answer=resultado.get(
            "answer"
        ),
        generated_sql=resultado.get(
            "generated_sql"
        ),
        columns=resultado.get(
            "columns"
        ),
        rows=resultado.get(
            "rows"
        ),
        row_count=resultado.get(
            "row_count"
        ),
        execution_time_ms=resultado.get(
            "execution_time_ms"
        ),
    )
