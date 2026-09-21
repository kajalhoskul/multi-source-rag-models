"""Simple word-based text chunking with overlap, shared by all three RAG pipelines."""
from typing import List


def chunk_text(text: str, chunk_size: int = 150, overlap: int = 30) -> List[str]:
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    step = max(chunk_size - overlap, 1)
    while start < len(words):
        chunk = " ".join(words[start:start + chunk_size])
        chunks.append(chunk)
        if start + chunk_size >= len(words):
            break
        start += step
    return chunks
