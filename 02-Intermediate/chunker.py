def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks, preferring to cut at spaces."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)

        # avoid cutting a word in half: back up to the last space in the 2nd half of the chunk
        if end < n:
            space = text.rfind(" ", start + chunk_size // 2, end)
            if space != -1:
                end = space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= n:
            break
        start = max(end - overlap, start + 1)   # step forward, keeping `overlap` characters

    return chunks