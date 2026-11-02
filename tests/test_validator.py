import pytest
from src.generator.validator import validate_and_format_quiz, ValidationError


def test_validator_shuffling_and_correctness():
    raw_data = {
        "question": "Which component manages node lifecycle in K8s?",
        "options": [
            "Node Lifecycle Controller",
            "CoreDNS",
            "Ingress Nginx",
            "Kubelet Daemon",
        ],
        "correct_option_id": 0,
        "explanation": "Node lifecycle controller monitors heartbeats.",
    }

    payload, record = validate_and_format_quiz(
        raw_data=raw_data,
        domain="containers_and_orchestration",
        subdomain="Kubernetes Control Plane",
    )

    # Verify that the correct option ID points to the expected correct string even after shuffling
    correct_str = payload.options[payload.correct_option_id]
    assert correct_str == "Node Lifecycle Controller"
    assert len(payload.options) == 4
    assert record.domain == "containers_and_orchestration"
    assert record.subdomain == "Kubernetes Control Plane"
    assert record.question == raw_data["question"]


def test_validator_rejects_malformed_json():
    with pytest.raises(ValidationError):
        validate_and_format_quiz(
            raw_data={"invalid": "payload"},
            domain="test",
            subdomain="test",
        )

