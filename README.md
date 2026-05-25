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

## AI assistant (in-notebook, for live sessions)

marimo has a built-in AI assistant that can answer questions and **generate or
edit cells in natural language** while you work — the session-oriented learning
companion. The project is preconfigured to use Claude (see
`[tool.marimo.ai.models]` in `pyproject.toml`); you only supply a key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # marimo reads this; never commit it
uv run marimo edit differential_equations/chapters/ch01_first_order_odes.py
```

Then inside the notebook, use the cell's **AI / sparkle** action to generate or
rewrite a cell from a prompt, or open the **chat panel** to ask about the
concept you're on. To use a stronger model, change the model id in
`pyproject.toml` (e.g. `anthropic/claude-opus-4-7`).

> This is the *live-session* lever (#2). Adding new chapters and library
> code across DE and the broader math curriculum is the *agentic* lever (#1):
> ask Claude Code to edit the notebooks/`delib`, which then auto-rebuilds the
> deployed pages via CI.

## Live preview (mobile-friendly)

Every push builds each chapter into a self-contained **WASM** page (runs in the
browser via Pyodide — interactive sliders and animations, no server) and
publishes them to GitHub Pages, so you can open a chapter from any device.

One-time setup: in the repo, go to **Settings → Pages → Build and deployment →
Source** and select **GitHub Actions**. After the next push, the
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
      ch01_first_order_odes.py   # worked reference chapter
      _template.py               # copy this to start a new chapter
    tests/
    assets/                   # exported gifs/mp4 (gitignored except *_sample.*)
```

## Adding a chapter

Copy `differential_equations/chapters/_template.py`, rename it
`chNN_<topic>.py`, and fill in the six fixed sections (title/goals, concept,
interactive exploration, time animation, "try it", recap). Chapters import only
from `delib` and the standard stack — never from each other.

## Notes

- `delib` lives inside `differential_equations/` but installs as a top-level
  `delib` package, so notebooks and tests can `import delib` from anywhere.
- Inline animation uses plotly (real play/pause). `delib.animate.animate_time`
  builds a matplotlib `FuncAnimation` for exporting gifs/mp4 to `assets/`.
