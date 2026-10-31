
import re


def _get_deadline_topic(text: str) -> str | None:
    """Identify the topic of a deadline claim."""

    text = text.lower()

    if re.search(r"\breimburse\w*\b|\bexpense claims?\b", text):
        return "reimbursement"

    if re.search(r"\bsubmit\w*\b|\bsubmission\b|\bfile\w*\b", text):
        return "submission"

    return None


def detect_contradictions(claims: list[dict]) -> list[dict]:
    """
    Find claims that state different deadlines for the same topic.

    This is a first-pass rule-based detector, not a complete
    natural language contradiction model.
    """

    contradictions = []

    for i, first in enumerate(claims):
        first_deadline = first.get("deadline")

        if not first_deadline:
            continue

        for second in claims[i + 1:]:
            second_deadline = second.get("deadline")

            if not second_deadline:
                continue

            # Different units cannot safely be compared directly.
            if first_deadline["unit"] != second_deadline["unit"]:
                continue

            first_topic = _get_deadline_topic(first["text"])
            second_topic = _get_deadline_topic(second["text"])

            # Require a known, matching topic.
            if not first_topic or first_topic != second_topic:
                continue

            if first_deadline["value"] == second_deadline["value"]:
                continue

            contradictions.append(
                {
                    "type": "conflicting_deadline",
                    "topic": first_topic,
                    "claim_1": first["text"],
                    "source_1": first.get("source", "unknown"),
                    "page_1": first.get("page_number"),
                    "claim_2": second["text"],
                    "source_2": second.get("source", "unknown"),
                    "page_2": second.get("page_number"),
                    "value_1": first_deadline["value"],
                    "value_2": second_deadline["value"],
                    "unit": first_deadline["unit"],
                }
            )

    return contradictions
