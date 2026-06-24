# Authoring Playbook — Differential Equations Chapters

**Read this end-to-end before touching a new chapter.** It captures every prose
and platform lesson distilled from building Chapter 1 (rumor / logistic) and
Chapter 2 (cooling coffee / Newton). The goal is that the *next* chapter is
"fill the recipe, reuse the kit," not "rediscover the platform."

The user works with us in a **structured five-step loop**:

> **plan → scaffold → adding details → test → refine**

Each step is a separate exchange. Don't collapse them; the user wants to see
the plan before code lands, and to refine prose/visuals after the chapter runs.

---

## 0. Where things live

```
differential_equations/
  delib/                 # Shared toolkit (visuals, exercises, tutor, numerics)
    __init__.py          # Re-exports — anything new must be listed here
    fields.py            # vector_field_plotly, slope_field_plotly, _field_arrows
    animate.py           # flow_field, animate_plotly, solution_surface
    solvers.py           # solve_ode, solve_system
    ui.py                # param_panel, run_exercise, exercise_*, tutor_*,
                         # key_field, key_bridge_widget, cell_picker_widget,
                         # check_number, equilibria_report, closed_form_report,
                         # derivation, video, ai_code, _guard_expr
  chapters/
    ch01_first_order_odes.py          # canonical template (rumor → logistic)
    ch02_separable_and_linear.py      # canonical template (cooling → Newton)
    ch03_..._.py                       # ← next chapter goes here

manim/                                # Offline-rendered hero derivations (mp4)
  newton_cooling.py                   # ch02 hero — per-atom morph
  derivation_kit.py                   # vinc, glyph, HIGHLIGHT helpers

assets/                               # Static images + Manim mp4s, copied to /site
scripts/build_wasm_site.py            # Pipeline: chapter.py → static HTML page
.github/workflows/deploy-pages.yml    # render + build + deploy to GitHub Pages
ROADMAP.md                            # Curriculum arc (chapters 1–12) + delib backlog
```

Active development branch: **`claude/tender-einstein-arCIU`**. Both `main` and
this branch deploy live; other feature branches only build as a CI check.

---

## 1. The five-step workflow (how we'll work)

For every chapter, run these steps as distinct exchanges with the user.

### 1.1 — Plan
- Read the chapter's row in `ROADMAP.md` (topic, worked example, primary visual,
  any 🔨 `delib` helpers required).
- Draft a **one-page plan** in chat: real-world hook, the equation, the
  narrative beats, what visuals are needed, what exercises will assess, what
  new `delib` helpers (if any) must land first.
- **Wait for approval** before scaffolding. If a new visual helper is needed
  and you have a *reference implementation idea*, surface it here — the user
  may hand you a concrete reference code from another chat session (the
  established workflow).

### 1.2 — Scaffold
- Build any **new `delib` helpers** first, fully self-contained (see §4.4),
  with a quick numeric sanity test (see §1.4).
- Create `differential_equations/chapters/chNN_topic.py` from the ch02 skeleton
  (§3.2). Use placeholder text for prose; *do* wire all visuals and exercises
  end-to-end so the page actually runs.
- Build the site locally (`python scripts/build_wasm_site.py`); confirm the
  chapter exports without errors.

### 1.3 — Adding details
- Fill in the **prose** beat by beat, applying §2 lessons.
- Wire up the **Manim hero derivation** if the chapter has one (§7).
- Author the **graded exercises** + **playground** (§5).

### 1.4 — Test
- `python -c "import ast; ast.parse(open('<chapter>.py').read())"` — syntax.
- `python scripts/build_wasm_site.py` — full export must succeed.
- Verify any new `delib` helpers with a small numeric script that loads them
  without importing the `delib` package (the package `__init__.py` pulls
  things that may need extra deps; load helpers via `importlib` instead — see
  `_field_arrows` verification in the cooling-arrow-size fix as a template).
- **`grep -o ... index.html`** the exported page to confirm CSS rules, JS
  hooks, and key strings landed.

### 1.5 — Refine
- The user reads the live page and sends feedback as numbered items.
- **Treat console errors as gold.** If the user shares browser console output,
  read it carefully — `multiple-defs`, `NameError`, and traceback frames
  almost always point to the real cause (the ch02 slider bug was nailed by a
  single `multiple-defs name "k"` line).
- Push fixes in small, focused commits; explain *what was wrong* in the
  reply, not just *what changed*. The user repeatedly emphasised they only
  report symptoms; you must diagnose.

---

## 2. The chapter narrative (the six beats + tutor)

The proven shape, with prose lessons baked in. Each beat is one or more
`@app.cell(hide_code=True)` cells containing `mo.md(r"""...""")`.

### 2.1 — Hook (a real story + a picture)
A concrete real-world phenomenon and a Plotly chart of it. **Concrete before
formal.** Ch01: a rumor on a 1000-person campus → S-curve. Ch02: a coffee
cooling in a 20°C room → decaying exponential.

> ⚠ **Continuity:** if this chapter's example has *nothing to do with* the
> previous chapter's, **say so out loud** — "Chapter N told one DE story; this
> is a brand-new, unrelated story; the lesson is that the same kind of
> rate-rule fits many phenomena." Ch02 omitted this and the user flagged it
> as a story discontinuity.

### 2.2 — Concept bridge ("what the story is really saying")
A short paragraph that names the math the story illustrates. **Explain how
$f(t, y)$ works as a slope-machine** (feed it a point, get back a slope); don't
just label it "first-order" and move on. Demote jargon ("first-order",
"linear", "separable") to a parenthetical *after* the intuition lands.

### 2.3 — Build the model
**Derive, don't assert.** Walk from the verbal mechanism to the equation:
- Define each variable.
- State the principle in plain English.
- Translate one phrase at a time into symbols.
- Land on the equation, *then* name it (e.g. "this equation has a name —
  Newton's law of cooling").

For non-obvious products like $y(K-y)$, **show concrete numerics** (in ch01:
"on a 1000-person campus, $y=10$ gives $10\times 990$, $y=500$ gives
$500\times 500$, $y=990$ gives $990\times 10$ — small at the ends, biggest in
the middle"). The user explicitly asked for this on ch01.

### 2.4 — Play with the symbols
Two flavours; pick what the chapter needs:

- **Live SymPy** (`delib.equilibria_report`, `delib.closed_form_report`) — the
  student edits a rate law in a `mo.ui.text`; the analysis re-solves on every
  keystroke. Guard with `_guard_expr` (already wired) so wild input can't
  freeze the kernel.
- **Animated derivation** — for chapters whose key insight *is* an algebraic
  manipulation, ship a hero **Manim** clip (§7) showing per-atom motion. The
  in-browser `delib.derivation` player still exists for smaller side
  derivations but is generally superseded by Manim for the main beat.

When introducing equilibria: **define what one is and why it exists** ("the
rate is zero, so the system has nowhere to move") *before* naming
stable/unstable. Don't start with "the superpower of writing the rule down"
or similar handwaving.

**Self-check quizzes** (optional, helpful for classification topics): four
`mo.ui.dropdown` with inline ✅/❌ marks beside each row, plus a detailed
"why" callout below. See ch02's "Quick check — which family?" for the
pattern. **Underscore loop variables** — `for _k in ...`, not `for k in ...`
— or marimo will register the leaked loop variable as a cell global and
trigger `multiple-defs` (see §4.2).

### 2.5 — See the flow
**Static → interactive → animated**, in that order, each adding one new idea.

- Static field with fixed parameters (`delib.vector_field_plotly`) — explain
  *how a slope field is made* (`dy/dt` is a slope; evaluate $f$ on a grid;
  each point gets a tilted segment).
- Sliders driving the same field (`delib.param_panel`) + a red exact-solution
  curve overlay. **The slope-field arrows are now uniform in pixel space**
  (`_field_arrows` uses an assumed `aspect` ratio, default 2.2) — every
  chapter gets consistently sized arrows regardless of axis ranges.
- Animated flow (`delib.flow_field`) — particles riding the static field.
  Static content **in the base figure**; only the particle trace moves per
  frame. This pattern keeps the payload at ~0.4 MB instead of 12 MB.

If a chapter introduces a new visual idea (phase line, bifurcation diagram,
phase portrait, nullclines, cobweb), build the `delib` helper for it first
(§4.4), test it numerically, then use it here.

### 2.6 — Read the formula (when there's a closed form)
After the derivation/closed form, **add a beat that reads it in plain
language**. Ch02's "What the formula is telling us": $T = T_r + (T_0 - T_r)
e^{-kt}$ → "room plus a leftover gap that shrinks exponentially." Pull out one
or two qualitative takeaways ("every cup forgets its past", "doubling $k$
halves the closing time"). The user explicitly asked for this on ch02.

### 2.7 — Try it (graded code grounds)
2–4 small code challenges. See §5 for the pattern. **Always coach-mode**
(`coach=True`) — the AI scaffolds but never fills in the graded `answer`.

### 2.8 — Playground (one open sandbox)
No grading, no prompt, no check. The student types/asks for anything. Wire
with `coach=False` so the AI may write complete runnable code.

### 2.9 — Recap & what's next
One short paragraph naming what was learned, and a sentence pointing forward
to the next chapter (state any pre-reqs).

### 2.10 — Tutor sidebar
Wire the **shared delib kit** (`key_bridge_widget`, `cell_picker_widget`,
`key_field`, `persist_key`, `tutor_chat`, `tutor_sidebar`) at the END of the
file. **Don't** roll a per-chapter inline tutor (ch01 used to; it drifted and
had to be refactored back onto the kit).

---

## 3. Prose lessons (from real feedback)

Each rule below traces to a specific feedback round. Apply them proactively.

| DO | DON'T | Source |
|---|---|---|
| Lead intuition before jargon ("$f$ is a slope-machine") | Drop "first-order" / "linear" without unpacking | ch01 R1 |
| Acknowledge story discontinuity ("this chapter opens a new, unrelated story") | Silently switch domains between chapters | ch02 R1 |
| Use concrete numbers to make a product intuitive ($10\times 990$, $500\times 500$) | Hand-wave "engine vs brake" without numbers | ch01 R1 |
| Define what an equilibrium **is and why it exists** before naming stability | "Quiet superpower of writing the rule down" | ch01 R1 |
| Show how a slope field is **constructed** (slope at each grid point) | "It assigns a slope to every point" with no construction | ch01 R1 |
| **Derive** the equation from a verbal principle, name it after | "This is Newton's law of cooling: $\dot T = -k(T-T_r)$" | ch02 R1 |
| **Read** the closed-form solution in plain language and pull out 1–2 takeaways | Drop the formula and move on | ch02 R1 |
| Replace technical-tool jargon with what the math does | "`dsolve` would spit out…" | ch02 R1 |
| Clarify questions that could read multiple ways | "Does it overshoot?" (what does overshoot mean?) | ch01 R1 |
| Inline ✅/❌ correctness mark next to each quiz dropdown | Only show a feedback list below | ch02 R2 |
| Captions on every Manim step ("integrate the LHS over T, the RHS over t"; "+ C absorbs both constants") | Trust the symbols to speak for themselves | ch02 R2 |
| Re-center the Manim equation after each operation | Anchor everything at `LEFT * 3.4` and let it drift | ch02 R2 |
| Order a derivation by what *motivates* it, even if that reverses the logical order (split → name the pieces → show figures, not figures-first) | Present a formal decomposition before the reader knows why they'd want it | ch07 |
| Stay inside the toolkit the chapter has built — derive with what the audience can already read | Reach for out-of-scope machinery (dot-products / vectors in a trig-level chapter) to "explain" a step | ch07 |
| Justify a representation switch with a concrete reason the reader can feel | Appeal to authority ("these aren't the numbers a physicist cares about") | ch07 |
| Show one intermediate line of even "trivial" algebra (square-and-add, divide-and-cancel) for transparency | Jump from the matched equations straight to the boxed result | ch07 |
| Build a two-part idea from what's *already on screen* (the swing's first cycles visibly growing) | Assert a decomposition the reader has no reason to believe yet | ch07 |
| Pre-empt the sharp reader's question with one honest sentence (why $A\cos(\omega t-\varphi)$ doesn't "become" the growing $t\sin\omega_0 t$ at resonance) | Drop a surprising formula and move on | ch07 |

Story-to-math gradient: keep the chapter's story present early ("your kitchen",
"your campus") and let it fade as the math takes over. A hard jump from story
to symbols reads as two different documents (ch01 R1).

---

## 4. Marimo gotchas (the bug bible)

These are real bugs we hit. Each entry: **symptom → cause → fix**.

### 4.1 — `mo.as_html(widget)` inside an `mo.md` f-string breaks reactivity
- **Symptom:** Sliders render but moving them doesn't update the chart.
- **Cause:** Embedding the widget via `f"... {mo.as_html(controls)}"` inside
  `mo.md` is fragile — the binding between the rendered widget and downstream
  cells reading `controls.value` can break.
- **Fix:** Split into two cells. Cell 1 defines `controls = delib.param_panel(...)`
  and `return (controls,)`. Cell 2 takes `controls` as a dep and renders
  `mo.vstack([mo.md(...), controls])`. This is the canonical marimo pattern.

### 4.2 — For-loop variables leak as cell globals → `multiple-defs`
- **Symptom (in browser console):** `{"type":"multiple-defs","name":"k","cells":["…","…"]}`.
  Downstream cells then fail with `NameError: name "k" is not defined`
  because marimo refuses to bind either definition.
- **Cause:** Python for-loop variables persist after the loop, so a cell with
  `for k in (...)` registers `k` as a module-level binding. Any other cell
  that also defines `k` (e.g. `k = controls.value["k"]`) collides.
- **Fix:** Prefix the loop variable: `for _k in (...)`. Underscore-prefixed
  names stay cell-private in marimo. The same goes for `_v`, `_ok`, etc.
  Comprehensions: `[_k for _k in _key]`, not `[k for k in _key]`.

### 4.3 — Chapter content lives in Shadow DOM
- **Symptom:** Page-level KaTeX / CSS / JS doesn't reach the chat bubble or
  some other content.
- **Cause:** marimo renders some content into encapsulated shadow roots; CSS
  inheritance and `document.querySelector` don't cross the boundary.
- **Fix:** The build's `MATH_RENDER_JS` walks every shadow root, injects a
  KaTeX `<link>` into roots that contain `$`, and observes them for streaming
  updates. Mirror that pattern if you need to inject anything else.

### 4.4 — `delib` is base64-inlined as ONE combined module for WASM
- **Symptom:** `ImportError: No module named 'delib.x'` in a chapter that
  imports `from delib.x import y`.
- **Cause:** The build concatenates every `delib/*.py` into one module and
  base64-inlines it into each chapter as the literal `delib` module. The
  individual submodule namespaces (`delib.fields`, `delib.animate`, …)
  don't exist at runtime.
- **Fix:** Inside `delib`, **never** import from another `delib` submodule
  at module level. If a helper needs to call another helper from a different
  file, either:
  - rely on the fact they all end up in the same combined namespace and
    reference the bare name (after re-export);
  - or `import delib` *inside the function body* and use `delib.thing`.

### 4.5 — Animations explode in size if static content is per-frame
- **Symptom:** Marimo's `output_max_bytes` error; multi-MB output for a
  simple particle animation.
- **Cause:** Every `go.Frame(data=[…full field, particles…])` re-embeds the
  whole static field once per frame.
- **Fix:** Put the static field as a trace in the **base** `go.Figure`, and
  let each frame update **only** the particle trace via
  `go.Frame(data=[particle_trace], traces=[particle_idx], name="…")`.
  `delib.flow_field` already does this — ~0.4 MB instead of 12 MB.

### 4.6 — Web Worker isolation (no `document`, no `sessionStorage`)
- **Symptom:** `sessionStorage is not defined`, `document is not defined` in
  the kernel.
- **Cause:** The Pyodide kernel runs in a Web Worker. It can `fetch`, but it
  cannot touch the DOM or main-thread storage.
- **Fix:** Anything needing the main thread goes through an **anywidget**
  whose `_esm` JS runs on the main thread:
  - `delib.key_bridge_widget()` reads/writes `sessionStorage["mathlearn.anthropicKey"]`.
  - `delib.cell_picker_widget()` walks `.marimo-cell` DOM nodes.

### 4.7 — Heavy SymPy expressions can hang the kernel
- **Symptom:** Browser tab unresponsive after entering something like
  `-k*(T-Tr)*e^999` in the equilibria text box.
- **Cause:** SymPy's `solve`/`dsolve` is single-threaded inside the worker
  and pathological expressions take forever.
- **Fix:** `delib._guard_expr(expr)` already vetoes huge exponents (>12),
  huge numbers (>1e6), and deep expressions (`count_ops > 60`). Call it
  before any `sympify`-backed analysis in a new helper.

### 4.8 — Multi-output cells in marimo
- A cell shows its **last unassigned expression** as the output. If you need
  to both define a global *and* show something, end the cell with the
  display expression (e.g. `fig` on its own line) and `return (...)` the
  globals downstream cells need.

### 4.9 — Page blank until Pyodide finishes booting (~60–90s)
- **Symptom:** The chapter shows only the loading splash for over a minute;
  nothing readable appears until the in-browser runtime has fully booted.
- **Cause:** A plain `marimo export html-wasm` embeds the notebook *source*
  but **no rendered cell outputs** — so the page genuinely has nothing to
  paint until Pyodide runs every cell. (Confirmed by dumping `index.html`:
  section headings existed only inside `<script>` blobs.)
- **Fix (two parts, both already in `build_wasm_site.py`):**
  1. Export with **`--execute`**: marimo runs the notebook once at build
     time and embeds each cell's rendered output into
     `window.__MARIMO_MOUNT_CONFIG__`. The React bundle mounts those on
     first paint (~2–3s), *before* Pyodide. Pyodide still boots in a worker
     afterward to make sliders / code cells live.
  2. The splash's `ready()` detector must watch for **content in `#root`**
     (a heading, or >200 chars of text), **not** a marimo-specific class.
     The old detector polled `.marimo-cell`, which this marimo version
     doesn't emit, so the splash never lifted until the 180s cap — hiding
     fully-rendered content underneath. That single wrong selector *was*
     the "blank for 90s" bug.
- **Don't** add a "warming up the interactive demos" pill keyed on figure
  presence: with `--execute` the figures are pre-rendered and animations
  play without Pyodide, so it fires over non-interactive sections and
  confuses readers. (Removed.)

### 4.10 — KaTeX renders inline math *tripled* ("x_h" → "xhx_hxh")
- **Symptom:** A math span shows three overlaid copies — rendered glyphs +
  raw TeX source + MathML — so `$x$` reads "xxx", `$x_h$` reads "xhx_hxh",
  and plain words between spans repeat ("and and and").
- **Cause:** KaTeX's hidden MathML/annotation layer leaks visible. **Two
  independent triggers**:
  (a) Density — one `mo.md` block with many math spans (worst case in ch07:
  6 `$$` displays + 10 inline `$...$` in a single block). The server-side
  HTML was correct; failure was client-side.
  (b) `--mode edit` — un-executed cells render through marimo's static
  fallback path which routes math through MathML, so the moment a cell is
  dense at all, it triples. This is why ch08 looked correct in `--mode run`
  but tripled badly under `--mode edit` even with moderate density.
- **Fix:** (a) Keep each `mo.md` light — at most ~3 display blocks, and
  split heavy derivations into multiple cells (display-only equation blocks
  apart from inline-only prose blocks). (b) Always export `--mode run` with
  `--execute`; the embedded snapshot bypasses the MathML fallback entirely.
  We don't use `--mode edit` anywhere anymore (see §8). Sanity-check a
  block by piping it through `marimo._output.md.md(...)` and counting
  `||[` (display) vs `||(` (inline) marimo-tex spans, and scanning for raw
  `\`-commands leaking *outside* `<marimo-tex>`.

### 4.11 — Inline `$...$` split across source lines renders as raw LaTeX
- **Symptom:** `\omega`, `\cos`, … appear literally instead of rendering.
- **Cause:** `pymdownx.arithmatex`'s inline matcher is line-bounded. An
  inline expression wrapped across two source lines inside the `r"""..."""`
  (e.g. `$x_p(t) = A\cos(\omega t -` ⏎ `\varphi)$`) is never recognised.
- **Fix:** Keep every inline `$...$` on a **single physical source line**.
  Expressions too long to fit go in a `$$...$$` display block — but mind
  §4.11b.

### 4.11b — A `$$` block with a continuation line starting `+ ` silently fails
- **Symptom:** A multi-line `$$ … $$` display renders as raw LaTeX
  (`$$`, `\bigl`, `L[y_p]` all literal). marimo's md pipeline reports the
  block as inline/none, not display.
- **Cause:** Markdown sees a line beginning with `+ ` (also `- ` / `* `) as
  a **bullet-list item**, which terminates the display block mid-LaTeX. So
  ```
  $$
  L = a + b
  + c          ← markdown reads this as a list bullet
  $$
  ```
  breaks, while the same content split with a leading `\;` / `&` does not.
- **Fix (most robust):** put the whole equation's content on **one physical
  line** between the `$$` delimiters (the delimiters may stay on their own
  lines). Long lines are fine — KaTeX scrolls. Alternatively wrap in
  `\begin{aligned} … \end{aligned}` and lead each continuation with `&`
  (never a bare `+`). Single-line content is the bulletproof choice; verify
  with the `marimo._output.md.md(...)` → count `||[` probe.

### 4.12 — `--execute` runs every cell at build time → build env needs the full stack
- **Symptom (CI):** `ModuleNotFoundError: No module named 'anywidget'` /
  `'sympy'` during export; build aborts.
- **Symptom (browser):** a Try-It cell errors with `No module named
  'matplotlib'` when the student presses Run.
- **Cause:** `--execute` executes the notebook during the build, so every
  package any cell imports must be installed in the build env. And the
  **browser** Pyodide only preinstalls what the PEP 723 header declares —
  `delib.run_exercise` imports matplotlib at call time (to hand the student
  `plt`), which fails if matplotlib isn't declared.
- **Fix:**
  - CI installs the chapters' full stack: **`pip install . anywidget sympy`**
    (mirrors `deploy/hf-space`; project metadata only declares delib's deps).
  - Pass **`--no-sandbox`** so marimo executes inline in that env,
    deterministically, instead of trying a `uv`-isolated env (CI has no
    `uv`, so it silently fell back to a bare interpreter and every cell
    errored).
  - **`PEP723_HEADER` must list every package a cell or exercise can import
    at runtime** — currently `marimo, anywidget, numpy, sympy, plotly,
    matplotlib`. Add to it whenever a chapter introduces a new runtime
    import, or the browser will `ModuleNotFound` at the moment that code runs.

---

## 5. The exercise system

The full kit lives in `delib.ui`. The wiring per challenge is ~5 cells:

```python
# 1. State holding the editor's current code.
@app.cell
def _(mo):
    d1_get, d1_set = mo.state("k, Tr, T0 = 0.2, 20.0, 90.0\n"
                              "# … task …\n"
                              "answer = ...\n")
    return d1_get, d1_set

# 2. UI controls (AI text + button + code editor + run button).
@app.cell
def _(d1_get, delib):
    d1_ai, d1_gen, d1_code, d1_run = delib.exercise_inputs(d1_get())
    return d1_ai, d1_code, d1_gen, d1_run

# 3. The ✨ button → call Claude (coach=True scaffolds without spoiling).
@app.cell
async def _(api_field, d1_ai, d1_code, d1_gen, d1_set, delib, key_bridge):
    await delib.exercise_ai(
        d1_gen, d1_ai, d1_code, d1_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="…short, model-facing description of the task…",
    )

# 4. Layout: prompt + ai + editor + run button.
@app.cell(hide_code=True)
def _(d1_ai, d1_code, d1_gen, d1_run, delib):
    delib.exercise_view("**1.** Markdown prompt for the student.",
                        d1_ai, d1_gen, d1_code, d1_run)

# 5. Run + auto-check.
@app.cell(hide_code=True)
def _(d1_code, d1_run, delib):
    delib.run_exercise(d1_code.value, d1_run.value, check=lambda ns: delib.check_number(
        ns, target=29.47, tol=0.5,
        ok="Right — about $29.5°C$; it's cooled most of the way already.",
        hint="Use $T(t)=T_r+(T_0-T_r)e^{-kt}$, or integrate with delib.solve_ode."))
```

### 5.1 — The exercise namespace (`run_exercise`)
Pre-bound names available without any `import`:

```
mo, np, plt, go, delib, math,
e, pi, tau, inf,
exp, log, log10, sqrt, sin, cos, tan, abs
```

Trig/exp/log/sqrt are `np.*` (array-aware). `e`, `pi`, `tau`, `inf` are
`math.*` (scalar). `ns_extra` from the chapter can override.

### 5.2 — Coach mode (graded challenges)
`coach=True` (default for `exercise_ai`) appends an instruction telling the
model to scaffold and hint but leave `answer = ...` blank for the student.
Use `coach=False` for the playground (no grading → AI may write the whole
program).

### 5.3 — ✨ button errors are surfaced
If the API call fails, `ai_code` writes a `# ⚠ tutor: <reason>` banner at
the top of the code editor instead of silently returning unchanged code.
Old banners are stripped before each new request so they don't stack.

### 5.4 — `check_number` (the standard auto-grader)
Compares `ns["answer"]` against `target` within `tol`. Pass `ok=` and `hint=`
markdown strings; they render as a green-success / yellow-warn callout.

---

## 6. The tutor system

End of every chapter file (see ch02 for the canonical block):

```python
@app.cell
def _(delib):
    key_bridge = delib.key_bridge_widget()
    return (key_bridge,)

@app.cell
def _(delib):
    picker = delib.cell_picker_widget()
    return (picker,)

@app.cell
def _(delib):
    api_field = delib.key_field()
    return (api_field,)

@app.cell
def _(api_field, delib, key_bridge):
    delib.persist_key(api_field, key_bridge)

@app.cell
def _(api_field, delib, key_bridge, picker):
    chatbox = delib.tutor_chat(
        api_field, key_bridge, picker,
        "This is Chapter N of a differential-equations course: …short context….",
        prompts=["explain this chapter in a paragraph",
                 "show the solution when …",
                 "plot …"],
    )
    return (chatbox,)

@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge, picker):
    delib.tutor_sidebar(api_field, key_bridge, picker, chatbox)
```

The sidebar is **owned by us** — `scripts/build_wasm_site.py` forces
`aside.app-sidebar { display:none !important }` and uses a single nav-bar
"💬 Tutor" button to toggle a body class `ml-show-tutor`, which floats the
sidebar as an overlay. Don't try to detect marimo's collapsed states; we
hide everything and only show on toggle.

The cell-picker enters pick-mode by removing `ml-show-tutor` (so the
sidebar can't cover the cells you're choosing from) and re-adds it on exit.
Both the inline and delib pickers have this behaviour.

---

## 7. Manim hero derivations (chapters with a key algebraic step)

When a chapter's central insight is an algebraic transformation (ch02:
separation of variables), render a hero clip offline with Manim and embed
it via `delib.video("clipname.mp4")`. CI renders it; do **not** try to run
Manim in this sandbox (no LaTeX, no ffmpeg).

### 7.1 — Per-atom morph (not TransformMatchingShapes)
Every leaf glyph is its own persistent mobject. Each step uses
`Transform(old, new_position)` per atom, so the motion is one continuous
deterministic morph, not a fade. Helpers in `manim/derivation_kit.py`:
`glyph("dT")`, `vinc(num, denom)`, `HIGHLIGHT` (teal for symbols being
manipulated).

### 7.2 — Per-step captions
Below the equation, a `Text(font_size=24, color=GREY_B).to_edge(DOWN, buff=1.1)`
names what the step is doing. Cross-fade old → new at each `self.play`. **Be
explicit about non-obvious details** (ch02 R2 feedback):
- Step 2: name the integration variable on each side ("LHS over T, RHS over t").
- Evaluate sub-step: call out the constant merge ("+ C absorbs both
  integration constants into one").
- Step 3 (exponentiate): call out the rename ("e^C is just another constant
  — rename it A").

### 7.3 — Re-center after every step
Per-atom morphs anchor at fixed positions, which causes the equation to
drift left as it grows. After each `self.play(...)` for a step, do a short
follow-up `self.play(VGroup(visible_glyphs).animate.move_to(ORIGIN),
run_time=0.4)`. Newton's cooling video does this for all four operations.

### 7.4 — CI render
`.github/workflows/deploy-pages.yml` has a `render` job that installs LaTeX +
Manim, renders any scene listed in the job, caches the output keyed on
`hashFiles('manim/**')`, and uploads the mp4 as an artifact. The build job
downloads it into `assets/` before the WASM export. Failure-tolerant: if a
render breaks, the chapter still builds and `delib.video`'s `fallback` note
shows instead.

To add a new hero clip:
1. Write `manim/<name>.py` with a `Scene<Name>` class.
2. Add a line to the render job:
   `manim render -qm -o <name> manim/<name>.py Scene<Name> || true`
   and a `find media -name '<name>.mp4' -exec cp {} assets-rendered/ \; || true`
3. Embed in the chapter with `delib.video("<name>.mp4", caption=…, fallback=…)`.

---

## 8. The build pipeline (one-liner mental model)

```
chapter.py → strip stray PEP723 + inline_delib() + prepend PEP723_HEADER
           → marimo export html-wasm --mode run --execute --no-sandbox
           → site/chNN_*/index.html  (+ nav bar, KaTeX, tutor JS, mobile CSS, splash)
```

- `chapters()` globs `ch[0-9][0-9]_*.py`. Anything else (templates, spike
  files) is ignored.
- `--mode run` auto-runs every cell, hides source code, and keeps `mo.ui`
  interactive — the experience students see.
- `--execute` pre-renders every cell's output into the page so it's
  **readable in ~2–3s**; Pyodide then boots in a background worker to
  hydrate the interactive widgets (§4.9). `--no-sandbox` runs that
  build-time execution in the build's own environment, so CI must install
  the full chapter stack (§4.12).
- `WIP_CHAPTERS` (a set) flags a chapter as a work in progress: the
  landing-page card gets dashed-gold "Draft" styling and a Draft pill so
  visitors know. **The page itself still exports `--mode run` with
  `--execute`** (same as production) — `--execute` makes draft loads as
  fast as prod, and the old `--mode edit` path triggered MathML
  triplication on dense math (§4.10), so it bought us nothing and cost
  legibility. Add a slug while authoring; remove it when shipped.
- Each page gets the nav bar (3-col grid: Previous / All chapters / Next +
  absolute-right Tutor button) and the shadow-DOM-aware KaTeX renderer.

---

## 9. Per-chapter checklist (do these in order)

- [ ] Look up the chapter's row in `ROADMAP.md`.
- [ ] **Plan** in chat; wait for approval.
- [ ] Build any new `delib` helper. Self-contained. Unit-test numerically.
      Add to `__init__.py`'s re-exports.
- [ ] Copy `ch02_separable_and_linear.py` as the skeleton for `chNN_topic.py`.
- [ ] Wire the visuals (static field → sliders → flow) using the
      definition-then-vstack pattern (§4.1) for any UI controls.
- [ ] Add the symbol-play beat (`equilibria_report`, `closed_form_report`,
      or a Manim hero clip).
- [ ] 2–4 graded challenges + 1 playground (§5).
- [ ] Tutor block at the end (§6); fresh chapter context string.
- [ ] **Build:** `python scripts/build_wasm_site.py` → no errors.
- [ ] **Grep** the exported HTML for the key prose / CSS / JS strings.
- [ ] Commit, push, wait for CI to deploy.
- [ ] **Refine** based on the user's first-read feedback, in the order they
      send it. If they share a console log, treat it as the primary clue.

---

## 10. Continuity log (read this every time)

What's done and what's still drifting. Update this section at the end of
every chapter so the next session inherits the state.

### Chapters
- **Ch 01–07 — all built and in production** (`WIP_CHAPTERS` is empty).
  See `ROADMAP.md` → *Status* for the per-chapter beat list; that's the
  source of truth for content. A few that carry reusable lessons:
  - **Ch 01** — split-cell + `mo.vstack` slider pattern; intro now grounds
    `y' = f(x,y)` (slope-that-varies-with-position) *before* the rumor hook.
  - **Ch 02** — classify-the-family quiz (`_k` loop-variable fix), per-atom
    Manim hero, "what the formula tells us" beat, inline ✅/❌ marks. Intro
    starts straight on the coffee (the "completely new story" framing was
    cut as needless).
  - **Ch 07** — the deepest prose + platform iteration to date. Its lessons
    are folded into §3 (prose) and §4.9–4.12 (platform) above; don't
    re-learn them. Reverse/math-first Section-4 ordering, trig-only
    derivation (no linear-algebra detour), `transient_steady_figures`
    helper added.
- **Ch 08 — next** (immediate backlog): non-homogeneous equations / driven
  RLC — undetermined coefficients, variation of parameters, superposition.
  New helper likely: a particular + homogeneous decomposition view.

### `delib` toolkit by signature (current)
```
# fields.py
slope_field_data(f, xlim, ylim, *, density=20)
slope_field_plotly(f, xlim, ylim, *, density=18, color, title)
vector_field_plotly(f, xlim, ylim, *, density=16, color, title, scale=1.0, aspect=2.2)
slope_field(f, xlim, ylim, *, density, ax)              # matplotlib
vector_field(F, xlim, ylim, *, density, ax, streamplot) # matplotlib (2-D)
phase_portrait(F, xlim, ylim, *, trajectories, density, ax)  # matplotlib
_field_arrows(GX, GY, S, xspan, yspan, *, density, aspect, scale, head, spread)

# animate.py
animate_time(update_fn, frames, *, fps, fig, backend)
animate_plotly(frames_data, *, layout, fps, transition_ms, easing, template)
flow_field(f, xlim, ylim, *, n_particles=160, n_frames=70, density=16,
           particle_color, field_color, extra_lines, title, seed)
solution_surface(f, t_span, y0_values, *, n_t, colorscale, title)
frame_index(tick, frames)

# solvers.py
solve_ode(f, t_span, y0, *, t_eval=None, method=…)      # f(t, y)
solve_system(F, t_span, y0_vec, *, t_eval=None)          # F(t, y) -> (dy/dt,...)

# ui.py — controls + grading
param_slider(spec)
param_panel(specs)                                       # -> mo.ui.dictionary
run_exercise(code, run_pressed, *, check=None, ns_extra=None)
check_number(ns, *, target, tol, key="answer", ok, hint)
exercise_inputs(default_code, *, run_label)             # -> (ai, gen, code, run)
exercise_ai(gen, ai, code, set_code, key, *, context, coach=True)  # async
exercise_view(prompt, ai, gen, code, run)
ai_code(instruction, current_code, key, *, context, coach, model)  # async

# ui.py — symbol play
equilibria_report(expr_str, *, var="y")
closed_form_report(rhs_str, *, func="y", indep="t")
_guard_expr(expr)
derivation(steps, *, autoplay_ms, title)                # in-browser FLIP player

# ui.py — tutor + assets
video(src, *, caption, width, fallback)
key_field()
key_bridge_widget()
cell_picker_widget()
persist_key(api_field, key_bridge)
tutor_chat(api_field, key_bridge, picker, context, *, prompts, model)
tutor_sidebar(api_field, key_bridge, picker, chatbox, *, title)

# oscillators.py (Ch 6/7)
oscillator_animate(omega0, gamma, F0, omega, *, ic, t_end, n_points, title, ...)
frequency_response(omega0, gamma, *, F0, omega_range, n, height, title)
transient_steady_figures(omega0, gamma, omega, *, t_end, n, height)  # (fig_h, fig_p)
steady_state_amplitude(omega0, gamma, F0, omega)
steady_state_phase(omega0, gamma, omega)
peak_frequency(omega0, gamma)

# widgets.py (graduated from the Lab — Canvas/WebAudio/anywidget)
rumor_crowd()                 # Ch 1
cooling_coffee(T0, Tr, k)     # Ch 2
spring_grab(...)              # Ch 6
resonance_audio(omega0, gamma, F0)   # Ch 7
solution_anatomy(...)         # Ch 7
feedback_form(chapter_name)   # end-of-chapter star + comment
```

### `delib` backlog (from ROADMAP)
- `phase_line(f, xrange)` — Ch 03
- `potential_plot(f, xrange)` — Ch 03
- `bifurcation_diagram(make_f, r_range, xrange)` — Ch 04
- `circle_flow(f, ...)` — Ch 05
- `phase_portrait_plotly(F, xlim, ylim)` — Ch 06
- `nullclines(F, xlim, ylim)` — Ch 07
- `trajectory_3d(F, t_span, starts)` — Ch 10
- `cobweb(g, x0, n)`, `orbit_diagram(make_g, r_range)` — Ch 11
- `symbolic_steps(expr)` — when an in-browser animated derivation is needed
  (Manim remains the hero option)

### Solved infrastructure (don't re-do)
- Nav bar layout: 1fr auto 1fr grid with absolute-positioned Tutor button.
- Tutor sidebar visibility: we own it (force-hidden, nav button toggles).
- Cell pick mode hides the tutor sidebar via `ml-show-tutor` class flip.
- Mobile chart clamp: `@media (max-width:640px)` clamps Plotly to 100% width.
- CI Manim render: cached on `hashFiles('manim/**')`, failure-tolerant.
- Web Worker bridges: `key_bridge_widget`, `cell_picker_widget`.
- Shadow-DOM KaTeX: `MATH_RENDER_JS` walks roots, injects CSS, observes.
- Arrow size: uniform in display-pixel space (set `aspect=` if a future
  chapter has a very different chart box).
- **WASM first paint:** `--execute` embeds rendered outputs; the splash
  lifts on `#root` content (not `.marimo-cell`); Pyodide hydrates widgets
  in the background. Readable in ~2–3s. (§4.9)
- **Build executes cells:** needs the full chapter stack in the build env
  (`pip install . anywidget sympy`) + every runtime import declared in
  `PEP723_HEADER` (now incl. matplotlib); `--no-sandbox` for determinism. (§4.12)
- **Production promotion:** every chapter exports `--mode run` + `--execute`
  regardless. `WIP_CHAPTERS` is purely a *display* flag now — listed slugs
  get the dashed-gold "Draft" card on the landing page so visitors know;
  remove to clear the badge when shipped.
- **Lab demo design (Ch 99):** dramatize the chapter's *thesis*, not a
  consequence — and a top-down 2-D map can't show "altitude," so it can't
  convey "stay at the same height." Demo 14 was rebuilt from a single
  contour-walker into **twin hikers** whose altimeters (accumulated
  $\int M\,dx + N\,dy$) agree at B iff the field is exact — the literal
  "path doesn't matter."

### Open follow-ups (small)
- SymPy first-load can stutter (chunky download). Not blocking; warn in
  chapter prose if the symbol-play beat is heavy.

---

## 11. Voice & style

Match the user's prose register: warm, concrete, declarative. Plain words for
math ("the gap above the room", not "the temperature differential"). One
short idea per sentence. Inline LaTeX for every symbol — never bare
`y'=ay`. Headings are conversational ("Make it your kitchen", "Try it — in
code"), not formal.

When the user pushes back, **diagnose**. They report symptoms, not causes.
Read the file, read the console log, run a sanity script. Don't apply
speculative fixes — make the failure visible (the ai-code error banner, the
console probe pattern), confirm root cause, then patch. The ch01 nav
overlap saga and the ch02 multiple-defs were both solved by reading rather
than guessing.

## Feedback form setup (Google Form)

Each chapter ends with a star + comment box (`delib.feedback_form`) that
posts anonymously to a Google Form whose responses land in a Sheet you own.
Until it's wired up, the widget shows a polite "being set up" placeholder, so
the site is safe to ship before the form exists. To activate it:

1. **Create the form.** [forms.google.com](https://forms.google.com) → blank
   form, e.g. "Math Learn feedback". Two questions are enough:
   - `Rating` — *Short answer* (the widget sends 1–5)
   - `Comment` — *Paragraph*

   Make neither "required" (the widget may send a rating with no comment, or
   vice versa). **The chapter name is folded into the comment automatically**
   (each comment arrives as `Chapter: <name>` then the note), so you don't
   need a separate chapter field.

   *Optional, for a clean separate chapter column:* add a third `Chapter` —
   *Short answer* question and set `GFORM_ENTRY_CHAPTER` to **that field's
   own** `entry.NNN`. Get it wrong or leave it blank and the chapter simply
   rides along in the comment instead — nothing is lost.

2. **Link responses to a Sheet.** Responses tab → the green Sheets icon →
   *Create new spreadsheet*. That's where feedback collects.

3. **Get the `entry.NNN` field IDs.** Click the ⋮ menu → *Get pre-filled
   link*, type a dummy value in each field, *Get link*, copy it. The URL
   contains `entry.123456=...` once per field — note which number goes with
   which question. (Each field's number is distinct; copying the wrong one
   is the usual cause of a field arriving blank.)

4. **Get the action URL.** It's the form's URL with `/viewform` replaced by
   `/formResponse`, i.e. `https://docs.google.com/forms/d/e/<ID>/formResponse`.

5. **Fill in the constants** at the top of
   `differential_equations/delib/widgets.py`:
   ```python
   GFORM_ACTION        = "https://docs.google.com/forms/d/e/<ID>/formResponse"
   GFORM_ENTRY_RATING  = "entry.<the Rating number>"
   GFORM_ENTRY_COMMENT = "entry.<the Comment number>"
   GFORM_ENTRY_CHAPTER = ""   # leave blank → chapter rides in the comment
   GFORM_VIEW_URL      = "https://docs.google.com/forms/d/e/<ID>/viewform"  # optional
   ```
   Only set `GFORM_ENTRY_CHAPTER` if you added the optional `Chapter`
   question and want its own column — and double-check it's *that* field's
   `entry.NNN`, not a copy of the rating/comment one.

6. Rebuild (`python scripts/build_wasm_site.py`) and the box goes live in
   every chapter. Submissions are anonymous; each comment is prefixed with
   `Chapter: <name>` (or the chapter lands in its own column if you wired
   the optional field), so you can always tell which chapter a note is about.

Note: Google Forms doesn't return CORS headers, so the widget POSTs in
`no-cors` mode and treats the request resolving as success — it can't read
the actual HTTP status. Do a test submission after wiring it up and confirm
the row appears in your Sheet.
