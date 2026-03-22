from __future__ import annotations
import re
from typing import List

def chunk_fixed(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i:i+chunk_size]))
        i += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 30]

def chunk_sentence_window(text: str, window: int = 5, stride: int = 3) -> List[str]:
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.strip()) > 20]
    chunks, i = [], 0
    while i < len(sents):
        chunks.append(" ".join(sents[i:i+window]))
        i += stride
    return [c for c in chunks if len(c.strip()) > 30]

def chunk_semantic(text: str, max_chunk_chars: int = 600) -> List[str]:
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if len(p.strip()) > 30]
    chunks, buf = [], ""
    for p in paras:
        if len(buf) + len(p) <= max_chunk_chars: buf = (buf + " " + p).strip()
        else:
            if buf: chunks.append(buf)
            buf = p
    if buf: chunks.append(buf)
    return chunks if chunks else chunk_fixed(text)

STRATEGY_MAP = {"fixed": chunk_fixed, "sentence_window": chunk_sentence_window, "semantic": chunk_semantic}

def chunk_text(text: str, strategy: str = "sentence_window") -> List[str]:
    return STRATEGY_MAP.get(strategy, chunk_sentence_window)(text)
