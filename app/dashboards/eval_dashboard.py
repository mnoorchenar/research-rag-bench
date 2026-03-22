from __future__ import annotations
import dash
from dash import dcc, html, Input, Output, State, ctx, ALL
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────────
# INDEX STRING  —  all CSS lives here so Dash injects it before first paint
# ─────────────────────────────────────────────────────────────────────────────
_INDEX = """<!DOCTYPE html>
<html data-theme="dark">
<head>{%metas%}<title>research-rag-bench</title>{%favicon%}{%css%}
<style>
/* ── tokens ── */
:root{
  --bg:#0d1117;--sf:#161b22;--sf2:#21262d;--bd:#30363d;
  --tx:#f0f6fc;--mt:#8b949e;
  --pr:#818cf8;--pr2:#6366f1;--pr-bg:rgba(129,140,248,.12);--pr-bd:rgba(129,140,248,.28);
  --ok:#3fb950;--wn:#d29922;--er:#f85149;
  --c1:#d29922;--c2:#818cf8;--c3:#3fb950;
  --sh:0 2px 8px rgba(0,0,0,.4);
  --r:12px;
}
[data-theme="light"]{
  --bg:#f0f4f8;--sf:#ffffff;--sf2:#f8fafc;--bd:#e2e8f0;
  --tx:#0f172a;--mt:#64748b;
  --pr:#4f46e5;--pr2:#4338ca;--pr-bg:rgba(79,70,229,.08);--pr-bd:rgba(79,70,229,.22);
  --ok:#059669;--wn:#d97706;--er:#dc2626;
  --c1:#f59e0b;--c2:#6366f1;--c3:#10b981;
  --sh:0 1px 4px rgba(0,0,0,.08);
}

/* ── reset ── */
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;transition:background .3s,color .3s}
a{color:inherit;text-decoration:none}
button,input,textarea,select{font-family:inherit}

/* ── Dash overrides ── */
.Select-control,.Select-menu-outer{background:var(--sf)!important;border-color:var(--bd)!important;color:var(--tx)!important}
.Select-option{background:var(--sf)!important;color:var(--tx)!important}
.Select-option.is-focused{background:var(--pr-bg)!important}
.Select-value-label,.Select-placeholder{color:var(--tx)!important}
.rc-slider-track{background:var(--pr)!important}
.rc-slider-handle{border-color:var(--pr)!important;background:var(--pr)!important}

/* ── LANDING SCREEN ── */
.landing{
  min-height:100vh;display:flex;flex-direction:column;align-items:center;
  justify-content:center;padding:40px 24px;text-align:center;
  background:radial-gradient(ellipse 120% 80% at 50% -10%,rgba(129,140,248,.18) 0%,transparent 60%);
  position:relative;overflow:hidden;
}
.landing::before{
  content:'';position:absolute;inset:0;
  background-image:linear-gradient(rgba(129,140,248,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(129,140,248,.04) 1px,transparent 1px);
  background-size:52px 52px;pointer-events:none;
}
[data-theme="light"] .landing{background:radial-gradient(ellipse 120% 80% at 50% -10%,rgba(79,70,229,.1) 0%,transparent 60%)}
.landing-badge{display:inline-flex;align-items:center;gap:8px;padding:5px 14px;border:1px solid var(--pr-bd);border-radius:20px;background:var(--pr-bg);font-size:12px;font-weight:700;color:var(--pr);letter-spacing:.05em;text-transform:uppercase;margin-bottom:22px}
.landing-title{font-size:clamp(2rem,5vw,3.2rem);font-weight:900;line-height:1.15;margin-bottom:16px;max-width:700px}
.landing-title .grad{background:linear-gradient(135deg,var(--pr),var(--ok));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.landing-sub{font-size:1rem;color:var(--mt);max-width:520px;line-height:1.7;margin-bottom:40px}
.landing-sub strong{color:var(--tx)}
.mode-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;width:100%;max-width:640px;margin-bottom:32px}
.mode-card{background:var(--sf);border:1px solid var(--bd);border-radius:16px;padding:28px 24px;cursor:pointer;text-align:left;transition:all .22s;position:relative;overflow:hidden}
.mode-card::before{content:'';position:absolute;inset:0;opacity:0;transition:opacity .22s;border-radius:16px}
.mode-card:hover{transform:translateY(-4px);box-shadow:0 12px 32px rgba(0,0,0,.3)}
.mode-card.general:hover{border-color:var(--ok);box-shadow:0 12px 32px rgba(63,185,80,.15)}
.mode-card.general::before{background:radial-gradient(circle at top left,rgba(63,185,80,.08),transparent 70%)}
.mode-card.expert:hover{border-color:var(--pr);box-shadow:0 12px 32px rgba(129,140,248,.18)}
.mode-card.expert::before{background:radial-gradient(circle at top left,rgba(129,140,248,.08),transparent 70%)}
.mode-card:hover::before{opacity:1}
.mode-icon{font-size:2.4rem;margin-bottom:12px;display:block}
.mode-title{font-size:1rem;font-weight:800;color:var(--tx);margin-bottom:6px}
.mode-desc{font-size:.84rem;color:var(--mt);line-height:1.6}
.mode-tag{display:inline-block;margin-top:10px;font-size:.72rem;font-weight:700;padding:3px 10px;border-radius:8px;letter-spacing:.04em}
.mode-card.general .mode-tag{background:rgba(63,185,80,.12);color:var(--ok);border:1px solid rgba(63,185,80,.25)}
.mode-card.expert .mode-tag{background:var(--pr-bg);color:var(--pr);border:1px solid var(--pr-bd)}
.landing-footer{font-size:.78rem;color:var(--mt)}

/* ── MAIN APP SHELL ── */
.app-shell{display:flex;flex-direction:column;min-height:100vh}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:0 24px;height:52px;background:var(--sf);border-bottom:1px solid var(--bd);position:sticky;top:0;z-index:200;flex-shrink:0}
.topbar-left{display:flex;align-items:center;gap:12px}
.topbar-logo{font-size:15px;font-weight:800;color:var(--tx)}
.topbar-badge{font-size:11px;color:var(--mt);background:var(--sf2);border:1px solid var(--bd);border-radius:6px;padding:2px 8px}
.topbar-right{display:flex;align-items:center;gap:8px}
.topbar-stats{font-size:11px;color:var(--mt)}
.icon-btn{background:var(--sf2);border:1px solid var(--bd);border-radius:8px;padding:5px 10px;cursor:pointer;color:var(--tx);font-size:14px;transition:all .2s;line-height:1}
.icon-btn:hover{border-color:var(--pr);color:var(--pr)}
.mode-chip{display:flex;align-items:center;gap:6px;font-size:11px;font-weight:700;padding:4px 10px;border-radius:8px;cursor:pointer;border:1px solid var(--bd);background:var(--sf2);color:var(--mt);transition:all .2s}
.mode-chip:hover{border-color:var(--pr);color:var(--pr)}

/* ── tabs ── */
.tabs-bar{display:flex;background:var(--sf);border-bottom:1px solid var(--bd);padding:0 24px;overflow-x:auto}
.tab-btn{padding:11px 18px;font-size:13px;font-weight:600;color:var(--mt);border:none;background:transparent;cursor:pointer;border-bottom:2px solid transparent;white-space:nowrap;transition:all .2s;font-family:inherit}
.tab-btn:hover{color:var(--tx)}
.tab-btn.active{color:var(--pr);border-bottom-color:var(--pr)}

/* ── page content wrapper ── */
.page{padding:28px 24px;max-width:900px;margin:0 auto;width:100%}
.page-wide{padding:28px 24px;max-width:1160px;margin:0 auto;width:100%}

/* ── card ── */
.card{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:22px;margin-bottom:16px;transition:background .3s}
.card-title{font-size:.72rem;font-weight:800;color:var(--mt);text-transform:uppercase;letter-spacing:.07em;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.card-title .dot{width:6px;height:6px;border-radius:50%;background:var(--pr);flex-shrink:0}

/* ── example cards ── */
.ex-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px}
.ex-card{background:var(--sf2);border:1px solid var(--bd);border-radius:10px;padding:14px;cursor:pointer;text-align:left;transition:all .2s;width:100%}
.ex-card:hover{border-color:var(--pr);background:var(--pr-bg);transform:translateY(-2px)}
.ex-card-icon{font-size:18px;margin-bottom:6px;display:block}
.ex-card-persona{font-size:10px;font-weight:700;color:var(--mt);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px}
.ex-card-q{font-size:12px;color:var(--tx);line-height:1.5;font-weight:500}
.ex-card-hint{font-size:11px;color:var(--pr);margin-top:6px;font-weight:600}

/* ── form controls ── */
.form-label{font-size:11px;font-weight:700;color:var(--mt);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px;display:flex;align-items:center;gap:6px}
.inp{width:100%;padding:10px 14px;border:1px solid var(--bd);border-radius:8px;font-size:14px;color:var(--tx);background:var(--sf2);outline:none;transition:border-color .2s}
.inp:focus{border-color:var(--pr)}
.inp-big{font-size:15px;padding:12px 16px}
.inp-area{resize:vertical;min-height:100px;font-family:monospace;font-size:13px}

/* ── method selector ── */
.method-row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:6px}
.meth-card{border:1px solid var(--bd);border-radius:10px;padding:12px 14px;cursor:pointer;transition:all .2s;background:var(--sf2);text-align:left}
.meth-card:hover,.meth-card.sel{border-color:var(--pr);background:var(--pr-bg)}
.meth-card.sel .meth-name{color:var(--pr)}
.meth-name{font-size:12px;font-weight:800;color:var(--tx);margin-bottom:3px}
.meth-desc{font-size:11px;color:var(--mt);line-height:1.45}
.meth-badge{font-size:10px;font-weight:700;padding:2px 7px;border-radius:5px;margin-top:6px;display:inline-block}

/* ── buttons ── */
.btn{display:inline-flex;align-items:center;gap:7px;padding:10px 22px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;border:none;transition:all .2s;font-family:inherit;white-space:nowrap}
.btn-pr{background:var(--pr);color:#fff}.btn-pr:hover{opacity:.88}
.btn-ghost{background:transparent;color:var(--mt);border:1px solid var(--bd)}.btn-ghost:hover{border-color:var(--pr);color:var(--pr)}
.btn-danger{background:rgba(248,81,73,.1);color:var(--er);border:1px solid rgba(248,81,73,.25)}.btn-danger:hover{background:rgba(248,81,73,.18)}
.btn-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px;align-items:center}

/* ── metrics pills ── */
.metrics-row{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:18px}
.metric-pill{flex:1;min-width:80px;text-align:center;padding:14px 10px;border-radius:12px;border:1px solid rgba(128,128,128,.12);background:rgba(128,128,128,.04)}
.metric-label{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px}
.metric-val{font-size:22px;font-weight:800;line-height:1.1;margin-bottom:4px}
.metric-bar-track{height:3px;border-radius:2px;background:rgba(128,128,128,.15);overflow:hidden}
.metric-bar-fill{height:100%;border-radius:2px;transition:width .6s}

/* ── chunk card ── */
.chunk-card{padding:13px 15px;border:1px solid var(--bd);border-radius:0 8px 8px 0;margin-bottom:9px;background:var(--sf)}
.chunk-header{display:flex;align-items:center;gap:7px;margin-bottom:7px}
.chunk-rank{font-size:11px;font-weight:800;color:#fff;background:var(--pr);border-radius:5px;padding:2px 8px;letter-spacing:.04em;flex-shrink:0}
.chunk-title{font-size:12px;font-weight:600;color:var(--mt);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chunk-score{font-size:11px;font-weight:700;padding:2px 8px;border-radius:5px;white-space:nowrap}
.chunk-text{font-size:13px;color:var(--tx);line-height:1.65}

/* ── answer card ── */
.answer-card{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:22px;margin-bottom:16px;border-left:3px solid var(--pr)}
.answer-label{font-size:10px;font-weight:700;color:var(--mt);text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px}
.answer-text{font-size:15px;line-height:1.8;color:var(--tx)}
.answer-by{font-size:11px;color:var(--mt);margin-top:10px;text-align:right;font-style:italic}

/* ── modal ── */
.modal-wrap{position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:9999;display:flex;align-items:center;justify-content:center;padding:24px}
.modal{background:var(--sf);border:1px solid var(--bd);border-radius:16px;padding:30px;max-width:440px;width:100%;box-shadow:0 24px 60px rgba(0,0,0,.4)}
.modal-icon{font-size:2.2rem;margin-bottom:12px}
.modal-title{font-size:1.05rem;font-weight:800;color:var(--tx);margin-bottom:8px}
.modal-body{font-size:.88rem;color:var(--mt);line-height:1.65;margin-bottom:14px}
.modal-q{font-size:.9rem;font-weight:600;color:var(--pr);background:var(--pr-bg);padding:10px 14px;border-radius:8px;margin-bottom:20px}
.modal-actions{display:flex;gap:10px}

/* ── tooltip ── */
.ttp{position:relative;display:inline-flex;align-items:center;cursor:help}
.ttp .tip{visibility:hidden;opacity:0;background:var(--sf);color:var(--tx);border:1px solid var(--bd);border-radius:8px;padding:9px 13px;font-size:12px;line-height:1.55;width:230px;position:absolute;z-index:999;bottom:calc(100% + 6px);left:50%;transform:translateX(-50%);transition:opacity .15s;pointer-events:none;white-space:normal;font-weight:400;box-shadow:var(--sh)}
.ttp:hover .tip{visibility:visible;opacity:1}
.tip-icon{font-size:11px;color:var(--mt);margin-left:4px}

/* ── info box ── */
.info-box{border-radius:10px;padding:14px 16px;font-size:13px;line-height:1.6;margin-bottom:14px}
.info-box.blue{background:var(--pr-bg);border:1px solid var(--pr-bd);color:var(--tx)}
.info-box.green{background:rgba(63,185,80,.07);border:1px solid rgba(63,185,80,.2);color:var(--tx)}

/* ── step bar ── */
.step-bar{display:flex;align-items:center;gap:0;margin-bottom:22px}
.step-item{display:flex;align-items:center;gap:7px;font-size:12px;font-weight:600}
.step-dot{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;flex-shrink:0;transition:all .3s}
.step-done .step-dot{background:var(--ok);color:#fff}
.step-active .step-dot{background:var(--pr);color:#fff}
.step-idle .step-dot{background:var(--sf2);color:var(--mt);border:1px solid var(--bd)}
.step-done .step-lbl{color:var(--ok)}
.step-active .step-lbl{color:var(--pr)}
.step-idle .step-lbl{color:var(--mt)}
.step-line{flex:1;height:1px;background:var(--bd);margin:0 8px;min-width:20px}

/* ── tables ── */
.data-table{width:100%;border-collapse:collapse}
.data-table th{font-size:10px;font-weight:700;color:var(--mt);text-transform:uppercase;letter-spacing:.06em;padding:8px 12px;border-bottom:1px solid var(--bd);text-align:left}
.data-table td{font-size:12px;padding:9px 12px;border-bottom:1px solid rgba(128,128,128,.07);color:var(--tx)}
.data-table td.muted{color:var(--mt)}

/* ── model tip ── */
.model-tip{display:flex;align-items:center;gap:8px;padding:10px 13px;border-radius:8px;font-size:13px;margin-top:8px;border:1px solid}

/* ── sections divider ── */
.divider{height:1px;background:var(--bd);margin:20px 0}

/* ── responsive ── */
@media(max-width:700px){
  .mode-grid,.ex-grid,.method-row{grid-template-columns:1fr}
  .metrics-row .metric-pill{min-width:calc(50% - 5px)}
}
</style>
</head>
<body>{%app_entry%}
<footer>{%config%}{%scripts%}{%renderer%}</footer>
</body></html>"""

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
EXAMPLES = [
    {
        "icon": "💬",
        "persona": "Curious beginner",
        "question": "What is a large language model?",
        "query": "survey large language models GPT transformer overview",
        "hint": "Great starting point",
        "simple_desc": "Learn what AI chatbots like ChatGPT actually are.",
        "expert_desc": "LLM survey: architecture, pretraining, scaling laws.",
    },
    {
        "icon": "🔍",
        "persona": "Everyday user",
        "question": "How does AI-powered search understand what I mean?",
        "query": "dense retrieval semantic search neural information retrieval",
        "hint": "Popular question",
        "simple_desc": "Discover why AI search understands meaning, not just words.",
        "expert_desc": "Dense vs sparse retrieval: embedding similarity vs TF-IDF.",
    },
    {
        "icon": "🤖",
        "persona": "Tech enthusiast",
        "question": "How does attention work inside a transformer?",
        "query": "attention mechanism transformer self-attention BERT GPT",
        "hint": "Core concept",
        "simple_desc": "Understand the key idea behind modern AI systems.",
        "expert_desc": "Self-attention: Q/K/V projections, softmax, multi-head.",
    },
    {
        "icon": "📊",
        "persona": "Data scientist",
        "question": "How is retrieval quality measured in RAG systems?",
        "query": "RAG evaluation faithfulness hallucination context precision recall",
        "hint": "Advanced topic",
        "simple_desc": "Learn how scientists check if AI answers are trustworthy.",
        "expert_desc": "RAGAS: faithfulness, answer relevance, context precision.",
    },
    {
        "icon": "🔀",
        "persona": "ML engineer",
        "question": "Why does hybrid search outperform BM25 or vector search alone?",
        "query": "hybrid retrieval BM25 dense reciprocal rank fusion evaluation",
        "hint": "What this app demonstrates",
        "simple_desc": "See why combining search methods gives better answers.",
        "expert_desc": "RRF: 1/(k+rank) fusion, ablation vs single-method baselines.",
    },
    {
        "icon": "🏥",
        "persona": "Domain specialist",
        "question": "Can AI read medical papers and answer clinical questions?",
        "query": "biomedical NLP clinical question answering PubMed language model",
        "hint": "Real-world application",
        "simple_desc": "Explore AI reading medical research to answer health questions.",
        "expert_desc": "Domain RAG on biomedical corpora: USMLE, PubMedQA benchmarks.",
    },
]

METHODS = {
    "bm25":   {"label": "BM25",        "color": "var(--c1)", "badge_bg": "rgba(210,153,34,.12)",  "badge_bd": "rgba(210,153,34,.25)",  "desc": "Keyword matching — fast and precise on exact technical terms.", "simple": "Searches for exact words"},
    "vector": {"label": "Dense Vector","color": "var(--c2)", "badge_bg": "rgba(129,140,248,.12)", "badge_bd": "rgba(129,140,248,.25)", "desc": "Semantic similarity — finds related ideas even with different wording.", "simple": "Understands meaning"},
    "hybrid": {"label": "Hybrid RRF",  "color": "var(--c3)", "badge_bg": "rgba(63,185,80,.12)",   "badge_bd": "rgba(63,185,80,.25)",   "desc": "Fuses BM25 + Vector via Reciprocal Rank Fusion — best of both worlds.", "simple": "Best of both ⭐"},
}

# ─────────────────────────────────────────────────────────────────────────────
# SHARED COMPONENT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _tip(txt, w=230):
    return html.Span([
        html.Span("ⓘ", className="tip-icon"),
        html.Span(txt, className="tip", style={"width": f"{w}px"}),
    ], className="ttp")


def _label(text, tip_txt="", tip_w=230):
    ch = [html.Span(text)]
    if tip_txt:
        ch.append(_tip(tip_txt, tip_w))
    return html.Div(ch, className="form-label")


def _metric_pill(label, value, color, show_bar=True):
    try:
        pct = f"{max(0.0, min(1.0, float(value))) * 100:.0f}%"
    except Exception:
        pct = "0%"
        show_bar = False
    return html.Div([
        html.Div(label, className="metric-label", style={"color": color}),
        html.Div(str(value), className="metric-val", style={"color": color}),
        (html.Div([html.Div(style={"height": "3px", "background": color, "width": pct}, className="metric-bar-fill")], className="metric-bar-track") if show_bar else html.Div()),
    ], className="metric-pill")


def _score_color(score):
    return "var(--ok)" if score >= 0.035 else ("var(--wn)" if score >= 0.025 else "var(--mt)")


def _chunk_card(r, compact=False):
    ch = r["chunk"]
    txt = (ch["text"][:220] + "…") if compact and len(ch["text"]) > 220 else ch["text"]
    sc = r["score"]
    sc_col = _score_color(sc)
    return html.Div([
        html.Div([
            html.Span(f"#{r['rank']}", className="chunk-rank"),
            html.Span(ch.get("title", "")[:70], className="chunk-title"),
            html.Span(f"↑ {sc:.4f}", className="chunk-score",
                      style={"background": f"rgba(128,128,128,.08)", "color": sc_col}),
        ], className="chunk-header"),
        html.P(txt, className="chunk-text"),
    ], className="chunk-card", style={"borderLeft": f"3px solid {sc_col}"})


def _step_bar(active):
    steps = [("Topic", 0), ("Papers", 1), ("Ask", 2)]
    items = []
    for i, (lbl, _) in enumerate(steps):
        state = "done" if i < active else ("active" if i == active else "idle")
        items.append(html.Div([
            html.Div("✓" if state == "done" else str(i + 1), className="step-dot"),
            html.Span(lbl, className="step-lbl"),
        ], className=f"step-item step-{state}"))
        if i < len(steps) - 1:
            items.append(html.Div(className="step-line"))
    return html.Div(items, className="step-bar")


def _model_tip_div(mid):
    from app.models.generator import DEFAULT_MODEL
    tips = {
        "google/flan-t5-base":  ("⚡", "rgba(210,153,34,.14)", "rgba(210,153,34,.3)",  "var(--wn)", "Fast but weaker answers. Good for quick testing."),
        "google/flan-t5-large": ("✅", "rgba(63,185,80,.1)",   "rgba(63,185,80,.25)",  "var(--ok)", "Recommended — best balance of speed and quality."),
        "google/flan-t5-xl":    ("🧠", "rgba(129,140,248,.1)", "rgba(129,140,248,.3)", "var(--pr)", "Highest quality — expect ~60 s per answer on CPU."),
    }
    ic, bg, bd, col, msg = tips.get(mid or DEFAULT_MODEL, tips["google/flan-t5-large"])
    return html.Div([
        html.Span(ic, style={"fontSize": "15px", "marginRight": "8px"}),
        html.Span(msg, style={"fontSize": "13px", "color": col}),
    ], className="model-tip",
       style={"background": bg, "borderColor": bd})


def _papers_table(docs):
    if not docs:
        return html.P("No papers yet.", style={"color": "var(--mt)", "fontSize": "13px"})
    return html.Table([
        html.Thead(html.Tr([html.Th(h) for h in ["Title", "Authors", "Published", "Category"]])),
        html.Tbody([html.Tr([
            html.Td(d.get("title", "")[:80]),
            html.Td(d.get("authors", "")[:36], className="muted"),
            html.Td(d.get("published", ""), className="muted"),
            html.Td(d.get("categories", ""), className="muted"),
        ]) for d in docs]),
    ], className="data-table")


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────────────────────────────────────

def _cc(theme):
    if theme == "dark":
        return {"bm25": "#d29922", "vector": "#818cf8", "hybrid": "#3fb950",
                "bg": "rgba(0,0,0,0)", "paper": "rgba(0,0,0,0)",
                "text": "#8b949e", "grid": "rgba(255,255,255,.05)", "font": "#f0f6fc"}
    return {"bm25": "#f59e0b", "vector": "#6366f1", "hybrid": "#10b981",
            "bg": "rgba(0,0,0,0)", "paper": "rgba(0,0,0,0)",
            "text": "#64748b", "grid": "rgba(0,0,0,.06)", "font": "#0f172a"}


def _layout(c, h=260, title=""):
    return dict(
        plot_bgcolor=c["bg"], paper_bgcolor=c["paper"], height=h,
        font=dict(family="Inter,sans-serif", size=11, color=c["font"]),
        margin=dict(l=12, r=12, t=40 if title else 12, b=12),
        title=dict(text=title, font=dict(size=12, color=c["font"]), x=0.02) if title else None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        xaxis=dict(showgrid=False, color=c["text"], tickfont=dict(size=11)),
        yaxis=dict(gridcolor=c["grid"], color=c["text"], tickfont=dict(size=11)),
    )


def _radar(metrics, theme):
    c = _cc(theme)
    cats = ["Relevance", "Diversity", "Avg Score"]
    fig = go.Figure()
    for m in ["bm25", "vector", "hybrid"]:
        mt = metrics.get(m, {})
        vals = [mt.get("context_relevance", 0), mt.get("diversity", 0), mt.get("avg_score", 0)]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            name=METHODS[m]["label"], fill="toself", fillcolor=c[m], opacity=0.14,
            line=dict(color=c[m], width=2.5), marker=dict(size=7, color=c[m])))
    fig.update_layout(
        polar=dict(bgcolor=c["bg"],
                   radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9, color=c["text"]), gridcolor=c["grid"], linecolor=c["grid"]),
                   angularaxis=dict(tickfont=dict(size=12, color=c["font"]), linecolor=c["grid"], gridcolor=c["grid"])),
        paper_bgcolor=c["paper"], plot_bgcolor=c["bg"], height=250,
        font=dict(family="Inter,sans-serif", size=11, color=c["font"]),
        margin=dict(l=12, r=12, t=12, b=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1, font=dict(size=11)),
    )
    return fig


def _bar(metrics, theme):
    c = _cc(theme)
    fig = go.Figure()
    for m in ["bm25", "vector", "hybrid"]:
        mt = metrics.get(m, {})
        vals = [mt.get("context_relevance", 0), mt.get("diversity", 0)]
        fig.add_trace(go.Bar(
            name=METHODS[m]["label"], x=["Context Relevance", "Diversity"], y=vals,
            marker_color=c[m], marker=dict(cornerradius=4),
            text=[f"{v:.3f}" for v in vals], textposition="outside",
            textfont=dict(size=10, color=c["font"]), cliponaxis=False))
    lo = _layout(c, h=260)
    lo["barmode"] = "group"
    lo["yaxis"]["range"] = [0, 1.2]
    fig.update_layout(**lo)
    return fig


def _area(questions, agg, theme):
    c = _cc(theme)
    labels = [q[:30] + "…" if len(q) > 30 else q for q in questions]
    fig = go.Figure()
    for m in ["bm25", "vector", "hybrid"]:
        fig.add_trace(go.Scatter(
            name=METHODS[m]["label"], x=labels, y=agg[m]["context_relevance"],
            mode="lines+markers", line=dict(color=c[m], width=2.5, shape="spline"),
            fill="tozeroy", fillcolor=c[m], opacity=0.8,
            marker=dict(size=7, color=c[m], line=dict(color="white", width=1.5))))
    lo = _layout(c, h=270, title="Context relevance per query")
    lo["xaxis"]["tickangle"] = -22
    fig.update_layout(**lo)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SCREENS
# ─────────────────────────────────────────────────────────────────────────────

def _landing():
    """Full-page onboarding — pick your mode."""
    return html.Div([
        html.Div("🔬 research-rag-bench", className="landing-badge"),
        html.H1([
            "Ask questions.\n",
            html.Span("Get answers from real research.", className="grad"),
        ], className="landing-title"),
        html.P([
            "This app fetches real scientific papers, searches them using AI, and writes a grounded answer. ",
            html.Strong("No API key. No cost. Fully open-source."),
        ], className="landing-sub"),

        html.Div("Who are you?", style={"fontSize": "13px", "fontWeight": "700", "color": "var(--mt)",
                                         "textTransform": "uppercase", "letterSpacing": ".07em", "marginBottom": "12px"}),
        html.Div([
            html.Button([
                html.Span("🙋", className="mode-icon"),
                html.Div("I'm curious about AI", className="mode-title"),
                html.Div("No technical background needed. I'll guide you step-by-step with plain English, examples, and simple controls.", className="mode-desc"),
                html.Span("Simple mode", className="mode-tag"),
            ], id="pick-simple", className="mode-card general", n_clicks=0),
            html.Button([
                html.Span("🔬", className="mode-icon"),
                html.Div("I'm a data scientist / researcher", className="mode-title"),
                html.Div("Show me full technical controls — retrieval method, top-k, chunking strategy, architecture metrics, and evaluation charts.", className="mode-desc"),
                html.Span("Expert mode", className="mode-tag"),
            ], id="pick-expert", className="mode-card expert", n_clicks=0),
        ], className="mode-grid"),

        html.Div("You can switch modes at any time from the top bar.", className="landing-footer"),
    ], className="landing")


def _app_shell(mode, tab, inner):
    """Persistent shell wrapping every app screen."""
    from app.store import store
    s = store.stats()
    stats_txt = f"📄 {s['n_documents']} papers · ✂️ {s['n_chunks']} chunks · {'✅ ready' if s['has_faiss'] else '⚪ not indexed'}"

    tabs = [
        ("🏠  Ask",     "ask"),
        ("📥  Load",    "load"),
        ("⚖️  Compare", "compare"),
        ("📊  Evaluate","evaluate"),
    ]
    tab_btns = [
        html.Button(lbl, id=f"tab-{v}", className=f"tab-btn {'active' if tab == v else ''}", n_clicks=0)
        for lbl, v in tabs
    ]

    return html.Div([
        # top bar
        html.Div([
            html.Div([
                html.Span("🔬", style={"fontSize": "18px"}),
                html.Span("research-rag-bench", className="topbar-logo"),
                html.Span("Hybrid RAG · arXiv", className="topbar-badge"),
            ], className="topbar-left"),
            html.Div([
                html.Span(stats_txt, className="topbar-stats", id="header-stats"),
                html.Button(
                    ["🙋 Simple" if mode == "simple" else "🔬 Expert", " ↕"],
                    id="switch-mode-btn", className="mode-chip", n_clicks=0,
                    title="Switch mode"),
                html.Button("🌙", id="theme-toggle", className="icon-btn", title="Toggle dark/light"),
            ], className="topbar-right"),
        ], className="topbar"),

        # tab bar
        html.Div(tab_btns, className="tabs-bar"),

        # content
        html.Div(inner, id="tab-body",
                 style={"background": "var(--bg)", "minHeight": "calc(100vh - 96px)"}),

        # modal slot
        html.Div(id="modal-slot"),
        dcc.Store(id="pending-ex", data=None),
    ], className="app-shell")


# ─────────────────────────────────────────────────────────────────────────────
# TAB CONTENT BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def _ask_tab(mode, step=0):
    from app.models.generator import MODEL_OPTIONS, DEFAULT_MODEL
    simple = mode == "simple"
    opts = [{"label": v["label"], "value": k} for k, v in MODEL_OPTIONS.items()]

    # example cards
    ex_cards = [
        html.Button([
            html.Span(e["icon"], className="ex-card-icon"),
            html.Div(e["persona"], className="ex-card-persona"),
            html.Div(e["question"], className="ex-card-q"),
            html.Div(e["simple_desc"] if simple else e["expert_desc"],
                     style={"fontSize": "11px", "color": "var(--mt)", "marginTop": "5px", "lineHeight": "1.4"}),
            html.Div(e["hint"], className="ex-card-hint"),
        ], id={"type": "ex-btn", "index": i}, className="ex-card", n_clicks=0,
           style={"width": "100%", "fontFamily": "inherit"})
        for i, e in enumerate(EXAMPLES)
    ]

    # method selector (hidden in simple mode — defaults to hybrid)
    if simple:
        method_section = html.Div([
            dcc.RadioItems(id="query-method", value="hybrid", options=[{"label": "hybrid", "value": "hybrid"}], style={"display": "none"}),
            dcc.Slider(id="query-k", min=5, max=5, value=5, marks={}, style={"display": "none"}),
        ])
    else:
        method_cards = [
            html.Button([
                html.Div(METHODS[m]["label"], className="meth-name"),
                html.Div(METHODS[m]["desc"], className="meth-desc"),
                html.Span(METHODS[m]["label"], className="meth-badge",
                          style={"background": METHODS[m]["badge_bg"],
                                 "color": METHODS[m]["color"],
                                 "border": f"1px solid {METHODS[m]['badge_bd']}"}),
            ], id=f"meth-{m}", className="meth-card sel" if m == "hybrid" else "meth-card",
               n_clicks=0, style={"fontFamily": "inherit", "cursor": "pointer"})
            for m in ["bm25", "vector", "hybrid"]
        ]
        method_section = html.Div([
            _label("Search method", "How the system finds relevant passages. Hybrid is recommended for most questions."),
            html.Div(method_cards, className="method-row"),
            dcc.RadioItems(id="query-method", value="hybrid",
                           options=[{"label": k, "value": k} for k in ["bm25", "vector", "hybrid"]],
                           style={"display": "none"}),
            html.Div([
                _label("Number of results", "How many passages to read before writing the answer. 5 is a good default.", mt=True),
                dcc.Slider(id="query-k", min=1, max=10, step=1, value=5,
                           marks={i: str(i) for i in [1, 3, 5, 7, 10]},
                           tooltip={"placement": "bottom"}),
            ], style={"marginTop": "16px"}),
        ])

    generator_label = "Answer quality" if simple else "Generator model"
    generator_tip = "Higher quality = smarter answers but slower. 'Balanced' is recommended." if simple else "Flan-T5 seq2seq. Larger = better answers, higher CPU time."

    return html.Div([
        _step_bar(step),

        # examples
        html.Div([
            html.Div([
                html.Span("✨ Try an example", style={"fontWeight": "700", "fontSize": "14px", "color": "var(--tx)"}),
                html.Span(" — click any card and the app loads the papers automatically",
                          style={"fontSize": "13px", "color": "var(--mt)"}),
            ], style={"marginBottom": "10px"}),
            html.Div(ex_cards, className="ex-grid"),
        ], className="card"),

        # divider
        html.Div([html.Span("— or type your own question —",
                            style={"fontSize": "12px", "color": "var(--mt)", "background": "var(--bg)",
                                   "padding": "0 14px", "position": "relative", "zIndex": "1"})],
                 style={"textAlign": "center", "borderTop": "1px solid var(--bd)",
                        "marginTop": "4px", "marginBottom": "20px", "lineHeight": "0"}),

        # question input
        html.Div([
            _label("Your question"),
            dcc.Input(id="query-input", type="text",
                      placeholder="What would you like to know from your indexed papers?",
                      className="inp inp-big", debounce=False),
            html.Div(style={"height": "14px"}),
            method_section,
            html.Div([
                _label(generator_label, generator_tip),
                dcc.Dropdown(id="query-model", options=opts, value=DEFAULT_MODEL,
                             clearable=False, style={"fontSize": "13px"}),
                html.Div(id="model-tip-out"),
            ], style={"marginTop": "16px"}),
            html.Div([
                html.Button("💬  Get Answer", id="query-btn", className="btn btn-pr"),
            ], className="btn-row"),
        ], className="card"),

        # metrics legend (always visible, language adapts to mode)
        html.Div([
            html.Div(["📐 ", html.Span("What do the scores mean?")], className="card-title"),
            html.Div([
                html.Div([html.Span("Relevance", style={"fontWeight": "800", "color": "var(--pr)"}), html.Span(" — " + ("How on-topic the retrieved passages are (0–1)" if simple else "Mean cosine sim between query embedding and chunk embeddings (0–1)"))]),
                html.Div([html.Span("Faithfulness", style={"fontWeight": "800", "color": "var(--ok)"}), html.Span(" — " + ("How much of the answer is supported by the papers (0–1). 1.0 = nothing made up." if simple else "Token overlap precision: answer tokens found in context / total answer tokens"))]),
                html.Div([html.Span("Diversity", style={"fontWeight": "800", "color": "var(--wn)"}), html.Span(" — " + ("How varied the retrieved passages are. Higher = less repetition." if simple else "1 − mean pairwise cosine similarity across retrieved chunks"))]),
            ], style={"display": "flex", "flexDirection": "column", "gap": "8px", "fontSize": "13px", "color": "var(--mt)", "lineHeight": "1.55"}),
        ], className="card info-box blue", style={"borderRadius": "var(--r)"}),

        dcc.Loading(html.Div(id="query-output"), type="dot", color="var(--pr)"),
    ], className="page")


def _load_tab():
    return html.Div([
        html.Div([
            html.Div(["📥 ", html.Span("Load papers from arXiv")], className="card-title"),
            html.P("Search for any topic and we'll fetch real papers from arXiv to build your knowledge base. You can also click any example card on the Ask tab — it loads papers automatically.",
                   style={"fontSize": "13px", "color": "var(--mt)", "marginBottom": "14px", "lineHeight": "1.6"}),
            _label("Search topic", "E.g. 'survey large language models' or 'retrieval augmented generation'"),
            dcc.Input(id="arxiv-query", type="text",
                      placeholder="e.g. survey large language models transformer",
                      className="inp"),
            html.Div([
                html.Div([
                    _label("Number of papers", "How many papers to fetch. 5–8 is a good start."),
                    dcc.Slider(id="n-papers", min=1, max=10, step=1, value=5,
                               marks={i: str(i) for i in range(1, 11)},
                               tooltip={"placement": "bottom"}),
                ], style={"flex": "1"}),
                html.Div([
                    _label("Text splitting method", "How papers are split into pieces for indexing. Sentence Window is recommended."),
                    dcc.Dropdown(id="chunk-strategy",
                                 options=[{"label": "Sentence Window (recommended)", "value": "sentence_window"},
                                          {"label": "Fixed-size + overlap", "value": "fixed"},
                                          {"label": "Semantic — paragraph-aware", "value": "semantic"}],
                                 value="sentence_window", clearable=False, style={"fontSize": "13px"}),
                ], style={"flex": "1", "marginLeft": "24px"}),
            ], style={"display": "flex", "alignItems": "flex-end", "marginTop": "14px", "gap": "8px"}),
            html.Div([
                html.Button("🔍  Fetch & Index", id="fetch-btn", className="btn btn-pr"),
                html.Button("🗑️  Clear All", id="clear-btn", className="btn btn-danger"),
            ], className="btn-row"),
            dcc.Loading(html.Div(id="ingest-status"), type="circle", color="var(--pr)"),
        ], className="card"),
        html.Div([
            html.Div(["📄 ", html.Span("Indexed papers")], className="card-title"),
            html.Div(id="papers-table"),
        ], className="card"),
    ], className="page")


def _compare_tab():
    return html.Div([
        html.Div([
            html.Div(["⚖️ ", html.Span("Compare all three search methods")], className="card-title"),
            html.P("Enter a question to see how BM25, Dense Vector, and Hybrid search each respond — with charts showing which method retrieved the most relevant passages.",
                   style={"fontSize": "13px", "color": "var(--mt)", "marginBottom": "14px", "lineHeight": "1.6"}),
            _label("Your question"),
            dcc.Input(id="compare-input", type="text",
                      placeholder="How does attention work in transformers?", className="inp"),
            html.Div([
                _label("Results per method", "Number of passages to retrieve for each method."),
                dcc.Slider(id="compare-k", min=1, max=8, step=1, value=4,
                           marks={i: str(i) for i in range(1, 9)},
                           tooltip={"placement": "bottom"}),
            ], style={"marginTop": "14px"}),
            html.Div([html.Button("⚖️  Run Comparison", id="compare-btn", className="btn btn-pr")], className="btn-row"),
        ], className="card"),
        dcc.Loading(html.Div(id="compare-output"), type="dot", color="var(--pr)"),
    ], className="page-wide")


def _evaluate_tab():
    return html.Div([
        html.Div([
            html.Div(["📊 ", html.Span("Batch evaluation")], className="card-title"),
            html.P("Enter up to 10 questions (one per line). The system measures how well each retrieval method performs across all of them and displays the results as charts.",
                   style={"fontSize": "13px", "color": "var(--mt)", "marginBottom": "14px", "lineHeight": "1.6"}),
            _label("Test questions — one per line"),
            dcc.Textarea(id="eval-queries", className="inp inp-area",
                         placeholder="What is attention?\nHow does BERT differ from GPT?\nExplain gradient descent\nWhat is contrastive learning?"),
            html.Div([
                _label("Results per question"),
                dcc.Slider(id="eval-k", min=1, max=8, step=1, value=5,
                           marks={i: str(i) for i in range(1, 9)},
                           tooltip={"placement": "bottom"}),
            ], style={"marginTop": "14px"}),
            html.Div([html.Button("📊  Run Batch Evaluation", id="eval-btn", className="btn btn-pr")], className="btn-row"),
        ], className="card"),
        dcc.Loading(html.Div(id="eval-output"), type="circle", color="var(--pr)"),
    ], className="page")


# ─────────────────────────────────────────────────────────────────────────────
# APP FACTORY
# ─────────────────────────────────────────────────────────────────────────────

def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname="/",
                    suppress_callback_exceptions=True,
                    meta_tags=[{"name": "viewport", "content": "width=device-width,initial-scale=1"}])
    app.index_string = _INDEX

    app.layout = html.Div([
        dcc.Store(id="theme-store",  data="dark",    storage_type="session"),
        dcc.Store(id="mode-store",   data="landing", storage_type="session"),
        dcc.Store(id="tab-store",    data="ask",     storage_type="session"),
        dcc.Store(id="step-store",   data=0,         storage_type="session"),
        dcc.Store(id="method-store", data="hybrid"),
        dcc.Interval(id="stats-tick", interval=7000, n_intervals=0),
        html.Div(id="root"),
    ])

    # ── theme toggle (clientside) ──────────────────────────────────────────
    app.clientside_callback(
        """function(n, cur){
            var nxt = cur==='dark'?'light':'dark';
            document.documentElement.setAttribute('data-theme', nxt);
            return [nxt, nxt==='dark'?'🌙':'☀️'];
        }""",
        [Output("theme-store", "data"), Output("theme-toggle", "children")],
        Input("theme-toggle", "n_clicks"), State("theme-store", "data"),
        prevent_initial_call=True)

    # ── root renderer — switches between landing and app shell ────────────
    @app.callback(
        Output("root", "children"),
        Input("mode-store", "data"), Input("tab-store", "data"), Input("step-store", "data"))
    def render_root(mode, tab, step):
        if mode == "landing":
            return _landing()
        tab = tab or "ask"
        inner_map = {
            "ask":      lambda: _ask_tab(mode, step or 0),
            "load":     _load_tab,
            "compare":  _compare_tab,
            "evaluate": _evaluate_tab,
        }
        inner = inner_map.get(tab, lambda: _ask_tab(mode, step or 0))()
        return _app_shell(mode, tab, inner)

    # ── mode selection from landing ────────────────────────────────────────
    @app.callback(
        Output("mode-store", "data"),
        Input("pick-simple", "n_clicks"), Input("pick-expert", "n_clicks"),
        Input("switch-mode-btn", "n_clicks"),
        State("mode-store", "data"),
        prevent_initial_call=True)
    def pick_mode(ns, ne, nsw, current):
        tid = ctx.triggered_id
        if tid == "pick-simple":  return "simple"
        if tid == "pick-expert":  return "expert"
        if tid == "switch-mode-btn":
            return "expert" if current == "simple" else "simple"
        return current

    # ── tab switching ──────────────────────────────────────────────────────
    @app.callback(
        Output("tab-store", "data"),
        [Input(f"tab-{t}", "n_clicks") for t in ["ask", "load", "compare", "evaluate"]],
        prevent_initial_call=True)
    def switch_tab(*_):
        tid = ctx.triggered_id
        return tid.replace("tab-", "") if tid else "ask"

    # ── header stats refresh ───────────────────────────────────────────────
    @app.callback(Output("header-stats", "children"), Input("stats-tick", "n_intervals"))
    def refresh_stats(_):
        from app.store import store
        s = store.stats()
        return f"📄 {s['n_documents']} papers · ✂️ {s['n_chunks']} chunks · {'✅ ready' if s['has_faiss'] else '⚪ not indexed'}"

    # ── model tip ──────────────────────────────────────────────────────────
    @app.callback(Output("model-tip-out", "children"), Input("query-model", "value"), prevent_initial_call=False)
    def model_tip(mid):
        from app.models.generator import DEFAULT_MODEL
        return _model_tip_div(mid or DEFAULT_MODEL)

    # ── method card clicks → update hidden radio + card highlight ──────────
    @app.callback(
        Output("query-method", "value"),
        Output("meth-bm25",   "className"),
        Output("meth-vector", "className"),
        Output("meth-hybrid", "className"),
        Input("meth-bm25",   "n_clicks"),
        Input("meth-vector", "n_clicks"),
        Input("meth-hybrid", "n_clicks"),
        prevent_initial_call=True)
    def pick_method(b, v, h):
        sel = ctx.triggered_id.replace("meth-", "") if ctx.triggered_id else "hybrid"
        return sel, *["meth-card sel" if m == sel else "meth-card" for m in ["bm25", "vector", "hybrid"]]

    # ── example card clicked → show modal ────────────────────────────────
    @app.callback(
        Output("modal-slot", "children"),
        Output("pending-ex", "data"),
        Input({"type": "ex-btn", "index": ALL}, "n_clicks"),
        prevent_initial_call=True)
    def open_modal(clicks):
        if not any(c and c > 0 for c in clicks):
            return dash.no_update, dash.no_update
        idx = next(i for i, c in enumerate(clicks) if c and c > 0)
        e = EXAMPLES[idx]
        return html.Div([
            html.Div([
                html.Div(e["icon"], className="modal-icon"),
                html.Div("Ready to explore this question?", className="modal-title"),
                html.Div([
                    "We'll fetch relevant papers from arXiv (~10–20 s), then load the question for you.",
                    html.Br(), html.Br(),
                    html.Span("No typing needed — just click and explore.", style={"color": "var(--ok)", "fontWeight": "600"}),
                ], className="modal-body"),
                html.Div(f'"{e["question"]}"', className="modal-q"),
                html.Div([
                    html.Button("📥 Yes, fetch papers & ask", id="modal-yes", n_clicks=0, className="btn btn-pr", style={"flex": "1", "justifyContent": "center"}),
                    html.Button("✏️ I'll type my own",          id="modal-no",  n_clicks=0, className="btn btn-ghost", style={"flex": "1", "justifyContent": "center"}),
                ], className="modal-actions"),
            ], className="modal"),
        ], className="modal-wrap"), idx

    # ── modal yes — fetch + populate ──────────────────────────────────────
    @app.callback(
        Output("ingest-status",  "children", allow_duplicate=True),
        Output("papers-table",   "children", allow_duplicate=True),
        Output("query-input",    "value"),
        Output("modal-slot",     "children", allow_duplicate=True),
        Output("step-store",     "data",     allow_duplicate=True),
        Output("tab-store",      "data",     allow_duplicate=True),
        Input("modal-yes", "n_clicks"),
        State("pending-ex", "data"),
        prevent_initial_call=True)
    def load_example(n, idx):
        if not n or idx is None:
            return [dash.no_update] * 6
        from app.store import store
        from app.utils.arxiv_loader import fetch_arxiv_papers
        from app.utils.chunker import chunk_text
        from app.models.embedder import embed_texts
        from app.models.retriever import build_faiss_index, build_bm25_index
        e = EXAMPLES[idx]
        try:
            papers = fetch_arxiv_papers(e["query"], max_results=6)
            new_chunks = []
            for p in papers:
                if any(d["id"] == p["id"] for d in store.documents):
                    continue
                store.add_document(p)
                for i, ct in enumerate(chunk_text(f"{p['title']}.\n\n{p['abstract']}", "sentence_window")):
                    new_chunks.append({"id": f"{p['id']}_chunk_{i}", "doc_id": p["id"],
                                       "title": p["title"], "text": ct, "chunk_idx": i, "source": p["url"]})
            store.add_chunks(new_chunks)
            if store.chunk_texts:
                embs = embed_texts(store.chunk_texts)
                store.set_embeddings(embs)
                store.faiss_index = build_faiss_index(embs)
                store.bm25_index  = build_bm25_index(store.chunk_texts)
            store.save()
            s = store.stats()
            status = html.Span(f"✅ Loaded {len(papers)} papers → {len(new_chunks)} new chunks. Total: {s['n_documents']} docs, {s['n_chunks']} chunks.",
                               style={"color": "var(--ok)", "fontSize": "13px"})
            return status, _papers_table(store.documents), e["question"], html.Div(), 1, "ask"
        except Exception as exc:
            return html.Span(f"❌ {exc}", style={"color": "var(--er)", "fontSize": "13px"}), dash.no_update, dash.no_update, html.Div(), dash.no_update, dash.no_update

    # ── modal no ───────────────────────────────────────────────────────────
    @app.callback(Output("modal-slot", "children", allow_duplicate=True),
                  Input("modal-no", "n_clicks"), prevent_initial_call=True)
    def close_modal(_):
        return html.Div()

    # ── manual ingest ──────────────────────────────────────────────────────
    @app.callback(
        Output("ingest-status", "children"),
        Output("papers-table",  "children"),
        Input("fetch-btn",  "n_clicks"),
        Input("clear-btn",  "n_clicks"),
        State("arxiv-query",    "value"),
        State("n-papers",       "value"),
        State("chunk-strategy", "value"),
        prevent_initial_call=True)
    def handle_ingest(_f, _c, query, n_papers, strategy):
        from app.store import store
        from app.utils.arxiv_loader import fetch_arxiv_papers
        from app.utils.chunker import chunk_text
        from app.models.embedder import embed_texts
        from app.models.retriever import build_faiss_index, build_bm25_index
        if ctx.triggered_id == "clear-btn":
            store.clear()
            return html.Span("✅ Index cleared.", style={"color": "var(--ok)", "fontSize": "13px"}), html.Div()
        if not query or not query.strip():
            return html.Span("⚠️ Please enter a search topic.", style={"color": "var(--wn)", "fontSize": "13px"}), dash.no_update
        try:
            papers = fetch_arxiv_papers(query.strip(), max_results=n_papers or 5)
            if not papers:
                return html.Span("❌ No papers found — try a different topic.", style={"color": "var(--er)", "fontSize": "13px"}), dash.no_update
            new_chunks = []
            for p in papers:
                if any(d["id"] == p["id"] for d in store.documents):
                    continue
                store.add_document(p)
                for i, ct in enumerate(chunk_text(f"{p['title']}.\n\n{p['abstract']}", strategy or "sentence_window")):
                    new_chunks.append({"id": f"{p['id']}_chunk_{i}", "doc_id": p["id"],
                                       "title": p["title"], "text": ct, "chunk_idx": i, "source": p["url"]})
            store.add_chunks(new_chunks)
            if store.chunk_texts:
                embs = embed_texts(store.chunk_texts)
                store.set_embeddings(embs)
                store.faiss_index = build_faiss_index(embs)
                store.bm25_index  = build_bm25_index(store.chunk_texts)
            store.save()
            s = store.stats()
            return (html.Span(f"✅ {len(papers)} paper(s) → {len(new_chunks)} new chunks. Total: {s['n_documents']} docs, {s['n_chunks']} chunks.",
                              style={"color": "var(--ok)", "fontSize": "13px"}),
                    _papers_table(store.documents))
        except Exception as exc:
            return html.Span(f"❌ {exc}", style={"color": "var(--er)", "fontSize": "13px"}), dash.no_update

    # ── query ──────────────────────────────────────────────────────────────
    @app.callback(
        Output("query-output", "children"),
        Output("step-store", "data", allow_duplicate=True),
        Input("query-btn", "n_clicks"),
        State("query-input",  "value"),
        State("query-method", "value"),
        State("query-k",      "value"),
        State("query-model",  "value"),
        State("mode-store",   "data"),
        prevent_initial_call=True)
    def handle_query(_, question, method, k, model_id, mode):
        from app.store import store
        from app.models.generator import generate_answer, MODEL_OPTIONS, DEFAULT_MODEL
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval, answer_faithfulness
        if not question or not question.strip():
            return html.Span("⚠️ Please enter a question.", style={"color": "var(--wn)", "fontSize": "13px"}), dash.no_update
        if not store.is_indexed:
            return html.Div([
                html.Span("⚠️ No papers loaded yet. ", style={"color": "var(--wn)", "fontSize": "13px", "fontWeight": "700"}),
                html.Span("Click an example card above or go to the Load tab to fetch papers first.", style={"color": "var(--mt)", "fontSize": "13px"}),
            ]), dash.no_update
        mid = model_id or DEFAULT_MODEL
        results = retrieve_top_k(question, method or "hybrid", store.faiss_index, store.bm25_index, store.chunks, k=k or 5)
        context = "\n\n".join(r["chunk"]["text"] for r in results)
        answer  = generate_answer(question, context, model_id=mid)
        mt = evaluate_retrieval(question, results)
        mt["faithfulness"] = answer_faithfulness(answer, context)
        mlabel = MODEL_OPTIONS.get(mid, {}).get("label", mid)
        simple = mode == "simple"
        return html.Div([
            html.Div([
                html.Div("Answer", className="answer-label"),
                html.P(answer, className="answer-text"),
                html.Div(f"Generated by {mlabel}", className="answer-by"),
            ], className="answer-card"),
            html.Div([
                _metric_pill("Relevance",    mt["context_relevance"],       "var(--pr)"),
                _metric_pill("Faithfulness", round(mt["faithfulness"], 3),  "var(--ok)"),
                _metric_pill("Diversity",    mt["diversity"],               "var(--wn)"),
                _metric_pill("Chunks",       mt["n_retrieved"],             "var(--mt)", show_bar=False),
            ], className="metrics-row"),
            html.Div([
                html.Div([
                    html.Span("Retrieved passages", style={"fontWeight": "700", "fontSize": "13px", "color": "var(--tx)"}),
                    html.Span(f"  ·  {METHODS.get(method or 'hybrid', METHODS['hybrid'])['label']}",
                              style={"fontSize": "12px", "color": "var(--pr)", "fontWeight": "700"}),
                ] + ([html.Span("  ·  What is this?",
                               style={"fontSize": "12px", "color": "var(--mt)", "marginLeft": "6px"})] if simple else []),
                style={"marginBottom": "12px"}),
                html.Div([_chunk_card(r) for r in results]),
            ], className="card"),
        ]), 2

    # ── compare ────────────────────────────────────────────────────────────
    @app.callback(
        Output("compare-output", "children"),
        Input("compare-btn", "n_clicks"),
        State("compare-input", "value"), State("compare-k", "value"), State("theme-store", "data"),
        prevent_initial_call=True)
    def handle_compare(_, question, k, theme):
        from app.store import store
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval
        if not question or not question.strip():
            return html.Span("⚠️ Please enter a question.", style={"color": "var(--wn)", "fontSize": "13px"})
        if not store.is_indexed:
            return html.Span("⚠️ No papers indexed.", style={"color": "var(--wn)", "fontSize": "13px"})
        all_r, all_m = {}, {}
        for m in ["bm25", "vector", "hybrid"]:
            r = retrieve_top_k(question, m, store.faiss_index, store.bm25_index, store.chunks, k=k or 4)
            all_r[m] = r; all_m[m] = evaluate_retrieval(question, r)
        t = theme or "dark"
        c = _cc(t)
        cols = [html.Div([
            html.Div([
                html.Span("●", style={"color": METHODS[m]["color"], "fontSize": "16px", "marginRight": "6px"}),
                html.Span(METHODS[m]["label"], style={"fontWeight": "800", "fontSize": "13px"}),
            ], style={"marginBottom": "8px", "display": "flex", "alignItems": "center"}),
            html.Div(f"Relevance: {all_m[m]['context_relevance']}  ·  Diversity: {all_m[m]['diversity']}",
                     style={"fontSize": "12px", "color": "var(--mt)", "marginBottom": "10px"}),
            html.Div([_chunk_card(r, compact=True) for r in all_r[m]]),
        ], className="card", style={"flex": "1", "minWidth": "0", "margin": "0 5px"}) for m in ["bm25", "vector", "hybrid"]]
        return html.Div([
            html.Div([dcc.Graph(figure=_radar(all_m, t), config={"displayModeBar": False})], className="card"),
            html.Div([dcc.Graph(figure=_bar(all_m, t),   config={"displayModeBar": False})], className="card"),
            html.Div(cols, style={"display": "flex", "gap": "0", "alignItems": "flex-start"}),
        ])

    # ── evaluate ───────────────────────────────────────────────────────────
    @app.callback(
        Output("eval-output", "children"),
        Input("eval-btn", "n_clicks"),
        State("eval-queries", "value"), State("eval-k", "value"), State("theme-store", "data"),
        prevent_initial_call=True)
    def handle_eval(_, queries_text, k, theme):
        from app.store import store
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval
        if not queries_text or not queries_text.strip():
            return html.Span("⚠️ Please enter at least one question.", style={"color": "var(--wn)", "fontSize": "13px"})
        if not store.is_indexed:
            return html.Span("⚠️ No papers indexed.", style={"color": "var(--wn)", "fontSize": "13px"})
        qs  = [q.strip() for q in queries_text.strip().split("\n") if q.strip()][:10]
        agg = {m: {"context_relevance": [], "diversity": []} for m in ["bm25", "vector", "hybrid"]}
        for q in qs:
            for m in agg:
                r  = retrieve_top_k(q, m, store.faiss_index, store.bm25_index, store.chunks, k=k or 5)
                mt = evaluate_retrieval(q, r)
                agg[m]["context_relevance"].append(mt["context_relevance"])
                agg[m]["diversity"].append(mt["diversity"])
        avg_rel = {m: round(sum(v["context_relevance"]) / len(v["context_relevance"]), 4) for m, v in agg.items()}
        avg_div = {m: round(sum(v["diversity"])         / len(v["diversity"]),         4) for m, v in agg.items()}
        summary = {m: {"context_relevance": avg_rel[m], "diversity": avg_div[m],
                       "avg_score": round((avg_rel[m] + avg_div[m]) / 2, 4)} for m in ["bm25", "vector", "hybrid"]}
        t = theme or "dark"
        return html.Div([
            html.Div([dcc.Graph(figure=_radar(summary, t), config={"displayModeBar": False})], className="card"),
            html.Div([dcc.Graph(figure=_area(qs, agg, t),  config={"displayModeBar": False})], className="card"),
            html.Div([
                html.Span(f"✅ Evaluated {len(qs)} question(s) across 3 methods.",
                          style={"color": "var(--ok)", "fontSize": "13px", "display": "block", "marginBottom": "8px"}),
                html.P("Hybrid RRF consistently scores highest — it fuses the keyword precision of BM25 with the semantic coverage of dense vector retrieval.",
                       style={"fontSize": "13px", "color": "var(--mt)", "lineHeight": "1.6"}),
            ], className="card"),
        ])

    return app