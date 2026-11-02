"""Asynchronous HTTP client for local Ollama instance."""

import json
import logging
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class OllamaClientError(Exception):
    """Base exception for Ollama client errors."""
    pass


class OllamaClient:
    """Communicates with a local Ollama instance running in Docker."""

    def __init__(
        self,
        base_url: str = "http://ollama:11434",
        model: str = "llama3.2:3b",
        timeout: float = 60.0,
        temperature: float = 0.7,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        self.max_retries = max_retries

    async def is_healthy(self) -> bool:
        """Ping Ollama API to check if it's responsive and available."""
        url = f"{self.base_url}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    logger.info("Ollama healthcheck succeeded.")
                    return True
                logger.warning(f"Ollama healthcheck returned status {response.status_code}")
                return False
        except Exception as exc:
            logger.warning(f"Ollama healthcheck failed: {exc}")
            return False

    async def generate_json(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Generate strict JSON from Ollama using /api/chat.
        Retries up to max_retries on connection or JSON decoding errors.
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": self.temperature,
            },
        }

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Requesting Ollama generation (attempt {attempt}/{self.max_retries})...")
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()

                # /api/chat returns message.content
                raw_content = data.get("message", {}).get("content", "").strip()
                if not raw_content:
                    raise OllamaClientError("Empty response content from Ollama")

                parsed = json.loads(raw_content)
                if not isinstance(parsed, dict):
                    raise OllamaClientError(f"Expected JSON object, got {type(parsed)}")

                return parsed

            except (httpx.HTTPError, json.JSONDecodeError, OllamaClientError) as exc:
                last_error = exc
                logger.warning(f"Ollama generation attempt {attempt} failed: {exc}")

        raise OllamaClientError(
            f"Ollama generation failed after {self.max_retries} attempts. Last error: {last_error}"
        )

