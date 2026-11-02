"""Telegram bot dispatcher for sending native Quiz polls."""

import logging
from typing import Optional
from telegram import Bot, Poll
from telegram.error import TelegramError

from src.models import QuizPollPayload

logger = logging.getLogger(__name__)


class TelegramQuizBot:
    """Handles Telegram Bot API communications and poll publishing."""

    def __init__(
        self,
        bot_token: str,
        channel_id: str,
        thread_id: Optional[int] = None,
    ):
        if not bot_token:
            logger.warning("BOT_TOKEN is not set; TelegramQuizBot will not be able to publish.")
        self.bot = Bot(token=bot_token) if bot_token else None
        self.channel_id = channel_id
        self.thread_id = thread_id

    async def send_quiz(self, payload: QuizPollPayload) -> bool:
        """
        Dispatches a native quiz poll to the configured Telegram channel/topic.
        Returns True if successful, False otherwise.
        """
        if not self.bot or not self.channel_id:
            logger.error("Cannot dispatch quiz: BOT_TOKEN or CHANNEL_ID is not configured.")
            return False

        try:
            logger.info(f"Publishing quiz to Telegram: '{payload.question[:50]}...'")
            await self.bot.send_poll(
                chat_id=self.channel_id,
                message_thread_id=self.thread_id,
                question=payload.question,
                options=payload.options,
                type=Poll.QUIZ,
                correct_option_id=payload.correct_option_id,
                explanation=payload.explanation,
                is_anonymous=True,
            )
            logger.info("Quiz successfully published to Telegram.")
            return True
        except TelegramError as exc:
            logger.error(f"Telegram API error while sending poll: {exc}")
            return False
        except Exception as exc:
            logger.error(f"Unexpected error while sending poll: {exc}")
            return False

