# SayQL

A local-first Natural Language to SQL application for PostgreSQL healthcare facility data.

## Features
- FastAPI backend
- PostgreSQL metadata inspection
- SQLAlchemy connection pooling
- Ollama-backed SQL generation
- Read-only query execution
- schema and SQL validation layers

## Setup

1. Create a virtual environment:
   python -m venv .venv
   source .venv/bin/activate

2. Install dependencies:
   pip install -r requirements.txt

3. Copy environment file:
   cp .env.example .env

4. Update database settings in `.env` if needed.

5. Run the app:
   uvicorn app.main:app --reload

## API
- GET /
- GET /health
- GET /api/schema
- POST /api/query
- POST /api/rawQuery

Example request:

```json
{
  "question": "How many facilities are there in each district?"
}
```

## Notes
This project is intentionally lightweight and uses direct SQLAlchemy + Ollama integration without LangChain or LlamaIndex.
