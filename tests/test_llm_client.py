import pytest

from app.llm.client import OpenRouterClient, OllamaClient, create_llm_client


def test_create_llm_client_selects_configured_provider():
    assert isinstance(create_llm_client("ollama"), OllamaClient)
    assert isinstance(create_llm_client("openrouter"), OpenRouterClient)


def test_create_llm_client_rejects_unknown_provider():
    with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
        create_llm_client("unknown")


def test_openrouter_client_parses_chat_completion(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "SELECT 1"}}]}

    def post(url, *, headers, json, timeout):
        assert url == "https://router.test/chat/completions"
        assert headers == {"Authorization": "Bearer test-key"}
        assert json["model"] == "test-model"
        assert json["messages"] == [{"role": "user", "content": "Give SQL"}]
        assert timeout == 60
        return Response()

    monkeypatch.setattr("app.llm.client.requests.post", post)

    client = OpenRouterClient(
        base_url="https://router.test/",
        api_key="test-key",
        model="test-model",
    )
    assert client.generate("Give SQL") == "SELECT 1"