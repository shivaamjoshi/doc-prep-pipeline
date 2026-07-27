def fixed_size_chunk(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    step = size - overlap

    i = 0
    while i < len(words):
        chunk_words = words[i:i+size]
        chunk_str = " ".join(chunk_words)
        chunks.append(chunk_str)

        if i + size >= len(words):   # this chunk already reached the end
            break

        i += step

    return chunks