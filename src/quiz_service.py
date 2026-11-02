"""High-level quiz orchestration service connecting generator, storage, and Telegram."""

import json
import logging
import random
from pathlib import Path
from typing import Optional, Tuple

from src.config import Settings
from src.generator.ollama_client import OllamaClient
from src.generator.prompt_builder import PromptBuilder
from src.generator.validator import ValidationError, validate_and_format_quiz
from src.models import QuizPollPayload, QuizRecord
from src.storage.history import HistoryStorage
from src.telegram.bot import TelegramQuizBot

logger = logging.getLogger(__name__)


class QuizService:
    """Coordinates question generation, fallback recovery, validation, storage, and dispatch."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.storage = HistoryStorage(settings.history_path)
        self.prompt_builder = PromptBuilder(settings.domains_file_path)
        self.ollama = OllamaClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            timeout=settings.ollama_timeout,
            temperature=settings.ollama_temperature,
            max_retries=settings.ollama_max_retries,
        )
        self.telegram = TelegramQuizBot(
            bot_token=settings.bot_token,
            channel_id=settings.channel_id,
            thread_id=settings.thread_id,
        )

    def _get_fallback_quiz(
        self, domain: str, subdomain: str, difficulty: str
    ) -> Tuple[QuizPollPayload, QuizRecord]:
        """Loads a question from local emergency fallback pool when Ollama is unavailable."""
        logger.warning("Attempting to load question from local fallback emergency pool...")
        fallback_file = Path(self.settings.fallback_pool_path)
        if not fallback_file.exists():
            raise FileNotFoundError(f"Fallback pool file does not exist: {fallback_file}")

        with open(fallback_file, "r", encoding="utf-8") as f:
            pool = json.load(f)

        if not pool:
            raise ValueError("Fallback pool is empty!")

        # Try to find a fallback question not in recent history
        random.shuffle(pool)
        for item in pool:
            if not self.storage.is_duplicate(item["question"], window=50):
                return validate_and_format_quiz(
                    raw_data=item,
                    domain=item.get("domain", domain),
                    subdomain=item.get("subdomain", subdomain),
                    difficulty=item.get("difficulty", difficulty),
                    source="fallback",
                )

        # If all are in recent history, pick random item
        item = random.choice(pool)
        return validate_and_format_quiz(
            raw_data=item,
            domain=item.get("domain", domain),
            subdomain=item.get("subdomain", subdomain),
            difficulty=item.get("difficulty", difficulty),
            source="fallback",
        )

    async def generate_quiz(self) -> Tuple[QuizPollPayload, QuizRecord]:
        """
        Generates and validates a new quiz question via local Ollama.
        Falls back to emergency pool if Ollama is unreachable.
        """
        recent_records = self.storage.get_recent_records(limit=30)
        recent_questions = self.storage.get_recent_questions(limit=15)
        domain, subdomain, difficulty = self.prompt_builder.select_domain_and_subdomain(
            recent_records
        )
        logger.info(f"Selected target: Domain='{domain}', Subdomain='{subdomain}', Difficulty='{difficulty}'")

        # Healthcheck Ollama
        is_healthy = await self.ollama.is_healthy()
        if not is_healthy:
            logger.error("Ollama is not responding to healthcheck. Falling back to local emergency pool.")
            return self._get_fallback_quiz(domain, subdomain, difficulty)

        system_prompt = self.prompt_builder.build_system_prompt(domain)
        user_prompt = self.prompt_builder.build_user_prompt(
            domain_key=domain,
            subdomain=subdomain,
            difficulty=difficulty,
            recent_questions=recent_questions,
        )

        for attempt in range(1, self.settings.ollama_max_retries + 1):
            try:
                raw_json = await self.ollama.generate_json(
                    prompt=user_prompt, system_prompt=system_prompt
                )
                payload, record = validate_and_format_quiz(
                    raw_data=raw_json,
                    domain=domain,
                    subdomain=subdomain,
                    difficulty=difficulty,
                    source="ollama",
                )

                if self.storage.is_duplicate(payload.question):
                    logger.warning(
                        f"Generated question is duplicate of recent quiz (attempt {attempt}). Retrying..."
                    )
                    continue

                return payload, record

            except (ValidationError, Exception) as exc:
                logger.warning(f"Generation attempt {attempt} failed validation: {exc}")

        logger.error("All Ollama generation attempts failed validation. Switching to fallback pool.")
        return self._get_fallback_quiz(domain, subdomain, difficulty)

    async def execute_daily_quiz(self) -> bool:
        """End-to-end task: generates, publishes to Telegram, and saves to history on success."""
        try:
            logger.info("Starting daily quiz execution workflow...")
            payload, record = await self.generate_quiz()

            logger.info(f"Dispatching quiz: '{payload.question}'")
            success = await self.telegram.send_quiz(payload)

            if success:
                self.storage.save_record(record)
                logger.info(f"Daily quiz '{record.id}' successfully completed and archived.")
                return True
            else:
                logger.error("Failed to publish quiz poll to Telegram.")
                return False

        except Exception as exc:
            logger.exception(f"Unhandled error in execute_daily_quiz: {exc}")
            return False

