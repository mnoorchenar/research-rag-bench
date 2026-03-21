---
title: research-rag-bench
colorFrom: blue
colorTo: indigo
sdk: docker
---

<div align="center">

<h1>🔬 research-rag-bench</h1>
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=3000&pause=1000&color=6366f1&center=true&vCenter=true&width=700&lines=Hybrid+Search+%C2%B7+Dense+%2B+Sparse+Retrieval+over+arXiv;Compare+BM25+%C2%B7+Vector+%C2%B7+Hybrid+RRF+Fusion+live;Built+with+FAISS+%C2%B7+sentence-transformers+%C2%B7+Flan-T5+%C2%B7+Dash" alt="Typing SVG"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3b82f6?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-4f46e5?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-3b82f6?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Spaces-ffcc00?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/mnoorchenar/spaces)
[![Status](https://img.shields.io/badge/Status-Active-22c55e?style=for-the-badge)](#)

<br/>

**🔬 research-rag-bench** — A full-stack RAG evaluation platform that fetches arXiv research papers on any topic, indexes them using three retrieval strategies (BM25, dense vector, and Reciprocal Rank Fusion), and benchmarks retrieval quality live — showing exactly why hybrid search outperforms either method alone.

<br/>

---

</div>

## Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Getting Started](#-getting-started)
- [Docker Deployment](#-docker-deployment)
- [Dashboard Modules](#-dashboard-modules)
- [ML Models](#-ml-models)
- [Project Structure](#-project-structure)
- [Author](#-author)
- [Contributing](#-contributing)
- [Disclaimer](#disclaimer)
- [License](#-license)

---

## ✨ Features

<table>
  <tr>
    <td>🔀 <b>Hybrid Retrieval</b></td>
    <td>BM25 + dense FAISS search fused with Reciprocal Rank Fusion (k=60) — implemented from scratch, no black-box wrappers</td>
  </tr>
  <tr>
    <td>📊 <b>Live Evaluation Metrics</b></td>
    <td>Context relevance (embedding cosine), answer faithfulness (token overlap), and retrieval diversity computed on every query</td>
  </tr>
  <tr>
    <td>📄 <b>arXiv Integration</b></td>
    <td>Search and ingest real research papers in one click; choose from three chunking strategies (fixed, sentence-window, semantic)</td>
  </tr>
  <tr>
    <td>⚖️ <b>Side-by-Side Comparison</b></td>
    <td>Run any query across all three methods simultaneously and inspect ranked results and metrics per method</td>
  </tr>
  <tr>
    <td>🔒 <b>Secure by Design</b></td>
    <td>Role-based access, audit logs, encrypted data pipelines</td>
  </tr>
  <tr>
    <td>🐳 <b>Containerized Deployment</b></td>
    <td>Docker-first architecture, cloud-ready and scalable</td>
  </tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 research-rag-bench                      │
│                                                         │
│  ┌───────────┐    ┌───────────┐    ┌───────────────┐  │
│  │  arXiv    │───▶│  Hybrid   │───▶│   Flask API   │  │
│  │  Papers   │    │  RAG      │    │   Backend     │  │
│  └───────────┘    │  Engine   │    └───────┬───────┘  │
│                   │ BM25+FAISS│            │           │
│                   │   +RRF    │   ┌────────▼────────┐  │
│                   └───────────┘   │  Plotly Dash    │  │
│                                   │   Dashboard     │  │
│                                   └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git

### Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/mnoorchenar/research-rag-bench.git
cd research-rag-bench

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install PyTorch (CPU-only, ~700 MB)
pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu

# 4. Install remaining dependencies
pip install -r requirements.txt

# 5. Configure environment variables
cp .env.example .env

# 6. Run the application
python wsgi.py
```

Open your browser at `http://localhost:7860` 🎉

---

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker compose up --build

# Or pull and run the pre-built image
docker pull mnoorchenar/research-rag-bench
docker run -p 7860:7860 mnoorchenar/research-rag-bench
```

---

## 📊 Dashboard Modules

| Module | Description | Status |
|--------|-------------|--------|
| 📥 Ingest | Fetch arXiv papers by topic and index with configurable chunking | ✅ Live |
| 💬 Query | Ask questions and get answers with cited retrieved context | ✅ Live |
| ⚖️ Compare | BM25 vs Dense Vector vs Hybrid RRF side by side | ✅ Live |
| 📊 Evaluate | Batch evaluation with aggregate metrics charts across methods | ✅ Live |
| 🔌 REST API | Programmatic endpoints: `/api/fetch-arxiv`, `/api/query`, `/api/compare` | ✅ Live |
| 🧠 Fine-tune | Domain-specific embedding fine-tuning on ingested corpus | 🗓️ Planned |

---

## 🧠 ML Models

```python
# Core models used in research-rag-bench
models = {
    "embedder": "sentence-transformers/all-MiniLM-L6-v2",
    "sparse_retrieval": "BM25Okapi (rank-bm25)",
    "vector_store": "FAISS IndexFlatIP (faiss-cpu)",
    "fusion": "Reciprocal Rank Fusion (k=60)",
    "generator": "google/flan-t5-base"
}
```

---

## 📁 Project Structure

```
research-rag-bench/
│
├── 📂 app/
│   ├── 📄 __init__.py          # Flask app factory
│   ├── 📄 store.py             # Thread-safe document & index store
│   ├── 📂 models/              # ML model definitions & loaders
│   │   ├── 📄 embedder.py      # SentenceTransformer wrapper
│   │   ├── 📄 generator.py     # Flan-T5 answer generation
│   │   └── 📄 retriever.py     # FAISS, BM25, and RRF retrieval
│   ├── 📂 routes/              # Flask API endpoints
│   │   ├── 📄 ingest.py        # /api/fetch-arxiv, /api/clear, /api/stats
│   │   └── 📄 query.py         # /api/query, /api/compare, /api/evaluate-batch
│   ├── 📂 dashboards/          # Plotly Dash layouts and callbacks
│   │   └── 📄 eval_dashboard.py
│   └── 📂 utils/               # Helpers, preprocessing, metrics
│       ├── 📄 chunker.py       # Fixed, sentence-window, semantic chunking
│       ├── 📄 metrics.py       # Context relevance, faithfulness, diversity
│       └── 📄 arxiv_loader.py  # arXiv API integration
│
├── 📂 data/
│   ├── 📂 raw/                 # Raw data sources
│   └── 📂 processed/           # Serialised document store (store.pkl)
│
├── 📂 tests/
│   └── 📄 test_retrieval.py    # Unit tests for retrieval and chunking
│
├── 📄 wsgi.py                  # Application entry point
├── 📄 Dockerfile               # Container definition
├── 📄 docker-compose.yml       # Multi-service orchestration
├── 📄 requirements.txt         # Python dependencies
└── 📄 .env.example             # Environment variable template
```

---

## 👨‍💻 Author

<div align="center">

<table>
<tr>
<td align="center" width="100%">

<img src="https://avatars.githubusercontent.com/mnoorchenar" width="120" style="border-radius:50%; border: 3px solid #4f46e5;" alt="Mohammad Noorchenarboo"/>

<h3>Mohammad Noorchenarboo</h3>

<code>Data Scientist</code> &nbsp;|&nbsp; <code>AI Researcher</code> &nbsp;|&nbsp; <code>Biostatistician</code>

📍 &nbsp;Ontario, Canada &nbsp;&nbsp; 📧 &nbsp;[mohammadnoorchenarboo@gmail.com](mailto:mohammadnoorchenarboo@gmail.com)

──────────────────────────────────────

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mnoorchenar)&nbsp;
[![Personal Site](https://img.shields.io/badge/Website-mnoorchenar.github.io-4f46e5?style=for-the-badge&logo=githubpages&logoColor=white)](https://mnoorchenar.github.io/)&nbsp;
[![HuggingFace](https://img.shields.io/badge/HuggingFace-ffcc00?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/mnoorchenar/spaces)&nbsp;
[![Google Scholar](https://img.shields.io/badge/Scholar-4285F4?style=for-the-badge&logo=googlescholar&logoColor=white)](https://scholar.google.ca/citations?user=nn_Toq0AAAAJ&hl=en)&nbsp;
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mnoorchenar)

</td>
</tr>
</table>

</div>

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## Disclaimer

<span style="color:red">This project is developed strictly for educational and research purposes and does not constitute professional advice of any kind. All datasets used are either synthetically generated or publicly available — no real user data is stored. This software is provided "as is" without warranty of any kind; use at your own risk.</span>

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:3b82f6,100:4f46e5&height=120&section=footer&text=Made%20with%20%E2%9D%A4%EF%B8%8F%20by%20Mohammad%20Noorchenarboo&fontColor=ffffff&fontSize=18&fontAlignY=80" width="100%"/>

[![GitHub Stars](https://img.shields.io/github/stars/mnoorchenar/research-rag-bench?style=social)](https://github.com/mnoorchenar/research-rag-bench)
[![GitHub Forks](https://img.shields.io/github/forks/mnoorchenar/research-rag-bench?style=social)](https://github.com/mnoorchenar/research-rag-bench/fork)

<sub>The name "research-rag-bench" is used purely for academic and research purposes. Any similarity to existing company names, products, or trademarks is entirely coincidental and unintentional. This project has no affiliation with any commercial entity.</sub>

</div>
