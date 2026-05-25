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
#     "numpy",
#     "scipy",
#     "matplotlib",
#     "plotly",
# ]
# ///
"""

WEB_ASSETS = ["tutor.js", "tutor.css"]


def chapters() -> list[Path]:
    return sorted(p for p in CHAPTERS_DIR.glob("*.py") if not p.name.startswith("_"))


def delib_bootstrap() -> str:
    parts = ["from __future__ import annotations"]
    for mod in DELIB_MODULES:
        src = (DELIB_DIR / f"{mod}.py").read_text()
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
    transformed = PEP723_HEADER + inline_delib(notebook.read_text())
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / notebook.name
        staged.write_text(transformed)
        subprocess.run(
            ["marimo", "export", "html-wasm", str(staged), "-o", str(out_dir), "--mode", "edit"],
            check=True,
        )


def pretty(name: str) -> str:
    """ch01_first_order_odes -> 'Ch01 — First Order Odes'."""
    head, _, tail = name.partition("_")
    return f"{head.capitalize()} — {tail.replace('_', ' ').title()}"


def tutor_config(name: str) -> dict:
    """Per-chapter config injected for the tutor widget (context + starters)."""
    context_file = CHAPTERS_DIR / f"{name}.context.md"
    starters_file = CHAPTERS_DIR / f"{name}.starters.txt"
    context = context_file.read_text().strip() if context_file.exists() else ""
    starters: list[str] = []
    if starters_file.exists():
        starters = [s.strip() for s in starters_file.read_text().splitlines() if s.strip()]
    return {"chapter": pretty(name), "context": context, "starters": starters}


def inject_tutor(page: Path, name: str) -> None:
    """Inject the tutor stylesheet, per-chapter config, and script into a page."""
    html = page.read_text()
    config = json.dumps(tutor_config(name))
    head = '<link rel="stylesheet" href="../tutor.css" /></head>'
    body = (
        f"<script>window.TUTOR_CONFIG = {config};</script>"
        '<script src="../tutor.js"></script></body>'
    )
    if "</head>" not in html or "</body>" not in html:
        raise ValueError(f"missing </head> or </body> in {page}")
    html = html.replace("</head>", head, 1).replace("</body>", body, 1)
    page.write_text(html)


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
        (SITE / asset).write_text((WEB_DIR / asset).read_text())

    names: list[str] = []
    for nb in nbs:
        name = nb.stem
        names.append(name)
        print(f"Exporting {nb.name} -> site/{name}/")
        export(nb, SITE / name)
        inject_tutor(SITE / name / "index.html", name)

    (SITE / "index.html").write_text(build_index(names))
    (SITE / ".nojekyll").write_text("")
    print(f"Built site with {len(names)} chapter(s) at {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
