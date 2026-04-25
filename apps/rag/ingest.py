from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    index: int
    content: str


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[Chunk]:
    text = (text or "").strip()
    if not text:
        return []

    chunks: list[Chunk] = []
    i = 0
    idx = 0
    while i < len(text):
        end = min(len(text), i + chunk_size)
        content = text[i:end].strip()
        if content:
            chunks.append(Chunk(index=idx, content=content))
            idx += 1
        i = max(end - overlap, end)
    return chunks

