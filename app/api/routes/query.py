from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db.postgres import execute_query
from app.db.schema import get_schema
from app.query_former.service import generate_sql

router = APIRouter(prefix="/api", tags=["query"])


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Natural language question to convert into SQL.")

class RawQueryRequest(BaseModel):
    raw_query: str = Field(..., min_length=10, description="Actual sql raw query to directly run on db.")


class QueryResponse(BaseModel):
    question: str
    sql: str
    results: list[dict]


class RawQueryResponse(BaseModel):
    results: list[dict]


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/schema")
def schema_endpoint() -> dict:
    return get_schema()


@router.post("/query", response_model=QueryResponse)
def run_query(payload: QueryRequest) -> QueryResponse:
    try:
        sql = generate_sql(payload.question)
        rows = execute_query(sql)
        return QueryResponse(question=payload.question, sql=sql, results=rows)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive failure path
        raise HTTPException(status_code=500, detail=f"Query execution failed: {exc}") from exc

@router.post("/rawQuery", response_model=RawQueryResponse)
def run_raw_query(payload: RawQueryRequest) -> RawQueryResponse:
    try:
        rows = execute_query(payload.raw_query)
        return RawQueryResponse(results=rows)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive failure path
        raise HTTPException(status_code=500, detail=f"Query execution failed: {exc}") from exc
