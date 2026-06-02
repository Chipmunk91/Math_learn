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
        (the *diagnostic ratio*), and discover a satisfying connection —
        the linear method from Chapter 2 turns out to be a *special
        case* of this chapter's recipe, with the role of $N$ pinned at
        $1$.

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
    # Frames the integrating factor as a *callback to Ch 2*, not a fresh
    # tool — we already used it there for linear ODEs. Here it's the same
    # move with a slightly different target (restore exactness, instead of
    # collapse the LHS into a single derivative).
    mo.md(
        r"""
        ## When it isn't exact — multiply by $\mu$

        The exactness test gives a clear binary: equation passes, look
        for $F$; equation fails, no $F$ to find. But "no $F$ to find"
        isn't a permanent verdict. The rescue tactic for the non-exact
        case is one we've already met before, in Chapter 2 — we just
        used it for a slightly different purpose there.

        Recall the linear method from Chapter 2: given
        $y' + p(x)\,y = q(x)$, we multiplied through by an
        **integrating factor** $\mu(x)$ chosen so that the left side
        collapsed into a single derivative $(\mu y)'$. Once that
        happened, the equation was directly integrable and we were
        done.

        Same move now, more general target. Given a non-exact
        equation $M\,dx + N\,dy = 0$, multiply through by some
        $\mu(x, y)$ chosen so that the *rescaled* equation

        $$
        \mu(x, y)\,M\,dx \;+\; \mu(x, y)\,N\,dy \;=\; 0
        $$

        passes the exactness test. Then Part 1's recipe takes over —
        recover $F$ from $(\mu M, \mu N)$, read off the contours
        $F(x, y) = C$.

        The integrating factor is doing the same job both times: it's
        the clever multiplier that turns a problem into a shape we
        already know how to handle. In Chapter 2 the target shape was
        *"single derivative on the LHS";* here it's *"exact."*  We'll
        see at the end of the section that the Chapter 2 case actually
        falls out of this one as a special case ($N = 1$) — but for
        now, the framing to carry is: same tool, broader use.

        How do we find such a $\mu$? The derivation is short but worth
        following one move at a time — particularly the moment where
        what looks like a hard equation in two variables collapses
        into an easy one, because we make a single inspired guess
        about what $\mu$ should look like. The video below walks
        through it.
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
    # Beat 7 (cont.) — after the video, before the step exercises: diagnostic
    # ratio + full-recipe checklist + Your-turn intro.
    mo.md(
        r"""
        ### Was our guess right? — checking the assumption

        Notice that the whole derivation pivoted on **one assumption**,
        the move in Step 4 of the video: we *guessed* that $\mu$
        depends only on $x$. That guess collapsed a hard equation into
        a tractable one, but we never proved $\mu$ *could* be a
        function of $x$ alone for this particular $M$ and $N$. Before
        we trust the formula, we should check whether the guess
        actually holds.

        The check is hiding inside the derivation itself. After we
        made the guess, the equation collapsed to

        $$
        \frac{\mu_x}{\mu} \;=\; \frac{M_y - N_x}{N}.
        $$

        Look at this equation. The **left side** depends only on $x$
        — because we assumed $\mu$ does, so its derivative does too.
        For the equation to be consistent, the **right side** has to
        depend only on $x$ as well. There should be no leftover $y$
        anywhere on the right after simplification.

        So the consistency check is concrete: **compute
        $(M_y - N_x)/N$ for your specific $M$ and $N$**. If it
        simplifies to a function of $x$ alone, the guess holds and
        the formula gives you $\mu$. If a $y$ refuses to cancel
        out, the guess fails — no $\mu$ depending only on $x$ can
        rescue this equation, and we'll need to try a different
        guess (like $\mu$ depending only on $y$; see further below).

        That ratio earns a name. Call it the **diagnostic ratio** for
        the equation, because computing it does double duty:

        1. **Diagnose the guess.** If the result is a function of $x$
           alone, the $\mu(x)$ guess is consistent with the equation.
           If $y$ doesn't cancel, the guess was wrong.
        2. **Build the formula.** When the diagnosis comes back
           clean, the same ratio is exactly what you integrate to
           recover $\mu$:

           $$
           \mu(x) \;=\; \exp\left(\int \frac{M_y - N_x}{N}\,dx\right).
           $$

        One computation, two answers — *whether* the rescue works
        and *what the rescue function is* — read off the same line.
        Hence "diagnostic."

        ### Now solve the equation — the full recipe

        We now have everything we need to take a *non-exact* equation
        all the way to an implicit solution. The full assembly is just
        five steps, with steps 4 and 5 handing off to the recipe from
        Part 1.

        1. **Diagnose.** Compute the diagnostic ratio
           $(M_y - N_x)/N$. If it simplifies to a function of $x$
           alone — call it $r(x)$ — proceed to step 2. If $y$
           refuses to cancel, try the mirror version (further below)
           instead.
        2. **Build $\mu$.** Integrate the ratio and exponentiate:

           $$
           \mu(x) \;=\; \exp\left(\int r(x)\,dx\right).
           $$
        3. **Multiply the original equation through by $\mu$**:

           $$
           \mu(x)\,M\,dx \;+\; \mu(x)\,N\,dy \;=\; 0.
           $$

           The rescaled equation passes the exactness test by
           construction — that's what we built $\mu$ for.
        4. **Apply the Part 1 recipe** to the rescaled pair
           $(\mu M,\,\mu N)$: partial-integrate $\mu M$ in $x$,
           then match $F_y$ against $\mu N$ to pin down the
           $y$-only piece $g(y)$. The result is $F(x, y)$.
        5. **Read off the solution.** Solutions are the contours
           of the landscape the integrating factor revealed:

           $$
           F(x, y) \;=\; C.
           $$

        Five steps for the non-exact case; Part 1's recipe was just
        steps 4 and 5. The new work is purely in steps 1–3.

        ### Your turn — solve the hook equation, step by step

        Apply the recipe to the equation that opened this part — the
        one whose exactness test failed in the hook:

        $$
        (3xy + y^2)\,dx + (x^2 + xy)\,dy = 0.
        $$

        Each of the five steps below asks for a numeric value at a
        specific point. Work the symbolic step on paper (or in SymPy)
        first; then plug a number into `answer` and press **Run &
        check** to verify before moving on.
        """
    )
    return


# --- Step 1: diagnose -----------------------------------------------------------
@app.cell
def _(mo):
    s1_get, s1_set = mo.state(
        "# Step 1 — Diagnose.\n"
        "# For the equation (3*x*y + y**2) dx + (x**2 + x*y) dy = 0,\n"
        "# compute the diagnostic ratio (M_y - N_x) / N and simplify.\n"
        "# Evaluate the simplified result at x = 2 and put the number\n"
        "# in `answer`. (It simplifies to a function of x alone.)\n"
        "import sympy as sp\n"
        "x, y = sp.symbols('x y')\n"
        "M = 3*x*y + y**2\n"
        "N = x**2 + x*y\n"
        "# ratio = ...\n"
        "answer = ...\n"
    )
    return s1_get, s1_set


@app.cell
def _(delib, s1_get):
    s1_ai, s1_gen, s1_code, s1_run = delib.exercise_inputs(s1_get())
    return s1_ai, s1_code, s1_gen, s1_run


@app.cell(hide_code=True)
def _(delib, s1_ai, s1_code, s1_gen, s1_run):
    delib.exercise_view(
        "**Step 1 — diagnose.** Compute $M_y$, then $N_x$, then the "
        "diagnostic ratio $(M_y - N_x)/N$ and simplify. Evaluate the "
        "simplified result at $x = 2$. Put the number in `answer`.",
        s1_ai, s1_gen, s1_code, s1_run,
        with_ai=False,
    )
    return


@app.cell(hide_code=True)
def _(delib, s1_code, s1_run):
    delib.run_exercise(s1_code.value, s1_run.value, check=lambda ns: delib.check_number(
        ns, target=0.5, tol=1e-4,
        ok="Right — $M_y - N_x = (3x + 2y) - (2x + y) = x + y$, so "
           "$(M_y - N_x)/N = (x + y)/(x(x + y)) = 1/x$. At $x = 2$, that's $0.5$.",
        hint="Compute $M_y = 3x + 2y$ and $N_x = 2x + y$ first; their "
             "difference is $x + y$. The denominator $x^2 + xy$ factors as "
             "$x(x + y)$, and the $x + y$ cancels.",
    ))
    return


# --- Step 2: build μ ------------------------------------------------------------
@app.cell
def _(mo):
    s2_get, s2_set = mo.state(
        "# Step 2 — Build μ.\n"
        "# Integrate the diagnostic ratio from Step 1 (which simplified to 1/x)\n"
        "# and exponentiate: μ(x) = exp(∫ (1/x) dx).\n"
        "# Evaluate μ at x = 5 and put the number in `answer`.\n"
        "import sympy as sp\n"
        "x = sp.symbols('x')\n"
        "# mu = ...\n"
        "answer = ...\n"
    )
    return s2_get, s2_set


@app.cell
def _(delib, s2_get):
    s2_ai, s2_gen, s2_code, s2_run = delib.exercise_inputs(s2_get())
    return s2_ai, s2_code, s2_gen, s2_run


@app.cell(hide_code=True)
def _(delib, s2_ai, s2_code, s2_gen, s2_run):
    delib.exercise_view(
        "**Step 2 — build $\\mu$.** Integrate the diagnostic ratio from "
        "Step 1 and exponentiate. Evaluate $\\mu$ at $x = 5$ and put "
        "the number in `answer`.",
        s2_ai, s2_gen, s2_code, s2_run,
        with_ai=False,
    )
    return


@app.cell(hide_code=True)
def _(delib, s2_code, s2_run):
    delib.run_exercise(s2_code.value, s2_run.value, check=lambda ns: delib.check_number(
        ns, target=5.0, tol=1e-4,
        ok="Right — $\\mu(x) = \\exp(\\int (1/x)\\,dx) = \\exp(\\ln x) = x$. "
           "So $\\mu(5) = 5$.",
        hint="$\\int (1/x)\\,dx = \\ln x$, then $\\exp(\\ln x) = x$. "
             "So $\\mu(x) = x$ and $\\mu(5) = 5$.",
    ))
    return


# --- Step 3: multiply through ---------------------------------------------------
@app.cell
def _(mo):
    s3_get, s3_set = mo.state(
        "# Step 3 — Multiply through by μ(x) = x.\n"
        "# Compute μM = x · (3xy + y²) and μN = x · (x² + xy).\n"
        "# Verify the rescaled equation is exact by computing (μM)_y\n"
        "# and evaluating at (x, y) = (1, 1). Put the number in `answer`.\n"
        "import sympy as sp\n"
        "x, y = sp.symbols('x y')\n"
        "mu = x\n"
        "M = 3*x*y + y**2\n"
        "N = x**2 + x*y\n"
        "muM = sp.expand(mu * M)\n"
        "muN = sp.expand(mu * N)\n"
        "# (mu*M)_y evaluated at (1, 1) = ?\n"
        "answer = ...\n"
    )
    return s3_get, s3_set


@app.cell
def _(delib, s3_get):
    s3_ai, s3_gen, s3_code, s3_run = delib.exercise_inputs(s3_get())
    return s3_ai, s3_code, s3_gen, s3_run


@app.cell(hide_code=True)
def _(delib, s3_ai, s3_code, s3_gen, s3_run):
    delib.exercise_view(
        "**Step 3 — multiply through.** Compute $\\mu M$ and $\\mu N$ "
        "with $\\mu(x) = x$, then verify exactness by evaluating "
        "$(\\mu M)_y$ at $(x, y) = (1, 1)$. Put the number in `answer`.",
        s3_ai, s3_gen, s3_code, s3_run,
        with_ai=False,
    )
    return


@app.cell(hide_code=True)
def _(delib, s3_code, s3_run):
    delib.run_exercise(s3_code.value, s3_run.value, check=lambda ns: delib.check_number(
        ns, target=5.0, tol=1e-4,
        ok="Right — $\\mu M = 3x^2 y + xy^2$, so $(\\mu M)_y = 3x^2 + 2xy$. "
           "At $(1, 1)$: $3 + 2 = 5$. (Also $(\\mu N)_x = 3x^2 + 2xy$ — they "
           "match, so the rescaled equation is exact, as the recipe promised.)",
        hint="Multiply: $\\mu M = x \\cdot (3xy + y^2) = 3x^2 y + xy^2$. "
             "Then $(\\mu M)_y = 3x^2 + 2xy$. Evaluate at $x = 1, y = 1$.",
    ))
    return


# --- Step 4: recover F ----------------------------------------------------------
@app.cell
def _(mo):
    s4_get, s4_set = mo.state(
        "# Step 4 — Recover F.\n"
        "# We have μM = 3x²y + xy² and μN = x³ + x²y.\n"
        "# Partial-integrate μM in x (treating y as constant) to get F\n"
        "# up to a function g(y). Match F_y against μN to pin down g.\n"
        "# Evaluate the resulting F at (x, y) = (1, 2). Put the number in `answer`.\n"
        "import sympy as sp\n"
        "x, y = sp.symbols('x y')\n"
        "muM = 3*x**2*y + x*y**2\n"
        "muN = x**3 + x**2*y\n"
        "# F = sp.integrate(muM, x) + g(y); pin g by matching F_y to muN.\n"
        "answer = ...\n"
    )
    return s4_get, s4_set


@app.cell
def _(delib, s4_get):
    s4_ai, s4_gen, s4_code, s4_run = delib.exercise_inputs(s4_get())
    return s4_ai, s4_code, s4_gen, s4_run


@app.cell(hide_code=True)
def _(delib, s4_ai, s4_code, s4_gen, s4_run):
    delib.exercise_view(
        "**Step 4 — recover $F$.** Partial-integrate $\\mu M$ in $x$ "
        "(treating $y$ as constant), then match $F_y$ against $\\mu N$ "
        "to pin down $g(y)$. Evaluate the resulting $F$ at "
        "$(x, y) = (1, 2)$ and put the number in `answer`.",
        s4_ai, s4_gen, s4_code, s4_run,
        with_ai=False,
    )
    return


@app.cell(hide_code=True)
def _(delib, s4_code, s4_run):
    delib.run_exercise(s4_code.value, s4_run.value, check=lambda ns: delib.check_number(
        ns, target=4.0, tol=1e-4,
        ok="Right — $F = x^3 y + \\tfrac{1}{2}x^2 y^2$, and $F(1, 2) = "
           "1 \\cdot 2 + \\tfrac{1}{2} \\cdot 1 \\cdot 4 = 2 + 2 = 4$.",
        hint="Integrate $\\mu M = 3x^2 y + xy^2$ in $x$: result is "
             "$x^3 y + \\tfrac{1}{2}x^2 y^2 + g(y)$. Then $F_y = "
             "x^3 + x^2 y + g'(y)$ must equal $\\mu N = x^3 + x^2 y$, "
             "so $g'(y) = 0$ and $g(y)$ is a constant (absorbed into $C$).",
    ))
    return


# --- Step 5: C for the curve through (1, 1) -------------------------------------
@app.cell
def _(mo):
    s5_get, s5_set = mo.state(
        "# Step 5 — State the implicit solution.\n"
        "# The general implicit solution is F(x, y) = C, with\n"
        "# F = x³y + (1/2) x² y². Find the specific value of C for the\n"
        "# solution curve passing through (x, y) = (1, 1).\n"
        "# Put it in `answer`.\n"
        "F = lambda x, y: x**3*y + x**2*y**2 / 2\n"
        "answer = ...\n"
    )
    return s5_get, s5_set


@app.cell
def _(delib, s5_get):
    s5_ai, s5_gen, s5_code, s5_run = delib.exercise_inputs(s5_get())
    return s5_ai, s5_code, s5_gen, s5_run


@app.cell(hide_code=True)
def _(delib, s5_ai, s5_code, s5_gen, s5_run):
    delib.exercise_view(
        "**Step 5 — find $C$ for a specific curve.** The implicit "
        "solution is $F(x, y) = C$ with "
        "$F = x^3 y + \\tfrac{1}{2}x^2 y^2$. What value of $C$ "
        "corresponds to the solution curve passing through "
        "$(x, y) = (1, 1)$? Put it in `answer`.",
        s5_ai, s5_gen, s5_code, s5_run,
        with_ai=False,
    )
    return


@app.cell(hide_code=True)
def _(delib, s5_code, s5_run):
    delib.run_exercise(s5_code.value, s5_run.value, check=lambda ns: delib.check_number(
        ns, target=1.5, tol=1e-4,
        ok="Right — $C = F(1, 1) = 1 + \\tfrac{1}{2} = 1.5$. The "
           "solution curve through $(1, 1)$ is the contour "
           "$x^3 y + \\tfrac{1}{2}x^2 y^2 = 1.5$. The equation whose "
           "test failed in the hook is now fully solved — there *was* "
           "a contour map behind it after all; we just had to multiply "
           "by $\\mu(x) = x$ to see it.",
        hint="Plug $x = 1, y = 1$ into $F$: "
             "$1^3 \\cdot 1 + \\tfrac{1}{2} \\cdot 1^2 \\cdot 1^2 "
             "= 1 + 0.5 = 1.5$.",
    ))
    return


# --- Closing prose: mu(y) mirror + Ch 2 connection ------------------------------
@app.cell(hide_code=True)
def _(mo):
    # Beat 7 (cont.) — after the step exercises: mu(y) mirror case + the
    # precise Ch 2 connection (one-way, linear ⊂ exact).
    mo.md(
        r"""
        ### The other half — when $\mu$ depends on $y$ instead

        The video walked through the case $\mu = \mu(x)$. There's
        a mirror version where we guess $\mu = \mu(y)$ instead,
        and the same derivation runs through with the roles of
        $x$ and $y$ swapped — *including* the diagnostic ratio,
        which becomes

        $$
        \frac{N_x - M_y}{M}
        $$

        (sign flip on top, $M$ in the denominator now instead of
        $N$). When *this* ratio depends on $y$ alone, then

        $$
        \mu(y) \;=\; \exp\left(\int \frac{N_x - M_y}{M}\,dy\right).
        $$

        **In practice**, when you meet a non-exact equation, you
        compute both diagnostic ratios and pick whichever
        simplifies to a function of just one variable. If neither
        does, you're in harder territory: $\mu$ has to depend on
        both $x$ and $y$, and the recipe stops working as a
        one-line formula. That happens; integrating factors
        aren't a silver bullet. But the catalogue of equations
        they *do* rescue is large.

        ### How Chapter 2's linear method fits inside this one

        One last connection worth drawing precisely. Take any
        first-order linear equation from Chapter 2:

        $$
        y' + p(x)\,y = q(x).
        $$

        Rewrite it in the symmetric $M\,dx + N\,dy = 0$ form by
        moving everything to one side:

        $$
        \bigl(p(x)\,y - q(x)\bigr)\,dx \;+\; dy \;=\; 0,
        $$

        so $M = p(x)\,y - q(x)$ and $N = 1$. Now run the
        diagnostic ratio:

        $$
        \frac{M_y - N_x}{N} \;=\; \frac{p(x) - 0}{1} \;=\; p(x).
        $$

        That depends on $x$ alone (since $p$ does) — the side
        condition is met automatically — and the formula the
        video derived gives

        $$
        \mu(x) \;=\; \exp\left(\int p(x)\,dx\right),
        $$

        *exactly* the integrating factor from Chapter 2's linear
        method.

        **But the implication only runs one way.** Every linear
        first-order equation slots into the integrating-factor
        recipe of this chapter as the $N = 1$ corner — but most
        exact equations are *not* linear. The rescaled hook
        equation we just solved has $y^2$ in $\mu M$ and $y$ in
        $\mu N$, and there's no way to peel either into the
        $dy/dx + P(x)\,y = Q(x)$ shape that Chapter 2 needs. So
        Chapter 2's linear recipe (recognise the LHS as
        $(\mu y)'$, integrate) doesn't apply once $N$ depends on
        $y$.

        That's why we used **Part 1's recipe** — partial-integrate
        $\mu M$ in $x$, match $F_y$ against $\mu N$ — and not
        Chapter 2's linear formula. Part 1's recipe handles the
        whole family of exact equations; Chapter 2's only handles
        the linear corner of it. **Linear is a *special case* of
        exact, not a separate-but-equivalent route.** Chapter 2's
        $\mu = e^{\int p\,dx}$ is what the general integrating-
        factor recipe gives when $N = 1$ — a satisfying tie-back,
        but a one-way one.
        """
    )
    return

@app.cell(hide_code=True)
def _(mo):
    # Beat 8 (intro) — frame the Bernoulli shape and point at the video.
    # The symbol-pushing derivation that used to be inline now lives in
    # manim/bernoulli_substitution.py and runs as a Manim clip; prose
    # below sets up "why this shape, why this substitution."
    mo.md(
        r"""
        ## Substitution: when the equation hides a familiar shape

        Most differential equations in the wild are nonlinear —
        population models with carrying capacity, autocatalytic
        reactions, the rumor on the 1,000-person campus from Chapter 1.
        The tools we've built so far don't address that head-on.
        Chapter 2's integrating factor needs the equation to be
        **linear**; Part 1's recipe (and Part 2's rescue) needs it to
        be **exact**, or rescuable to exact by a $\mu(x, y)$. Plenty
        of nonlinear equations sit outside both boxes.

        For those, we need a different angle of attack. The idea: some
        nonlinear equations have a recognisable *shape* underneath —
        a structure that becomes visible only after we change
        variables. The right substitution exposes the shape and turns
        the equation into one of the kinds we already know how to
        solve.

        We'll look at one shape in detail — the **Bernoulli**
        equation, which covers a surprising fraction of the
        first-order equations you'll meet in physics and biology —
        and then briefly mention a sibling (the **homogeneous**
        equation). In both cases the move is the same: find a
        substitution that maps the equation onto a shape we already
        know — linear, separable, or exact — then run the recipe
        you've already learned.

        ### The Bernoulli shape

        An equation of the form

        $$
        y' + p(x)\,y \;=\; q(x)\,y^n
        $$

        is called a **Bernoulli equation** when $n$ is anything other
        than $0$ or $1$. (If $n = 0$, the right side is just $q(x)$
        and we're already linear; if $n = 1$, we can move the $y$
        term to the left and we're *still* linear.) It's the cases
        like $n = 2, 3, \tfrac{1}{2}, -1$ — where the right-hand side
        is *genuinely* nonlinear in $y$ — that we want a new tool for.

        **The idea.** We want the equation to be linear in some new
        variable, because then the integrating-factor recipe from the
        last section applies directly. So we look for a substitution
        $v = (\text{some function of } y)$ that *swallows* the
        awkward $y^n$. The video below walks the derivation through
        one move at a time — divide by $y^n$, identify $y^{1-n}$
        sitting in the middle term, define $v$ to be that, and the
        equation collapses to a linear one in $v$.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Beat 8 (cont.) — Manim hero: derive v = y^(1-n) and linearise.
    delib.video(
        "bernoulli_substitution.mp4",
        caption="Deriving the Bernoulli substitution v = y^(1-n), one move at a time",
        fallback="The Bernoulli derivation is being rendered "
                 "(see manim/bernoulli_substitution.py).",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 8 (cont.) — after the video: how to solve the linearised v-equation.
    # Mirrors the "Now solve" recipe in Beat 7 for the integrating-factor case.
    mo.md(
        r"""
        ### Now solve the linearised equation

        The video ended with the linear form in $v$:

        $$
        \boxed{\quad v' \;+\; (1 - n)\,p(x)\,v \;=\; (1 - n)\,q(x). \quad}
        $$

        That's a linear first-order ODE — exactly Chapter 2's shape,
        with new "$p$" and "$q$" given by $(1-n)\,p(x)$ and
        $(1-n)\,q(x)$. So the integrating-factor recipe takes over,
        in four steps:

        1. **Build the integrating factor.** With "$p_v(x) = (1-n)\,p(x)$",
           compute

           $$
           \mu_v(x) \;=\; \exp\left(\int (1 - n)\,p(x)\,dx\right).
           $$
        2. **Multiply through** by $\mu_v(x)$. The left side collapses
           into a single derivative by construction:

           $$
           \bigl(\mu_v\,v\bigr)' \;=\; \mu_v\,(1 - n)\,q(x).
           $$
        3. **Integrate both sides** in $x$:

           $$
           \mu_v(x)\,v \;=\; \int \mu_v(x)\,(1-n)\,q(x)\,dx \;+\; C.
           $$

           Solve for $v(x)$ by dividing through by $\mu_v(x)$.
        4. **Invert the substitution** to recover $y$. Since
           $v = y^{1-n}$,

           $$
           y \;=\; v^{1/(1-n)}.
           $$

        Four steps. Steps 1–3 are Chapter 2 verbatim (with $p$ and
        $q$ scaled by $1 - n$); step 4 is just the substitution
        running in reverse. That's the whole assembly.

        Below, we run this recipe on a specific Bernoulli equation —
        the logistic equation that opened Chapter 1.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, go, mo, np):
    # Beat 8 (cont.) — the logistic worked example, with the closed-form vs
    # numerical figure as the proof.
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
            ### The logistic — Chapter 1's rumor, solved

            Take the equation that opened Chapter 1: the rumor
            spreading across a campus, the S-curve in time.
            Normalised to a population of $1$, the rate law is

            $$
            \dot y \;=\; y\,(1 - y).
            $$

            Multiply out and move the $y$ term to the left:

            $$
            \dot y - y \;=\; -y^2.
            $$

            Match against the Bernoulli template
            $y' + p\,y = q\,y^n$: $p = -1$, $q = -1$, $n = 2$. The
            substitution is $v = y^{1-2} = 1/y$. Plug into the boxed
            linear form above with $(1 - n) = -1$:

            $$
            v' + (-1)(-1)\,v \;=\; (-1)(-1)
            \quad\Longrightarrow\quad
            \dot v + v \;=\; 1.
            $$

            Apply the four-step recipe. $\mu_v(t) = \exp(\int 1\,dt) = e^t$,
            so $(e^t v)' = e^t$. Integrate: $e^t v = e^t + C$. Divide:
            $v(t) = 1 + Ce^{-t}$. Invert the substitution:

            $$
            y(t) \;=\; \frac{1}{v(t)} \;=\; \frac{1}{1 + C\,e^{-t}}.
            $$

            There's the S-curve, in closed form.

            With $y(0) = 0.1$, the condition $1/(1 + C) = 0.1$ pins
            $C = 9$, so $y(t) = 1/(1 + 9\,e^{-t})$. Below, this
            formula is plotted against the numerical solution
            `delib.solve_ode` produces from the same equation:
            """
        ),
        _fig,
        mo.md(
            r"""
            The two are indistinguishable to plotting precision —
            proof that the S-curve we read off Chapter 1's slope
            field was always going to be this exact sigmoid.
            Bernoulli substitution turned the nonlinear equation
            linear, and the integrating-factor recipe finished the
            job.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 8 (cont.) — homogeneous sibling, collapsed by default. Same
    # accordion pattern as the positive-definite side note in Ch 3a.
    mo.accordion(
        {
            "Optional dive: a sibling shape — homogeneous equations":
            mo.md(
                r"""
                The Bernoulli substitution worked by choosing $v$ to
                swallow the awkward $y^n$. The same kind of trick —
                pick a substitution that gets you to an equation you
                already know how to solve — works for other shapes
                too. The most common sibling is the **homogeneous**
                equation:

                $$
                y' \;=\; F\left(\tfrac{y}{x}\right),
                $$

                where the right-hand side depends on $x$ and $y$ only
                through their ratio. (Watch for it in the wild: any
                $y'$ that simplifies to a function of $y/x$ alone —
                things like $y' = (x + y)/(x - y)$ qualify.)

                **The substitution.** The natural guess here is

                $$
                v \;=\; \frac{y}{x}, \qquad \text{so} \quad y \;=\; x\,v.
                $$

                Differentiate using the product rule (and chain rule):

                $$
                y' \;=\; v + x\,v'.
                $$

                Substitute that into the original equation
                $y' = F(y/x) = F(v)$:

                $$
                v + x\,v' \;=\; F(v).
                $$

                Move the $v$ across:

                $$
                x\,v' \;=\; F(v) - v.
                $$

                Now divide both sides by $x\,(F(v) - v)$ — and look
                at what happens. The left side has only $v$ and
                $dv/dx$; the right side has only $x$ and $dx$:

                $$
                \frac{dv}{F(v) - v} \;=\; \frac{dx}{x}.
                $$

                **That's separable.** Two integrations finish the
                job, and the substitution $v = y/x$ runs in reverse
                to recover $y$.

                ### A small worked example

                Take $y' = \dfrac{x + y}{x}$. Rewriting:

                $$
                y' \;=\; 1 + \frac{y}{x},
                $$

                so $F(v) = 1 + v$, and $F(v) - v = 1$. The separable
                equation becomes

                $$
                \frac{dv}{1} \;=\; \frac{dx}{x},
                \quad\text{i.e.}\quad
                dv \;=\; \frac{dx}{x}.
                $$

                Integrate: $v = \ln|x| + C$. Invert:

                $$
                \frac{y}{x} \;=\; \ln|x| + C
                \quad\Longrightarrow\quad
                y \;=\; x\,\ln|x| + C\,x.
                $$

                ### Different shape, different substitution, same idea

                When a method has a clear target in mind — "get to
                linear", "get to separable" — the substitution to
                try is often just whatever is standing in the way:

                - **Bernoulli** ($y' + p y = q y^n$): $v = y^{1-n}$
                  → linear in $v$.
                - **Homogeneous** ($y' = F(y/x)$): $v = y/x$ →
                  separable in $(v, x)$.

                Both are special cases of a broader theme — there's
                a family of equations whose nonlinearity has a
                pattern, and the right substitution finds the
                pattern. The chapter beyond Bernoulli and
                homogeneous is mostly about recognising more of
                these patterns as they come up.
                """
            )
        }
    )
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
             "$\\mu(x) = \\exp\\int (M_y - N_x)/N\\,dx$.",
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
             "$\\mu(y) = \\exp\\int (N_x - M_y)/M\\,dy$.",
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
