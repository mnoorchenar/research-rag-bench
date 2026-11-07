from __future__ import annotations
from typing import List, Dict
import numpy as np
from app.models.embedder import embed_texts, embed_query

def context_relevance(query: str, chunk_texts: List[str]) -> float:
    if not chunk_texts: return 0.0
    return float(np.mean(embed_texts(chunk_texts) @ embed_query(query)))

def answer_faithfulness(answer: str, context: str) -> float:
    at = set(answer.lower().split())
    if not at: return 0.0
    return round(len(at & set(context.lower().split())) / len(at), 4)

def _diversity(embs: np.ndarray) -> float:
    """1 minus the mean pairwise cosine similarity (embeddings are normalised)."""
    n = len(embs)
    if n < 2: return 1.0
    sim = embs @ embs.T
    pairs = sim[np.triu_indices(n, k=1)]
    return round(1.0 - float(np.mean(pairs)), 4)

def retrieval_diversity(chunk_texts: List[str]) -> float:
    if len(chunk_texts) < 2: return 1.0
    return _diversity(embed_texts(chunk_texts))

def evaluate_retrieval(query: str, results: List[Dict]) -> Dict:
    texts = [r["chunk"]["text"] for r in results]
    avg_score = round(float(np.mean([r["score"] for r in results])), 4) if results else 0.0
    if not texts:
        return {"context_relevance": 0.0, "diversity": 1.0, "avg_score": avg_score, "n_retrieved": 0}
    embs = embed_texts(texts)           # one encoding pass serves both metrics
    relevance = float(np.mean(embs @ embed_query(query)))
    return {"context_relevance": round(relevance, 4), "diversity": _diversity(embs),
            "avg_score": avg_score, "n_retrieved": len(results)}
