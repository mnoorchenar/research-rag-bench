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


def test_bm25_returns_k_results(indices):
    _, bm25_idx = indices
    results = retrieve_bm25("transformer language model", bm25_idx, k=3)
    assert len(results) == 3
    assert all(0 <= i < len(TEXTS) for i, _ in results)


def test_vector_returns_k_results(indices):
    faiss_idx, _ = indices
    results = retrieve_vector("attention mechanism neural", faiss_idx, k=3)
    assert len(results) == 3


def test_vector_top_result_is_relevant(indices):
    faiss_idx, _ = indices
    results = retrieve_vector("BM25 term frequency", faiss_idx, k=1)
    assert results[0][0] == 4  # BM25 text is index 4


def test_rrf_merges_lists():
    list_a = [(0, 0.9), (1, 0.8), (2, 0.6)]
    list_b = [(2, 0.95), (0, 0.7), (3, 0.5)]
    fused = reciprocal_rank_fusion([list_a, list_b])
    ids = [i for i, _ in fused]
    assert 0 in ids and 2 in ids
    assert fused[0][1] > fused[-1][1]  # scores are descending


def test_rrf_scores_sum_correctly():
    single_list = [(0, 1.0), (1, 0.5)]
    fused = reciprocal_rank_fusion([single_list], k=60)
    expected_0 = 1.0 / (60 + 1)
    assert abs(fused[0][1] - expected_0) < 1e-9


def test_chunk_fixed():
    text = " ".join(["word"] * 600)
    chunks = chunk_fixed(text, chunk_size=100, overlap=20)
    assert len(chunks) >= 5


def test_chunk_sentence_window():
    text = "First sentence here. Second sentence about AI. Third about ML. Fourth about NLP. Fifth sentence done. Sixth one too."
    chunks = chunk_sentence_window(text, window=3, stride=2)
    assert len(chunks) >= 2


def test_chunk_semantic_respects_paragraphs():
    text = "Paragraph one about transformers.\n\nParagraph two about attention.\n\nParagraph three about embeddings and vector stores."
    chunks = chunk_semantic(text, max_chunk_chars=200)
    assert len(chunks) >= 2
