from __future__ import annotations
import re
import numpy as np
from transformers import pipeline

# ── available models — ordered small → large ──────────────────────────────────
MODEL_OPTIONS = {
    "google/flan-t5-base":  {"label": "Flan-T5 Base  (fast, weaker answers)",   "max_ctx": 900,  "max_new": 200},
    "google/flan-t5-large": {"label": "Flan-T5 Large  (recommended, balanced)",  "max_ctx": 1800, "max_new": 256},
    "google/flan-t5-xl":    {"label": "Flan-T5 XL  (best answers, slow on CPU)", "max_ctx": 2400, "max_new": 320},
}
DEFAULT_MODEL = "google/flan-t5-large"

# per-model pipeline cache — avoids reloading when user switches back
_pipes: dict = {}

FAIL_PHRASES = [
    "do not contain a direct answer",
    "not contain enough information",
    "cannot answer",
    "no direct answer",
    "not directly answer",
    "does not provide",
    "not provided",
    "not mentioned",
]


def get_generator(model_id: str = DEFAULT_MODEL):
    if model_id not in MODEL_OPTIONS:
        model_id = DEFAULT_MODEL
    if model_id not in _pipes:
        _pipes[model_id] = pipeline(
            "text2text-generation",
            model=model_id,
            max_new_tokens=MODEL_OPTIONS[model_id]["max_new"],
        )
    return _pipes[model_id], MODEL_OPTIONS[model_id]


def _is_title_string(s: str) -> bool:
    """Return True if the string looks like a paper title rather than an informative sentence.
    Titles are short, lack verbs, and often contain colons or all-title-case words."""
    if len(s) < 40:
        return True
    words = s.split()
    # if more than 70% of words are title-cased and no lowercase function words appear, it's a title
    title_cased = sum(1 for w in words if w and w[0].isupper() and w not in ("The", "A", "An"))
    lowercase_content = sum(1 for w in words if w.islower() and len(w) > 3)
    if lowercase_content < 2:
        return True
    # sentences ending with a paper title pattern (word: word word word)
    if re.match(r"^[A-Z][^a-z]{0,5}[A-Z].*:.*[A-Z]", s) and "." not in s[10:]:
        return True
    return False


def _distil_context(question: str, context: str, top_n: int = 6) -> str:
    """Extract the top_n most query-relevant informative sentences using embedding similarity.
    Filters out paper title strings so Flan-T5 receives only content sentences."""
    from app.models.embedder import embed_texts, embed_query

    raw = [s.strip() for s in re.split(r"(?<=[.!?])\s+", context) if len(s.strip()) > 25]
    sentences = [s for s in raw if not _is_title_string(s)]
    if not sentences:
        sentences = raw  # fall back to all if filtering removed everything

    q_emb = embed_query(question)
    s_embs = embed_texts(sentences)
    scores = s_embs @ q_emb
    top_idx = np.argsort(scores)[::-1][:top_n]
    top_idx_sorted = sorted(top_idx)
    return " ".join(sentences[i] for i in top_idx_sorted)


def _is_refusal(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in FAIL_PHRASES)


def generate_answer(question: str, context: str, model_id: str = DEFAULT_MODEL) -> str:
    """Generate an answer using the selected Flan-T5 model with context distillation."""
    pipe, cfg = get_generator(model_id)

    # distil context to the most relevant sentences before feeding the model
    distilled = _distil_context(question, context, top_n=6)
    ctx = distilled[:cfg["max_ctx"]]

    prompt = (
        f"You are a research assistant. Use the sentences below to answer the question.\n\n"
        f"Sentences from papers:\n{ctx}\n\n"
        f"Question: {question}\n\n"
        f"Write a clear 2-3 sentence answer based on the sentences above. "
        f"If the sentences describe or use the concept, explain it in your own words.\n\n"
        f"Answer:"
    )

    result = pipe(prompt, max_new_tokens=cfg["max_new"], do_sample=False, repetition_penalty=1.3)
    answer = result[0]["generated_text"].strip()

    # if model still refuses, build a fallback answer from the distilled sentences directly
    if not answer or len(answer) < 12 or _is_refusal(answer):
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", ctx) if len(s.strip()) > 30]
        if sentences:
            return " ".join(sentences[:3])
        return "No sufficiently relevant content found in the indexed papers for this question."

    return answer
