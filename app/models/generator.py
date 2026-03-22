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


def _distil_context(question: str, context: str, top_n: int = 6) -> str:
    """Extract the top_n most query-relevant sentences from context using embedding similarity.
    This gives Flan-T5 a focused, clean input instead of dense multi-paragraph blobs."""
    from app.models.embedder import embed_texts, embed_query

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", context) if len(s.strip()) > 25]
    if not sentences:
        return context

    q_emb = embed_query(question)
    s_embs = embed_texts(sentences)
    scores = s_embs @ q_emb
    top_idx = np.argsort(scores)[::-1][:top_n]
    # preserve original reading order so Flan-T5 sees coherent flow
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
