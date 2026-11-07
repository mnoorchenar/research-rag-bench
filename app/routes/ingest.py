from __future__ import annotations
import logging
from flask import Blueprint, request, jsonify
from app.store import store
from app.services import index_papers

log = logging.getLogger(__name__)
ingest_bp = Blueprint("ingest", __name__)


@ingest_bp.route("/fetch-arxiv", methods=["POST"])
def fetch_arxiv():
    data = request.get_json(silent=True) or {}
    query = str(data.get("query", "")).strip()
    try:
        max_results = max(1, min(int(data.get("max_results", 5)), 15))
    except (TypeError, ValueError):
        return jsonify({"error": "max_results must be a number"}), 400
    strategy = data.get("chunk_strategy", "sentence_window")
    if not query:
        return jsonify({"error": "query is required"}), 400
    try:
        result = index_papers(query, max_results=max_results, strategy=strategy)
    except Exception:
        log.exception("arXiv ingest failed")
        return jsonify({"error": "Could not fetch or index papers. Try again in a moment."}), 502
    if not result["found"]:
        return jsonify({"error": "No papers found."}), 404
    return jsonify({"status": "ok", "papers_added": result["papers_added"],
                    "chunks_added": result["chunks_added"], "stats": store.stats()})


@ingest_bp.route("/clear", methods=["POST"])
def clear_index():
    store.clear()
    return jsonify({"status": "ok"})


@ingest_bp.route("/stats", methods=["GET"])
def get_stats():
    return jsonify(store.stats())
