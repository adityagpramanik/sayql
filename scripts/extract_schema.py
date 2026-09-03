from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import create_engine, inspect, text

from app.config import settings


def extract_schema() -> dict:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    inspector = inspect(engine)

    schema = {"tables": {}, "relationships": {}}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema["tables"][table_name] = [
            {"name": column["name"], "type": str(column["type"]), "nullable": column.get("nullable", True)}
            for column in columns
        ]

        for fk in inspector.get_foreign_keys(table_name):
            for source_column, target_column in zip(fk.get("constrained_columns", []), fk.get("referred_columns", [])):
                schema["relationships"][f"{table_name}.{source_column}"] = {
                    "source_table": table_name,
                    "source_column": source_column,
                    "target_table": fk.get("referred_table"),
                    "target_column": target_column,
                }

    output_path = Path(__file__).resolve().parents[1] / "metadata" / "schema.json"
    output_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    return schema


if __name__ == "__main__":
    extract_schema()
