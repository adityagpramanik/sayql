from __future__ import annotations

import re


def validate_sql(sql: str) -> str:
    cleaned = sql.strip()
    if not cleaned:
        raise ValueError("Generated SQL is empty.")

    if not re.match(r"^select\b", cleaned, flags=re.IGNORECASE):
        raise ValueError("Only SELECT statements are allowed.")

    forbidden = [
        "; drop",
        "; delete",
        "; update",
        "insert into",
        "update ",
        "delete from",
        "alter table",
        "drop table",
        "create table",
    ]

    lowered = cleaned.lower()
    for token in forbidden:
        if token in lowered:
            raise ValueError("Unsafe SQL detected.")

    return cleaned
