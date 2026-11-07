FROM python:3.10-slim
WORKDIR /app
ENV PORT=7860 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/opt/hf_home

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# typing-extensions comes from PyPI first: the PyTorch index only has its source package, which cannot be built there.
RUN pip install --no-cache-dir typing-extensions \
 && pip install --no-cache-dir torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Download the embedding model and the default answer model at build time,
# so the first question does not wait on a multi-gigabyte download.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" \
 && python -c "from transformers import pipeline; pipeline('text2text-generation', model='google/flan-t5-large')"

COPY . .
RUN mkdir -p data/raw data/processed docs
EXPOSE 7860
CMD ["gunicorn","--bind","0.0.0.0:7860","--workers","1","--timeout","300","wsgi:server"]
