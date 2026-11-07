"""Fast tests: no network, no model downloads."""
import os
import tempfile
import zlib

# The store is created when `app.store` is first imported, so point it at a scratch folder first.
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="rag-bench-test-")

import numpy as np
import pytest


def fake_embed_texts(texts, *args, **kwargs):
    """Deterministic bag-of-words embedding, so tests need no model download."""
    out = np.zeros((len(texts), 128), dtype="float32")
    for row, text in enumerate(texts):
        for word in str(text).lower().split():
            out[row, zlib.crc32(word.strip(".,;:!?").encode()) % 128] += 1.0
    return out / np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-9)


@pytest.fixture(autouse=True)
def fake_embeddings(monkeypatch):
    from app.models import embedder
    from app.utils import metrics
    from app import services

    for module in (embedder, metrics, services):
        monkeypatch.setattr(module, "embed_texts", fake_embed_texts)


@pytest.fixture
def clean_store():
    from app.store import store

    store.clear()
    yield store
    store.clear()
