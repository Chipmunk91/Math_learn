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
