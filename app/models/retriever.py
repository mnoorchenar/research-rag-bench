from __future__ import annotations
from typing import List, Tuple, Dict
import numpy as np
import faiss
from rank_bm25 import BM25Okapi
from .embedder import embed_query


# ── index builders ────────────────────────────────────────────────────────────

def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """Inner-product index (equivalent to cosine similarity on L2-normalised vectors)."""
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings.astype(np.float32))
    return index


def build_bm25_index(texts: List[str]) -> BM25Okapi:
    return BM25Okapi([t.lower().split() for t in texts])


# ── individual retrievers ─────────────────────────────────────────────────────

def retrieve_vector(query: str, faiss_index: faiss.IndexFlatIP, k: int = 10) -> List[Tuple[int, float]]:
    q_emb = embed_query(query).astype(np.float32).reshape(1, -1)
    scores, indices = faiss_index.search(q_emb, min(k, faiss_index.ntotal))
    return [(int(i), float(s)) for i, s in zip(indices[0], scores[0]) if i >= 0]


def retrieve_bm25(query: str, bm25_index: BM25Okapi, k: int = 10) -> List[Tuple[int, float]]:
    scores = bm25_index.get_scores(query.lower().split())
    top_k = np.argsort(scores)[::-1][:k]
    return [(int(i), float(scores[i])) for i in top_k]


# ── Reciprocal Rank Fusion ────────────────────────────────────────────────────

def reciprocal_rank_fusion(ranked_lists: List[List[Tuple[int, float]]], k: int = 60) -> List[Tuple[int, float]]:
    """Standard RRF: score(d) = Σ 1/(k + rank(d)) across all lists. k=60 is the canonical default."""
    rrf: Dict[int, float] = {}
    for ranked in ranked_lists:
        for rank, (doc_id, _) in enumerate(ranked):
            rrf[doc_id] = rrf.get(doc_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(rrf.items(), key=lambda x: x[1], reverse=True)


# ── unified entry point ───────────────────────────────────────────────────────

def retrieve_top_k(query: str, method: str, faiss_index, bm25_index, chunks: List[Dict], k: int = 5) -> List[Dict]:
    if method == "vector":
        raw = retrieve_vector(query, faiss_index, k=k)
        return [{"chunk": chunks[i], "score": round(s, 4), "rank": r + 1, "method": "vector"} for r, (i, s) in enumerate(raw)]
    if method == "bm25":
        raw = retrieve_bm25(query, bm25_index, k=k)
        max_s = max((s for _, s in raw), default=1.0) or 1.0
        return [{"chunk": chunks[i], "score": round(s / max_s, 4), "rank": r + 1, "method": "bm25"} for r, (i, s) in enumerate(raw)]
    # hybrid
    vec = retrieve_vector(query, faiss_index, k=k * 2)
    bm = retrieve_bm25(query, bm25_index, k=k * 2)
    fused = reciprocal_rank_fusion([vec, bm])[:k]
    return [{"chunk": chunks[idx], "score": round(score, 6), "rank": r + 1, "method": "hybrid"} for r, (idx, score) in enumerate(fused)]
