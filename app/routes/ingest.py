from __future__ import annotations
import traceback
from flask import Blueprint, request, jsonify
from app.store import store
from app.models.embedder import embed_texts
from app.models.retriever import build_faiss_index, build_bm25_index
from app.utils.chunker import chunk_text
from app.utils.arxiv_loader import fetch_arxiv_papers

ingest_bp = Blueprint("ingest", __name__)

def _rebuild_indices():
    texts = store.chunk_texts
    if not texts: return
    embs = embed_texts(texts)
    store.set_embeddings(embs)
    store.faiss_index = build_faiss_index(embs)
    store.bm25_index  = build_bm25_index(texts)
    store.save()

@ingest_bp.route("/fetch-arxiv", methods=["POST"])
def fetch_arxiv():
    data = request.get_json(silent=True) or {}
    query = data.get("query","").strip()
    max_results = max(1,min(int(data.get("max_results",5)),15))
    strategy = data.get("chunk_strategy","sentence_window")
    if not query: return jsonify({"error":"query is required"}),400
    try:
        papers = fetch_arxiv_papers(query, max_results=max_results)
        if not papers: return jsonify({"error":"No papers found."}),404
        new_chunks, added_ids = [], []
        for p in papers:
            if any(d["id"]==p["id"] for d in store.documents): continue
            store.add_document(p); added_ids.append(p["id"])
            for i,ct in enumerate(chunk_text(f"{p['title']}.\n\n{p['abstract']}", strategy)):
                new_chunks.append({"id":f"{p['id']}_chunk_{i}","doc_id":p["id"],"title":p["title"],"text":ct,"chunk_idx":i,"source":p["url"]})
        store.add_chunks(new_chunks); _rebuild_indices()
        return jsonify({"status":"ok","papers_added":len(added_ids),"chunks_added":len(new_chunks),"stats":store.stats()})
    except Exception as exc:
        return jsonify({"error":str(exc),"trace":traceback.format_exc()}),500

@ingest_bp.route("/clear", methods=["POST"])
def clear_index():
    store.clear(); return jsonify({"status":"ok"})

@ingest_bp.route("/stats", methods=["GET"])
def get_stats():
    return jsonify(store.stats())
