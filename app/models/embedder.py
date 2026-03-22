from __future__ import annotations
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

_model = None
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

def get_embedder():
    global _model
    if _model is None: _model = SentenceTransformer(MODEL_ID)
    return _model

def embed_texts(texts: List[str]) -> np.ndarray:
    return get_embedder().encode(texts, normalize_embeddings=True, show_progress_bar=False, batch_size=32)

def embed_query(query: str) -> np.ndarray:
    return embed_texts([query])[0]
