"""Held-out sentence benchmark for BM25, dense vector and hybrid (RRF) retrieval.

For every paper, two sentences are removed from its abstract before indexing. Each removed
sentence then becomes a query, and the correct answer is the paper it came from. A method
scores a hit when a chunk of that paper is among its top results.

This measures how well each method finds the right paper from related wording. It is not
a test of answering real user questions. It also avoids the problem with the live "context
relevance" metric, which uses the same embedding model as the vector retriever.

Run from the repository root:

    python -m scripts.evaluate_retrieval            # uses the saved corpus snapshot
    python -m scripts.evaluate_retrieval --refresh  # downloads a new corpus from arXiv first

Writes docs/evaluation.json and docs/results.svg.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.models.embedder import MODEL_ID, embed_texts  # noqa: E402
from app.models.retriever import (  # noqa: E402
    build_bm25_index, build_faiss_index, retrieve_top_k,
)
from app.utils.arxiv_loader import fetch_arxiv_papers  # noqa: E402
from app.utils.chunker import chunk_text  # noqa: E402

CORPUS = ROOT / "docs" / "eval_corpus.json"
RESULTS = ROOT / "docs" / "evaluation.json"
FIGURE = ROOT / "docs" / "results.svg"

# The same three topics as the example chips in the dashboard.
TOPICS = [
    "machine learning model evaluation deep learning neural networks",
    "digital marketing consumer behavior NLP sentiment analysis",
    "clinical NLP biomedical text mining disease prediction",
]
PAPERS_PER_TOPIC = 10
CHUNK_STRATEGY = "sentence_window"
HELD_OUT_PER_PAPER = 2
MIN_SENTENCES = 6
MIN_QUERY_CHARS = 60
METHODS = ("bm25", "vector", "hybrid")
LABELS = {"bm25": "BM25", "vector": "Dense vector", "hybrid": "Hybrid RRF"}
COLORS = {"bm25": "#d97706", "vector": "#4f46e5", "hybrid": "#059669"}


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.strip()) > 20]


def load_corpus(refresh: bool) -> list[dict]:
    if CORPUS.exists() and not refresh:
        return json.loads(CORPUS.read_text(encoding="utf-8"))
    papers, seen = [], set()
    for topic in TOPICS:
        for paper in fetch_arxiv_papers(topic, max_results=PAPERS_PER_TOPIC):
            if paper["id"] not in seen:
                seen.add(paper["id"])
                papers.append({**paper, "topic": topic})
    CORPUS.write_text(json.dumps(papers, indent=1, ensure_ascii=False), encoding="utf-8")
    return papers


def build_task(papers: list[dict]):
    """Return (chunks, queries). Held-out sentences are removed from the indexed text."""
    chunks, queries = [], []
    for paper in papers:
        sentences = split_sentences(paper["abstract"])
        held_out = []
        if len(sentences) >= MIN_SENTENCES:
            for position in (len(sentences) // 3, (2 * len(sentences)) // 3)[:HELD_OUT_PER_PAPER]:
                if len(sentences[position]) >= MIN_QUERY_CHARS and sentences[position] not in held_out:
                    held_out.append(sentences[position])
        kept = " ".join(s for s in sentences if s not in held_out)
        for i, text in enumerate(chunk_text(f"{paper['title']}.\n\n{kept}", CHUNK_STRATEGY)):
            chunks.append({"id": f"{paper['id']}_{i}", "doc_id": paper["id"], "title": paper["title"], "text": text})
        queries += [{"text": s, "doc_id": paper["id"]} for s in held_out]
    return chunks, queries


def first_relevant_rank(results: list[dict], doc_id: str) -> int | None:
    """Rank (1-based) of the first chunk that belongs to the source paper."""
    for result in results:
        if result["chunk"]["doc_id"] == doc_id:
            return result["rank"]
    return None


def evaluate(chunks: list[dict], queries: list[dict]) -> dict:
    texts = [c["text"] for c in chunks]
    faiss_index, bm25_index = build_faiss_index(embed_texts(texts)), build_bm25_index(texts)
    scores = {m: {"hit@1": 0, "hit@5": 0, "rr": 0.0} for m in METHODS}
    for query in queries:
        for method in METHODS:
            results = retrieve_top_k(query["text"], method, faiss_index, bm25_index, chunks, k=len(chunks))
            rank = first_relevant_rank(results, query["doc_id"])
            if rank:
                scores[method]["hit@1"] += rank <= 1
                scores[method]["hit@5"] += rank <= 5
                scores[method]["rr"] += 1 / rank
    n = len(queries)
    return {m: {"hit@1": round(v["hit@1"] / n, 3), "hit@5": round(v["hit@5"] / n, 3), "mrr": round(v["rr"] / n, 3)}
            for m, v in scores.items()}


def write_figure(results: dict, n_queries: int, n_papers: int) -> None:
    """Grouped bar chart on a white card, so it reads in light and dark themes."""
    metrics = [("hit@1", "Hit@1"), ("hit@5", "Hit@5"), ("mrr", "MRR")]
    left, top, plot_w, plot_h = 70, 70, 880, 220
    group_w = plot_w / len(metrics)
    bar_w = 58
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="400" viewBox="0 0 1000 400" role="img" '
        'aria-labelledby="title desc" font-family="-apple-system, \'Segoe UI\', Helvetica, Arial, sans-serif">',
        '<title id="title">Retrieval benchmark: BM25, dense vector and hybrid search</title>',
        '<desc id="desc">' + "; ".join(
            f"{LABELS[m]}: Hit@1 {results[m]['hit@1']:.2f}, Hit@5 {results[m]['hit@5']:.2f}, MRR {results[m]['mrr']:.2f}"
            for m in METHODS) + f". {n_queries} held-out sentence queries over {n_papers} papers.</desc>",
        '<rect x="1" y="1" width="998" height="398" rx="12" fill="#ffffff" stroke="#d0d7de" stroke-width="2"/>',
        '<text x="24" y="34" font-size="17" font-weight="700" fill="#0f172a">Finding the source paper from a held-out sentence</text>',
        f'<text x="24" y="54" font-size="13" fill="#475569">{n_queries} queries, {n_papers} papers, higher is better</text>',
    ]
    for tick in (0, 0.25, 0.5, 0.75, 1.0):
        y = top + plot_h - tick * plot_h
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="#e2e8f0" stroke-width="1"/>')
        parts.append(f'<text x="{left - 10}" y="{y + 4:.1f}" font-size="12" fill="#64748b" text-anchor="end">{tick:.2f}</text>')
    for gi, (key, label) in enumerate(metrics):
        gx = left + gi * group_w
        for mi, method in enumerate(METHODS):
            value = results[method][key]
            height = value * plot_h
            x = gx + group_w / 2 - (len(METHODS) * bar_w + (len(METHODS) - 1) * 12) / 2 + mi * (bar_w + 12)
            y = top + plot_h - height
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w}" height="{height:.1f}" rx="4" fill="{COLORS[method]}"/>')
            parts.append(f'<text x="{x + bar_w / 2:.1f}" y="{y - 7:.1f}" font-size="13" font-weight="700" fill="#0f172a" text-anchor="middle">{value:.2f}</text>')
        parts.append(f'<text x="{gx + group_w / 2:.1f}" y="{top + plot_h + 24}" font-size="14" font-weight="600" fill="#0f172a" text-anchor="middle">{label}</text>')
    legend_x = 24
    for method in METHODS:
        parts.append(f'<rect x="{legend_x}" y="360" width="14" height="14" rx="3" fill="{COLORS[method]}"/>')
        parts.append(f'<text x="{legend_x + 22}" y="372" font-size="13" fill="#0f172a">{LABELS[method]}</text>')
        legend_x += 150
    parts.append("</svg>")
    FIGURE.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--refresh", action="store_true", help="download a new corpus from arXiv first")
    args = parser.parse_args()

    papers = load_corpus(args.refresh)
    chunks, queries = build_task(papers)
    results = evaluate(chunks, queries)

    report = {
        "date": datetime.date.today().isoformat(),
        "embedding_model": MODEL_ID,
        "chunk_strategy": CHUNK_STRATEGY,
        "n_papers": len({p["id"] for p in papers}),
        "n_chunks": len(chunks),
        "n_queries": len(queries),
        "results": results,
    }
    RESULTS.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_figure(results, len(queries), report["n_papers"])

    print(f"{report['n_queries']} queries, {report['n_papers']} papers, {report['n_chunks']} chunks")
    for method in METHODS:
        r = results[method]
        print(f"{LABELS[method]:13} hit@1 {r['hit@1']:.3f}  hit@5 {r['hit@5']:.3f}  mrr {r['mrr']:.3f}")


if __name__ == "__main__":
    main()
