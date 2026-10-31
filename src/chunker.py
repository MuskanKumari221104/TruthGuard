
def chunk_document(
    document: dict,
    chunk_size: int = 500,
    overlap: int = 100,
) -> list[dict]:
    """
    Split a processed document into overlapping text chunks.

    chunk_size and overlap are measured in characters, not tokens.
    Each chunk retains its source filename and page number.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    if not isinstance(document, dict):
        raise TypeError("document must be a dictionary.")

    source = document.get("source", "unknown")
    pages = document.get("pages", [])

    if not isinstance(pages, list):
        raise ValueError("document['pages'] must be a list.")

    chunks = []
    chunk_index = 0
    step_size = chunk_size - overlap

    for page in pages:
        if not isinstance(page, dict):
            raise ValueError("Each page must be a dictionary.")

        text = page.get("text", "").strip()
        page_number = page.get("page_number")

        if not text:
            continue

        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "chunk_id": chunk_index,
                        "source": source,
                        "page_number": page_number,
                        "text": chunk_text,
                    }
                )
                chunk_index += 1

            if end == len(text):
                break

            start += step_size

    return chunks
