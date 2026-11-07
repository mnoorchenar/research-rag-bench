"""Shared ingestion logic, used by both the REST API and the dashboard."""
from __future__ import annotations
import threading

import numpy as np

from app.store import store
from app.models.embedder import embed_texts
from app.utils.arxiv_loader import fetch_arxiv_papers
from app.utils.chunker import chunk_text

_index_lock = threading.Lock()


def index_papers(query: str, max_results: int = 5, strategy: str = "sentence_window") -> dict:
    """Fetch papers from arXiv, chunk them and add them to the search indices.

    Only the new chunks are embedded; earlier embeddings are reused.
    Returns {"found", "papers_added", "chunks_added"}; "found" is 0 when arXiv has no match.
    """
    papers = fetch_arxiv_papers(query, max_results=max_results)
    if not papers:
        return {"found": 0, "papers_added": 0, "chunks_added": 0}

    with _index_lock:
        known = {d["id"] for d in store.documents}
        new_chunks, added = [], 0
        for p in papers:
            if p["id"] in known:
                continue
            store.add_document(p)
            added += 1
            for i, text in enumerate(chunk_text(f"{p['title']}.\n\n{p['abstract']}", strategy)):
                new_chunks.append({"id": f"{p['id']}_chunk_{i}", "doc_id": p["id"], "title": p["title"],
                                   "text": text, "chunk_idx": i, "source": p["url"]})
        if new_chunks:
            old = store.embeddings
            if old is not None and len(old) == len(store.chunks):
                embeddings = np.vstack([old, embed_texts([c["text"] for c in new_chunks])])
                store.add_chunks(new_chunks)
            else:                                   # nothing reusable: embed everything
                store.add_chunks(new_chunks)
                embeddings = embed_texts(store.chunk_texts)
            store.set_embeddings(embeddings)
            store.rebuild_indices()
            store.save()
        return {"found": len(papers), "papers_added": added, "chunks_added": len(new_chunks)}
