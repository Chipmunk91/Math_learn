# Curriculum Roadmap — Differential Equations

The course teaches differential equations the way you can *see* them: every idea
is anchored to an interactive picture of the flow. The arc follows Strogatz's
*Nonlinear Dynamics and Chaos* (1D flows → 2D phase plane → chaos), because that
progression is exactly what the slope-field / vector-field / flow / phase-portrait
visuals we've built are best at.

This file is the backlog. Each chapter is a self-contained marimo notebook that
ships to a static WASM page; scaling the site means working down this list, not
redesigning anything.

---

## The chapter template — a narrative arc

Every chapter tells a story: start from something real, build the math from it,
play with it, then visualize and practice. Concrete first, formalism second.

1. **Hook** — a real-world observation/case study + a picture, posing the question.
   (Ch1: a rumor spreading across a 1,000-person campus → the S-curve.)
2. **Build the model** — reason from the phenomenon to the equation, justifying
   each term, landing on the chapter's ODE.
3. **Play with the symbols** — manipulate the formalism live: `delib.equilibria_report`
   solves `dy/dt = 0` with SymPy and classifies stability as the student edits the
   rate law.
4. **See it** — the `delib` Plotly visuals: static field → `param_panel` sliders →
   `flow_field` animation (particles riding the field). 3-D where it earns its place.
5. **Try it** — interactive code grounds: each task is AI-assist (`delib.ai_code`,
   coach mode) → editable code → output → auto-eval (`delib.run_exercise`).
6. **Playground** — an open, ungraded sandbox: editable code + ✨ AI assist + Run.

The tutor sidebar (chat, BYO-key) is always present alongside, for free-form help.

## Conventions

- **Files:** `differential_equations/chapters/chNN_topic.py` (sorted by `NN`),
  plus `chNN_topic.context.md` (tutor system context) and optional
  `chNN_topic.starters.txt`. Names starting with `_` or `zz_` are not built.
- **Shared code only via `delib`.** Chapters never import one another.
- **Run mode + light Plotly** everywhere, so it auto-runs, is read-only, and the
  charts match. Prefer `*_plotly` helpers; the tutor is told to do the same.
- **Animations:** static content in the base figure, only moving traces in frames
  (keeps output small — see the `flow_field` pattern).
- **Math is checkable:** lean on `solve_ode`/numerics so a wrong formula shows up
  as a wrong-looking picture; add a `delib` unit test when you add a helper.

---

## The arc

### Part I — Flows on the line (1-D)

| Ch | Title | Learning goals | Worked example | Primary visual | `delib` |
|----|-------|----------------|----------------|----------------|---------|
| 01 | First-order ODEs & slope fields | Read a field as every solution at once; equilibria as flat stripes | Logistic $y'=ay(1-y/K)$ | vector field + particle flow | ✅ done |
| 02 | Separable & linear first-order | Solve in closed form; check the formula against the field | $y'=ay$, mixing tank | field + exact-vs-numerical overlay | uses existing |
| 03 | Fixed points & stability (the phase line) | Classify equilibria; stability from $f'$; potential $V$ with $f=-V'$ | $\dot x = x - x^3$ | **1-D phase line** + potential well | 🔨 `phase_line`, `potential_plot` |
| 04 | Bifurcations in 1-D | Saddle-node, transcritical, pitchfork; read a bifurcation diagram | $\dot x = r + x^2$; $\dot x = rx - x^3$ | **bifurcation diagram** (sweep $r$) | 🔨 `bifurcation_diagram` |
| 05 | Flows on the circle | Oscillators; uniform vs non-uniform; the bottleneck near $\dot\theta=0$ | $\dot\theta = \omega - a\sin\theta$ | **flow on a circle** | 🔨 `circle_flow` |

### Part II — The phase plane (2-D systems)

| Ch | Title | Learning goals | Worked example | Primary visual | `delib` |
|----|-------|----------------|----------------|----------------|---------|
| 06 | Linear 2-D systems | Eigenvalues → node / saddle / spiral / center; eigen-directions | $\dot{\mathbf x}=A\mathbf x$ | **2-D phase portrait** + trajectories | 🔨 `phase_portrait_plotly` |
| 07 | Nonlinear phase portraits | Nullclines; linearize at fixed points; classify | Competing species; pendulum | vector field + **nullclines** + flow | 🔨 `nullclines` |
| 08 | Limit cycles | Closed orbits; Poincaré–Bendixson; relaxation oscillation | Van der Pol | trajectories spiralling onto a **limit cycle** (animated) | uses 06–07 + flow |
| 09 | Bifurcations in 2-D | Hopf bifurcation: a fixed point births a cycle | $\dot r = \mu r - r^3,\ \dot\theta=\omega$ | phase portrait swept over $\mu$ | uses 06 + slider |

### Part III — Chaos

| Ch | Title | Learning goals | Worked example | Primary visual | `delib` |
|----|-------|----------------|----------------|----------------|---------|
| 10 | The Lorenz equations | Strange attractors; sensitive dependence on initial conditions | Lorenz system | **3-D trajectory** (Scatter3d), two near-identical starts diverging | 🔨 `trajectory_3d` (+ `solution_surface` ✅) |
| 11 | One-dimensional maps | Iteration, cobwebs, period-doubling route to chaos | Logistic map $x_{n+1}=rx_n(1-x_n)$ | **cobweb** + **orbit diagram** | 🔨 `cobweb`, `orbit_diagram` |
| 12 | Fractals *(capstone, optional)* | Self-similarity; fractal dimension | Cantor set; logistic-map orbit diagram zoom | iterated-map imagery | 🔨 `iterate_map` |

Legend: ✅ exists · 🔨 new `delib` helper to build.

---

## `delib` helpers to build (ordered by first use)

These extend the current toolkit (`slope_field*`, `vector_field_plotly`,
`flow_field`, `solution_surface`, `solve_ode/solve_system`, `param_panel`). Each
should be light-theme Plotly, self-contained (no cross-module imports, for WASM
inlining), and animation-safe (static content in base, moving content in frames).

- **`phase_line(f, xrange)`** — 1-D flow on a line: fixed points (filled = stable,
  open = unstable) with arrows between them. *(Ch 03)*
- **`potential_plot(f, xrange)`** — the potential $V$ with $f=-V'$; a ball rolling
  downhill. *(Ch 03)*
- **`bifurcation_diagram(make_f, r_range, xrange)`** — stable/unstable branches of
  fixed points vs a parameter. *(Ch 04)*
- **`circle_flow(f, ...)`** — flow on $S^1$ with a moving point. *(Ch 05)*
- **`phase_portrait_plotly(F, xlim, ylim)`** — 2-D vector field + a few seeded
  trajectories (the 2-D analogue of `vector_field_plotly`). *(Ch 06)*
- **`nullclines(F, xlim, ylim)`** — $\dot x=0$ and $\dot y=0$ curves over the field.
  *(Ch 07)*
- **`trajectory_3d(F, t_span, starts)`** — animated 3-D `Scatter3d` trajectories
  for chaos. *(Ch 10)*
- **`cobweb(g, x0, n)`** and **`orbit_diagram(make_g, r_range)`** — for maps.
  *(Ch 11)*

---

## Status

- **Ch 01** — built (field, sliders, particle flow, playground). The template.
- **Ch 02–12** — to author against this roadmap.
- Cross-cutting features in flight (other sessions): chapter **navigation**.

When packaging the playground into a reusable `delib.playground(context)` lands,
adding it to a new chapter becomes one line — so the per-chapter work is mostly
the math content + choosing the right visual from the table above.
