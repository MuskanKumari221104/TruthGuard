
from datetime import date


def _parse_date(value: str) -> date | None:
    """Convert a YYYY-MM-DD string into a date."""
    if not isinstance(value, str):
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _normalise_text(value) -> str:
    """Normalize text for safe comparisons."""
    if not isinstance(value, str):
        return ""

    return " ".join(value.lower().split())


def _valid_authority(value) -> bool:
    """Check whether authority is a valid integer."""
    return isinstance(value, int) and not isinstance(value, bool)


def _make_citations(claims: list[dict]) -> list[dict]:
    """Create unique source and page citations."""
    citations = []
    seen = set()

    for claim in claims:
        source = claim.get("source")
        page_number = claim.get("page_number")

        key = (source, page_number)

        if source and key not in seen:
            citations.append({
                "source": source,
                "page_number": page_number,
            })
            seen.add(key)

    return citations


def _get_resolution_result(
    status: str,
    answer: str | None,
    reason: str,
    citations: list[dict],
) -> dict:
    """Create a consistent resolver response."""
    return {
        "status": status,
        "answer": answer,
        "reason": reason,
        "citations": citations,
    }


def resolve_conflict(
    claims: list[dict],
    documents: dict[str, dict],
    question_date: str,
) -> dict:
    """
    Resolve competing claims using configured document metadata.

    Document metadata:
        authority: integer; higher means more authoritative
        effective_date: YYYY-MM-DD
        supersedes: list of source filenames
        scope: description of where the document applies

    Claims:
        text, source, deadline, page_number
        optionally topic and scope

    Resolution rules:
        1. Ignore documents not yet effective.
        2. Require valid effective dates and document scopes.
        3. Prefer explicit, one-way supersession.
        4. Otherwise, use unequal configured authority levels.
        5. Require one candidate to defeat every conflicting candidate.
        6. Abstain when the evidence does not establish a clear winner.
    """

    # Step 1: Validate the question date.
    reference_date = _parse_date(question_date)

    if reference_date is None:
        raise ValueError(
            "question_date must use YYYY-MM-DD format."
        )

    if not isinstance(claims, list):
        raise TypeError("claims must be a list.")

    if not isinstance(documents, dict):
        raise TypeError("documents must be a dictionary.")

    if len(claims) < 2:
        return _get_resolution_result(
            status="insufficient_evidence",
            answer=None,
            reason="At least two competing claims are required.",
            citations=_make_citations(claims),
        )

    # Step 2: Validate claims and document metadata.
    candidates = []

    for claim in claims:
        if not isinstance(claim, dict):
            continue

        source = claim.get("source")
        metadata = documents.get(source)

        if not isinstance(metadata, dict):
            continue

        deadline = claim.get("deadline")

        if not isinstance(deadline, dict):
            continue

        deadline_value = deadline.get("value")
        deadline_unit = _normalise_text(deadline.get("unit"))

        if deadline_value is None or not deadline_unit:
            continue

        effective_date = _parse_date(
            metadata.get("effective_date")
        )

        if effective_date is None:
            continue

        # A document cannot govern a question asked before
        # its effective date.
        if effective_date > reference_date:
            continue

        document_scope = _normalise_text(
            metadata.get("scope")
        )

        if not document_scope:
            continue

        # If claims provide scope, conflicting scope descriptions
        # must not be silently treated as equivalent.
        claim_scope = _normalise_text(claim.get("scope"))

        if claim_scope and claim_scope != document_scope:
            continue

        topic = _normalise_text(claim.get("topic"))

        supersedes = metadata.get("supersedes", [])

        if not isinstance(supersedes, list):
            supersedes = []

        supersedes = [
            item for item in supersedes
            if isinstance(item, str)
        ]

        authority = metadata.get("authority")

        if not _valid_authority(authority):
            authority = None

        candidates.append({
            "claim": claim,
            "source": source,
            "metadata": metadata,
            "deadline_value": deadline_value,
            "deadline_unit": deadline_unit,
            "effective_date": effective_date,
            "scope": document_scope,
            "topic": topic,
            "authority": authority,
            "supersedes": supersedes,
        })

    if len(candidates) < 2:
        return _get_resolution_result(
            status="unresolved",
            answer=None,
            reason=(
                "Not enough claims have valid effective dates and "
                "scope metadata to establish which rule applies."
            ),
            citations=_make_citations(claims),
        )

    # Step 3: Group claims that can meaningfully be compared.
    groups = {}

    for candidate in candidates:
        group_key = (
            candidate["deadline_unit"],
            candidate["scope"],
            candidate["topic"],
        )

        groups.setdefault(group_key, []).append(candidate)

    conflicting_groups = []

    for group in groups.values():
        distinct_values = {
            candidate["deadline_value"]
            for candidate in group
        }

        if len(distinct_values) > 1:
            conflicting_groups.append(group)

    if len(conflicting_groups) != 1:
        return _get_resolution_result(
            status="unresolved",
            answer=None,
            reason=(
                "Conflicting claims could not be grouped into one "
                "clearly comparable set of rules."
            ),
            citations=_make_citations(claims),
        )

    competing_candidates = conflicting_groups[0]

    # Step 4: Determine whether one candidate defeats another.
    def defeats(first, second):
        """
        Return True only when first has a clear advantage
        over second through explicit supersession or authority.
        """

        first_source = first["source"]
        second_source = second["source"]

        first_supersedes_second = (
            second_source in first["supersedes"]
        )

        second_supersedes_first = (
            first_source in second["supersedes"]
        )

        # Conflicting supersession statements are ambiguous.
        if first_supersedes_second and second_supersedes_first:
            return False

        if first_supersedes_second:
            return True

        if second_supersedes_first:
            return False

        # Without explicit supersession, compare trusted
        # configured authority levels.
        first_authority = first["authority"]
        second_authority = second["authority"]

        if first_authority is None or second_authority is None:
            return False

        return first_authority > second_authority

    # Step 5: Find candidates that defeat every different claim.
    possible_winners = []

    for candidate in competing_candidates:
        defeats_every_conflict = True

        for other in competing_candidates:
            if candidate is other:
                continue

            # Claims with the same deadline are not contradictory.
            if (
                candidate["deadline_value"]
                == other["deadline_value"]
            ):
                continue

            if not defeats(candidate, other):
                defeats_every_conflict = False
                break

        if defeats_every_conflict:
            possible_winners.append(candidate)

    # Step 6: Abstain unless exactly one winner exists.
    if len(possible_winners) != 1:
        return _get_resolution_result(
            status="unresolved",
            answer=None,
            reason=(
                "Conflicting claims were found, but the available "
                "metadata does not establish one clear winner. "
                "TruthGuard is abstaining rather than guessing."
            ),
            citations=_make_citations([
                candidate["claim"]
                for candidate in competing_candidates
            ]),
        )

    winner = possible_winners[0]

    # Step 7: Explain why the candidate was selected.
    explicit_supersession = any(
        other["source"] in winner["supersedes"]
        and other["deadline_value"] != winner["deadline_value"]
        for other in competing_candidates
    )

    if explicit_supersession:
        reason = (
            f"Selected {winner['source']} based on explicit "
            "supersession."
        )
    else:
        reason = (
            f"Selected {winner['source']} based on higher "
            "configured authority."
        )

    return _get_resolution_result(
        status="resolved",
        answer=winner["claim"]["text"],
        reason=reason,
        citations=_make_citations([winner["claim"]]),
    )
