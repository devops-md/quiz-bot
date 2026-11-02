import asyncio
from unittest.mock import AsyncMock, patch
from telegram.error import TelegramError

from src.models import QuizPollPayload
from src.telegram.bot import TelegramQuizBot


def test_telegram_bot_send_quiz_mocked():
    bot = TelegramQuizBot(bot_token="fake_token", channel_id="@devopsmoldova", thread_id=123)

    payload = QuizPollPayload(
        question="What is GitOps?",
        options=["ArgoCD", "Docker", "Linux", "Nginx"],
        correct_option_id=0,
        explanation="GitOps uses Git as the single source of truth.",
    )

    with patch("telegram.Bot.send_poll", new_callable=AsyncMock) as mock_send_poll:
        result = asyncio.run(bot.send_quiz(payload))
        assert result is True
        mock_send_poll.assert_called_once()


def test_telegram_bot_send_quiz_handles_error():
    bot = TelegramQuizBot(bot_token="fake_token", channel_id="@devopsmoldova")

    payload = QuizPollPayload(
        question="What is GitOps?",
        options=["ArgoCD", "Docker", "Linux", "Nginx"],
        correct_option_id=0,
        explanation="GitOps uses Git as the single source of truth.",
    )

    with patch(
        "telegram.Bot.send_poll", new_callable=AsyncMock, side_effect=TelegramError("Chat not found")
    ):
        result = asyncio.run(bot.send_quiz(payload))
        assert result is False