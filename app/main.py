from fastapi import FastAPI

from app.api.routes.query import router as query_router

app = FastAPI(title="NL Data Analyst", version="0.1.0")
app.include_router(query_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "NL Data Analyst API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}