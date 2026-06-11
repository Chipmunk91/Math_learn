# Curriculum Roadmap — Differential Equations

This course teaches differential equations the way you can *see* them: every
idea is anchored to a story, an interactive picture, and runnable code. It
spans the full standard undergraduate DE curriculum — closed-form solution
techniques, higher-order linear systems, numerical methods, qualitative
dynamics, PDEs, and chaos — built as self-contained marimo notebooks that
ship to a static WASM site.

This file is the backlog. Scaling the site means working down this list, not
redesigning anything.

---

## The chapter template — a narrative arc

Every chapter tells a story: start from something concrete, build the math
out of it, watch it work, then practice. *Concrete first, formalism second.*
No assumed knowledge; new terms get *earned* in the prose, not declared.

1. **Hook** — a real-world observation or case study + a picture, posing the
   question. (Ch 1: a rumor across a 1,000-person campus → the S-curve.
   Ch 4: a physics engine ticking forward 60 times a second.
   Ch 5: a gene that switches a cell's state.)
2. **Build the model** — reason from the phenomenon to the equation,
   justifying each term, landing on the chapter's ODE.
3. **Derive** — the math move(s) the chapter is teaching, in the gentlest
   voice possible. Manim videos handle long symbolic derivations
   (`delib.video("name.mp4")`); short live SymPy handles the rest.
4. **Play with the symbols** — manipulate the formalism live: sliders,
   `equilibria_report`, `closed_form_report`, `solve_steps` — the student
   edits and the formula / picture updates.
5. **See it** — the `delib` Plotly visuals: static field → `param_panel`
   sliders → `flow_field` / `animate_plotly` animations. 3-D where it earns
   its place.
6. **Try it** — small, focused exercises with auto-grading
   (`delib.exercise_view(..., with_ai=False)` for step-by-step practice;
   `delib.exercise_view(..., with_ai=True)` when an AI coach helps).
7. **Playground** — an open, ungraded sandbox: editable code + ✨ AI assist
   + Run.
8. **Recap & what's next** — the chapter's punchline + a pointer to the
   next.

The tutor sidebar (chat, BYO-key, claude-sonnet-4-6 Socratic mode) is
always present for free-form help.

## Conventions

- **Files:** `differential_equations/chapters/chNN_topic.py` (sorted by
  `NN`). Multi-part chapters use `chNNa_topic.py` / `chNNb_topic.py`. Names
  starting with `_` or `zz_` are not built.
- **Optional sidecars:** `chNN_topic.context.md` (tutor system context),
  `chNN_topic.starters.txt`.
- **Shared code only via `delib`.** Chapters never import one another.
- **Run mode + light Plotly** everywhere, so it auto-runs, is read-only, and
  the charts match. Prefer `*_plotly` helpers; the tutor is told to do the
  same.
- **Animations:** static content in the base figure, only moving traces in
  frames (keeps output small — see the `flow_field` and Ch 4 Heun-step
  animation patterns).
- **Manim** for long symbolic derivations (Ch 2 cooling, Ch 3a F-recovery,
  Ch 3b integrating factor + Bernoulli substitution, Ch 4 Euler walking
  the field). Rendered via CI into `assets/`, cached on `hashFiles('manim/**')`.
- **Math is checkable:** lean on SymPy and numerics so a wrong formula
  shows up as a wrong-looking picture; add a `delib` unit test when you
  add a helper.

---

## The arc

### Part I — First-order ODEs (the solving toolkit)

The closed-form half of the course. Every method on this list answers the
question "given an equation of *this shape*, how do I get a formula?" The
chapter that doesn't answer it — Ch 4 — explains what to do when no
formula exists.

| Ch  | Title                                      | Story / hook                                | Math content                                                              | Primary visuals                                            | Status |
|-----|--------------------------------------------|---------------------------------------------|---------------------------------------------------------------------------|------------------------------------------------------------|--------|
| 01  | First-order ODEs & slope fields            | Rumor across a 1,000-person campus          | Slope field as "every solution at once"; logistic equation                | Vector field + particle flow + slider                      | ✅      |
| 02  | Separable & linear first-order             | Coffee cooling toward room temp             | Separation of variables; integrating factor for linear; Newton's cooling  | Field + exact-vs-numerical overlay; cooling Manim          | ✅      |
| 03a | Exact equations — when the path doesn't matter | Hiker on a contour map                  | Path-independent test $M_y = N_x$; recover $F$ from $(M, N)$              | Contour / level-curve hero; F-recovery Manim               | ✅      |
| 03b | Integrating factors & substitutions        | The equation that *almost* worked           | $\mu(x)$ vs $\mu(y)$; Bernoulli linearization; homogeneous substitution   | Integrating-factor + Bernoulli Manim; step-by-step practice | ✅      |
| 04  | Numerical methods                          | What a physics engine actually does at 60 Hz | Euler, Heun (RK2), RK4; order of accuracy; stiffness; adaptive step      | Slope-field + 3-method hero; log-log convergence; stability plots | ✅      |

### Part II — Higher-order linear ODEs & transforms

The second pillar of the standard curriculum: when the equation is
second-order (and beyond), the algebra changes shape but the geometric
intuition still carries.

| Ch  | Title                                      | Story / hook                                | Math content                                                              | Primary visuals                                            | Status |
|-----|--------------------------------------------|---------------------------------------------|---------------------------------------------------------------------------|------------------------------------------------------------|--------|
| 06  | Second-order linear ODEs                   | A mass on a spring (no damping yet)         | Characteristic equation; real / repeated / complex roots; general solution | Roots-in-complex-plane ↔ response hero; characteristic-equation Manim | ✅      |
| 07  | Damping, forcing, resonance                | A child on a swing                          | $\ddot x + 2\gamma\dot x + \omega_0^2 x = F_0\cos(\omega t)$; transient + steady state; amplitude and phase response | Two-panel A(ω) / φ(ω) hero with sliders; side-by-side drive-vs-response animations; steady-state Manim | ✅      |
| 08  | Non-homogeneous equations                  | The driven RLC circuit                      | Undetermined coefficients; variation of parameters; superposition         | Particular + homogeneous decomposition slider              | TBD    |
| 09  | Laplace transforms                         | A switch flips on at $t = 1$ second         | $\mathcal L\{f\}$, inverse, derivatives, convolution; impulse / step inputs | Pole-zero plot ↔ time-domain response                      | TBD    |

### Part III — Qualitative dynamics (1-D and 2-D)

The Strogatz half of the course. Once the equation is nonlinear and a
formula is off the table (or beside the point), the question becomes
*what does the flow look like?* Fixed points, stability, bifurcations,
phase portraits, limit cycles.

| Ch  | Title                                      | Story / hook                                | Math content                                                              | Primary visuals                                            | Status |
|-----|--------------------------------------------|---------------------------------------------|---------------------------------------------------------------------------|------------------------------------------------------------|--------|
| 05  | Fixed points & stability (the phase line)  | A gene that flips a cell's state            | $\dot x = f(x)$; equilibria; stability from $f'(x^*)$; potential $V$       | Phase line + potential well + slider                       | ✅      |
| 10  | Bifurcations in 1-D                        | A laser crossing the lasing threshold       | Saddle-node, transcritical, pitchfork; normal forms; reading a diagram    | Bifurcation diagram swept over $r$                         | TBD    |
| 11  | Flows on the circle                        | A firefly entraining to a periodic stimulus | $\dot\theta = \omega - a\sin\theta$; phase-locking; the bottleneck         | Flow on $S^1$ with moving point                            | TBD    |
| 12  | Linear 2-D systems                         | Two species competing for a resource        | $\dot{\mathbf x} = A\mathbf x$; eigenvalues → node / saddle / spiral / center | 2-D phase portrait + trajectories + eigen-direction arrows | TBD    |
| 13  | Nonlinear phase portraits                  | The pendulum, in full                       | Nullclines; Jacobian at fixed points; linear classification carries over   | Vector field + nullclines + flow                           | TBD    |
| 14  | Limit cycles                               | A heartbeat (van der Pol)                   | Closed orbits; Poincaré–Bendixson; relaxation oscillation                  | Trajectories spiralling onto a limit cycle (animated)      | TBD    |
| 15  | Bifurcations in 2-D                        | A neuron firing for the first time          | Hopf bifurcation: fixed point births a cycle                               | Phase portrait swept over $\mu$                            | TBD    |

### Part IV — Partial differential equations

A short introduction to the next big idea: spatial *and* temporal variation
in the same equation. Just enough to motivate the toolbox, not a full PDE
course.

| Ch  | Title                                      | Story / hook                                | Math content                                                              | Primary visuals                                            | Status |
|-----|--------------------------------------------|---------------------------------------------|---------------------------------------------------------------------------|------------------------------------------------------------|--------|
| 16  | Intro to PDEs                              | The temperature down a metal rod over time  | Classification (heat / wave / Laplace); boundary vs initial conditions    | Cartoon comparisons of the three canonical PDEs            | TBD    |
| 17  | Heat equation & separation of variables    | Cooling a steel bar                         | $u_t = \alpha u_{xx}$; separation; eigenfunction expansion; superposition | Animated $u(x, t)$ surface + Fourier-mode breakdown        | TBD    |
| 18  | Wave equation                              | A plucked guitar string                     | $u_{tt} = c^2 u_{xx}$; d'Alembert; standing waves                         | String animation + travelling-wave decomposition           | TBD    |
| 19  | Fourier series                             | Synthesizing a square wave                  | Series convergence; Gibbs phenomenon; orthogonality                       | Partial-sum slider; coefficient bar chart                  | TBD    |

### Part V — Chaos

The capstone. Chaotic dynamics is what *requires* the visual toolkit the
rest of the course built.

| Ch  | Title                                      | Story / hook                                | Math content                                                              | Primary visuals                                            | Status |
|-----|--------------------------------------------|---------------------------------------------|---------------------------------------------------------------------------|------------------------------------------------------------|--------|
| 20  | The Lorenz attractor                       | Weather prediction                          | Sensitive dependence on initial conditions; strange attractors             | 3-D trajectory + two near-identical starts diverging       | TBD    |
| 21  | One-dimensional maps                       | A population that goes haywire              | Iteration, cobweb, period-doubling route to chaos                          | Cobweb animation + orbit diagram                           | TBD    |
| 22  | Fractals (capstone, optional)              | Coastline length, Mandelbrot zoom           | Self-similarity; fractal dimension                                         | Iterated-map imagery                                       | TBD    |

Legend: ✅ built · TBD to author.

---

## `delib` helpers — built and to-build

### Built (current toolkit)

Anything chapters 1–5 use. Live in `differential_equations/delib/`.

- **Fields & flows:** `slope_field`, `slope_field_plotly`, `slope_field_data`,
  `vector_field`, `vector_field_plotly`, `phase_portrait` (matplotlib),
  `phase_line`, `potential_plot`, `level_curves`, `overlay_solution`.
- **Solvers:** `solve_ode`, `solve_system` (scipy-backed).
- **Numerical-methods walks (Ch 4):** `euler_steps`, `heun_steps`, `rk4_steps`.
- **Forced oscillators (Ch 7):** `oscillator_animate`, `frequency_response`,
  `steady_state_amplitude`, `steady_state_phase`, `peak_frequency`.
- **Animation:** `animate_plotly`, `animate_time`, `flow_field`,
  `solution_surface`, `frame_index`.
- **UI / interaction:** `param_slider`, `param_panel`, `run_exercise`,
  `ai_code`, `equilibria_report`, `closed_form_report`, `solve_steps`,
  `exercise_view`, `exercise_inputs`, `exercise_ai`, `check_number`,
  `derivation`, `video`.
- **Tutor & key plumbing:** `key_field`, `key_bridge_widget`,
  `cell_picker_widget`, `persist_key`, `tutor_chat`, `tutor_sidebar`.

### To build (ordered by first chapter that needs it)

Each helper is light-theme Plotly, self-contained (no cross-module imports,
for WASM inlining), and animation-safe (static content in base, moving
content in frames).

- **`pole_zero_plot(num, den)`** — complex-plane poles + zeros, with the
  unit circle / imaginary axis as visual references. *(Ch 9)*
- **`laplace_table()`** — interactive lookup pairing $f(t)$ ↔ $F(s)$ with
  derivation notes. *(Ch 9)*
- **`bifurcation_diagram(make_f, r_range, xrange)`** — stable / unstable
  branches of fixed points swept over a parameter. *(Ch 10)*
- **`circle_flow(f, ...)`** — flow on $S^1$ with a moving point.  *(Ch 11)*
- **`phase_portrait_plotly(F, xlim, ylim)`** — 2-D vector field + seeded
  trajectories (Plotly version of the existing matplotlib helper). *(Ch 12)*
- **`nullclines(F, xlim, ylim)`** — $\dot x = 0$ and $\dot y = 0$ curves
  over the field. *(Ch 13)*
- **`limit_cycle_view(F, ...)`** — trajectory animator showing spiral-in
  to a closed orbit. *(Ch 14)*
- **`heat_solve_1d(L, T, ic, bc, alpha)`** — finite-difference solver +
  animated $u(x, t)$ surface. *(Ch 17)*
- **`wave_animate_1d(...)`** — standing / travelling wave animation.
  *(Ch 18)*
- **`fourier_partial_sums(f, N)`** — partial-sum convergence slider with
  Gibbs phenomenon visible at jumps. *(Ch 19)*
- **`trajectory_3d(F, t_span, starts)`** — animated 3-D `Scatter3d` for
  chaos. *(Ch 20)*
- **`cobweb(g, x0, n)`** and **`orbit_diagram(make_g, r_range)`** — for
  maps. *(Ch 21)*

---

## Status

### Built

- **Ch 01** — Rumor hook → logistic; live SymPy; slope field + particle flow;
  4 challenges; playground; tutor.
- **Ch 02** — Coffee-cooling hook → linear first-order with closed form;
  Newton's cooling Manim; cooling-method Manim; tutor.
- **Ch 03a** — Hiker / contour-map hook → exactness test; F-recovery Manim;
  contour-level-curves visualization; positive-definite accordion; two
  step-by-step exercises; tutor.
- **Ch 03b** — "When the test fails" → $\mu(x)$ derivation as a Manim;
  Bernoulli linearization Manim + step-by-step practice; homogeneous
  substitution accordion; three exercises; tutor.
- **Ch 04** — Physics-engine hook → Euler walk; Manim of Euler walking
  $y' = y - x^2$; interactive $h$-slider; order-of-accuracy log-log; Heun
  (RK2) construction animation; RK4 + Simpson connection; convergence hero;
  stiffness on $N' = -\lambda N$; backward Euler; adaptive-step closer.
  *(Try-it challenges, playground, recap pending.)*
- **Ch 05** — Wall-light-switch hook → six-trajectory figure; the cubic
  $\dot x = x - x^3$ derived from sign requirements; phase-line-collapse
  Manim; stability via linearisation $\dot\eta \approx f'(x^*)\eta$
  (pays off Ch 4's decay equation); potential landscape with barrier
  height; basins of attraction + bifurcation teaser; 3 exercises;
  playground; recap; tutor.
- **Ch 06** — Mass-on-spring hook (oscillation impossible in 1-D) →
  Newton + Hooke → guess-and-check $\cos$, $\omega = \sqrt{k/m}$ with
  sliders; exponential ansatz Manim → characteristic equation; three
  cases by $b^2 - 4c$ with three animated case panels + Euler's-formula
  accordion; roots-in-complex-plane ↔ response hero (b, c sliders);
  worked initial-conditions example; 3 exercises; playground; recap
  (now with a forward-looking pointer to Ch 9 / Ch 12 explaining the
  "guessed" exponential as a principled identity); tutor.
- **Ch 07** — Child-on-a-swing hook (right-rhythm vs wrong-rhythm
  side-by-side animations) → transient + steady-state decomposition;
  canonical $\ddot x + 2\gamma\dot x + \omega_0^2 x = F_0\cos(\omega t)$;
  Manim derivation of $A(\omega)$ and $\varphi(\omega)$ by
  ansatz-substitute-and-match; two-panel amplitude/phase frequency-
  response hero with $\omega_0, \gamma$ sliders; side-by-side drive-
  vs-response animations showing the phase regimes; $\gamma = 0$
  resonance-disaster note (Tacoma Narrows); 3 exercises; playground;
  recap. New delib helpers (`oscillator_animate`,
  `frequency_response`, plus the three scalar steady-state shortcuts).

### Cross-cutting infrastructure built

- BYO-key tutor: claude-sonnet-4-6, Socratic system prompt, persistent key
  via `key_bridge_widget` + `persist_key`.
- Manim CI: `.github/workflows/deploy-pages.yml` renders hero scenes,
  caches on `hashFiles('manim/**')`, deploys to GitHub Pages with `main`
  and the active integration branch live.
- `exercise_view(..., with_ai=False)` for step-by-step practice without an
  AI button.
- Multi-part chapter support: `chNN[a-z]_*.py` glob in
  `scripts/build_wasm_site.py`.

### Immediate backlog

- **Ch 08**: non-homogeneous equations (undetermined coefficients,
  variation of parameters, the driven RLC circuit angle).
- **Ch 09 onward**: Laplace transforms (and the principled rederivation
  of the Ch 6 ansatz), then Part III.

The pattern is now well-established — each new chapter is mostly math
content + choosing the right visual from the `delib` table + a hook story
that earns the formalism.
