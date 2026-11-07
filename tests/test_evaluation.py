"""The retrieval benchmark: its task construction and its saved results."""

import json
import xml.dom.minidom

from scripts import evaluate_retrieval as bench

SENTENCES = [
    "Dense retrieval embeds queries and documents into a shared space.",
    "Sparse retrieval counts the terms that queries and documents share.",
    "Hybrid retrieval fuses both rankings into a single ordered list.",
    "Reciprocal rank fusion needs no calibration between score scales.",
    "Chunk size changes what a single passage is able to answer well.",
    "Overlap keeps related ideas from being split across two passages.",
    "Evaluation on held out sentences measures how well papers are found.",
]
PAPER = {"id": "2001.0001", "title": "Retrieval methods", "abstract": " ".join(SENTENCES)}


def test_held_out_sentences_are_removed_from_the_index():
    chunks, queries = bench.build_task([PAPER])
    indexed = " ".join(c["text"] for c in chunks)
    assert len(queries) == bench.HELD_OUT_PER_PAPER
    for query in queries:
        assert query["text"] not in indexed
        assert query["doc_id"] == PAPER["id"]


def test_short_abstracts_are_skipped_as_query_sources():
    short = {**PAPER, "abstract": " ".join(SENTENCES[:3])}
    chunks, queries = bench.build_task([short])
    assert queries == [] and chunks            # still indexed, but no query is drawn from it


def test_first_relevant_rank_finds_the_source_paper():
    results = [
        {"rank": 1, "chunk": {"doc_id": "other"}},
        {"rank": 2, "chunk": {"doc_id": "mine"}},
        {"rank": 3, "chunk": {"doc_id": "mine"}},
    ]
    assert bench.first_relevant_rank(results, "mine") == 2
    assert bench.first_relevant_rank(results, "missing") is None


def test_evaluate_scores_a_tiny_corpus(monkeypatch):
    from tests.conftest import fake_embed_texts

    monkeypatch.setattr(bench, "embed_texts", fake_embed_texts)
    other = {**PAPER, "id": "2001.0002", "title": "Cooking",
             "abstract": " ".join(f"Boil the {w} pasta slowly in salted water for ten minutes {i}." for i, w in enumerate(
                 ["thin", "thick", "fresh", "dried", "green", "red", "yellow"]))}
    chunks, queries = bench.build_task([PAPER, other])
    results = bench.evaluate(chunks, queries)
    for method in bench.METHODS:
        assert results[method]["hit@5"] == 1.0          # two unrelated topics are easy to separate
        assert 0 < results[method]["mrr"] <= 1


def test_saved_results_match_the_figure_and_are_complete():
    report = json.loads(bench.RESULTS.read_text(encoding="utf-8"))
    assert set(report["results"]) == set(bench.METHODS)
    svg = bench.FIGURE.read_text(encoding="utf-8")
    xml.dom.minidom.parseString(svg)                    # well-formed
    for method in bench.METHODS:
        assert f"{report['results'][method]['hit@5']:.2f}" in svg


def test_saved_corpus_supports_the_reported_query_count():
    papers = json.loads(bench.CORPUS.read_text(encoding="utf-8"))
    report = json.loads(bench.RESULTS.read_text(encoding="utf-8"))
    chunks, queries = bench.build_task(papers)
    assert len(queries) == report["n_queries"]
    assert len(chunks) == report["n_chunks"]
