"""Data models for quiz domains, questions, LLM output, and Telegram payloads."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


class Domain(BaseModel):
    """Domain with title, description, and list of subdomains."""

    title: str
    description: str
    subdomains: List[str]


class DomainCatalog(BaseModel):
    """Full taxonomy loaded from questions_domains.json."""

    version: str = "2.0.0"
    description: str = ""
    difficulty_levels: List[str] = ["beginner", "intermediate", "advanced"]
    domains: Dict[str, Domain]


class GeneratedQuestion(BaseModel):
    """Schema expected directly from Ollama JSON output."""

    question: str = Field(..., min_length=10)
    options: List[str]
    correct_option_id: int = Field(..., ge=0, le=3)
    explanation: str = Field(..., min_length=5)

    @field_validator("explanation", mode="before")
    @classmethod
    def trim_explanation(cls, explanation: Any) -> str:
        if not isinstance(explanation, str):
            explanation = str(explanation)
        exp = explanation.strip()
        if len(exp) > 200:
            exp = exp[:197] + "..."
        return exp

    @field_validator("options")
    @classmethod
    def validate_options_length(cls, options: List[str]) -> List[str]:
        if len(options) != 4:
            raise ValueError(f"Quiz question must have exactly 4 options, got {len(options)}")
        for idx, opt in enumerate(options):
            trimmed = opt.strip()
            if not (1 <= len(trimmed) <= 100):
                raise ValueError(
                    f"Option {idx} length ({len(trimmed)}) must be between 1 and 100 characters"
                )
        return [opt.strip() for opt in options]

    @field_validator("question")
    @classmethod
    def sanitize_question(cls, question: str) -> str:
        q = question.strip()
        if len(q) > 300:
            raise ValueError(f"Question exceeds 300 characters limit: {len(q)}")
        return q


class QuizRecord(BaseModel):
    """Structured question stored in the persistent history log."""

    id: str
    domain: str
    subdomain: str
    difficulty: str = "intermediate"
    question: str
    options: List[str]
    correct_option_id: int
    explanation: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: Literal["ollama", "fallback"] = "ollama"


class QuizPollPayload(BaseModel):
    """Validated Telegram quiz poll payload ready to be dispatched."""

    question: str
    options: List[str]
    correct_option_id: int
    explanation: str