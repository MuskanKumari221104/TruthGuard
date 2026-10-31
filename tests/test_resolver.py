
import pytest

from src.resolver import resolve_conflict


def make_claim(source, days, topic="reimbursement", scope=None):
    claim = {
        "text": f"Submit reimbursement claims within {days} calendar days.",
        "source": source,
        "page_number": 1,
        "deadline": {
            "value": days,
            "unit": "calendar_days",
        },
        "topic": topic,
    }

    if scope is not None:
        claim["scope"] = scope

    return claim


def make_document(authority, effective_date="2025-01-01",
                  supersedes=None, scope="reimbursement"):
    return {
        "authority": authority,
        "effective_date": effective_date,
        "supersedes": supersedes or [],
        "scope": scope,
    }


def test_explicit_supersession_resolves_conflict():
    claims = [
        make_claim("policy_v1.txt", 30),
        make_claim("policy_amendment.txt", 15),
    ]

    documents = {
        "policy_v1.txt": make_document(1),
        "policy_amendment.txt": make_document(
            1,
            effective_date="2025-03-01",
            supersedes=["policy_v1.txt"],
        ),
    }

    result = resolve_conflict(
        claims, documents, question_date="2025-04-01"
    )

    assert result["status"] == "resolved"
    assert result["answer"] == claims[1]["text"]
    assert result["citations"][0]["source"] == "policy_amendment.txt"


def test_future_amendment_is_not_selected():
    claims = [
        make_claim("policy_v1.txt", 30),
        make_claim("policy_amendment.txt", 15),
    ]

    documents = {
        "policy_v1.txt": make_document(1),
        "policy_amendment.txt": make_document(
            2,
            effective_date="2026-01-01",
            supersedes=["policy_v1.txt"],
        ),
    }

    result = resolve_conflict(
        claims, documents, question_date="2025-06-01"
    )

    assert result["status"] == "unresolved"
    assert result["answer"] is None


def test_equal_authority_without_supersession_abstains():
    claims = [
        make_claim("policy_a.txt", 30),
        make_claim("policy_b.txt", 15),
    ]

    documents = {
        "policy_a.txt": make_document(1),
        "policy_b.txt": make_document(1),
    }

    result = resolve_conflict(
        claims, documents, question_date="2025-06-01"
    )

    assert result["status"] == "unresolved"
    assert result["answer"] is None


def test_missing_metadata_abstains():
    result = resolve_conflict(
        [
            make_claim("policy_a.txt", 30),
            make_claim("policy_b.txt", 15),
        ],
        {},
        question_date="2025-06-01",
    )

    assert result["status"] == "unresolved"


def test_invalid_question_date_is_rejected():
    with pytest.raises(ValueError):
        resolve_conflict([], {}, question_date="not-a-date")


def test_higher_authority_resolves_conflict():
    claims = [
        make_claim("policy_a.txt", 30),
        make_claim("policy_b.txt", 15),
    ]

    documents = {
        "policy_a.txt": make_document(1),
        "policy_b.txt": make_document(2),
    }

    result = resolve_conflict(
        claims, documents, question_date="2025-06-01"
    )

    assert result["status"] == "resolved"
    assert result["answer"] == claims[1]["text"]
    assert result["citations"][0]["source"] == "policy_b.txt"


def test_mutual_supersession_abstains():
    claims = [
        make_claim("policy_a.txt", 30),
        make_claim("policy_b.txt", 15),
    ]

    documents = {
        "policy_a.txt": make_document(
            2, supersedes=["policy_b.txt"]
        ),
        "policy_b.txt": make_document(
            2, supersedes=["policy_a.txt"]
        ),
    }

    result = resolve_conflict(
        claims, documents, question_date="2025-06-01"
    )

    assert result["status"] == "unresolved"
    assert result["answer"] is None


def test_different_topics_are_not_compared():
    claims = [
        make_claim("policy_a.txt", 30, topic="reimbursement"),
        make_claim("policy_b.txt", 15, topic="leave"),
    ]

    documents = {
        "policy_a.txt": make_document(1),
        "policy_b.txt": make_document(2),
    }

    result = resolve_conflict(
        claims, documents, question_date="2025-06-01"
    )

    assert result["status"] == "unresolved"
    assert result["answer"] is None


def test_identical_deadlines_are_not_resolved_as_conflict():
    claims = [
        make_claim("policy_a.txt", 30),
        make_claim("policy_b.txt", 30),
    ]

    documents = {
        "policy_a.txt": make_document(1),
        "policy_b.txt": make_document(2),
    }

    result = resolve_conflict(
        claims, documents, question_date="2025-06-01"
    )

    assert result["status"] == "unresolved"
    assert result["answer"] is None


def test_invalid_effective_date_abstains():
    claims = [
        make_claim("policy_a.txt", 30),
        make_claim("policy_b.txt", 15),
    ]

    documents = {
        "policy_a.txt": make_document(1),
        "policy_b.txt": make_document(
            2, effective_date="invalid-date"
        ),
    }

    result = resolve_conflict(
        claims, documents, question_date="2025-06-01"
    )

    assert result["status"] == "unresolved"
    assert result["answer"] is None


def test_mismatched_claim_scope_is_ignored():
    claims = [
        make_claim(
            "policy_a.txt", 30,
            scope="reimbursement"
        ),
        make_claim(
            "policy_b.txt", 15,
            scope="travel expenses"
        ),
    ]

    documents = {
        "policy_a.txt": make_document(
            1, scope="reimbursement"
        ),
        "policy_b.txt": make_document(
            2, scope="reimbursement"
        ),
    }

    result = resolve_conflict(
        claims, documents, question_date="2025-06-01"
    )

    assert result["status"] == "unresolved"
    assert result["answer"] is None
