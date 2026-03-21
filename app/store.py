from __future__ import annotations
import os
import pickle
import threading
from typing import List, Dict, Optional
import numpy as np


class DocumentStore:
    """Thread-safe in-memory store with pickle persistence to data/processed/store.pkl."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._lock = threading.Lock()
        self.documents: List[Dict] = []
        self.chunks: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
        self.faiss_index = None
        self.bm25_index = None
        os.makedirs(os.path.join(data_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(data_dir, "processed"), exist_ok=True)
        self._load()

    # ── persistence ──────────────────────────────────────────────────────────

    def _persist_path(self) -> str:
        return os.path.join(self.data_dir, "processed", "store.pkl")

    def _load(self):
        path = self._persist_path()
        if os.path.exists(path):
            try:
                with open(path, "rb") as fh:
                    data = pickle.load(fh)
                self.documents = data.get("documents", [])
                self.chunks = data.get("chunks", [])
                self.embeddings = data.get("embeddings", None)
            except Exception:
                pass

    def save(self):
        with self._lock:
            with open(self._persist_path(), "wb") as fh:
                pickle.dump({"documents": self.documents, "chunks": self.chunks, "embeddings": self.embeddings}, fh)

    # ── mutations ─────────────────────────────────────────────────────────────

    def add_document(self, doc: Dict):
        with self._lock:
            self.documents.append(doc)

    def add_chunks(self, new_chunks: List[Dict]):
        with self._lock:
            self.chunks.extend(new_chunks)

    def set_embeddings(self, embeddings: np.ndarray):
        with self._lock:
            self.embeddings = embeddings

    def clear(self):
        with self._lock:
            self.documents = []
            self.chunks = []
            self.embeddings = None
            self.faiss_index = None
            self.bm25_index = None
        self.save()

    # ── accessors ─────────────────────────────────────────────────────────────

    @property
    def chunk_texts(self) -> List[str]:
        return [c["text"] for c in self.chunks]

    @property
    def is_indexed(self) -> bool:
        return bool(self.chunks) and self.embeddings is not None and self.faiss_index is not None and self.bm25_index is not None

    def stats(self) -> Dict:
        return {
            "n_documents": len(self.documents),
            "n_chunks": len(self.chunks),
            "has_faiss": self.faiss_index is not None,
            "has_bm25": self.bm25_index is not None,
        }


store = DocumentStore()
