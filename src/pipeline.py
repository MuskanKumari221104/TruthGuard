
import re
from datetime import date
from pathlib import Path

from src.document_processor import process_document
from src.chunker import chunk_document
from src.retrieval import EvidenceRetriever
from src.claim_extractor import extract_claims
from src.contradiction_detector import detect_contradictions
from src.resolver import resolve_conflict
from src.answer_generator import generate_answer
from src.metadata_extractor import extract_metadata


def run_pipeline(
    file_paths: list[str | Path],
    question: str,
    document_metadata: dict[str, dict] | None = None,
    question_date: str | None = None,
) -> dict:
    """Run the TruthGuard document verification pipeline."""

    # Step 1: Validate the question and input documents.
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not file_paths:
        return generate_answer(question, [])

    # Step 2: Prepare document metadata.
    metadata = {
        name: dict(values)
        for name, values in (document_metadata or {}).items()
    }

    reference_date = question_date or date.today().isoformat()

    # Remove numeric prefixes added by Streamlit uploads.
    def original_name(file_path):
        name = Path(file_path).name
        return re.sub(r"^\d+_", "", name)

    actual_names = {
        original_name(path): Path(path).name
        for path in file_paths
    }

    # Step 3: Add trusted demonstration metadata.
    # These are configured rules for the sample documents,
    # not metadata inferred automatically from document text.

    def add_demo_metadata(
        original,
        authority,
        effective_date,
        scope,
        supersedes=None,
    ):
        actual = actual_names.get(original)

        if actual and actual not in metadata:
            metadata[actual] = {
                "authority": authority,
                "effective_date": effective_date,
                "scope": scope,
                "supersedes": [
                    actual_names[name]
                    for name in (supersedes or [])
                    if name in actual_names
                ],
            }

    add_demo_metadata(
        "policy_v1.txt",
        authority=2,
        effective_date="2025-01-01",
        scope="reimbursement covered expenses",
    )

    add_demo_metadata(
        "old_faq.txt",
        authority=1,
        effective_date="2025-02-01",
        scope="reimbursement covered expenses",
    )

    add_demo_metadata(
        "policy_amendment.txt",
        authority=3,
        effective_date="2025-03-01",
        scope="reimbursement covered expenses",
        supersedes=["policy_v1.txt", "old_faq.txt"],
    )

    # Step 4: Process documents, extract metadata, and create chunks.
    all_chunks = []

    for file_path in file_paths:
        document = process_document(file_path)

        # Extract metadata automatically from document text.
        extracted_metadata = extract_metadata(document["text"])

        # Retrieve trusted/configured metadata for this document.
        configured_metadata = metadata.get(document["source"], {})

        # Configured metadata takes priority over extracted metadata.
        # Authority is never inferred from document text.
        combined_metadata = {
            **extracted_metadata,
            **configured_metadata,
        }

        # Keep automatically extracted metadata separately for auditing.
        combined_metadata["extracted_metadata"] = extracted_metadata

        metadata[document["source"]] = combined_metadata

        # Create searchable evidence chunks.
        all_chunks.extend(chunk_document(document))

    if not all_chunks:
        return generate_answer(question, [])

    # Step 5: Retrieve relevant evidence.
    retriever = EvidenceRetriever()
    retriever.index_chunks(all_chunks)

    evidence = retriever.retrieve(question, top_k=10)

    # Step 6: Extract claims from retrieved evidence.
    claims = extract_claims(evidence)

    # Step 7: Detect potential contradictions.
    contradictions = detect_contradictions(claims)

    # Step 8: Resolve conflicts using document metadata.
    resolution = None

    if contradictions:
        conflicting_texts = {
            conflict["claim_1"]
            for conflict in contradictions
        } | {
            conflict["claim_2"]
            for conflict in contradictions
        }

        conflicting_claims = [
            claim
            for claim in claims
            if claim["text"] in conflicting_texts
        ]

        resolution = resolve_conflict(
            conflicting_claims,
            metadata,
            question_date=reference_date,
        )

    # Step 9: Generate the final answer.
    result = generate_answer(
        question=question,
        evidence=evidence,
        resolution=resolution,
    )

    # Step 10: Include verification details.
    result["contradictions"] = contradictions
    result["evidence"] = evidence
    result["claims"] = claims
    result["document_metadata"] = metadata

    return result
