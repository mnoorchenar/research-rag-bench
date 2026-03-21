from __future__ import annotations
import re
from typing import List


def chunk_fixed(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    """Split on word boundaries with a fixed window and configurable overlap."""
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i : i + chunk_size]))
        i += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 30]


def chunk_sentence_window(text: str, window: int = 5, stride: int = 3) -> List[str]:
    """Group consecutive sentences into overlapping windows — preserves local context."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.strip()) > 20]
    chunks, i = [], 0
    while i < len(sentences):
        chunks.append(" ".join(sentences[i : i + window]))
        i += stride
    return [c for c in chunks if len(c.strip()) > 30]


def chunk_semantic(text: str, max_chunk_chars: int = 600) -> List[str]:
    """Merge paragraphs greedily up to max_chunk_chars — respects natural topic boundaries."""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if len(p.strip()) > 30]
    chunks, buf = [], ""
    for para in paragraphs:
        if len(buf) + len(para) <= max_chunk_chars:
            buf = (buf + " " + para).strip()
        else:
            if buf:
                chunks.append(buf)
            buf = para
    if buf:
        chunks.append(buf)
    return chunks if chunks else chunk_fixed(text)


STRATEGY_MAP = {"fixed": chunk_fixed, "sentence_window": chunk_sentence_window, "semantic": chunk_semantic}


def chunk_text(text: str, strategy: str = "sentence_window") -> List[str]:
    return STRATEGY_MAP.get(strategy, chunk_sentence_window)(text)
