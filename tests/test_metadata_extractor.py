
from src.metadata_extractor import extract_metadata


def test_extracts_amendment_metadata():
    text = """
    Document Version: 2.0
    Last updated: 1 March 2025
    Effective from: 1 March 2025
    This approved amendment applies to covered employee reimbursement expenses.
    This amendment explicitly supersedes the earlier 30-calendar-day deadline.
    """

    metadata = extract_metadata(text)

    assert metadata["version"] == "2.0"
    assert metadata["last_updated"] == "2025-03-01"
    assert metadata["effective_date"] == "2025-03-01"
    assert metadata["scope"] is not None
    assert metadata["supersedes_text"]
    assert metadata["authority"] is None


def test_missing_metadata_is_not_guessed():
    metadata = extract_metadata(
        "Employees must submit reimbursement claims within 15 days."
    )

    assert metadata["effective_date"] is None
    assert metadata["last_updated"] is None
    assert metadata["version"] is None
    assert metadata["authority"] is None


def test_invalid_input():
    import pytest

    with pytest.raises(TypeError):
        extract_metadata(None)
