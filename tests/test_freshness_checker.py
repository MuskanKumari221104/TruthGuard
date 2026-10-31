
from datetime import date

import pytest

from src.freshness_checker import (
    check_freshness,
    extract_document_dates,
    parse_date,
)


def test_parse_written_date():
    assert parse_date("1 January 2025") == date(2025, 1, 1)


def test_extract_last_updated_date():
    result = extract_document_dates(
        "Company Policy\nLast updated: 1 January 2025"
    )

    assert result["last_updated"] == date(2025, 1, 1)


def test_extract_effective_date():
    result = extract_document_dates(
        "Policy amendment\nEffective from: 1 March 2025"
    )

    assert result["effective_date"] == date(2025, 3, 1)


def test_effective_document():
    result = check_freshness(
        "Effective from: 1 March 2025",
        question_date="2 March 2025",
    )

    assert result["effective_status"] == "effective"


def test_future_document_is_not_yet_effective():
    result = check_freshness(
        "Effective from: 1 March 2026",
        question_date="1 January 2026",
    )

    assert result["effective_status"] == "not_yet_effective"


def test_missing_effective_date_is_unknown():
    result = check_freshness(
        "Company policy without an effective date",
        question_date="1 January 2026",
    )

    assert result["effective_status"] == "unknown"


def test_invalid_reference_date_is_rejected():
    with pytest.raises(ValueError):
        check_freshness(
            "Company policy",
            question_date="not-a-date",
        )
