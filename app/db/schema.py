from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import inspect

from app.db.postgres import engine


BASE_DIR = Path(__file__).resolve().parents[1]
SCHEMA_FILE = BASE_DIR / "metadata" / "schema.json"

MANUAL_RELATIONSHIPS = {
    "facility": {
        "state_id": {"table": "states", "column": "id"},
        "district_id": {"table": "district", "column": "id"},
        "sub_district_id": {"table": "sub_district", "column": "id"},
    }
}


def load_manual_schema() -> dict[str, Any]:
    if not SCHEMA_FILE.exists():
        return {"tables": {}, "relationships": {}}

    with SCHEMA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_schema_from_db() -> dict[str, Any]:
    inspector = inspect(engine)
    schema: dict[str, Any] = {"tables": {}, "relationships": {}}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema["tables"][table_name] = [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column.get("nullable", True),
                "default": column.get("default"),
            }
            for column in columns
        ]

        for foreign_key in inspector.get_foreign_keys(table_name):
            referred_table = foreign_key.get("referred_table")
            constrained_columns = foreign_key.get("constrained_columns", [])
            referred_columns = foreign_key.get("referred_columns", [])

            for source_column, target_column in zip(constrained_columns, referred_columns):
                schema["relationships"][f"{table_name}.{source_column}"] = {
                    "source_table": table_name,
                    "source_column": source_column,
                    "target_table": referred_table,
                    "target_column": target_column,
                }

    return schema


def build_schema_metadata() -> dict[str, Any]:
    manual_schema = load_manual_schema()

    try:
        db_schema = extract_schema_from_db()
    except Exception:
        db_schema = {"tables": {}, "relationships": {}}

    combined = {"tables": db_schema.get("tables", {}), "relationships": db_schema.get("relationships", {})}

    for table_name, table_columns in manual_schema.get("tables", {}).items():
        combined["tables"].setdefault(table_name, table_columns)

    for table_name, mapping in manual_schema.get("relationships", {}).items():
        combined["relationships"].setdefault(table_name, mapping)

    for table_name, column_map in MANUAL_RELATIONSHIPS.items():
        if table_name not in combined["tables"]:
            continue

        for column_name, target in column_map.items():
            combined["relationships"].setdefault(f"{table_name}.{column_name}", {
                "source_table": table_name,
                "source_column": column_name,
                "target_table": target["table"],
                "target_column": target["column"],
            })

    return combined


def get_schema() -> dict[str, Any]:
    return build_schema_metadata()
