
import pymupdf
import pytest

from src.document_processor import (
    DocumentProcessingError,
    process_document,
)


def test_process_txt_file(tmp_path):
    """Check that a TXT file is read correctly."""

    file_path = tmp_path / "policy.txt"
    file_path.write_text(
        "Claims must be submitted within 30 days.",
        encoding="utf-8",
    )

    result = process_document(file_path)

    assert result["source"] == "policy.txt"
    assert result["file_type"] == "txt"
    assert result["page_count"] == 1
    assert "within 30 days" in result["text"]
    assert result["pages"][0]["page_number"] == 1


def test_process_pdf_file(tmp_path):
    """Check that text is extracted from a PDF."""

    file_path = tmp_path / "policy.pdf"

    with pymupdf.open() as pdf:
        page = pdf.new_page()
        page.insert_text(
            (72, 72),
            "Claims must be submitted within 15 days.",
        )
        pdf.save(file_path)

    result = process_document(file_path)

    assert result["source"] == "policy.pdf"
    assert result["file_type"] == "pdf"
    assert result["page_count"] == 1
    assert "within 15 days" in result["text"]
    assert result["pages"][0]["page_number"] == 1


def test_missing_file_raises_error(tmp_path):
    """Check that a missing file produces a clear error."""

    file_path = tmp_path / "missing.txt"

    with pytest.raises(DocumentProcessingError, match="File not found"):
        process_document(file_path)


def test_unsupported_file_type_raises_error(tmp_path):
    """Check that unsupported file types are rejected."""

    file_path = tmp_path / "notes.docx"
    file_path.write_text("Example content", encoding="utf-8")

    with pytest.raises(
        DocumentProcessingError,
        match="Unsupported file type",
    ):
        process_document(file_path)


def test_empty_file_raises_error(tmp_path):
    """Check that empty documents are rejected."""

    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(
        DocumentProcessingError,
        match="No extractable text",
    ):
        process_document(file_path)
