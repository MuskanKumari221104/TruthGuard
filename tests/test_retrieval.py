
import pytest

from src.retrieval import EvidenceRetriever


def test_retrieval_finds_relevant_passage():
    chunks = [
        {
            "chunk_id": 0,
            "source": "policy.txt",
            "page_number": 1,
            "text": "Employees must submit reimbursement claims within 30 days.",
        },
        {
            "chunk_id": 1,
            "source": "leave.txt",
            "page_number": 2,
            "text": "Employees receive 20 days of annual leave.",
        },
    ]

    retriever = EvidenceRetriever()
    retriever.index_chunks(chunks)

    results = retriever.retrieve(
        "What is the deadline for reimbursement claims?",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0]["source"] == "policy.txt"
    assert results[0]["page_number"] == 1
    assert "30 days" in results[0]["text"]
    assert "similarity_score" in results[0]


def test_retrieval_rejects_empty_question():
    retriever = EvidenceRetriever()
    retriever.index_chunks([
        {
            "chunk_id": 0,
            "source": "policy.txt",
            "page_number": 1,
            "text": "Claims must be submitted within 30 days.",
        }
    ])

    with pytest.raises(ValueError):
        retriever.retrieve("   ")


def test_retrieval_requires_indexing_first():
    retriever = EvidenceRetriever()

    with pytest.raises(RuntimeError):
        retriever.retrieve("What is the policy?")
