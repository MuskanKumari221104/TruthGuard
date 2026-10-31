
from src.claim_extractor import extract_claims
from src.contradiction_detector import detect_contradictions


def test_extracts_deadline_claim():
    chunks = [
        {
            "chunk_id": 0,
            "source": "policy_v1.txt",
            "page_number": 1,
            "text": (
                "Employees must submit reimbursement claims "
                "within 30 calendar days."
            ),
        }
    ]

    claims = extract_claims(chunks)

    assert len(claims) == 1
    assert claims[0]["deadline"]["value"] == 30
    assert claims[0]["deadline"]["unit"] == "calendar_days"
    assert claims[0]["source"] == "policy_v1.txt"


def test_detects_conflicting_reimbursement_deadlines():
    chunks = [
        {
            "source": "policy_v1.txt",
            "page_number": 1,
            "text": (
                "Employees must submit reimbursement claims "
                "within 30 calendar days."
            ),
        },
        {
            "source": "policy_amendment.txt",
            "page_number": 2,
            "text": (
                "Employees must submit reimbursement claims "
                "within 15 calendar days."
            ),
        },
    ]

    claims = extract_claims(chunks)
    conflicts = detect_contradictions(claims)

    assert len(conflicts) == 1
    assert conflicts[0]["value_1"] == 30
    assert conflicts[0]["value_2"] == 15
    assert conflicts[0]["source_1"] == "policy_v1.txt"
    assert conflicts[0]["source_2"] == "policy_amendment.txt"


def test_does_not_flag_identical_deadlines():
    chunks = [
        {
            "source": "policy_a.txt",
            "page_number": 1,
            "text": "Submit reimbursement claims within 30 days.",
        },
        {
            "source": "policy_b.txt",
            "page_number": 1,
            "text": "Submit reimbursement claims within 30 days.",
        },
    ]

    claims = extract_claims(chunks)

    assert detect_contradictions(claims) == []


def test_does_not_compare_different_topics():
    chunks = [
        {
            "source": "leave.txt",
            "page_number": 1,
            "text": "Employees receive annual leave within 30 days.",
        },
        {
            "source": "policy.txt",
            "page_number": 1,
            "text": "Submit reimbursement claims within 15 days.",
        },
    ]

    claims = extract_claims(chunks)

    assert detect_contradictions(claims) == []


def test_claim_without_deadline_is_retained():
    chunks = [
        {
            "source": "policy.txt",
            "page_number": 1,
            "text": "Claims submitted late may be rejected.",
        }
    ]

    claims = extract_claims(chunks)

    assert len(claims) == 1
    assert claims[0]["deadline"] is None
