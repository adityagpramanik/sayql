from __future__ import annotations

from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

try:
    from pydantic import BaseModel, ConfigDict
    from pydantic_settings import BaseSettings
except ImportError:  # pragma: no cover
    from pydantic import BaseModel, BaseSettings
    ConfigDict = dict


class Settings(BaseSettings):
    LLM_PROVIDER: str = "ollama"
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "database_name"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"
    OPENROUTER_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "minimax/minimax-m3:free"

    model_config = ConfigDict(
        env_file=str(Path(__file__).resolve().parents[1] / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def resolved_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+psycopg://{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
