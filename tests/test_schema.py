import json
from pathlib import Path


def test_schema_file_exists_and_has_expected_tables():
    schema_path = Path("metadata/schema.json")
    assert schema_path.exists(), "schema.json should exist"

    with schema_path.open("r", encoding="utf-8") as f:
        schema = json.load(f)

    assert "tables" in schema
    assert "facility" in schema["tables"]
    assert "district" in schema["tables"]
    assert "states" in schema["tables"]
    assert "sub_district" in schema["tables"]
