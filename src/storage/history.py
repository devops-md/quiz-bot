"""Storage manager for tracking published quiz history and preventing duplicates."""

import json
import logging
import os
import re
from pathlib import Path
from typing import List, Optional

from src.models import QuizRecord

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """Lowercase and strip non-alphanumeric characters for fuzzy duplicate matching."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


class HistoryStorage:
    """Manages reading and writing quiz records to a persistent JSON history file."""

    def __init__(self, history_file_path: str = "data/history.json"):
        self.history_file = Path(history_file_path)
        self._ensure_storage_ready()

    def _ensure_storage_ready(self) -> None:
        """Create parent directory and empty history file if not present."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def load_history(self) -> List[QuizRecord]:
        """Load all historical quiz records."""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                return [QuizRecord(**item) for item in raw_data]
        except Exception as exc:
            logger.error(f"Failed to load history from {self.history_file}: {exc}")
            return []

    def save_record(self, record: QuizRecord) -> None:
        """Append a new quiz record to history."""
        records = self.load_history()
        records.append(record)

        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([r.model_dump() for r in records], f, indent=2, ensure_ascii=False)
            logger.info(f"Recorded quiz {record.id} to {self.history_file}")
        except Exception as exc:
            logger.error(f"Failed to write quiz history to {self.history_file}: {exc}")

    def get_recent_records(self, limit: int = 50) -> List[QuizRecord]:
        """Get the most recent N quiz records."""
        records = self.load_history()
        return records[-limit:]

    def get_recent_questions(self, limit: int = 20) -> List[str]:
        """Get recent question texts for negative prompting."""
        return [r.question for r in self.get_recent_records(limit=limit)]

    def is_duplicate(self, question_text: str, window: int = 100) -> bool:
        """Check if a question is too similar to any question published within recent window."""
        norm_new = normalize_text(question_text)
        recent_records = self.get_recent_records(limit=window)
        for r in recent_records:
            if normalize_text(r.question) == norm_new:
                return True
        return False

