import pytest

from app.models.retriever import (
    build_faiss_index, build_bm25_index, retrieve_vector, retrieve_bm25,
    reciprocal_rank_fusion, retrieve_top_k,
)
from app.utils.chunker import chunk_fixed, chunk_sentence_window, chunk_semantic

TEXTS = [
    "Retrieval augmented generation combines information retrieval with neural language model generation.",
    "BERT is a transformer encoder pre-trained with masked language modelling and next-sentence prediction.",
    "Attention mechanisms allow neural networks to focus on relevant parts of an input sequence.",
    "Dense retrieval uses neural embeddings to find semantically similar documents at query time.",
    "BM25 is a probabilistic sparse retrieval model based on term frequency and inverse document frequency.",
]
PARA = chr(10) * 2  # paragraph break
CHUNKS = [{"id": str(i), "text": t, "title": f"paper {i}"} for i, t in enumerate(TEXTS)]


@pytest.fixture
def indices():
    from app.models.embedder import embed_texts

    return build_faiss_index(embed_texts(TEXTS)), build_bm25_index(TEXTS)


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
    a = [(0, 0.9), (1, 0.8), (2, 0.6)]
    b = [(2, 0.95), (0, 0.7), (3, 0.5)]
    fused = reciprocal_rank_fusion([a, b])
    ids = [i for i, _ in fused]
    assert 0 in ids and 2 in ids
    assert fused[0][1] > fused[-1][1]


def test_rrf_rewards_agreement():
    # Chunk 7 is second in both lists; chunks 1 and 2 each top only one list.
    fused = reciprocal_rank_fusion([[(1, 1.0), (7, 0.5)], [(2, 1.0), (7, 0.5)]])
    assert fused[0][0] == 7


@pytest.mark.parametrize("method", ["bm25", "vector", "hybrid"])
def test_retrieve_top_k_shape(indices, method):
    fi, bm = indices
    results = retrieve_top_k("dense retrieval embeddings", method, fi, bm, CHUNKS, k=3)
    assert [r["rank"] for r in results] == [1, 2, 3]
    assert all(r["method"] == method for r in results)
    assert results[0]["chunk"]["id"] == "3"


def test_bm25_scores_are_normalised(indices):
    fi, bm = indices
    results = retrieve_top_k("sparse retrieval", "bm25", fi, bm, CHUNKS, k=3)
    assert results[0]["score"] == 1.0
    assert all(0 <= r["score"] <= 1 for r in results)


def test_chunk_fixed():
    assert len(chunk_fixed(" ".join(["word"] * 600), chunk_size=100, overlap=20)) >= 5


def test_chunk_sentence_window():
    text = ("Dense retrieval embeds queries and documents. Sparse retrieval counts matching terms. "
            "Hybrid retrieval fuses both rankings. Reciprocal rank fusion needs no score calibration. "
            "Chunk size changes what a passage can answer. Overlap keeps ideas from being split in half.")
    chunks = chunk_sentence_window(text, window=3, stride=2)
    assert len(chunks) == 3
    assert chunks[0].startswith("Dense retrieval") and "Hybrid retrieval" in chunks[0]


def test_chunk_sentence_window_drops_fragments():
    assert chunk_sentence_window("Too short. Tiny.") == []


def test_chunk_semantic():
    text = ("Transformers use self attention over tokens." + PARA +
            "Attention weights show which words matter." + PARA +
            "Embeddings place similar text close together.")
    chunks = chunk_semantic(text, max_chunk_chars=60)
    assert len(chunks) == 3


def test_chunk_semantic_merges_small_paragraphs():
    text = "Transformers use self attention." + PARA + "Attention weights show which words matter."
    assert len(chunk_semantic(text, max_chunk_chars=200)) == 1
