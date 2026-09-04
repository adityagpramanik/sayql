# SayQL

A local-first Natural Language to SQL application for PostgreSQL healthcare facility data.

## Features
- FastAPI backend
- PostgreSQL metadata inspection
- SQLAlchemy connection pooling
- Configurable Ollama or OpenRouter SQL generation
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

4. Update database and LLM settings in `.env` if needed. Set `LLM_PROVIDER=openrouter`
   and provide `OPENROUTER_API_KEY` to use OpenRouter.

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
This project is intentionally lightweight and uses direct SQLAlchemy and HTTP LLM
integrations without LangChain or LlamaIndex.
