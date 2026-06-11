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
        # Chapter 3, Part 1 — When the path doesn't matter

        **Find the hidden contour map.**

        Chapter 3 is split into two parts. *This* part is about a family of
        first-order equations where the **path** you take from one point
        to another doesn't change the answer — and the solutions turn out
        to be the contour lines of a hidden two-variable function. **Part 2**
        picks up where this part ends (with the test failing) and asks:
        when the path *does* matter, what can we still do?

        By the end of this part you should be able to:

        - Understand what makes a differential equation **exact**, and see
          why the solutions of an exact equation are the *contour lines*
          of a hidden two-variable function $F(x, y)$.
        - Run a simple test on $M(x, y)\,dx + N(x, y)\,dy = 0$ to check
          whether it is exact — and, when it is, find the $F$ whose
          contours give the solutions.
        - Read the contour map: tell whether the hidden landscape is
          shaped like a bowl, a trough, or a saddle, and what that says
          about the equation's solutions.
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
                         "Rescuing this equation is what Part 2 of the chapter is about.")
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
    # Beat 5 (cont.) — the chapter's moral. Just the contours/arrows
    # equivalence, the heart of the figure above. Detailed shape analysis
    # (bowl/saddle, sum-of-squares, positive definite, slider regimes) is
    # off the main differential-equation track, so it lives inside an
    # accordion below.
    mo.md(
        r"""
        Read the picture in two passes.

        **The contours.** The landscape $F(x, y) = x^2 + xy + y^2$ that
        you (or the video) recovered shows up here as nested closed
        loops — ellipses tilted around the origin. Pick any of them
        and you've drawn a solution of the equation.

        **The arrows.** Each one points along
        $(1, dy/dx) = (1, -M/N) = (1, -(2x+y)/(x+2y))$. Look at any
        arrow and the contour underneath it: the arrow is tangent.
        The ellipse *is* the solution; the slope field *is* the same
        picture, viewed twice. That equivalence is the whole moral of
        the chapter in one figure.
        """
    )
    return


# --- The shape of F (sum-of-squares + positive definite + slider) lives
# --- inside one accordion. It's a beautiful side topic, but it's about
# --- quadratic forms more than about differential equations — readers
# --- who want it can expand it; readers heading for Part 2 can skip it.


@app.cell(hide_code=True)
def _(delib):
    # The slider widget is created here but not displayed inline; it gets
    # rendered later, inside the accordion below.
    a_panel = delib.param_panel(
        [{"name": "a", "label": "cross-term coefficient a",
          "start": -3.0, "stop": 3.0, "step": 0.1, "value": 1.0}]
    )
    return (a_panel,)


@app.cell(hide_code=True)
def _(a_panel, delib):
    # Same: build the slider figure but don't display it inline. It also
    # gets rendered inside the accordion.
    a = a_panel.value["a"]
    _F = lambda x, y, _a=a: x**2 + _a*x*y + y**2
    _M = lambda x, y, _a=a: 2*x + _a*y
    _N = lambda x, y, _a=a: _a*x + 2*y
    slider_fig = delib.level_curves(
        _F, (-3.0, 3.0), (-3.0, 3.0),
        levels=[-4.0, -2.0, -0.5, 0.5, 2.0, 4.0, 7.0],
        field=(_M, _N),
        title=f"F(x, y) = x² + {a:+.2f}·xy + y²",
    )
    return (slider_fig,)


@app.cell(hide_code=True)
def _(a_panel, mo, slider_fig):
    # The big optional dive: shape of the hidden landscape, with the slider
    # for interactive exploration. Everything inside this accordion is
    # about quadratic forms (bowl / trough / saddle, discriminant test,
    # positive-definite) more than about the equation itself, so it's
    # collapsed by default. Readers who want the analytical story expand it.
    mo.accordion(
        {
            "Optional dive: a closer look at the shape of the hidden "
            "landscape (bowl, trough, or saddle?)":
            mo.vstack([
                mo.md(
                    r"""
                    ### Why those level curves are closed loops

                    The landscape $F(x, y) = x^2 + xy + y^2$ is a
                    **bowl** — zero at the origin and growing in every
                    direction as you walk away from it. The cleanest
                    way to see "never negative" is to rewrite $F$ as a
                    sum of squares:

                    $$
                    x^2 + xy + y^2 \;=\; \Bigl(x + \tfrac{y}{2}\Bigr)^{2} + \tfrac{3}{4}\,y^2.
                    $$

                    Two squared quantities added together can never be
                    negative, and they're both zero only when
                    $x + y/2 = 0$ *and* $y = 0$ — i.e. only at the
                    origin. So slicing this bowl horizontally at any
                    positive height $C$ gives a closed curve. The
                    slice happens to be an ellipse, tilted around the
                    origin, because the bowl is quadratic.

                    ### "Positive definite" — a name and a one-line test

                    What we just verified about $F$ — *non-negative
                    everywhere, zero only at the origin* — has a
                    standard name: $F$ is **positive definite**.
                    Quadratic forms with this property show up
                    everywhere stability does (a spring's potential
                    energy near rest, the second-derivative test in
                    calculus, the energy function of a convex
                    optimisation).

                    For *any* two-variable quadratic
                    $\;A\,x^2 + B\,xy + C\,y^2$, you can check
                    positive-definiteness in one line without
                    completing the square:

                    $$
                    B^2 - 4AC \;<\; 0
                    \quad \text{(together with } A > 0\text{, so the bowl opens upward).}
                    $$

                    The quantity $B^2 - 4AC$ is the **discriminant** —
                    the same expression that decides whether
                    $Ax^2 + Bx + C = 0$ has real roots, doing the
                    analogous job here: it controls whether the level
                    sets *close up* (no real roots → bowl → ellipses)
                    or *open out* (real roots → saddle → hyperbolas).

                    For our $F = x^2 + xy + y^2$: $A = 1$, $B = 1$,
                    $C = 1$, so $B^2 - 4AC = 1 - 4 = -3 < 0$. Positive
                    definite, confirming the bowl.

                    ### Morph the contours — bowl, trough, saddle

                    Vary $a$ in $F(x, y) = x^2 + a\,xy + y^2$. We can
                    predict each regime ahead of time using the
                    discriminant test above: matching coefficients
                    $(A, B, C) = (1,\,a,\,1)$, we get

                    $$
                    B^2 - 4AC \;=\; a^2 - 4.
                    $$

                    That single quantity controls everything:
                    """
                ),
                a_panel,
                slider_fig,
                mo.md(
                    r"""
                    - **$|a| < 2$ — discriminant negative. Positive
                      definite, a bowl.** Slices are closed curves —
                      **ellipses**, tilted around the origin.
                    - **$a = \pm 2$ — discriminant zero. The boundary
                      case, a trough.** $F$ collapses to $(x \pm y)^2$
                      — zero all along the line $y = \mp x$, growing
                      only as you walk away from that line. Slices are
                      pairs of parallel lines, and $F_x$ and $F_y$
                      both vanish along the trough's bottom — so the
                      slope field has no direction to point.
                    - **$|a| > 2$ — discriminant positive. No longer
                      positive definite, a saddle.** $F$ now *grows*
                      in some directions and *shrinks* (goes negative)
                      in others. Slices are **hyperbolas**, branching
                      off to infinity, and there are level sets at
                      both positive and negative $C$.

                    Drag through $a = 2$ slowly and watch the closed
                    loops snap open into the unbounded branches. That
                    qualitative change in the whole picture — caused
                    by one parameter crossing a threshold — has a
                    name. It's a **bifurcation**, and we'll see it
                    again in Ch 6 in the context of 1-D ODEs.
                    """
                ),
            ])
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it — in code

        Two drills for this part, both with the same workflow: run the
        exactness test on a new equation, recover $F$ via partial
        integration, plug in a number. Three SymPy calls each; expect a
        minute of thinking and a few lines of code.

        1. **Check exactness, recover $F$, and read off $F$ at a specific
           point.** Trigonometric and polynomial pieces mixed together.
        2. **Find the implicit solution through a given point.** Same
           recipe, different equation — this time the answer is the
           value of the conserved quantity along that solution curve.

        Part 2 will pick the practice back up with non-exact equations,
        integrating factors, and substitutions.
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
        with_ai=False,
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_code, e1_run):
    import math as _math
    delib.run_exercise(e1_code.value, e1_run.value, check=lambda ns: delib.check_number(
        ns, target=_math.sin(1) + 1.0, tol=1e-3,
        ok="Right — $F = \\sin x + x^2 y + \\cos y$, so $F(1, 0) = \\sin 1 + 1 \\approx 1.8415$.",
        hint="Integrate $M$ in $x$ → $\\sin x + x^2 y + g(y)$; then $F_y = x^2 + g'(y)$ must match $N$.",
    ))
    return


# --- Challenge 2: implicit solution through a given point --------------------
@app.cell
def _(mo):
    e2_get, e2_set = mo.state(
        "# Consider (2*x + exp(y)) dx + (x*exp(y) - 3*y**2) dy = 0.\n"
        "# Check exactness, recover F, and find the constant C in F = C\n"
        "# for the solution curve passing through (x, y) = (1, 0).\n"
        "# (Hint: C = F(1, 0).)\n"
        "import sympy as sp\n"
        "x, y = sp.symbols('x y')\n"
        "M = 2*x + sp.exp(y)\n"
        "N = x*sp.exp(y) - 3*y**2\n"
        "# ... compute F, then C = F(1, 0) ...\n"
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
        context="M = 2x + e^y; N = x e^y - 3 y^2. M_y = e^y, N_x = e^y -> exact. "
                "F = integrate M dx = x^2 + x e^y + g(y). "
                "F_y = x e^y + g'(y) must equal N = x e^y - 3 y^2 -> g'(y) = -3 y^2 -> g(y) = -y^3. "
                "F(x, y) = x^2 + x e^y - y^3. "
                "Solution through (1, 0) satisfies F = C with C = F(1, 0) = 1 + 1 - 0 = 2. "
                "Put 2 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_ai, e2_code, e2_gen, e2_run):
    delib.exercise_view(
        "**2.** Consider the exact equation "
        "$(2x + e^y)\\,dx + (x\\,e^y - 3y^2)\\,dy = 0$. The solution curve "
        "through $(x, y) = (1, 0)$ is the contour $F(x, y) = C$ for some "
        "constant $C$. Find $C$ and put it in `answer`.",
        e2_ai, e2_gen, e2_code, e2_run,
        with_ai=False,
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_code, e2_run):
    delib.run_exercise(e2_code.value, e2_run.value, check=lambda ns: delib.check_number(
        ns, target=2.0, tol=1e-4,
        ok="Right — $F = x^2 + xe^y - y^3$, so $F(1, 0) = 1 + 1 - 0 = 2$. "
           "The solution through $(1, 0)$ lives on the contour $F = 2$.",
        hint="Integrate $M$ in $x$ to get $x^2 + xe^y + g(y)$; match $F_y$ "
             "against $N$ to find $g'(y) = -3y^2$; then evaluate $F$ at $(1, 0)$.",
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
        context="Open sandbox for Chapter 3 Part 1 (exact equations, level "
                "curves, the contour-map view of solutions). Helpers: "
                "delib.level_curves(F, xrange, yrange, levels=..., field=True or (M, N)). "
                "Write complete runnable code; assign a Plotly figure to `view`. "
                "Part 2's topics (integrating factors, Bernoulli) are out of "
                "scope here -- flag them but don't try to solve them in this sandbox.",
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


# --- Tutor (BYO-key chat, from delib) ------------------------------------------
@app.cell
def _(delib):
    key_bridge = delib.key_bridge_widget()
    return (key_bridge,)


@app.cell
def _(delib):
    api_field = delib.key_field()
    return (api_field,)


@app.cell
def _(api_field, delib, key_bridge):
    delib.persist_key(api_field, key_bridge)
    return

@app.cell
def _(delib):
    picker = delib.cell_picker_widget()
    return (picker,)


@app.cell
def _(mo):
    # State indirection so the chat widget never re-runs on cell pick.
    # The tutor_chat cell depends on picked_get (a stable function ref);
    # the sync cell below writes the picker's value into the state; the
    # chat_model closure inside tutor_chat calls picked_get() at send-
    # time, which marimo does not track as a cell-level dependency.
    picked_get, picked_set = mo.state({"text": "", "title": ""})
    return picked_get, picked_set


@app.cell
def _(picked_set, picker):
    # picker.value changing re-runs this cell only; it creates no
    # widgets, so a re-run is harmless and just refreshes the state.
    _val = picker.value or {}
    picked_set({"text": _val.get("picked_text", ""),
                "title": _val.get("picked_title", "")})
    return



@app.cell
def _(api_field, delib, key_bridge, picked_get):
    chatbox = delib.tutor_chat(
        api_field, key_bridge,
        "This is Chapter 3, Part 1 of a differential-equations course: "
        "*exact* first-order equations, anchored to the hiker-on-a-contour-map "
        "story. Key ideas: the exactness condition M_y = N_x; what it means "
        "geometrically (order of stepping doesn't matter -- right-then-up equals "
        "up-then-right -- which is path independence); solutions of an exact "
        "ODE are the contour lines of a hidden two-variable function F with "
        "F_x = M, F_y = N; the recipe to recover F is partial-integrate M in "
        "x and then match against N to pin down g(y). Part 2 of this chapter "
        "(separate file) will handle non-exact equations -- integrating "
        "factors and substitutions -- so for now keep the focus on the "
        "exact case and the contour-map interpretation. Do NOT solve "
        "non-exact equations as if they were already exact; flag them and "
        "point the reader to Part 2.",
        prompts=[
            "explain this part in a paragraph",
            "show me another exact equation and recover F step by step",
            "what does 'path independence' have to do with exact equations?",
        ],
        picked_get=picked_get,
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge, picker):
    delib.tutor_sidebar(api_field, key_bridge, chatbox, picker=picker)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Recap & what's next

        **Recap.** *Exact* equations are the ones where the path you take
        from one point to another doesn't change anything — and that
        deep property is captured by a simple one-line test, the boxed
        $M_y = N_x$. When the test passes, there's a hidden two-variable
        function $F$ behind the equation; the equation's solutions are
        the contours of that landscape, and the slope field is just the
        same picture viewed twice. The recipe to recover $F$ — partial-
        integrate $M$ in $x$, match against $N$ to pin down what depends
        on $y$ alone — turns a problem into three SymPy calls (or a
        slim derivation by hand).

        Reading the picture: the conic-quadratic toy $x^2 + a\,xy + y^2$
        flips through three shapes as $a$ crosses $\pm 2$, with the
        contour map flipping right along with it — closed loops giving
        way to parallel lines giving way to hyperbolas. The discriminant
        $B^2 - 4AC$ is the one-line test for which regime you're in
        (positive definite, the boundary trough, or saddle).

        **What's next.** This whole part assumed the test passed. But
        most equations you'll meet in the wild *don't* — most slope
        fields don't come from a conserved $F$. **Part 2** picks up
        right there, with an equation that fails the test, and asks:
        can we still rescue it? The answer turns out to be yes, twice
        over — multiply through by a clever factor (the **integrating
        factor**), or change variables until the equation becomes
        something we already know how to solve (a **substitution**).
        Part 2's punchline ties Chapter 2's linear-equation formula
        back to Part 1's exactness condition.
        """
    )
    return


if __name__ == "__main__":
    app.run()
