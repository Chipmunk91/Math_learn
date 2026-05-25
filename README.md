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
