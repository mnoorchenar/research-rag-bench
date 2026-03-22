from __future__ import annotations
import dash
from dash import dcc, html, Input, Output, State, ctx
import plotly.graph_objects as go

# ── CSS custom properties index string — powers dark/light without Python rerenders ──
_INDEX = """<!DOCTYPE html>
<html data-theme="dark">
<head>{%metas%}<title>🔬 research-rag-bench</title>{%favicon%}{%css%}
<style>
:root,[data-theme="light"]{
  --bg:#f1f5f9;--sf:#ffffff;--sf2:#f8fafc;--bd:#e2e8f0;
  --tx:#0f172a;--mt:#64748b;--hn:#94a3b8;
  --pr:#4f46e5;--pr-rgb:79,70,229;--pr-bg:#eef2ff;--pr-bd:rgba(79,70,229,.22);
  --ok:#059669;--ok-rgb:5,150,105;
  --wn:#d97706;--wn-rgb:217,119,6;
  --er:#dc2626;--er-rgb:220,38,38;
  --c1:#f59e0b;--c2:#6366f1;--c3:#10b981;
  --sh:0 1px 3px rgba(0,0,0,.07);
}
[data-theme="dark"]{
  --bg:#0d1117;--sf:#161b22;--sf2:#0d1117;--bd:#30363d;
  --tx:#f0f6fc;--mt:#8b949e;--hn:#6e7681;
  --pr:#818cf8;--pr-rgb:129,140,248;--pr-bg:rgba(129,140,248,.12);--pr-bd:rgba(129,140,248,.28);
  --ok:#3fb950;--ok-rgb:63,185,80;
  --wn:#d29922;--wn-rgb:210,153,34;
  --er:#f85149;--er-rgb:248,81,73;
  --c1:#d29922;--c2:#818cf8;--c3:#3fb950;
  --sh:0 1px 4px rgba(0,0,0,.35);
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--tx);transition:background .3s,color .3s}
.Select-control,.Select-menu-outer{background:var(--sf)!important;border-color:var(--bd)!important;color:var(--tx)!important}
.Select-option{background:var(--sf)!important;color:var(--tx)!important}
.Select-option.is-focused,.VirtualizedSelectFocusedOption{background:var(--pr-bg)!important}
.Select-value-label{color:var(--tx)!important}
.Select-placeholder{color:var(--mt)!important}
.rc-slider-track{background:var(--pr)!important}
.rc-slider-handle{border-color:var(--pr)!important;background:var(--pr)!important}
</style>
</head>
<body>{%app_entry%}
<footer>{%config%}{%scripts%}{%renderer%}</footer>
</body></html>"""

# ── design tokens — all reference CSS vars so they auto-respond to theme ─────
CARD  = {"background":"var(--sf)","border":"1px solid var(--bd)","borderRadius":"12px","padding":"22px","marginBottom":"16px","boxShadow":"var(--sh)","transition":"background .3s,border-color .2s"}
LABEL = {"fontSize":"11px","fontWeight":"700","color":"var(--mt)","textTransform":"uppercase","letterSpacing":".06em","display":"block","marginBottom":"6px"}
INP   = {"width":"100%","padding":"9px 13px","border":"1px solid var(--bd)","borderRadius":"8px","fontSize":"14px","color":"var(--tx)","background":"var(--sf2)","outline":"none","boxSizing":"border-box","fontFamily":"inherit","transition":"border-color .2s"}
BTN   = {"display":"inline-flex","alignItems":"center","gap":"7px","padding":"9px 22px","background":"var(--pr)","color":"#fff","border":"none","borderRadius":"8px","fontSize":"14px","fontWeight":"600","cursor":"pointer","fontFamily":"inherit","transition":"opacity .2s"}
BTN_D = {**BTN,"background":"rgba(var(--er-rgb),.1)","color":"var(--er)","border":"1px solid rgba(var(--er-rgb),.3)","marginLeft":"10px"}
BTN_T = {"background":"var(--sf2)","border":"1px solid var(--bd)","borderRadius":"8px","padding":"7px 13px","cursor":"pointer","fontSize":"16px","color":"var(--tx)","fontFamily":"inherit","transition":"all .2s","lineHeight":"1","outline":"none"}
TAB_S = {"padding":"10px 22px","color":"var(--mt)","border":"none","background":"transparent","fontSize":"14px","cursor":"pointer","fontFamily":"inherit","borderBottom":"2px solid transparent"}
TAB_A = {**TAB_S,"color":"var(--pr)","borderBottom":"2px solid var(--pr)","fontWeight":"600"}
OK    = {"color":"var(--ok)","fontSize":"13px","marginTop":"8px"}
WARN  = {"color":"var(--wn)","fontSize":"13px","marginTop":"8px"}
ERR   = {"color":"var(--er)","fontSize":"13px","marginTop":"8px"}

METHOD_LABELS  = {"bm25":"BM25","vector":"Dense Vector","hybrid":"Hybrid (RRF)"}
METHOD_CSS_VAR = {"bm25":"var(--c1)","vector":"var(--c2)","hybrid":"var(--c3)"}

# chart hex colors per theme (Plotly cannot read CSS vars)
def _cc(theme: str) -> dict:
    if theme == "dark":
        return {"bm25":"#d29922","vector":"#818cf8","hybrid":"#3fb950","bg":"rgba(0,0,0,0)","paper":"rgba(0,0,0,0)","text":"#8b949e","grid":"rgba(255,255,255,.06)","font":"#f0f6fc"}
    return {"bm25":"#f59e0b","vector":"#6366f1","hybrid":"#10b981","bg":"rgba(0,0,0,0)","paper":"rgba(0,0,0,0)","text":"#64748b","grid":"rgba(0,0,0,.06)","font":"#0f172a"}

def _base_layout(c: dict, title: str = "", h: int = 260) -> dict:
    return dict(
        title=dict(text=title, font=dict(size=13, color=c["font"]), x=0.02) if title else None,
        plot_bgcolor=c["bg"], paper_bgcolor=c["paper"],
        font=dict(family="Inter,sans-serif", size=12, color=c["font"]),
        margin=dict(l=16,r=16,t=40 if title else 16,b=16), height=h,
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=11)),
        xaxis=dict(showgrid=False, color=c["text"], tickfont=dict(size=11)),
        yaxis=dict(gridcolor=c["grid"], color=c["text"], tickfont=dict(size=11)),
    )


# ── chart builders ─────────────────────────────────────────────────────────────

def _radar_chart(metrics: dict, theme: str) -> go.Figure:
    """Spider/radar chart — visually shows each method's strengths at a glance."""
    c = _cc(theme)
    cats = ["Relevance","Diversity","Avg Score"]
    fig = go.Figure()
    for m in ["bm25","vector","hybrid"]:
        mt = metrics.get(m, {})
        vals = [mt.get("context_relevance",0), mt.get("diversity",0), mt.get("avg_score",0)]
        fig.add_trace(go.Scatterpolar(
            r=vals+[vals[0]], theta=cats+[cats[0]], name=METHOD_LABELS[m],
            fill="toself", fillcolor=c[m], opacity=0.15,
            line=dict(color=c[m], width=2.5), marker=dict(size=7, color=c[m]),
        ))
    fig.update_layout(
        polar=dict(
            bgcolor=c["bg"],
            radialaxis=dict(visible=True, range=[0,1], tickfont=dict(size=10,color=c["text"]), gridcolor=c["grid"], linecolor=c["grid"]),
            angularaxis=dict(tickfont=dict(size=12,color=c["font"]), linecolor=c["grid"], gridcolor=c["grid"]),
        ),
        paper_bgcolor=c["paper"], plot_bgcolor=c["bg"],
        font=dict(family="Inter,sans-serif", size=12, color=c["font"]),
        margin=dict(l=16,r=16,t=16,b=16), height=260,
        legend=dict(orientation="h",yanchor="bottom",y=1.04,xanchor="right",x=1,font=dict(size=11)),
    )
    return fig


def _bar_chart(metrics: dict, theme: str) -> go.Figure:
    """Grouped bar chart with value annotations for side-by-side method comparison."""
    c = _cc(theme)
    fig = go.Figure()
    cats = ["Context Relevance","Diversity"]
    for m in ["bm25","vector","hybrid"]:
        mt = metrics.get(m, {})
        vals = [mt.get("context_relevance",0), mt.get("diversity",0)]
        fig.add_trace(go.Bar(
            name=METHOD_LABELS[m], x=cats, y=vals, marker_color=c[m],
            marker=dict(line=dict(width=0), cornerradius=4),
            text=[f"{v:.3f}" for v in vals], textposition="outside",
            textfont=dict(size=10,color=c["font"]), cliponaxis=False,
        ))
    layout = _base_layout(c, h=270)
    layout["yaxis"]["range"] = [0, 1.15]
    layout["barmode"] = "group"
    fig.update_layout(**layout)
    return fig


def _area_chart(questions: list, agg: dict, theme: str) -> go.Figure:
    """Smooth area line chart showing per-query context relevance across methods."""
    c = _cc(theme)
    labels = [q[:32]+"…" if len(q)>32 else q for q in questions]
    fig = go.Figure()
    for m in ["bm25","vector","hybrid"]:
        vals = agg[m]["context_relevance"]
        fig.add_trace(go.Scatter(
            name=METHOD_LABELS[m], x=labels, y=vals, mode="lines+markers",
            line=dict(color=c[m], width=2.5, shape="spline"),
            fill="tozeroy", fillcolor=c[m],
            marker=dict(size=8, color=c[m], line=dict(color="white",width=1.5)),
            opacity=0.85,
        ))
    layout = _base_layout(c, "Per-query context relevance", h=280)
    layout["xaxis"]["tickangle"] = -28
    fig.update_layout(**layout)
    return fig


# ── small UI helpers ───────────────────────────────────────────────────────────

def _pill(label: str, value, css_color: str) -> html.Div:
    try:
        pct = f"{max(0.0,min(1.0,float(value)))*100:.0f}%"
        bar = html.Div([
            html.Div(style={"height":"3px","background":"rgba(128,128,128,.15)","borderRadius":"2px","overflow":"hidden","marginTop":"8px"}),
            html.Div(style={"height":"3px","background":css_color,"width":pct,"marginTop":"-3px","borderRadius":"2px","transition":"width .5s"}),
        ])
    except Exception:
        bar = None
    ch = [
        html.Div(label, style={**LABEL,"color":css_color,"marginBottom":"2px"}),
        html.Div(str(value), style={"fontSize":"22px","fontWeight":"700","color":css_color,"lineHeight":"1.1"}),
    ]
    if bar: ch.append(bar)
    return html.Div(ch, style={"textAlign":"center","padding":"14px 12px","background":"rgba(128,128,128,.04)","border":"1px solid rgba(128,128,128,.12)","borderRadius":"12px","flex":"1","minWidth":"88px"})


def _score_badge(score: float) -> html.Span:
    c = "var(--ok)" if score>=0.035 else ("var(--wn)" if score>=0.025 else "var(--mt)")
    return html.Span(f"↑ {score:.4f}", style={"fontSize":"11px","color":c,"background":"rgba(128,128,128,.08)","borderRadius":"6px","padding":"2px 8px","fontWeight":"700","whiteSpace":"nowrap"})


def _chunk_card(r: dict, compact: bool = False) -> html.Div:
    ch = r["chunk"]
    txt = (ch["text"][:220]+"…" if len(ch["text"])>220 else ch["text"]) if compact else ch["text"]
    sc = r["score"]
    bc = "var(--ok)" if sc>=0.035 else ("var(--wn)" if sc>=0.025 else "var(--bd)")
    return html.Div([
        html.Div([
            html.Span(f"#{r['rank']}", style={"fontSize":"11px","fontWeight":"800","color":"#fff","background":"var(--pr)","borderRadius":"6px","padding":"2px 9px","marginRight":"8px","letterSpacing":".04em"}),
            html.Span(ch.get("title","")[:72], style={"fontSize":"12px","fontWeight":"600","color":"var(--mt)","flex":"1","overflow":"hidden","textOverflow":"ellipsis","whiteSpace":"nowrap"}),
            _score_badge(sc),
        ], style={"display":"flex","alignItems":"center","gap":"6px","marginBottom":"8px"}),
        html.P(txt, style={"fontSize":"13px","color":"var(--tx)","lineHeight":"1.65","margin":0}),
    ], style={"padding":"14px 16px","border":"1px solid var(--bd)","borderLeft":f"3px solid {bc}","borderRadius":"0 8px 8px 0","marginBottom":"10px","background":"var(--sf)","transition":"border-color .2s"})


def _papers_table(docs: list) -> html.Div:
    if not docs: return html.P("No papers indexed yet.", style={"color":"var(--mt)","fontSize":"14px"})
    th = {"fontSize":"11px","padding":"8px 12px","color":"var(--mt)","textTransform":"uppercase","letterSpacing":".05em","borderBottom":"1px solid var(--bd)","textAlign":"left","fontWeight":"700"}
    td = {"fontSize":"13px","padding":"9px 12px","color":"var(--tx)","borderBottom":"1px solid var(--bd)"}
    td_m = {**td,"color":"var(--mt)"}
    return html.Table([
        html.Thead(html.Tr([html.Th("Title",style=th),html.Th("Authors",style=th),html.Th("Published",style=th),html.Th("Category",style=th)])),
        html.Tbody([html.Tr([html.Td(d.get("title","")[:90],style=td),html.Td(d.get("authors","")[:40],style=td_m),html.Td(d.get("published",""),style=td_m),html.Td(d.get("categories",""),style=td_m)]) for d in docs]),
    ], style={"width":"100%","borderCollapse":"collapse"})


def _model_tip(mid: str) -> html.Div:
    from app.models.generator import DEFAULT_MODEL
    tips = {
        "google/flan-t5-base":  ("⚡","var(--wn)","Fast but weaker — switch to Large for better answers."),
        "google/flan-t5-large": ("✅","var(--ok)","Recommended — good balance of speed and quality."),
        "google/flan-t5-xl":    ("🧠","var(--pr)","Most capable — expect ~60 s per query on CPU."),
    }
    ic,col,msg = tips.get(mid or DEFAULT_MODEL, tips[DEFAULT_MODEL])
    return html.Div([html.Span(ic,style={"fontSize":"15px","marginRight":"8px"}),html.Span(msg,style={"fontSize":"13px","color":col})],
        style={"padding":"10px 14px","background":"rgba(128,128,128,.06)","border":"1px solid rgba(128,128,128,.14)","borderRadius":"8px","marginTop":"10px","display":"flex","alignItems":"center"})


# ── tab layout builders ────────────────────────────────────────────────────────

def _ingest_layout():
    return html.Div([
        html.Div([
            html.Label("arXiv search query", style=LABEL),
            dcc.Input(id="arxiv-query",type="text",placeholder="e.g. survey large language models transformer",style=INP),
            html.Div([
                html.Div([html.Label("Papers to fetch",style={**LABEL,"marginTop":"14px"}),dcc.Slider(id="n-papers",min=1,max=10,step=1,value=5,marks={i:str(i) for i in range(1,11)},tooltip={"placement":"bottom"})],style={"flex":"1"}),
                html.Div([html.Label("Chunking strategy",style={**LABEL,"marginTop":"14px"}),dcc.Dropdown(id="chunk-strategy",options=[{"label":"Sentence Window","value":"sentence_window"},{"label":"Fixed-size + overlap","value":"fixed"},{"label":"Semantic (paragraph-aware)","value":"semantic"}],value="sentence_window",clearable=False,style={"fontSize":"14px"})],style={"flex":"1","marginLeft":"28px"}),
            ],style={"display":"flex","alignItems":"flex-end","gap":"8px"}),
            html.Div([html.Button("🔍  Fetch & Index",id="fetch-btn",style={**BTN,"marginTop":"16px"}),html.Button("🗑️  Clear Index",id="clear-btn",style={**BTN_D,"marginTop":"16px"})]),
            dcc.Loading(html.Div(id="ingest-status"),type="circle",color="var(--pr)"),
        ], style=CARD),
        html.Div([
            html.Div("Indexed papers", style={**LABEL,"marginBottom":"12px"}),
            html.Div(id="papers-table"),
        ], style=CARD),
    ], style={"maxWidth":"820px","margin":"0 auto"})


def _query_layout():
    from app.models.generator import MODEL_OPTIONS, DEFAULT_MODEL
    opts = [{"label":v["label"],"value":k} for k,v in MODEL_OPTIONS.items()]
    return html.Div([
        html.Div([
            html.Label("Your question", style=LABEL),
            dcc.Input(id="query-input",type="text",placeholder="What is retrieval-augmented generation?",style={**INP,"fontSize":"15px"}),
            html.Div([
                html.Div([html.Label("Retrieval method",style={**LABEL,"marginTop":"14px"}),dcc.RadioItems(id="query-method",options=[{"label":"  BM25","value":"bm25"},{"label":"  Dense Vector","value":"vector"},{"label":"  Hybrid RRF","value":"hybrid"}],value="hybrid",inline=True,labelStyle={"marginRight":"18px","fontSize":"14px","color":"var(--tx)"})],style={"flex":"1"}),
                html.Div([html.Label("Top-k chunks",style={**LABEL,"marginTop":"14px"}),dcc.Slider(id="query-k",min=1,max=10,step=1,value=5,marks={i:str(i) for i in [1,3,5,7,10]},tooltip={"placement":"bottom"})],style={"flex":"1","marginLeft":"28px"}),
            ],style={"display":"flex"}),
            html.Div([
                html.Label("Generator model",style={**LABEL,"marginTop":"14px"}),
                dcc.Dropdown(id="query-model",options=opts,value=DEFAULT_MODEL,clearable=False,style={"fontSize":"13px"}),
                html.Div(id="model-tip-out"),
            ]),
            html.Button("💬  Get Answer",id="query-btn",style={**BTN,"marginTop":"16px"}),
        ], style=CARD),
        dcc.Loading(html.Div(id="query-output"),type="dot",color="var(--pr)"),
    ], style={"maxWidth":"820px","margin":"0 auto"})


def _compare_layout():
    return html.Div([
        html.Div([
            html.Label("Query to compare across all retrieval methods",style=LABEL),
            dcc.Input(id="compare-input",type="text",placeholder="How does attention work in transformers?",style=INP),
            html.Div([html.Label("Top-k",style={**LABEL,"marginTop":"14px"}),dcc.Slider(id="compare-k",min=1,max=8,step=1,value=4,marks={i:str(i) for i in range(1,9)},tooltip={"placement":"bottom"})]),
            html.Button("⚖️  Run Comparison",id="compare-btn",style={**BTN,"marginTop":"16px"}),
        ], style=CARD),
        dcc.Loading(html.Div(id="compare-output"),type="dot",color="var(--pr)"),
    ], style={"maxWidth":"1100px","margin":"0 auto"})


def _eval_layout():
    return html.Div([
        html.Div([
            html.Label("Test queries — one per line (max 10)",style=LABEL),
            dcc.Textarea(id="eval-queries",placeholder="What is attention?\nHow does BERT differ from GPT?\nExplain gradient descent\nWhat is contrastive learning?",style={**INP,"resize":"vertical","fontFamily":"monospace","fontSize":"13px","minHeight":"110px"}),
            html.Div([html.Label("Top-k per query",style={**LABEL,"marginTop":"14px"}),dcc.Slider(id="eval-k",min=1,max=8,step=1,value=5,marks={i:str(i) for i in range(1,9)},tooltip={"placement":"bottom"})]),
            html.Button("📊  Run Batch Evaluation",id="eval-btn",style={**BTN,"marginTop":"16px"}),
        ], style=CARD),
        dcc.Loading(html.Div(id="eval-output"),type="circle",color="var(--pr)"),
    ], style={"maxWidth":"820px","margin":"0 auto"})


# ── app factory ────────────────────────────────────────────────────────────────

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname="/",
                    suppress_callback_exceptions=True,
                    meta_tags=[{"name":"viewport","content":"width=device-width,initial-scale=1"}])
    app.index_string = _INDEX

    app.layout = html.Div([
        dcc.Store(id="theme-store", data="dark", storage_type="session"),

        html.Div([
            html.Div([
                html.Span("🔬",style={"fontSize":"20px","marginRight":"8px"}),
                html.Span("research-rag-bench",style={"fontSize":"18px","fontWeight":"700","color":"var(--tx)"}),
                html.Span("Hybrid RAG · arXiv · Evaluation",style={"fontSize":"12px","color":"var(--mt)","marginLeft":"12px"}),
            ], style={"display":"flex","alignItems":"center"}),
            html.Div([
                html.Div(id="header-stats",style={"fontSize":"12px","color":"var(--mt)","marginRight":"14px"}),
                html.Button("🌙",id="theme-toggle",style=BTN_T,title="Toggle dark / light mode"),
            ], style={"display":"flex","alignItems":"center"}),
        ], style={"display":"flex","justifyContent":"space-between","alignItems":"center","padding":"12px 28px","background":"var(--sf)","borderBottom":"1px solid var(--bd)","position":"sticky","top":"0","zIndex":"100","transition":"background .3s,border-color .2s"}),

        dcc.Tabs(id="main-tabs", value="ingest", children=[
            dcc.Tab(label="📥  Ingest",   value="ingest",   style=TAB_S, selected_style=TAB_A),
            dcc.Tab(label="💬  Query",    value="query",    style=TAB_S, selected_style=TAB_A),
            dcc.Tab(label="⚖️  Compare",  value="compare",  style=TAB_S, selected_style=TAB_A),
            dcc.Tab(label="📊  Evaluate", value="evaluate", style=TAB_S, selected_style=TAB_A),
        ], style={"background":"var(--sf)","borderBottom":"1px solid var(--bd)","paddingLeft":"20px","transition":"background .3s"}),

        html.Div(id="tab-content",style={"padding":"28px","background":"var(--bg)","minHeight":"calc(100vh - 90px)","transition":"background .3s"}),
        dcc.Interval(id="stats-interval", interval=8000, n_intervals=0),
    ], style={"fontFamily":"'Inter',-apple-system,sans-serif","background":"var(--bg)","minHeight":"100vh"})

    # clientside callback — toggles data-theme on <html>, updates button icon
    app.clientside_callback(
        """function(n, current){
            var next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            return [next, next === 'dark' ? '🌙' : '☀️'];
        }""",
        [Output("theme-store","data"), Output("theme-toggle","children")],
        Input("theme-toggle","n_clicks"),
        State("theme-store","data"),
        prevent_initial_call=True,
    )

    @app.callback(Output("tab-content","children"), Input("main-tabs","value"))
    def render_tab(tab):
        return {"ingest":_ingest_layout,"query":_query_layout,"compare":_compare_layout,"evaluate":_eval_layout}.get(tab,_ingest_layout)()

    @app.callback(Output("header-stats","children"), Input("stats-interval","n_intervals"))
    def update_header(_):
        from app.store import store
        s = store.stats()
        return f"📄 {s['n_documents']} papers · ✂️ {s['n_chunks']} chunks · {'✅ indexed' if s['has_faiss'] else '⚪ not indexed'}"

    @app.callback(Output("model-tip-out","children"), Input("query-model","value"), prevent_initial_call=False)
    def update_model_tip(mid):
        from app.models.generator import DEFAULT_MODEL
        return _model_tip(mid or DEFAULT_MODEL)

    @app.callback(
        Output("ingest-status","children"), Output("papers-table","children"),
        Input("fetch-btn","n_clicks"), Input("clear-btn","n_clicks"),
        State("arxiv-query","value"), State("n-papers","value"), State("chunk-strategy","value"),
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
            return html.Span("✅  Index cleared.", style=OK), html.Div()
        if not query or not query.strip():
            return html.Span("⚠️  Please enter a search query.", style=WARN), dash.no_update
        try:
            papers = fetch_arxiv_papers(query.strip(), max_results=n_papers or 5)
            if not papers: return html.Span("❌  No papers found.", style=ERR), dash.no_update
            new_chunks = []
            for p in papers:
                if any(d["id"]==p["id"] for d in store.documents): continue
                store.add_document(p)
                for i,ct in enumerate(chunk_text(f"{p['title']}.\n\n{p['abstract']}", strategy or "sentence_window")):
                    new_chunks.append({"id":f"{p['id']}_chunk_{i}","doc_id":p["id"],"title":p["title"],"text":ct,"chunk_idx":i,"source":p["url"]})
            store.add_chunks(new_chunks)
            if store.chunk_texts:
                embs = embed_texts(store.chunk_texts)
                store.set_embeddings(embs)
                store.faiss_index = build_faiss_index(embs)
                store.bm25_index  = build_bm25_index(store.chunk_texts)
            store.save()
            s = store.stats()
            return html.Span(f"✅  {len(papers)} paper(s) → {len(new_chunks)} new chunks. Total: {s['n_documents']} docs, {s['n_chunks']} chunks.", style=OK), _papers_table(store.documents)
        except Exception as exc:
            return html.Span(f"❌  {exc}", style=ERR), dash.no_update

    @app.callback(
        Output("query-output","children"),
        Input("query-btn","n_clicks"),
        State("query-input","value"), State("query-method","value"), State("query-k","value"), State("query-model","value"),
        prevent_initial_call=True,
    )
    def handle_query(_, question, method, k, model_id):
        from app.store import store
        from app.models.generator import generate_answer, MODEL_OPTIONS, DEFAULT_MODEL
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval, answer_faithfulness
        if not question or not question.strip(): return html.Span("⚠️  Please enter a question.", style=WARN)
        if not store.is_indexed: return html.Span("⚠️  No documents indexed. Go to Ingest first.", style=WARN)
        mid = model_id or DEFAULT_MODEL
        results = retrieve_top_k(question, method or "hybrid", store.faiss_index, store.bm25_index, store.chunks, k=k or 5)
        context = "\n\n".join(r["chunk"]["text"] for r in results)
        answer  = generate_answer(question, context, model_id=mid)
        mt = evaluate_retrieval(question, results)
        mt["faithfulness"] = answer_faithfulness(answer, context)
        mlabel = MODEL_OPTIONS.get(mid,{}).get("label", mid)
        return html.Div([
            html.Div([
                html.Div("Answer", style={**LABEL,"marginBottom":"10px"}),
                html.Div([html.Div(style={"width":"3px","flexShrink":"0","background":"var(--pr)","borderRadius":"2px","marginRight":"14px","alignSelf":"stretch"}),html.P(answer,style={"fontSize":"15px","color":"var(--tx)","lineHeight":"1.8","margin":0})],style={"display":"flex"}),
                html.Div(f"Generated by {mlabel}", style={"fontSize":"11px","color":"var(--mt)","marginTop":"10px","fontStyle":"italic","textAlign":"right"}),
            ], style=CARD),
            html.Div([
                _pill("Relevance",   mt["context_relevance"],        "var(--pr)"),
                _pill("Faithfulness",round(mt["faithfulness"],3),    "var(--ok)"),
                _pill("Diversity",   mt["diversity"],                "var(--wn)"),
                _pill("Chunks",      mt["n_retrieved"],              "var(--mt)"),
            ], style={"display":"flex","gap":"10px","flexWrap":"wrap","marginBottom":"18px"}),
            html.Div([
                html.Div([html.Span("Retrieved chunks",style={**LABEL,"marginBottom":0}),html.Span(f"method: {METHOD_LABELS.get(method,method)}",style={"fontSize":"11px","color":"var(--pr)","background":"var(--pr-bg)","borderRadius":"6px","padding":"2px 10px","fontWeight":"700"})],style={"display":"flex","justifyContent":"space-between","alignItems":"center","marginBottom":"14px"}),
                html.Div([_chunk_card(r) for r in results]),
            ], style=CARD),
        ])

    @app.callback(
        Output("compare-output","children"),
        Input("compare-btn","n_clicks"),
        State("compare-input","value"), State("compare-k","value"), State("theme-store","data"),
        prevent_initial_call=True,
    )
    def handle_compare(_, question, k, theme):
        from app.store import store
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval
        if not question or not question.strip(): return html.Span("⚠️  Please enter a query.", style=WARN)
        if not store.is_indexed: return html.Span("⚠️  No documents indexed.", style=WARN)
        all_r, all_m = {}, {}
        for m in ["bm25","vector","hybrid"]:
            r = retrieve_top_k(question, m, store.faiss_index, store.bm25_index, store.chunks, k=k or 4)
            all_r[m]=r; all_m[m]=evaluate_retrieval(question,r)
        t = theme or "dark"
        cols = [html.Div([
            html.Div([html.Span("●",style={"color":METHOD_CSS_VAR[m],"fontSize":"18px","marginRight":"7px","lineHeight":"1"}),html.Span(METHOD_LABELS[m],style={"fontWeight":"700","fontSize":"14px","color":"var(--tx)"})],style={"display":"flex","alignItems":"center","marginBottom":"8px"}),
            html.Div([html.Span(f"Relevance: {all_m[m]['context_relevance']}",style={"fontSize":"12px","color":"var(--mt)","marginRight":"12px"}),html.Span(f"Diversity: {all_m[m]['diversity']}",style={"fontSize":"12px","color":"var(--mt)"})],style={"marginBottom":"12px"}),
            html.Div([_chunk_card(r,compact=True) for r in all_r[m]]),
        ], style={**CARD,"flex":"1","margin":"0 5px","minWidth":"0"}) for m in ["bm25","vector","hybrid"]]
        return html.Div([
            html.Div([dcc.Graph(figure=_radar_chart(all_m,t),config={"displayModeBar":False})],style=CARD),
            html.Div([dcc.Graph(figure=_bar_chart(all_m,t),config={"displayModeBar":False})],style=CARD),
            html.Div(cols,style={"display":"flex","gap":"0","alignItems":"flex-start"}),
        ])

    @app.callback(
        Output("eval-output","children"),
        Input("eval-btn","n_clicks"),
        State("eval-queries","value"), State("eval-k","value"), State("theme-store","data"),
        prevent_initial_call=True,
    )
    def handle_eval(_, queries_text, k, theme):
        from app.store import store
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval
        if not queries_text or not queries_text.strip(): return html.Span("⚠️  Please enter at least one query.", style=WARN)
        if not store.is_indexed: return html.Span("⚠️  No documents indexed.", style=WARN)
        qs  = [q.strip() for q in queries_text.strip().split("\n") if q.strip()][:10]
        agg = {m:{"context_relevance":[],"diversity":[]} for m in ["bm25","vector","hybrid"]}
        for q in qs:
            for m in agg:
                r  = retrieve_top_k(q, m, store.faiss_index, store.bm25_index, store.chunks, k=k or 5)
                mt = evaluate_retrieval(q, r)
                agg[m]["context_relevance"].append(mt["context_relevance"])
                agg[m]["diversity"].append(mt["diversity"])
        avg_rel = {m:round(sum(v["context_relevance"])/len(v["context_relevance"]),4) for m,v in agg.items()}
        avg_div = {m:round(sum(v["diversity"])/len(v["diversity"]),4) for m,v in agg.items()}
        summary = {m:{"context_relevance":avg_rel[m],"diversity":avg_div[m],"avg_score":round((avg_rel[m]+avg_div[m])/2,4)} for m in ["bm25","vector","hybrid"]}
        t = theme or "dark"
        return html.Div([
            html.Div([dcc.Graph(figure=_radar_chart(summary,t),config={"displayModeBar":False})],style=CARD),
            html.Div([dcc.Graph(figure=_area_chart(qs,agg,t),config={"displayModeBar":False})],style=CARD),
            html.Div([
                html.Span(f"✅  Evaluated {len(qs)} quer{'y' if len(qs)==1 else 'ies'} across 3 methods.",style={**OK,"display":"block","marginBottom":"8px"}),
                html.P("Context Relevance = mean cosine similarity (query ↔ chunk). Diversity = 1 − mean pairwise chunk similarity. Hybrid RRF scores highest because it recovers from the blind spots of each individual method.",style={"fontSize":"13px","color":"var(--mt)","lineHeight":"1.65","margin":0}),
            ],style=CARD),
        ])

    return app
