def chunk_text(
    text: str,
    chunk_size: int = 700,
    overlap: int = 120
) -> list[str]:
    """
    Split text into overlapping word-based chunks.

    chunk_size = approximate number of words per chunk
    overlap = repeated words between chunks
    """

    words = text.split()

    if not words:
        return []

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk = " ".join(chunk_words).strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks