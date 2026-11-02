import asyncio
import json
import pytest
from unittest.mock import AsyncMock, patch
import httpx

from src.generator.ollama_client import OllamaClient, OllamaClientError


def test_ollama_client_healthcheck_success():
    client = OllamaClient(base_url="http://localhost:11434")

    mock_resp = httpx.Response(200, json={"models": []})
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
        is_healthy = asyncio.run(client.is_healthy())
        assert is_healthy is True


def test_ollama_client_generate_json_success():
    client = OllamaClient(base_url="http://localhost:11434")

    expected_content = {
        "question": "What is Kubernetes?",
        "options": ["A container orchestrator", "An OS", "A language", "A browser"],
        "correct_option_id": 0,
        "explanation": "Kubernetes is an open-source container orchestration system.",
    }

    req = httpx.Request("POST", "http://localhost:11434/api/chat")
    mock_resp = httpx.Response(
        200,
        request=req,
        json={"message": {"role": "assistant", "content": json.dumps(expected_content)}},
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_resp):
        result = asyncio.run(client.generate_json("User prompt", "System prompt"))
        assert result == expected_content


def test_ollama_client_retries_and_raises_error():
    client = OllamaClient(base_url="http://localhost:11434", max_retries=2)

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        side_effect=httpx.ConnectError("Failed to connect"),
    ):
        with pytest.raises(OllamaClientError):
            asyncio.run(client.generate_json("User prompt", "System prompt"))