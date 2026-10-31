
from src.answer_generator import generate_answer


def test_no_evidence_returns_insufficient_evidence():
    result = generate_answer("What is the deadline?", [])

    assert result["status"] == "insufficient_evidence"
    assert result["citations"] == []


def test_unresolved_conflict_does_not_guess():
    resolution = {
        "status": "unresolved",
        "answer": None,
        "reason": "Conflicting policies have equal authority.",
        "citations": [{"source": "policy.txt", "page_number": 1}],
    }

    result = generate_answer(
        "What is the deadline?",
        [],
        resolution,
    )

    assert result["status"] == "unresolved"
    assert "could not safely determine" in result["answer"]


def test_resolved_answer_keeps_citation():
    resolution = {
        "status": "resolved",
        "answer": "Submit claims within 15 calendar days.",
        "reason": "An effective amendment explicitly supersedes the old policy.",
        "citations": [{"source": "amendment.txt", "page_number": 2}],
    }

    result = generate_answer(
        "What is the deadline?",
        [],
        resolution,
    )

    assert result["status"] == "answered"
    assert "15 calendar days" in result["answer"]
    assert result["citations"][0]["source"] == "amendment.txt"
