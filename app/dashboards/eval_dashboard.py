"""
eval_dashboard.py  —  research-rag-bench
Architecture rule: every component ID is ALWAYS present in the DOM.
Show/hide is done via style callbacks only — never conditional rendering.
This prevents "Callback referencing non-existent ID" errors.
"""
from __future__ import annotations
import dash
from dash import dcc, html, Input, Output, State, ctx, ALL, clientside_callback
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
_INDEX = """<!DOCTYPE html>
<html data-theme="dark">
<head>{%metas%}<title>research-rag-bench</title>{%favicon%}{%css%}
<style>
:root{
  --bg:#0d1117;--sf:#161b22;--sf2:#21262d;--bd:#30363d;
  --tx:#f0f6fc;--mt:#8b949e;
  --pr:#818cf8;--pr-bg:rgba(129,140,248,.13);--pr-bd:rgba(129,140,248,.3);
  --ok:#3fb950;--wn:#d29922;--er:#f85149;
  --c1:#d29922;--c2:#818cf8;--c3:#3fb950;
  --sh:0 2px 12px rgba(0,0,0,.45);--r:12px;
}
[data-theme="light"]{
  --bg:#f0f4f8;--sf:#fff;--sf2:#f8fafc;--bd:#e2e8f0;
  --tx:#0f172a;--mt:#64748b;
  --pr:#4f46e5;--pr-bg:rgba(79,70,229,.08);--pr-bd:rgba(79,70,229,.22);
  --ok:#059669;--wn:#d97706;--er:#dc2626;
  --c1:#f59e0b;--c2:#6366f1;--c3:#10b981;
  --sh:0 1px 5px rgba(0,0,0,.09);
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;transition:background .3s,color .3s}
button,input,textarea,select{font-family:inherit}

/* Dash widget overrides */
.Select-control,.Select-menu-outer{background:var(--sf)!important;border-color:var(--bd)!important;color:var(--tx)!important}
.Select-option{background:var(--sf)!important;color:var(--tx)!important}
.Select-option.is-focused{background:var(--pr-bg)!important}
.Select-value-label,.Select-placeholder{color:var(--tx)!important}
.rc-slider-track{background:var(--pr)!important}
.rc-slider-handle{border-color:var(--pr)!important;background:var(--pr)!important}

/* LANDING */
.landing{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:48px 24px;text-align:center;background:radial-gradient(ellipse 130% 70% at 50% -5%,rgba(129,140,248,.2) 0%,transparent 55%);position:relative;overflow:hidden;}
.landing::after{content:'';position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(rgba(129,140,248,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(129,140,248,.04) 1px,transparent 1px);background-size:54px 54px}
[data-theme="light"] .landing{background:radial-gradient(ellipse 130% 70% at 50% -5%,rgba(79,70,229,.1) 0%,transparent 55%)}
.l-badge{display:inline-flex;align-items:center;gap:8px;padding:5px 16px;border:1px solid var(--pr-bd);border-radius:20px;background:var(--pr-bg);font-size:11px;font-weight:700;color:var(--pr);letter-spacing:.06em;text-transform:uppercase;margin-bottom:24px;position:relative;z-index:1}
.l-title{font-size:clamp(2rem,5vw,3.4rem);font-weight:900;line-height:1.15;margin-bottom:14px;max-width:680px;position:relative;z-index:1}
.l-title .g{background:linear-gradient(135deg,var(--pr),var(--ok));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.l-sub{font-size:.98rem;color:var(--mt);max-width:500px;line-height:1.72;margin-bottom:44px;position:relative;z-index:1}
.l-sub strong{color:var(--tx)}
.l-cards{display:grid;grid-template-columns:1fr 1fr;gap:14px;width:100%;max-width:600px;margin-bottom:28px;position:relative;z-index:1}
.l-card{background:var(--sf);border:1.5px solid var(--bd);border-radius:16px;padding:26px 22px;cursor:pointer;text-align:left;transition:all .22s;position:relative;overflow:hidden}
.l-card:hover{transform:translateY(-5px);box-shadow:var(--sh)}
.l-card.gen:hover{border-color:var(--ok);box-shadow:0 14px 40px rgba(63,185,80,.14)}
.l-card.exp:hover{border-color:var(--pr);box-shadow:0 14px 40px rgba(129,140,248,.18)}
.l-card-glow{position:absolute;inset:0;border-radius:14px;opacity:0;transition:opacity .22s}
.l-card.gen .l-card-glow{background:radial-gradient(circle at 0 0,rgba(63,185,80,.1),transparent 65%)}
.l-card.exp .l-card-glow{background:radial-gradient(circle at 0 0,rgba(129,140,248,.1),transparent 65%)}
.l-card:hover .l-card-glow{opacity:1}
.l-icon{font-size:2.2rem;margin-bottom:10px;display:block;position:relative;z-index:1}
.l-name{font-size:.98rem;font-weight:800;color:var(--tx);margin-bottom:5px;position:relative;z-index:1}
.l-desc{font-size:.82rem;color:var(--mt);line-height:1.6;position:relative;z-index:1}
.l-tag{display:inline-block;margin-top:9px;font-size:.7rem;font-weight:700;padding:3px 10px;border-radius:7px;position:relative;z-index:1}
.l-card.gen .l-tag{background:rgba(63,185,80,.12);color:var(--ok);border:1px solid rgba(63,185,80,.25)}
.l-card.exp .l-tag{background:var(--pr-bg);color:var(--pr);border:1px solid var(--pr-bd)}
.l-note{font-size:.78rem;color:var(--mt);position:relative;z-index:1}

/* TOPBAR */
.topbar{height:50px;display:flex;align-items:center;justify-content:space-between;padding:0 22px;background:var(--sf);border-bottom:1px solid var(--bd);position:sticky;top:0;z-index:200;transition:background .3s}
.tb-logo{font-size:14px;font-weight:800;color:var(--tx);display:flex;align-items:center;gap:8px}
.tb-badge{font-size:10px;color:var(--mt);background:var(--sf2);border:1px solid var(--bd);border-radius:5px;padding:2px 7px}
.tb-right{display:flex;align-items:center;gap:8px}
.tb-stats{font-size:11px;color:var(--mt)}
.ib{background:var(--sf2);border:1px solid var(--bd);border-radius:7px;padding:5px 10px;cursor:pointer;color:var(--tx);font-size:13px;transition:all .2s;line-height:1;white-space:nowrap}
.ib:hover{border-color:var(--pr);color:var(--pr)}

/* TABS */
.tabs{display:flex;background:var(--sf);border-bottom:1px solid var(--bd);padding:0 22px;overflow-x:auto}
.tb{padding:10px 16px;font-size:13px;font-weight:600;color:var(--mt);border:none;background:transparent;cursor:pointer;border-bottom:2px solid transparent;white-space:nowrap;transition:all .2s;font-family:inherit}
.tb:hover{color:var(--tx)}
.tb.on{color:var(--pr);border-bottom-color:var(--pr)}

/* SEARCH FLOW */
.search-hero{display:flex;flex-direction:column;align-items:center;text-align:center;padding:48px 24px 32px;transition:padding .4s;}
.search-hero.compact{padding:16px 24px 0}
.sh-logo{font-size:1.2rem;font-weight:900;color:var(--tx);margin-bottom:22px;display:flex;align-items:center;gap:8px;transition:all .4s}
.search-hero.compact .sh-logo{display:none}
.search-box-wrap{width:100%;max-width:640px;position:relative;margin-bottom:6px}
.search-box{width:100%;padding:14px 52px 14px 20px;font-size:16px;border:1.5px solid var(--bd);border-radius:26px;background:var(--sf);color:var(--tx);outline:none;transition:border-color .2s,box-shadow .2s;box-shadow:var(--sh);}
.search-box:focus{border-color:var(--pr);box-shadow:0 0 0 3px var(--pr-bg)}
.search-enter-btn{position:absolute;right:8px;top:50%;transform:translateY(-50%);background:var(--pr);border:none;border-radius:18px;padding:7px 16px;color:#fff;font-size:12px;font-weight:700;cursor:pointer;transition:opacity .2s;font-family:inherit}
.search-enter-btn:hover{opacity:.85}
.search-hint{font-size:12px;color:var(--mt);margin-bottom:18px}

/* EXAMPLE CARDS */
.ex-wrap{width:100%;max-width:760px;margin-bottom:12px}
.ex-label{font-size:11px;color:var(--mt);font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:10px;text-align:left}
.ex-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.ex-card{background:var(--sf2);border:1px solid var(--bd);border-radius:10px;padding:12px 13px;cursor:pointer;text-align:left;transition:all .2s;width:100%}
.ex-card:hover{border-color:var(--pr);background:var(--pr-bg);transform:translateY(-2px)}
.ex-icon{font-size:16px;margin-bottom:4px;display:block}
.ex-persona{font-size:10px;font-weight:700;color:var(--mt);text-transform:uppercase;letter-spacing:.05em;margin-bottom:3px}
.ex-q{font-size:12px;color:var(--tx);line-height:1.45;font-weight:500}
.ex-tag{font-size:10px;color:var(--pr);font-weight:700;margin-top:5px;display:block}

/* STEP INDICATOR */
.steps{display:flex;align-items:center;width:100%;max-width:420px;margin:0 auto 24px}
.st{display:flex;align-items:center;gap:6px;font-size:12px;font-weight:600}
.st-dot{width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;flex-shrink:0;transition:all .3s}
.done .st-dot{background:var(--ok);color:#fff}
.active .st-dot{background:var(--pr);color:#fff}
.idle .st-dot{background:var(--sf2);color:var(--mt);border:1px solid var(--bd)}
.done .st-lbl{color:var(--ok)}
.active .st-lbl{color:var(--pr)}
.idle .st-lbl{color:var(--mt)}
.st-line{flex:1;height:1px;background:var(--bd);margin:0 7px;min-width:16px}

/* EXPERT CONTROLS */
.expert-panel{width:100%;max-width:760px;display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.ctrl-card{background:var(--sf);border:1px solid var(--bd);border-radius:10px;padding:14px}
.ctrl-lbl{font-size:10px;font-weight:700;color:var(--mt);text-transform:uppercase;letter-spacing:.07em;margin-bottom:8px;display:flex;align-items:center;gap:5px}
.meth-row{display:flex;gap:6px}
.mc{flex:1;border:1px solid var(--bd);border-radius:8px;padding:9px 10px;cursor:pointer;transition:all .2s;background:var(--sf2);text-align:left}
.mc:hover,.mc.on{border-color:var(--pr);background:var(--pr-bg)}
.mc.on .mc-name{color:var(--pr)}
.mc-name{font-size:11px;font-weight:800;color:var(--tx);margin-bottom:2px}
.mc-desc{font-size:10px;color:var(--mt);line-height:1.4}

/* ANSWER AREA */
.answer-wrap{width:100%;max-width:760px}
.a-card{background:var(--sf);border:1px solid var(--bd);border-left:3px solid var(--pr);border-radius:0 var(--r) var(--r) 0;padding:20px;margin-bottom:14px}
.a-lbl{font-size:10px;font-weight:700;color:var(--mt);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}
.a-text{font-size:15px;line-height:1.8;color:var(--tx)}
.a-by{font-size:11px;color:var(--mt);margin-top:8px;text-align:right;font-style:italic}
.metrics-row{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.mp{flex:1;min-width:76px;text-align:center;padding:12px 8px;border-radius:10px;border:1px solid rgba(128,128,128,.12);background:rgba(128,128,128,.04)}
.mp-lbl{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:3px}
.mp-val{font-size:20px;font-weight:800;line-height:1}
.mp-bar{height:3px;border-radius:2px;background:rgba(128,128,128,.15);overflow:hidden;margin-top:6px}
.mp-fill{height:100%;border-radius:2px;transition:width .5s}
.chunks-card{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:18px}
.chunks-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.chunk-item{padding:12px 14px;border:1px solid var(--bd);border-radius:0 8px 8px 0;margin-bottom:8px;background:var(--sf)}
.ci-hdr{display:flex;align-items:center;gap:6px;margin-bottom:6px}
.ci-rank{font-size:10px;font-weight:800;color:#fff;background:var(--pr);border-radius:5px;padding:2px 7px;flex-shrink:0}
.ci-title{font-size:11px;font-weight:600;color:var(--mt);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ci-score{font-size:10px;font-weight:700;padding:2px 7px;border-radius:5px;white-space:nowrap;background:rgba(128,128,128,.08)}
.ci-text{font-size:12px;color:var(--tx);line-height:1.6}

/* GENERIC */
.card{background:var(--sf);border:1px solid var(--bd);border-radius:var(--r);padding:20px;margin-bottom:14px;transition:background .3s}
.card-h{font-size:11px;font-weight:700;color:var(--mt);text-transform:uppercase;letter-spacing:.07em;margin-bottom:12px}
.inp{width:100%;padding:9px 13px;border:1px solid var(--bd);border-radius:8px;font-size:14px;color:var(--tx);background:var(--sf2);outline:none;transition:border-color .2s}
.inp:focus{border-color:var(--pr)}
.inp-area{resize:vertical;min-height:96px;font-family:monospace;font-size:13px}
.fl{font-size:11px;font-weight:700;color:var(--mt);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px;display:block}
.btn{display:inline-flex;align-items:center;gap:6px;padding:9px 20px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;border:none;transition:all .2s;font-family:inherit;white-space:nowrap}
.btn-p{background:var(--pr);color:#fff}.btn-p:hover{opacity:.87}
.btn-d{background:rgba(248,81,73,.1);color:var(--er);border:1px solid rgba(248,81,73,.25)}.btn-d:hover{background:rgba(248,81,73,.18)}
.btn-g{background:transparent;color:var(--mt);border:1px solid var(--bd)}.btn-g:hover{border-color:var(--pr);color:var(--pr)}
.btn-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;align-items:center}
.ok{color:var(--ok);font-size:13px}.wn{color:var(--wn);font-size:13px}.er{color:var(--er);font-size:13px}
.dt{width:100%;border-collapse:collapse}
.dt th{font-size:10px;font-weight:700;color:var(--mt);text-transform:uppercase;letter-spacing:.06em;padding:7px 10px;border-bottom:1px solid var(--bd);text-align:left}
.dt td{font-size:12px;padding:8px 10px;border-bottom:1px solid rgba(128,128,128,.07);color:var(--tx)}
.dt .m{color:var(--mt)}

/* TOOLTIP */
.tip-i{font-size:11px;color:var(--mt);margin-left:4px;cursor:help;position:relative;display:inline-flex;align-items:center}
.tip-i::before{content:'ⓘ'}
.tip-box{display:none;position:absolute;bottom:calc(100% + 5px);left:50%;transform:translateX(-50%);background:var(--sf);border:1px solid var(--bd);border-radius:8px;padding:8px 12px;font-size:11px;line-height:1.55;width:210px;white-space:normal;font-weight:400;z-index:999;box-shadow:var(--sh);color:var(--tx)}
.tip-i:hover .tip-box{display:block}

/* MODAL */
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:9999;display:flex;align-items:center;justify-content:center;padding:24px}
.modal{background:var(--sf);border:1px solid var(--bd);border-radius:16px;padding:28px;max-width:420px;width:100%;box-shadow:0 24px 60px rgba(0,0,0,.4)}
.m-icon{font-size:2rem;margin-bottom:10px}
.m-title{font-size:1rem;font-weight:800;color:var(--tx);margin-bottom:8px}
.m-body{font-size:.87rem;color:var(--mt);line-height:1.65;margin-bottom:12px}
.m-q{font-size:.88rem;font-weight:600;color:var(--pr);background:var(--pr-bg);padding:9px 13px;border-radius:8px;margin-bottom:18px}
.m-btns{display:flex;gap:8px}

@media(max-width:640px){
  .l-cards,.ex-grid,.expert-panel{grid-template-columns:1fr}
  .meth-row{flex-direction:column}
}
</style>
</head>
<body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer>
</body></html>"""

# ─────────────────────────────────────────────────────────────────────────────
# STATIC DATA
# ─────────────────────────────────────────────────────────────────────────────
EXAMPLES = [
    {"icon":"💬","persona":"Curious beginner",   "q":"What is a large language model?",                          "arxiv":"survey large language models GPT transformer overview",          "tag":"Great start"},
    {"icon":"🔍","persona":"Everyday user",       "q":"How does AI understand what I mean when I search?",        "arxiv":"dense retrieval semantic search neural information retrieval",    "tag":"Popular"},
    {"icon":"🤖","persona":"Tech enthusiast",     "q":"How does the attention mechanism work?",                   "arxiv":"attention mechanism transformer self-attention BERT",             "tag":"Core concept"},
    {"icon":"📊","persona":"Data scientist",      "q":"How is retrieval quality measured in RAG systems?",        "arxiv":"RAG evaluation faithfulness hallucination context grounding",      "tag":"Advanced"},
    {"icon":"🔀","persona":"ML engineer",         "q":"Why does hybrid search beat BM25 or vector search alone?", "arxiv":"hybrid retrieval BM25 dense reciprocal rank fusion evaluation",   "tag":"What this app shows"},
    {"icon":"🏥","persona":"Domain specialist",   "q":"Can AI answer medical questions from research papers?",    "arxiv":"biomedical NLP clinical question answering PubMed language model", "tag":"Real-world use"},
]

METHODS = {
    "bm25":   {"label":"BM25",         "color":"var(--c1)", "expert":"Probabilistic sparse retrieval (TF-IDF based)"},
    "vector": {"label":"Dense Vector", "color":"var(--c2)", "expert":"Embedding cosine similarity via FAISS IndexFlatIP"},
    "hybrid": {"label":"Hybrid RRF ★", "color":"var(--c3)", "expert":"Reciprocal Rank Fusion k=60 over BM25 + dense lists"},
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _sc(s):
    return "var(--ok)" if s>=0.035 else ("var(--wn)" if s>=0.025 else "var(--mt)")

def _metric(label, value, color):
    try:
        pct = f"{max(0.0,min(1.0,float(value)))*100:.0f}%"
        bar = html.Div(html.Div(style={"height":"100%","borderRadius":"2px","background":color,"width":pct,"transition":"width .5s"}),className="mp-bar")
    except Exception:
        bar = html.Div()
    return html.Div([
        html.Div(label, className="mp-lbl", style={"color":color}),
        html.Div(str(value), className="mp-val", style={"color":color}),
        bar,
    ], className="mp")

def _chunk(r, compact=False):
    ch = r["chunk"]
    txt = (ch["text"][:200]+"…") if compact and len(ch["text"])>200 else ch["text"]
    sc = r["score"]; col = _sc(sc)
    return html.Div([
        html.Div([
            html.Span(f"#{r['rank']}", className="ci-rank"),
            html.Span(ch.get("title","")[:70], className="ci-title"),
            html.Span(f"↑ {sc:.4f}", className="ci-score", style={"color":col}),
        ], className="ci-hdr"),
        html.P(txt, className="ci-text"),
    ], className="chunk-item", style={"borderLeft":f"3px solid {col}"})

def _steps_bar(active):
    labels = [("Question",0),("Papers",1),("Answer",2)]
    items = []
    for i,(lbl,_) in enumerate(labels):
        s = "done" if i<active else ("active" if i==active else "idle")
        items.append(html.Div([
            html.Div("✓" if s=="done" else str(i+1), className="st-dot"),
            html.Span(lbl, className="st-lbl"),
        ], className=f"st {s}"))
        if i < len(labels)-1:
            items.append(html.Div(className="st-line"))
    return html.Div(items, className="steps")

def _papers_table(docs):
    if not docs: return html.P("No papers yet.", style={"color":"var(--mt)","fontSize":"13px"})
    return html.Table([
        html.Thead(html.Tr([html.Th(h) for h in ["Title","Authors","Published","Category"]])),
        html.Tbody([html.Tr([
            html.Td(d.get("title","")[:80]), html.Td(d.get("authors","")[:34],className="m"),
            html.Td(d.get("published",""),className="m"), html.Td(d.get("categories",""),className="m"),
        ]) for d in docs]),
    ], className="dt")

def _model_tip_el(mid):
    from app.models.generator import DEFAULT_MODEL
    tips = {
        "google/flan-t5-base":  ("⚡","rgba(210,153,34,.12)","rgba(210,153,34,.28)","var(--wn)","Fast but weaker. Good for testing."),
        "google/flan-t5-large": ("✅","rgba(63,185,80,.1)","rgba(63,185,80,.25)","var(--ok)","Recommended — best balance of speed and quality."),
        "google/flan-t5-xl":    ("🧠","rgba(129,140,248,.1)","rgba(129,140,248,.28)","var(--pr)","Highest quality — expect ~60 s per answer on free CPU."),
    }
    ic,bg,bd,col,msg = tips.get(mid or DEFAULT_MODEL, tips["google/flan-t5-large"])
    return html.Div([
        html.Span(ic, style={"fontSize":"14px","marginRight":"7px"}),
        html.Span(msg, style={"fontSize":"12px","color":col}),
    ], style={"padding":"9px 13px","borderRadius":"8px","border":f"1px solid {bd}","background":bg,"display":"flex","alignItems":"center","marginTop":"8px"})

def _tip_span(tooltip_text):
    """Tooltip icon — children passed first, then className. No SyntaxError."""
    return html.Span([html.Div(tooltip_text, className="tip-box")], className="tip-i")

# ─────────────────────────────────────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────────────────────────────────────
def _cc(t):
    if t=="dark": return {"bm25":"#d29922","vector":"#818cf8","hybrid":"#3fb950","bg":"rgba(0,0,0,0)","paper":"rgba(0,0,0,0)","txt":"#8b949e","grid":"rgba(255,255,255,.05)","font":"#f0f6fc"}
    return {"bm25":"#f59e0b","vector":"#6366f1","hybrid":"#10b981","bg":"rgba(0,0,0,0)","paper":"rgba(0,0,0,0)","txt":"#64748b","grid":"rgba(0,0,0,.06)","font":"#0f172a"}

def _base(c,h=260,title=""):
    return dict(plot_bgcolor=c["bg"],paper_bgcolor=c["paper"],height=h,
        font=dict(family="Inter,sans-serif",size=11,color=c["font"]),
        margin=dict(l=12,r=12,t=38 if title else 12,b=12),
        title=dict(text=title,font=dict(size=12,color=c["font"]),x=0.02) if title else None,
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=11)),
        xaxis=dict(showgrid=False,color=c["txt"],tickfont=dict(size=11)),
        yaxis=dict(gridcolor=c["grid"],color=c["txt"],tickfont=dict(size=11)))

def _radar(m,t):
    c=_cc(t); cats=["Relevance","Diversity","Avg"]
    fig=go.Figure()
    for k in ["bm25","vector","hybrid"]:
        v=[m.get(k,{}).get("context_relevance",0),m.get(k,{}).get("diversity",0),m.get(k,{}).get("avg_score",0)]
        fig.add_trace(go.Scatterpolar(r=v+[v[0]],theta=cats+[cats[0]],name=METHODS[k]["label"],
            fill="toself",fillcolor=c[k],opacity=0.14,line=dict(color=c[k],width=2.5),marker=dict(size=7,color=c[k])))
    fig.update_layout(polar=dict(bgcolor=c["bg"],
        radialaxis=dict(visible=True,range=[0,1],tickfont=dict(size=9,color=c["txt"]),gridcolor=c["grid"],linecolor=c["grid"]),
        angularaxis=dict(tickfont=dict(size=12,color=c["font"]),linecolor=c["grid"],gridcolor=c["grid"])),
        paper_bgcolor=c["paper"],height=240,font=dict(family="Inter,sans-serif",size=11,color=c["font"]),
        margin=dict(l=12,r=12,t=12,b=12),
        legend=dict(orientation="h",yanchor="bottom",y=1.04,xanchor="right",x=1,font=dict(size=11)))
    return fig

def _bar(m,t):
    c=_cc(t); fig=go.Figure()
    for k in ["bm25","vector","hybrid"]:
        vals=[m.get(k,{}).get("context_relevance",0),m.get(k,{}).get("diversity",0)]
        fig.add_trace(go.Bar(name=METHODS[k]["label"],x=["Relevance","Diversity"],y=vals,
            marker_color=c[k],marker=dict(cornerradius=4),
            text=[f"{v:.3f}" for v in vals],textposition="outside",
            textfont=dict(size=10,color=c["font"]),cliponaxis=False))
    lo=_base(c,h=250); lo["barmode"]="group"; lo["yaxis"]["range"]=[0,1.2]
    fig.update_layout(**lo); return fig

def _area(qs,agg,t):
    c=_cc(t); labels=[q[:28]+"…" if len(q)>28 else q for q in qs]; fig=go.Figure()
    for k in ["bm25","vector","hybrid"]:
        fig.add_trace(go.Scatter(name=METHODS[k]["label"],x=labels,y=agg[k]["context_relevance"],
            mode="lines+markers",line=dict(color=c[k],width=2.5,shape="spline"),
            fill="tozeroy",fillcolor=c[k],opacity=0.8,
            marker=dict(size=7,color=c[k],line=dict(color="white",width=1.5))))
    lo=_base(c,h=260,title="Context relevance per query"); lo["xaxis"]["tickangle"]=-20
    fig.update_layout(**lo); return fig

# ─────────────────────────────────────────────────────────────────────────────
# FULL LAYOUT  —  all IDs always present in DOM
# ─────────────────────────────────────────────────────────────────────────────
def _full_layout():
    from app.models.generator import MODEL_OPTIONS, DEFAULT_MODEL
    gen_opts = [{"label":v["label"],"value":k} for k,v in MODEL_OPTIONS.items()]

    ex_btns = [
        html.Button([
            html.Span(e["icon"], className="ex-icon"),
            html.Div(e["persona"], className="ex-persona"),
            html.Div(e["q"], className="ex-q"),
            html.Span(e["tag"], className="ex-tag"),
        ], id={"type":"exbtn","index":i}, className="ex-card", n_clicks=0,
           style={"width":"100%","fontFamily":"inherit"})
        for i,e in enumerate(EXAMPLES)
    ]

    method_cards = [
        html.Button([
            html.Div(METHODS[m]["label"], className="mc-name"),
            html.Div(METHODS[m]["expert"], className="mc-desc"),
        ], id=f"mc-{m}", className="mc on" if m=="hybrid" else "mc",
           n_clicks=0, style={"fontFamily":"inherit"})
        for m in ["bm25","vector","hybrid"]
    ]

    return html.Div([
        # stores
        dcc.Store(id="s-theme",  data="dark",    storage_type="session"),
        dcc.Store(id="s-mode",   data="landing", storage_type="session"),
        dcc.Store(id="s-tab",    data="ask",     storage_type="session"),
        dcc.Store(id="s-step",   data=0,         storage_type="session"),
        dcc.Store(id="s-method", data="hybrid"),
        dcc.Store(id="s-pex",    data=None),
        dcc.Interval(id="iv-stats", interval=7000, n_intervals=0),

        # ── LANDING ──────────────────────────────────────────────────────────
        html.Div([
            html.Div("🔬 research-rag-bench", className="l-badge"),
            html.H1(["Ask questions. ", html.Span("Get answers from real research.", className="g")], className="l-title"),
            html.P(["Fetches real scientific papers, searches them with AI, and writes a grounded answer. ", html.Strong("No API key. No cost. Open-source.")], className="l-sub"),
            html.Div("How would you describe yourself?", style={"fontSize":"13px","fontWeight":"700","color":"var(--mt)","textTransform":"uppercase","letterSpacing":".07em","marginBottom":"12px","position":"relative","zIndex":"1"}),
            html.Div([
                html.Button([
                    html.Div(className="l-card-glow"),
                    html.Span("🙋", className="l-icon"),
                    html.Div("I'm new to AI / just curious", className="l-name"),
                    html.Div("No technical knowledge needed — guided with plain English, ready-made examples, and simple controls.", className="l-desc"),
                    html.Span("Simple mode", className="l-tag"),
                ], id="pick-s", className="l-card gen", n_clicks=0),
                html.Button([
                    html.Div(className="l-card-glow"),
                    html.Span("🔬", className="l-icon"),
                    html.Div("Data scientist / ML researcher", className="l-name"),
                    html.Div("Full technical controls — retrieval methods, chunking strategy, top-k, evaluation metrics, and architecture charts.", className="l-desc"),
                    html.Span("Expert mode", className="l-tag"),
                ], id="pick-e", className="l-card exp", n_clicks=0),
            ], className="l-cards"),
            html.Div("You can switch modes at any time from the top bar.", className="l-note"),
        ], id="screen-landing"),

        # ── APP SHELL ─────────────────────────────────────────────────────────
        html.Div([
            # topbar
            html.Div([
                html.Div([html.Span("🔬",style={"fontSize":"17px"}), html.Span("research-rag-bench",className="tb-logo"), html.Span("Hybrid RAG · arXiv",className="tb-badge")], style={"display":"flex","alignItems":"center","gap":"8px"}),
                html.Div([html.Span("",id="stats-txt",className="tb-stats"), html.Button("↕ Mode",id="sw-mode",className="ib"), html.Button("🌙",id="btn-theme",className="ib")], className="tb-right"),
            ], className="topbar"),
            # tabs
            html.Div([
                html.Button("🏠  Ask",      id="tab-ask",      className="tb on", n_clicks=0),
                html.Button("📥  Load",     id="tab-load",     className="tb",    n_clicks=0),
                html.Button("⚖️  Compare",  id="tab-compare",  className="tb",    n_clicks=0),
                html.Button("📊  Evaluate", id="tab-evaluate", className="tb",    n_clicks=0),
            ], className="tabs"),

            # ── ASK TAB ──────────────────────────────────────────────────────
            html.Div([
                html.Div([
                    html.Div("🔬 research-rag-bench", className="sh-logo"),
                    html.Div(id="steps-slot"),
                    html.Div([
                        dcc.Input(id="q-input", type="text", debounce=False,
                                  placeholder="Ask anything about your papers…",
                                  className="search-box", n_submit=0),
                        html.Button("Ask →", id="q-btn", className="search-enter-btn", n_clicks=0),
                    ], className="search-box-wrap"),
                    html.Div("Press Enter or click Ask →", className="search-hint"),
                    html.Div([
                        html.Div("✨ Or try an example — papers load automatically", className="ex-label"),
                        html.Div(ex_btns, className="ex-grid"),
                    ], className="ex-wrap"),
                    # expert panel — always in DOM, toggled via style callback
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span("Search method"),
                                _tip_span("How the app finds relevant passages. Hybrid is recommended."),
                            ], className="ctrl-lbl"),
                            html.Div(method_cards, className="meth-row"),
                            dcc.RadioItems(id="q-method", value="hybrid",
                                           options=[{"label":k,"value":k} for k in ["bm25","vector","hybrid"]],
                                           style={"display":"none"}),
                        ], className="ctrl-card"),
                        html.Div([
                            html.Div([
                                html.Span("Results"),
                                _tip_span("How many passages to retrieve before writing the answer."),
                            ], className="ctrl-lbl"),
                            dcc.Slider(id="q-k", min=1, max=10, step=1, value=5,
                                       marks={i:str(i) for i in [1,3,5,7,10]},
                                       tooltip={"placement":"bottom"}),
                            html.Div(style={"height":"8px"}),
                            html.Div([
                                html.Span("Generator"),
                                _tip_span("The model that writes the answer. Larger = better quality, slower on CPU."),
                            ], className="ctrl-lbl"),
                            dcc.Dropdown(id="q-model", options=gen_opts, value=DEFAULT_MODEL,
                                         clearable=False, style={"fontSize":"13px"}),
                            html.Div(id="model-tip"),
                        ], className="ctrl-card"),
                    ], className="expert-panel", id="expert-panel"),
                ], className="search-hero", id="search-hero"),
                dcc.Loading(html.Div(id="answer-area"), type="dot", color="var(--pr)"),
            ], id="tab-content-ask", style={"display":"flex","flexDirection":"column","alignItems":"center"}),

            # ── LOAD TAB ─────────────────────────────────────────────────────
            html.Div([
                html.Div([
                    html.Div("Load papers from arXiv", className="card-h"),
                    html.P("Search any topic — we fetch real papers and build your knowledge base. Example cards on the Ask tab do this automatically.", style={"fontSize":"13px","color":"var(--mt)","marginBottom":"12px","lineHeight":"1.6"}),
                    html.Label("Search topic", className="fl"),
                    dcc.Input(id="ingest-q", type="text", placeholder="e.g. survey large language models transformer", className="inp"),
                    html.Div([
                        html.Div([
                            html.Label("Number of papers", className="fl", style={"marginTop":"12px"}),
                            dcc.Slider(id="n-papers", min=1, max=10, step=1, value=5,
                                       marks={i:str(i) for i in range(1,11)}, tooltip={"placement":"bottom"}),
                        ], style={"flex":"1"}),
                        html.Div([
                            html.Label("Text splitting", className="fl", style={"marginTop":"12px"}),
                            dcc.Dropdown(id="chunk-strat",
                                         options=[{"label":"Sentence Window (recommended)","value":"sentence_window"},
                                                  {"label":"Fixed-size + overlap","value":"fixed"},
                                                  {"label":"Semantic — paragraph-aware","value":"semantic"}],
                                         value="sentence_window", clearable=False, style={"fontSize":"13px"}),
                        ], style={"flex":"1","marginLeft":"20px"}),
                    ], style={"display":"flex","alignItems":"flex-end","marginTop":"4px"}),
                    html.Div([
                        html.Button("🔍  Fetch & Index", id="fetch-btn", className="btn btn-p"),
                        html.Button("🗑️  Clear all",     id="clear-btn", className="btn btn-d"),
                    ], className="btn-row"),
                    dcc.Loading(html.Div(id="ingest-status"), type="circle", color="var(--pr)"),
                ], className="card"),
                html.Div([
                    html.Div("Indexed papers", className="card-h"),
                    html.Div(id="papers-table"),
                ], className="card"),
            ], id="tab-content-load", style={"maxWidth":"820px","margin":"0 auto","padding":"24px","display":"none"}),

            # ── COMPARE TAB ──────────────────────────────────────────────────
            html.Div([
                html.Div([
                    html.Div("Compare all three search methods", className="card-h"),
                    html.P("Run the same question through BM25, Dense Vector, and Hybrid search simultaneously.", style={"fontSize":"13px","color":"var(--mt)","marginBottom":"12px","lineHeight":"1.6"}),
                    html.Label("Your question", className="fl"),
                    dcc.Input(id="cmp-q", type="text", placeholder="How does attention work in transformers?", className="inp"),
                    html.Div([
                        html.Label("Results per method", className="fl", style={"marginTop":"12px"}),
                        dcc.Slider(id="cmp-k", min=1, max=8, step=1, value=4,
                                   marks={i:str(i) for i in range(1,9)}, tooltip={"placement":"bottom"}),
                    ]),
                    html.Div([html.Button("⚖️  Run Comparison", id="cmp-btn", className="btn btn-p")], className="btn-row"),
                ], className="card"),
                dcc.Loading(html.Div(id="cmp-out"), type="dot", color="var(--pr)"),
            ], id="tab-content-compare", style={"maxWidth":"1100px","margin":"0 auto","padding":"24px","display":"none"}),

            # ── EVALUATE TAB ─────────────────────────────────────────────────
            html.Div([
                html.Div([
                    html.Div("Batch evaluation", className="card-h"),
                    html.P("Enter up to 10 questions (one per line) to benchmark all three retrieval methods at once.", style={"fontSize":"13px","color":"var(--mt)","marginBottom":"12px","lineHeight":"1.6"}),
                    html.Label("Test questions — one per line", className="fl"),
                    dcc.Textarea(id="eval-qs", className="inp inp-area",
                                 placeholder="What is attention?\nHow does BERT differ from GPT?\nExplain gradient descent"),
                    html.Div([
                        html.Label("Results per question", className="fl", style={"marginTop":"12px"}),
                        dcc.Slider(id="eval-k", min=1, max=8, step=1, value=5,
                                   marks={i:str(i) for i in range(1,9)}, tooltip={"placement":"bottom"}),
                    ]),
                    html.Div([html.Button("📊  Run Evaluation", id="eval-btn", className="btn btn-p")], className="btn-row"),
                ], className="card"),
                dcc.Loading(html.Div(id="eval-out"), type="circle", color="var(--pr)"),
            ], id="tab-content-evaluate", style={"maxWidth":"820px","margin":"0 auto","padding":"24px","display":"none"}),

        ], id="screen-app", style={"display":"none"}),

        # modal — always in DOM
        html.Div(id="modal-slot"),
    ])

# ─────────────────────────────────────────────────────────────────────────────
# APP FACTORY
# ─────────────────────────────────────────────────────────────────────────────
def create_dash_app(server):
    app = dash.Dash(__name__, server=server, url_base_pathname="/",
                    suppress_callback_exceptions=True,
                    meta_tags=[{"name":"viewport","content":"width=device-width,initial-scale=1"}])
    app.index_string = _INDEX
    app.layout = _full_layout()

    # theme
    app.clientside_callback(
        """function(n,cur){var nxt=cur==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',nxt);return[nxt,nxt==='dark'?'🌙':'☀️'];}""",
        [Output("s-theme","data"),Output("btn-theme","children")],
        Input("btn-theme","n_clicks"),State("s-theme","data"),prevent_initial_call=True)

    # landing vs app
    @app.callback(Output("screen-landing","style"),Output("screen-app","style"),Input("s-mode","data"))
    def toggle_screens(mode):
        if mode=="landing": return {"display":"block"},{"display":"none"}
        return {"display":"none"},{"display":"block"}

    # mode selection
    @app.callback(Output("s-mode","data"),Input("pick-s","n_clicks"),Input("pick-e","n_clicks"),Input("sw-mode","n_clicks"),State("s-mode","data"),prevent_initial_call=True)
    def set_mode(ns,ne,nsw,cur):
        t=ctx.triggered_id
        if t=="pick-s": return "simple"
        if t=="pick-e": return "expert"
        if t=="sw-mode": return "expert" if cur=="simple" else "simple"
        return cur

    # expert panel show/hide
    @app.callback(Output("expert-panel","style"),Input("s-mode","data"))
    def toggle_expert(mode):
        if mode=="simple": return {"display":"none"}
        return {"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px","marginBottom":"12px","width":"100%","maxWidth":"760px"}

    # search hero compact
    @app.callback(Output("search-hero","className"),Input("s-step","data"))
    def hero_class(step):
        return "search-hero compact" if (step or 0)>=2 else "search-hero"

    # step bar
    @app.callback(Output("steps-slot","children"),Input("s-step","data"))
    def update_steps(step):
        return _steps_bar(step or 0)

    # stats
    @app.callback(Output("stats-txt","children"),Input("iv-stats","n_intervals"))
    def stats_tick(_):
        from app.store import store
        s=store.stats()
        return f"📄 {s['n_documents']} papers · ✂️ {s['n_chunks']} chunks · {'✅ ready' if s['has_faiss'] else '⚪ not indexed'}"

    # tab switching
    @app.callback(
        Output("tab-content-ask","style"),Output("tab-content-load","style"),
        Output("tab-content-compare","style"),Output("tab-content-evaluate","style"),
        Output("tab-ask","className"),Output("tab-load","className"),
        Output("tab-compare","className"),Output("tab-evaluate","className"),
        Output("s-tab","data"),
        Input("tab-ask","n_clicks"),Input("tab-load","n_clicks"),
        Input("tab-compare","n_clicks"),Input("tab-evaluate","n_clicks"),
        prevent_initial_call=True)
    def switch_tab(*_):
        t=(ctx.triggered_id or "tab-ask").replace("tab-","")
        ask_s  = {"display":"flex","flexDirection":"column","alignItems":"center"}
        page_s = {"maxWidth":"820px","margin":"0 auto","padding":"24px"}
        wide_s = {"maxWidth":"1100px","margin":"0 auto","padding":"24px"}
        all_s  = {"ask":dict(**ask_s),"load":dict(**page_s),"compare":dict(**wide_s),"evaluate":dict(**page_s)}
        for k in all_s:
            if k!=t: all_s[k]["display"]="none"
        tabs=["ask","load","compare","evaluate"]
        return (*[all_s[k] for k in tabs],*["tb on" if k==t else "tb" for k in tabs],t)

    # method cards
    @app.callback(Output("q-method","value"),Output("mc-bm25","className"),Output("mc-vector","className"),Output("mc-hybrid","className"),Input("mc-bm25","n_clicks"),Input("mc-vector","n_clicks"),Input("mc-hybrid","n_clicks"),prevent_initial_call=True)
    def pick_method(b,v,h):
        sel=(ctx.triggered_id or "mc-hybrid").replace("mc-","")
        return sel,*["mc on" if m==sel else "mc" for m in ["bm25","vector","hybrid"]]

    # model tip
    @app.callback(Output("model-tip","children"),Input("q-model","value"),prevent_initial_call=False)
    def model_tip(mid):
        from app.models.generator import DEFAULT_MODEL
        return _model_tip_el(mid or DEFAULT_MODEL)

    # example → modal
    @app.callback(Output("modal-slot","children"),Output("s-pex","data"),Input({"type":"exbtn","index":ALL},"n_clicks"),prevent_initial_call=True)
    def open_modal(clicks):
        if not any(c and c>0 for c in clicks): return dash.no_update,dash.no_update
        idx=next(i for i,c in enumerate(clicks) if c and c>0)
        e=EXAMPLES[idx]
        return html.Div([html.Div([
            html.Div(e["icon"],className="m-icon"),
            html.Div("Load this example?",className="m-title"),
            html.Div(["We'll fetch relevant papers from arXiv (~15 s), then pre-fill the question. Just press Ask → when ready."],className="m-body"),
            html.Div(f'"{e["q"]}"',className="m-q"),
            html.Div([
                html.Button("📥 Yes, load papers",  id="modal-yes",n_clicks=0,className="btn btn-p", style={"flex":"1","justifyContent":"center"}),
                html.Button("✏️ I'll type my own",   id="modal-no", n_clicks=0,className="btn btn-g",style={"flex":"1","justifyContent":"center"}),
            ],className="m-btns"),
        ],className="modal")],className="modal-bg"),idx

    # modal yes
    @app.callback(
        Output("ingest-status","children",allow_duplicate=True),
        Output("papers-table","children",allow_duplicate=True),
        Output("q-input","value"),
        Output("modal-slot","children",allow_duplicate=True),
        Output("s-step","data",allow_duplicate=True),
        Output("s-tab","data",allow_duplicate=True),
        Output("tab-content-ask","style",allow_duplicate=True),
        Output("tab-content-load","style",allow_duplicate=True),
        Output("tab-ask","className",allow_duplicate=True),
        Output("tab-load","className",allow_duplicate=True),
        Input("modal-yes","n_clicks"),State("s-pex","data"),prevent_initial_call=True)
    def load_example(n,idx):
        if not n or idx is None: return [dash.no_update]*10
        from app.store import store
        from app.utils.arxiv_loader import fetch_arxiv_papers
        from app.utils.chunker import chunk_text
        from app.models.embedder import embed_texts
        from app.models.retriever import build_faiss_index,build_bm25_index
        e=EXAMPLES[idx]
        try:
            papers=fetch_arxiv_papers(e["arxiv"],max_results=6)
            new_chunks=[]
            for p in papers:
                if any(d["id"]==p["id"] for d in store.documents): continue
                store.add_document(p)
                for i,ct in enumerate(chunk_text(f"{p['title']}.\n\n{p['abstract']}","sentence_window")):
                    new_chunks.append({"id":f"{p['id']}_chunk_{i}","doc_id":p["id"],"title":p["title"],"text":ct,"chunk_idx":i,"source":p["url"]})
            store.add_chunks(new_chunks)
            if store.chunk_texts:
                embs=embed_texts(store.chunk_texts); store.set_embeddings(embs)
                store.faiss_index=build_faiss_index(embs); store.bm25_index=build_bm25_index(store.chunk_texts)
            store.save(); s=store.stats()
            st=html.Span(f"✅ Loaded {len(papers)} papers → {len(new_chunks)} new chunks. Total: {s['n_documents']} docs, {s['n_chunks']} chunks.",className="ok")
            ask_s={"display":"flex","flexDirection":"column","alignItems":"center"}
            load_s={"maxWidth":"820px","margin":"0 auto","padding":"24px","display":"none"}
            return st,_papers_table(store.documents),e["q"],html.Div(),1,"ask",ask_s,load_s,"tb on","tb"
        except Exception as exc:
            return html.Span(f"❌ {exc}",className="er"),*([dash.no_update]*9)

    # modal no
    @app.callback(Output("modal-slot","children",allow_duplicate=True),Input("modal-no","n_clicks"),prevent_initial_call=True)
    def close_modal(_): return html.Div()

    # query (Enter or button)
    @app.callback(
        Output("answer-area","children"),Output("s-step","data",allow_duplicate=True),
        Input("q-btn","n_clicks"),Input("q-input","n_submit"),
        State("q-input","value"),State("q-method","value"),State("q-k","value"),
        State("q-model","value"),State("s-mode","data"),prevent_initial_call=True)
    def handle_query(_,ns,question,method,k,model_id,mode):
        from app.store import store
        from app.models.generator import generate_answer,MODEL_OPTIONS,DEFAULT_MODEL
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval,answer_faithfulness
        if not question or not question.strip():
            return html.Span("⚠️ Please enter a question.",className="wn"),dash.no_update
        if not store.is_indexed:
            return html.Div([html.Span("⚠️ No papers loaded. ",className="wn",style={"fontWeight":"700"}),html.Span("Click an example card above, or go to the Load tab.",style={"color":"var(--mt)","fontSize":"13px"})]),dash.no_update
        mid=model_id or DEFAULT_MODEL
        if mode=="simple": method,k="hybrid",5
        results=retrieve_top_k(question,method or "hybrid",store.faiss_index,store.bm25_index,store.chunks,k=k or 5)
        context="\n\n".join(r["chunk"]["text"] for r in results)
        answer=generate_answer(question,context,model_id=mid)
        mt=evaluate_retrieval(question,results); mt["faithfulness"]=answer_faithfulness(answer,context)
        mlabel=MODEL_OPTIONS.get(mid,{}).get("label",mid)
        simple=mode=="simple"
        mth_label=METHODS.get(method or "hybrid",METHODS["hybrid"])["label"]
        return html.Div([
            html.Div([html.Div("Answer",className="a-lbl"),html.P(answer,className="a-text"),html.Div(f"Generated by {mlabel}",className="a-by")],className="a-card"),
            html.Div([_metric("Relevance",mt["context_relevance"],"var(--pr)"),_metric("Faithfulness",round(mt["faithfulness"],3),"var(--ok)"),_metric("Diversity",mt["diversity"],"var(--wn)"),_metric("Chunks",mt["n_retrieved"],"var(--mt)")],className="metrics-row"),
            (html.Div([html.Span("📐 What do the scores mean? ",style={"fontWeight":"700","fontSize":"12px","color":"var(--tx)"}),html.Span("Relevance = how on-topic the passages are. Faithfulness = how much the answer is backed by the papers (1.0 = nothing made up). Diversity = how varied the passages are.",style={"fontSize":"12px","color":"var(--mt)"})],style={"background":"var(--pr-bg)","border":"1px solid var(--pr-bd)","borderRadius":"8px","padding":"10px 14px","marginBottom":"14px","lineHeight":"1.6"}) if simple else html.Div()),
            html.Div([
                html.Div([html.Span("Retrieved passages",style={"fontWeight":"700","fontSize":"13px","color":"var(--tx)"}),html.Span(f" · {mth_label}",style={"fontSize":"12px","color":"var(--pr)","fontWeight":"700"})],className="chunks-hdr"),
                html.Div([_chunk(r) for r in results]),
            ],className="chunks-card"),
        ],className="answer-wrap"),2

    # ingest
    @app.callback(Output("ingest-status","children"),Output("papers-table","children"),Input("fetch-btn","n_clicks"),Input("clear-btn","n_clicks"),State("ingest-q","value"),State("n-papers","value"),State("chunk-strat","value"),prevent_initial_call=True)
    def handle_ingest(_f,_c,query,n,strat):
        from app.store import store
        from app.utils.arxiv_loader import fetch_arxiv_papers
        from app.utils.chunker import chunk_text
        from app.models.embedder import embed_texts
        from app.models.retriever import build_faiss_index,build_bm25_index
        if ctx.triggered_id=="clear-btn":
            store.clear(); return html.Span("✅ Index cleared.",className="ok"),html.Div()
        if not query or not query.strip():
            return html.Span("⚠️ Please enter a topic.",className="wn"),dash.no_update
        try:
            papers=fetch_arxiv_papers(query.strip(),max_results=n or 5)
            if not papers: return html.Span("❌ No papers found.",className="er"),dash.no_update
            new_chunks=[]
            for p in papers:
                if any(d["id"]==p["id"] for d in store.documents): continue
                store.add_document(p)
                for i,ct in enumerate(chunk_text(f"{p['title']}.\n\n{p['abstract']}",strat or "sentence_window")):
                    new_chunks.append({"id":f"{p['id']}_chunk_{i}","doc_id":p["id"],"title":p["title"],"text":ct,"chunk_idx":i,"source":p["url"]})
            store.add_chunks(new_chunks)
            if store.chunk_texts:
                embs=embed_texts(store.chunk_texts); store.set_embeddings(embs)
                store.faiss_index=build_faiss_index(embs); store.bm25_index=build_bm25_index(store.chunk_texts)
            store.save(); s=store.stats()
            return html.Span(f"✅ {len(papers)} paper(s) → {len(new_chunks)} new chunks. Total: {s['n_documents']} docs, {s['n_chunks']} chunks.",className="ok"),_papers_table(store.documents)
        except Exception as exc:
            return html.Span(f"❌ {exc}",className="er"),dash.no_update

    # compare
    @app.callback(Output("cmp-out","children"),Input("cmp-btn","n_clicks"),State("cmp-q","value"),State("cmp-k","value"),State("s-theme","data"),prevent_initial_call=True)
    def handle_compare(_,q,k,theme):
        from app.store import store
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval
        if not q or not q.strip(): return html.Span("⚠️ Please enter a question.",className="wn")
        if not store.is_indexed: return html.Span("⚠️ No papers indexed.",className="wn")
        all_r,all_m={},{}
        for m in ["bm25","vector","hybrid"]:
            r=retrieve_top_k(q,m,store.faiss_index,store.bm25_index,store.chunks,k=k or 4)
            all_r[m]=r; all_m[m]=evaluate_retrieval(q,r)
        t=theme or "dark"
        cols=[html.Div([
            html.Div([html.Span("●",style={"color":METHODS[m]["color"],"fontSize":"16px","marginRight":"6px"}),html.Span(METHODS[m]["label"],style={"fontWeight":"800","fontSize":"13px"})],style={"display":"flex","alignItems":"center","marginBottom":"7px"}),
            html.Div(f"Relevance: {all_m[m]['context_relevance']}  ·  Diversity: {all_m[m]['diversity']}",style={"fontSize":"12px","color":"var(--mt)","marginBottom":"10px"}),
            html.Div([_chunk(r,compact=True) for r in all_r[m]]),
        ],className="card",style={"flex":"1","minWidth":"0","margin":"0 4px"}) for m in ["bm25","vector","hybrid"]]
        return html.Div([
            html.Div([dcc.Graph(figure=_radar(all_m,t),config={"displayModeBar":False})],className="card"),
            html.Div([dcc.Graph(figure=_bar(all_m,t),  config={"displayModeBar":False})],className="card"),
            html.Div(cols,style={"display":"flex","gap":"0"}),
        ])

    # evaluate
    @app.callback(Output("eval-out","children"),Input("eval-btn","n_clicks"),State("eval-qs","value"),State("eval-k","value"),State("s-theme","data"),prevent_initial_call=True)
    def handle_eval(_,qs_text,k,theme):
        from app.store import store
        from app.models.retriever import retrieve_top_k
        from app.utils.metrics import evaluate_retrieval
        if not qs_text or not qs_text.strip(): return html.Span("⚠️ Please enter questions.",className="wn")
        if not store.is_indexed: return html.Span("⚠️ No papers indexed.",className="wn")
        qs=[q.strip() for q in qs_text.strip().split("\n") if q.strip()][:10]
        agg={m:{"context_relevance":[],"diversity":[]} for m in ["bm25","vector","hybrid"]}
        for q in qs:
            for m in agg:
                r=retrieve_top_k(q,m,store.faiss_index,store.bm25_index,store.chunks,k=k or 5)
                mt=evaluate_retrieval(q,r)
                agg[m]["context_relevance"].append(mt["context_relevance"])
                agg[m]["diversity"].append(mt["diversity"])
        avg_r={m:round(sum(v["context_relevance"])/len(v["context_relevance"]),4) for m,v in agg.items()}
        avg_d={m:round(sum(v["diversity"])/len(v["diversity"]),4) for m,v in agg.items()}
        summary={m:{"context_relevance":avg_r[m],"diversity":avg_d[m],"avg_score":round((avg_r[m]+avg_d[m])/2,4)} for m in ["bm25","vector","hybrid"]}
        t=theme or "dark"
        return html.Div([
            html.Div([dcc.Graph(figure=_radar(summary,t),config={"displayModeBar":False})],className="card"),
            html.Div([dcc.Graph(figure=_area(qs,agg,t), config={"displayModeBar":False})],className="card"),
            html.Div([html.Span(f"✅ Evaluated {len(qs)} question(s) across 3 methods.",className="ok",style={"display":"block","marginBottom":"7px"}),html.P("Hybrid RRF consistently scores highest — keyword precision from BM25 combined with semantic coverage from dense retrieval.",style={"fontSize":"13px","color":"var(--mt)","lineHeight":"1.6"})],className="card"),
        ])

    return app