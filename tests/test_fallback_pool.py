import json
from pathlib import Path
from src.generator.validator import validate_and_format_quiz


def test_fallback_pool_all_questions_valid():
    pool_file = Path("data/fallback_pool.json")
    assert pool_file.exists()

    with open(pool_file, "r", encoding="utf-8") as f:
        pool = json.load(f)

    assert len(pool) >= 5

    for idx, item in enumerate(pool):
        payload, record = validate_and_format_quiz(
            raw_data=item,
            domain=item.get("domain", "general"),
            subdomain=item.get("subdomain", "general"),
            source="fallback",
        )
        assert len(payload.options) == 4
        assert 0 <= payload.correct_option_id < 4
        assert len(payload.question) <= 300
        for opt in payload.options:
            assert len(opt) <= 100
        assert len(payload.explanation) <= 200

