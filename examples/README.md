# Standalone notebooks (`uv run`)

These are single-file marimo notebooks that bundle everything they need
inline — no local package install, no virtualenv, no clone-and-pip. Anyone
with [uv](https://docs.astral.sh/uv/) can run one with **two commands**:

```sh
curl -O https://raw.githubusercontent.com/Chipmunk91/Math_learn/main/examples/spotlight_resonance.py
uvx marimo edit --sandbox spotlight_resonance.py
```

`uvx` (= `uv tool run`) installs marimo into a temporary tool env and
runs it. The `--sandbox` flag tells marimo to read the PEP 723 header at
the top of the file and provision a *second* ephemeral venv with the
notebook's own dependencies (numpy, sympy, plotly, anywidget). Nothing is
installed on your machine outside those temp venvs; the first launch
takes about 30 seconds to populate them, then it's snappy.

> **Common gotcha.** `uv run marimo edit …` looks like the natural
> command, but it fails with *"program not found"*. That's because
> `uv run <cmd>` doesn't install `<cmd>` — it expects `marimo` to be on
> PATH already. The recipe above (`uvx marimo edit --sandbox …`) is the
> uv-idiomatic way to launch a sandboxed marimo notebook.

On Windows PowerShell the download line is the same (`curl.exe -O …`);
the rest is identical.

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
