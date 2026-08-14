from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    sql: str = Field(..., min_length=1)


class QueryResponse(BaseModel):
    success: bool
    columns: list[str]
    rows: list[list[Any]]
    row_count: int
    execution_time_ms: int
    executed_sql: str


class ErrorResponse(BaseModel):
    success: bool = False
    error_type: str
    message: str


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
    )


class AskResponse(BaseModel):
    success: bool
    status: str
    answer: str | None = None
    generated_sql: str | None = None
    columns: list[str] | None = None
    rows: list[list[Any]] | None = None
    row_count: int | None = None
    execution_time_ms: int | None = None
