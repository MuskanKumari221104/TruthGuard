
import re


def _get_citations(evidence: list[dict]) -> list[dict]:
    """Return unique citations from the supplied evidence."""
    citations = []
    seen = set()

    for item in evidence:
        source = item.get("source", "unknown")
        page_number = item.get("page_number")
        key = (source, page_number)

        if key not in seen:
            seen.add(key)
            citations.append({
                "source": source,
                "page_number": page_number,
            })

    return citations


def _find_supported_deadline(
    question: str,
    evidence: list[dict],
) -> str | None:
    """
    Find an explicit deadline in evidence for a question
    asking about reimbursement claim submission.
    """
    question_lower = question.lower()

    asks_about_reimbursement = (
        "reimbursement" in question_lower
        and any(word in question_lower for word in (
            "claim", "submit", "submission", "deadline", "days"
        ))
    )

    if not asks_about_reimbursement:
        return None

    pattern = re.compile(
        r"[^.!?\n]*"
        r"(?:submit|file|send)"
        r"[^.!?\n]*"
        r"reimbursement claims?"
        r"[^.!?\n]*?"
        r"(?:within|no later than|maximum of|up to)"
        r"\s+\d+\s+"
        r"(?:calendar days|working days|business days|days)"
        r"[^.!?\n]*[.!?]?",
        re.IGNORECASE,
    )

    for item in evidence:
        text = item.get("text", "")

        for match in pattern.finditer(text):
            sentence = match.group(0).strip()

            if sentence:
                return sentence

    return None


def generate_answer(
    question: str,
    evidence: list[dict],
    resolution: dict | None = None,
) -> dict:
    """
    Generate an evidence-grounded response.

    Uses templates and explicit text matching, not an LLM.
    Only answers deadline questions when a matching statement
    is found in the supplied evidence.
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if resolution and resolution.get("status") == "resolved":
        return {
            "status": "answered",
            "question": question,
            "answer": resolution.get("answer"),
            "reason": resolution.get("reason", ""),
            "citations": resolution.get("citations", []),
        }

    if resolution and resolution.get("status") == "unresolved":
        return {
            "status": "unresolved",
            "question": question,
            "answer": (
                "I could not safely determine which conflicting claim "
                "applies from the available evidence."
            ),
            "reason": resolution.get("reason", ""),
            "citations": resolution.get("citations", []),
        }

    if not evidence:
        return {
            "status": "insufficient_evidence",
            "question": question,
            "answer": (
                "I could not find relevant evidence to answer this question."
            ),
            "reason": "No evidence passages were retrieved.",
            "citations": [],
        }

    citations = _get_citations(evidence)

    deadline_statement = _find_supported_deadline(question, evidence)

    if deadline_statement:
        return {
            "status": "answered",
            "question": question,
            "answer": deadline_statement,
            "reason": (
                "An explicit reimbursement submission deadline "
                "was found in the retrieved evidence. This is a "
                "text-matched answer, not a complete conflict or "
                "document-authority verification."
            ),
            "citations": citations,
        }

    return {
        "status": "evidence_found",
        "question": question,
        "answer": (
            "Relevant passages were found, but a verified answer "
            "has not yet been established."
        ),
        "reason": "The evidence requires further verification.",
        "citations": citations,
    }
