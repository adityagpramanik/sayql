from __future__ import annotations

from typing import Optional

import requests

from app.config import settings


class OllamaError(RuntimeError):
    """Raised when Ollama cannot generate a usable response."""


class OllamaClient:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None) -> None:
        self.base_url = (base_url or settings.OLLAMA_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.ok
        except requests.RequestException:
            return False

    def generate(self, prompt: str) -> str:
        if not self.is_available():
            raise OllamaError(
                f"Ollama is not reachable at {self.base_url}. "
                "Start Ollama and verify OLLAMA_URL."
            )

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "think": False},
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else "unknown"
            raise OllamaError(
                f"Ollama rejected the generation request with HTTP {status_code}. "
                f"Verify that model '{self.model}' is installed."
            ) from exc
        except requests.RequestException as exc:
            raise OllamaError(f"Ollama generation request failed: {exc}") from exc
        except ValueError as exc:
            raise OllamaError("Ollama returned invalid JSON from /api/generate.") from exc

        if not isinstance(payload, dict):
            raise OllamaError("Ollama returned an unexpected response format.")

        generated_sql = str(payload.get("response", "")).strip()
        if not generated_sql:
            raise OllamaError("Ollama returned an empty response. Check the selected model.")
        return generated_sql



ollama_client = OllamaClient()
