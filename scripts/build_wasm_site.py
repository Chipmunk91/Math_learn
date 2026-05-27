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
import hashlib
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
WEB_DIR = REPO / "web"
SITE = REPO / "site"

# delib is a locally-installed package and does not exist in the browser's
# Pyodide runtime. For the WASM build we inline its source into each notebook so
# the exported page is self-contained.
DELIB_MODULES = ["solvers", "fields", "animate", "ui"]
_FUTURE = re.compile(r"^from __future__ import .*$", re.MULTILINE)

PEP723_HEADER = """\
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "anywidget",
#     "numpy",
#     "scipy",
#     "matplotlib",
#     "plotly",
# ]
# ///
"""

WEB_ASSETS = ["tutor.js", "tutor.css"]

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
    '"fix with ai","ai completion","sql","add sql cell","convert to sql"];'
    'function norm(s){return (s||"").replace(/\\s+/g," ").trim().toLowerCase();}'
    "function sweep(){"
    'var ns=document.querySelectorAll(\'button,[role="menuitem"],a[role="menuitem"]\');'
    "for(var i=0;i<ns.length;i++){var n=ns[i];if(n.dataset.mlHidden)continue;"
    'var label=norm(n.getAttribute("aria-label"))||norm(n.textContent);'
    'if(LABELS.indexOf(label)!==-1){n.style.display="none";n.dataset.mlHidden="1";}}}'
    "var pend=false;function schedule(){if(pend)return;pend=true;"
    "requestAnimationFrame(function(){pend=false;sweep();});}"
    "function start(){new MutationObserver(schedule).observe(document.body,"
    "{childList:true,subtree:true});sweep();}"
    'if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",start);}'
    "else{start();}"
    "})();</script>"
)


def chapters() -> list[Path]:
    return sorted(p for p in CHAPTERS_DIR.glob("*.py") if not p.name.startswith("_"))


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
    pattern = re.compile(r"^[ \t]*import delib[ \t]*$", re.MULTILINE)
    if not pattern.search(source):
        raise ValueError("expected a standalone `import delib` line to inline")
    return pattern.sub(delib_bootstrap().rstrip("\n"), source, count=1)


def export(notebook: Path, out_dir: Path) -> None:
    """Export a chapter to a single WASM HTML page (edit mode, code hidden)."""
    transformed = PEP723_HEADER + inline_delib(notebook.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / notebook.name
        staged.write_text(transformed, encoding="utf-8")
        subprocess.run(
            [sys.executable, "-m", "marimo", "export", "html-wasm", str(staged), "-o", str(out_dir), "--mode", "edit"],
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


def asset_version(filename: str) -> str:
    """Short content hash so deploys bust the browser cache for our assets."""
    return hashlib.md5((WEB_DIR / filename).read_bytes()).hexdigest()[:8]


def inject_tutor(page: Path, name: str) -> None:
    """Inject the tutor stylesheet, per-chapter config, and script into a page."""
    html = page.read_text(encoding="utf-8")
    config = json.dumps(tutor_config(name))
    css_v = asset_version("tutor.css")
    js_v = asset_version("tutor.js")
    head = (
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous" />'
        '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>'
        '<link rel="stylesheet" href="../tutor.css?v=' + css_v + '" />'
        + MARIMO_CHROME_CSS
        + "</head>"
    )
    body = (
        f"<script>window.TUTOR_CONFIG = {config};</script>"
        + MARIMO_HIDE_JS
        + '<script src="../tutor.js?v=' + js_v + '"></script></body>'
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
     play the animations, and ask the built-in tutor (tap the 💬 icon).</p>
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
    for asset in WEB_ASSETS:
        (SITE / asset).write_text((WEB_DIR / asset).read_text(encoding="utf-8"), encoding="utf-8")

    names: list[str] = []
    for nb in nbs:
        name = nb.stem
        names.append(name)
        print(f"Exporting {nb.name} -> site/{name}/")
        export(nb, SITE / name)
        inject_tutor(SITE / name / "index.html", name)

    (SITE / "index.html").write_text(build_index(names), encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built site with {len(names)} chapter(s) at {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
