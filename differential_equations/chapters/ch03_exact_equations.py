import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go
    import sympy as sp

    import delib
    return delib, go, mo, np, plt, sp


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Chapter 3 — Exact equations & substitutions

        **When the slope field hides a conserved quantity, the solutions are its level curves.**

        By the end of this chapter you should be able to:

        - Recognise an **exact** ODE $M\,dx + N\,dy = 0$ from
          $\partial M/\partial y = \partial N/\partial x$ and recover the
          conserved $F$ with $F_x = M$, $F_y = N$.
        - See solutions as the **level curves** of that $F$, and read off the
          slope field as the gradient direction $-\nabla F$ rotated 90°.
        - Use an **integrating factor** to rescue a not-quite-exact equation —
          and recognise that the Ch 2 first-order-linear formula is just the
          special case $\mu = e^{\int p\,dx}$.
        - Tackle **Bernoulli** $y' + p(x)\,y = q(x)\,y^n$ with the substitution
          $v = y^{1-n}$, and **homogeneous** $y' = F(y/x)$ with $v = y/x$.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, mo):
    # Beat 1 — hook: a hiker on a contour map. Show contours of a smooth F
    # over a patch of "terrain"; the walker stays on one contour the whole way.
    _F_terrain = lambda x, y: (x**2 + y**2) / 4 - 0.6 * (x**2 - y**2 / 3)
    _hike = delib.level_curves(
        _F_terrain, (-3.0, 3.0), (-3.0, 3.0),
        n=120,
        title="A walker's path on a contour map — altitude stays constant",
    )
    mo.vstack([
        mo.md(
            r"""
            ## A hiker reading a contour map

            *(placeholder — hiker story: each contour line on a topographic map
            connects points of equal altitude. Walking along a contour means
            altitude never changes — and that single constraint, written as an
            ODE, is the whole subject of this chapter.)*

            Pick any contour. If you walk along it, your altitude $F(x, y)$
            stays constant — so $dF = 0$ at every step. That equation,
            $F_x\,dx + F_y\,dy = 0$, is the **general form** of an *exact*
            differential equation. Every contour is a solution.
            """
        ),
        _hike,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 2 — concept bridge.
    mo.md(
        r"""
        ## From a conserved quantity to an ODE (and back)

        *(placeholder — bridge: any smooth $F(x, y)$ defines a 1-parameter
        family of curves $F = C$. Differentiating, $F_x + F_y \,dy/dx = 0$, so
        $dy/dx = -F_x/F_y$. Run that backward: any equation of the form
        $M\,dx + N\,dy = 0$ is *asking* whether some $F$ has $F_x = M, F_y = N$.)*

        Differentiate $F(x, y) = C$ implicitly: $F_x + F_y \dfrac{dy}{dx} = 0$,
        so $\dfrac{dy}{dx} = -\dfrac{F_x}{F_y}$. Run that backward — given
        $M\,dx + N\,dy = 0$, we're asking whether some $F$ exists with
        $F_x = M$ and $F_y = N$. When it does, the chapter is done: solutions
        are $F = C$. When it doesn't, we work to make one.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3 — exactness condition.
    mo.md(
        r"""
        ## The exactness condition

        *(placeholder — equality of mixed partials: a smooth $F$ exists with
        $F_x = M$, $F_y = N$ iff $M_y = N_x$. Then recover $F$ by partial
        integration: $F = \int M\,dx + g(y)$, then fix $g$ from $F_y = N$.)*

        $$
        \boxed{\quad M_y = N_x \quad \Longleftrightarrow \quad \text{exact, with } dF = M\,dx + N\,dy.\quad}
        $$

        The recipe for $F$: integrate $M$ in $x$ to get $\int M\,dx + g(y)$,
        then differentiate the result in $y$ and match against $N$ to pin
        down $g(y)$.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Beat 4 — hero visual 1: level curves of F = x^2 + xy + y^2 with the
    # slope field of (M, N) = (2x + y, x + 2y) overlaid. Field rides contours.
    _F = lambda x, y: x**2 + x*y + y**2
    _M = lambda x, y: 2*x + y
    _N = lambda x, y: x + 2*y
    delib.level_curves(
        _F, (-3.0, 3.0), (-3.0, 3.0),
        levels=[0.25, 1.0, 2.0, 4.0, 7.0],
        field=(_M, _N),
        title="Contours of  F = x² + xy + y²  with slope field of  (2x + y) dx + (x + 2y) dy = 0",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        *(placeholder — read the picture: the contours of $F$ are ellipses;
        the slope field arrows are tangent to them everywhere. Pick any
        starting point and a unique ellipse passes through it — that's the
        solution to the IVP.)*
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 5 — live SymPy walk-through.
    mo.md(
        r"""
        ## Recover $F$ from $(M, N)$ — symbolically, live

        *(placeholder — edit $M$ and $N$ below. The cell tests exactness, and
        if exact, runs the partial-integration recipe to recover $F$ and
        prints the implicit solution $F = C$.)*
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    M_input = mo.ui.text(value="2*x + y", full_width=True, label="M(x, y) =")
    N_input = mo.ui.text(value="x + 2*y", full_width=True, label="N(x, y) =")
    mo.vstack([M_input, N_input])
    return M_input, N_input


@app.cell(hide_code=True)
def _(M_input, N_input, mo, sp):
    x, y = sp.symbols("x y", real=True)
    try:
        M_expr = sp.sympify(M_input.value)
        N_expr = sp.sympify(N_input.value)
    except (sp.SympifyError, SyntaxError) as e:
        _out = mo.md(f"*Could not parse:* `{e}`")
    else:
        My = sp.diff(M_expr, y)
        Nx = sp.diff(N_expr, x)
        exact = sp.simplify(My - Nx) == 0
        lines = [
            f"$M_y = {sp.latex(My)}$",
            f"$N_x = {sp.latex(Nx)}$",
        ]
        if exact:
            lines.append("**Exact.** ✓")
            F_partial = sp.integrate(M_expr, x)
            g_prime = sp.simplify(N_expr - sp.diff(F_partial, y))
            g_of_y = sp.integrate(g_prime, y)
            F_full = sp.simplify(F_partial + g_of_y)
            lines.append(f"$F(x, y) = {sp.latex(F_full)}$")
            lines.append(f"Solutions: ${sp.latex(F_full)} = C.$")
        else:
            lines.append("**Not exact** — $M_y \\neq N_x$. "
                         "You'll need an integrating factor (next section).")
        _out = mo.md("\n\n".join(lines))
    _out
    return


@app.cell(hide_code=True)
def _(delib, mo):
    # Beat 6 — slider: morph F = x^2 + a*xy + y^2 from ellipses through
    # degenerate to hyperbolas.
    a_panel = delib.param_panel(
        [{"name": "a", "label": "cross-term coefficient a",
          "start": -3.0, "stop": 3.0, "step": 0.1, "value": 1.0}]
    )
    mo.vstack([
        mo.md(
            r"""
            ## Slider: morph the contours

            *(placeholder — vary $a$ in $F(x, y) = x^2 + a\,xy + y^2$. For
            $|a| < 2$ the contours are ellipses (positive-definite). At
            $|a| = 2$ they degenerate to parallel lines (the conic is a
            double line). For $|a| > 2$ they're hyperbolas. The slope field
            redraws in lockstep — same picture, two views.)*
            """
        ),
        a_panel,
    ])
    return (a_panel,)


@app.cell(hide_code=True)
def _(a_panel, delib):
    a = a_panel.value["a"]
    _F = lambda x, y, _a=a: x**2 + _a*x*y + y**2
    _M = lambda x, y, _a=a: 2*x + _a*y
    _N = lambda x, y, _a=a: _a*x + 2*y
    delib.level_curves(
        _F, (-3.0, 3.0), (-3.0, 3.0),
        levels=[-4.0, -2.0, -0.5, 0.5, 2.0, 4.0, 7.0],
        field=(_M, _N),
        title=f"F(x, y) = x² + {a:+.2f}·xy + y²",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 7 — integrating factors.
    mo.md(
        r"""
        ## When it isn't exact — multiply by $\mu$

        *(placeholder — if $M_y \neq N_x$, look for $\mu(x, y)$ such that
        $(\mu M)_y = (\mu N)_x$. Two clean cases:*

        - $(M_y - N_x)/N$ depends on $x$ only $\Rightarrow$
          $\mu = \exp\!\left(\int (M_y - N_x)/N\,dx\right)$.
        - $(N_x - M_y)/M$ depends on $y$ only $\Rightarrow$
          $\mu = \exp\!\left(\int (N_x - M_y)/M\,dy\right)$.

        *Punch line: the Ch 2 first-order linear formula
        $\mu(x) = e^{\int p\,dx}$ for $y' + p(x)\,y = q(x)$ is exactly this
        — the special case where the equation, rewritten as
        $(p\,y - q)\,dx + dy = 0$, already has $M_y - N_x = p$ depending on
        $x$ only.)*
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, go, mo, np):
    # Beat 8 — Bernoulli payoff: derive the closed-form logistic via v = 1/y,
    # then overlay against a numerical solve_ode of the same equation to show
    # the formula is right.
    _t = np.linspace(0, 8, 200)
    _y0 = 0.1
    _C = 1.0 / _y0 - 1.0
    _y_exact = 1.0 / (1.0 + _C * np.exp(-_t))
    _sol = delib.solve_ode(lambda t, y: y * (1 - y), (0.0, 8.0), _y0, t_eval=_t)
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(
        x=_t, y=_y_exact, mode="lines",
        line=dict(color="#5b7db1", width=3),
        name="closed form  y(t) = 1 / (1 + 9·e^-t)",
    ))
    _fig.add_trace(go.Scatter(
        x=_sol.t, y=_sol.y[0], mode="markers",
        marker=dict(color="#d1495b", size=5, symbol="circle-open"),
        name="numerical (solve_ode)",
    ))
    _fig.add_hline(y=1, line=dict(color="#2a9d8f", dash="dash", width=1.2),
                   annotation_text="carrying capacity y = 1",
                   annotation_position="bottom right")
    _fig.update_layout(
        template="plotly_white",
        title=dict(text="Logistic ẏ = y(1 - y), y(0) = 0.1  —  closed form vs numerical",
                   x=0.02),
        xaxis=dict(title="t"), yaxis=dict(title="y(t)"),
        height=360, margin=dict(l=55, r=20, t=46, b=42),
        paper_bgcolor="white", plot_bgcolor="white",
        legend=dict(x=0.02, y=0.98),
    )
    mo.vstack([
        mo.md(
            r"""
            ## Substitution: Bernoulli in action

            *(placeholder — Bernoulli $y' + p(x)\,y = q(x)\,y^n$. The
            substitution $v = y^{1-n}$ collapses the nonlinearity: a quick
            chain rule gives $v' + (1-n)\,p(x)\,v = (1-n)\,q(x)$ — **linear**.
            Worked example: logistic $\dot y = y(1 - y)$ rewrites as
            $\dot y - y = -y^2$ (Bernoulli with $n = 2$), $v = 1/y$ turns it
            into $\dot v + v = 1$, integrating-factor it, get
            $v = 1 + Ce^{-t}$, invert: $y = 1/(1 + Ce^{-t})$. The numerical
            solution agrees to plotting precision.)*

            *Sibling trick: homogeneous $y' = F(y/x)$ collapses under $v = y/x$
            to a separable equation in $v, x$.*
            """
        ),
        _fig,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it — in code

        *(placeholder — short intro to the 3 challenges.)*
        """
    )
    return


# --- Challenge 1: exactness check + recover F at a point ---------------------
@app.cell
def _(mo):
    e1_get, e1_set = mo.state(
        "# Consider (cos(x) + 2*x*y) dx + (x**2 - sin(y)) dy = 0.\n"
        "# (a) Check exactness.  (b) Recover F.  (c) Evaluate F(1, 0) and put it in `answer`.\n"
        "import sympy as sp\n"
        "x, y = sp.symbols('x y')\n"
        "M = sp.cos(x) + 2*x*y\n"
        "N = x**2 - sp.sin(y)\n"
        "# ... compute F ...\n"
        "answer = ...\n"
    )
    return e1_get, e1_set


@app.cell
def _(delib, e1_get):
    e1_ai, e1_gen, e1_code, e1_run = delib.exercise_inputs(e1_get())
    return e1_ai, e1_code, e1_gen, e1_run


@app.cell
async def _(api_field, delib, e1_ai, e1_code, e1_gen, e1_set, key_bridge):
    await delib.exercise_ai(
        e1_gen, e1_ai, e1_code, e1_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="M = cos(x) + 2 x y; N = x^2 - sin(y). M_y = 2x, N_x = 2x -> exact. "
                "F = integrate M dx = sin(x) + x^2 y + g(y). "
                "F_y = x^2 + g'(y) must equal N = x^2 - sin(y) -> g'(y) = -sin(y) -> g(y) = cos(y). "
                "F = sin(x) + x^2 y + cos(y). F(1, 0) = sin(1) + 0 + 1 = sin(1) + 1 "
                "≈ 1.8414709848. Put float(sin(1) + 1) in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_ai, e1_code, e1_gen, e1_run):
    delib.exercise_view(
        "**1.** For $(\\cos x + 2xy)\\,dx + (x^2 - \\sin y)\\,dy = 0$: check "
        "exactness, recover $F$, and evaluate $F(1, 0)$. Put it in `answer`.",
        e1_ai, e1_gen, e1_code, e1_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_code, e1_run):
    import math
    delib.run_exercise(e1_code.value, e1_run.value, check=lambda ns: delib.check_number(
        ns, target=math.sin(1) + 1.0, tol=1e-3,
        ok="Right — $F = \\sin x + x^2 y + \\cos y$, so $F(1, 0) = \\sin 1 + 1 \\approx 1.8415$.",
        hint="Integrate $M$ in $x$ → $\\sin x + x^2 y + g(y)$; then $F_y = x^2 + g'(y)$ must match $N$.",
    ))
    return


# --- Challenge 2: integrating factor ------------------------------------------
@app.cell
def _(mo):
    e2_get, e2_set = mo.state(
        "# The equation (3*x*y + y**2) dx + (x**2 + x*y) dy = 0 is NOT exact.\n"
        "# Find an integrating factor mu(x) (it depends on x only here).\n"
        "# Then evaluate mu(2) and put it in `answer`.\n"
        "import sympy as sp\n"
        "x, y = sp.symbols('x y')\n"
        "M = 3*x*y + y**2\n"
        "N = x**2 + x*y\n"
        "# Hint: (M_y - N_x) / N should depend on x only.\n"
        "answer = ...\n"
    )
    return e2_get, e2_set


@app.cell
def _(delib, e2_get):
    e2_ai, e2_gen, e2_code, e2_run = delib.exercise_inputs(e2_get())
    return e2_ai, e2_code, e2_gen, e2_run


@app.cell
async def _(api_field, delib, e2_ai, e2_code, e2_gen, e2_set, key_bridge):
    await delib.exercise_ai(
        e2_gen, e2_ai, e2_code, e2_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="M = 3 x y + y^2; N = x^2 + x y. M_y = 3 x + 2 y; N_x = 2 x + y; not equal. "
                "(M_y - N_x) / N = (x + y) / (x(x + y)) = 1/x -- depends on x only. "
                "So mu(x) = exp(integral 1/x dx) = x. Thus mu(2) = 2. Put 2 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_ai, e2_code, e2_gen, e2_run):
    delib.exercise_view(
        "**2.** The equation $(3xy + y^2)\\,dx + (x^2 + xy)\\,dy = 0$ is not "
        "exact. Find an integrating factor $\\mu(x)$ that depends only on $x$, "
        "evaluate $\\mu(2)$, and put it in `answer`.",
        e2_ai, e2_gen, e2_code, e2_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_code, e2_run):
    delib.run_exercise(e2_code.value, e2_run.value, check=lambda ns: delib.check_number(
        ns, target=2.0, tol=1e-4,
        ok="Right — $(M_y - N_x)/N = 1/x$, so $\\mu(x) = x$ and $\\mu(2) = 2$.",
        hint="Compute $(M_y - N_x)/N$; if it depends on $x$ only, then "
             "$\\mu(x) = \\exp\\!\\int (M_y - N_x)/N\\,dx$.",
    ))
    return


# --- Challenge 3: Bernoulli / logistic ----------------------------------------
@app.cell
def _(mo):
    e3_get, e3_set = mo.state(
        "# Solve the logistic equation dy/dt = y * (1 - y) with y(0) = 0.1.\n"
        "# It's Bernoulli with n = 2. The closed form is y(t) = 1 / (1 + C * exp(-t)).\n"
        "# Pin C from y(0) = 0.1, then evaluate y(2) and put it in `answer`.\n"
        "import math\n"
        "answer = ...\n"
    )
    return e3_get, e3_set


@app.cell
def _(delib, e3_get):
    e3_ai, e3_gen, e3_code, e3_run = delib.exercise_inputs(e3_get())
    return e3_ai, e3_code, e3_gen, e3_run


@app.cell
async def _(api_field, delib, e3_ai, e3_code, e3_gen, e3_set, key_bridge):
    await delib.exercise_ai(
        e3_gen, e3_ai, e3_code, e3_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="Logistic ẏ = y(1 - y), y(0) = 0.1. Closed form y(t) = 1/(1 + C exp(-t)). "
                "y(0) = 1/(1 + C) = 0.1 -> C = 9. y(2) = 1/(1 + 9 * exp(-2)) "
                "≈ 1/(1 + 1.2181) ≈ 0.4510. Put float(1/(1 + 9 * math.exp(-2))) in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_ai, e3_code, e3_gen, e3_run):
    delib.exercise_view(
        "**3.** Solve $\\dot y = y(1 - y)$ with $y(0) = 0.1$ via Bernoulli "
        "substitution and evaluate $y(2)$. Put it in `answer`.",
        e3_ai, e3_gen, e3_code, e3_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_code, e3_run):
    import math
    target = 1.0 / (1.0 + 9.0 * math.exp(-2.0))
    delib.run_exercise(e3_code.value, e3_run.value, check=lambda ns: delib.check_number(
        ns, target=target, tol=1e-3,
        ok="Right — $y(0) = 0.1$ pins $C = 9$, so $y(2) = 1/(1 + 9 e^{-2}) \\approx 0.451$.",
        hint="$v = 1/y$ turns the equation into $\\dot v + v = 1$; integrate to get "
             "$v = 1 + Ce^{-t}$, then invert.",
    ))
    return


# --- Playground ----------------------------------------------------------------
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## Playground — free exploration

        No task, no grading. Type any Python, or ask the tutor (✨) to write it,
        then **Run** to see the result.
        """
    )
    return


@app.cell
def _(mo):
    pg_get, pg_set = mo.state(
        "# Try a different conserved quantity. Edit F and watch its contours.\n"
        "F = lambda x, y: x**2 - y**2\n"
        "view = delib.level_curves(F, (-3, 3), (-3, 3),\n"
        "                          levels=[-4, -1, 0, 1, 4],\n"
        "                          field=True,\n"
        "                          title='Hyperbolas: F = x² - y²')\n"
    )
    return pg_get, pg_set


@app.cell
def _(delib, pg_get):
    pg_ai, pg_gen, pg_code, pg_run = delib.exercise_inputs(pg_get(), run_label="Run")
    return pg_ai, pg_code, pg_gen, pg_run


@app.cell
async def _(api_field, delib, key_bridge, pg_ai, pg_code, pg_gen, pg_set):
    await delib.exercise_ai(
        pg_gen, pg_ai, pg_code, pg_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        coach=False,
        context="Open sandbox for chapter 3 (exact equations, level curves, "
                "integrating factors, Bernoulli). Helpers: "
                "delib.level_curves(F, xrange, yrange, levels=..., field=True or (M, N)). "
                "Write complete runnable code; assign a Plotly figure to `view`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, pg_ai, pg_code, pg_gen, pg_run):
    delib.exercise_view(None, pg_ai, pg_gen, pg_code, pg_run)
    return


@app.cell(hide_code=True)
def _(delib, pg_code, pg_run):
    delib.run_exercise(pg_code.value, pg_run.value)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Recap & what's next

        *(placeholder — recap: exact $\Leftrightarrow$ a conserved $F$ exists
        $\Leftrightarrow$ solutions are its level curves. Integrating factors
        and substitutions are tactics to re-express a non-exact equation until
        it becomes exact (or linear). Next: Ch 04 — numerical methods, for
        when no clever change of variables saves you and you walk the field
        step by step. The slope-field picture from Ch 1 will turn into actual
        simulator steps you can step too big and watch blow up.)*
        """
    )
    return


# --- Tutor (BYO-key chat, from delib) ------------------------------------------
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
    return


@app.cell
def _(api_field, delib, key_bridge, picker):
    chatbox = delib.tutor_chat(
        api_field, key_bridge, picker,
        "This is Chapter 3 of a differential-equations course: exact equations "
        "and substitutions, anchored to the hiker-on-a-contour-map story. Key "
        "ideas: exactness condition M_y = N_x; solutions of an exact ODE are "
        "the level curves of a conserved F with F_x = M, F_y = N; integrating "
        "factors rescue near-exact equations (and the Ch 2 linear-ODE formula "
        "is the special case); Bernoulli y' + p y = q y^n linearises under "
        "v = y^(1-n); homogeneous y' = F(y/x) collapses under v = y/x. The "
        "chapter's worked Bernoulli example is the logistic equation — the "
        "same one whose numerical solution opened Ch 1.",
        prompts=[
            "explain this chapter in a paragraph",
            "show me a non-exact equation and the integrating factor that fixes it",
            "solve y' = y - y^3 by separating variables",
        ],
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge, picker):
    delib.tutor_sidebar(api_field, key_bridge, picker, chatbox)
    return


if __name__ == "__main__":
    app.run()
