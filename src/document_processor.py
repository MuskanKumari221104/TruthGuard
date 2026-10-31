
from pathlib import Path

import pymupdf  # PyMuPDF


SUPPORTED_EXTENSIONS = {".txt", ".pdf"}


class DocumentProcessingError(Exception):
    """Raised when a document cannot be processed."""
    pass


def extract_text_from_txt(file_path: Path) -> str:
    """Read and return the text inside a TXT file."""

    try:
        return file_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        # Fallback for some older text files.
        try:
            return file_path.read_text(encoding="cp1252")
        except UnicodeDecodeError as exc:
            raise DocumentProcessingError(
                f"Could not decode text file: {file_path.name}"
            ) from exc
    except OSError as exc:
        raise DocumentProcessingError(
            f"Could not read text file: {file_path.name}"
        ) from exc


def extract_text_from_pdf(file_path: Path) -> list[dict]:
    """Extract text from each PDF page, preserving page numbers."""

    extracted_pages = []

    try:
        with pymupdf.open(file_path) as pdf:
            if pdf.is_encrypted:
                raise DocumentProcessingError(
                    f"PDF is password-protected: {file_path.name}"
                )

            for page_number, page in enumerate(pdf, start=1):
                page_text = page.get_text("text").strip()

                extracted_pages.append({
                    "page_number": page_number,
                    "text": page_text,
                })

    except DocumentProcessingError:
        raise
    except (OSError, ValueError, pymupdf.FileDataError) as exc:
        raise DocumentProcessingError(
            f"Could not read PDF file: {file_path.name}"
        ) from exc

    return extracted_pages


def process_document(file_path: str | Path) -> dict:
    """
    Process a PDF or TXT file and return its text and metadata.

    The returned dictionary is designed for later TruthGuard components.
    """

    path = Path(file_path)

    if not path.exists():
        raise DocumentProcessingError(
            f"File not found: {path}"
        )

    if not path.is_file():
        raise DocumentProcessingError(
            f"Path is not a file: {path}"
        )

    file_type = path.suffix.lower()

    if file_type not in SUPPORTED_EXTENSIONS:
        raise DocumentProcessingError(
            f"Unsupported file type: {file_type or 'no extension'}. "
            "Please use a PDF or TXT file."
        )

    if file_type == ".txt":
        text = extract_text_from_txt(path).strip()
        pages = [{"page_number": 1, "text": text}]

    else:
        pages = extract_text_from_pdf(path)
        text = "\n\n".join(
            page["text"] for page in pages if page["text"]
        ).strip()

    if not text:
        raise DocumentProcessingError(
            f"No extractable text found in {path.name}. "
            "The file may be empty or the PDF may contain scanned pages. "
            "Scanned PDFs may require OCR."
        )

    return {
        "source": path.name,
        "file_type": file_type.lstrip("."),
        "page_count": len(pages),
        "text": text,
        "pages": pages,
    }
