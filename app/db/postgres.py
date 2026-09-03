from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine: Engine = create_engine(
    settings.resolved_database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def execute_query(sql: str) -> list[dict]:
    """Execute a read-only SQL query and return rows as dictionaries."""
    statement = sql.strip()
    if not statement:
        raise ValueError("SQL statement cannot be empty.")

    if not statement.lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed for read-only execution.")

    with engine.connect() as connection:
        result = connection.execute(text(statement))
        return [dict(row) for row in result.mappings().all()]


def get_session():
    return SessionLocal()
