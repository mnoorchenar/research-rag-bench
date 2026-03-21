from __future__ import annotations
from typing import List, Dict
import numpy as np
from app.models.embedder import embed_texts, embed_query


def context_relevance(query: str, chunk_texts: List[str]) -> float:
    """Average cosine similarity between the query embedding and each retrieved chunk embedding."""
    if not chunk_texts:
        return 0.0
    q_emb = embed_query(query)
    c_embs = embed_texts(chunk_texts)
    return float(np.mean(c_embs @ q_emb))


def answer_faithfulness(answer: str, context: str) -> float:
    """Token-overlap precision: fraction of answer tokens that appear in the context."""
    answer_tokens = set(answer.lower().split())
    if not answer_tokens:
        return 0.0
    context_tokens = set(context.lower().split())
    return round(len(answer_tokens & context_tokens) / len(answer_tokens), 4)


def retrieval_diversity(chunk_texts: List[str]) -> float:
    """1 − mean pairwise cosine similarity between retrieved chunks. Higher = more diverse."""
    if len(chunk_texts) < 2:
        return 1.0
    embs = embed_texts(chunk_texts)
    sim_matrix = embs @ embs.T
    n = len(chunk_texts)
    pairs = [sim_matrix[i, j] for i in range(n) for j in range(i + 1, n)]
    return round(1.0 - float(np.mean(pairs)), 4)


def evaluate_retrieval(query: str, results: List[Dict]) -> Dict[str, float]:
    texts = [r["chunk"]["text"] for r in results]
    return {
        "context_relevance": round(context_relevance(query, texts), 4),
        "diversity": retrieval_diversity(texts),
        "avg_score": round(float(np.mean([r["score"] for r in results])), 4) if results else 0.0,
        "n_retrieved": len(results),
    }
