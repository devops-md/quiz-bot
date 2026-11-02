"""Prompt engineering and domain selection for Ollama quiz generation."""

import json
import logging
import random
from pathlib import Path
from typing import List, Optional, Tuple

from src.models import DomainCatalog, QuizRecord

logger = logging.getLogger(__name__)


TECHNICAL_SYSTEM_PROMPT = """You are an expert senior DevOps/SRE lead creating high-quality daily technical quizzes for a professional DevOps community.

Your task is to generate a realistic, practical multiple-choice quiz question for the requested domain and subdomain.

STRICT TELEGRAM QUIZ CONSTRAINTS:
1. Question MUST be between 30 and 280 characters.
2. Provide exactly 4 options. Each option MUST be between 1 and 90 characters.
3. Exactly ONE option must be indisputably correct.
4. All distractors (incorrect options) must be realistic, plausible DevOps concepts or tools—never use joke or impossible options.
5. Explanation MUST be between 20 and 180 characters explaining why the answer is correct.
6. Return ONLY valid JSON adhering strictly to the schema below without any Markdown fences or formatting.

JSON Schema:
{
  "question": "string (30-280 chars)",
  "options": [
    "string (1-90 chars)",
    "string (1-90 chars)",
    "string (1-90 chars)",
    "string (1-90 chars)"
  ],
  "correct_option_id": 0,
  "explanation": "string (20-180 chars)"
}
"""

CULTURE_SYSTEM_PROMPT = """You are a senior tech lead and IT historian creating engaging trivia questions about IT culture, famous memes, historic bugs, and developer folklore for a DevOps community.

Your task is to generate a witty, authentic quiz question celebrating community lore or historic IT milestones.

STRICT TELEGRAM QUIZ CONSTRAINTS:
1. Question MUST be between 30 and 280 characters.
2. Provide exactly 4 options. Each option MUST be between 1 and 90 characters.
3. Exactly ONE option must be indisputably correct.
4. Distractors must be believable tech options or clever community humor.
5. Explanation MUST be between 20 and 180 characters explaining the punchline, historical context, or resolution.
6. Return ONLY valid JSON adhering strictly to the schema below without any Markdown fences or formatting.

JSON Schema:
{
  "question": "string (30-280 chars)",
  "options": [
    "string (1-90 chars)",
    "string (1-90 chars)",
    "string (1-90 chars)",
    "string (1-90 chars)"
  ],
  "correct_option_id": 0,
  "explanation": "string (20-180 chars)"
}
"""


class PromptBuilder:
    """Builds prompts and manages domain/subdomain rotation."""

    def __init__(self, catalog_path: str = "questions_domains.json"):
        self.catalog_path = catalog_path
        self.catalog = self._load_catalog(catalog_path)

    def _load_catalog(self, path: str) -> DomainCatalog:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Domains catalog file not found: {path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return DomainCatalog(**data)

    def select_domain_and_subdomain(
        self, recent_records: Optional[List[QuizRecord]] = None
    ) -> Tuple[str, str, str]:
        """
        Selects next domain, subdomain, and difficulty with balanced rotation.
        Avoids recently used domains if possible.
        """
        all_domain_keys = list(self.catalog.domains.keys())
        if not all_domain_keys:
            raise ValueError("No domains found in catalog")

        recent_domains = [r.domain for r in (recent_records or [])][-5:]
        candidates = [d for d in all_domain_keys if d not in recent_domains]
        if not candidates:
            candidates = all_domain_keys

        domain_key = random.choice(candidates)
        domain_obj = self.catalog.domains[domain_key]

        subdomains = domain_obj.subdomains
        recent_subdomains = [r.subdomain for r in (recent_records or [])][-10:]
        subdomain_candidates = [s for s in subdomains if s not in recent_subdomains]
        if not subdomain_candidates:
            subdomain_candidates = subdomains

        subdomain = random.choice(subdomain_candidates)
        difficulty = random.choice(self.catalog.difficulty_levels)

        return domain_key, subdomain, difficulty

    def build_system_prompt(self, domain_key: str) -> str:
        """Returns the appropriate system prompt based on domain."""
        if domain_key in ("it_memes_and_culture", "history_of_it"):
            return CULTURE_SYSTEM_PROMPT
        return TECHNICAL_SYSTEM_PROMPT

    def build_user_prompt(
        self,
        domain_key: str,
        subdomain: str,
        difficulty: str,
        recent_questions: Optional[List[str]] = None,
    ) -> str:
        """Formats user prompt with domain specifications and negative deduplication context."""
        domain_title = self.catalog.domains[domain_key].title
        description = self.catalog.domains[domain_key].description

        negative_context = ""
        if recent_questions:
            recent_sample = recent_questions[-6:]
            negative_context = (
                "\nDo NOT repeat or ask about any of these recently asked topics:\n- "
                + "\n- ".join(recent_sample)
            )

        return (
            f"Generate a {difficulty.upper()} difficulty quiz question.\n"
            f"Domain: {domain_title} ({description})\n"
            f"Subdomain: {subdomain}\n"
            f"{negative_context}\n\n"
            f"Remember: Output strictly JSON with 'question', 'options' (array of 4 strings), "
            f"'correct_option_id' (integer 0-3), and 'explanation'."
        )

