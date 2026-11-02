import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

from src.config import Settings
from src.quiz_service import QuizService


def test_quiz_service_fallback_when_ollama_offline(tmp_path: Path):
    history_file = tmp_path / "test_history.json"
    settings = Settings(
        history_path=str(history_file),
        fallback_pool_path="data/fallback_pool.json",
        domains_file_path="questions_domains.json",
        ollama_base_url="http://non-existent-host:11434",
    )

    service = QuizService(settings)
    payload, record = asyncio.run(service.generate_quiz())

    assert payload is not None
    assert record.source == "fallback"
    assert len(payload.options) == 4
    assert 0 <= payload.correct_option_id < 4
    assert len(payload.question) <= 300


def test_quiz_service_execute_daily_quiz_end_to_end(tmp_path: Path):
    history_file = tmp_path / "e2e_history.json"
    settings = Settings(
        bot_token="fake-token",
        channel_id="@fake-channel",
        history_path=str(history_file),
        fallback_pool_path="data/fallback_pool.json",
        domains_file_path="questions_domains.json",
        ollama_base_url="http://non-existent-host:11434",
    )

    service = QuizService(settings)

    with patch.object(service.telegram, "send_quiz", new_callable=AsyncMock, return_value=True):
        success = asyncio.run(service.execute_daily_quiz())
        assert success is True

    # History should now contain 1 record
    history = service.storage.load_history()
    assert len(history) == 1
    assert history[0].source == "fallback"
