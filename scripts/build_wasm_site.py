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
#     "scipy",
#     "sympy",
#     "matplotlib",
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
    return (
        "    import base64 as _b64, sys as _sys, types as _types\n"
        '    _delib = _types.ModuleType("delib")\n'
        f'    _delib_src = _b64.b64decode("{encoded}").decode("utf-8")\n'
        '    exec(compile(_delib_src, "delib (inlined for WASM)", "exec"), _delib.__dict__)\n'
        '    _sys.modules["delib"] = _delib\n'
        "    import delib\n"
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
    head = KATEX_CSS + MARIMO_CHROME_CSS + "</head>"
    body = (
        f"<script>window.TUTOR_CONFIG = {config};</script>"
        + MATH_RENDER_JS
        + MARIMO_HIDE_JS
        + "</body>"
    )
    if "</head>" not in html or "</body>" not in html:
        raise ValueError(f"missing </head> or </body> in {page}")
    html = html.replace("</head>", head, 1).replace("</body>", body, 1)
    page.write_text(html, encoding="utf-8")


def build_index(names: list[str]) -> str:
    cards = "\n".join(
        f"""      <li class="card">
        <a href="./{n}/">{pretty(n)}</a>
      </li>"""
        for n in names
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Math Learn — Differential Equations</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 40rem; margin: 3rem auto;
           padding: 0 1.25rem; line-height: 1.5; color: #1d2733; }}
    h1 {{ font-size: 1.6rem; }}
    ul {{ list-style: none; padding: 0; }}
    .card {{ border: 1px solid #d6dde6; border-radius: 0.6rem; margin: 0.6rem 0; }}
    .card a {{ display: block; padding: 0.9rem 1rem; text-decoration: none;
               font-weight: 600; color: #2a5d9c; }}
    .card a:active, .card a:hover {{ background: #f5f8fc; }}
    p {{ color: #56636f; }}
  </style>
</head>
<body>
  <h1>Differential Equations Playground</h1>
  <p>Interactive chapters that run entirely in your browser — drag the sliders,
     play the animations, and ask the in-notebook playground to write and run code.</p>
  <p>Each chapter reads top-to-bottom; expand any cell to edit and re-run its
     code right in the browser.</p>
  <ul>
{cards}
  </ul>
</body>
</html>
"""


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

    (SITE / "index.html").write_text(build_index(names), encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built site with {len(names)} chapter(s) at {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
