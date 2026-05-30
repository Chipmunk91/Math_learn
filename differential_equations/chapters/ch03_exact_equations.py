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
def _(delib, mo, np):
    # Beat 1 — hook: a hiker on a contour map. Synthetic but topographically
    # honest terrain: one Gaussian peak in the upper right, one Gaussian basin
    # in the lower left. The contour ring around either feature is a solution
    # to the chapter's ODE form.
    _F_terrain = lambda x, y: (
        np.exp(-((x - 1.2)**2 + (y - 0.6)**2) / 1.4)
        - 0.65 * np.exp(-((x + 1.0)**2 + (y + 0.8)**2) / 1.8)
    )
    _hike = delib.level_curves(
        _F_terrain, (-3.0, 3.0), (-3.0, 3.0),
        n=140,
        title="A topographic map — altitude is a function of position, F(x, y)",
    )
    mo.vstack([
        mo.md(
            r"""
            ## A hiker reading a contour map

            If you've ever read a topographic map, you've already seen the
            picture for this chapter.

            Every closed loop on the map is a **contour line** — every point
            on the loop has the same altitude $F(x, y)$. Set out walking along
            a contour and your altitude doesn't change. A small step
            $(dx, dy)$ keeps you on the same line, so
            $dF = F_x\,dx + F_y\,dy = 0$ at every step. Stare at that for a
            second: it's an ordinary differential equation. The contour you're
            walking is a **solution** of it. The whole map is a phase
            portrait.

            The figure below is synthetic — a Gaussian peak in the upper
            right, a shallower basin in the lower left — but the principle is
            the same as any USGS quad sheet. The nested rings around the peak
            are level sets of "stay this high." The ones around the basin are
            "stay this low." Pick any of them and you've drawn a solution
            curve of an ODE.
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

        The hook hides two statements glued together, and they're worth
        pulling apart.

        **One direction.** Pick any smooth $F(x, y)$. The equation
        $F(x, y) = C$ traces out a curve for each $C$ — a 1-parameter family
        of contours. Differentiate implicitly:

        $$
        F_x + F_y \,\frac{dy}{dx} = 0
        \;\;\Longrightarrow\;\;
        \frac{dy}{dx} = -\frac{F_x}{F_y}.
        $$

        Every conserved quantity comes with a slope field attached to it,
        perpendicular to $\nabla F$. Going the other way along that field is
        going *along* a contour.

        **The other direction.** Run the question backward. Given an ODE in
        the symmetric form

        $$
        M(x, y)\,dx + N(x, y)\,dy = 0,
        $$

        we're asking whether some $F$ exists with $F_x = M$ and $F_y = N$. If
        yes, the chapter is essentially done — solutions are the level curves
        $F = C$, and you're hiking on a contour map. If no, the next two
        sections are about *making* one: multiply by a clever factor, or
        change variables.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3 — exactness condition.
    mo.md(
        r"""
        ## The exactness condition

        Here's the test. Suppose $F$ does exist with $F_x = M$ and $F_y = N$.
        Differentiate $M$ with respect to $y$ — that's $F_{xy}$. Differentiate
        $N$ with respect to $x$ — that's $F_{yx}$. For any smooth $F$, mixed
        partials are equal, so

        $$
        \boxed{\quad M_y = N_x \quad}
        $$

        as a **necessary condition** for exactness. The converse holds on any
        simply connected region (the Poincaré lemma): if $M_y = N_x$
        throughout a rectangle, then an $F$ exists there. So on the
        rectangles we'll work with, the boxed condition is also sufficient.

        **The recipe for $F$.** Once exact, recover $F$ in two short steps:

        1. **Integrate $M$ in $x$:** $\displaystyle F = \int M\,dx + g(y)$. The
           "constant" of integration depends on $y$ — integration in $x$
           ignored $y$, so anything that's a function of $y$ alone is fair.
        2. **Differentiate that in $y$ and match against $N$:**
           $\displaystyle F_y = \frac{\partial}{\partial y}\!\int M\,dx + g'(y) = N$.
           Solve for $g'(y)$, integrate once more, and you have $F$.
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
        Read the picture in two passes.

        **The contours.** They're ellipses tilted at 45°. The conic
        $x^2 + xy + y^2 = C$ is positive-definite (discriminant
        $1^2 - 4\cdot 1\cdot 1 = -3 < 0$), so the level sets are closed loops
        at every positive $C$, nested around the origin.

        **The arrows.** Each one points along $(1, dy/dx) = (1, -M/N) =
        (1, -(2x+y)/(x+2y))$. Look at any arrow and the contour underneath
        it: the arrow is tangent. The ellipse *is* the solution; the slope
        field *is* the same picture, viewed twice. That equivalence is the
        whole moral of the chapter in one figure.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 5 — live SymPy walk-through.
    mo.md(
        r"""
        ## Recover $F$ from $(M, N)$ — symbolically, live

        Edit $M$ and $N$ below. The cell computes $M_y$ and $N_x$, compares
        them, and — when they agree — walks the partial-integration recipe
        from the previous section to give you $F$ and the implicit solution
        $F = C$.

        A few to try (each says something different):

        - $M = y\cos x + 2xy$, $N = \sin x + x^2 - 2$. Exact? What does the
          implicit solution look like — does it factor?
        - $M = e^y$, $N = x\,e^y$. The implicit solution is the cleanest one
          you'll see all chapter.
        - $M = y$, $N = -x$. (Spoiler: not exact — and you can't fix it with
          a $\mu$ that depends on $x$ or $y$ alone.)
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
    x, y = sp.symbols("x y")
    try:
        # Pass our (x, y) into sympify's namespace so it doesn't create fresh
        # Symbols with mismatched assumptions, which would silently break diff.
        M_expr = sp.sympify(M_input.value, locals={"x": x, "y": y})
        N_expr = sp.sympify(N_input.value, locals={"x": x, "y": y})
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

            Vary $a$ in $F(x, y) = x^2 + a\,xy + y^2$. The conic changes
            character three different ways:

            - **$|a| < 2$:** positive-definite, contours are **ellipses**
              tilted around the origin. Same story as the previous figure.
            - **$a = \pm 2$:** **degenerate.** The polynomial factors as
              $(x \pm y)^2$, and the level sets collapse to *pairs of parallel
              lines*. The gradient vanishes along $y = \mp x$, so the slope
              field becomes singular there — the arrows go to zero length.
            - **$|a| > 2$:** indefinite, contours are **hyperbolas.** Level
              sets exist for both positive and negative $C$, and the negative
              ones snake along the perpendicular axis.

            Drag through $a = 2$ slowly and watch the closed loops snap open
            into the unbounded branches. That's a one-parameter bifurcation
            of the conic, and it's a foretaste of Ch 6 — where a parameter
            sweep makes fixed points appear, vanish, or swap stability.
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

        When $M_y \neq N_x$, look for a multiplier $\mu(x, y)$ such that
        $\mu M\,dx + \mu N\,dy = 0$ *is* exact. The exactness condition
        $(\mu M)_y = (\mu N)_x$ becomes a PDE for $\mu$ — solvable in general
        only when $\mu$ is forced to be simple. Two clean cases that keep
        things ODE-only:

        - If $\dfrac{M_y - N_x}{N}$ depends on $x$ only, then $\mu = \mu(x)$
          exists and

          $$
          \mu(x) = \exp\!\left(\int \frac{M_y - N_x}{N}\,dx\right).
          $$

        - If $\dfrac{N_x - M_y}{M}$ depends on $y$ only, then $\mu = \mu(y)$
          exists with the symmetric formula in $y$.

        ### The Ch 2 connection (punchline)

        Take any first-order linear equation $y' + p(x)\,y = q(x)$ and rewrite
        it as the symmetric form

        $$
        \bigl(p(x)\,y - q(x)\bigr)\,dx + dy = 0.
        $$

        Now $M = p(x)\,y - q(x)$ and $N = 1$, so $M_y - N_x = p(x)$ — already
        depends on $x$ alone. Plug into the box above:

        $$
        \mu(x) = \exp\!\left(\int p(x)\,dx\right).
        $$

        That's exactly the integrating factor from Ch 2. The "trick" wasn't a
        trick — it was the exactness condition all along, specialised to
        $N = 1$. One mechanism, two appearances.
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

            When the equation is nonlinear but in the **Bernoulli form**

            $$
            y' + p(x)\,y = q(x)\,y^n, \qquad n \neq 0, 1,
            $$

            the substitution $v = y^{1-n}$ collapses the nonlinearity.
            Differentiating gives $v' = (1-n)\,y^{-n}\,y'$. Divide the
            original equation by $y^n$ and multiply by $1-n$:

            $$
            v' + (1 - n)\,p(x)\,v = (1 - n)\,q(x).
            $$

            **Linear in $v$.** The previous section applies — integrating
            factor, integrate, invert with $y = v^{1/(1-n)}$.

            ### The logistic, from scratch

            Take $\dot y = y(1 - y)$ — the **same equation** whose numerical
            S-curve opened Ch 1. Rewrite as $\dot y - y = -y^2$. Bernoulli
            with $p = -1$, $q = -1$, $n = 2$. Set $v = y^{1-2} = 1/y$; the
            transformed equation is

            $$
            \dot v + v = 1.
            $$

            Solve: $v_h = Ce^{-t}$, $v_p = 1$, so $v = 1 + Ce^{-t}$, and
            inverting,

            $$
            y(t) = \frac{1}{1 + Ce^{-t}}.
            $$

            With $y(0) = 0.1$, the constant $C = 9$. The plot below overlays
            this closed form on `delib.solve_ode` running the same equation
            — they agree to plotting precision, which is the only proof we
            need that Ch 1's S-curve was always going to be a sigmoid.

            *Sibling trick.* For a **homogeneous** equation $y' = F(y/x)$, the
            substitution $v = y/x$ reduces it to a separable equation in
            $(v, x)$. Different change of variable, same idea: rewrite until
            a tool from earlier in the chapter applies.
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

        Three drills, each one minute of thinking and a few lines of code, in
        order of cost:

        1. **Read the test, recover $F$, plug in a number.** This is the whole
           chapter in 3 SymPy calls.
        2. **Find an integrating factor.** When the test fails, the diagnostic
           ratio $(M_y - N_x)/N$ tells you whether $\mu(x)$ alone will do.
        3. **Solve a Bernoulli equation.** The same $v = y^{1-n}$ trick on a
           specific case, with a numeric answer at a specific point.
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

        **Recap.** *Exact* equations are the ones whose slope field comes
        from a conserved $F$ — and the test for that is the boxed
        $M_y = N_x$. When it holds, solutions are the level curves $F = C$,
        and the chapter's hero figure (contours + arrows = one picture)
        becomes a recipe you can hand-execute. When the test fails, two
        tactics buy it back:

        - **Integrating factor.** Multiply through by $\mu$ until the
          rewritten equation passes the test. The Ch 2 formula
          $\mu = e^{\int p\,dx}$ was this all along.
        - **Substitution.** Change variables until the equation is linear
          (Bernoulli) or separable (homogeneous). The Ch 1 logistic S-curve
          came out of *this* — Bernoulli with $n = 2$, closed-form solved
          two chapters later.

        **What's next.** Sometimes no clever rewriting saves you — the
        equation is exact in no coordinates and substitutes to nothing nice.
        **Ch 4** is what you do then: walk the slope field one tiny step at
        a time and *simulate*. The same field picture from Ch 1 returns as
        actual simulator steps you can step too big and watch blow up —
        which is exactly what happens to MuJoCo or PyBullet when you pick
        the wrong $\Delta t$.
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
