import numpy as np
import pytest
from app.models.retriever import build_faiss_index, build_bm25_index, retrieve_vector, retrieve_bm25, reciprocal_rank_fusion
from app.utils.chunker import chunk_fixed, chunk_sentence_window, chunk_semantic

TEXTS = [
    "Retrieval augmented generation combines information retrieval with neural language model generation.",
    "BERT is a transformer encoder pre-trained with masked language modelling and next-sentence prediction.",
    "Attention mechanisms allow neural networks to focus on relevant parts of an input sequence.",
    "Dense retrieval uses neural embeddings to find semantically similar documents at query time.",
    "BM25 is a probabilistic sparse retrieval model based on term frequency and inverse document frequency.",
]

@pytest.fixture(scope="module")
def indices():
    from app.models.embedder import embed_texts
    embs = embed_texts(TEXTS)
    return build_faiss_index(embs), build_bm25_index(TEXTS)

def test_bm25_returns_k(indices):
    _, bm = indices
    assert len(retrieve_bm25("transformer language model", bm, k=3)) == 3

def test_vector_returns_k(indices):
    fi, _ = indices
    assert len(retrieve_vector("attention mechanism", fi, k=3)) == 3

def test_vector_top_result_relevant(indices):
    fi, _ = indices
    assert retrieve_vector("BM25 term frequency", fi, k=1)[0][0] == 4

def test_rrf_merges():
    a = [(0,0.9),(1,0.8),(2,0.6)]
    b = [(2,0.95),(0,0.7),(3,0.5)]
    fused = reciprocal_rank_fusion([a,b])
    ids = [i for i,_ in fused]
    assert 0 in ids and 2 in ids
    assert fused[0][1] > fused[-1][1]

def test_chunk_fixed():
    assert len(chunk_fixed(" ".join(["word"]*600), chunk_size=100, overlap=20)) >= 5

def test_chunk_sentence_window():
    text = "First sentence. Second about AI. Third about ML. Fourth about NLP. Fifth done. Sixth too."
    assert len(chunk_sentence_window(text, window=3, stride=2)) >= 2

def test_chunk_semantic():
    text = "Para one about transformers.\n\nPara two about attention.\n\nPara three about embeddings."
    assert len(chunk_semantic(text, max_chunk_chars=200)) >= 2
