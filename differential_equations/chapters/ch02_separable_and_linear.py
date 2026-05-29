import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go

    import delib
    return delib, go, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Chapter 2 — Separable & linear first-order equations

        **Now we solve, not just sketch.**

        By the end of this chapter you should be able to:

        - Spot a **separable** equation and solve it by integrating each side.
        - Spot a **linear** equation $y' + p(t)\,y = q(t)$ and solve it too.
        - Read **Newton's law of cooling** as a separable *and* linear ODE.
        - Find the **closed-form** solution and check it against the slope field.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, go, mo, np):
    # Beat 1 — the observation.
    _t = np.linspace(0, 30, 80)
    _sol = delib.solve_ode(lambda t, T: -0.2 * (T - 20.0), (0.0, 30.0), 90.0, t_eval=_t)
    _fig = go.Figure(go.Scatter(x=_sol.t, y=_sol.y[0], mode="lines",
                                line=dict(color="#b5651d", width=3),
                                hoverinfo="skip", showlegend=False))
    _fig.add_hline(y=20, line=dict(color="#9aa7b5", dash="dot", width=1),
                   annotation_text="room 20°C", annotation_position="bottom right")
    _fig.update_layout(
        template="plotly_white", title=dict(text="A cup of coffee cooling", x=0.02),
        xaxis=dict(title="minutes"), yaxis=dict(title="temperature (°C)"),
        height=320, margin=dict(l=60, r=20, t=46, b=42),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    mo.vstack([
        mo.md(
            r"""
            ## A story about change — round two

            In Chapter 1 we *read* an equation off a field but never solved it. This
            time we'll get an exact formula. Here's the story.

            Pour a coffee at **90°C** in a **20°C** room and it cools — fast at first,
            then ever more slowly, easing toward room temperature but (in principle)
            never quite arriving. The curve is a **decaying exponential**, the mirror
            image of Chapter 1's S-curve.

            Why this shape? Because the coffee cools in proportion to how far it is
            *above* the room. A scalding cup dumps heat quickly; a lukewarm one barely
            cools at all. The bigger the gap, the faster it shrinks — and a quantity
            whose rate of decrease is proportional to itself decays exponentially.
            """
        ),
        _fig,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 2 — the concept these equations belong to.
    mo.md(
        r"""
        ## Two families we can actually solve

        Most differential equations have **no** tidy formula. But two families do, and
        the cooling coffee is in both.

        - **Separable:** $\dfrac{dy}{dt} = g(t)\,h(y)$. Everything-$y$ can be moved to
          one side and everything-$t$ to the other, then you integrate each side on its
          own: $\displaystyle\int \frac{dy}{h(y)} = \int g(t)\,dt.$
        - **Linear:** $\dfrac{dy}{dt} + p(t)\,y = q(t)$ — $y$ and $y'$ appear only to the
          first power, never multiplied together. These always have a closed-form
          solution.

        Telling which family an equation belongs to is half the battle: it tells you
        *which solving recipe* to reach for.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3a — build the model.
    mo.md(
        r"""
        ## Newton's law of cooling

        Let $T(t)$ be the coffee's temperature and $T_r$ the room's. "Cools in
        proportion to the gap above the room" is, word for word,

        $$ \frac{dT}{dt} = -k\,(T - T_r), \qquad k > 0. $$

        The minus sign makes it *cool* (the rate is negative while $T > T_r$); the
        constant $k$ is how fast. This is **separable** — group the $T$'s and the
        $t$'s — and also **linear**: rewrite it as $T' + kT = kT_r$. One equation, both
        recipes apply.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3b — watch the separable method unfold (Manim clip, rendered offline).
    mo.md(
        r"""
        ## Solve it — watch the method

        `dsolve` would spit out the answer in one line, but that hides *how*. Because
        the equation is **separable**, we can watch the algebra move: $(T - T_r)$ flies
        into the denominator, the integral signs appear and evaluate, and finally $T$ is
        isolated. The highlighted symbols are the ones being manipulated at each step.
        Press **▶** to play.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    delib.video(
        "newton_cooling.mp4",
        caption="Separation of variables, term by term",
        fallback="The animated derivation is being rendered (see manim/newton_cooling.py).",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 4 — bridge into the field.
    mo.md(
        r"""
        ## Check the formula against the field

        A formula is only convincing if it matches the flow. The slope field of
        $dT/dt = -k(T - T_r)$ assigns a slope to every point $(t, T)$: above the room
        the arrows point **down** (cooling), below it they point **up** (warming), and
        right at $T = T_r$ they go flat — the lone equilibrium. The exact solution
        should thread straight through that flow.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    _fig = delib.vector_field_plotly(
        lambda x, y: -0.2 * (y - 20.0), (0, 30), (10, 95), density=18,
        title="Cooling field  (k = 0.2, room = 20°C)",
    )
    _fig.add_hline(y=20, line=dict(color="#2a9d8f", dash="dash", width=1.5),
                   annotation_text="room 20°C", annotation_position="top right")
    _fig
    return


@app.cell(hide_code=True)
def _(delib, mo):
    controls = delib.param_panel(
        [
            {"name": "k", "label": "cooling rate k", "start": 0.05, "stop": 0.6, "step": 0.05, "value": 0.2},
            {"name": "Tr", "label": "room temperature Tr", "start": 0.0, "stop": 40.0, "step": 1.0, "value": 20.0},
            {"name": "T0", "label": "starting temp T₀", "start": 40.0, "stop": 100.0, "step": 1.0, "value": 90.0},
        ]
    )
    mo.md(
        f"""
        ## Make it your kitchen

        Drag the sliders: $k$ is how fast it cools, $T_r$ is the room, and $T_0$ is how
        hot it started. The field redraws and the **red curve** — the exact solution
        from $T(0) = T_0$ — bends to follow it. Notice every curve, hot or cold, slides
        onto the room-temperature line.

        {mo.as_html(controls)}
        """
    )
    return (controls,)


@app.cell(hide_code=True)
def _(controls, delib, go):
    k = controls.value["k"]
    Tr = controls.value["Tr"]
    T0 = controls.value["T0"]

    fig = delib.vector_field_plotly(
        lambda x, y: -k * (y - Tr), (0, 30), (10, 100), density=18,
        title=f"k = {k:.2f},  room = {Tr:.0f}°C,  start = {T0:.0f}°C",
    )
    fig.add_hline(y=Tr, line=dict(color="#2a9d8f", dash="dash", width=1.5))
    sol = delib.solve_ode(lambda t, T: -k * (T - Tr), (0.0, 30.0), T0)
    fig.add_trace(go.Scatter(x=sol.t, y=sol.y[0], mode="lines",
                             line=dict(color="#d1495b", width=3),
                             hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=[sol.t[0]], y=[sol.y[0][0]], mode="markers",
                             marker=dict(color="#d1495b", size=9),
                             hoverinfo="skip", showlegend=False))
    fig
    return Tr, k


@app.cell(hide_code=True)
def _(Tr, delib, go, k, mo):
    _eq = [go.Scatter(x=[0, 30], y=[Tr, Tr], mode="lines",
                      line=dict(color="#2a9d8f", dash="dash", width=1.5),
                      hoverinfo="skip", showlegend=False)]
    anim_fig = delib.flow_field(
        lambda x, y: -k * (y - Tr), (0, 30), (10, 100),
        extra_lines=_eq, title=f"Many cups, one destiny: {Tr:.0f}°C",
    )
    mo.md(
        "## Many cups at once\n\nEach dot is a cup that started at a different "
        "temperature, set cooling in the same room. Press **▶ Play**: hot ones fall, "
        "cold ones rise, and *all* of them settle onto $T = T_r$. That single shared "
        "destination is the **stable equilibrium** — and the exact formula "
        "$T(t) = T_r + (T_0 - T_r)e^{-kt}$ says the same thing, since $e^{-kt} \\to 0$."
    )
    return (anim_fig,)


@app.cell(hide_code=True)
def _(anim_fig):
    anim_fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it — in code

        You've seen the field and the formula; now compute with them. Type and run your
        own answer, or ask the tutor (the ✨ box) to write or edit it — then **Run &
        check**.
        """
    )
    return


# --- Challenge 1: temperature after 10 minutes ---------------------------------
@app.cell
def _(mo):
    d1_get, d1_set = mo.state(
        "k, Tr, T0 = 0.2, 20.0, 90.0\n"
        "# Cooling: dT/dt = -k*(T - Tr).\n"
        "# What is the coffee's temperature after 10 minutes? Put it in `answer`.\n"
        "answer = ...\n"
    )
    return d1_get, d1_set


@app.cell
def _(d1_get, delib):
    d1_ai, d1_gen, d1_code, d1_run = delib.exercise_inputs(d1_get())
    return d1_ai, d1_code, d1_gen, d1_run


@app.cell
async def _(api_field, d1_ai, d1_code, d1_gen, d1_set, delib, key_bridge):
    await delib.exercise_ai(
        d1_gen, d1_ai, d1_code, d1_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="Newton cooling dT/dt=-k(T-Tr), k=0.2, Tr=20, T0=90. Task: temperature at t=10 min in `answer` (delib.solve_ode, or T(t)=Tr+(T0-Tr)*exp(-k*t)).",
    )
    return


@app.cell(hide_code=True)
def _(d1_ai, d1_code, d1_gen, d1_run, delib):
    delib.exercise_view(
        "**1.** With $k=0.2$, room $20°C$, starting $90°C$ — what is the coffee's "
        "temperature after **10 minutes**? Put it in `answer`.",
        d1_ai, d1_gen, d1_code, d1_run,
    )
    return


@app.cell(hide_code=True)
def _(d1_code, d1_run, delib):
    delib.run_exercise(d1_code.value, d1_run.value, check=lambda ns: delib.check_number(
        ns, target=29.47, tol=0.5,
        ok="Right — about $29.5°C$; it's cooled most of the way already.",
        hint="Use $T(t)=T_r+(T_0-T_r)e^{-kt}$, or integrate with delib.solve_ode to $t=10$.",
    ))
    return


# --- Challenge 2: the long-run temperature -------------------------------------
@app.cell
def _(mo):
    d2_get, d2_set = mo.state(
        "Tr = 20.0\n"
        "# As t -> infinity, what temperature does the coffee approach?\n"
        "answer = ...\n"
    )
    return d2_get, d2_set


@app.cell
def _(d2_get, delib):
    d2_ai, d2_gen, d2_code, d2_run = delib.exercise_inputs(d2_get())
    return d2_ai, d2_code, d2_gen, d2_run


@app.cell
async def _(api_field, d2_ai, d2_code, d2_gen, d2_set, delib, key_bridge):
    await delib.exercise_ai(
        d2_gen, d2_ai, d2_code, d2_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="Newton cooling dT/dt=-k(T-Tr). Task: the long-run (equilibrium) temperature in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(d2_ai, d2_code, d2_gen, d2_run, delib):
    delib.exercise_view(
        "**2.** Let it sit forever. What temperature does the coffee approach? Put the "
        "number in `answer`.",
        d2_ai, d2_gen, d2_code, d2_run,
    )
    return


@app.cell(hide_code=True)
def _(d2_code, d2_run, delib):
    delib.run_exercise(d2_code.value, d2_run.value, check=lambda ns: delib.check_number(
        ns, target=20.0,
        ok="Right — it approaches the room temperature $T_r = 20°C$ (the equilibrium).",
        hint="Set $dT/dt = 0$: the only steady temperature is $T = T_r$.",
    ))
    return


# --- Playground ----------------------------------------------------------------
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## Playground — free exploration

        No task, no grading. Type any Python, or ask the tutor (✨) to write it, then
        **Run** to see the result.
        """
    )
    return


@app.cell
def _(mo):
    pg_get, pg_set = mo.state(
        "view = delib.vector_field_plotly(lambda x, y: -0.2*(y - 20.0), (0, 30), (10, 100))\n"
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
        context="Open sandbox for chapter 2 (Newton cooling, separable/linear). Write complete, runnable code; assign a Plotly figure to `view`.",
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

        A separable or linear first-order equation hands you a real formula — and it
        threads exactly through the slope field, with every solution sliding onto the
        equilibrium $T = T_r$.

        **Next:** *Fixed points & stability* — we'll stop tracking one curve and ask
        which equilibria **attract** and which **repel**, reading stability straight off
        the rate.
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
        "This is Chapter 2 of a differential-equations course: separable & linear "
        "first-order equations, worked through Newton's law of cooling "
        "dT/dt = -k(T - Tr) (room temperature Tr, cooling rate k), with closed-form "
        "solution T(t) = Tr + (T0 - Tr) e^(-k t).",
        prompts=[
            "explain separable vs linear",
            "solve the cooling equation by hand",
            "plot a few cooling curves",
        ],
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge, picker):
    delib.tutor_sidebar(api_field, key_bridge, picker, chatbox)
    return


if __name__ == "__main__":
    app.run()
