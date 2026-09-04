# SayQL — Implementation Plan

## 0. Objective

Build a local-first, cloud-agnostic Natural Language to SQL (NL2SQL) system.

Current database:

PostgreSQL database containing healthcare facility/location data.

The user should eventually be able to ask questions such as:

- "Show all hospitals in Karnataka."
- "How many facilities are there in each district?"
- "Which districts have the most PHCs?"
- "Show CHCs in Bangalore rural areas."
- "How many public facilities are in each state?"
- "List facilities within a particular district."
- "Which states have the highest number of rural facilities?"

The system must:

1. Understand the natural-language question.
2. Retrieve relevant database metadata.
3. Generate a structured query plan.
4. Convert the query plan into safe PostgreSQL SQL.
5. Execute the SQL.
6. Return the result and generated SQL.
7. Eventually support RAG and an agentic workflow.

---

# 1. Technology Stack

## Current

- Python 3.12+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Ollama
- Qwen3 14B
- uv for Python dependency management

## Future

- Qdrant — Vector DB (Vector Database)
- Qwen3-Embedding — embedding model
- Qwen3-Reranker — retrieval reranking
- Parquet — data-lake storage format
- Spark — distributed data processing
- MinIO — S3-compatible object storage
- vLLM — production LLM inference
- Redis — caching
- OpenTelemetry — observability

Do NOT introduce LangChain/LlamaIndex initially.

Implement the core pipeline directly so the behavior is understandable and testable.

---

# 2. Repository Structure

Create:

nl-data-analyst/

├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── query.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── postgres.py
│   │   └── schema.py
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   └── client.py
│   │
│   ├── query_former/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── prompt.py
│   │   ├── service.py
│   │   ├── sql_compiler.py
│   │   └── validator.py
│   │
│   └── rag/
│       └── __init__.py
│
├── metadata/
│   ├── schema.json
│   └── business_metrics.yaml
│
├── tests/
│   ├── test_schema.py
│   ├── test_query_former.py
│   ├── test_sql_compiler.py
│   └── evaluation/
│       └── questions.json
│
├── scripts/
│   └── extract_schema.py
│
├── .env
├── .env.example
├── .gitignore
├── pyproject.toml
├── Dockerfile
└── README.md

---

# 3. PostgreSQL Database Schema

The current database contains four tables.

## district

- id: integer
- name: character varying

## states

- id: integer
- name: character varying

## sub_district

- id: integer
- name: character varying

## facility

- id: integer
- state_id: integer
- district_id: integer
- sub_district_id: integer
- type: facility_type
- name: character varying
- address: text
- latitude: character varying
- longitude: character varying
- location_type: location_type

Custom PostgreSQL enum types:

facility_type:

- chc
- dis_h
- phc
- sub_cen
- s_t_h

location_type:

- rural
- urban
- public

---

# 4. Expected Relationships

The expected logical relationships are:

facility.state_id
    →
states.id

facility.district_id
    →
district.id

facility.sub_district_id
    →
sub_district.id

IMPORTANT:

Do not assume these relationships blindly.

The schema extraction code must inspect PostgreSQL PK/FK metadata and use the actual constraints when available.

If FK constraints are not present, support manually configured relationships in metadata/schema.json.

---

# 5. Environment Configuration

Create `.env.example`:

DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/database_name

OLLAMA_URL=http://localhost:11434

OLLAMA_MODEL=qwen3:14b

Create `app/config.py`.

Use Pydantic Settings.

Never hard-code:

- database credentials
- Ollama URL
- model name

---

# 6. PostgreSQL Connection

Implement:

app/db/postgres.py

Use SQLAlchemy.

Requirements:

- Create a reusable SQLAlchemy engine.
- Configure connection pooling.
- Expose a function to execute read-only queries.
- Return rows as dictionaries.
- Do not create a new engine per request.

Example interface:

```python
def execute_query(sql: str) -> list[dict]:
    ...