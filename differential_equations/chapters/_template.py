import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go

    # The ONLY shared import. Never import another chapter.
    import delib
    return delib, go, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    # 1. Title + learning goals (3–5 bullets).
    mo.md(
        r"""
        # Chapter NN — <title>

        **<one-line hook>.**

        By the end of this chapter you should be able to:

        - <outcome 1>
        - <outcome 2>
        - <outcome 3>
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # 2. Concept: the math, kept brief, with one static illustrating plot below.
    mo.md(
        r"""
        ## Concept

        <the math, a few sentences and a key equation>

        $$ y' = f(x, y) $$
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, plt):
    # 2 (cont). A static illustration with fixed parameters.
    _ax = delib.slope_field(lambda x, y: -y, xlim=(0, 10), ylim=(-3, 3))
    _ax.set_title("static illustration")
    _ax.figure
    return


@app.cell(hide_code=True)
def _(delib, mo):
    # 3. Interactive exploration (the centerpiece): sliders bound to a field plot.
    controls = delib.param_panel(
        [
            {"name": "p", "label": "parameter p", "start": -2.0, "stop": 2.0, "step": 0.1, "value": 1.0},
        ]
    )
    mo.md(
        f"""
        ## Interactive exploration

        Drag the sliders; the plot below redraws live.

        {mo.as_html(controls)}
        """
    )
    return (controls,)


@app.cell(hide_code=True)
def _(controls, delib, plt):
    # 3 (cont). Read slider values and redraw. This cell re-runs on every change.
    p = controls.value["p"]

    fig_explore, ax_explore = plt.subplots(figsize=(7, 5))
    delib.slope_field(lambda x, y: p * y, xlim=(0, 10), ylim=(-3, 3), ax=ax_explore)
    sol = delib.solve_ode(lambda t, y: p * y, (0.0, 10.0), 1.0)
    delib.overlay_solution(ax_explore, sol.t, sol.y[0])
    fig_explore
    return


@app.cell(hide_code=True)
def _(delib, go, mo, np):
    # 4. Time animation: one playable animation over t (plotly play/pause inline).
    n_frames = 60
    t_anim = np.linspace(0.0, 10.0, n_frames)
    ys = np.exp(-t_anim)  # replace with this chapter's solution

    frames_data = [
        {
            "name": f"{t_anim[i]:.1f}",
            "data": [
                go.Scatter(x=t_anim[: i + 1], y=ys[: i + 1], mode="lines",
                           line=dict(color="#d1495b", width=3)),
            ],
        }
        for i in range(n_frames)
    ]
    anim_fig = delib.animate_plotly(
        frames_data,
        layout=dict(xaxis=dict(range=[0, 10]), yaxis=dict(range=[0, 1.1]), height=460),
    )
    mo.md("## Time animation\n\nPress **▶ Play**.")
    return (anim_fig,)


@app.cell(hide_code=True)
def _(anim_fig):
    anim_fig
    return


@app.cell(hide_code=True)
def _(mo):
    # 5. Try it: 2–4 open-ended nudges.
    mo.md(
        r"""
        ## Try it

        1. <prompt>
        2. <prompt>
        3. <prompt>
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # 6. Recap + what's next (text only, no code dependency on other chapters).
    mo.md(
        r"""
        ## Recap & what's next

        <one line recap>

        **Next:** *<next chapter title>* — <one line>.
        """
    )
    return


if __name__ == "__main__":
    app.run()
