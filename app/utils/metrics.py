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

def retrieval_diversity(chunk_texts: List[str]) -> float:
    if len(chunk_texts) < 2: return 1.0
    embs = embed_texts(chunk_texts)
    sim = embs @ embs.T
    n = len(chunk_texts)
    pairs = [sim[i,j] for i in range(n) for j in range(i+1,n)]
    return round(1.0 - float(np.mean(pairs)), 4)

def evaluate_retrieval(query: str, results: List[Dict]) -> Dict:
    texts = [r["chunk"]["text"] for r in results]
    return {"context_relevance":round(context_relevance(query,texts),4),"diversity":retrieval_diversity(texts),"avg_score":round(float(np.mean([r["score"] for r in results])),4) if results else 0.0,"n_retrieved":len(results)}
