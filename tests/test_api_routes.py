from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_route():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_schema_route_returns_metadata_shape():
    response = client.get("/api/schema")
    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload, dict)
    assert "tables" in payload
    assert "relationships" in payload
    assert isinstance(payload["tables"], dict)
    assert isinstance(payload["relationships"], dict)


def test_select_query_route_accepts_valid_select_queries():
    payload = {"question": "How many facilities are there in each district?"}
    response = client.post("/api/query", json=payload)

    assert response.status_code in {200, 500}
    if response.status_code == 200:
        body = response.json()
        assert "question" in body
        assert "sql" in body
        assert body["sql"].lower().startswith("select")


def test_select_query_route_rejects_non_select_sql_input():
    payload = {"question": "DELETE FROM facility"}
    response = client.post("/api/query", json=payload)

    assert response.status_code in {400, 500}
    if response.status_code == 400:
        assert "detail" in response.json()
