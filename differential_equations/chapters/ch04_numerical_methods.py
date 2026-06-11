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
        # Chapter 4 — Numerical methods

        **Walk the field when you can't solve it.**

        By the end of this chapter you should be able to:

        - Understand why most differential equations don't have
          closed-form solutions, and why every physics simulator
          (MuJoCo, PyBullet, Drake, Unity) handles this the same way:
          by stepping forward in tiny time increments.
        - Apply **Euler's method** — the simplest possible "walk the
          slope field" recipe — to any first-order ODE and produce a
          numerical trajectory.
        - Recognise that Euler is **first-order accurate** (halving
          the step size halves the error), and that **RK4** is
          fourth-order (halving the step size cuts error by 16×).
        - Diagnose **numerical instability**: identify when a chosen
          step size is too large for the equation at hand, causing
          the numerical solution to oscillate and blow up instead of
          converging.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, go, mo, np):
    # Beat 1 — hook: a physics engine ticking forward in tiny time steps.
    # Slope field of y' = y - x^2 with the exact solution overlaid and an
    # Euler walk (h = 0.25, 8 steps) shown as dots so the "stepping"
    # nature of numerical integration is visible. The gap between the
    # dots and the smooth curve is the entire subject of this chapter.
    _f = lambda x, y: y - x**2
    _hook_fig = delib.slope_field_plotly(
        _f, (-0.1, 2.2), (0.5, 3.3),
        density=18,
        title="Inside a physics engine: stepping the slope field of  y' = y - x²",
    )

    # Exact solution: with y(0) = 1, y(x) = 2 + 2x + x² - e^x.
    _xs_exact = np.linspace(0, 2.0, 200)
    _ys_exact = 2 + 2 * _xs_exact + _xs_exact**2 - np.exp(_xs_exact)
    _hook_fig.add_trace(go.Scatter(
        x=_xs_exact, y=_ys_exact, mode="lines",
        line=dict(color="#5b7db1", width=3),
        name="exact solution",
    ))

    # Euler walk with h = 0.25, 8 steps.
    _h, _n = 0.25, 8
    _x_e, _y_e = [0.0], [1.0]
    for _ in range(_n):
        _slope = _y_e[-1] - _x_e[-1]**2
        _x_e.append(_x_e[-1] + _h)
        _y_e.append(_y_e[-1] + _h * _slope)
    _hook_fig.add_trace(go.Scatter(
        x=_x_e, y=_y_e, mode="markers",
        marker=dict(size=12, color="#d1495b", symbol="circle",
                    line=dict(color="#7a2a3a", width=1.5)),
        name="Euler steps (h = 0.25)",
    ))
    _hook_fig.update_layout(
        showlegend=True,
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.8)"),
    )

    mo.vstack([
        mo.md(
            r"""
            ## What a physics engine actually does

            Open any physics-based video game — a bouncing ball, a
            swinging pendulum, a robot arm — and zoom into what the
            engine does on every frame. The rules of motion are easy to
            write down: gravity pulls, the floor pushes back, friction
            slows things. Together they form a differential equation:
            at every moment, an object's acceleration depends on its
            current position, velocity, and the forces around it.

            The engine can't solve that equation in closed form. The
            expression for "where is the ball 5 seconds from now?"
            isn't a clean formula — it depends on collisions and
            contacts that the engine doesn't know about in advance.
            So it doesn't even try. Instead, it **ticks forward in
            tiny time steps** — typically 1/60 of a second. At each
            tick: read the current slope from the equations of motion,
            take a small step in that direction, repeat. Sixty times a
            second.

            That's the whole job of a physics engine: **walking the
            slope field from Chapter 1, one tiny step at a time.**
            MuJoCo, PyBullet, Drake, Unity's physics, every robotics
            simulator you've ever used — they all do this.

            This chapter is the same idea in slightly less fancy form.
            When you have an ODE $y' = f(x, y)$ that doesn't have a
            closed-form solution, you walk the slope field. We'll
            learn three things:

            - **How to walk** — Euler's method, then RK4 as the
              better-behaved cousin.
            - **How to know when you're walking too coarsely** — the
              *order* of a method tells you how the error shrinks with
              step size.
            - **How to recognise when your walk is about to blow up** —
              the stability story that every real-world simulator
              has to handle.

            The figure below shows the basic idea. The slope field of
            $y' = y - x^2$ has its little tangent arrows everywhere;
            the smooth blue curve is the exact solution starting from
            $y(0) = 1$ (this equation happens to have a closed form,
            $y = 2 + 2x + x^2 - e^x$, which won't be the case in
            general); and the red dots are where a coarse simulator
            with step size $h = 0.25$ would *think* the trajectory
            went. The dots are not on the curve. **That gap is what
            this chapter is about.**
            """
        ),
        _hook_fig,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 2 — concept bridge from "slope at every point" (Ch 1's slope
    # field) to "step forward by slope × step-size." Stays text-only;
    # Beat 3 derives the formula and Beat 5 has the interactive hero.
    mo.md(
        r"""
        ## From slope to step

        Pick any first-order ODE we've met since Chapter 1:

        $$
        \frac{dy}{dx} \;=\; f(x, y).
        $$

        It assigns a **slope** to every point in the plane. Chapter 1
        drew those slopes as a field of little arrows. Chapter 2
        turned some of them into formulas. But the equation itself is
        a much simpler object: at every point $(x, y)$, it tells you
        the *direction* the solution is heading.

        That's already a recipe for walking. Start at the initial
        condition $(x_0, y_0)$. Look at $f(x_0, y_0)$ — that's the
        slope of the true solution at your starting point. Take a
        small step of width $h$ along the $x$-axis, following that
        slope. You arrive at

        $$
        \bigl(x_0 + h,\; y_0 + h \cdot f(x_0, y_0)\bigr).
        $$

        Now do it again from there. Look at the new slope, take
        another step. And again. And again. The slope changes as you
        move, so your trajectory **curves** — but it's a polyline of
        straight segments, not a smooth curve. Each segment was drawn
        using the slope at its starting point only; once you've
        stepped, the slope is already (slightly) wrong for where
        you've landed.

        The shorter the steps, the closer your polyline tracks the
        true curve. The longer the steps, the more visibly
        polygonal — and sometimes, the more dramatically wrong.

        That's the whole concept, in one paragraph. The next section
        writes the rule down as a single line of algebra, and the
        rest of the chapter is about three questions: *how to choose
        $h$, how good (or bad) the rule turns out to be at that
        choice, and what better rules exist when the simplest one
        isn't good enough.*
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3 — derive Euler's method as a single line of algebra from
    # Beat 2's intuition, plus a worked first step on the hook equation
    # so the formula is concrete. Text + math only; Beat 4 (planned
    # Manim) will be the visual companion.
    mo.md(
        r"""
        ## Writing the step down

        The previous section said "look at the slope, step in that
        direction, repeat." Let's turn that into a single line of
        algebra.

        You're standing at the point $(x_n, y_n)$ at step $n$ of your
        walk. The slope of the true solution *passing through that
        point* is $f(x_n, y_n)$ — that's all the equation gives you,
        and it's all you have. (You don't know yet where the true
        solution is heading next, because you haven't taken the step.)

        Take a step of width $h$ in the $x$-direction. Follow that
        slope exactly — as if the solution were a straight line with
        that slope over the whole step. You arrive at the new
        $x$-coordinate $x_n + h$, and at a $y$-coordinate that has
        gone up (or down) by (slope $\times$ step width):

        $$
        y \;=\; y_n \;+\; h \cdot f(x_n, y_n).
        $$

        Call this new point $(x_{n+1}, y_{n+1})$. Then repeat from
        there. The update rule is just:

        $$
        \boxed{\quad
        x_{n+1} = x_n + h,
        \qquad
        y_{n+1} = y_n + h \cdot f(x_n, y_n).
        \quad}
        $$

        This is **Euler's method**, the simplest possible numerical
        recipe for an ODE. Two lines. That's the whole thing.

        Notice what we just did — and didn't do. The slope
        $f(x_n, y_n)$ is the *true* slope of the solution at our
        current point. But by following it for a full step of width
        $h$, we've ended up at $(x_{n+1}, y_{n+1})$, which is
        **generally not on the true solution**. The true solution
        curves; our step is straight. So at the *next* step we'll be
        reading the equation's slope at a point that's slightly off
        the real curve. The error compounds as we go.

        For small $h$, the per-step error is small — the linear
        approximation to a smooth curve is very accurate over short
        distances. For large $h$, the per-step error is large, and
        after enough steps the accumulated error can swamp the
        answer.

        ### One step, worked out

        Take the equation from the hook, $y' = y - x^2$, with the
        initial condition $y(0) = 1$. Use step size $h = 0.25$. Compute
        the first step by hand:

        - At $(x_0, y_0) = (0, 1)$, the slope is
          $f(0, 1) = 1 - 0^2 = 1$.
        - Step in $x$: $x_1 = 0 + 0.25 = 0.25$.
        - Step in $y$: $y_1 = 1 + 0.25 \cdot 1 = 1.25$.

        So after one step the simulator's dot lands at
        $(0.25, 1.25)$. The exact solution at $x = 0.25$ is
        $y = 2 + 0.5 + 0.0625 - e^{0.25} \approx 1.279$. The Euler
        dot is at $1.250$, below the true curve by about $0.029$ —
        that's the per-step error.

        For step 2, we read the slope *at the dot*, not at the true
        curve: $f(0.25, 1.25) = 1.25 - 0.0625 = 1.1875$. The dot
        lands at $(0.5,\; 1.25 + 0.25 \cdot 1.1875) = (0.5, 1.547)$.
        The true value at $x = 0.5$ is about $1.602$, so the dot is
        now off by $0.055$ — the error has grown.

        Continue this for eight steps and you reproduce the red dots
        from the hook figure exactly. (You can flip back and verify
        the arithmetic.)
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 4 (intro) — frame the Manim that animates Euler walking the
    # field of y' = y - x², step by step. Same equation and h = 0.25 as
    # the hook figure, so the video literally brings that figure to life.
    mo.md(
        r"""
        ## Watch the recipe in motion

        The video below brings the hook figure to life: same equation
        $y' = y - x^2$ with $y(0) = 1$, same step $h = 0.25$. Each
        frame shows the slope the equation gives at the current
        point, then the dot stepping along that slope, then the
        segment being laid down. After eight steps the exact
        solution comes in as an overlay so the per-step error is
        visible all at once.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Beat 4 — Manim hero: Euler walking the slope field of y' = y - x²
    # with h = 0.25, eight steps, exact-solution overlay at the end.
    delib.video(
        "euler_walks_field.mp4",
        caption="Euler's method walking the slope field of  y' = y − x²,   h = 0.25",
        fallback="The Euler-walks-field animation is being rendered "
                 "(see manim/euler_walks_field.py).",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 5 (intro) — set up the slider hero: shrink h, watch the polyline
    # collapse onto the exact curve. This is the visual the chapter has been
    # promising since the hook ("how small is small enough?").
    mo.md(
        r"""
        ## Shrink the step yourself

        The previous animation used $h = 0.25$ — a deliberately coarse
        step so each piece of the polyline is visible. In practice you
        almost never run a simulator that coarse; you'd typically pick
        $h$ small enough that the polyline is *visually* indistinguishable
        from the true curve.

        The slider below lets you do exactly that. Same equation,
        $y' = y - x^2$ with $y(0) = 1$, same window. The red polyline
        is Euler's walk at whatever $h$ you choose; the smooth blue
        curve is the exact solution. Drag $h$ down and watch the
        polyline melt onto the curve. Drag $h$ up toward $0.5$ and
        watch the gap open dramatically — at the largest step, the
        eight-step walk is already noticeably off by $x = 2$.

        Some things worth noticing as you scrub:

        - **The gap doesn't blow up.** Even at $h = 0.5$, Euler still
          tracks the *shape* of the solution. It's wrong by a constant
          amount, not catastrophically wrong. This won't always be the
          case — the last section of the chapter shows an equation
          where it fails dramatically.
        - **Halving $h$ roughly halves the error.** Try $h = 0.25$,
          then $h = 0.125$, then $h = 0.0625$, and eyeball the gap at
          $x = 2$. Each halving cuts the gap by about two. That ratio
          is what *first-order accurate* means, and the next section
          turns it into a formula.
        - **It costs you compute.** Halving $h$ doubles the number of
          steps you have to take. The whole art of numerical
          integration is buying accuracy *cheaply* — which is the
          motivation for the better methods we'll meet shortly.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Beat 5 — slider for h. Range 0.025..0.5 in 0.025 increments so the
    # student can sweep from "indistinguishable from exact" to "visibly
    # polygonal." Default 0.25 matches the hook + Manim, so the chapter
    # opens on the worst case and the slider improves from there.
    h_panel = delib.param_panel([
        {"name": "h", "label": "step size  h",
         "start": 0.025, "stop": 0.5, "step": 0.025, "value": 0.25},
    ])
    return (h_panel,)


@app.cell(hide_code=True)
def _(delib, go, h_panel, mo, np):
    # Beat 5 — interactive hero: Euler polyline (red) vs exact solution
    # (blue) for y' = y - x^2 with y(0) = 1, parametrised by h. Number of
    # steps adapts so the walk always covers x in [0, 2].
    _f = lambda x, y: y - x**2
    _h = float(h_panel.value["h"])
    _x_end = 2.0
    _n = max(1, int(round(_x_end / _h)))

    _xs_e, _ys_e = delib.euler_steps(_f, 0.0, 1.0, _h, _n)

    _xs_exact = np.linspace(0, _x_end, 200)
    _ys_exact = 2 + 2 * _xs_exact + _xs_exact**2 - np.exp(_xs_exact)

    _fig = delib.slope_field_plotly(
        _f, (-0.1, 2.2), (0.5, 3.3),
        density=18,
        title=f"y' = y − x²  with  h = {_h:.3f}   ({_n} steps to x = 2)",
    )
    _fig.add_trace(go.Scatter(
        x=_xs_exact, y=_ys_exact, mode="lines",
        line=dict(color="#5b7db1", width=3),
        name="exact solution",
    ))
    _fig.add_trace(go.Scatter(
        x=_xs_e, y=_ys_e, mode="lines+markers",
        line=dict(color="#d1495b", width=2),
        marker=dict(size=7, color="#d1495b", symbol="circle",
                    line=dict(color="#7a2a3a", width=1)),
        name=f"Euler walk (h = {_h:.3f})",
    ))

    # Gap at the endpoint — the single number that says "how wrong are
    # you at x = 2 with this h?" Useful for the halving-the-step ratio
    # the prose calls out.
    _exact_end = 2 + 2 * _x_end + _x_end**2 - np.exp(_x_end)
    _gap_end = _ys_e[-1] - _exact_end
    _fig.update_layout(
        showlegend=True,
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.8)"),
    )

    mo.vstack([
        h_panel,
        _fig,
        mo.md(
            rf"At $x = 2$: Euler gives $y \approx {_ys_e[-1]:.4f}$, "
            rf"exact $y \approx {_exact_end:.4f}$, "
            rf"**gap $= {_gap_end:+.4f}$**."
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 6 (intro) — turn the slider's "halving h halves the error"
    # observation into a formula. Briefly distinguish local vs global
    # error, sketch the Taylor argument for why Euler is order 1, set
    # up the log-log figure below as the empirical confirmation.
    mo.md(
        r"""
        ## Why halving the step halves the error

        The slider gave you the headline result: shrink $h$, and the
        gap at $x = 2$ shrinks by roughly the same factor. Let's name
        the relationship.

        For a numerical method, the **global error** $E(h)$ is how far
        off the numerical solution is from the true solution at a fixed
        final $x$, when you took the walk with step size $h$. For most
        well-behaved methods, this error settles into the form

        $$
        E(h) \;\approx\; C \cdot h^{p}
        $$

        for some constant $C$ that depends on the equation and the
        interval, and some exponent $p$ that depends only on the
        **method**. That exponent $p$ is the method's **order of
        accuracy**. Euler's method is **first-order**, meaning $p = 1$:
        the error is proportional to $h$. Halve $h$, halve the error.

        ### Where does $p = 1$ come from?

        Take a Taylor expansion of the true solution around the current
        point $(x_n, y_n)$:

        $$
        y(x_n + h) \;=\; y(x_n) \;+\; h\, y'(x_n) \;+\; \tfrac{1}{2}\, h^2\, y''(x_n) \;+\; \mathcal{O}(h^3).
        $$

        Euler's step *only keeps the first two terms* — it uses
        $y(x_n) + h \cdot f(x_n, y_n)$, which is exactly $y(x_n) + h
        \cdot y'(x_n)$. So the **per-step error** (called the *local
        truncation error*) is what Euler threw away:

        $$
        y(x_n + h) \;-\; \bigl[y_n + h \cdot f(x_n, y_n)\bigr]
        \;=\; \tfrac{1}{2}\, h^2\, y''(x_n) \;+\; \mathcal{O}(h^3).
        $$

        Each step costs you something on the order of $h^2$. But to
        walk across a fixed interval of length $L$, you take $L/h$
        steps — and these errors accumulate. Multiplying $h^2$ per
        step by $L/h$ steps gives a **global error of order $h$**.
        That's Euler's $p = 1$.

        The argument generalises. Any method whose per-step error is
        $\mathcal{O}(h^{p+1})$ has global error $\mathcal{O}(h^{p})$,
        because you take $L/h$ such steps. So matching higher-order
        Taylor terms in the local step buys you a steeper error
        curve globally. The well-known **RK4** method matches through
        $h^4$ locally, so its global error is $\mathcal{O}(h^4)$ —
        quartic. We'll build it later in the chapter.

        ### See it on a log-log plot

        We have a *prediction* — $E(h) \approx C \cdot h$ for Euler —
        and we'd like to verify it from actual numbers. The cleanest
        way is to plot the error against the step size, but on
        **logarithmic axes** for both. Here's why.

        Take the logarithm of both sides of $E = C \cdot h^p$:

        $$
        \log E \;=\; \log C \;+\; p \cdot \log h.
        $$

        Compare with the equation of a straight line, $y = b + m \cdot x$.
        Same shape. With $\log h$ playing the role of $x$ and $\log E$
        the role of $y$, the exponent $p$ becomes the **slope** of a
        straight line. So a power law $E = C h^p$ — which on linear
        axes is a curve — becomes a **straight line on log-log axes**,
        and the *slope of that line is the exponent you're trying to
        measure*. That's the entire trick. Log-log plots are the
        microscope physicists and engineers reach for whenever they
        suspect something obeys a power law and want to read off the
        exponent.

        Let's take an example on the same anchor equation we've been
        walking all chapter, $y' = y - x^2$ with $y(0) = 1$. We'll
        pick **nine step sizes** spaced cleanly along the log axis —
        the "1, 2, 5" sequence per decade that scientific plots
        traditionally use: $h = 0.5,\; 0.2,\; 0.1,\; 0.05,\; 0.02,\;
        0.01,\; 0.005,\; 0.002,\; 0.001$.

        For each one of those nine $h$ values, we run a **completely
        independent** Euler walk:

        1. Start fresh at $(x_0, y_0) = (0, 1)$.
        2. Take $n = 2 / h$ steps of width $h$, applying the rule
           from earlier: $y_{n+1} = y_n + h \cdot f(x_n, y_n)$.
        3. After $n$ steps you've arrived at $x = 2$. Call the final
           $y$ value $y_\text{Euler}$.
        4. Compare to the exact value
           $y(2) = 2 + 4 + 4 - e^2 \approx 2.611$.
        5. The **error** for this $h$ is $|y_\text{Euler} - y(2)|$.

        So each row of the table below is *its own walk*, not a
        refinement of the previous one. The interval covered is
        always $x \in [0, 2]$, but the granularity changes:
        $h = 0.5$ gets there in $4$ giant steps, $h = 0.1$ takes
        $20$ steps, $h = 0.001$ takes $2000$ tiny ones. The
        question we're asking is: *how much accuracy do we buy by
        taking more, smaller steps?*

        Plot those nine $(h,\; |\text{error}|)$ pairs on log-log
        axes and lay a dashed reference line of slope $1$ on top.
        If the Taylor argument is right, the red dots should lie on
        that reference line — at least once $h$ is small enough.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, go, np):
    # Beat 6 — log-log plot of |gap at x = 2| vs h for Euler on the
    # anchor equation y' = y - x^2. Reference dashed line of slope 1
    # makes the order-of-accuracy claim visually checkable. Same
    # equation as Beats 1, 3, 4, 5 — the chapter has one running
    # anchor for the smooth-convergence story.
    _f = lambda x, y: y - x**2
    _x_end = 2.0
    _exact_end = 2 + 2 * _x_end + _x_end**2 - float(np.exp(_x_end))

    # 1-2-5 sequence per decade — the cleanest spacing for log axes,
    # and the only h values that fall *on* the visible tick marks (no
    # more arbitrary 0.0078125-flavoured numbers). Spans 3 decades.
    _hs = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]
    _errs = []
    for _h in _hs:
        _n = max(1, int(round(_x_end / _h)))
        _, _ys = delib.euler_steps(_f, 0.0, 1.0, _h, _n)
        _errs.append(abs(float(_ys[-1]) - _exact_end))

    # Reference line through the smallest-h point with slope exactly 1.
    _h_arr = np.array(_hs)
    _e_arr = np.array(_errs)
    _C_ref = _e_arr[-1] / _h_arr[-1]  # anchor at the cleanest point
    _ref = _C_ref * _h_arr

    # Per-point text labels: "h = 0.05, E = 0.047" beside each marker
    # so the picture is self-contained without a table look-up.
    _labels = [f"h = {h:g},  E = {e:.3g}" for h, e in zip(_hs, _errs)]

    _fig = go.Figure()
    _fig.add_trace(go.Scatter(
        x=_h_arr, y=_ref, mode="lines",
        line=dict(color="#7c8aa0", width=1.8, dash="dash"),
        name="slope 1 reference  (E = C·h)",
        hoverinfo="skip",
    ))
    _fig.add_trace(go.Scatter(
        x=_h_arr, y=_e_arr, mode="lines+markers+text",
        line=dict(color="#d1495b", width=2),
        marker=dict(size=10, color="#d1495b",
                    line=dict(color="#7a2a3a", width=1.2)),
        text=_labels,
        textposition="top left",
        textfont=dict(size=11, color="#7a2a3a"),
        cliponaxis=False,
        name="Euler — measured |gap at x = 2|",
        hovertemplate="h = %{x:.4f}<br>|error| = %{y:.4e}<extra></extra>",
    ))
    # dtick=1 on a log axis = one tick per decade; suppresses the
    # 2,3,...9 minor labels that were reading as a second axis. Range
    # padded on the left for the leftmost label and on the right so the
    # 'h = 0.5, E = ...' label doesn't clip.
    _fig.update_layout(
        template="plotly_white",
        title=dict(
            text="Order of accuracy: |error at x = 2|  vs  step size h   "
                 "(y' = y − x²)",
            x=0.02,
        ),
        xaxis=dict(title="step size  h  (log scale)", type="log",
                   dtick=1, minor=dict(showgrid=False),
                   range=[np.log10(_hs[-1]) - 0.6, np.log10(_hs[0]) + 0.5],
                   zeroline=False),
        yaxis=dict(title="|error at x = 2|  (log scale)", type="log",
                   dtick=1, minor=dict(showgrid=False),
                   range=[np.log10(min(_errs)) - 0.7, np.log10(max(_errs)) + 0.6],
                   zeroline=False),
        paper_bgcolor="white", plot_bgcolor="white",
        height=560, showlegend=True,
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.85)"),
        margin=dict(l=70, r=40, t=60, b=55),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(delib, mo, np):
    # Beat 6 — post-figure walk-through: how to read slope 1 off the
    # picture, the ratio table, and the cost argument that motivates
    # RK4 in the next beat.
    _f = lambda x, y: y - x**2
    _x_end = 2.0
    _exact_end = 2 + 2 * _x_end + _x_end**2 - float(np.exp(_x_end))
    _hs = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]
    _errs = []
    for _h in _hs:
        _n = max(1, int(round(_x_end / _h)))
        _, _ys = delib.euler_steps(_f, 0.0, 1.0, _h, _n)
        _errs.append(abs(float(_ys[-1]) - _exact_end))

    # Table compares the h-shrink ratio to the error-shrink ratio. For
    # first-order (slope 1), they should match. With the 1-2-5 sequence
    # the h ratio alternates 2.5, 2, 2, 2.5, 2, 2, ... and the error
    # ratio tracks it almost exactly once h is small.
    _rows = ["| h | n_steps | \\|error\\| | h(prev) / h(cur) | error(prev) / error(cur) |",
             "|---|---|---|---|---|"]
    _prev_h, _prev_e = None, None
    for _h, _e in zip(_hs, _errs):
        _hr = "—" if _prev_h is None else f"{_prev_h / _h:.2f}"
        _er = "—" if _prev_e is None else f"{_prev_e / _e:.3f}"
        _n = max(1, int(round(_x_end / _h)))
        _rows.append(f"| {_h:g} | {_n} | {_e:.4e} | {_hr} | {_er} |")
        _prev_h, _prev_e = _h, _e
    _table = "\n".join(_rows)

    mo.md(
        "### What the picture says about the trade-off\n\n"
        "**The exchange rate is one-for-one.** *Whatever factor you "
        "shrink $h$ by, the error shrinks by the same factor* — at "
        "least once $h$ is small enough. Look at the leftmost pair "
        "of dots: $h$ doubles from $0.001$ to $0.002$ and the error "
        "doubles from $0.000999$ to $0.001995$. Step right one pair "
        "and $h$ goes up $2.5\\times$; the error goes up $2.5\\times$ "
        "too. Both axes move in lockstep. So *the number of extra "
        "steps you take is literally how much accuracy you buy*. "
        "Halve $h$ → twice as many steps → twice the accuracy. Ten "
        "times the steps → ten times the accuracy. That linear trade "
        "is the whole bargain Euler offers.\n\n"
        "**The bargain breaks down at large $h$.** Out at $h = 0.5$ "
        "the red point sits *below* the dashed reference — the error "
        "grew a little slower than the formula predicted. The "
        "first-order rule $E \\approx C h$ is an **asymptotic** "
        "statement, true only in the small-$h$ limit. At $h = 0.5$ "
        "the higher-order Taylor terms (the $h^2$, $h^3$ bits Euler "
        "threw away when we derived the rule above) still bend the "
        "curve, and the constant $C$ hasn't even stabilised. The "
        "practical lesson: don't trust the slope-1 cost model when "
        "$h$ is big. Shrink $h$ until consecutive rows of the table "
        "give matching ratios, *then* use the model to plan further "
        "refinement.\n\n"
        f"{_table}\n\n"
        "**The trade-off, named.** Now we can answer the question we "
        "started with — *how much accuracy do we buy by taking more, "
        "smaller steps?* — with a sharp number: **for Euler, it's "
        "one-for-one, forever.** Want $10\\times$ better accuracy? "
        "Take $10\\times$ more steps, do $10\\times$ more compute. "
        "Want $100\\times$ better accuracy? $100\\times$ more compute. "
        "Want six digits where you currently have two? A million "
        "times more compute. That's fine when the equation is benign "
        "and two digits are enough. It's painful when you need real "
        "precision, or when you're running a simulation in real time "
        "and a $10\\times$ slowdown knocks you out of budget.\n\n"
        "The next section builds **RK4**, which changes the exchange "
        "rate. With RK4 you buy $10\\times$ more accuracy for only "
        "$10^{1/4} \\approx 1.8\\times$ more compute. A million times "
        "more accuracy for only $\\approx 32\\times$ more compute. "
        "That's the whole reason RK4 exists, and it's the central "
        "trade-off all of numerical analysis circles back to."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 7 (intro) — motivate higher-order methods by going back to
    # what Euler threw away: the slope it used was only the slope at the
    # *start* of the interval. Introduce Heun's method (RK2) as the
    # first improvement, derived as the trapezoidal rule applied to the
    # integral of y'.
    mo.md(
        r"""
        ## A better walk: sample the slope more than once per step

        We've named the trade-off Euler offers — one unit of compute
        buys one unit of accuracy, forever. Now we ask whether a
        cleverer rule can change the exchange rate.

        Go back to what Euler actually does. At step $n$, it reads
        the slope $f(x_n, y_n)$ at the *start* of the interval, then
        uses that *single number* as if it were the slope across the
        entire interval $[x_n, x_n + h]$. But the true solution
        curves. The slope at the start is only an instantaneous
        snapshot — by the time you're halfway through the step, the
        true slope has already changed a little.

        So here's the natural question: **what if we sampled the
        slope at more than one point within the step, and combined
        the samples cleverly?** That's the entire idea behind the
        Runge–Kutta family of methods. We'll build it up in two
        moves: first a method that samples the slope **twice**
        (start and end), and then RK4, which samples **four times**.

        ### Move 1 — average the start slope and the end-guess slope

        Here's the most obvious improvement on Euler. At step $n$,
        with current point $(x_n, y_n)$:

        - Read the slope at the start: $k_1 = f(x_n, y_n)$.
        - Use $k_1$ to make a tentative Euler step to the end:
          $\tilde y = y_n + h \cdot k_1$. This is just one provisional
          Euler step.
        - Now read the slope *at that tentative endpoint*:
          $k_2 = f(x_n + h, \tilde y)$.
        - For the actual step, **average the two slopes** and use the
          average as the slope across the whole interval:

        $$
        y_{n+1} \;=\; y_n \;+\; \frac{h}{2}\,(k_1 + k_2).
        $$

        This is called **Heun's method**, or "improved Euler," or
        RK2. The intuition is geometric: instead of trusting the
        slope at one end of the interval, you peek at what the slope
        would be at the other end and split the difference.

        **Why it's better.** Look at the update formula
        $\tfrac{h}{2}(k_1 + k_2)$ and compare it to integrating the
        true derivative across the interval,
        $\int_{x_n}^{x_n + h} y'(s)\, ds$. Approximating that integral
        by a *single* sample at the left end gives $h \cdot k_1$ —
        that's Euler. Approximating it by the *average* of the left
        and right samples times the width is the **trapezoidal
        rule** — that's Heun's. The trapezoidal rule is exact for
        linear integrands and almost-exact for smooth ones, while
        the left-endpoint rule is exact only for constants. So Heun
        captures the *change* in slope across the interval that
        Euler missed, at the cost of one extra slope read per step.

        The Taylor accounting works out to **local error
        $\mathcal{O}(h^3)$, global error $\mathcal{O}(h^2)$**.
        Heun's is *second-order accurate*. Halve $h$ and the error
        drops by a factor of $4$, not $2$. So you've changed the
        exchange rate: each unit of extra compute now buys you a
        *bigger* unit of accuracy.

        ### Watch one Heun's step assemble itself

        The video below builds the construction in five labelled
        stages on $y' = y - x^2$ from $(0, 1)$ with $h = 0.5$. The
        headline comes at the end: Heun's endpoint lands $2.6\times$
        closer to the true solution than Euler's tentative step did,
        for one extra slope read.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Manim hero: one Heun (RK2) step assembling itself on y' = y - x²
    # from (0, 1) with h = 0.5 — k1 read, tentative Euler step, k2 read,
    # averaged-slope real step, true-endpoint comparison.
    delib.video(
        "heun_step.mp4",
        caption="One Heun (RK2) step on  y' = y − x²,   h = 0.5",
        fallback="The Heun-step animation is being rendered "
                 "(see manim/heun_step.py).",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 7 — RK4 recipe. State the four k's and the weighted average,
    # then justify the weights via the Simpson's-rule connection (in the
    # autonomous case f(x, y) = g(x), RK4 literally *is* Simpson's rule
    # applied to the integral of g).
    mo.md(
        r"""
        ### Move 2 — sample four times, weighted average

        Heun's already gave us order 2 for one extra slope read.
        What if we sample the slope **four times** within each step,
        chosen carefully, and combine them with the right weights?
        That's **RK4** — the classical fourth-order Runge–Kutta
        method, the one that every numerical library reaches for as
        its default.

        At step $n$, starting from $(x_n, y_n)$:

        $$
        \begin{aligned}
        k_1 &= f(x_n,\;\; y_n) \\
        k_2 &= f\!\left(x_n + \tfrac{h}{2},\;\; y_n + \tfrac{h}{2}\, k_1\right) \\
        k_3 &= f\!\left(x_n + \tfrac{h}{2},\;\; y_n + \tfrac{h}{2}\, k_2\right) \\
        k_4 &= f\!\left(x_n + h,\;\;\;\;\, y_n + h\, k_3\right) \\[4pt]
        y_{n+1} &= y_n + \frac{h}{6}\bigl(k_1 + 2 k_2 + 2 k_3 + k_4\bigr).
        \end{aligned}
        $$

        Read what's happening operationally:

        - $k_1$ is the slope at the *start* of the interval — same as
          Euler's only slope.
        - $k_2$ uses $k_1$ to project to the **midpoint**, then reads
          the slope there. A first guess at what's happening in the
          middle of the step.
        - $k_3$ uses $k_2$ to project to the midpoint *again* (with
          the refined slope), and re-reads. A second, better guess at
          the midpoint.
        - $k_4$ uses $k_3$ to project all the way to the **end** of
          the step, and reads the slope there.

        So you've sampled the slope at four points within the
        interval: once at the start, **twice** at the middle (cross-
        checking each other), and once at the end. Now combine them
        with weights $(1, 2, 2, 1) / 6$ — the start and end get
        weight $1$, each midpoint sample gets weight $2$, divide by
        $6$ so the weights sum to $1$.

        ### Why those weights?

        The weights $(1, 2, 2, 1)/6$ are chosen so that the Taylor
        expansion of the RK4 update matches the true solution through
        $h^4$. The full coefficient-matching argument is mostly
        bookkeeping — numerical-methods textbooks work through it
        carefully if you're curious. We'll skip the derivation and
        just trust the result: by spending four slope evaluations per
        step, the per-step error drops to $\mathcal{O}(h^5)$, which
        gives global error $\mathcal{O}(h^4)$ — fourth-order
        accurate, exactly as advertised.

        **What you've bought.** Four slope evaluations per step
        instead of one — i.e. $4\times$ the per-step cost. In
        exchange the order jumped from $1$ (Euler) to $4$ (RK4).
        Halving $h$ now divides the error by $2^4 = 16$, not $2$.
        Want $10\times$ more accuracy? Shrink $h$ by only
        $10^{1/4} \approx 1.8\times$, which costs only
        $\approx 1.8 \times 4 \approx 7\times$ more compute than
        Euler at the original $h$. For modest accuracy that ratio
        sounds bad. For *high* accuracy the gap is astronomical, as
        the numbers below make vivid.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 8 (intro) — frame the two hero figures: a coarse-h trajectory
    # picture so the order difference is *visible*, and a log-log
    # convergence plot stacking the three power laws so the orders are
    # legible as slopes.
    mo.md(
        r"""
        ## Three methods, side by side

        Let's see the orders in action. The two figures below run
        Euler, Heun, and RK4 on the same equation, $y' = y - x^2$
        from $(0, 1)$.

        The **first** is a trajectory comparison at a deliberately
        coarse step, $h = 0.4$ — five steps to cross $x \in [0, 2]$.
        Coarse enough that Euler's polyline is visibly off, Heun's
        tracks more closely but is still imperfect, and RK4's
        polyline is nearly indistinguishable from the exact curve.

        The **second** restates the log-log convergence picture from
        before, now with all three methods on the same axes — three
        straight lines of different slopes ($1$, $2$, $4$). The
        steeper the line, the dramatically cheaper accuracy gets as
        you shrink $h$.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, go, np):
    # Beat 8 — trajectory hero. y' = y - x^2 from (0, 1) at h = 0.4
    # (5 steps to x = 2). Slope field + exact curve + three polylines:
    # Euler (visibly off), Heun (close), RK4 (essentially on the curve).
    _f = lambda x, y: y - x**2
    _h, _n = 0.4, 5

    _xs_eu, _ys_eu = delib.euler_steps(_f, 0.0, 1.0, _h, _n)
    _xs_he, _ys_he = delib.heun_steps(_f, 0.0, 1.0, _h, _n)
    _xs_rk, _ys_rk = delib.rk4_steps(_f, 0.0, 1.0, _h, _n)

    _xs_exact = np.linspace(0, 2.0, 200)
    _ys_exact = 2 + 2 * _xs_exact + _xs_exact**2 - np.exp(_xs_exact)

    _fig = delib.slope_field_plotly(
        _f, (-0.1, 2.2), (0.5, 3.3), density=18,
        title="Euler vs Heun (RK2) vs RK4  —  y' = y − x², h = 0.4, 5 steps",
    )
    _fig.add_trace(go.Scatter(
        x=_xs_exact, y=_ys_exact, mode="lines",
        line=dict(color="#5b7db1", width=3),
        name="exact solution",
    ))
    _fig.add_trace(go.Scatter(
        x=_xs_eu, y=_ys_eu, mode="lines+markers",
        line=dict(color="#d1495b", width=2),
        marker=dict(size=9, color="#d1495b",
                    line=dict(color="#7a2a3a", width=1)),
        name=f"Euler  (order 1) — end gap {abs(_ys_eu[-1] - _ys_exact[-1]):.3f}",
    ))
    _fig.add_trace(go.Scatter(
        x=_xs_he, y=_ys_he, mode="lines+markers",
        line=dict(color="#e9a23b", width=2),
        marker=dict(size=9, color="#e9a23b",
                    line=dict(color="#8a5c0e", width=1)),
        name=f"Heun  (order 2) — end gap {abs(_ys_he[-1] - _ys_exact[-1]):.3f}",
    ))
    _fig.add_trace(go.Scatter(
        x=_xs_rk, y=_ys_rk, mode="lines+markers",
        line=dict(color="#2a9d8f", width=2),
        marker=dict(size=9, color="#2a9d8f",
                    line=dict(color="#1d6e64", width=1)),
        name=f"RK4   (order 4) — end gap {abs(_ys_rk[-1] - _ys_exact[-1]):.5f}",
    ))
    _fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.9)",
                    font=dict(size=11)),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 8 — caption for the trajectory hero, calling out what to
    # notice as the reader compares the three polylines.
    mo.md(
        r"""
        Five steps each, same step size, same starting point, same
        equation. The only thing that changes between the polylines
        is **how many slope samples each method takes per step** —
        $1$ for Euler, $2$ for Heun, $4$ for RK4. Read the end-gap
        numbers in the legend: Euler is off by $0.26$, Heun by
        $0.12$, RK4 by $0.0005$. RK4 is **about 500× closer to the
        exact curve than Euler** here, for $4\times$ the per-step
        cost. The cost ratio is fixed; the accuracy ratio explodes
        as the order increases.

        Now the same story as a convergence plot.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, go, np):
    # Beat 8 — log-log convergence hero. Three methods, same h sweep,
    # three power-law lines that should land on three reference slopes
    # (1, 2, 4). The figure stack puts the orders on top of each other
    # for visual comparison.
    _f = lambda x, y: y - x**2
    _x_end = 2.0
    _exact_end = 2 + 2 * _x_end + _x_end**2 - float(np.exp(_x_end))

    _hs = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]
    _err_eu, _err_he, _err_rk = [], [], []
    for _h in _hs:
        _n = max(1, int(round(_x_end / _h)))
        _, _y_e = delib.euler_steps(_f, 0.0, 1.0, _h, _n)
        _, _y_h = delib.heun_steps(_f, 0.0, 1.0, _h, _n)
        _, _y_r = delib.rk4_steps(_f, 0.0, 1.0, _h, _n)
        _err_eu.append(abs(float(_y_e[-1]) - _exact_end))
        _err_he.append(abs(float(_y_h[-1]) - _exact_end))
        _err_rk.append(abs(float(_y_r[-1]) - _exact_end))

    _h_arr = np.array(_hs)

    # Reference power-law lines, anchored at the smallest h for each
    # method (where the asymptotic regime is cleanest).
    _ref_eu = _err_eu[-1] * (_h_arr / _hs[-1]) ** 1
    _ref_he = _err_he[-1] * (_h_arr / _hs[-1]) ** 2
    _ref_rk = _err_rk[-1] * (_h_arr / _hs[-1]) ** 4

    _fig = go.Figure()
    # Reference lines first so the data sits on top.
    _fig.add_trace(go.Scatter(
        x=_h_arr, y=_ref_eu, mode="lines",
        line=dict(color="#d1495b", width=1.3, dash="dash"),
        name="slope 1 reference  (∝ h¹)",
        hoverinfo="skip",
    ))
    _fig.add_trace(go.Scatter(
        x=_h_arr, y=_ref_he, mode="lines",
        line=dict(color="#e9a23b", width=1.3, dash="dash"),
        name="slope 2 reference  (∝ h²)",
        hoverinfo="skip",
    ))
    _fig.add_trace(go.Scatter(
        x=_h_arr, y=_ref_rk, mode="lines",
        line=dict(color="#2a9d8f", width=1.3, dash="dash"),
        name="slope 4 reference  (∝ h⁴)",
        hoverinfo="skip",
    ))
    _fig.add_trace(go.Scatter(
        x=_h_arr, y=_err_eu, mode="lines+markers",
        line=dict(color="#d1495b", width=2),
        marker=dict(size=10, color="#d1495b",
                    line=dict(color="#7a2a3a", width=1.2)),
        name="Euler  (order 1)",
        hovertemplate="h = %{x:.4f}<br>Euler error = %{y:.3e}<extra></extra>",
    ))
    _fig.add_trace(go.Scatter(
        x=_h_arr, y=_err_he, mode="lines+markers",
        line=dict(color="#e9a23b", width=2),
        marker=dict(size=10, color="#e9a23b",
                    line=dict(color="#8a5c0e", width=1.2)),
        name="Heun  (order 2)",
        hovertemplate="h = %{x:.4f}<br>Heun error = %{y:.3e}<extra></extra>",
    ))
    _fig.add_trace(go.Scatter(
        x=_h_arr, y=_err_rk, mode="lines+markers",
        line=dict(color="#2a9d8f", width=2),
        marker=dict(size=10, color="#2a9d8f",
                    line=dict(color="#1d6e64", width=1.2)),
        name="RK4   (order 4)",
        hovertemplate="h = %{x:.4f}<br>RK4 error = %{y:.3e}<extra></extra>",
    ))

    _y_min = min(min(_err_rk), min(_ref_rk))
    _y_max = max(max(_err_eu), max(_ref_eu))

    _fig.update_layout(
        template="plotly_white",
        title=dict(
            text="Convergence: |error at x = 2|  vs  h  for three methods "
                 "(y' = y − x²)",
            x=0.02,
        ),
        xaxis=dict(title="step size  h  (log scale)", type="log",
                   dtick=1, minor=dict(showgrid=False),
                   range=[np.log10(_hs[-1]) - 0.6, np.log10(_hs[0]) + 0.5],
                   zeroline=False),
        yaxis=dict(title="|error at x = 2|  (log scale)", type="log",
                   dtick=1, minor=dict(showgrid=False),
                   range=[np.log10(_y_min) - 0.7, np.log10(_y_max) + 0.5],
                   zeroline=False),
        paper_bgcolor="white", plot_bgcolor="white",
        height=540, showlegend=True,
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.9)",
                    font=dict(size=11)),
        margin=dict(l=70, r=20, t=60, b=55),
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 8 — closing insight: the three slopes ARE the orders, and
    # the gap between them at small h is the practical case for higher
    # order. Sets up the stiffness section below.
    mo.md(
        r"""
        Three straight lines, three different steepnesses. **The
        slope of each line is the order of the method.** Euler hugs
        the slope-$1$ reference; Heun follows slope $2$; RK4 tracks
        slope $4$. (The slight bend at large $h$ is the same
        higher-order-Taylor-terms effect we noticed earlier — the
        asymptotic formula isn't tight until $h$ is small.)

        The **practical** content is the vertical separation between
        the lines. At $h = 0.01$, Euler's error is $\sim\!10^{-2}$,
        Heun's is $\sim\!10^{-4}$, RK4's is $\sim\!10^{-10}$. **Eight
        orders of magnitude** between Euler and RK4 at the same step
        size on the same equation. RK4 pays $4\times$ more per step;
        in return it eats eight decimal digits of error that Euler
        could only buy by taking $10^{8}$ times more steps. That's
        why production solvers default to an order-$4$ or order-$5$
        method, not Euler.

        Everything above assumed that **shrinking $h$ always helps**.
        The next section shows a kind of equation where that
        assumption breaks sharply — and where neither RK4 nor any
        amount of step shrinking saves you, until we change the
        *family* of method entirely.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 9 (intro) — switch anchor equation to radioactive decay
    # N' = -lambda N, which is the textbook test case for stability.
    # Frames the next several cells: even though Euler converges smoothly
    # on benign equations, on decaying equations there's a sharp h
    # threshold above which the numerical solution oscillates and blows
    # up, and "shrink h" stops being a free lunch.
    mo.md(
        r"""
        ## When more steps stops helping: stiffness

        The convergence story above was tidy: shrink $h$, get less
        error, repeat. That tidy picture relied on the equation
        being well-behaved. Let's try the method on a different kind
        of equation — one where things go very differently.

        Take

        $$
        \frac{dN}{dt} \;=\; -\lambda\, N, \qquad N(0) = N_0,
        $$

        with some positive constant $\lambda$. This equation
        describes any process where the **rate of decrease is
        proportional to the current amount**: a radioactive sample
        thinning out over time, a capacitor discharging through a
        resistor, a drug clearing from your bloodstream, hot coffee
        cooling toward room temperature (the Newton's-cooling
        equation we met in Chapter 2 is the same shape). The bigger
        $\lambda$, the faster the decay. The exact solution is the
        familiar $N(t) = N_0\, e^{-\lambda t}$ — a smooth, monotonic
        decay to zero. Any sane numerical method should reproduce
        it.

        Apply Euler at step size $h$:

        $$
        N_{n+1} \;=\; N_n + h \cdot (-\lambda N_n) \;=\; N_n (1 - h\lambda).
        $$

        So each step *multiplies* the current value by the constant
        $1 - h\lambda$. Call that constant the **amplification
        factor**. After $n$ steps,

        $$
        N_n \;=\; N_0 \cdot (1 - h\lambda)^n.
        $$

        For the numerical solution to behave like the true one — decay
        smoothly toward zero — we need the amplification factor to
        satisfy $|1 - h\lambda| < 1$. Solve:

        $$
        |1 - h\lambda| < 1 \quad \Longleftrightarrow \quad 0 < h\lambda < 2.
        $$

        That gives a **hard ceiling on $h$**:

        $$
        h \;<\; \frac{2}{\lambda}.
        $$

        Above that ceiling, $1 - h\lambda$ has magnitude $\ge 1$, and
        instead of decaying, the numerical solution **oscillates
        between positive and negative values with growing magnitude**.
        Negative *amount of radioactive material* — physically
        nonsense — and the magnitude grows without bound as you take
        more steps. The figure below makes this visible.
        """
    )
    return


@app.cell(hide_code=True)
def _(go, mo, np):
    # Beat 9 — Euler on radioactive decay at four h values bracketing
    # the 2/lambda stability threshold. lambda = 1, t in [0, 8], so the
    # threshold is at h = 2. Pick h = 0.5 (well-behaved), h = 1.5
    # (oscillates but bounded), h = 2.5 (blows up oscillating), h = 3.0
    # (blows up wildly). Exact decay overlaid in blue for reference.
    _lam = 1.0
    _N0 = 1.0
    _t_end = 8.0
    _hs = [0.5, 1.5, 2.5, 3.0]
    _colors = ["#2a9d8f", "#e9a23b", "#d1495b", "#7a1a2a"]

    _fig = go.Figure()
    _ts_e = np.linspace(0, _t_end, 200)
    _ns_e = _N0 * np.exp(-_lam * _ts_e)
    _fig.add_trace(go.Scatter(
        x=_ts_e, y=_ns_e, mode="lines",
        line=dict(color="#5b7db1", width=3),
        name="exact:  N(t) = N₀ e^(−λt)",
    ))

    for _h, _color in zip(_hs, _colors):
        _n = max(1, int(round(_t_end / _h)))
        _ts = np.arange(_n + 1) * _h
        _ns = np.empty(_n + 1)
        _ns[0] = _N0
        _amp = 1 - _h * _lam
        for _i in range(_n):
            _ns[_i + 1] = _ns[_i] * _amp
        _final_mag = abs(_ns[-1])
        _tag = ("stable" if abs(_amp) < 1
                else "marginal" if abs(_amp) == 1
                else "BLOWING UP")
        _fig.add_trace(go.Scatter(
            x=_ts, y=_ns, mode="lines+markers",
            line=dict(color=_color, width=2),
            marker=dict(size=8, color=_color),
            name=f"Euler h = {_h:.1f}   (1 − hλ = {_amp:+.2f}, {_tag})",
        ))

    _fig.update_layout(
        template="plotly_white",
        title=dict(
            text="Euler on radioactive decay  N' = −N, N(0) = 1  "
                 "(stability threshold: h < 2)",
            x=0.02,
        ),
        xaxis=dict(title="t", zeroline=True, zerolinecolor="#bbb"),
        yaxis=dict(title="N(t)", zeroline=True, zerolinecolor="#bbb",
                   range=[-3, 3]),
        paper_bgcolor="white", plot_bgcolor="white",
        height=480, showlegend=True,
        legend=dict(x=0.45, y=0.98, bgcolor="rgba(255,255,255,0.9)",
                    font=dict(size=11)),
        margin=dict(l=60, r=20, t=60, b=55),
    )
    mo.vstack([
        _fig,
        mo.md(
            "This figure uses $\\lambda = 1$, so the amplification "
            "factor is simply $1 - h$: each Euler step multiplies the "
            "current value of $N$ by $(1 - h)$. The stability condition "
            "$|1 - h\\lambda| < 1$ becomes $h < 2$ — that's the "
            "threshold in the title. Each colour is one choice of $h$, "
            "and what you see follows directly from its multiplier:\n\n"
            "- **Teal, $h = 0.5$** — multiplier $1 - 0.5 = +0.5$. Every "
            "step *halves* $N$: positive, shrinking, just like the true "
            "decay. The polyline hugs the exact curve.\n"
            "- **Gold, $h = 1.5$** — multiplier $1 - 1.5 = -0.5$. The "
            "magnitude still shrinks by half each step, **but the sign "
            "is negative**, so $N$ flips between positive and negative "
            "every step: $1 \\to -0.5 \\to 0.25 \\to -0.125 \\to \\dots$ "
            "The polyline zig-zags through zero while slowly dying out. "
            "Bounded, but nothing like the true solution.\n"
            "- **Red, $h = 2.5$** — multiplier $1 - 2.5 = -1.5$. Now the "
            "magnitude **grows** by $1.5\\times$ each step *and* the sign "
            "flips: $1 \\to -1.5 \\to 2.25 \\to -3.375 \\to \\dots$ The "
            "swing widens every step and exits the visible window almost "
            "immediately.\n"
            "- **Dark red, $h = 3.0$** — multiplier $-2$. The swing "
            "*doubles* every step. Total blowup.\n\n"
            "Notice what's *not* happening: the blowup has **nothing "
            "to do with accuracy**. Even the bounded oscillation at "
            "$h = 1.5$ is wildly inaccurate, but the disaster at "
            "$h = 2.5$ and $h = 3$ is qualitatively different — the "
            "solution diverges from *any* reasonable physical answer, "
            "and taking more steps only makes it worse (more steps to "
            "amplify through).\n\n"
            "This is **numerical instability**, and the threshold "
            "$h < 2 / \\lambda$ is sharp. Above it Euler is useless "
            "*at any precision*."
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 9 — what about RK4? It has its own stability threshold, more
    # lenient than Euler but qualitatively the same disease. The polyfit
    # for R(z) = 1 - z + z^2/2 - z^3/6 + z^4/24 has |R(z)| = 1 at
    # z ≈ 2.785 on the real axis, so RK4 buys ~40% more h before blowup
    # but doesn't fix the underlying problem.
    mo.md(
        r"""
        ### Does RK4 save us? Only a little.

        Higher-order methods have *more lenient* stability
        thresholds, but the disease is the same. Working through the
        same algebra for RK4 on this equation gives a stability
        ceiling at $h\lambda \lesssim 2.785$ — about $40\%$ more
        room than Euler, but still a ceiling forced on you by
        stability rather than by accuracy.

        And it gets painful when $\lambda$ is large. If
        $\lambda = 10^6$, both methods need $h \lesssim 10^{-6}$ to
        stay stable. Even if you only care about three digits of
        accuracy, you're forced to take a million tiny steps. **A
        fast component nobody cares about dictates the step size for
        the whole simulation.** That's the textbook definition of a
        **stiff** problem, and it shows up everywhere fast and slow
        time-scales coexist — chemistry, circuits, fluid–chemistry
        coupling, control systems.

        The fix isn't a better explicit method. It's a fundamentally
        different family.

        ### The fix: implicit methods

        Look at Euler again:

        $$
        N_{n+1} \;=\; N_n + h \cdot \underbrace{f(t_n, N_n)}_{\text{slope at the } \mathbf{start}}.
        $$

        The slope is read at the **current** point. That's what
        "explicit" means — the new value is given by a formula in
        terms of the *old* value.

        An **implicit** method reads the slope at the **destination**
        instead:

        $$
        N_{n+1} \;=\; N_n + h \cdot \underbrace{f(t_{n+1}, N_{n+1})}_{\text{slope at the } \mathbf{end}}.
        $$

        Notice the catch: $N_{n+1}$ appears on *both sides*. You
        can't just plug numbers in — you have to **solve** for
        $N_{n+1}$ at every step. For nonlinear $f$ that means running
        a Newton iteration per step (cheap, but a real cost).

        On our linear decay test, though, the algebra closes in one
        line. Substituting $f(t, N) = -\lambda N$:

        $$
        N_{n+1} \;=\; N_n - h \lambda N_{n+1}
        \quad \Longleftrightarrow \quad
        N_{n+1} (1 + h\lambda) = N_n
        \quad \Longleftrightarrow \quad
        N_{n+1} \;=\; \frac{N_n}{1 + h\lambda}.
        $$

        This is **backward Euler**. The amplification factor is now
        $1/(1 + h\lambda)$, which is **always in $(0, 1)$ for any
        $h > 0$**. There is no stability threshold. You can take a
        step of size $h = 10^{6}$ on this equation and the numerical
        solution will still decay monotonically toward zero. It may
        be *inaccurate* — you've skipped over almost all the decay
        in one step — but it won't blow up. The figure below shows
        the same four $h$ values run through backward Euler.
        """
    )
    return


@app.cell(hide_code=True)
def _(go, mo, np):
    # Beat 9 — backward Euler on the same decay test at the same four
    # h values. All four trajectories stay bounded and decay
    # monotonically toward zero, demonstrating that the implicit step
    # has no stability threshold on this problem.
    _lam = 1.0
    _N0 = 1.0
    _t_end = 8.0
    _hs = [0.5, 1.5, 2.5, 3.0]
    _colors = ["#2a9d8f", "#e9a23b", "#d1495b", "#7a1a2a"]

    _fig = go.Figure()
    _ts_e = np.linspace(0, _t_end, 200)
    _ns_e = _N0 * np.exp(-_lam * _ts_e)
    _fig.add_trace(go.Scatter(
        x=_ts_e, y=_ns_e, mode="lines",
        line=dict(color="#5b7db1", width=3),
        name="exact:  N(t) = N₀ e^(−λt)",
    ))

    for _h, _color in zip(_hs, _colors):
        _n = max(1, int(round(_t_end / _h)))
        _ts = np.arange(_n + 1) * _h
        _ns = np.empty(_n + 1)
        _ns[0] = _N0
        _amp = 1.0 / (1.0 + _h * _lam)
        for _i in range(_n):
            _ns[_i + 1] = _ns[_i] * _amp
        _fig.add_trace(go.Scatter(
            x=_ts, y=_ns, mode="lines+markers",
            line=dict(color=_color, width=2),
            marker=dict(size=8, color=_color),
            name=f"Backward Euler h = {_h:.1f}   "
                 f"(1/(1+hλ) = {_amp:+.3f}, stable)",
        ))

    _fig.update_layout(
        template="plotly_white",
        title=dict(
            text="Backward Euler on the same decay  "
                 "(no stability threshold)",
            x=0.02,
        ),
        xaxis=dict(title="t", zeroline=True, zerolinecolor="#bbb"),
        yaxis=dict(title="N(t)", zeroline=True, zerolinecolor="#bbb",
                   range=[-0.1, 1.1]),
        paper_bgcolor="white", plot_bgcolor="white",
        height=440, showlegend=True,
        legend=dict(x=0.45, y=0.98, bgcolor="rgba(255,255,255,0.9)",
                    font=dict(size=11)),
        margin=dict(l=60, r=20, t=60, b=55),
    )
    mo.vstack([
        _fig,
        mo.md(
            "All four trajectories *decay monotonically*, no matter how "
            "big the step. The largest one ($h = 3.0$) is wildly "
            "inaccurate — three points to cover $t \\in [0, 8]$, with "
            "an amplification of $0.25$ per step instead of the true "
            "$e^{-3} \\approx 0.05$ — but the solution is "
            "**qualitatively correct**: positive, decreasing, heading "
            "to zero. That's the point. Implicit methods trade "
            "per-step cost (you solve a small equation for $N_{n+1}$ "
            "instead of computing it directly) for the freedom to "
            "choose $h$ for **accuracy**, not stability. Production "
            "solvers like `scipy.integrate.solve_ivp` switch to "
            "implicit options (`BDF`, `Radau`) the moment they detect "
            "stiffness."
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 10 — adaptive step sizing. Production solvers don't ask you
    # to choose h; they pick it themselves using an embedded-RK error
    # estimate (RKF45 / Dormand–Prince). Closes the chapter with a
    # pointer to Ch 5 (the connection between numerical stability and
    # dynamical-systems stability).
    mo.md(
        r"""
        ## Letting the solver pick the step size

        So far the chapter has assumed *you* pick $h$ and live with
        the consequences. Real solvers don't work that way — they
        **adjust $h$ on the fly**, taking big steps where the
        solution is slow and tame and shrinking $h$ where it
        wiggles fast.

        The trick is to estimate the per-step error cheaply, then
        steer $h$ based on it. The standard idea is **embedded
        Runge–Kutta** methods:

        > Compute two RK steps at the same $h$ — one of order $4$,
        > one of order $5$ — using mostly the same slope samples.
        > The difference between the two answers is your estimate of
        > the per-step error.

        Because the order-$5$ result is much more accurate than the
        order-$4$ one, their difference is essentially the error in
        the cheaper estimate. If that error is bigger than your
        tolerance, reject the step and try a smaller $h$; if it's
        smaller, accept it and consider growing $h$.

        The default in most libraries is **Dormand–Prince**,
        sometimes labelled `RK45`. Six slope evaluations per step
        give you the order-$5$ answer *and* a free error estimate.
        You stop choosing $h$ at all — you choose a tolerance, and
        the solver chooses $h$ step by step:

        ```python
        from scipy.integrate import solve_ivp
        sol = solve_ivp(lambda t, y: y - t**2, (0, 2), [1.0],
                        method="RK45", rtol=1e-8, atol=1e-10)
        ```

        For stiff problems the same machinery wraps an implicit
        per-step solve instead (`Radau`, `BDF` in scipy).

        ### Closing thought

        This chapter has been about **the methods that simulate** a
        differential equation. The next chapter goes the other way:
        instead of asking "what trajectory does the equation
        produce?", it asks "what does the equation tell us about the
        *long-term* behaviour without solving it at all?" The
        numerical tools you just built become exploration aids, not
        the main event.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it — in code

        Three short challenges, one per big idea of the chapter:
        take Euler steps yourself, measure an order of accuracy,
        and find a stability ceiling. `delib.euler_steps`,
        `delib.heun_steps`, and `delib.rk4_steps` are available,
        and `print()` works if you want to inspect intermediate
        values.
        """
    )
    return


# --- Challenge 1: two Euler steps by hand --------------------------------------
@app.cell
def _(mo):
    e1_get, e1_set = mo.state(
        "# For y' = y - x**2 with y(0) = 1 and h = 0.5, take TWO Euler\n"
        "# steps and put the resulting y (at x = 1.0) in `answer`.\n"
        "# Each step: y_new = y + h * (y - x**2), then x_new = x + h.\n"
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
        context="y' = y - x^2, y(0)=1, h=0.5. Step 1: slope f(0,1)=1, "
                "y=1+0.5*1=1.5 at x=0.5. Step 2: slope f(0.5,1.5)=1.5-0.25"
                "=1.25, y=1.5+0.5*1.25=2.125 at x=1.0. Put 2.125 in "
                "`answer`. (delib.euler_steps(f, 0, 1, 0.5, 2) also "
                "works.)",
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_ai, e1_code, e1_gen, e1_run):
    delib.exercise_view(
        "**1.** For $y' = y - x^2$ with $y(0) = 1$ and $h = 0.5$, take "
        "**two Euler steps** and put the resulting $y$ at $x = 1$ in "
        "`answer`. (By hand or with `delib.euler_steps` — your choice.)",
        e1_ai, e1_gen, e1_code, e1_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_code, e1_run):
    delib.run_exercise(e1_code.value, e1_run.value, check=lambda ns: delib.check_number(
        ns, target=2.125, tol=1e-3,
        ok="Right — step 1 lands at $(0.5, 1.5)$, step 2 reads the slope "
           "$1.25$ *at the dot* and lands at $(1.0, 2.125)$.",
        hint="Step 1: slope $f(0,1) = 1$, so $y = 1 + 0.5 \\cdot 1 = 1.5$. "
             "Step 2: read the slope at $(0.5, 1.5)$, not on the true curve.",
    ))
    return


# --- Challenge 2: measure the order of accuracy --------------------------------
@app.cell
def _(mo):
    e2_get, e2_set = mo.state(
        "# Run Euler to x = 2 (y' = y - x**2, y(0) = 1) twice: once with\n"
        "# h = 0.1 and once with h = 0.05. The exact value is\n"
        "# y(2) = 2 + 2*2 + 2**2 - np.exp(2). Compute each |error| and\n"
        "# put the RATIO error(h=0.1) / error(h=0.05) in `answer`.\n"
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
        context="Use delib.euler_steps(lambda x, y: y - x**2, 0, 1, h, n) "
                "with (h=0.1, n=20) and (h=0.05, n=40). exact = 2+4+4-"
                "np.exp(2) ~ 2.611. error(0.1) ~ 0.0888, error(0.05) ~ "
                "0.0471, ratio ~ 1.89. Halving h halved the error — "
                "first-order. Put the ratio in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_ai, e2_code, e2_gen, e2_run):
    delib.exercise_view(
        "**2.** Measure Euler's order yourself: run to $x = 2$ at "
        "$h = 0.1$ and at $h = 0.05$, compute both errors against the "
        "exact $y(2)$, and put the **ratio** "
        "$\\text{error}(0.1) / \\text{error}(0.05)$ in `answer`. "
        "What number should a first-order method give?",
        e2_ai, e2_gen, e2_code, e2_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_code, e2_run):
    delib.run_exercise(e2_code.value, e2_run.value, check=lambda ns: delib.check_number(
        ns, target=1.887, tol=0.05,
        ok="Right — about $1.89$, close to the theoretical $2$ for a "
           "first-order method (it approaches exactly $2$ as $h \\to 0$).",
        hint="`delib.euler_steps(f, 0, 1, 0.1, 20)` and "
             "`delib.euler_steps(f, 0, 1, 0.05, 40)`; compare each final "
             "$y$ against `2 + 4 + 4 - np.exp(2)`.",
    ))
    return


# --- Challenge 3: the stability ceiling -----------------------------------------
@app.cell
def _(mo):
    e3_get, e3_set = mo.state(
        "# For dN/dt = -4*N, Euler's update multiplies N by (1 - 4*h)\n"
        "# each step. What is the LARGEST step size h for which the\n"
        "# numerical solution still decays instead of blowing up?\n"
        "# Put it in `answer`.\n"
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
        context="Stability needs |1 - h*lambda| < 1 with lambda = 4, i.e. "
                "0 < 4h < 2, so h < 2/4 = 0.5. Put 0.5 in `answer`. "
                "(Students can also verify empirically with "
                "delib.euler_steps(lambda t, N: -4*N, 0, 1, h, 20).)",
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_ai, e3_code, e3_gen, e3_run):
    delib.exercise_view(
        "**3.** For $\\dot N = -4N$, what is the **largest** $h$ for which "
        "Euler still decays instead of blowing up? Put it in `answer`. "
        "(Derive it from the amplification factor, or hunt for it "
        "numerically with `delib.euler_steps` — both work.)",
        e3_ai, e3_gen, e3_code, e3_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_code, e3_run):
    delib.run_exercise(e3_code.value, e3_run.value, check=lambda ns: delib.check_number(
        ns, target=0.5, tol=0.02,
        ok="Right — the ceiling is $h = 2/\\lambda = 2/4 = 0.5$. Above it "
           "$|1 - 4h| > 1$ and every step amplifies the error.",
        hint="Stability needs $|1 - h\\lambda| < 1$ with $\\lambda = 4$. "
             "Solve for $h$.",
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
        "f = lambda x, y: y - x**2\n"
        "xs, ys = delib.euler_steps(f, 0.0, 1.0, 0.25, 8)\n"
        "view = delib.slope_field_plotly(f, (-0.1, 2.2), (0.5, 3.3),\n"
        "                                title='Try a different f, h, or method!')\n"
        "view.add_scatter(x=list(xs), y=list(ys), mode='lines+markers',\n"
        "                 name='Euler walk')\n"
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
        context="Open sandbox for chapter 4 (numerical methods). Helpers: "
                "delib.euler_steps(f, x0, y0, h, n), delib.heun_steps(...), "
                "delib.rk4_steps(...) — each returns (xs, ys) arrays — plus "
                "delib.slope_field_plotly(f, xlim, ylim). Write complete "
                "runnable code; assign a Plotly figure to `view`.",
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
        ---
        ## Recap & what's next

        - A first-order ODE assigns a **slope** to every point;
          when no formula exists, you can still **walk the field**:
          step, re-read the slope, repeat. That's Euler's method —
          and, at heart, every physics simulator ever shipped.
        - The walk's error follows $E \approx C h^p$, where $p$ is
          the method's **order of accuracy** — readable as the slope
          of a line on a log-log plot. Euler is order 1; sampling
          the slope twice per step (Heun) gives order 2; four
          careful samples (RK4) give order 4.
        - Higher order changes the **exchange rate** between compute
          and accuracy: at the same step size, RK4 can be millions
          of times more accurate than Euler for only $4\times$ the
          per-step cost.
        - On decaying equations, explicit methods have a **stability
          ceiling** ($h < 2/\lambda$ for Euler): above it, the
          numerical solution oscillates and blows up no matter how
          accurate the method is. **Implicit** methods (backward
          Euler) read the slope at the destination and have no such
          ceiling — the cure for **stiff** problems.
        - Production solvers pick $h$ for you, using an embedded
          pair of estimates to keep a per-step error budget.

        **Next:** instead of simulating an equation forward, we ask
        what its long-term behaviour is — fixed points, stability,
        and the phase line — without solving anything at all.
        """
    )
    return


# --- Tutor (BYO-key chat, from delib) -------------------------------------------
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
        "This is Chapter 4 of a differential-equations course: numerical "
        "methods for first-order ODEs, framed as 'what a physics engine "
        "actually does inside.' Key ideas the reader is working through: "
        "Euler's method as walking the slope field one step at a time; "
        "order of accuracy (Euler is first-order, RK4 is fourth-order); "
        "numerical stability and stiffness (when step size is too big, the "
        "numerical solution oscillates and blows up). The anchor equation "
        "for the smooth-convergence story is y' = y - x^2 with y(0) = 1 "
        "(closed form y = 2 + 2x + x^2 - e^x). The anchor equation for "
        "stiffness is y' = -lambda y. Earlier chapters introduced: slope "
        "fields (Ch 1), separable / linear ODEs and the integrating factor "
        "(Ch 2), exact equations and the integrating-factor rescue (Ch 3a "
        "and Ch 3b).",
        prompts=[
            "explain this chapter in a paragraph",
            "why does my Euler trajectory not match the exact curve?",
            "what does 'order of accuracy' mean?",
        ],
        picked_get=picked_get,
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge, picker):
    delib.tutor_sidebar(api_field, key_bridge, chatbox, picker=picker)
    return
if __name__ == "__main__":
    app.run()
