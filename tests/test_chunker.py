
import pytest

from src.chunker import chunk_document


def test_short_document_creates_one_chunk():
    document = {
        "source": "policy.txt",
        "pages": [
            {
                "page_number": 1,
                "text": "Claims must be submitted within 30 days.",
            }
        ],
    }

    chunks = chunk_document(document, chunk_size=100, overlap=20)

    assert len(chunks) == 1
    assert chunks[0]["source"] == "policy.txt"
    assert chunks[0]["page_number"] == 1
    assert "within 30 days" in chunks[0]["text"]


def test_long_document_creates_overlapping_chunks():
    text = "A" * 1000

    document = {
        "source": "long_policy.txt",
        "pages": [{"page_number": 1, "text": text}],
    }

    chunks = chunk_document(document, chunk_size=200, overlap=50)

    assert len(chunks) > 1
    assert len(chunks[0]["text"]) == 200
    assert chunks[0]["text"][-50:] == chunks[1]["text"][:50]


def test_chunks_preserve_page_numbers():
    document = {
        "source": "policy.pdf",
        "pages": [
            {"page_number": 1, "text": "First page content."},
            {"page_number": 2, "text": "Second page content."},
        ],
    }

    chunks = chunk_document(document, chunk_size=100, overlap=10)

    assert chunks[0]["page_number"] == 1
    assert chunks[1]["page_number"] == 2


def test_blank_pages_are_skipped():
    document = {
        "source": "policy.pdf",
        "pages": [
            {"page_number": 1, "text": ""},
            {"page_number": 2, "text": "Useful policy text."},
        ],
    }

    chunks = chunk_document(document)

    assert len(chunks) == 1
    assert chunks[0]["page_number"] == 2


def test_invalid_chunk_size_is_rejected():
    document = {
        "source": "policy.txt",
        "pages": [{"page_number": 1, "text": "Some text."}],
    }

    with pytest.raises(ValueError):
        chunk_document(document, chunk_size=0)


def test_invalid_overlap_is_rejected():
    document = {
        "source": "policy.txt",
        "pages": [{"page_number": 1, "text": "Some text."}],
    }

    with pytest.raises(ValueError):
        chunk_document(document, chunk_size=100, overlap=100)
