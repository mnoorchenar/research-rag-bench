from __future__ import annotations
from transformers import pipeline

_pipe = None
MODEL_ID = "google/flan-t5-base"
MAX_CONTEXT_CHARS = 900
MAX_NEW_TOKENS = 200


def get_generator():
    global _pipe
    if _pipe is None:
        _pipe = pipeline("text2text-generation", model=MODEL_ID, max_new_tokens=MAX_NEW_TOKENS)
    return _pipe


def generate_answer(question: str, context: str) -> str:
    """Generate an answer from context using Flan-T5-base (CPU-friendly, no API key needed)."""
    ctx = context[:MAX_CONTEXT_CHARS]
    prompt = f"Answer the following question based only on the provided context. If the context does not contain enough information, say 'I cannot answer from the provided context.'\n\nContext:\n{ctx}\n\nQuestion: {question}\n\nAnswer:"
    result = get_generator()(prompt, max_new_tokens=MAX_NEW_TOKENS, do_sample=False)
    return result[0]["generated_text"].strip()
