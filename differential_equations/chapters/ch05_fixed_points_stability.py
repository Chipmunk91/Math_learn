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
        # Chapter 3 — Fixed points & stability (the phase line)

        **Where does motion stop, and does the stop hold?**

        By the end of this chapter you should be able to:

        - Find the **fixed points** of $\dot x = f(x)$ and classify each as
          **stable** or **unstable** from the sign of $f'(x^*)$.
        - Read a **phase line** as a picture of the flow on a 1-D state space.
        - See the same dynamics as a **potential landscape** $V(x)$ with
          $f = -V'$: stable = valley, unstable = hill.
        - Identify the **basin of attraction** of each stable fixed point.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, go, mo, np):
    # Beat 1 — hook: a wall light switch. Several "marbles" released from
    # different starts sort themselves into one of two destinations.
    _starts = [-1.6, -0.8, -0.1, 0.1, 0.8, 1.6]
    _t = np.linspace(0, 6, 120)
    _fig = go.Figure()
    for _x0 in _starts:
        _sol = delib.solve_ode(lambda t, x: x - x**3, (0.0, 6.0), _x0, t_eval=_t)
        _fig.add_trace(go.Scatter(
            x=_sol.t, y=_sol.y[0], mode="lines",
            line=dict(color="#2f6fb0" if _x0 > 0 else "#b5651d", width=2),
            hoverinfo="skip", showlegend=False,
        ))
    _fig.add_hline(y=1, line=dict(color="#2a9d8f", dash="dash", width=1.5),
                   annotation_text="up", annotation_position="top right")
    _fig.add_hline(y=-1, line=dict(color="#2a9d8f", dash="dash", width=1.5),
                   annotation_text="down", annotation_position="bottom right")
    _fig.add_hline(y=0, line=dict(color="#d1495b", dash="dot", width=1),
                   annotation_text="hill (no rest here)", annotation_position="top right")
    _fig.update_layout(
        template="plotly_white",
        title=dict(text="Six marbles, two destinations", x=0.02),
        xaxis=dict(title="time"), yaxis=dict(title="x(t)"),
        height=340, margin=dict(l=60, r=20, t=46, b=42),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    mo.vstack([
        mo.md(
            r"""
            ## A story about two stable rest-states

            *(placeholder — wall light switch story, bistability hook)*

            Six marbles, six different starting positions. By the end every one is
            stuck at either $x = +1$ or $x = -1$. None of them ever settles on
            $x = 0$ — that middle option is on the menu of "places where motion
            stops," but as you can see, it doesn't *hold*.
            """
        ),
        _fig,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 2 — concept bridge.
    mo.md(
        r"""
        ## Where the motion stops — and whether it sticks

        *(placeholder — concept bridge: define "fixed point" as where dx/dt = 0,
        and "stable / unstable" by whether a small nudge is undone.)*

        The hook above asked two separate questions, and a 1-D differential
        equation $\dot x = f(x)$ answers both in one shot. *Where does motion
        stop?* Wherever $f(x) = 0$. *Does the stop hold?* That depends on what
        the flow does **just next to** the resting point.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3 — build the model: why x' = x - x^3.
    mo.md(
        r"""
        ## Building the switch equation

        *(placeholder — derive dot x = x - x^3 from "two attractive states with
        an unstable middle"; the simplest cubic with that shape.)*

        The cubic $\dot x = x - x^3$ has exactly three zeros — $x = -1, 0, +1$
        — and a simple shape: positive between $-1$ and $0$, negative between
        $0$ and $+1$, swapping sign at every zero. That's the right structure.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Beat 4 — the phase line (FIRST hero visual).
    delib.phase_line(lambda x: x - x**3, (-2.0, 2.0),
                     title="Phase line of  x' = x - x^3")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        *(placeholder — how to read the phase line: each circle is a fixed
        point; filled = stable, open = unstable; the arrows show the flow on
        each interval.)*
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 5 — the stability test from f'.
    mo.md(
        r"""
        ## Stability, formally — read it off $f'(x^*)$

        *(placeholder — at a fixed point x*, linearise: small perturbations grow
        like e^{f'(x*) t}. f' negative -> decay (stable); f' positive -> grow
        (unstable). f' = 0 is the borderline case.)*

        Edit the rate law below and watch the equilibria and their stability
        re-solve symbolically, live.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    eq_input = mo.ui.text(value="x - x**3", full_width=True, label="dx/dt =")
    eq_input
    return (eq_input,)


@app.cell(hide_code=True)
def _(delib, eq_input):
    delib.equilibria_report(eq_input.value, var="x")
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 6 — the potential landscape (SECOND hero visual).
    mo.md(
        r"""
        ## Same picture, two ways — the potential well

        *(placeholder — introduce V with f = -V'. Stable iff sitting in a
        valley; unstable iff balanced on a hill. The barrier height between
        valleys is the energy to flip the switch.)*

        Define $V(x) = -\int_{x_0}^{x} f(s)\,ds$, so $f = -V'$. The dynamics
        $\dot x = f(x) = -V'(x)$ is the rule a marble would follow rolling
        downhill on the landscape $V$. **Valleys** are stable rest-states;
        **hills** are unstable ones.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    delib.potential_plot(lambda x: x - x**3, (-2.0, 2.0),
                         title="Potential V(x) for x' = x - x^3")
    return


@app.cell(hide_code=True)
def _(delib, mo):
    # Beat 7 — drop-the-marble slider.
    controls = delib.param_panel(
        [{"name": "x0", "label": "starting position x₀",
          "start": -1.8, "stop": 1.8, "step": 0.05, "value": 0.5}]
    )
    return (controls,)


@app.cell(hide_code=True)
def _(controls, mo):
    mo.vstack([
        mo.md(
            r"""
            ## Make it your switch — drop the marble

            *(placeholder — drag $x_0$; the phase line shows where it starts,
            the potential well shows the same point on the landscape, and a
            short time-trace below shows which valley it falls into.)*
            """
        ),
        controls,
    ])
    return


@app.cell(hide_code=True)
def _(controls, delib, mo):
    x0 = controls.value["x0"]
    pl = delib.phase_line(lambda x: x - x**3, (-2.0, 2.0),
                          marker_x=x0, title=f"Phase line — marble at x₀ = {x0:.2f}")
    pv = delib.potential_plot(lambda x: x - x**3, (-2.0, 2.0),
                              marker_x=x0, title=f"Potential — marble at x₀ = {x0:.2f}")
    mo.vstack([pl, pv])
    return (x0,)


@app.cell(hide_code=True)
def _(delib, go, np, x0):
    # The marble's actual trajectory in time, for the chosen x0.
    _t = np.linspace(0, 10, 200)
    _sol = delib.solve_ode(lambda t, x: x - x**3, (0.0, 10.0), x0, t_eval=_t)
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(x=_sol.t, y=_sol.y[0], mode="lines",
                              line=dict(color="#d1495b", width=3),
                              hoverinfo="skip", showlegend=False))
    _fig.add_hline(y=1, line=dict(color="#2a9d8f", dash="dash", width=1))
    _fig.add_hline(y=-1, line=dict(color="#2a9d8f", dash="dash", width=1))
    _fig.add_hline(y=0, line=dict(color="#d1495b", dash="dot", width=1))
    _fig.update_layout(
        template="plotly_white",
        title=dict(text=f"x(t) from x₀ = {x0:.2f}", x=0.02),
        xaxis=dict(title="t"), yaxis=dict(title="x(t)", range=[-2, 2]),
        height=280, margin=dict(l=55, r=20, t=46, b=42),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it — in code

        *(placeholder — short intro to the 3 challenges.)*
        """
    )
    return


# --- Challenge 1: classify the equilibria of a DIFFERENT cubic -----------------
@app.cell
def _(mo):
    e1_get, e1_set = mo.state(
        "# For dot x = 4*x - x**3, find the STABLE fixed point with the LARGEST\n"
        "# value of x. Assign that x to `answer`.\n"
        "# Hint: fixed points satisfy f(x) = 0; stable means f'(x*) < 0.\n"
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
        context="dot x = 4 x - x^3. Fixed points: 0, +/-2. f'(x) = 4 - 3 x^2. f'(0)=+4 (unstable); f'(+/-2)=-8 (stable). The largest stable x is +2. Put 2 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_ai, e1_code, e1_gen, e1_run):
    delib.exercise_view(
        "**1.** For $\\dot x = 4x - x^3$, find the **stable** fixed point with "
        "the **largest** value of $x$. Put it in `answer`.",
        e1_ai, e1_gen, e1_code, e1_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_code, e1_run):
    delib.run_exercise(e1_code.value, e1_run.value, check=lambda ns: delib.check_number(
        ns, target=2.0, tol=0.05,
        ok="Right — $x = +2$ is stable ($f'(\\pm 2) = -8 < 0$); $x = 0$ is unstable.",
        hint="Solve $4x - x^3 = 0$ for the three fixed points $\\{0, \\pm 2\\}$, then keep those with $f'(x^*)<0$.",
    ))
    return


# --- Challenge 2: which valley does the marble fall into? ---------------------
@app.cell
def _(mo):
    e2_get, e2_set = mo.state(
        "# For dot x = x - x**3 starting at x0 = 0.01,\n"
        "# integrate to t = 30 and put the final x in `answer`.\n"
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
        context="dot x = x - x^3, x0 = 0.01 (just above the unstable middle). Integrate to t=30 with delib.solve_ode; the final x is +1 (it falls into the right valley). Put 1.0 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_ai, e2_code, e2_gen, e2_run):
    delib.exercise_view(
        "**2.** For $\\dot x = x - x^3$ starting at $x_0 = 0.01$, where does the "
        "marble end up? Integrate to $t = 30$ and put $x(30)$ in `answer`.",
        e2_ai, e2_gen, e2_code, e2_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_code, e2_run):
    delib.run_exercise(e2_code.value, e2_run.value, check=lambda ns: delib.check_number(
        ns, target=1.0, tol=0.05,
        ok="Right — $x_0 = 0.01$ is on the right side of the unstable middle, so it falls into the $x = +1$ valley.",
        hint="The unstable fixed point at $x=0$ splits the basins. Anything $x_0 > 0$ goes to $+1$.",
    ))
    return


# --- Challenge 3: barrier height ------------------------------------------------
@app.cell
def _(mo):
    e3_get, e3_set = mo.state(
        "# For dot x = x - x**3, the potential is V(x) = -x**2/2 + x**4/4\n"
        "# (since f = -V'). Compute the BARRIER HEIGHT between the two\n"
        "# valleys: V(0) - V(-1). Put it in `answer`.\n"
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
        context="V(x) = -x^2/2 + x^4/4. V(0) = 0, V(-1) = -1/2 + 1/4 = -1/4. Barrier = V(0) - V(-1) = 0 - (-0.25) = 0.25. Put 0.25 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_ai, e3_code, e3_gen, e3_run):
    delib.exercise_view(
        "**3.** The potential for $\\dot x = x - x^3$ is "
        "$V(x) = -\\dfrac{x^2}{2} + \\dfrac{x^4}{4}$. Compute the **barrier "
        "height** $V(0) - V(-1)$ — the energy needed to flip from the left "
        "valley over the hill. Put it in `answer`.",
        e3_ai, e3_gen, e3_code, e3_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_code, e3_run):
    delib.run_exercise(e3_code.value, e3_run.value, check=lambda ns: delib.check_number(
        ns, target=0.25, tol=1e-4,
        ok="Right — the barrier is $\\tfrac{1}{4}$. That's how much energy keeps the switch from flipping on its own.",
        hint="Compute $V(0)$ and $V(-1)$ from $V(x) = -x^2/2 + x^4/4$ and subtract.",
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
        "view = delib.phase_line(lambda x: x - x**3, (-2.0, 2.0),\n"
        "                        title='Try editing this rate law!')\n"
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
        context="Open sandbox for chapter 3 (1-D phase line, potential, fixed points). "
                "Helpers available: delib.phase_line(f, xrange), delib.potential_plot(f, xrange), "
                "delib.equilibria_report(expr, var='x'). Write complete runnable code; assign a Plotly figure to `view`.",
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

        *(placeholder — recap fixed points / stability test / potential view /
        basin of attraction. Next: Ch 06 bifurcations — what happens if we
        morph the equation's parameters and a fixed point appears or vanishes?)*
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
        "This is Chapter 3 of a differential-equations course: 1-D fixed points "
        "and stability, worked through the bistable equation x' = x - x^3 (the "
        "wall-light-switch story). Key visuals: phase line (filled = stable, "
        "open = unstable, arrows = flow direction) and potential V(x) with "
        "f = -V'. Stability test: f'(x*) < 0 means stable.",
        prompts=[
            "explain this chapter in a paragraph",
            "show another bistable system and its phase line",
            "plot the potential for x' = sin(x)",
        ],
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge):
    delib.tutor_sidebar(api_field, key_bridge, chatbox)
    return


if __name__ == "__main__":
    app.run()
