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
        # Chapter 3, Part 2 — Making it not matter

        **When the test fails, rewrite until it passes.**

        Part 1 left off with a clean recipe: test the equation, and if it
        passes the $M_y = N_x$ check, recover $F$ and read off the contour
        map. But the world is full of equations that *don't* pass — most
        slope fields don't come from a conserved $F$. This part is about
        what to do when the test fails: rewrite the equation until it
        does pass, or change variables until it becomes something we
        already know how to solve.

        By the end of this part you should be able to:

        - Recognise when an equation fails the exactness test, and use
          the **diagnostic ratio** $(M_y - N_x)/N$ to check whether a
          multiplier $\mu(x)$ will rescue it.
        - Apply an **integrating factor** to turn a non-exact equation
          into an exact one — and see that Chapter 2's linear-equation
          formula was exactly this with $N = 1$.
        - Recognise the **Bernoulli** shape $y' + p(x)\,y = q(x)\,y^n$,
          use the substitution $v = y^{1-n}$ to flatten the
          nonlinearity, and derive Chapter 1's logistic S-curve as an
          explicit formula.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Hook — concrete equation that fails the exactness test; motivates the
    # rescue tactic and previews the Ch 2 connection.
    mo.md(
        r"""
        ## When the test fails — what now?

        Part 1 ended on a high. Pass the $M_y = N_x$ test, recover $F$
        by partial integration, and the equation's solutions are the
        contours of a hidden landscape. We even drew the map.

        But here's an equation:

        $$
        (3xy + y^2)\,dx + (x^2 + xy)\,dy = 0.
        $$

        On the surface, it has the same shape as the equations from
        Part 1 — two functions $M$ and $N$ of two variables, the
        promised symmetric form. Let's run the test:

        - $M = 3xy + y^2$, so $M_y = 3x + 2y$.
        - $N = x^2 + xy$, so $N_x = 2x + y$.

        Those aren't equal. The test fails. There is no hidden landscape
        behind *this* equation — no contour map to draw, no clean recipe
        to apply.

        Or — is there?

        This part is about the situation where the original equation
        fails the test, but a slightly *rewritten* version of it passes.
        The rewriting trick is reliable enough to deserve a name: the
        **integrating factor**. We'll derive it, name the key quantity
        (the *diagnostic ratio*), and discover a satisfying twist — the
        trick we'll use here is the same trick Chapter 2 used to solve
        linear equations. One mechanism, two appearances.

        For nonlinear equations the integrating factor doesn't reach,
        there's a second tactic — **substitution** — that we'll meet in
        the back half of this part. The closing payoff is the explicit
        formula for Chapter 1's S-curve.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 7 — integrating factors: intro before the Manim derivation.
    mo.md(
        r"""
        ## When it isn't exact — multiply by $\mu$

        The exactness test gives a clear binary: equation passes, look for
        $F$; equation fails, no $F$ to find. But "no $F$ to find" isn't a
        permanent verdict. There's a way to **rescue** a non-exact
        equation: multiply both sides by a cleverly-chosen function
        $\mu(x, y)$ — called an **integrating factor** — picked so that
        the rescaled equation

        $$
        \mu(x, y)\,M\,dx \;+\; \mu(x, y)\,N\,dy \;=\; 0
        $$

        *does* pass the exactness test. The contour map we couldn't find
        before is now hiding behind the rescaled equation, and we can
        recover it with the recipe from Part 1.

        How do we find such a $\mu$? The derivation is short but worth
        following one move at a time — particularly the moment where what
        looks like a hard equation in two variables collapses into an
        easy one, because we make a single inspired guess about what
        $\mu$ should look like. The video below walks through it.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Beat 7 (cont.) — Manim hero: derive μ(x) = exp(∫ (M_y - N_x)/N dx).
    delib.video(
        "integrating_factor.mp4",
        caption="Deriving the integrating factor μ(x), one move at a time",
        fallback="The integrating-factor derivation is being rendered "
                 "(see manim/integrating_factor.py).",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 7 (cont.) — after the video: diagnostic ratio name + symmetric μ(y) case
    # + the Ch 2 connection as the prose punchline.
    mo.md(
        r"""
        ### A name for the key quantity

        The whole recipe boils down to a single expression — the thing
        we integrated:

        $$
        \frac{M_y - N_x}{N}.
        $$

        It's useful enough to give a name. Call it the **diagnostic
        ratio** for the equation, because computing it tells you two
        things at once:

        - **Diagnosis.** Plug your specific $M$ and $N$ in and simplify.
          If the result is a function of $x$ alone — no $y$ left
          anywhere — then a $\mu$ depending only on $x$ does exist, and
          the recipe applies. If $y$ doesn't cancel out, this particular
          recipe won't save the equation, and we'd need a different
          tactic.
        - **The formula.** When the diagnosis comes back clean, the
          same ratio is exactly what you integrate to recover $\mu$:

          $$
          \mu(x) = \exp\!\left(\int \frac{M_y - N_x}{N}\,dx\right).
          $$

        One computation, two answers — *whether* the rescue works and
        *what the rescue function looks like* — read off the same line.

        ### The other half — when $\mu$ depends on $y$ instead

        The video walked through the case $\mu = \mu(x)$. There's a
        mirror version where we guess $\mu = \mu(y)$ instead, and the
        same derivation runs through with the roles of $x$ and $y$
        swapped — *including* the diagnostic ratio, which becomes

        $$
        \frac{N_x - M_y}{M}
        $$

        (sign flip on top, $M$ in the denominator now instead of $N$).
        When *this* ratio depends on $y$ alone, then

        $$
        \mu(y) \;=\; \exp\!\left(\int \frac{N_x - M_y}{M}\,dy\right).
        $$

        **In practice**, when you meet a non-exact equation, you
        compute both diagnostic ratios and pick whichever simplifies
        to a function of just one variable. If neither does, you're in
        harder territory: $\mu$ has to depend on both $x$ and $y$, and
        the recipe stops working as a one-line formula. That happens;
        integrating factors aren't a silver bullet. But the catalogue
        of equations they *do* rescue is large.

        ### The Chapter 2 connection — one mechanism, two appearances

        Here's the punchline of this section, and it's a satisfying one.

        Take any first-order linear equation from Chapter 2:

        $$
        y' + p(x)\,y = q(x).
        $$

        Rewrite it in the symmetric $M\,dx + N\,dy = 0$ form. Moving
        everything to one side:

        $$
        \bigl(p(x)\,y - q(x)\bigr)\,dx \;+\; dy \;=\; 0.
        $$

        So $M = p(x)\,y - q(x)$ and $N = 1$. Now run the diagnostic
        ratio for this equation:

        $$
        \frac{M_y - N_x}{N} \;=\; \frac{p(x) - 0}{1} \;=\; p(x).
        $$

        It depends on $x$ alone (since $p$ is a function of $x$ alone)
        — the side condition for $\mu(x)$ is met automatically. Plug
        the ratio into the formula the video just derived:

        $$
        \mu(x) \;=\; \exp\!\left(\int p(x)\,dx\right).
        $$

        That's *exactly* the integrating factor we derived in Chapter 2
        for linear equations — there, by requiring the left-hand side of
        $y' + p(t)\,y = q(t)$ to collapse into $(\mu y)'$. Here, the
        same formula falls out of a totally different starting point:
        requiring the *rescaled* equation $\mu M\,dx + \mu N\,dy = 0$
        to pass the exactness test, then specialising to $N = 1$.

        Two completely different roads, one formula at the end. **One
        mechanism, two appearances.** Later chapters will keep pulling
        that thread: most of the methods that look like one-off tricks
        turn out to be special cases of more general ideas.
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
            ## Substitution: when nonlinearity has a useful shape

            The integrating-factor recipe handles every *linear*
            first-order ODE — a lot of equations, but not all of them.
            Many real rate laws are nonlinear: populations limited by
            carrying capacity, autocatalytic reactions, the rumor on
            the 1,000-person campus from Chapter 1. None of those rate
            laws are linear in $y$.

            So when we meet a nonlinear equation, is there hope, or do
            we hand off to numerical methods?

            Sometimes there's still hope — when the nonlinearity
            happens to have a particular *shape*, a clever
            **substitution** can flatten it back into one of the
            equations we already know how to solve. We'll look at one
            shape in detail (it covers a surprising fraction of the
            first-order equations you'll meet in physics and biology),
            then briefly mention a sibling.

            ### The Bernoulli shape

            An equation of the form

            $$
            y' + p(x)\,y \;=\; q(x)\,y^n
            $$

            is called a **Bernoulli equation** when $n$ is anything
            other than $0$ or $1$. (If $n = 0$, the right side is just
            $q(x)$ and we're already linear; if $n = 1$, we can move
            the $y$ term to the left and we're *still* linear.) It's
            the cases like $n = 2, 3, \tfrac{1}{2}, -1$ — where the
            right-hand side is *genuinely* nonlinear in $y$ — that we
            want a new tool for.

            **The idea.** We want the equation to be linear in some new
            variable, because then the integrating-factor recipe from
            the last section applies directly. So we look for a
            substitution $v = (\text{some function of } y)$ that
            *swallows* the awkward $y^n$.

            Let's not guess — let's compute. Divide the original
            equation through by $y^n$ to isolate the nonlinear piece:

            $$
            \frac{y'}{y^n} \;+\; p(x)\,y^{1-n} \;=\; q(x).
            $$

            The middle term has $y^{1-n}$ sitting in it. If we
            **defined** $v$ to be that exact thing —

            $$
            v \;=\; y^{1-n},
            $$

            — then the middle term becomes $p(x)\,v$, which is linear
            in $v$. So we now know what the substitution should be.

            Does it also work for the first term, $y'/y^n$? Let's
            check by computing $v'$ from our definition:

            $$
            \frac{dv}{dx} \;=\; (1 - n)\,y^{-n}\,\frac{dy}{dx}
            \;=\; (1 - n)\,\frac{y'}{y^n}.
            $$

            Almost — the first term in our equation is $y'/y^n$, but
            $v'$ has an extra factor of $(1 - n)$ that needs absorbing.
            Easy fix: multiply our rearranged equation through by
            $(1 - n)$:

            $$
            (1 - n)\,\frac{y'}{y^n} + (1 - n)\,p(x)\,y^{1-n}
            \;=\; (1 - n)\,q(x).
            $$

            Now substitute $v = y^{1-n}$ and
            $v' = (1 - n)\,y'/y^n$:

            $$
            \boxed{\quad v' \;+\; (1 - n)\,p(x)\,v
            \;=\; (1 - n)\,q(x).\quad}
            $$

            **That's linear in $v$.** The integrating-factor recipe
            from the last section solves it. Once we have $v(x)$, we
            get $y$ back by inverting the substitution:
            $y = v^{1/(1-n)}$.

            The same recipe — *try $v = y^{1-n}$, the equation goes
            linear, solve, invert* — works for every Bernoulli equation
            regardless of the specific $p$, $q$, or $n$.

            ### The logistic — Chapter 1's rumor, solved

            Let's apply this to the equation that opened Chapter 1:
            the rumor spreading across a campus, the S-curve in time.
            Normalised to a population of $1$, the rate law is

            $$
            \dot y \;=\; y\,(1 - y).
            $$

            Multiply out and move the $y$ term to the left:

            $$
            \dot y - y \;=\; -y^2.
            $$

            Now match against the Bernoulli template
            $y' + p\,y = q\,y^n$:

            - The coefficient of $y$ on the left is $-1$, so $p = -1$.
            - The coefficient of $y^n$ on the right is $-1$, so
              $q = -1$.
            - The exponent on the right is $2$, so $n = 2$.

            The substitution is therefore $v = y^{1-2} = 1/y$. Plug
            into the boxed formula:

            $$
            v' + (1 - 2)(-1)\,v \;=\; (1 - 2)(-1),
            $$

            which simplifies (since $(-1)(-1) = +1$ on both sides) to

            $$
            \dot v + v \;=\; 1.
            $$

            That's a linear first-order ODE in $v$ — exactly the kind
            we just learned how to solve. The integrating factor is
            $\mu(t) = \exp\bigl(\int 1\,dt\bigr) = e^t$. Multiplying
            through: $(e^t v)' = e^t$. Integrating: $e^t v = e^t + C$.
            Dividing:

            $$
            v(t) \;=\; 1 + C\,e^{-t}.
            $$

            And the final move — invert the substitution to recover
            $y$:

            $$
            y(t) \;=\; \frac{1}{v(t)} \;=\; \frac{1}{1 + C\,e^{-t}}.
            $$

            There's the S-curve, in closed form.

            To make it concrete: starting from $y(0) = 0.1$ (the
            rumor's initial reach in Chapter 1), the condition
            $1/(1 + C) = 0.1$ pins $C = 9$, so
            $y(t) = 1/(1 + 9\,e^{-t})$. Below, this formula is plotted
            against the numerical solution `delib.solve_ode` would
            produce from the same equation and initial condition:
            """
        ),
        _fig,
        mo.md(
            r"""
            The two are indistinguishable to plotting precision —
            proof that the S-curve we read off Chapter 1's slope field
            was always going to be this exact sigmoid. Bernoulli
            substitution turned the nonlinear equation linear, and the
            integrating-factor recipe finished the job.

            ### A sibling — the homogeneous shape

            The Bernoulli substitution worked by choosing $v$ to
            swallow the awkward $y^n$. The same kind of trick — pick a
            substitution that gets you to an equation you already know
            how to solve — works for other shapes too. The most common
            sibling is the **homogeneous** equation,

            $$
            y' \;=\; F\!\left(\frac{y}{x}\right),
            $$

            where the right-hand side depends on $y$ and $x$ only
            through their ratio. The natural guess here is $v = y/x$.
            A short chain-rule calculation turns the equation into a
            **separable** one in $(v, x)$ — the simplest shape from
            Chapter 2 — and two integrations finish the job.

            *Different shape, different substitution, same idea.* When
            a method has a clear target in mind — "get to linear",
            "get to separable" — the substitution to try is often just
            whatever is standing in the way.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it — in code

        Three drills for this part, in order of cost:

        1. **Find an integrating factor $\mu(x)$.** Compute the
           diagnostic ratio, integrate, read off $\mu$ at a specific
           value of $x$. The same equation the hook posed.
        2. **Find an integrating factor $\mu(y)$ — the mirror case.**
           Same recipe with the roles of $x$ and $y$ swapped.
        3. **Solve a Bernoulli equation in closed form.** The
           $v = y^{1-n}$ substitution, then read off $y$ at a specific
           time. Chapter 1's logistic equation, this time as an
           explicit formula.
        """
    )
    return


# --- Challenge 1: integrating factor μ(x) ------------------------------------
@app.cell
def _(mo):
    e1_get, e1_set = mo.state(
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
        context="M = 3 x y + y^2; N = x^2 + x y. M_y = 3 x + 2 y; N_x = 2 x + y; not equal. "
                "(M_y - N_x) / N = (x + y) / (x(x + y)) = 1/x -- depends on x only. "
                "So mu(x) = exp(integral 1/x dx) = x. Thus mu(2) = 2. Put 2 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_ai, e1_code, e1_gen, e1_run):
    delib.exercise_view(
        "**1.** The equation $(3xy + y^2)\\,dx + (x^2 + xy)\\,dy = 0$ is "
        "not exact. Find an integrating factor $\\mu(x)$ that depends "
        "only on $x$, evaluate $\\mu(2)$, and put it in `answer`.",
        e1_ai, e1_gen, e1_code, e1_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_code, e1_run):
    delib.run_exercise(e1_code.value, e1_run.value, check=lambda ns: delib.check_number(
        ns, target=2.0, tol=1e-4,
        ok="Right — $(M_y - N_x)/N = 1/x$, so $\\mu(x) = x$ and $\\mu(2) = 2$.",
        hint="Compute $(M_y - N_x)/N$; if it depends on $x$ only, then "
             "$\\mu(x) = \\exp\\!\\int (M_y - N_x)/N\\,dx$.",
    ))
    return


# --- Challenge 2: integrating factor μ(y) (the mirror case) -------------------
@app.cell
def _(mo):
    e2_get, e2_set = mo.state(
        "# The equation y**2 dx - x*y dy = 0 is NOT exact, and (M_y - N_x)/N\n"
        "# is NOT a function of x alone. Try the mirror case: find mu(y)\n"
        "# (depends on y only) and evaluate it at y = 2. Put mu(2) in `answer`.\n"
        "import sympy as sp\n"
        "x, y = sp.symbols('x y')\n"
        "M = y**2\n"
        "N = -x*y\n"
        "# Hint: (N_x - M_y) / M should depend on y only.\n"
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
        context="M = y^2; N = -x y. M_y = 2 y; N_x = -y; not equal. "
                "(N_x - M_y)/M = (-y - 2y)/y^2 = -3y/y^2 = -3/y -- depends on y only. "
                "So mu(y) = exp(integral -3/y dy) = exp(-3 ln y) = 1/y^3. "
                "Thus mu(2) = 1/8 = 0.125. Put 1/8 (or 0.125) in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_ai, e2_code, e2_gen, e2_run):
    delib.exercise_view(
        "**2.** The equation $y^2\\,dx - xy\\,dy = 0$ is also not exact, "
        "and its $(M_y - N_x)/N$ ratio doesn't simplify to a function of "
        "$x$ alone. Try the mirror recipe: find $\\mu(y)$ (depending only "
        "on $y$), evaluate $\\mu(2)$, and put it in `answer`.",
        e2_ai, e2_gen, e2_code, e2_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_code, e2_run):
    delib.run_exercise(e2_code.value, e2_run.value, check=lambda ns: delib.check_number(
        ns, target=0.125, tol=1e-4,
        ok="Right — $(N_x - M_y)/M = -3/y$, so $\\mu(y) = 1/y^3$ and "
           "$\\mu(2) = 1/8$.",
        hint="Compute $(N_x - M_y)/M$. If it depends on $y$ only, then "
             "$\\mu(y) = \\exp\\!\\int (N_x - M_y)/M\\,dy$.",
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

        No task, no grading. Type any Python, or ask the tutor (✨) to
        write it, then **Run** to see the result.
        """
    )
    return


@app.cell
def _(mo):
    pg_get, pg_set = mo.state(
        "# Try a non-exact equation. Run the diagnostic ratios and see\n"
        "# which (if either) gives a one-variable function.\n"
        "import sympy as sp\n"
        "x, y = sp.symbols('x y')\n"
        "M = 2*x*y + y**2\n"
        "N = x**2 + 2*x*y\n"
        "My, Nx = sp.diff(M, y), sp.diff(N, x)\n"
        "ratio_x = sp.simplify((My - Nx) / N)  # function of x only?\n"
        "ratio_y = sp.simplify((Nx - My) / M)  # function of y only?\n"
        "view = mo.md(\n"
        "    f'M_y = {sp.latex(My)}; N_x = {sp.latex(Nx)}'\n"
        "    f'  ;  diagnostic ratios:'\n"
        "    f'  (M_y - N_x)/N = {sp.latex(ratio_x)}'\n"
        "    f'  ;  (N_x - M_y)/M = {sp.latex(ratio_y)}'\n"
        ")\n"
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
        context="Open sandbox for Chapter 3 Part 2 (integrating factors, "
                "Bernoulli substitution). SymPy is available as sp; the "
                "marimo namespace as mo. Common moves: check exactness via "
                "M_y vs N_x; run the diagnostic ratios (M_y - N_x)/N and "
                "(N_x - M_y)/M to look for mu(x) or mu(y); apply v = y^(1-n) "
                "to a Bernoulli equation. Write complete runnable code; "
                "assign the result you want shown to `view`.",
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

        **Recap.** When the $M_y = N_x$ test fails, two tactics buy
        back our ability to solve:

        - **Integrating factor.** Multiply the original equation
          through by a function $\mu(x, y)$, chosen so the rescaled
          equation passes the test. The **diagnostic ratio**
          $(M_y - N_x)/N$ does double duty: it tells you (a) whether a
          $\mu(x)$ works, and (b) if so, what $\mu$ is. The mirror
          $(N_x - M_y)/M$ handles the $\mu(y)$ case. The recipe
          specialised to $N = 1$ *is* the Chapter 2 linear-equation
          formula — one mechanism with two appearances.
        - **Substitution.** Change variables until the equation becomes
          something you already know how to solve. Bernoulli's
          $v = y^{1-n}$ turns $y' + p\,y = q\,y^n$ into a linear
          equation; the homogeneous trick $v = y/x$ makes
          $y' = F(y/x)$ separable. Chapter 1's logistic S-curve turned
          out to be Bernoulli with $n = 2$ — closed-form solved here.

        **What's next.** Sometimes no clever rewriting saves you — the
        equation is exact in no coordinates and substitutes to nothing
        nice. **Chapter 4** is what you do then: walk the slope field
        one tiny step at a time and *simulate*. The same field picture
        from Chapter 1 returns as actual simulator steps you can step
        too big and watch blow up — which is exactly what happens to
        MuJoCo or PyBullet when you pick the wrong $\Delta t$.
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
        "This is Chapter 3, Part 2 of a differential-equations course: "
        "rescuing non-exact first-order equations with integrating factors "
        "and substitutions. Key ideas: when M_y != N_x the equation isn't "
        "exact, but multiplying through by a clever mu(x, y) -- the "
        "integrating factor -- can make the rescaled equation exact. The "
        "diagnostic ratio (M_y - N_x)/N tells you (a) whether a mu(x) "
        "exists and (b) what it is; the mirror (N_x - M_y)/M handles the "
        "mu(y) case. Specialised to N = 1, the recipe gives exactly the "
        "Chapter 2 linear-ODE formula mu = exp(int p dx). Bernoulli "
        "y' + p y = q y^n flattens under the substitution v = y^(1-n); "
        "the homogeneous y' = F(y/x) collapses under v = y/x. The chapter's "
        "worked Bernoulli example is the logistic equation from Chapter 1. "
        "Part 1 (the exactness condition itself, recovering F, contour "
        "maps) is the prerequisite -- if a student asks about the test or "
        "the F-recovery procedure, that's covered there, not here.",
        prompts=[
            "explain this part in a paragraph",
            "show me another non-exact equation and find the integrating factor",
            "solve another Bernoulli equation with different p, q, n",
        ],
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge, picker):
    delib.tutor_sidebar(api_field, key_bridge, picker, chatbox)
    return


if __name__ == "__main__":
    app.run()
