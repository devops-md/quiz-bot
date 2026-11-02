import json
import pytest
from pathlib import Path
from src.models import QuizRecord
from src.storage.history import HistoryStorage


def test_history_storage_roundtrip(tmp_path: Path):
    history_file = tmp_path / "test_history.json"
    storage = HistoryStorage(str(history_file))

    assert storage.load_history() == []

    record = QuizRecord(
        id="test-1",
        domain="cicd_and_gitops",
        subdomain="GitOps",
        question="What is ArgoCD?",
        options=["Declarative GitOps tool", "Compiler", "Kernel", "Database"],
        correct_option_id=0,
        explanation="ArgoCD is a declarative GitOps continuous delivery tool for Kubernetes.",
        source="fallback",
    )

    storage.save_record(record)
    loaded = storage.load_history()
    assert len(loaded) == 1
    assert loaded[0].id == "test-1"
    assert loaded[0].question == "What is ArgoCD?"

    # Test duplicate detection
    assert storage.is_duplicate("What is ArgoCD?")
    assert not storage.is_duplicate("What is FluxCD?")

