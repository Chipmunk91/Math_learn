# Standalone notebooks (`uv run`)

These are single-file marimo notebooks that bundle everything they need
inline — no local package install, no virtualenv, no clone-and-pip. Anyone
with [uv](https://docs.astral.sh/uv/) can run one with **one command**:

```sh
uv run marimo edit examples/spotlight_resonance.py
```

uv reads the PEP 723 `# /// script` header at the top of the file, builds a
temporary venv with the listed dependencies, and launches marimo with the
notebook open. Nothing is installed on your machine outside that venv.

## What's here

| File | Subject | Source chapter |
|---|---|---|
| [`spotlight_resonance.py`](spotlight_resonance.py) | A child on a swing — drag-the-mass, audible resonance, transient + steady-state choreography, and the full $A(\omega)$ / $\varphi(\omega)$ frequency-response story for the damped driven oscillator. | `differential_equations/chapters/ch07_damping_forcing_resonance.py` |

## Where these files come from

Each file in this directory is **auto-generated** from a chapter in the
main course (`differential_equations/chapters/`) by
`scripts/build_wasm_site.py`. The build inlines our local `delib` package
(every helper, widget, and Manim-rendered video) directly into the
notebook, then prepends the PEP 723 header so `uv run` can pick it up.

That means:

- **Do not edit files in `examples/` by hand.** They get overwritten on
  every site build. Edit the source chapter instead.
- A CI guard (`python scripts/build_wasm_site.py --check-examples`) refuses
  to deploy if any file here has drifted from its source — so the version
  you see in this repo is always in sync with the chapter that produced it.

## The full course

These standalone notebooks are a tiny slice. The whole course runs in the
browser (no install at all) at
**<https://chipmunk91.github.io/Math_learn/>** — eight chapters spanning
slope fields, separable & linear, exact equations, integrating factors,
numerical methods, fixed-point stability, second-order ODEs, damping &
resonance, plus an animation playground showcasing eleven different
in-browser rendering technologies tied to the equations underneath them.
