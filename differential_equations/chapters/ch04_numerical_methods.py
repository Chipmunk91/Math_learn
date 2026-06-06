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
              the stability story that haunts every real-world
              simulator.

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

        ### How small is small enough?

        That's what the rest of this chapter answers. Next, an
        animation walks Euler through the field step by step — same
        equation, same $h$, but with the slope vector drawn at each
        step so you can see the recipe in motion. After that you'll
        get a slider for $h$ so you can shrink it yourself and watch
        the red polyline collapse onto the smooth curve.
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

        Same equation as above, $y' = y - x^2$ with $y(0) = 1$, same
        step size $h = 0.25$. The video below builds Euler's walk one
        step at a time. At each step you see the slope vector the
        equation gives at the current point, then the dot stepping
        along that slope, and finally the segment laid down as part
        of the polyline. After eight steps the exact solution comes
        in as an overlay — the gap between the red polyline and the
        smooth blue curve is the per-step error compounding.

        This is the same picture as the hook figure, drawn live.
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
          amount, not catastrophically wrong. This will not be true
          for every equation — Beat 9 shows one where it is.
        - **Halving $h$ roughly halves the error.** Try $h = 0.25$,
          then $h = 0.125$, then $h = 0.0625$, and eyeball the gap at
          $x = 2$. Each halving cuts the gap by about two. That ratio
          is what *first-order accurate* means, and the next section
          turns it into a formula.
        - **It costs you compute.** Halving $h$ doubles the number of
          steps you have to take. In a physics engine running at
          60 Hz over a 10-second simulation, that matters. The whole
          art of numerical integration is buying accuracy *cheaply* —
          which is exactly what RK4 (later in the chapter) is about.
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
        curve globally. **RK4** matches through $h^4$ locally, so its
        global error is $\mathcal{O}(h^4)$ — quartic. We'll build it
        in Beat 7.

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
        "threw away in Beat 6's derivation) still bend the curve, "
        "and the constant $C$ hasn't even stabilised. The practical "
        "lesson: don't trust the slope-1 cost model when $h$ is "
        "big. Shrink $h$ until consecutive rows of the table give "
        "matching ratios, *then* use the model to plan further "
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
        "and two digits are enough. It's brutal when you need real "
        "precision, or when you're running a physics engine at 60 Hz "
        "over a multi-hour simulation and *10× more compute* knocks "
        "you out of real-time.\n\n"
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

        Beat 6 named the trade-off Euler offers — one unit of compute
        buys one unit of accuracy, forever. Now we ask whether a
        cleverer recipe can change the exchange rate.

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
        """
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
        ### Move 2 — sample four times, weight Simpson-style

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

        ### Why those weights? — Simpson's rule in disguise

        The weighting isn't arbitrary; it's stolen from a much older
        result, **Simpson's rule** for numerical integration. To see
        the connection, look at the special case where the equation
        has no $y$-dependence: $y' = g(x)$. Then integrating gives
        the exact answer

        $$
        y(x_n + h) - y(x_n) \;=\; \int_{x_n}^{x_n + h} g(s)\, ds.
        $$

        Simpson's rule approximates that integral as

        $$
        \int_{x_n}^{x_n + h} g(s)\, ds
        \;\approx\; \frac{h}{6}\bigl(g(x_n) + 4\, g(x_n + \tfrac{h}{2}) + g(x_n + h)\bigr),
        $$

        and is **exact for any polynomial $g$ of degree $\le 3$**.
        Now look at what the four RK4 slopes become in this no-$y$
        case: $k_1 = g(x_n)$, $k_2 = g(x_n + h/2)$, $k_3 = g(x_n + h/2)$
        (same as $k_2$ because no $y$-dependence), $k_4 = g(x_n + h)$.
        The RK4 update is

        $$
        \frac{h}{6}(k_1 + 2 k_2 + 2 k_3 + k_4)
        \;=\; \frac{h}{6}\bigl(g(x_n) + 4\, g(x_n + \tfrac{h}{2}) + g(x_n + h)\bigr).
        $$

        That's **exactly Simpson's rule**. So in the autonomous case
        RK4 inherits Simpson's exactness-for-cubics property — local
        error $\mathcal{O}(h^5)$, global error $\mathcal{O}(h^4)$.
        For the general $y' = f(x, y)$ case, $k_2$ and $k_3$ aren't
        equal (the $y$-dependence makes the two midpoint estimates
        slightly different), but their average plays the same
        Simpson-midpoint role, and the order-4 accuracy carries
        through — that's the actual content of the original
        Runge–Kutta derivation, which we won't grind through.

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
def _(delib, mo, np):
    # Beat 7 — numerical comparison: error at x = 2 for Euler, Heun
    # (RK2), and RK4 on the anchor equation, at six h values. Builds
    # the table that makes the order-1 vs order-2 vs order-4 picture
    # impossible to dismiss as theoretical.
    _f = lambda x, y: y - x**2
    _x_end = 2.0
    _exact_end = 2 + 2 * _x_end + _x_end**2 - float(np.exp(_x_end))

    _hs = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01]
    _rows = ["| h | n_steps | Euler \\|err\\| | Heun (RK2) \\|err\\| | RK4 \\|err\\| | RK4 better than Euler by |",
             "|---|---|---|---|---|---|"]
    for _h in _hs:
        _n = max(1, int(round(_x_end / _h)))
        _, _y_e = delib.euler_steps(_f, 0.0, 1.0, _h, _n)
        _, _y_h = delib.heun_steps(_f, 0.0, 1.0, _h, _n)
        _, _y_r = delib.rk4_steps(_f, 0.0, 1.0, _h, _n)
        _e_eu = abs(float(_y_e[-1]) - _exact_end)
        _e_he = abs(float(_y_h[-1]) - _exact_end)
        _e_rk = abs(float(_y_r[-1]) - _exact_end)
        _ratio = _e_eu / _e_rk
        _rows.append(
            f"| {_h:g} | {_n} | {_e_eu:.3e} | {_e_he:.3e} | {_e_rk:.3e} | {_ratio:,.0f}× |"
        )
    _table = "\n".join(_rows)

    mo.md(
        "### See the order in numbers\n\n"
        "Same anchor equation as Beat 6 — $y' = y - x^2$ with "
        "$y(0) = 1$, walk out to $x = 2$, compare to the exact value "
        f"$y(2) \\approx 2.611$. For each $h$, run all three methods "
        f"and tabulate the error.\n\n{_table}\n\n"
        "**Read down each column.** Halve $h$ (e.g. $0.1 \\to 0.05$) "
        "and watch the error column shrink:\n\n"
        "- Euler shrinks by $\\approx 2\\times$ — first order.\n"
        "- Heun shrinks by $\\approx 4\\times$ — second order.\n"
        "- RK4 shrinks by $\\approx 16\\times$ — fourth order.\n\n"
        "Each new order squares the previous error-reduction factor.\n\n"
        "**Read across each row.** At $h = 0.1$ — a reasonable step "
        "size — Euler is off by about $0.09$ (two-digit accuracy), "
        "Heun by $0.0075$ (still two digits), and RK4 by $1.3 \\times "
        "10^{-6}$ (six digits). RK4 is about **67,000× more accurate "
        "than Euler at the same $h$**, for $4\\times$ the per-step "
        "cost. That ratio is *astonishing*. It's why nobody actually "
        "uses Euler when accuracy matters — RK4 dominates it on every "
        "axis except raw simplicity.\n\n"
        "Beat 8 makes this concrete: a single hero figure with all "
        "three methods walking the slope field side by side, and a "
        "log-log convergence plot stacking the three power-law lines "
        "(slope 1, slope 2, slope 4) so the orders are visible at a "
        "glance."
    )
    return


# --- Tutor (BYO-key chat, from delib). Skeleton for now; chapter content
# --- will fill in below as later beats are built.
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
def _(api_field, delib, key_bridge):
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
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge):
    delib.tutor_sidebar(api_field, key_bridge, chatbox)
    return


if __name__ == "__main__":
    app.run()
