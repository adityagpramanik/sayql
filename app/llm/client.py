from __future__ import annotations

from typing import Optional, Protocol

import requests

from app.config import settings


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...


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


class OpenRouterError(RuntimeError):
    """Raised when OpenRouter cannot generate a usable response."""


class OpenRouterClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.base_url = (base_url or settings.OPENROUTER_URL).rstrip("/")
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL

    def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise OpenRouterError(
                "OPENROUTER_API_KEY is not configured. Set it in the environment."
            )

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "X-OpenRouter-Cache": "true" 
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "reasoning": {
                        "enabled": False
                    },
                    "stream": False
                },
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else "unknown"
            raise OpenRouterError(
                f"OpenRouter rejected the generation request with HTTP {status_code}."
            ) from exc
        except requests.RequestException as exc:
            raise OpenRouterError(f"OpenRouter generation request failed: {exc}") from exc
        except ValueError as exc:
            raise OpenRouterError("OpenRouter returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise OpenRouterError("OpenRouter returned an unexpected response format.")

        try:
            generated_sql = str(payload["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenRouterError("OpenRouter returned no generated content.") from exc

        if not generated_sql:
            raise OpenRouterError("OpenRouter returned an empty response.")
        return generated_sql


def create_llm_client(provider: Optional[str] = None) -> LLMClient:
    selected_provider = (provider or settings.LLM_PROVIDER).strip().lower()
    clients = {
        "ollama": OllamaClient,
        "openrouter": OpenRouterClient,
    }
    client_class = clients.get(selected_provider)
    if client_class is None:
        supported = ", ".join(sorted(clients))
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{selected_provider}'. Choose one of: {supported}."
        )
    return client_class()


llm_client = create_llm_client()
