"""Validation and sanitization of LLM output for Telegram Quiz poll requirements."""

import logging
import random
import uuid
from typing import Any, Dict, Tuple

from src.models import GeneratedQuestion, QuizPollPayload, QuizRecord

logger = logging.getLogger(__name__)

# Telegram Bot API hard limits
MAX_QUESTION_LEN = 300
MAX_OPTION_LEN = 100
MAX_EXPLANATION_LEN = 200


class ValidationError(Exception):
    """Raised when generated question violates Telegram limits."""
    pass


def validate_and_format_quiz(
    raw_data: Dict[str, Any],
    domain: str,
    subdomain: str,
    difficulty: str = "intermediate",
    source: str = "ollama",
) -> Tuple[QuizPollPayload, QuizRecord]:
    """
    Validates LLM raw response against Pydantic model and Telegram limits,
    randomizes option placement, and prepares Telegram payload + history record.
    """
    try:
        model = GeneratedQuestion(**raw_data)
    except Exception as exc:
        logger.error(f"Failed to parse LLM response into GeneratedQuestion model: {exc}")
        raise ValidationError(f"Model validation error: {exc}") from exc

    # Sanity checks on length
    if len(model.question) > MAX_QUESTION_LEN:
        raise ValidationError(
            f"Question length ({len(model.question)}) exceeds Telegram limit ({MAX_QUESTION_LEN})"
        )

    for i, opt in enumerate(model.options):
        if len(opt) > MAX_OPTION_LEN:
            raise ValidationError(
                f"Option {i} length ({len(opt)}) exceeds Telegram limit ({MAX_OPTION_LEN})"
            )

    # Telegram explanation limit
    explanation = model.explanation.strip()
    if len(explanation) > MAX_EXPLANATION_LEN:
        explanation = explanation[: MAX_EXPLANATION_LEN - 3] + "..."

    # Shuffle options to avoid LLM position bias
    options = list(model.options)
    correct_answer = options[model.correct_option_id]
    random.shuffle(options)
    shuffled_correct_id = options.index(correct_answer)

    poll_payload = QuizPollPayload(
        question=model.question,
        options=options,
        correct_option_id=shuffled_correct_id,
        explanation=explanation,
    )

    record_id = f"{domain[:4]}-{uuid.uuid4().hex[:8]}"
    history_record = QuizRecord(
        id=record_id,
        domain=domain,
        subdomain=subdomain,
        difficulty=difficulty,
        question=model.question,
        options=options,
        correct_option_id=shuffled_correct_id,
        explanation=explanation,
        source=source,  # type: ignore
    )

    return poll_payload, history_record

