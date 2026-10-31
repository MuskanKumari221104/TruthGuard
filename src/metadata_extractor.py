
import re
from datetime import datetime


DATE_FORMATS = (
    "%d %B %Y",
    "%d %b %Y",
    "%Y-%m-%d",
    "%d/%m/%Y",
)


def _normalize_date(value: str) -> str | None:
    """Convert a supported date into YYYY-MM-DD format."""
    value = value.strip().rstrip(".,;")

    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(value, date_format).date().isoformat()
        except ValueError:
            continue

    return None


def extract_metadata(document_text: str) -> dict:
    """
    Extract explicitly stated metadata from a document.

    This function does not decide whether a document is authoritative.
    """

    if not isinstance(document_text, str):
        raise TypeError("document_text must be a string.")

    metadata = {
        "effective_date": None,
        "last_updated": None,
        "version": None,
        "supersedes_text": [],
        "scope": None,
        "authority": None,
    }

    effective_match = re.search(
        r"^\s*Effective\s+(?:from|date)\s*:\s*(.+?)\s*$",
        document_text,
        re.IGNORECASE | re.MULTILINE,
    )

    updated_match = re.search(
        r"^\s*Last updated\s*:\s*(.+?)\s*$",
        document_text,
        re.IGNORECASE | re.MULTILINE,
    )

    version_match = re.search(
        r"^\s*Document Version\s*:\s*([^\r\n]+)",
        document_text,
        re.IGNORECASE | re.MULTILINE,
    )

    if effective_match:
        metadata["effective_date"] = _normalize_date(
            effective_match.group(1)
        )

    if updated_match:
        metadata["last_updated"] = _normalize_date(
            updated_match.group(1)
        )

    if version_match:
        metadata["version"] = version_match.group(1).strip()

    # Capture explicit supersession statements without assuming
    # that every mentioned document is definitely superseded.
    for line in document_text.splitlines():
        if re.search(r"\bsupersed(?:e|es|ed|ing)\b", line, re.IGNORECASE):
            metadata["supersedes_text"].append(line.strip())

    # Capture the explicitly stated scope sentence, if present.
    scope_match = re.search(
        r"^\s*(This approved amendment applies to .+?[.!]?)\s*$",
        document_text,
        re.IGNORECASE | re.MULTILINE,
    )

    if scope_match:
        metadata["scope"] = scope_match.group(1).strip()

    return metadata
