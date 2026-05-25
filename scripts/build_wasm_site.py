#!/usr/bin/env python3
"""Export every chapter notebook to interactive WASM HTML and build a landing page.

Produces a static, mobile-friendly site under ``site/``:

    site/
      index.html            # links to each chapter
      .nojekyll
      <chapter-name>/        # one WASM-exported notebook per chapter

The exported notebooks run entirely in the browser via Pyodide, so the site
needs no server and works from a phone.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = REPO / "differential_equations" / "chapters"
SITE = REPO / "site"


def chapters() -> list[Path]:
    """All chapter notebooks except files starting with an underscore (template)."""
    return sorted(p for p in CHAPTERS_DIR.glob("*.py") if not p.name.startswith("_"))


def export(notebook: Path, out_dir: Path) -> None:
    subprocess.run(
        [
            "marimo", "export", "html-wasm",
            str(notebook),
            "-o", str(out_dir),
            "--mode", "run",
        ],
        check=True,
    )


def pretty(name: str) -> str:
    """ch01_first_order_odes -> 'Ch01 — First Order Odes'."""
    head, _, tail = name.partition("_")
    return f"{head.capitalize()} — {tail.replace('_', ' ').title()}"


def build_index(names: list[str]) -> str:
    items = "\n".join(
        f'      <li><a href="./{n}/">{pretty(n)}</a></li>' for n in names
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
    li {{ margin: 0.6rem 0; }}
    a {{ display: block; padding: 0.9rem 1rem; border: 1px solid #d6dde6;
         border-radius: 0.6rem; text-decoration: none; color: #2a5d9c; font-weight: 600; }}
    a:active, a:hover {{ background: #f2f6fb; }}
    p {{ color: #56636f; }}
  </style>
</head>
<body>
  <h1>Differential Equations Playground</h1>
  <p>Interactive chapters that run entirely in your browser — drag the sliders,
     play the animations. Tap a chapter to begin.</p>
  <ul>
{items}
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
    names: list[str] = []
    for nb in nbs:
        name = nb.stem
        names.append(name)
        print(f"Exporting {nb.name} -> site/{name}/")
        export(nb, SITE / name)

    (SITE / "index.html").write_text(build_index(names))
    (SITE / ".nojekyll").write_text("")
    print(f"Built site with {len(names)} chapter(s) at {SITE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
