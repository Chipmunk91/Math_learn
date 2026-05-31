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

        **Read the equation as a contour map.**

        By the end of this chapter you should be able to:

        - Understand what makes a differential equation **exact**, and see
          why the solutions of an exact equation are the *contour lines* of a
          hidden two-variable function $F(x, y)$.
        - Run a simple test on $M(x, y)\,dx + N(x, y)\,dy = 0$ to check
          whether it is exact — and, when it is, find the $F$ whose contours
          give the solutions.
        - Use an **integrating factor** — a multiplier $\mu$ that turns a
          not-quite-exact equation into an exact one — and see that
          Chapter 2's first-order-linear solution formula was an integrating
          factor in disguise.
        - Solve a **Bernoulli** equation $y' + p(x)\,y = q(x)\,y^n$ by a
          **substitution** that turns the nonlinear equation into a linear
          one, and use this trick to derive Chapter 1's logistic S-curve as
          an explicit formula.
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
        title="The same hillside, viewed from above",
    )
    mo.vstack([
        mo.md(
            r"""
            ## A walk across a hillside

            Imagine you're hiking on a hillside. The ground rises and falls
            under your feet — some directions take you uphill, others
            downhill, and others (somewhere in between) keep you at the
            height you're already at.

            Try this experiment in your head. You set out from a starting
            spot and at every step you pick the direction that keeps you
            **exactly at the altitude you started from** — never up, never
            down, only sideways relative to gravity. You don't have a map.
            You're feeling the slope under your feet and choosing the flat
            direction each time.

            What path do you trace?

            Not a straight line. The hill bends, so your path bends too —
            sometimes curving gently, sometimes turning more sharply where
            the ground steepens. After a long enough walk you might find
            yourself looking back at your starting spot from far away, the
            path snaking behind you like a ribbon laid across the hillside.

            Now imagine a thousand hikers, each starting at a *different*
            altitude, each obeying the same rule: walk so your height doesn't
            change. Each one traces a different ribbon. Stack all those
            ribbons onto one picture of the hillside, viewed from straight
            above. What you'd see is below.

            Cartographers actually draw these. They call each ribbon a
            **contour line** — a curve along which the altitude has one
            single value. The picture is called a **contour map**. The
            specific hillside below is synthetic: a small peak in the upper
            right, a shallower basin in the lower left. But every real
            mountain map is drawn this way.
            """
        ),
        _hike,
        mo.md(
            r"""
            **Pick any single contour and that's a hiker's path.**

            That single observation is what this whole chapter unpacks. We're
            going to write down the rule "walk so altitude doesn't change" as
            a differential equation — the kind we've been studying since
            Chapter 1 — and then we'll discover that whenever we encounter
            *that* shape of equation, there's a hidden hillside behind it,
            and the equation's solutions are its contours.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 2 — concept bridge.
    mo.md(
        r"""
        ## From the hiker's rule to a differential equation

        The hook ended with a promise: write down the rule "walk so altitude
        doesn't change" as a differential equation. Let's keep that promise.

        You're standing somewhere on the hillside at a spot we'll label
        $(x, y)$ — those are your coordinates on the map seen from above.
        Your altitude at that spot is $F(x, y)$, some specific number. You
        take a small step, going from $(x, y)$ to $(x + dx,\, y + dy)$. The
        step is small enough that the hillside looks essentially flat in the
        immediate neighbourhood of where you started.

        How much does your altitude change over that step?

        It depends on which way you stepped. Let's break the step into two
        pieces and add them up.

        - **Pure step in the $x$ direction** ($dy = 0$): your altitude changes
          by an amount proportional to $dx$. Doubling the step doubles the
          altitude change, because the ground is locally flat. Call the
          proportionality factor $F_x$ — the **rate** at which altitude grows
          per unit step in the $x$ direction. Then

          $$
          dF \;=\; F_x \cdot dx \qquad (\text{pure-}x\text{ step}).
          $$

        - **Pure step in the $y$ direction** ($dx = 0$): same idea, with its
          own rate $F_y$:

          $$
          dF \;=\; F_y \cdot dy \qquad (\text{pure-}y\text{ step}).
          $$

        - **General step** (both $dx$ and $dy$ non-zero): because the hillside
          is locally flat, the two contributions just add up:

          $$
          dF \;=\; F_x\,dx \;+\; F_y\,dy.
          $$

          (If you've met the **chain rule** before, you'll recognise this as
          the chain rule for a function of two variables. If not, no harm —
          we just derived it from the geometry.)

        Now apply the hiker's rule. The rule says altitude doesn't change
        along the step, so $dF = 0$. Plug that into the line above:

        $$
        \boxed{\quad F_x\,dx \;+\; F_y\,dy \;=\; 0 \quad}
        $$

        There it is. That's the differential equation behind the hiker's
        walk. Geometrically it says: *if a step in $x$ would take you
        uphill, the step in $y$ had better take you downhill by exactly the
        same amount, so that the two contributions cancel*. The equation
        pins down the allowed ratio of $dy$ to $dx$ at every point on the
        map.

        ### Now run the question backwards

        We just *started* with a landscape $F$ and *built* a differential
        equation from it. The interesting half of this chapter is the
        reverse problem.

        Suppose someone hands you a differential equation that already has
        the right *shape*:

        $$
        M(x, y)\,dx \;+\; N(x, y)\,dy \;=\; 0.
        $$

        The letters $M$ and $N$ are just labels for the two functions
        sitting in front of $dx$ and $dy$ — whatever they happen to be in
        the equation you've been handed. The natural question to ask,
        looking at it next to the boxed equation above, is:

        > Is there a hidden landscape $F(x, y)$ — somewhere, behind the
        > scenes — whose contour map is exactly the picture this equation
        > describes? In other words, can we find an $F$ with $F_x = M$ and
        > $F_y = N$?

        Two possible answers, two different stories:

        - **Yes** — and the equation is called **exact**. The chapter is
          essentially done in this case: solutions are the contours
          $F(x, y) = C$, and you're walking on a hidden hillside.
        - **No** — and there's still work to do. The rest of the chapter is
          about what to do then: either multiply the equation by a clever
          factor that *makes* a landscape appear (an **integrating
          factor**), or change variables until the equation becomes a kind
          we already know how to solve (a **substitution**).

        The next section gives a simple test for which case you're in.
        """
    )
    return


@app.cell(hide_code=True)
def _(go, mo):
    # Beat 3 — exactness test, with a graphic for the two paths and an
    # explicit baby-step from the difference quotient to the partial-
    # derivative form. dx and dy are drawn exaggerated for visibility;
    # in the math they → 0.
    _x0, _y0 = 1.0, 1.0
    _dx, _dy = 1.8, 1.2

    _rect = go.Figure()
    # Dashed rectangle outline to set the scene
    _rect.add_trace(go.Scatter(
        x=[_x0, _x0 + _dx, _x0 + _dx, _x0, _x0],
        y=[_y0, _y0, _y0 + _dy, _y0 + _dy, _y0],
        mode="lines",
        line=dict(color="#cccccc", width=1, dash="dot"),
        showlegend=False, hoverinfo="skip",
    ))
    # Blue path: right then up
    _rect.add_annotation(x=_x0 + _dx, y=_y0, ax=_x0, ay=_y0,
                         xref="x", yref="y", axref="x", ayref="y",
                         arrowhead=2, arrowsize=1.4, arrowwidth=3,
                         arrowcolor="#2f6fb0", showarrow=True)
    _rect.add_annotation(x=_x0 + _dx, y=_y0 + _dy, ax=_x0 + _dx, ay=_y0,
                         xref="x", yref="y", axref="x", ayref="y",
                         arrowhead=2, arrowsize=1.4, arrowwidth=3,
                         arrowcolor="#2f6fb0", showarrow=True)
    # Red path: up then right
    _rect.add_annotation(x=_x0, y=_y0 + _dy, ax=_x0, ay=_y0,
                         xref="x", yref="y", axref="x", ayref="y",
                         arrowhead=2, arrowsize=1.4, arrowwidth=3,
                         arrowcolor="#d1495b", showarrow=True)
    _rect.add_annotation(x=_x0 + _dx, y=_y0 + _dy, ax=_x0, ay=_y0 + _dy,
                         xref="x", yref="y", axref="x", ayref="y",
                         arrowhead=2, arrowsize=1.4, arrowwidth=3,
                         arrowcolor="#d1495b", showarrow=True)
    # Corner coordinate labels
    _rect.add_annotation(x=_x0, y=_y0, text="(x, y)", showarrow=False,
                         xshift=-28, yshift=-12, font=dict(size=13))
    _rect.add_annotation(x=_x0 + _dx, y=_y0, text="(x+dx, y)", showarrow=False,
                         xshift=34, yshift=-12, font=dict(size=13))
    _rect.add_annotation(x=_x0 + _dx, y=_y0 + _dy, text="(x+dx, y+dy)",
                         showarrow=False, xshift=44, yshift=12, font=dict(size=13))
    _rect.add_annotation(x=_x0, y=_y0 + _dy, text="(x, y+dy)", showarrow=False,
                         xshift=-34, yshift=12, font=dict(size=13))
    # Rate labels — evaluated at the *start* of each leg, hence those arguments
    _rect.add_annotation(x=_x0 + _dx / 2, y=_y0, text="rate <b>M(x, y)</b>",
                         showarrow=False, yshift=-30,
                         font=dict(color="#2f6fb0", size=13))
    _rect.add_annotation(x=_x0 + _dx, y=_y0 + _dy / 2,
                         text="rate <b>N(x+dx, y)</b>",
                         showarrow=False, xshift=75,
                         font=dict(color="#2f6fb0", size=13))
    _rect.add_annotation(x=_x0, y=_y0 + _dy / 2, text="rate <b>N(x, y)</b>",
                         showarrow=False, xshift=-65,
                         font=dict(color="#d1495b", size=13))
    _rect.add_annotation(x=_x0 + _dx / 2, y=_y0 + _dy,
                         text="rate <b>M(x, y+dy)</b>",
                         showarrow=False, yshift=30,
                         font=dict(color="#d1495b", size=13))
    _rect.update_layout(
        template="plotly_white",
        title=dict(text="Two paths from (x, y) to (x+dx, y+dy) — blue: right then up; red: up then right",
                   x=0.5, xanchor="center", font=dict(size=13)),
        xaxis=dict(range=[_x0 - 1.3, _x0 + _dx + 1.5], visible=False),
        yaxis=dict(range=[_y0 - 0.9, _y0 + _dy + 0.9], visible=False,
                   scaleanchor="x"),
        height=380, showlegend=False,
        margin=dict(l=30, r=30, t=50, b=30),
        paper_bgcolor="white", plot_bgcolor="white",
    )

    mo.vstack([
        mo.md(
            r"""
            ## A simple test for exactness

            We've set up the question — given an equation
            $M(x, y)\,dx + N(x, y)\,dy = 0$, is there a hidden landscape
            $F(x, y)$ somewhere with $F_x = M$ and $F_y = N$? Looking for
            one by guessing is hopeless. We'd like a test we can run
            directly on $M$ and $N$ that *tells* us whether $F$ exists —
            before we go searching for it.

            That test comes from a small observation about hillsides.

            ### Order of stepping doesn't matter

            You're standing at $(x, y)$. Take one step **right** by $dx$,
            then one step **up** by $dy$. You arrive at
            $(x + dx,\, y + dy)$, at some new altitude.

            Now repeat the trip from the same starting spot, in the
            **other** order: up by $dy$ first, then right by $dx$. You
            arrive at the *same point* — and at the *same altitude*,
            because altitude is a function of position alone, not of the
            path you took to get there.

            Same start, same end, same altitude. So the two total altitude
            changes have to be equal.

            Here are the two paths drawn out. Notice the labels on each
            leg — they record which rate function (M or N) applies, *and*
            the point at which that rate is evaluated. Why those specific
            arguments matters, and we'll unpack it just below the figure.
            """
        ),
        _rect,
        mo.md(
            r"""
            Each leg is a pure-direction step — the same kind we handled
            when we built up the formula $dF = F_x\,dx + F_y\,dy$. So we
            already know what the altitude change is on each leg: it's
            the rate times the step length. The only new wrinkle is
            *where the rate is evaluated*, and the answer is:

            > **At the starting point of that leg.** The linear
            > approximation "altitude grows at rate $F_x$ per unit of
            > $x$" is taken at the point where the step *begins* — that's
            > where the slope is being measured. As soon as you take a
            > step you're at a new point and the rate there is (slightly)
            > different.

            Walk through the **blue path** (right then up) with this in
            mind:

            - **Right step.** Starts at $(x, y)$, ends at $(x + dx,\, y)$.
              Pure-$x$ step. The rate-in-$x$ at the starting point is
              $M(x, y)$. So altitude change ≈ $M(x, y) \cdot dx$.
            - **Up step.** Starts at $(x + dx, y)$ — the new place — ends
              at $(x + dx,\, y + dy)$. Pure-$y$ step. The rate-in-$y$ at
              *this new* starting point is $N(x + dx, y)$. So altitude
              change ≈ $N(x + dx, y) \cdot dy$.

            Add the two:

            $$
            \text{right then up:}\quad
            dF \;=\; M(x, y)\,dx \;+\; N(x + dx, y)\,dy.
            $$

            Now the **red path** (up then right), exactly the same way —
            up from $(x, y)$ first, so the rate is $N(x, y)$; then right
            from $(x, y + dy)$, so the rate is $M(x, y + dy)$:

            $$
            \text{up then right:}\quad
            dF \;=\; N(x, y)\,dy \;+\; M(x, y + dy)\,dx.
            $$

            Set the two expressions equal — both compute the same altitude
            change between the same two points, just by different routes:

            $$
            M(x, y)\,dx + N(x + dx, y)\,dy
            \;=\; N(x, y)\,dy + M(x, y + dy)\,dx.
            $$

            Gather the $M$ terms on one side, the $N$ terms on the other:

            $$
            \bigl[N(x + dx, y) - N(x, y)\bigr]\,dy
            \;=\;
            \bigl[M(x, y + dy) - M(x, y)\bigr]\,dx.
            $$

            Each bracket is asking *how much one of our functions changes
            when we take a small step in one direction* — exactly what a
            derivative measures. Let's extract the derivative form in
            three small steps so nothing happens by sleight of hand.

            **(1) Divide both sides by $dx \cdot dy$.** The $dx$ on the
            right and the $dy$ on the left each cancel against a copy in
            the denominator:

            $$
            \frac{N(x + dx, y) - N(x, y)}{dx}
            \;=\;
            \frac{M(x, y + dy) - M(x, y)}{dy}.
            $$

            **(2) Recognise each side.** Each fraction is a **difference
            quotient** — change in the function divided by change in the
            input — the same shape as the calculus-101 limit
            $\bigl(f(x + h) - f(x)\bigr)/h$. The only twist is that one
            of the two variables is held fixed while the other moves.

            **(3) Shrink the step to zero.** As $dx \to 0$, the left side
            becomes the **partial derivative** of $N$ with respect to
            $x$, written $\partial N / \partial x$ or just $N_x$ for
            short. Same on the right, with $M$ and $y$:

            $$
            \lim_{dx \to 0}\frac{N(x + dx, y) - N(x, y)}{dx}
            \;=\; N_x,
            \quad\;
            \lim_{dy \to 0}\frac{M(x, y + dy) - M(x, y)}{dy}
            \;=\; M_y.
            $$

            Equating the two limits gives the test:

            $$
            \boxed{\quad M_y \;=\; N_x \quad}
            $$

            **If the equation $M\,dx + N\,dy = 0$ comes from a hidden
            landscape, then $M$ and $N$ have to satisfy this.** (And the
            $F_x$ we'd been describing as "the rate at which altitude
            grows per unit step in $x$" was a partial derivative all
            along — we just hadn't called it that yet.)

            The other direction — *if* $M_y = N_x$ holds throughout the
            region we care about, does a landscape always exist? — turns
            out to be yes, on the kinds of regions we'll deal with
            (rectangles, half-planes, anywhere without holes punched
            out). Proving that is a slightly more technical story, but
            the practical upshot is what matters: **the test is the whole
            question.**

            So the workflow becomes:

            > Compute $M_y$. Compute $N_x$. Compare.
            > Equal? **Exact**, and a landscape is waiting to be found.
            > Not equal? **Not exact** — we'll come back to it in the
            > integrating-factor section.

            ### Trying it on a real equation

            Take the equation we'll work with through the rest of this
            chapter:

            $$
            (2x + y)\,dx + (x + 2y)\,dy = 0.
            $$

            So $M(x, y) = 2x + y$ and $N(x, y) = x + 2y$. Run the test.

            - $M = 2x + y$. Differentiating in $y$ means asking how $M$
              changes when $y$ moves (with $x$ held fixed). The $2x$
              doesn't depend on $y$ — it doesn't move. The $y$ term
              contributes $1$ per unit of $y$. So $M_y = 1$.
            - $N = x + 2y$. Differentiating in $x$, same logic: the $2y$
              doesn't move, the $x$ contributes $1$. So $N_x = 1$.

            $M_y = N_x$. **The equation is exact.** There's a hidden
            landscape $F$ behind it, and its contours are the equation's
            solutions.

            ### So what *is* $F$?

            The test tells us a landscape exists, but it stays mum about
            *what* it is. Finding $F$ given $M$ and $N$ is its own little
            procedure — and it's easier to follow as an animation than as
            a wall of symbols. The video below walks through it step by
            step for our $M = 2x + y$, $N = x + 2y$ example. The result
            — which you'll see drop out at the end — is
            $F(x, y) = x^2 + xy + y^2$, and the next section uses it to
            draw the contour map.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(delib):
    # Beat 3.5 — Manim hero: the F-recovery walkthrough. delib.video hides
    # itself and shows the fallback note if the asset isn't rendered yet, so
    # wiring this in before the mp4 exists won't break the page.
    delib.video(
        "f_recovery.mp4",
        caption="Recovering F from M = 2x + y, N = x + 2y, one step at a time",
        fallback="The animated F-recovery is being rendered (see manim/f_recovery.py).",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 4 — live SymPy walk-through (moved BEFORE the contour visual so
    # the natural flow is: watch the recipe -> try it yourself -> see the
    # result drawn as a contour map in the next section).
    mo.md(
        r"""
        ## Recover $F$ from $(M, N)$ — symbolically, live

        Edit $M$ and $N$ below. The cell computes $M_y$ and $N_x$, compares
        them, and — when they agree — walks the same partial-integration
        recipe we just watched in the video, to give you $F$ and the
        implicit solution $F = C$.

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
    # Map common math constants into sympify's namespace so an input like
    # "e^y" parses as exp(y), not Symbol("e")**y. Without this, the derivative
    # of e^y comes back as e^y * log(e) and the chapter's own bait example
    # breaks. Also map E, pi, Pi so the page accepts either case.
    _sym_locals = {"x": x, "y": y, "e": sp.E, "E": sp.E, "pi": sp.pi, "Pi": sp.pi}
    try:
        M_expr = sp.sympify(M_input.value, locals=_sym_locals)
        N_expr = sp.sympify(N_input.value, locals=_sym_locals)
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
def _(delib):
    # Beat 5 — hero contour visual: level curves of F = x^2 + xy + y^2 with
    # the slope field of (M, N) = (2x + y, x + 2y) overlaid. The natural
    # payoff after the live cell: "here's the landscape you (or the video)
    # just recovered, drawn as contours."
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

        **The contours.** The landscape $F(x, y) = x^2 + xy + y^2$ is a
        **bowl** — zero at the origin, and growing as you walk away from
        it in any direction. The cleanest way to see "never negative" is
        to rewrite $F$ as a sum of squares:

        $$
        x^2 + xy + y^2 \;=\; \Bigl(x + \tfrac{y}{2}\Bigr)^{\!2} + \tfrac{3}{4}\,y^2.
        $$

        Two squared quantities added together can never be negative, and
        they're both zero only when $x + y/2 = 0$ *and* $y = 0$ — i.e.
        only at the origin. So slicing this bowl horizontally at any
        positive height $C$ gives a closed curve. The slice happens to
        be an ellipse, tilted around the origin, because the bowl is
        quadratic.

        > **Side note — "positive definite," a name and a one-line test.**
        >
        > What we just verified about $F$ — *non-negative everywhere,
        > zero only at the origin* — has a standard name: $F$ is
        > **positive definite**. Quadratic forms with this property show
        > up everywhere stability does (a spring's potential energy near
        > rest, the second-derivative test in calculus, the energy
        > function of a convex optimisation), so it's worth knowing the
        > name and the calculation.
        >
        > For *any* two-variable quadratic
        > $\;A\,x^2 + B\,xy + C\,y^2$, you can check positive-definiteness
        > in one line without completing the square:
        >
        > $$
        > B^2 - 4AC \;<\; 0
        > \quad \text{(together with } A > 0\text{, so the bowl opens upward).}
        > $$
        >
        > The quantity $B^2 - 4AC$ is the **discriminant** — yes, the same
        > expression that decides whether $Ax^2 + Bx + C = 0$ has real
        > roots, doing the analogous job here: it controls whether the
        > level sets *close up* (no real roots → bowl → ellipses) or
        > *open out* (real roots → saddle → hyperbolas).
        >
        > For our $F = x^2 + xy + y^2$: $A = 1$, $B = 1$, $C = 1$, so
        > $B^2 - 4AC = 1 - 4 = -3 < 0$. Positive definite, confirming the
        > bowl. The slider in the next section uses this one-line test
        > once, and three regimes drop out instantly.

        **The arrows.** Each one points along
        $(1, dy/dx) = (1, -M/N) = (1, -(2x+y)/(x+2y))$. Look at any
        arrow and the contour underneath it: the arrow is tangent. The
        ellipse *is* the solution; the slope field *is* the same picture,
        viewed twice. That equivalence is the whole moral of the chapter
        in one figure.
        """
    )
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

            Vary $a$ in $F(x, y) = x^2 + a\,xy + y^2$. We can predict the
            three regimes ahead of time using the discriminant test from
            the side note: matching coefficients
            $(A, B, C) = (1,\,a,\,1)$, we get

            $$
            B^2 - 4AC \;=\; a^2 - 4.
            $$

            That single quantity controls everything:

            - **$|a| < 2$ — discriminant negative. Positive definite, a
              bowl.** Slices are closed curves — **ellipses**, tilted
              around the origin.
            - **$a = \pm 2$ — discriminant zero. The boundary case, a
              trough.** $F$ collapses to $(x \pm y)^2$ — zero all along
              the line $y = \mp x$, growing only as you walk away from
              that line. Slices are pairs of parallel lines, and $F_x$
              and $F_y$ both vanish along the trough's bottom — so the
              slope field has no direction to point.
            - **$|a| > 2$ — discriminant positive. No longer positive
              definite, a saddle.** $F$ now *grows* in some directions
              and *shrinks* (goes negative) in others. Slices are
              **hyperbolas**, branching off to infinity, and there are
              level sets at both positive and negative $C$.

            Drag through $a = 2$ slowly and watch the closed loops snap
            open into the unbounded branches. That qualitative change in
            the whole picture — caused by one parameter crossing a
            threshold — has a name. It's a **bifurcation**, and we'll
            see it again in Ch 6 in the context of 1-D ODEs.
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
        recover it with the recipe from earlier in the chapter.

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
    # Beat 7 (cont.) — after the video: symmetric μ(y) case + the Ch 2
    # connection as the prose punchline.
    mo.md(
        r"""
        ### The other half — when $\mu$ depends on $y$ instead

        The video walked through the case $\mu = \mu(x)$ — multiplier
        that depends only on $x$. But we could just as well try the
        guess $\mu = \mu(y)$. The recipe is exactly the same with the
        roles of $x$ and $y$ swapped:

        $$
        \mu(y) \;=\; \exp\!\left(\int \frac{N_x - M_y}{M}\,dy\right),
        $$

        valid when $(N_x - M_y)/M$ turns out to depend on $y$ alone.

        In practice, when you meet a non-exact equation, you compute
        both diagnostic ratios — $(M_y - N_x)/N$ and $(N_x - M_y)/M$ —
        and pick whichever simplifies to a function of just one
        variable. If both fail, you're in the harder territory where
        $\mu$ has to depend on *both* $x$ and $y$, and the recipe stops
        working as a one-line formula. That happens; integrating factors
        aren't a silver bullet. But often enough — especially in the
        first-year-physics catalogue of equations — one of the two clean
        cases works.

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
        ratio:

        $$
        \frac{M_y - N_x}{N} \;=\; \frac{p(x) - 0}{1} \;=\; p(x).
        $$

        It already depends on $x$ alone (since $p$ is a function of $x$
        alone) — the side condition for $\mu(x)$ is satisfied
        automatically. Plug into the formula the video just derived:

        $$
        \mu(x) \;=\; \exp\!\left(\int p(x)\,dx\right).
        $$

        That's *exactly* the integrating factor we used in Chapter 2 to
        solve linear ODEs — derived there as a clever trick. Here it
        falls out of the integrating-factor recipe with $N$ pinned at
        $1$.

        The Chapter 2 method wasn't a trick at all. It was the
        integrating-factor recipe, specialised to one particular shape
        of equation. **One mechanism, two appearances.** Later chapters
        will keep pulling that thread: most of the methods that look like
        one-off tricks turn out to be special cases of more general
        ideas.
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
