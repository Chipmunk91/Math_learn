# Math Learn — interactive playground

An interactive, animated, chapter-based playground for learning math. Each
chapter is a self-contained [marimo](https://marimo.io) notebook: change a
slider, watch the field / phase portrait / solution respond instantly.

The first subject is **differential equations**, under
[`differential_equations/`](differential_equations/).

## Quickstart

```bash
uv sync                       # create the env and install deps + delib
uv run pytest                 # run the library tests
uv run marimo edit differential_equations/chapters/ch01_first_order_odes.py
```

Dragging the `a`, `K`, and `y₀` sliders in chapter 1 reshapes the slope field
and moves the solution curve in real time; the time animation plays with native
play/pause.

## AI tutor (in-page, bring-your-own-key)

Every published chapter has a built-in Socratic tutor — tap the **💬** icon to
open a chat that already knows the chapter (its equation, parameters, and
exercises). Highlight a passage before opening it and the tutor scopes its help
to that selection; otherwise it answers about the whole chapter.

It's **bring-your-own-key**: each visitor pastes their own Anthropic API key,
which is held only in that browser tab for the session (cleared when the tab
closes) and sent **directly** to Anthropic. The key never reaches any server,
and each visitor pays for their own usage — so the static site costs the owner
nothing to host.

The widget is plain, dependency-free JS in [`web/`](web/) (`tutor.js` +
`tutor.css`), injected into each exported chapter by the build. Per-chapter
grounding comes from two sidecar files next to the notebook:
`chNN_<topic>.context.md` (what the tutor knows) and
`chNN_<topic>.starters.txt` (suggested opening prompts, one per line).

## Live preview (mobile-friendly)

Every push builds each chapter into a self-contained **WASM** page (runs in the
browser via Pyodide — interactive sliders and animations, no server). Pushes to
`main` also **publish** the site to GitHub Pages, so you can open a chapter from
any device. Each chapter page gets a top bar to step to the previous / next
chapter or jump back to the index, and the index lists every chapter.

Feature-branch pushes only run the build (as a CI check) — they do **not**
deploy, so the live site always reflects `main`. To see a branch's changes,
use the local preview below or merge to `main`.

One-time setup: in the repo, go to **Settings → Pages → Build and deployment →
Source** and select **GitHub Actions**. After the next push to `main`, the
`Deploy WASM playground to Pages` workflow publishes the site; its run page
shows the URL (typically `https://<owner>.github.io/<repo>/`).

To build the static site locally:

```bash
uv run python scripts/build_wasm_site.py   # output in ./site
python -m http.server --directory site     # then open the printed URL
```

## Layout

```
math_learn/
  pyproject.toml              # uv-managed; delib is installed as a package
  differential_equations/
    delib/                    # the ONLY shared code between chapters
      solvers.py              # solve_ode / solve_system  (solve_ivp wrappers)
      fields.py               # slope_field / vector_field / phase_portrait
      animate.py              # plotly play/pause + matplotlib export
      ui.py                   # standardized marimo sliders
    chapters/
      ch01_first_order_odes.py            # worked reference chapter
      ch01_first_order_odes.context.md    # what the tutor knows about it
      ch01_first_order_odes.starters.txt  # suggested tutor prompts
      _template.py                        # copy this to start a new chapter
    tests/
    assets/                   # exported gifs/mp4 (gitignored except *_sample.*)
  web/                        # in-page tutor widget (tutor.js + tutor.css)
  scripts/build_wasm_site.py  # exports chapters to WASM + injects the tutor
```

## Adding a chapter

Copy `differential_equations/chapters/_template.py`, rename it
`chNN_<topic>.py`, and fill in the six fixed sections (title/goals, concept,
interactive exploration, time animation, "try it", recap). Chapters import only
from `delib` and the standard stack — never from each other.

For the tutor, add two sidecars next to it: `chNN_<topic>.context.md` (a plain
summary of the equation, parameters, on-screen widgets, and exercises) and
`chNN_<topic>.starters.txt` (a few suggested prompts, one per line). Both are
optional; without them the tutor still works with just the chapter title.

## Notes

- `delib` lives inside `differential_equations/` but installs as a top-level
  `delib` package, so notebooks and tests can `import delib` from anywhere.
- Inline animation uses plotly (real play/pause). `delib.animate.animate_time`
  builds a matplotlib `FuncAnimation` for exporting gifs/mp4 to `assets/`.
