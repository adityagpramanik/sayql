from __future__ import annotations

from app.query_former.validator import validate_sql


def compile_query(sql: str) -> str:
    cleaned = sql.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```sql", "").replace("```", "").strip()
    return validate_sql(cleaned)
