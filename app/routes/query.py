from __future__ import annotations
import traceback
from flask import Blueprint, request, jsonify
from app.store import store
from app.models.generator import generate_answer
from app.models.retriever import retrieve_top_k
from app.utils.metrics import evaluate_retrieval, answer_faithfulness

query_bp = Blueprint("query", __name__)


def _guard():
    if not store.is_indexed:
        return {"error": "No documents indexed yet. Please ingest papers first."}
    return None


@query_bp.route("/query", methods=["POST"])
def query():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    method = data.get("method", "hybrid")
    k = max(1, min(int(data.get("k", 5)), 10))

    if not question:
        return jsonify({"error": "question is required"}), 400
    if (err := _guard()):
        return jsonify(err), 400

    try:
        results = retrieve_top_k(question, method, store.faiss_index, store.bm25_index, store.chunks, k=k)
        context = "\n\n".join(r["chunk"]["text"] for r in results)
        answer = generate_answer(question, context)
        metrics = evaluate_retrieval(question, results)
        metrics["faithfulness"] = answer_faithfulness(answer, context)
        return jsonify({
            "answer": answer,
            "retrieved_chunks": [{"rank": r["rank"], "score": r["score"], "text": r["chunk"]["text"][:400], "title": r["chunk"].get("title", ""), "source": r["chunk"].get("source", "")} for r in results],
            "metrics": metrics,
        })
    except Exception as exc:
        return jsonify({"error": str(exc), "trace": traceback.format_exc()}), 500


@query_bp.route("/compare", methods=["POST"])
def compare():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    k = max(1, min(int(data.get("k", 5)), 10))

    if not question:
        return jsonify({"error": "question is required"}), 400
    if (err := _guard()):
        return jsonify(err), 400

    try:
        comparison = {}
        for method in ["bm25", "vector", "hybrid"]:
            results = retrieve_top_k(question, method, store.faiss_index, store.bm25_index, store.chunks, k=k)
            comparison[method] = {
                "results": [{"rank": r["rank"], "score": r["score"], "text": r["chunk"]["text"][:300], "title": r["chunk"].get("title", "")} for r in results],
                "metrics": evaluate_retrieval(question, results),
            }
        return jsonify({"question": question, "comparison": comparison})
    except Exception as exc:
        return jsonify({"error": str(exc), "trace": traceback.format_exc()}), 500


@query_bp.route("/evaluate-batch", methods=["POST"])
def evaluate_batch():
    data = request.get_json(silent=True) or {}
    questions = data.get("questions", [])
    k = max(1, min(int(data.get("k", 5)), 10))

    if not questions:
        return jsonify({"error": "questions list is required"}), 400
    if (err := _guard()):
        return jsonify(err), 400

    try:
        agg = {m: {"context_relevance": [], "diversity": []} for m in ["bm25", "vector", "hybrid"]}
        for q in questions[:10]:
            for method in agg:
                results = retrieve_top_k(q.strip(), method, store.faiss_index, store.bm25_index, store.chunks, k=k)
                mt = evaluate_retrieval(q, results)
                agg[method]["context_relevance"].append(mt["context_relevance"])
                agg[method]["diversity"].append(mt["diversity"])
        summary = {m: {"avg_context_relevance": round(sum(v["context_relevance"]) / len(v["context_relevance"]), 4), "avg_diversity": round(sum(v["diversity"]) / len(v["diversity"]), 4)} for m, v in agg.items()}
        return jsonify({"summary": summary, "n_queries": len(questions[:10])})
    except Exception as exc:
        return jsonify({"error": str(exc), "trace": traceback.format_exc()}), 500
