#!/usr/bin/env python3
"""Export every chapter notebook to one interactive WASM page and build a site.

Produces a static, mobile-friendly site under ``site/``:

    site/
      index.html            # one link per chapter
      .nojekyll
      tutor.js, tutor.css   # the in-page AI tutor widget (web/)
      <chapter-name>/       # one WASM-exported notebook per chapter

Each chapter is exported once in ``edit`` mode with code hidden by default, so
it reads cleanly but any cell can be expanded and edited in the browser. The
build injects the tutor widget (a floating icon -> chat panel) plus that
chapter's context into the exported page. The tutor is bring-your-own-key: each
visitor pastes their own Anthropic key, so the site needs no server and costs
the owner nothing.
"""

from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = REPO / "differential_equations" / "chapters"
DELIB_DIR = REPO / "differential_equations" / "delib"
ASSETS_DIR = REPO / "assets"  # pre-rendered media (e.g. Manim clips) -> site/assets/
SITE = REPO / "site"
WEB = REPO / "web"            # static templates/assets (landing.html, …)

# Absolute base URL for share-card (Open Graph) tags. Default to the
# GitHub Pages project-page convention; override with SITE_BASE_URL for a
# custom domain. No trailing slash.
SITE_BASE_URL = os.environ.get(
    "SITE_BASE_URL", "https://chipmunk91.github.io/Math_learn"
).rstrip("/")

# The full course arc, grouped by Part (titles match ROADMAP.md). Each entry
# is (display title, built-slug-or-None); a chapter shows as "available" when
# its slug is among the chapters actually built.
ROADMAP_PARTS = [
    ("Part I · First-order equations", "reading the field, then solving it", [
        ("First-order ODEs & slope fields", "ch01_first_order_odes"),
        ("Separable & linear", "ch02_separable_and_linear"),
        ("Exact equations", "ch03a_exact_equations"),
        ("Integrating factors & substitutions", "ch03b_integrating_factors"),
        ("Numerical methods", "ch04_numerical_methods"),
    ]),
    ("Part II · Higher-order & transforms", "oscillation, resonance, Laplace", [
        ("Second-order ODEs", "ch06_second_order"),
        ("Damping, forcing, resonance", "ch07_damping_forcing_resonance"),
        ("Non-homogeneous equations", None),
        ("Laplace transforms", None),
    ]),
    ("Part III · Qualitative dynamics", "what the flow does without solving it", [
        ("Fixed points & stability", "ch05_fixed_points_stability"),
        ("Bifurcations in 1-D", None),
        ("Flows on the circle", None),
        ("Linear 2-D systems", None),
        ("Nonlinear phase portraits", None),
        ("Limit cycles", None),
        ("Bifurcations in 2-D", None),
    ]),
    ("Part IV · Partial differential equations", "variation in space and time", [
        ("Intro to PDEs", None),
        ("Heat equation", None),
        ("Wave equation", None),
        ("Fourier series", None),
    ]),
    ("Part V · Chaos", "sensitive dependence, strange attractors", [
        ("The Lorenz attractor", None),
        ("One-dimensional maps", None),
        ("Fractals", None),
    ]),
]

# Nice (chapter-label, title) for the built chapters shown as "Read it now"
# cards, in reading order. Keys are slugs; the lab is featured separately.
CHAPTER_CARDS = {
    "ch01_first_order_odes": ("Chapter 1", "First-order ODEs & slope fields"),
    "ch02_separable_and_linear": ("Chapter 2", "Separable & linear equations"),
    "ch03a_exact_equations": ("Chapter 3 · I", "Exact equations"),
    "ch03b_integrating_factors": ("Chapter 3 · II", "Integrating factors & substitutions"),
    "ch04_numerical_methods": ("Chapter 4", "Numerical methods"),
    "ch05_fixed_points_stability": ("Chapter 5", "Fixed points & stability"),
    "ch06_second_order": ("Chapter 6", "Second-order ODEs"),
    "ch07_damping_forcing_resonance": ("Chapter 7", "Damping, forcing, resonance"),
}

# delib is a locally-installed package and does not exist in the browser's
# Pyodide runtime. For the WASM build we inline its source into each notebook so
# the exported page is self-contained.
# Every module in differential_equations/delib/ that chapters use must be
# listed here — the WASM bootstrap concatenates exactly these sources into
# the inlined `delib` module. Forgetting a new module breaks chapters at
# runtime in the browser (helpers silently missing) even though the local
# build passes.
DELIB_MODULES = ["solvers", "fields", "animate", "oscillators", "widgets", "ui"]
_FUTURE = re.compile(r"^from __future__ import .*$", re.MULTILINE)

PEP723_HEADER = """\
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "anywidget",
#     "numpy",
#     "sympy",
#     "plotly",
# ]
# ///
"""

# Strip marimo's editor chrome down to just the notebook. The cells and their
# per-cell controls (run, add, delete, edit) live outside these wrappers, so
# hiding the chrome leaves editing fully intact. Selectors are marimo's stable
# data-testid hooks. Tune this list if a future marimo version renames them.
MARIMO_CHROME_CSS = (
    "<style>"
    '[data-testid="chrome-sidebar"],'
    '[data-testid="chrome-context-aware-panel"],'
    '[data-testid="chrome-footer"],'
    '[data-testid="footer-panel"],'
    '[data-testid="chrome-controls-top-right"],'
    '[data-testid="watermark"],'
    '[data-testid="static-notebook-banner"],'
    # Per-cell language switcher (Python <-> SQL/Markdown). Hiding it keeps every
    # cell Python, so learners can't flip a cell to SQL.
    '[data-testid="language-button"],'
    '[data-testid="language-toggle-button"]'
    "{display:none !important;}"
    "</style>"
)

# Hide marimo's SQL and "Generate with AI" affordances, which only confuse a
# math-learning context (and AI codegen can't work without a server anyway).
# These buttons/menu items carry no stable data-testid, so we match them by
# their accessible label and re-apply on every DOM change. Verified against
# marimo 0.23.8; re-check the LABELS list after a marimo upgrade.
MARIMO_HIDE_JS = (
    "<script>(function(){"
    'var LABELS=["generate with ai","chat with ai","edit with ai",'
    '"fix with ai","ai completion","sql","add sql cell","convert to sql",'
    '"add to notebook"];'
    'function norm(s){return (s||"").replace(/\\s+/g," ").trim().toLowerCase();}'
    "function sweep(){"
    'var ns=document.querySelectorAll(\'button,[role="menuitem"],a[role="menuitem"]\');'
    "for(var i=0;i<ns.length;i++){var n=ns[i];if(n.dataset.mlHidden)continue;"
    'var label=norm(n.getAttribute("aria-label"))||norm(n.textContent);'
    'if(LABELS.indexOf(label)!==-1||label.indexOf("add to notebook")!==-1){n.style.display="none";n.dataset.mlHidden="1";continue;}'
    # Hide marimo's own sidebar opener: a small icon button parked at the very
    # top-left, just under our fixed nav. Our nav "Tutor" button replaces it.
    'if(!n.closest(".ml-chapter-nav")){var r=n.getBoundingClientRect();'
    "if(r.top>=40&&r.top<96&&r.left<64&&r.width<=56&&r.height<=56){"
    'n.style.display="none";n.dataset.mlHidden="1";}}}}'
    "var pend=false;function schedule(){if(pend)return;pend=true;"
    "requestAnimationFrame(function(){pend=false;sweep();});}"
    "function start(){new MutationObserver(schedule).observe(document.body,"
    "{childList:true,subtree:true});window.addEventListener('resize',schedule);sweep();}"
    'if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",start);}'
    "else{start();}"
    "})();</script>"
)

# marimo renders the chat inside Shadow DOM (style-encapsulated), so a page-level
# KaTeX auto-render never reaches it. This walks every shadow root, injects KaTeX's
# stylesheet into roots that contain math (shadow DOM doesn't inherit page CSS), and
# observes each root so streaming chat messages get rendered too. Idempotent; code/
# pre ignored; marimo's own math has no literal $ so it's untouched.
KATEX_CSS = (
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous" />'
)
MATH_RENDER_JS = (
    '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>'
    '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" crossorigin="anonymous"></script>'
    "<script>(function(){"
    "var CSS='https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css';"
    "var seen=new WeakSet();"
    "var OPTS={delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],throwOnError:false,ignoredTags:['script','noscript','style','textarea','pre','code']};"
    "function ensureCss(root){try{if(root.querySelector&&!root.querySelector('link[data-mlk]')){var l=document.createElement('link');l.rel='stylesheet';l.href=CSS;l.setAttribute('data-mlk','1');root.appendChild(l);}}catch(e){}}"
    "var MCSS='@media(max-width:640px){.js-plotly-plot,.plotly,.plot-container,.svg-container{max-width:100%!important}.cm-editor,.cm-scroller{max-width:100%!important}table{display:block;overflow-x:auto}img,svg{max-width:100%;height:auto}.marimo-cell,[data-testid=\"cell-output\"]{overflow-x:auto;max-width:100%}}';"
    "function injectMobile(root){try{if(root.querySelector&&!root.querySelector('style[data-mlm]')){var s=document.createElement('style');s.setAttribute('data-mlm','1');s.textContent=MCSS;root.appendChild(s);}}catch(e){}}"
    "function proc(root){if(!window.renderMathInElement)return;try{if((root.textContent||'').indexOf('$')>-1){ensureCss(root);var k=root.children||[];for(var i=0;i<k.length;i++){try{window.renderMathInElement(k[i],OPTS);}catch(e){}}}}catch(e){}}"
    "function walk(root){injectMobile(root);proc(root);var els;try{els=root.querySelectorAll('*');}catch(e){return;}for(var i=0;i<els.length;i++){var sr=els[i].shadowRoot;if(sr){if(!seen.has(sr)){seen.add(sr);try{new MutationObserver(sch).observe(sr,{childList:true,subtree:true,characterData:true});}catch(e){}}walk(sr);}}}"
    "var p=false;function sch(){if(p)return;p=true;requestAnimationFrame(function(){p=false;walk(document.body);});}"
    "function start(){new MutationObserver(sch).observe(document.body,{childList:true,subtree:true});sch();setTimeout(sch,800);setTimeout(sch,2000);setTimeout(sch,4000);}"
    'if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",start);}else{start();}'
    "})();</script>"
)


# marimo's bundled Plotly throws a non-fatal TypeError reading
# '_redrawFromAutoMarginCount' when a chart's container is resized before the
# chart is fully drawn (rampant during our load-time layout thrash + the
# chrome-hiding observer). The chart still renders fine; marimo's plugin just
# catches it and console.errors a red "PlotlyPlugin: ..." line. This filter
# drops exactly that one message (matched by the property name) so real errors
# are untouched. Belt-and-suspenders with the build-time bundle guard in
# patch_plotly_assets(); this version-independent filter is the robust backstop.
PLOTLY_GUARD_JS = (
    "<script>(function(){"
    "var KEY='_redrawFromAutoMarginCount';"
    "function hit(s){return !!(s&&s.indexOf&&s.indexOf(KEY)>=0);}"
    "var oe=console.error.bind(console);"
    "console.error=function(){try{var s='';for(var i=0;i<arguments.length;i++){"
    "var a=arguments[i];s+=' '+((a&&a.message)||a);}if(hit(s))return;}catch(e){}"
    "return oe.apply(console,arguments);};"
    "window.addEventListener('error',function(e){"
    "if(hit(e&&e.message)||(e&&e.error&&hit(String(e.error.message)))){"
    "e.preventDefault();e.stopImmediatePropagation();}},true);"
    "window.addEventListener('unhandledrejection',function(e){"
    "var r=e&&e.reason;if(r&&hit(String((r&&r.message)||r)))e.preventDefault();});"
    "})();</script>"
)


# A branded splash shown immediately on a chapter page, covering everything
# (z-index above the nav) until marimo's WASM runtime has booted Pyodide and
# rendered the first cell. Without it, a cold visitor stares at a blank page
# for several seconds and assumes the site is broken.
LOADING_CSS = (
    "<style>"
    ".ml-loading{position:fixed;inset:0;z-index:3000;background:#fff;"
    "display:flex;flex-direction:column;align-items:center;justify-content:center;"
    "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;"
    "color:#1d2733;text-align:center;padding:1.5rem;transition:opacity .55s ease;}"
    ".ml-loading.ml-hide{opacity:0;pointer-events:none;}"
    ".ml-loading .ring{width:46px;height:46px;border-radius:50%;"
    "border:4px solid #e3e9f0;border-top-color:#5b7db1;"
    "animation:ml-spin .9s linear infinite;}"
    ".ml-loading .t{margin-top:1.1rem;font-size:1.15rem;font-weight:600;}"
    ".ml-loading .s{margin-top:.4rem;font-size:.95rem;color:#56636f;max-width:24rem;line-height:1.5;}"
    ".ml-loading .b{margin-top:1.2rem;font-size:.82rem;color:#9aa7b5;max-width:26rem;line-height:1.5;}"
    # Indeterminate progress bar (we can't read true % from the Pyodide worker,
    # so honest continuous motion beats a faked percentage).
    ".ml-loading .bar{margin-top:1.25rem;width:240px;max-width:70vw;height:6px;"
    "border-radius:3px;background:#e7ecf2;overflow:hidden;position:relative;}"
    ".ml-loading .bar i{position:absolute;top:0;left:-42%;height:100%;width:40%;"
    "background:#5b7db1;border-radius:3px;animation:ml-slide 1.25s ease-in-out infinite;}"
    ".ml-loading .el{margin-top:.5rem;font-size:.8rem;color:#9aa7b5;"
    "font-variant-numeric:tabular-nums;}"
    # Small non-blocking pill shown after the splash lifts, until the first
    # interactive demo (canvas / Plotly) renders.
    ".ml-warm{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);"
    "z-index:2900;background:#16223a;color:#dfe7f2;font:13px/1.3 -apple-system,"
    "BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;padding:9px 16px;"
    "border-radius:999px;box-shadow:0 6px 22px rgba(0,0,0,.22);display:flex;"
    "align-items:center;gap:9px;opacity:0;transition:opacity .4s ease;}"
    ".ml-warm.show{opacity:1;}"
    ".ml-warm .d{width:9px;height:9px;border-radius:50%;border:2px solid #6f86ad;"
    "border-top-color:#dfe7f2;animation:ml-spin .8s linear infinite;}"
    "@keyframes ml-slide{0%{left:-42%;}100%{left:104%;}}"
    "@keyframes ml-spin{to{transform:rotate(360deg);}}"
    "</style>"
)

# Drives the splash: honest phased status messages + an elapsed counter while
# Pyodide boots (the real cost is package install/import in a Web Worker, which
# we can't read directly, so phases are time-estimated and the bar is
# indeterminate). Lifts the splash once the intro is readable (a non-empty
# .marimo-cell) so reading can start immediately, then shows a small
# non-blocking pill until the first interactive demo renders. Hard 180s cap
# (real loads run ~60-90s, so the old 75s cap could uncover a half-built page).
LOADING_JS = r"""<script>(function () {
  var ov = document.getElementById('ml-loading'); if (!ov) return;
  var st = document.getElementById('ml-status'), el = document.getElementById('ml-elapsed');
  var t0 = Date.now(), done = false;
  var phases = [
    [0,  'Starting Python in your browser (Pyodide)…'],
    [6,  'Loading the scientific stack — NumPy, Plotly…'],
    [18, 'Unpacking and importing packages (the slow part)…'],
    [40, 'Booting the notebook kernel…'],
    [60, 'Almost there — rendering the chapter…']
  ];
  function tick() {
    var s = (Date.now() - t0) / 1000, msg = phases[0][1];
    for (var i = 0; i < phases.length; i++) { if (s >= phases[i][0]) msg = phases[i][1]; }
    if (st) st.textContent = msg;
    if (el) el.textContent = s.toFixed(0) + 's';
  }
  function ready() { var c = document.querySelector('.marimo-cell'); return !!(c && (c.textContent || '').trim().length > 0); }
  function hasDemo() { return !!document.querySelector('canvas, .js-plotly-plot, .plotly-graph-div'); }
  function warm() {
    if (hasDemo()) return;
    var w = document.createElement('div');
    w.className = 'ml-warm';
    w.innerHTML = '<span class="d"></span>warming up the interactive demos…';
    document.body.appendChild(w);
    requestAnimationFrame(function () { w.classList.add('show'); });
    var wt = Date.now();
    var wi = setInterval(function () {
      if (hasDemo() || Date.now() - wt > 150000) {
        clearInterval(wi); w.classList.remove('show');
        setTimeout(function () { if (w.parentNode) w.parentNode.removeChild(w); }, 450);
      }
    }, 400);
  }
  function hide() {
    if (done) return; done = true;
    ov.classList.add('ml-hide');
    setTimeout(function () { if (ov && ov.parentNode) ov.parentNode.removeChild(ov); }, 700);
    warm();
  }
  tick();
  var iv = setInterval(function () {
    tick();
    if (ready()) { if (st) st.textContent = 'Rendering the chapter…'; clearInterval(iv); setTimeout(hide, 500); return; }
    if (Date.now() - t0 > 180000) { clearInterval(iv); hide(); }
  }, 250);
})();</script>"""


def _loading_overlay(name: str) -> str:
    """The splash markup for a chapter page (title personalised)."""
    if _is_lab(name):
        what = "the Animation Lab"
    elif name in CHAPTER_CARDS:
        what = CHAPTER_CARDS[name][1]
    else:
        what = "the chapter"
    return (
        '<div class="ml-loading" id="ml-loading">'
        '<div class="ring"></div>'
        f'<div class="t">Loading {what}…</div>'
        '<div class="s" id="ml-status">Starting Python in your browser…</div>'
        '<div class="bar"><i></i></div>'
        '<div class="el" id="ml-elapsed">0s</div>'
        '<div class="b">This page runs a full Python runtime (Pyodide) right in '
        'your browser — no server, nothing installed. The first load can take up '
        "to a minute; it's working even when it looks still.</div>"
        '</div>'
    )


# A slim fixed bar at the top of every chapter linking to the previous/next
# chapter and back to the index. marimo's real scroll container is .dvn-scroller
# (its page is position:sticky/absolute top:0, so it ignores #root padding); we
# pad THAT so the bar never covers the first cell. The bar also carries a Tutor
# toggle that reveals marimo's mo.sidebar (aside.app-sidebar), which auto-collapses
# to display:none on narrow screens.
NAV_CSS = (
    "<style>"
    # 3-column grid so "All chapters" is always dead-centre in the viewport
    # (the auto centre column is centred by the two equal 1fr side columns,
    # regardless of the Previous/Next label widths). Previous hugs the right of
    # col 1 and Next the left of col 3, so both sit the same gap from the centre.
    # The Tutor button is pulled out of the flow (absolute, right edge) so it
    # can't pull the trio off-centre.
    ".ml-chapter-nav{position:fixed;top:0;left:0;right:0;z-index:1000;display:grid;"
    "grid-template-columns:1fr auto 1fr;align-items:center;column-gap:1.5rem;height:44px;"
    "padding:0 .75rem;background:rgba(255,255,255,.92);"
    "-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);"
    "border-bottom:1px solid #d6dde6;box-sizing:border-box;"
    "font-family:system-ui,sans-serif;font-size:.9rem;}"
    ".ml-chapter-nav a,.ml-chapter-nav button{text-decoration:none;color:#2a5d9c;"
    "font-weight:600;padding:.35rem .6rem;border-radius:.4rem;white-space:nowrap;"
    "border:none;background:transparent;cursor:pointer;font:inherit;}"
    ".ml-chapter-nav a:hover,.ml-chapter-nav button:hover{background:#f0f5fb;}"
    ".ml-chapter-nav .ml-nav-home{color:#1d2733;}"
    ".ml-chapter-nav .ml-nav-disabled{color:#aab4c0;font-weight:600;"
    "padding:.35rem .6rem;white-space:nowrap;}"
    # The content sits in a `position:absolute; top:0` wrapper with no positioned
    # ancestor, so it anchored to the VIEWPORT top — which is why padding/margin on
    # a static #root did nothing. Make #root the positioned, height-bounded
    # container (relative + height) and offset it; the inset-0 content now fills
    # #root, which starts at 44px.
    "#root{position:relative !important;margin-top:44px !important;height:calc(100vh - 44px) !important;box-sizing:border-box;}"
    "html{scroll-padding-top:48px;}"
    # Chapter content is light DOM, so clamp wide charts here (mobile crop fix) and
    # hide Plotly's toolbar on small screens (it overlaps titles).
    "@media (max-width:640px){.js-plotly-plot,.plot-container,.plotly,.svg-container,.main-svg{max-width:100% !important;}"
    ".marimo-cell{overflow-x:auto;max-width:100%;}.modebar-container,.modebar{display:none !important;}}"
    ".ml-chapter-nav a{max-width:34vw;overflow:hidden;text-overflow:ellipsis;}"
    # Symmetric trio: Previous at the inner edge of col 1, Next at the inner edge
    # of col 3, "All chapters" centred in the auto column between them.
    ".ml-nav-prev{justify-self:end;}.ml-nav-home{justify-self:center;}"
    ".ml-nav-next{justify-self:start;}"
    # We take full ownership of the tutor sidebar's visibility rather than trying
    # to detect marimo's own collapse states. marimo has THREE: inline, a narrow
    # icon bar (desktop "awkward bar"), and display:none (mobile). Detecting only
    # display:none missed the narrow bar. So: force the sidebar hidden always, and
    # let our nav "Tutor" button (always shown) be the single show/hide toggle.
    "aside.app-sidebar{display:none !important;}"
    # Tutor is a utility button anchored to the right edge, out of the grid flow
    # so it never shifts the centred Previous / All chapters / Next trio.
    ".ml-nav-tutor{position:absolute;right:.75rem;top:50%;transform:translateY(-50%);}"
    # When toggled on, float the sidebar as an overlay below the nav. The more
    # specific selector beats the blanket hide above.
    "body.ml-show-tutor aside.app-sidebar{display:block !important;position:fixed !important;"
    "top:44px !important;bottom:0 !important;left:0 !important;width:min(420px,92vw) !important;"
    "z-index:1500 !important;overflow:auto !important;background:#fff !important;"
    "box-shadow:0 8px 30px rgba(0,0,0,.18);}"
    # Make the active Tutor button read as a close affordance.
    "body.ml-show-tutor .ml-nav-tutor{background:#e7f0fb;color:#16223a;}"
    "@media (max-width:480px){.ml-chapter-nav{font-size:.8rem;padding:0 .4rem;}}"
    "</style>"
)


def nav_bar(names: list[str], idx: int) -> str:
    """Build the prev / index / next navigation bar for chapter ``idx``."""
    if idx > 0:
        prev = names[idx - 1]
        left = f'<a class="ml-nav-prev" href="../{prev}/" title="{pretty(prev)}">&larr; Previous</a>'
    else:
        left = '<span class="ml-nav-prev ml-nav-disabled">&larr; Previous</span>'
    if idx < len(names) - 1:
        nxt = names[idx + 1]
        right = f'<a class="ml-nav-next" href="../{nxt}/" title="{pretty(nxt)}">Next &rarr;</a>'
    else:
        right = '<span class="ml-nav-next ml-nav-disabled">Next &rarr;</span>'
    home = '<a class="ml-nav-home" href="../">All chapters</a>'
    # Tutor toggle (visible only when the sidebar auto-collapses): flip a body
    # class our CSS uses to float aside.app-sidebar, and expand it so its content
    # (hidden when data-expanded=false) shows.
    tutor = (
        '<button class="ml-nav-tutor" aria-label="Toggle tutor" '
        "onclick=\"document.body.classList.toggle('ml-show-tutor');"
        "var a=document.querySelector('aside.app-sidebar');"
        "if(a){a.setAttribute('data-expanded','true');}\">&#128172; Tutor</button>"
    )
    return (
        '<nav class="ml-chapter-nav" aria-label="Chapter navigation">'
        f"{left}{home}{right}{tutor}</nav>"
    )


def inject_nav(page: Path, names: list[str], idx: int) -> None:
    """Add the chapter navigation bar (styles in <head>, bar after <body>)."""
    html = page.read_text(encoding="utf-8")
    if "</head>" not in html or "<body>" not in html:
        raise ValueError(f"missing </head> or <body> in {page}")
    html = html.replace("</head>", NAV_CSS + "</head>", 1)
    html = html.replace("<body>", "<body>" + nav_bar(names, idx), 1)
    page.write_text(html, encoding="utf-8")


def chapters() -> list[Path]:
    # Real chapters: chNN_<topic>.py *or* chNN<letter>_<topic>.py for chapters
    # that ship in multiple parts (e.g. ch03a_..., ch03b_...). Lexical sort
    # puts ch03a_ before ch03b_ before ch04_ before ch05_, which matches the
    # intended reading order. Skips _template.py and zz_spike_*.py experiments.
    return sorted(
        list(CHAPTERS_DIR.glob("ch[0-9][0-9]_*.py"))
        + list(CHAPTERS_DIR.glob("ch[0-9][0-9][a-z]_*.py"))
    )


def delib_bootstrap() -> str:
    parts = ["from __future__ import annotations"]
    for mod in DELIB_MODULES:
        src = (DELIB_DIR / f"{mod}.py").read_text(encoding="utf-8")
        parts.append(_FUTURE.sub("", src))
    combined = "\n\n".join(parts)
    encoded = base64.b64encode(combined.encode("utf-8")).decode("ascii")
    # Rebuild the `delib` package from a base64 string at runtime, since the
    # Pyodide runtime can't `import delib` from disk. Wrapped with timing so
    # the ?diag=1 overlay can show how long b64-decode / exec / import take.
    return (
        "    import base64 as _b64, sys as _sys, types as _types, time as _tm\n"
        "    _t0 = _tm.perf_counter()\n"
        '    _delib = _types.ModuleType("delib")\n'
        f'    _delib_src = _b64.b64decode("{encoded}").decode("utf-8")\n'
        "    _t1 = _tm.perf_counter()\n"
        '    exec(compile(_delib_src, "delib (inlined for WASM)", "exec"),\n'
        "         _delib.__dict__)\n"
        "    _t2 = _tm.perf_counter()\n"
        '    _sys.modules["delib"] = _delib\n'
        "    import delib\n"
        "    _t3 = _tm.perf_counter()\n"
        "    try:  # surface to the ?diag=1 overlay via the JS console\n"
        "        import js as _js  # only present in Pyodide\n"
        "        _js.console.log(f'[diag] delib b64-decode: {(_t1-_t0)*1000:.0f}ms')\n"
        "        _js.console.log(f'[diag] delib exec: {(_t2-_t1)*1000:.0f}ms')\n"
        "        _js.console.log(f'[diag] delib import: {(_t3-_t2)*1000:.0f}ms')\n"
        "    except Exception:\n"
        "        pass\n"
    )


def inline_delib(source: str) -> str:
    # Tolerate a trailing comment after `import delib` (e.g. `# noqa`).
    pattern = re.compile(r"^[ \t]*import delib[ \t]*(?:#.*)?$", re.MULTILINE)
    if not pattern.search(source):
        raise ValueError("expected a standalone `import delib` line to inline")
    return pattern.sub(delib_bootstrap().rstrip("\n"), source, count=1)


def export(notebook: Path, out_dir: Path) -> None:
    """Export a chapter to a single WASM HTML page (run mode: auto-runs, code hidden)."""
    transformed = PEP723_HEADER + inline_delib(notebook.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / notebook.name
        staged.write_text(transformed, encoding="utf-8")
        subprocess.run(
            [sys.executable, "-m", "marimo", "export", "html-wasm", str(staged), "-o", str(out_dir), "--mode", "run"],
            check=True,
        )


def pretty(name: str) -> str:
    """ch01_first_order_odes -> 'Ch01 — First Order Odes'."""
    head, _, tail = name.partition("_")
    return f"{head.capitalize()} — {tail.replace('_', ' ').title()}"


_CELL_SPLIT = re.compile(r"(?m)^@app\.cell")
_DEF_LINE = re.compile(r"def _\([^)]*\):\n")
_MD_CELL = re.compile(
    r'^mo\.md\(\s*[rf]?(?:"""|\'\'\')(.*?)(?:"""|\'\'\')\s*\)\s*$', re.S
)


def parse_cells(source: str) -> list[dict]:
    """Extract each cell's authored source in document order.

    The exported page renders one ``.marimo-cell`` per ``@app.cell`` in file
    order, so the widget can map a clicked cell to ``cells[index]``. Markdown
    cells return their prose; other cells return their code. This gives the
    tutor the real source even for code cells (whose rendered DOM is empty or
    virtualized) and exact LaTeX for markdown.
    """
    cells: list[dict] = []
    for block in _CELL_SPLIT.split(source)[1:]:
        m = _DEF_LINE.search(block)
        if not m:
            continue
        # Take the indented function body, stopping at the first dedent.
        body_lines = []
        for line in block[m.end():].split("\n"):
            if line.startswith("    "):
                body_lines.append(line[4:])
            elif line.strip() == "":
                body_lines.append("")
            else:
                break
        while body_lines and not body_lines[-1].strip():
            body_lines.pop()
        while body_lines and body_lines[-1].strip().startswith("return"):
            body_lines.pop()
        while body_lines and not body_lines[-1].strip():
            body_lines.pop()
        text = "\n".join(body_lines).strip("\n")
        md = _MD_CELL.match(text)
        if md:
            cells.append({"kind": "markdown", "text": textwrap.dedent(md.group(1)).strip("\n")})
        else:
            cells.append({"kind": "code", "text": text})
    return cells


def tutor_config(name: str) -> dict:
    """Per-chapter config injected for the tutor widget (context + starters)."""
    context_file = CHAPTERS_DIR / f"{name}.context.md"
    starters_file = CHAPTERS_DIR / f"{name}.starters.txt"
    context = context_file.read_text(encoding="utf-8").strip() if context_file.exists() else ""
    starters: list[str] = []
    if starters_file.exists():
        starters = [s.strip() for s in starters_file.read_text(encoding="utf-8").splitlines() if s.strip()]
    cells = parse_cells((CHAPTERS_DIR / f"{name}.py").read_text(encoding="utf-8"))
    return {
        "chapter": pretty(name),
        "context": context,
        "starters": starters,
        "cells": cells,
    }



def inject_tutor(page: Path, name: str) -> None:
    """Inject the per-chapter config and chrome-hiding into a page.

    The floating JS tutor has been retired — the in-notebook playground is the
    only AI surface. We still inject ``window.TUTOR_CONFIG`` because the
    playground's main-thread bridge reads its ``cells`` list for the cell picker.
    """
    html = page.read_text(encoding="utf-8")
    config = json.dumps(tutor_config(name))
    head = LOADING_CSS + KATEX_CSS + MARIMO_CHROME_CSS + "</head>"
    body = (
        f"<script>window.TUTOR_CONFIG = {config};</script>"
        + PLOTLY_GUARD_JS
        + MATH_RENDER_JS
        + MARIMO_HIDE_JS
        + LOADING_JS
        + "</body>"
    )
    if "</head>" not in html or "</body>" not in html:
        raise ValueError(f"missing </head> or </body> in {page}")
    html = html.replace("</head>", head, 1).replace("</body>", body, 1)
    # Splash goes right after the opening <body> tag so it paints before the
    # WASM runtime boots. A callable replacement inserts the markup literally
    # (no backslash/group-ref processing); tolerates body attributes.
    overlay = _loading_overlay(name)
    html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + overlay, html, count=1)
    page.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# ?diag=1 load-time diagnostic overlay.
#
# Pyodide does the bulk of its work in a Web Worker AFTER the main document's
# `load` event fires, so the browser's normal indicators don't reflect what's
# really happening. This overlay captures three slowness sources:
#
#   1. Network — hooks window.fetch to log every request with bytes + duration
#      (wheels, Pyodide bootstrap, anywidget esm.sh modules).
#   2. DOM milestones — MutationObserver for first marimo element, first cell,
#      first canvas, first Plotly chart.
#   3. Python-side phases — parses `[diag] <name>: <Nms>` lines from console.log
#      (emitted by the delib bootstrap; further phases can be added the same way).
#
# Visible only when the URL has `?diag=1`. Production loads are unaffected.
# ---------------------------------------------------------------------------
DIAG_SCRIPT = r"""<script>(function () {
  if (new URLSearchParams(location.search).get('diag') !== '1') return;
  function rel() { return performance.now(); }
  var events = [];
  function logEvent(name, detail) { events.push({ t: rel(), name: name, detail: detail || '' }); schedRender(); }

  // ---- DOM milestones + live cell/output timeline (main-thread visible) ----
  // Pyodide runs Python in a Web Worker but renders OUTPUT into this document,
  // so watching cells / charts / canvases appear gives a per-cell execution
  // timeline even though the Python itself is out of reach.
  var firstSeen = {};
  var last = { cells: 0, plotly: 0, canvas: 0 };
  var CELL_SEL = '[data-testid=cell], .marimo-cell, [data-cell-id]';
  function countSel(s) { try { return document.querySelectorAll(s).length; } catch (e) { return 0; } }
  function tick() {
    if (!firstSeen.dom && document.querySelector('[data-testid], iframe')) { firstSeen.dom = true; logEvent('first marimo DOM element'); }
    var cells = countSel(CELL_SEL), plotly = countSel('.js-plotly-plot, .plotly-graph-div'), canvas = countSel('canvas');
    if (cells !== last.cells) { logEvent('cells rendered: ' + cells); last.cells = cells; }
    if (plotly !== last.plotly) { logEvent('Plotly charts: ' + plotly); last.plotly = plotly; }
    if (canvas !== last.canvas) { logEvent('canvases: ' + canvas); last.canvas = canvas; }
  }
  function start() {
    logEvent('DOMContentLoaded');
    new MutationObserver(tick).observe(document.body, { childList: true, subtree: true });
    tick();
  }
  if (document.body) start(); else document.addEventListener('DOMContentLoaded', start);
  window.addEventListener('load', function () { logEvent('window load'); });
  setInterval(tick, 1000);

  // ---- Python-side [diag] lines. These also appear directly in the DevTools
  //      console (Pyodide's worker logs surface there); this hook only catches
  //      any that happen to be emitted on the main thread. ----
  var origLog = console.log.bind(console);
  console.log = function () {
    try {
      var msg = arguments[0];
      if (typeof msg === 'string' && msg.indexOf('[diag]') === 0) {
        var m = msg.match(/^\[diag\]\s+(.+?):\s+(\d+(?:\.\d+)?)\s*(ms|s)?$/);
        if (m) logEvent('py: ' + m[1], (parseFloat(m[2]) * (m[3] === 's' ? 1000 : 1)).toFixed(0) + 'ms');
      }
    } catch (e) {}
    return origLog.apply(console, arguments);
  };

  // ---- Resource Timing: what the MAIN thread loaded (pyodide.js, the .wasm,
  //      the marimo JS bundle, katex, esm.sh widget modules). Pyodide fetches
  //      its Python wheels inside the Worker; those do NOT appear here -- use
  //      the DevTools Network tab for them. transferSize 0 + a body = cached. ----
  function resourceRows() {
    var list = performance.getEntriesByType ? performance.getEntriesByType('resource') : [];
    return list.map(function (e) {
      var bytes = e.transferSize || 0, body = e.decodedBodySize || e.encodedBodySize || 0;
      return { url: shortUrl(e.name), bytes: bytes, body: body, cached: (bytes === 0 && body > 0), ms: e.duration || 0 };
    });
  }
  function shortUrl(u) { try { var p = new URL(u, location.href); return p.hostname + p.pathname; } catch (e) { return String(u).slice(0, 70); } }

  // ---- Overlay ----
  var overlay = document.createElement('div');
  overlay.id = 'ml-diag';
  overlay.style.cssText = 'position:fixed;top:8px;right:8px;width:470px;max-height:90vh;overflow:auto;background:rgba(15,18,24,0.96);color:#dfe5ed;font:11px/1.4 ui-monospace,Menlo,monospace;padding:10px 12px;border-radius:8px;z-index:2147483647;box-shadow:0 6px 28px rgba(0,0,0,0.45)';
  overlay.innerHTML =
    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">' +
      '<b style="color:#9cf">Load diagnostics (?diag=1)</b>' +
      '<button id="ml-diag-x" style="background:transparent;border:0;color:#9ab;cursor:pointer;font-size:15px">&times;</button>' +
    '</div><div data-time style="color:#9ab;margin-bottom:6px"></div><div data-events></div><div data-net></div>';
  function attach() { (document.body || document.documentElement).appendChild(overlay); overlay.querySelector('#ml-diag-x').onclick = function () { overlay.remove(); }; }
  if (document.body) attach(); else document.addEventListener('DOMContentLoaded', attach);
  setInterval(function () { var el = overlay.querySelector('[data-time]'); if (el) el.textContent = 'elapsed: ' + (rel() / 1000).toFixed(1) + 's'; }, 200);

  var sched = false;
  function schedRender() { if (sched) return; sched = true; requestAnimationFrame(function () { sched = false; render(); }); }
  function fmtMs(ms) { return ms < 1000 ? ms.toFixed(0) + 'ms' : (ms / 1000).toFixed(2) + 's'; }
  function fmtB(b) { return b < 1024 ? b + 'B' : (b < 1048576 ? (b / 1024).toFixed(1) + 'KB' : (b / 1048576).toFixed(2) + 'MB'); }
  function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }
  function render() {
    var ee = overlay.querySelector('[data-events]');
    if (ee) ee.innerHTML = '<b style="color:#9cf">Timeline</b>' + events.map(function (e) {
      return '<div><span style="color:#fc9">' + (e.t / 1000).toFixed(2) + 's</span>  ' + esc(e.name) + (e.detail ? '  <span style="color:#9ab">' + esc(e.detail) + '</span>' : '') + '</div>';
    }).join('');
    var rows = resourceRows().sort(function (a, b) { return (b.bytes || b.body) - (a.bytes || a.body); }).slice(0, 25);
    var ne = overlay.querySelector('[data-net]');
    if (ne) ne.innerHTML =
      '<b style="color:#9cf;display:block;margin-top:8px">Main-thread resources (top 25)</b>' +
      '<div style="color:#c98;margin-bottom:3px">Pyodide wheels download inside a Worker &mdash; they are NOT here. Use DevTools &rarr; Network for those.</div>' +
      rows.map(function (n) {
        return '<div><span style="color:#fc9">' + (n.cached ? 'cache' : fmtB(n.bytes)) + '</span>  <span style="color:#9ab">' + fmtMs(n.ms) + '</span>  ' + esc(n.url) + '</div>';
      }).join('');
  }
  setTimeout(function () {
    console.group('[diag] snapshot @45s');
    console.table(events);
    console.table(resourceRows().sort(function (a, b) { return b.body - a.body; }).slice(0, 40));
    console.groupEnd();
  }, 45000);
  setTimeout(render, 50);
})();</script>"""


def inject_diag(page: Path) -> None:
    """Insert the ?diag=1 load-time instrumentation into a chapter page.

    Invisible unless the URL contains ?diag=1; safe to ship to production.
    Adds the overlay just before </body> so it doesn't compete with marimo's
    runtime boot for parse time.
    """
    html = page.read_text(encoding="utf-8")
    if "</body>" not in html:
        return
    html = html.replace("</body>", DIAG_SCRIPT + "</body>", 1)
    page.write_text(html, encoding="utf-8")


def patch_plotly_assets() -> None:
    """Null-guard marimo's bundled Plotly ``doAutoMargin`` at the source.

    It does ``J._fullLayout._redrawFromAutoMarginCount++`` without checking
    that ``_fullLayout`` exists, which throws (non-fatally) when a chart is
    resized before it's drawn. We insert an early ``if(!J||!J._fullLayout)
    return;`` guard into the vendored ``Plot-*.js``. Idempotent. Warns (does
    not fail) if the anchor moves in a future marimo release — the
    PLOTLY_GUARD_JS console filter is the version-independent backstop.
    """
    anchor = "doAutoMargin=function(J){var st=J._fullLayout,"
    guard = "doAutoMargin=function(J){if(!J||!J._fullLayout)return;var st=J._fullLayout,"
    n = 0
    for js in SITE.glob("*/assets/Plot-*.js"):
        text = js.read_text(encoding="utf-8")
        if guard in text:
            continue  # already patched
        if anchor in text:
            js.write_text(text.replace(anchor, guard), encoding="utf-8")
            n += 1
    if n:
        print(f"Patched Plotly doAutoMargin guard in {n} asset file(s).")
    else:
        print("NOTE: Plotly doAutoMargin anchor not found; relying on the "
              "PLOTLY_GUARD_JS console filter.", file=sys.stderr)


def _is_lab(slug: str) -> bool:
    return slug.startswith("ch99") or "animation_lab" in slug


def build_index(names: list[str]) -> str:
    """Render the landing page from web/landing.html.

    Injects: the absolute base URL (share cards), the start/lab links, the
    'Read it now' cards (built chapters in reading order), and the full
    five-part roadmap with available chapters linked. Falls back to a bare
    chapter list if the template is missing.
    """
    built = set(names)
    chapters = [n for n in names if not _is_lab(n)]
    lab = next((n for n in names if _is_lab(n)), None)
    start_href = chapters[0] if chapters else (names[0] if names else "")
    lab_href = lab or start_href

    template_path = WEB / "landing.html"
    if not template_path.exists():
        # minimal fallback — keeps the build working without the template
        items = "\n".join(f'  <li><a href="./{n}/">{pretty(n)}</a></li>' for n in names)
        return ("<!doctype html><meta charset=utf-8>"
                "<title>Differential Equations</title>"
                f"<h1>Differential Equations</h1><ul>{items}</ul>")

    # 'Read it now' cards — built chapters in reading order, nice titles.
    card_li = []
    for slug in chapters:
        label, title = CHAPTER_CARDS.get(slug, ("Chapter", pretty(slug)))
        card_li.append(
            f'        <li class="card"><a href="./{slug}/">'
            f'<span class="n">{label}</span>'
            f'<span class="t">{title}</span></a></li>'
        )
    available_html = "\n".join(card_li)

    # The five-part roadmap; built chapters become links, the rest grey chips.
    parts_html = []
    for part_title, part_sub, entries in ROADMAP_PARTS:
        chips = []
        for title, slug in entries:
            if slug and slug in built:
                chips.append(
                    f'<li class="chip done"><a href="./{slug}/">'
                    f'<span class="mark">✓</span> {title}</a></li>'
                )
            else:
                chips.append(f'<li class="chip todo">{title}</li>')
        parts_html.append(
            f'      <div class="part">\n'
            f'        <h3>{part_title} <small>· {part_sub}</small></h3>\n'
            f'        <ul class="chips">\n          '
            + "\n          ".join(chips)
            + f'\n        </ul>\n      </div>'
        )
    roadmap_html = "\n".join(parts_html)

    html = template_path.read_text(encoding="utf-8")
    return (
        html.replace("__BASE_URL__", SITE_BASE_URL)
        .replace("__START_HREF__", start_href)
        .replace("__LAB_HREF__", lab_href)
        .replace("__AVAILABLE_CHAPTERS__", available_html)
        .replace("__ROADMAP__", roadmap_html)
    )


def main() -> int:
    nbs = chapters()
    if not nbs:
        print("No chapter notebooks found.", file=sys.stderr)
        return 1

    SITE.mkdir(parents=True, exist_ok=True)

    # Copy pre-rendered media (Manim clips, etc.) so delib.video() can find them.
    if ASSETS_DIR.is_dir():
        import shutil

        shutil.copytree(ASSETS_DIR, SITE / "assets", dirs_exist_ok=True)

    names = [nb.stem for nb in nbs]
    for idx, nb in enumerate(nbs):
        name = nb.stem
        print(f"Exporting {nb.name} -> site/{name}/")
        export(nb, SITE / name)
        inject_tutor(SITE / name / "index.html", name)
        inject_nav(SITE / name / "index.html", names, idx)
        inject_diag(SITE / name / "index.html")

    patch_plotly_assets()

    (SITE / "index.html").write_text(build_index(names), encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built site with {len(names)} chapter(s) at {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
