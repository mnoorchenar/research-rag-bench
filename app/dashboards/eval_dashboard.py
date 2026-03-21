from __future__ import annotations
import dash
from dash import dcc, html, Input, Output, State, ctx
import plotly.graph_objects as go

# ── design tokens ─────────────────────────────────────────────────────────────
C = {
    "bg": "#f8fafc", "surface": "#ffffff", "border": "#e2e8f0",
    "primary": "#4f46e5", "primary_light": "#eef2ff",
    "text": "#1e293b", "muted": "#64748b",
    "success": "#059669", "warning": "#d97706", "error": "#dc2626",
    "bm25": "#f59e0b", "vector": "#6366f1", "hybrid": "#10b981",
}
METHOD_COLORS = {"bm25": C["bm25"], "vector": C["vector"], "hybrid": C["hybrid"]}
METHOD_LABELS = {"bm25": "BM25", "vector": "Dense Vector", "hybrid": "Hybrid (RRF)"}

INPUT_STYLE = {"width": "100%", "padding": "8px 12px", "border": f"1px solid {C['border']}", "borderRadius": "8px", "fontSize": "14px", "color": C["text"], "outline": "none", "boxSizing": "border-box"}
BTN = {"padding": "9px 22px", "background": C["primary"], "color": "#fff", "border": "none", "borderRadius": "8px", "fontSize": "14px", "cursor": "pointer", "fontWeight": "600", "marginTop": "8px"}
BTN_DANGER = {**BTN, "background": C["error"], "marginLeft": "8px"}
LABEL = {"fontSize": "12px", "fontWeight": "600", "color": C["muted"], "marginBottom": "4px", "display": "block", "textTransform": "uppercase", "letterSpacing": "0.04em"}
CARD = {"background": C["surface"], "border": f"1px solid {C['border']}", "borderRadius": "12px", "padding": "20px", "marginBottom": "16px"}
TAB_STYLE = {"padding": "10px 22px", "color": C["muted"], "border": "none", "background": "transparent", "fontSize": "14px", "cursor": "pointer"}
TAB_SELECTED = {**TAB_STYLE, "color": C["primary"], "borderBottom": f"2px solid {C['primary']}", "fontWeight": "600"}

NOTICE_WARN = {"color": C["warning"], "fontSize": "13px", "marginTop": "8px"}
NOTICE_OK = {"color": C["success"], "fontSize": "13px", "marginTop": "8px"}
NOTICE_ERR = {"color": C["error"], "fontSize": "13px", "marginTop": "8px"}


# ── small helpers ──────────────────────────────────────────────────────────────

def card(children, extra=None):
    return html.Div(children, style={**CARD, **(extra or {})})


def pill(label, value, color):
    return html.Div([
        html.Div(label, style={"fontSize": "11px", "fontWeight": "600", "color": color, "textTransform": "uppercase", "letterSpacing": "0.05em"}),
        html.Div(str(value), style={"fontSize": "22px", "fontWeight": "700", "color": color, "marginTop": "2px"}),
    ], style={"textAlign": "center", "padding": "12px 18px", "background": f"{color}14", "borderRadius": "10px", "border": f"1px solid {color}28", "minWidth": "90px"})


def chunk_card(result, compact=False):
    ch = result["chunk"]
    txt = ch["text"][:180] + ("…" if compact and len(ch["text"]) > 180 else "") if compact else ch["text"]
    return html.Div([
        html.Div([
            html.Span(f"#{result['rank']}", style={"fontSize": "11px", "fontWeight": "700", "color": "#fff", "background": C["primary"], "borderRadius": "4px", "padding": "2px 7px", "marginRight": "8px"}),
            html.Span(ch.get("title", "")[:65], style={"fontSize": "12px", "fontWeight": "600", "color": C["muted"], "flex": "1"}),
            html.Span(f"score {result['score']}", style={"fontSize": "11px", "color": C["primary"], "background": C["primary_light"], "borderRadius": "4px", "padding": "2px 7px"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
        html.P(txt, style={"fontSize": "13px", "color": C["text"], "lineHeight": "1.6", "margin": 0}),
    ], style={"padding": "12px", "border": f"1px solid {C['border']}", "borderRadius": "8px", "marginBottom": "8px", "background": "#fafafe"})


def papers_table(documents):
    if not documents:
        return html.P("No papers indexed yet.", style={"color": C["muted"], "fontSize": "14px"})
    th_style = {"fontSize": "11px", "padding": "8px 12px", "color": C["muted"], "textTransform": "uppercase", "letterSpacing": "0.05em", "borderBottom": f"1px solid {C['border']}", "textAlign": "left"}
    td_style = {"fontSize": "13px", "padding": "9px 12px", "color": C["text"], "borderBottom": f"1px solid {C['bg']}"}
    return html.Table([
        html.Thead(html.Tr([html.Th("Title", style=th_style), html.Th("Authors", style=th_style), html.Th("Published", style=th_style), html.Th("Category", style=th_style)])),
        html.Tbody([html.Tr([html.Td(d.get("title", "")[:80], style=td_style), html.Td(d.get("authors", "")[:40], style={**td_style, "color": C["muted"]}), html.Td(d.get("published", ""), style={**td_style, "color": C["muted"]}), html.Td(d.get("categories", ""), style={**td_style, "color": C["muted"]})]) for d in documents]),
    ], style={"width": "100%", "borderCollapse": "collapse"})


def comparison_chart(all_metrics):
    fig = go.Figure()
    for m in ["bm25", "vector", "hybrid"]:
        fig.add_trace(go.Bar(name=METHOD_LABELS[m], x=["Context Relevance", "Diversity"], y=[all_metrics[m]["context_relevance"], all_metrics[m]["diversity"]], marker_color=METHOD_COLORS[m]))
    fig.update_layout(barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, sans-serif", size=12, color=C["text"]), margin=dict(l=20, r=20, t=20, b=20), height=240, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(range=[0, 1], gridcolor=C["border"])
    return fig


# ── tab layouts ───────────────────────────────────────────────────────────────

def _ingest_layout():
    return html.Div([
        card([
            html.Label("arXiv search query", style=LABEL),
            dcc.Input(id="arxiv-query", type="text", placeholder="e.g. retrieval augmented generation transformers", style=INPUT_STYLE),
            html.Div([
                html.Div([html.Label("Papers to fetch", style={**LABEL, "marginTop": "14px"}), dcc.Slider(id="n-papers", min=1, max=10, step=1, value=3, marks={i: str(i) for i in range(1, 11)}, tooltip={"placement": "bottom"})], style={"flex": "1"}),
                html.Div([html.Label("Chunking strategy", style={**LABEL, "marginTop": "14px"}), dcc.Dropdown(id="chunk-strategy", options=[{"label": "Sentence Window", "value": "sentence_window"}, {"label": "Fixed-size + overlap", "value": "fixed"}, {"label": "Semantic (paragraph-aware)", "value": "semantic"}], value="sentence_window", clearable=False, style={"fontSize": "14px"})], style={"flex": "1", "marginLeft": "28px"}),
            ], style={"display": "flex", "alignItems": "flex-end"}),
            html.Div([
                html.Button("🔍  Fetch & Index", id="fetch-btn", style=BTN),
                html.Button("🗑️  Clear Index", id="clear-btn", style=BTN_DANGER),
            ]),
            dcc.Loading(html.Div(id="ingest-status"), type="circle", color=C["primary"]),
        ]),
        card([
            html.H3("Indexed papers", style={"fontSize": "14px", "fontWeight": "600", "color": C["muted"], "marginTop": 0, "textTransform": "uppercase", "letterSpacing": "0.04em", "marginBottom": "12px"}),
            html.Div(id="papers-table"),
        ]),
    ], style={"maxWidth": "820px", "margin": "0 auto"})


def _query_layout():
    return html.Div([
        card([
            html.Label("Your question", style=LABEL),
            dcc.Input(id="query-input", type="text", placeholder="What is retrieval-augmented generation?", style={**INPUT_STYLE, "fontSize": "15px"}),
            html.Div([
                html.Div([html.Label("Retrieval method", style={**LABEL, "marginTop": "14px"}), dcc.RadioItems(id="query-method", options=[{"label": "  BM25", "value": "bm25"}, {"label": "  Dense Vector", "value": "vector"}, {"label": "  Hybrid RRF", "value": "hybrid"}], value="hybrid", inline=True, labelStyle={"marginRight": "18px", "fontSize": "14px"})], style={"flex": "1"}),
                html.Div([html.Label("Top-k chunks", style={**LABEL, "marginTop": "14px"}), dcc.Slider(id="query-k", min=1, max=10, step=1, value=5, marks={i: str(i) for i in [1, 3, 5, 7, 10]}, tooltip={"placement": "bottom"})], style={"flex": "1", "marginLeft": "28px"}),
            ], style={"display": "flex"}),
            html.Button("💬  Get Answer", id="query-btn", style=BTN),
        ]),
        dcc.Loading(html.Div(id="query-output"), type="dot", color=C["primary"]),
    ], style={"maxWidth": "820px", "margin": "0 auto"})


def _compare_layout():
    return html.Div([
        card([
            html.Label("Query to compare across methods", style=LABEL),
            dcc.Input(id="compare-input", type="text", placeholder="How does attention work in transformers?", style=INPUT_STYLE),
            html.Div([html.Label("Top-k", style={**LABEL, "marginTop": "14px"}), dcc.Slider(id="compare-k", min=1, max=8, step=1, value=4, marks={i: str(i) for i in range(1, 9)}, tooltip={"placement": "bottom"})]),
            html.Button("⚖️  Run Comparison", id="compare-btn", style=BTN),
        ]),
        dcc.Loading(html.Div(id="compare-output"), type="dot", color=C["primary"]),
    ], style={"maxWidth": "1100px", "margin": "0 auto"})


def _eval_layout():
    return html.Div([
        card([
            html.Label("Test queries — one per line (max 10)", style=LABEL),
            dcc.Textarea(id="eval-queries", placeholder="What is attention?\nHow does BERT differ from GPT?\nExplain gradient descent\nWhat is contrastive learning?", style={**INPUT_STYLE, "resize": "vertical", "fontFamily": "monospace", "fontSize": "13px", "minHeight": "110px"}),
            html.Div([html.Label("Top-k per query", style={**LABEL, "marginTop": "14px"}), dcc.Slider(id="eval-k", min=1, max=8, step=1, value=5, marks={i: str(i) for i in range(1, 9)}, tooltip={"placement": "bottom"})]),
            html.Button("📊  Run Batch Evaluation", id="eval-btn", style=BTN),
        ]),
        dcc.Loading(html.Div(id="eval-output"), type="circle", color=C["primary"]),
    ], style={"maxWidth": "820px", "margin": "0 auto"})


# ── factory ───────────────────────────────────────────────────────────────────

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname="/", suppress_callback_exceptions=True, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

    app.layout = html.Div([
        html.Div([
            html.Div([
                html.Span("🔬", style={"fontSize": "20px", "marginRight": "8px"}),
                html.Span("research-rag-bench", style={"fontSize": "18px", "fontWeight": "700", "color": C["text"]}),
                html.Span("Hybrid RAG · arXiv · Evaluation", style={"fontSize": "12px", "color": C["muted"], "marginLeft": "12px"}),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div(id="header-stats", style={"fontSize": "12px", "color": C["muted"]}),
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "12px 32px", "background": C["surface"], "borderBottom": f"1px solid {C['border']}", "position": "sticky", "top": 0, "zIndex": 100}),

        dcc.Tabs(id="main-tabs", value="ingest", children=[
            dcc.Tab(label="📥  Ingest", value="ingest", style=TAB_STYLE, selected_style=TAB_SELECTED),
            dcc.Tab(label="💬  Query", value="query", style=TAB_STYLE, selected_style=TAB_SELECTED),
            dcc.Tab(label="⚖️  Compare", value="compare", style=TAB_STYLE, selected_style=TAB_SELECTED),
            dcc.Tab(label="📊  Evaluate", value="evaluate", style=TAB_STYLE, selected_style=TAB_SELECTED),
        ], style={"background": C["surface"], "borderBottom": f"1px solid {C['border']}", "paddingLeft": "24px"}),

        html.Div(id="tab-content", style={"padding": "28px 32px", "background": C["bg"], "minHeight": "calc(100vh - 96px)"}),
        dcc.Interval(id="stats-interval", interval=8000, n_intervals=0),
    ], style={"fontFamily": "Inter, -apple-system, BlinkMacSystemFont, sans-serif", "background": C["bg"], "minHeight": "100vh"})

    # ── tab router ────────────────────────────────────────────────────────────
    @app.callback(Output("tab-content", "children"), Input("main-tabs", "value"))
    def render_tab(tab):
        return {"ingest": _ingest_layout, "query": _query_layout, "compare": _compare_layout, "evaluate": _eval_layout}.get(tab, _ingest_layout)()

    # ── header stats ──────────────────────────────────────────────────────────
    @app.callback(Output("header-stats", "children"), Input("stats-interval", "n_intervals"))
    def update_header(_):
        from app.store import store
        s = store.stats()
        idx_status = "✅ indexed" if s["has_faiss"] else "⚪ not indexed"
        return f"📄 {s['n_documents']} papers · ✂️ {s['n_chunks']} chunks · {idx_status}"

    # ── ingest ────────────────────────────────────────────────────────────────
    @app.callback(
        Output("ingest-status", "children"), Output("papers-table", "children"),
        Input("fetch-btn", "n_clicks"), Input("clear-btn", "n_clicks"),
        State("arxiv-query", "value"), State("n-papers", "value"), State("chunk-strategy", "value"),
        prevent_initial_call=True,
    )
    def handle_ingest(_f, _c, query, n_papers, strategy):
        from app.store import store
        from app.utils.arxiv_loader import fetch_arxiv_papers
        from app.utils.chunker import chunk_text
        from app.models.embedder import embed_texts
        from app.models.retriever import build_faiss_index, build_bm25_index

        if ctx.triggered_id == "clear-btn":
            store.clear()
            return html.Span("✅  Index cleared.", style=NOTICE_OK), html.Div()

        if not query or not query.strip():
            return html.Span("⚠️  Please enter a search query.", style=NOTICE_WARN), dash.no_update

        try:
            papers = fetch_arxiv_papers(query.strip(), max_results=n_papers or 3)
            if not papers:
                return html.Span("❌  No papers found — try a different query.", style=NOTICE_ERR), dash.no_update

            new_chunks = []
            for paper in papers:
                if any(d["id"] == paper["id"] for d in store.documents):
                    continue
                store.add_document(paper)
                full_text = f"{paper['title']}.\n\n{paper['abstract']}"
                for idx, ct in enumerate(chunk_text(full_text, strategy or "sentence_window")):
                    new_chunks.append({"id": f"{paper['id']}_chunk_{idx}", "doc_id": paper["id"], "title": paper["title"], "text": ct, "chunk_idx": idx, "source": paper["url"]})

            store.add_chunks(new_chunks)
            if store.chunk_texts:
                embs = embed_texts(store.chunk_texts)
                store.set_embeddings(embs)
                store.faiss_index = build_faiss_index(embs)
                store.bm25_index = build_bm25_index(store.chunk_texts)
            store.save()

            s = store.stats()
            status = html.Span(f"✅  Indexed {len(papers)} paper(s) → {len(new_chunks)} new chunks. Total: {s['n_documents']} docs, {s['n_chunks']} chunks.", style=NOTICE_OK)
            return status, papers_table(store.documents)
        except Exception as exc:
            return html.Span(f"❌  Error: {exc}", style=NOTICE_ERR), dash.no_update

    # ── query ─────────────────────────────────────────────────────────────────
    @app.callback(
        Output("query-output", "children"),
        Input("query-btn", "n_clicks"),
        State("query-input", "value"), State("query-method", "value"), State("query-k", "value"),
        prevent_initial_call=True,
    )
    def handle_query(_, question, method, k):
        from app.store import store
        from app.models.generator import generate_answer
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval, answer_faithfulness

        if not question or not question.strip():
            return html.Span("⚠️  Please enter a question.", style=NOTICE_WARN)
        if not store.is_indexed:
            return html.Span("⚠️  No documents indexed. Go to Ingest first.", style=NOTICE_WARN)

        results = retrieve_top_k(question, method or "hybrid", store.faiss_index, store.bm25_index, store.chunks, k=k or 5)
        context = "\n\n".join(r["chunk"]["text"] for r in results)
        answer = generate_answer(question, context)
        mt = evaluate_retrieval(question, results)
        mt["faithfulness"] = answer_faithfulness(answer, context)

        return html.Div([
            card([
                html.Div("Answer", style={**LABEL, "marginBottom": "8px"}),
                html.P(answer, style={"fontSize": "15px", "color": C["text"], "lineHeight": "1.75", "margin": 0}),
            ], extra={"borderLeft": f"3px solid {C['primary']}"}),
            html.Div([
                pill("Context Relevance", mt["context_relevance"], C["primary"]),
                pill("Faithfulness", round(mt["faithfulness"], 3), C["success"]),
                pill("Diversity", mt["diversity"], C["warning"]),
                pill("Chunks", mt["n_retrieved"], C["muted"]),
            ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "16px"}),
            card([
                html.Div(f"Retrieved chunks — method: {METHOD_LABELS.get(method, method)}", style={**LABEL, "marginBottom": "12px"}),
                html.Div([chunk_card(r) for r in results]),
            ]),
        ])

    # ── compare ───────────────────────────────────────────────────────────────
    @app.callback(
        Output("compare-output", "children"),
        Input("compare-btn", "n_clicks"),
        State("compare-input", "value"), State("compare-k", "value"),
        prevent_initial_call=True,
    )
    def handle_compare(_, question, k):
        from app.store import store
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval

        if not question or not question.strip():
            return html.Span("⚠️  Please enter a query.", style=NOTICE_WARN)
        if not store.is_indexed:
            return html.Span("⚠️  No documents indexed. Go to Ingest first.", style=NOTICE_WARN)

        all_results, all_metrics = {}, {}
        for m in ["bm25", "vector", "hybrid"]:
            r = retrieve_top_k(question, m, store.faiss_index, store.bm25_index, store.chunks, k=k or 4)
            all_results[m] = r
            all_metrics[m] = evaluate_retrieval(question, r)

        columns = []
        for m in ["bm25", "vector", "hybrid"]:
            col = html.Div([
                html.Div([
                    html.Span("●", style={"color": METHOD_COLORS[m], "fontSize": "20px", "marginRight": "8px", "lineHeight": "1"}),
                    html.Span(METHOD_LABELS[m], style={"fontWeight": "700", "fontSize": "14px", "color": C["text"]}),
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                html.Div([
                    html.Span(f"Relevance: {all_metrics[m]['context_relevance']}", style={"fontSize": "12px", "color": C["muted"], "marginRight": "12px"}),
                    html.Span(f"Diversity: {all_metrics[m]['diversity']}", style={"fontSize": "12px", "color": C["muted"]}),
                ], style={"marginBottom": "12px"}),
                html.Div([chunk_card(r, compact=True) for r in all_results[m]]),
            ], style={**CARD, "flex": "1", "margin": "0 6px", "minWidth": "0"})
            columns.append(col)

        return html.Div([
            card([dcc.Graph(figure=comparison_chart(all_metrics), config={"displayModeBar": False})]),
            html.Div(columns, style={"display": "flex", "gap": "0", "alignItems": "flex-start"}),
        ])

    # ── evaluate ──────────────────────────────────────────────────────────────
    @app.callback(
        Output("eval-output", "children"),
        Input("eval-btn", "n_clicks"),
        State("eval-queries", "value"), State("eval-k", "value"),
        prevent_initial_call=True,
    )
    def handle_eval(_, queries_text, k):
        from app.store import store
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval

        if not queries_text or not queries_text.strip():
            return html.Span("⚠️  Please enter at least one query.", style=NOTICE_WARN)
        if not store.is_indexed:
            return html.Span("⚠️  No documents indexed. Go to Ingest first.", style=NOTICE_WARN)

        questions = [q.strip() for q in queries_text.strip().split("\n") if q.strip()][:10]
        agg = {m: {"context_relevance": [], "diversity": []} for m in ["bm25", "vector", "hybrid"]}
        for q in questions:
            for m in agg:
                r = retrieve_top_k(q, m, store.faiss_index, store.bm25_index, store.chunks, k=k or 5)
                mt = evaluate_retrieval(q, r)
                agg[m]["context_relevance"].append(mt["context_relevance"])
                agg[m]["diversity"].append(mt["diversity"])

        avg_rel = {m: round(sum(v["context_relevance"]) / len(v["context_relevance"]), 4) for m, v in agg.items()}
        avg_div = {m: round(sum(v["diversity"]) / len(v["diversity"]), 4) for m, v in agg.items()}

        fig_bar = go.Figure()
        for m in ["bm25", "vector", "hybrid"]:
            fig_bar.add_trace(go.Bar(name=METHOD_LABELS[m], x=["Avg Context Relevance", "Avg Diversity"], y=[avg_rel[m], avg_div[m]], marker_color=METHOD_COLORS[m]))
        fig_bar.update_layout(barmode="group", title="Average metrics across all test queries", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, sans-serif", size=12, color=C["text"]), margin=dict(l=20, r=20, t=44, b=20), height=280, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_bar.update_yaxes(range=[0, 1], gridcolor=C["border"])
        fig_bar.update_xaxes(showgrid=False)

        q_labels = [q[:40] + "…" if len(q) > 40 else q for q in questions]
        fig_line = go.Figure()
        for m in ["bm25", "vector", "hybrid"]:
            fig_line.add_trace(go.Scatter(name=METHOD_LABELS[m], x=q_labels, y=agg[m]["context_relevance"], mode="lines+markers", line=dict(color=METHOD_COLORS[m], width=2), marker=dict(size=7)))
        fig_line.update_layout(title="Context relevance per query", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, sans-serif", size=12, color=C["text"]), margin=dict(l=20, r=20, t=44, b=80), height=290, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis=dict(tickangle=-30, showgrid=False), yaxis=dict(range=[0, 1], gridcolor=C["border"]))

        return html.Div([
            card([dcc.Graph(figure=fig_bar, config={"displayModeBar": False})]),
            card([dcc.Graph(figure=fig_line, config={"displayModeBar": False})]),
            card([
                html.Div(f"✅  Evaluated {len(questions)} quer{'y' if len(questions)==1 else 'ies'} across 3 methods.", style={**NOTICE_OK, "marginTop": 0, "marginBottom": "8px"}),
                html.P("Context Relevance = mean cosine similarity (query ↔ chunk). Diversity = 1 − mean pairwise chunk similarity. Hybrid RRF consistently ranks best on real corpora because it recovers from the blind spots of each individual method.", style={"fontSize": "13px", "color": C["muted"], "lineHeight": "1.6", "margin": 0}),
            ]),
        ])

    return app
