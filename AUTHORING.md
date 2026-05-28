# Authoring Playbook

How to build a chapter, distilled from Chapter 1. Read this before starting a new
chapter; it turns hard-won lessons into a repeatable recipe so each chapter is
"fill the recipe," not "rediscover the platform."

---

## 1. What Chapter 1 is (the proven set)

**Content — a 6-beat narrative** (`differential_equations/chapters/ch01_first_order_odes.py`):
1. **Hook** — a real story (a rumor spreading on a campus) + its observed S-curve.
2. **Concept bridge** — names what the story is: a first-order rule `dy/dt = f(t,y)`.
3. **Build the model** — derive the logistic equation from the mechanism.
4. **Play with the symbols** — live SymPy equilibria/stability as you edit the rate law.
5. **See it** — slope/vector field → slider exploration → flow animation.
6. **Try it** — coach-mode code challenges (auto-checked) → an open playground.

**Toolkit — `delib`** (shared, inlined into every WASM page):
- Numerics: `solve_ode`, `solve_system`.
- Static visuals: `slope_field_plotly`, `vector_field_plotly` (arrows), `solution_surface` (3D).
- Animation: `flow_field` (particles riding the field), `animate_plotly`.
- Symbols: `equilibria_report` (SymPy: solve `dy/dt=0`, classify stability).
- UI: `param_panel`/`param_slider`, `run_exercise` (run + auto-grade code), `ai_code` (per-exercise AI, `coach=True` to scaffold without spoiling).

**Platform — the build + tutor:**
- WASM export in **run mode** (auto-runs, read-only source, `mo.ui` still interactive).
- A floating **tutor chat** (BYO Anthropic key, client-side) + a click-to-pick cell selector.
- Cross-chapter **nav bar**; chapters are `chNN_*.py` (others are skipped).

---

## 2. Composition lessons (content)

- **Concrete before formal.** Open with a phenomenon and a picture; earn the
  equation before writing it. Abstract definitions up front kill engagement.
- **Name the concept once.** After the hook, a short bridge that says "this is a
  differential equation, here's what that means" anchors the math.
- **Fade the story, don't cut it.** Keep a thread of the story through the visuals
  (sliders = story knobs; animation = many stories), then hand off to pure math at
  "Try it." A hard jump from narrative to symbols reads as two different documents.
- **Every visual earns its place.** Static → interactive → animated, each adding one
  new idea. 3-D only where it reveals something 2-D can't.
- **Practice has two modes.** Graded **code grounds** (AI scaffolds via `coach=True`,
  auto-checked) for "did you get it," plus one **open playground** (no grading) for
  "what are you curious about."

---

## 3. Platform lessons (technical — save future pain)

- **The kernel is in a Web Worker.** It can `fetch` but cannot see `sessionStorage`,
  `document`, or the page. Anything needing the main thread (the BYO key, picking a
  cell) goes through an **anywidget** whose JS runs on the main thread.
- **Chapter content lives in Shadow DOM.** Page-level CSS/JS can't reach it. To style
  or process it (KaTeX math, mobile CSS) you must **walk the shadow roots and inject
  there** (see `MATH_RENDER_JS` in the build).
- **Animations: static in the base, only motion in frames.** Repeating a static field
  in every frame blew one figure to 12 MB. Put fixed traces in the base figure and
  have frames update only the moving trace (`go.Frame(..., traces=[i])`).
- **`delib` is inlined as one combined module for WASM.** Each module must be
  self-contained — no module-level `from delib.x import y` (the submodule doesn't
  exist at runtime). Reference helpers within the same module, or `import delib` at
  call time.
- **Tell the AI the exact API.** Generated code invented kwargs (`t_range=`) until the
  prompts listed precise `delib` signatures with "do not invent keyword arguments."
- **LaTeX:** `mo.md` renders math natively; the **chat bubble** needed the shadow-DOM
  KaTeX pass.
- **BYO key, client-side**, with the `anthropic-dangerous-direct-browser-access`
  header; persisted in `sessionStorage` and shared via the KeyBridge widget.

---

## 4. Per-chapter checklist

1. Pick the topic + a **real-world hook** from `ROADMAP.md`.
2. Write the **6 beats** with the story→math gradient. (Add a `.context.md` for the tutor.)
3. Reuse `delib` visuals; build any **missing helper** (the 🔨 list in `ROADMAP.md`)
   in its own self-contained, WASM-safe form, with a unit test.
4. Add a **symbol-play** beat (`equilibria_report`, or a richer symbolic tool when
   the algebra demands it).
5. Add **2–4 coach-mode code challenges** (`run_exercise` + `ai_code`) and one **open
   playground**.
6. Name the file `chNN_topic.py`; `python scripts/build_wasm_site.py`; run the tests;
   eyeball mobile; push.

---

## 5. Known follow-ups

- **Mobile polish** — title/nav clearance and chart sizing are improved but not final.
- **SymPy load** — first use downloads a chunky package in the browser; watch the pause.
- **Animated symbol manipulation** — step-by-step algebra reveal (factor → solve →
  roots), needed once later chapters get symbol-heavy. Tracked in `ROADMAP.md`.
- **Packaging** — the per-challenge wiring is ~5 cells each; factor into a tighter
  `delib` helper before the challenge count grows across chapters.
