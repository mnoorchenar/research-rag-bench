from __future__ import annotations
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


def generate_answer(question: str, context: str, model_id: str = DEFAULT_MODEL) -> str:
    """Generate an answer using the selected Flan-T5 model."""
    pipe, cfg = get_generator(model_id)
    ctx = context[:cfg["max_ctx"]]

    prompt = (
        f"You are a research assistant. Read the context below carefully, "
        f"then give a clear and complete answer to the question.\n\n"
        f"Context:\n{ctx}\n\n"
        f"Question: {question}\n\n"
        f"Instructions: Answer in 2-4 sentences using only information from the context. "
        f"If the context does not contain enough information to answer, "
        f"say exactly: 'The indexed papers do not contain a direct answer to this question.'\n\n"
        f"Answer:"
    )

    result = pipe(prompt, max_new_tokens=cfg["max_new"], do_sample=False, repetition_penalty=1.3)
    answer = result[0]["generated_text"].strip()
    if not answer or len(answer) < 8:
        return "The indexed papers do not contain a direct answer to this question."
    return answer
