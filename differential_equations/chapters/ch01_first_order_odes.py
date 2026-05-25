import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go

    import delib
    return delib, go, mo, np, plt


@app.cell
def _(mo):
    mo.md(
        r"""
        # Chapter 1 — First-order ODEs & slope fields

        **See the field, follow the flow.**

        By the end of this chapter you should be able to:

        - Read a **slope field** as a picture of *every* solution to $y' = f(x, y)$ at once.
        - Predict how a solution curve bends just by looking at the field.
        - Explain how the parameters of an equation reshape the whole flow.
        - Connect **equilibria** (where $y' = 0$) to the horizontal stripes in the field.
        - See a single solution emerge in time as it follows the flow from its start point.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Concept

        A first-order ODE $y' = f(x, y)$ doesn't hand you one solution — it hands
        you a *rule for the slope* at every point of the plane. Draw a tiny arrow
        with slope $f(x, y)$ at a grid of points and you get the **slope field**:
        a map of the flow that every solution must follow.

        Our worked equation is the **logistic** model

        $$ y' = a\,y\left(1 - \frac{y}{K}\right), $$

        with growth rate $a$ and carrying capacity $K$. It has two equilibria,
        $y = 0$ and $y = K$, where the slope is zero and the field goes flat.
        """
    )
    return


@app.cell
def _(delib, np, plt):
    def logistic_grid(a, K):
        """y' = a*y*(1 - y/K), vectorized over a slope-field grid."""
        return lambda x, y: a * y * (1.0 - y / K)

    # A static illustration with fixed parameters, before we make it interactive.
    _f = logistic_grid(1.0, 4.0)
    _ax = delib.slope_field(_f, xlim=(0, 10), ylim=(-1, 6), density=22)
    _ax.axhline(4.0, color="#2a9d8f", lw=1.5, ls="--", label="K = 4 (equilibrium)")
    _ax.axhline(0.0, color="#888", lw=1.0, ls=":", label="y = 0 (equilibrium)")
    _ax.set_title("Slope field of the logistic equation (a = 1, K = 4)")
    _ax.legend(loc="lower right")
    _ax.figure
    return (logistic_grid,)


@app.cell
def _(delib, mo):
    controls = delib.param_panel(
        [
            {"name": "a", "label": "growth rate a", "start": -2.0, "stop": 2.0, "step": 0.1, "value": 1.0},
            {"name": "K", "label": "carrying capacity K", "start": 0.5, "stop": 5.0, "step": 0.1, "value": 4.0},
            {"name": "y0", "label": "initial condition y₀", "start": -1.0, "stop": 6.0, "step": 0.1, "value": 0.5},
        ]
    )
    mo.md(
        f"""
        ## Interactive exploration

        Drag the sliders. The slope field redraws and the red solution curve — the
        one passing through $y(0) = y_0$ — bends to follow the new flow in real time.

        {mo.as_html(controls)}
        """
    )
    return (controls,)


@app.cell
def _(controls, delib, logistic_grid, np, plt):
    a = controls.value["a"]
    K = controls.value["K"]
    y0 = controls.value["y0"]

    f_grid = logistic_grid(a, K)

    fig_explore, ax_explore = plt.subplots(figsize=(7, 5))
    delib.slope_field(f_grid, xlim=(0, 10), ylim=(-1, 6), density=22, ax=ax_explore)

    # Equilibria flatten the field; show them for reference.
    ax_explore.axhline(K, color="#2a9d8f", lw=1.5, ls="--")
    ax_explore.axhline(0.0, color="#888", lw=1.0, ls=":")

    # Integrate the single solution through y0 and overlay it on the flow.
    sol = delib.solve_ode(lambda t, y: a * y * (1.0 - y / K), (0.0, 10.0), y0)
    delib.overlay_solution(ax_explore, sol.t, sol.y[0], label=f"y(0) = {y0:.1f}")
    ax_explore.set_title(f"a = {a:.1f},  K = {K:.1f},  y₀ = {y0:.1f}")
    fig_explore
    return K, a, f_grid, sol, y0


@app.cell
def _(K, a, delib, go, mo, np, y0):
    # --- Section 4: time animation -------------------------------------------
    # Trace the solution curve being drawn as t advances, with native play/pause.
    n_frames = 60
    t_request = np.linspace(0.0, 10.0, n_frames)
    sol_anim = delib.solve_ode(lambda t, y: a * y * (1.0 - y / K), (0.0, 10.0), y0, t_eval=t_request)
    # The solver stops early if the solution diverges, so use what it returned
    # rather than assuming all n_frames points exist.
    t_anim = sol_anim.t
    ys = sol_anim.y[0]
    n = len(t_anim)

    finite = ys[np.isfinite(ys)]
    lo = float(min(finite.min(), 0.0)) if finite.size else -1.0
    hi = float(max(finite.max(), K)) if finite.size else K + 1.0
    y_lo, y_hi = lo - 0.5, hi + 0.5

    def _equilibria():
        return [
            go.Scatter(x=[0, 10], y=[K, K], mode="lines",
                       line=dict(color="#2a9d8f", dash="dash"), name="K"),
            go.Scatter(x=[0, 10], y=[0, 0], mode="lines",
                       line=dict(color="#bbb", dash="dot"), name="y = 0"),
            go.Scatter(x=t_anim, y=ys, mode="lines",
                       line=dict(color="#f0c9cf"), name="full solution"),
        ]

    frames_data = [
        {
            "name": f"{t_anim[i]:.1f}",
            "data": _equilibria()
            + [
                go.Scatter(x=t_anim[: i + 1], y=ys[: i + 1], mode="lines",
                           line=dict(color="#d1495b", width=3), name="y(t)"),
                go.Scatter(x=[t_anim[i]], y=[ys[i]], mode="markers",
                           marker=dict(color="#d1495b", size=10), name="now"),
            ],
        }
        for i in range(n)
    ]

    anim_fig = delib.animate_plotly(
        frames_data,
        layout=dict(
            title="The solution being traced as t advances",
            xaxis=dict(title="t", range=[0, 10]),
            yaxis=dict(title="y", range=[y_lo, y_hi]),
            height=480,
            showlegend=False,
        ),
    )
    mo.md("## Time animation\n\nPress **▶ Play** to watch the solution follow the flow from $y_0$.")
    return (anim_fig,)


@app.cell
def _(anim_fig):
    anim_fig
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Try it

        1. Set $a < 0$. Which equilibrium becomes the **attractor** now, and which
           one repels nearby solutions?
        2. Start with $y_0$ *above* $K$. Does the population fall to $K$ or overshoot?
        3. Find a value of $K$ where a solution starting at $y_0 = 0.5$ barely moves
           over the whole window. What does that say about the slope near $y = 0$?
        4. Push $a$ toward $2$. How does the steepness of the climb to $K$ change?
        """
    )
    return


@app.cell
def _():
    CHAPTER_CONTEXT = r"""
    Chapter 1 — First-order ODEs & slope fields.

    Big idea: a first-order ODE y' = f(x, y) gives a *rule for the slope* at
    every point of the plane, not a single solution. Drawing a short arrow of
    slope f(x, y) on a grid produces the SLOPE FIELD — a picture of the flow
    that every solution must stay tangent to.

    Worked equation: the logistic model
        y' = a*y*(1 - y/K)
    with growth rate a and carrying capacity K. Its equilibria (where y' = 0)
    are y = 0 and y = K; there the field goes flat (horizontal stripes).
    Stability depends on the sign of a: for a > 0, y = K attracts and y = 0
    repels; for a < 0 the roles flip.

    What the learner sees on screen:
    - A slope field that redraws as they drag sliders for a, K, and the initial
      condition y0.
    - A red solution curve through y(0) = y0 bending to follow the flow.
    - A time animation tracing y(t) as t advances from 0 to 10.

    "Try it" exercises:
    1. Set a < 0: which equilibrium becomes the attractor, which repels?
    2. Start with y0 above K: does it fall to K or overshoot?
    3. Find a K where a solution from y0 = 0.5 barely moves — what does that say
       about the slope near y = 0?
    4. Push a toward 2: how does the steepness of the climb to K change?
    """
    return (CHAPTER_CONTEXT,)


@app.cell
def _(CHAPTER_CONTEXT, delib):
    tutor_panel = delib.tutor(
        CHAPTER_CONTEXT,
        section="Try it",
        starters=[
            "I set a < 0. I think y = 0 becomes the attractor — am I right?",
            "Why does the field go flat exactly at y = 0 and y = K?",
            "Give me a hint for question 2 without telling me the answer.",
            "How does the growth rate a change the shape of the solution curve?",
        ],
    )
    tutor_panel
    return (tutor_panel,)


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Recap & what's next

        A slope field turns an equation into a flow you can *see*; a solution curve is
        just a path that stays tangent to it everywhere.

        **Next:** *Separable & linear first-order* — instead of only reading the field,
        we'll solve these equations in closed form and check the formula against the
        very flow we drew here. *(No code from this chapter is required to start it.)*
        """
    )
    return


if __name__ == "__main__":
    app.run()
