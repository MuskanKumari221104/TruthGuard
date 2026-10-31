
from datetime import date, datetime
import re


def parse_date(value: str | None) -> date | None:
    """Parse supported date formats into a date object."""

    if not value:
        return None

    value = value.strip()

    formats = (
        "%d %B %Y",   # 1 January 2025
        "%d %b %Y",   # 1 Jan 2025
        "%Y-%m-%d",   # 2025-01-01
        "%d/%m/%Y",   # 01/01/2025
    )

    for date_format in formats:
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue

    return None


def extract_document_dates(text: str) -> dict:
    """
    Extract common document update and effective dates.

    Returns parsed dates where recognizable; missing dates remain None.
    """

    patterns = {
        "last_updated": (
            r"Last updated\s*:\s*"
            r"(\d{1,2}\s+[A-Za-z]+\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})"
        ),
        "effective_date": (
            r"Effective(?:\s+from|\s+date)?\s*:\s*"
            r"(\d{1,2}\s+[A-Za-z]+\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})"
        ),
    }

    result = {
        "last_updated": None,
        "effective_date": None,
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            result[field] = parse_date(match.group(1))

    return result


def check_freshness(
    document_text: str,
    question_date: str | None = None,
) -> dict:
    """
    Report document dates and whether an effective date has arrived.

    This function does not decide whether a document is authoritative
    or whether it supersedes another document.
    """

    dates = extract_document_dates(document_text)

    if question_date:
        reference_date = parse_date(question_date)

        if reference_date is None:
            raise ValueError("Unsupported question_date format.")
    else:
        reference_date = date.today()

    effective_date = dates["effective_date"]

    if effective_date is None:
        status = "unknown"
    elif effective_date <= reference_date:
        status = "effective"
    else:
        status = "not_yet_effective"

    return {
        **dates,
        "reference_date": reference_date,
        "effective_status": status,
    }
