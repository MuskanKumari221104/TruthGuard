
import re


def extract_claims(chunks: list[dict]) -> list[dict]:
    """
    Extract sentence-level claims from retrieved document chunks.

    Preserve source and page metadata so claims can be traced
    back to the original evidence.
    """

    claims = []
    claim_id = 0

    for chunk in chunks:
        text = chunk.get("text", "")

        # Split text into sentences using common sentence punctuation.
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            # Extract deadline values such as "within 30 days".
            deadline_match = re.search(
                r"\b(?:within|no later than|maximum of|up to)\s+"
                r"(\d+)\s+(calendar\s+days|working\s+days|business\s+days|days)\b",
                sentence,
                flags=re.IGNORECASE,
            )

            deadline = None

            if deadline_match:
                unit = deadline_match.group(2).lower()
                deadline = {
                    "value": int(deadline_match.group(1)),
                    "unit": "calendar_days" if "calendar" in unit
                    else "business_days" if "business" in unit
                    else "working_days" if "working" in unit
                    else "days",
                }

            claims.append(
                {
                    "claim_id": claim_id,
                    "text": sentence,
                    "source": chunk.get("source", "unknown"),
                    "page_number": chunk.get("page_number"),
                    "deadline": deadline,
                }
            )

            claim_id += 1

    return claims
