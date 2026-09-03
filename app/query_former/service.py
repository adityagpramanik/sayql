from __future__ import annotations

from app.llm.client import ollama_client
from app.query_former.prompt import PROMPT_TEMPLATE
from app.query_former.sql_compiler import compile_query


def generate_sql(question: str) -> str:
    prompt = PROMPT_TEMPLATE.format(question=question)
    raw_sql = ollama_client.generate(prompt)
    return compile_query(raw_sql)
