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