from __future__ import annotations
import logging
from flask import Blueprint, request, jsonify
from app.store import store
from app.models.generator import generate_answer, DEFAULT_MODEL, MODEL_OPTIONS
from app.models.retriever import retrieve_top_k
from app.utils.metrics import evaluate_retrieval, answer_faithfulness

log = logging.getLogger(__name__)
query_bp = Blueprint("query", __name__)
METHODS = ("bm25", "vector", "hybrid")


def _guard():
    if not store.is_indexed:
        return {"error": "No documents indexed yet."}
    return None


def _k(data) -> int:
    try:
        return max(1, min(int(data.get("k", 5)), 10))
    except (TypeError, ValueError):
        return 5


def _failure(what: str):
    log.exception(what)
    return jsonify({"error": f"{what}. Try again in a moment."}), 500


@query_bp.route("/query", methods=["POST"])
def query():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()
    method = data.get("method", "hybrid")
    model_id = data.get("model_id", DEFAULT_MODEL)
    if not question:
        return jsonify({"error": "question is required"}), 400
    if method not in METHODS:
        return jsonify({"error": f"method must be one of {', '.join(METHODS)}"}), 400
    if model_id not in MODEL_OPTIONS:
        return jsonify({"error": f"model_id must be one of {', '.join(MODEL_OPTIONS)}"}), 400
    if (err := _guard()):
        return jsonify(err), 400
    try:
        results = retrieve_top_k(question, method, store.faiss_index, store.bm25_index, store.chunks, k=_k(data))
        context = "\n\n".join(r["chunk"]["text"] for r in results)
        answer = generate_answer(question, context, model_id=model_id)
        mt = evaluate_retrieval(question, results)
        mt["faithfulness"] = answer_faithfulness(answer, context)
        return jsonify({"answer": answer,
                        "retrieved_chunks": [{"rank": r["rank"], "score": r["score"], "text": r["chunk"]["text"][:400],
                                              "title": r["chunk"].get("title", ""), "source": r["chunk"].get("source", "")}
                                             for r in results],
                        "metrics": mt})
    except Exception:
        return _failure("Could not answer the question")


@query_bp.route("/compare", methods=["POST"])
def compare():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    if (err := _guard()):
        return jsonify(err), 400
    try:
        k = _k(data)
        comparison = {}
        for method in METHODS:
            results = retrieve_top_k(question, method, store.faiss_index, store.bm25_index, store.chunks, k=k)
            comparison[method] = {"results": [{"rank": r["rank"], "score": r["score"], "text": r["chunk"]["text"][:300],
                                               "title": r["chunk"].get("title", "")} for r in results],
                                  "metrics": evaluate_retrieval(question, results)}
        return jsonify({"question": question, "comparison": comparison})
    except Exception:
        return _failure("Could not compare the methods")


@query_bp.route("/evaluate-batch", methods=["POST"])
def evaluate_batch():
    data = request.get_json(silent=True) or {}
    questions = [str(q).strip() for q in data.get("questions", []) if str(q).strip()][:10]
    if not questions:
        return jsonify({"error": "questions list is required"}), 400
    if (err := _guard()):
        return jsonify(err), 400
    try:
        k = _k(data)
        agg = {m: {"context_relevance": [], "diversity": []} for m in METHODS}
        for q in questions:
            for method in METHODS:
                results = retrieve_top_k(q, method, store.faiss_index, store.bm25_index, store.chunks, k=k)
                mt = evaluate_retrieval(q, results)
                agg[method]["context_relevance"].append(mt["context_relevance"])
                agg[method]["diversity"].append(mt["diversity"])
        summary = {m: {"avg_context_relevance": round(sum(v["context_relevance"]) / len(questions), 4),
                       "avg_diversity": round(sum(v["diversity"]) / len(questions), 4)} for m, v in agg.items()}
        return jsonify({"summary": summary, "n_queries": len(questions)})
    except Exception:
        return _failure("Could not evaluate the questions")
