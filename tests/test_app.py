import pytest

from app.store import DocumentStore
from app.utils.metrics import evaluate_retrieval, answer_faithfulness

PAPERS = [
    {"id": "1111.0001", "title": "Dense retrieval",
     "abstract": "Dense retrieval embeds queries and documents. It finds related passages even without shared words. "
                 "Results improve on paraphrased questions.",
     "authors": "A", "published": "2024-01-01", "categories": "cs.IR", "url": "http://arxiv.org/abs/1111.0001"},
    {"id": "1111.0002", "title": "Sparse retrieval",
     "abstract": "BM25 scores documents by term frequency. It is fast and precise on exact terms. "
                 "Names and numbers are matched well.",
     "authors": "B", "published": "2024-01-02", "categories": "cs.IR", "url": "http://arxiv.org/abs/1111.0002"},
]


@pytest.fixture
def client(clean_store):
    from app import create_app

    server, _ = create_app()
    server.config["TESTING"] = True
    return server.test_client()


@pytest.fixture
def arxiv(monkeypatch):
    from app import services

    monkeypatch.setattr(services, "fetch_arxiv_papers", lambda q, max_results=5: PAPERS[:max_results])


# ── Store ────────────────────────────────────────────────────────────────────

def test_reloaded_store_can_answer_queries(tmp_path):
    from app.models.embedder import embed_texts

    first = DocumentStore(str(tmp_path))
    first.add_chunks([{"id": "a", "text": "alpha beta gamma delta"}, {"id": "b", "text": "epsilon zeta eta theta"}])
    first.set_embeddings(embed_texts(first.chunk_texts))
    first.rebuild_indices()
    first.save()

    second = DocumentStore(str(tmp_path))          # a restart
    assert second.is_indexed
    assert second.faiss_index.ntotal == 2


def test_clear_empties_everything(clean_store, arxiv):
    from app.services import index_papers

    index_papers("retrieval")
    clean_store.clear()
    assert clean_store.stats() == {"n_documents": 0, "n_chunks": 0, "has_faiss": False, "has_bm25": False}


# ── Ingest service ───────────────────────────────────────────────────────────

def test_index_papers_builds_both_indices(clean_store, arxiv):
    from app.services import index_papers

    result = index_papers("retrieval")
    assert result["papers_added"] == 2 and result["chunks_added"] >= 2
    assert clean_store.is_indexed
    assert len(clean_store.embeddings) == len(clean_store.chunks) == clean_store.faiss_index.ntotal


def test_second_fetch_only_embeds_new_chunks(clean_store, monkeypatch):
    from app import services
    from tests.conftest import fake_embed_texts

    embedded = []

    def counting(texts, *a, **k):
        embedded.append(len(texts))
        return fake_embed_texts(texts)

    monkeypatch.setattr(services, "embed_texts", counting)
    monkeypatch.setattr(services, "fetch_arxiv_papers", lambda q, max_results=5: PAPERS[:1])
    services.index_papers("first")
    monkeypatch.setattr(services, "fetch_arxiv_papers", lambda q, max_results=5: PAPERS)
    result = services.index_papers("second")

    assert result["papers_added"] == 1                       # the first paper is already known
    assert embedded[1] == result["chunks_added"]             # old chunks are not embedded again
    assert len(clean_store.embeddings) == len(clean_store.chunks)


def test_refetching_known_papers_changes_nothing(clean_store, arxiv):
    from app.services import index_papers

    index_papers("retrieval")
    before = clean_store.stats()
    again = index_papers("retrieval")
    assert again["papers_added"] == 0 and again["chunks_added"] == 0
    assert clean_store.stats() == before


# ── Metrics ──────────────────────────────────────────────────────────────────

def _result(text, score=0.5):
    return {"chunk": {"text": text}, "score": score}


def test_evaluate_retrieval_handles_no_results():
    assert evaluate_retrieval("anything", [])["n_retrieved"] == 0


def test_identical_chunks_have_no_diversity():
    mt = evaluate_retrieval("dense retrieval", [_result("dense retrieval"), _result("dense retrieval")])
    assert mt["diversity"] == pytest.approx(0.0, abs=1e-3)


def test_relevant_chunks_score_higher_than_unrelated_ones():
    relevant = evaluate_retrieval("dense retrieval", [_result("dense retrieval embeddings")])
    unrelated = evaluate_retrieval("dense retrieval", [_result("cooking pasta with tomato")])
    assert relevant["context_relevance"] > unrelated["context_relevance"]


def test_faithfulness_is_word_overlap():
    assert answer_faithfulness("alpha beta", "alpha beta gamma") == 1.0
    assert answer_faithfulness("alpha zeta", "alpha beta gamma") == 0.5
    assert answer_faithfulness("", "alpha") == 0.0


# ── Generator fallbacks ──────────────────────────────────────────────────────

def test_refusal_falls_back_to_retrieved_sentences(monkeypatch):
    from app.models import generator

    class Refuses:
        def __call__(self, *a, **k):
            return [{"generated_text": "The sentences do not contain enough information."}]

    cfg = generator.MODEL_OPTIONS[generator.DEFAULT_MODEL]
    monkeypatch.setattr(generator, "get_generator", lambda m=None: (Refuses(), cfg))
    context = ("Dense retrieval embeds queries and documents into one space. "
               "It finds related passages without shared words.")
    assert "Dense retrieval embeds" in generator.generate_answer("what is dense retrieval", context)


# ── REST API ─────────────────────────────────────────────────────────────────

def test_stats_start_empty(client):
    assert client.get("/api/stats").get_json()["n_chunks"] == 0


def test_query_needs_an_index(client):
    r = client.post("/api/query", json={"question": "what is bm25"})
    assert r.status_code == 400 and "No documents" in r.get_json()["error"]


def test_query_validates_input(client):
    assert client.post("/api/query", json={}).status_code == 400
    assert client.post("/api/query", json={"question": "x", "method": "nope"}).status_code == 400
    assert client.post("/api/query", json={"question": "x", "model_id": "nope"}).status_code == 400


def test_fetch_arxiv_flow(client, arxiv):
    r = client.post("/api/fetch-arxiv", json={"query": "retrieval", "max_results": 2})
    assert r.status_code == 200 and r.get_json()["papers_added"] == 2

    compare = client.post("/api/compare", json={"question": "term frequency", "k": 3}).get_json()
    assert set(compare["comparison"]) == {"bm25", "vector", "hybrid"}
    assert compare["comparison"]["bm25"]["results"][0]["title"] == "Sparse retrieval"

    batch = client.post("/api/evaluate-batch", json={"questions": ["dense embeddings", "term frequency"]}).get_json()
    assert batch["n_queries"] == 2
    assert set(batch["summary"]) == {"bm25", "vector", "hybrid"}


def test_query_returns_answer_and_metrics(client, arxiv, monkeypatch):
    from app.routes import query as query_routes

    client.post("/api/fetch-arxiv", json={"query": "retrieval"})
    monkeypatch.setattr(query_routes, "generate_answer", lambda q, c, model_id=None: "BM25 scores by term frequency.")
    body = client.post("/api/query", json={"question": "how does bm25 score", "method": "bm25"}).get_json()
    assert body["answer"].startswith("BM25")
    assert body["retrieved_chunks"][0]["rank"] == 1
    assert 0 <= body["metrics"]["faithfulness"] <= 1


def test_errors_do_not_leak_stack_traces(client, monkeypatch):
    from app.routes import ingest as ingest_routes

    def boom(*a, **k):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(ingest_routes, "index_papers", boom)
    r = client.post("/api/fetch-arxiv", json={"query": "x"})
    assert r.status_code == 502
    text = r.get_data(as_text=True)
    assert "secret internal detail" not in text and "Traceback" not in text and "trace" not in r.get_json()


def test_no_papers_found_is_a_404(client, monkeypatch):
    from app import services

    monkeypatch.setattr(services, "fetch_arxiv_papers", lambda q, max_results=5: [])
    assert client.post("/api/fetch-arxiv", json={"query": "zzzz"}).status_code == 404


def test_bad_max_results_is_rejected(client):
    assert client.post("/api/fetch-arxiv", json={"query": "x", "max_results": "many"}).status_code == 400


# ── Dashboard ────────────────────────────────────────────────────────────────

def test_passage_colour_marks_the_method_not_the_score():
    from app.dashboards.eval_dashboard import _chunk

    low = _chunk({"rank": 1, "score": 0.03, "chunk": {"text": "a", "title": "t"}}, color="#123456")
    high = _chunk({"rank": 1, "score": 1.0, "chunk": {"text": "a", "title": "t"}}, color="#123456")
    assert low.style["borderLeft"] == high.style["borderLeft"] == "3px solid #123456"
