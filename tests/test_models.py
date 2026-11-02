import pytest
from pydantic import ValidationError

from src.models import GeneratedQuestion, QuizPollPayload, QuizRecord


def test_generated_question_valid():
    q = GeneratedQuestion(
        question="Which tool is used for container image vulnerability scanning?",
        options=["Trivy", "Prometheus", "Nginx", "Terraform"],
        correct_option_id=0,
        explanation="Trivy is an open-source scanner from Aqua Security for container images.",
    )
    assert q.correct_option_id == 0
    assert len(q.options) == 4
    assert "Trivy" in q.options


def test_generated_question_invalid_options_count():
    with pytest.raises(ValidationError):
        GeneratedQuestion(
            question="What is Kubernetes?",
            options=["Option 1", "Option 2"],  # only 2 options instead of 4
            correct_option_id=0,
            explanation="Explanation text here.",
        )


def test_generated_question_option_too_long():
    with pytest.raises(ValidationError):
        GeneratedQuestion(
            question="What is Kubernetes?",
            options=[
                "A" * 105,  # Exceeds 100 chars
                "Option 2",
                "Option 3",
                "Option 4",
            ],
            correct_option_id=0,
            explanation="Explanation text here.",
        )


def test_generated_question_explanation_trimming():
    long_explanation = "E" * 250
    q = GeneratedQuestion(
        question="Valid question text?",
        options=["Opt1", "Opt2", "Opt3", "Opt4"],
        correct_option_id=1,
        explanation=long_explanation,
    )
    assert len(q.explanation) <= 200
    assert q.explanation.endswith("...")

