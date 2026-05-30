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


@app.cell(hide_code=True)
def _(delib, go, mo, np):
    # Beat 1 — the real-world observation that motivates the whole chapter.
    _t = np.linspace(0, 14, 80)
    _sol = delib.solve_ode(lambda t, y: 0.9 * y * (1 - y / 1000.0), (0.0, 14.0), 3.0, t_eval=_t)
    _fig = go.Figure(go.Scatter(x=_sol.t, y=_sol.y[0], mode="lines",
                                line=dict(color="#2f6fb0", width=3),
                                hoverinfo="skip", showlegend=False))
    _fig.update_layout(
        template="plotly_white",
        title=dict(text="One rumor on a 1,000-person campus", x=0.02),
        xaxis=dict(title="day"), yaxis=dict(title="people who've heard it"),
        height=320, margin=dict(l=60, r=20, t=46, b=42),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    mo.vstack([
        mo.md(
            r"""
            ## A story about change

            Most of the math you've met so far describes where things *are* — a point,
            a length, a value. **Differential equations** capture something subtler and
            far more powerful: how things *change*. They rarely hand you the answer
            outright. Instead they hand you a **rule for the rate of change** at each
            instant, and let the whole story unfold from it. Populations, epidemics,
            cooling coffee, orbiting planets, the charge on your phone — all of them are
            stories told by differential equations.

            The quickest way to *feel* that is with a story. So here's one.

            Monday morning, **3 people** on a 1,000-person campus know a juicy rumor. By
            Friday, *everyone* does. If you plot how many have heard it each day, you
            don't get a straight line — you get this lazy **S**: a slow start, an
            explosive middle, and a gentle leveling-off.

            Why that exact shape? Because spreading takes **two** people: one who knows
            and one who doesn't. On Monday there are only a handful of tellers, so it
            creeps. By midweek there are plenty of tellers *and* plenty of fresh ears,
            so it erupts. By Friday almost everyone has heard it, so there's hardly
            anyone left to tell — and it flattens. All the drama lives in the middle.
            """
        ),
        _fig,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Bridge — name the concept the story just illustrated.
    mo.md(
        r"""
        ## What the story is really saying

        Notice we never wrote a formula for "how many know it on day 7." We described
        something more *local*: how fast the number is changing **right now**, in terms
        of how many already know. That is exactly what a **differential equation** is —
        a rule of the form

        $$ \frac{dy}{dt} = f(t, y), $$

        which reads *"tell me where you are, and I'll tell you how fast you're moving."*
        Think of $f$ as a little machine: feed it the current day $t$ and the current
        count $y$, and it hands back the **slope** — how fast $y$ is climbing at that
        instant. Plug in a *different* $(t, y)$ and you generally get a different slope.
        So the equation never states an answer outright; it states a **rule you can
        apply at any point**. Hand a solver that rule plus a starting value and it walks
        forward in tiny steps: read the slope here, nudge $y$ a little, read the new
        slope there, nudge again — and the whole curve grows out of the rule. The
        S-shape above is exactly what you get when you **follow the rate**, day by day.

        (You'll hear an equation like this called **first-order**. The name just means
        the rule needs only the present value $y$ — not its acceleration or any
        higher rate of change — to tell you the slope. Nothing more mysterious than
        that.)

        So the rest of this chapter is three moves: **(1)** turn the rumor story into
        such a rate-rule, **(2)** read what the rule tells us *before* solving it, and
        **(3)** watch the family of solutions it implies.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 2 — build the model from the story.
    mo.md(
        r"""
        ## Turning the story into an equation

        Let $y(t)$ be how many people have heard the rumor by day $t$, out of a campus
        of $K$ people. We don't know $y(t)$ yet — that's the whole point. But we *can*
        describe its **rate of change** straight from the mechanism of gossip.

        A fresh telling happens only when a **knower** runs into a **non-knower**. There
        are $y$ knowers and $K - y$ people who haven't heard yet, so the number of
        possible "telling" encounters — and therefore the rate at which new people learn
        the rumor — is proportional to their product:

        $$ \frac{dy}{dt} = b\,y\,(K - y). $$

        It reads more cleanly if we factor out the capacity and write the very same rule
        as

        $$ \frac{dy}{dt} = a\,y\left(1 - \frac{y}{K}\right), \qquad a = bK, $$

        the famous **logistic equation**. Hear it as two voices in tension. The factor
        $y$ is the **engine**: more knowers means more spreading, which is why a rumor
        with no one to start it never moves. The factor $(1 - y/K)$ is the **brake**: as
        $y$ climbs toward the whole campus $K$, the pool of fresh ears shrinks toward
        zero and the brake clamps down.

        Put numbers to the product $y(K - y)$ on a campus of $K = 1000$ to feel why the
        rate rises then falls:

        - **Early**, $y = 10$ know. Fresh ears are everywhere ($K - y = 990$), but there
          are only $10$ tellers, so $y(K-y)=10\times 990$ is small — the rumor *barely
          moves*.
        - **Late**, $y = 990$ know. Now tellers are everywhere, but only $10$ fresh
          ears remain, so $y(K-y)=990\times 10$ is small *again* — it barely moves.
        - **Middle**, $y = 500$. Both factors are large at once ($500\times 500$), the
          product peaks, and the rumor *erupts*.

        Small at both ends, biggest in the middle: that tug-of-war — engine winning
        early, brake winning late — is *exactly* the S-curve we observed.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3 — play with the symbols (live SymPy below).
    mo.md(
        r"""
        ## Play with the symbols

        Once we have the rule, the most revealing question is: where does the spread
        **stop**? Change stops exactly where the rate is zero, $dy/dt = 0$. A $y$-value
        where that happens is called an **equilibrium** — plug it back into the rule and
        the rate vanishes, so the count just sits there forever, unchanging. Equilibria
        exist because $f(y)$ *is* the rate of change: wherever $f$ passes through zero,
        the system is momentarily told to move at speed zero, and a population sitting
        exactly there has nowhere to go.

        For our rumor, setting $a\,y(1 - y/K) = 0$ gives two of them — $y = 0$ (nobody
        knows) and $y = K$ (everybody does) — and they behave oppositely. Near $y = 0$
        the smallest spark grows, so solutions are pushed *away*: that's an **unstable**
        equilibrium. Near $y = K$ any wobble gets pulled back, so solutions settle
        *onto* it: that's a **stable** one. The quick test is the slope of the rate
        itself, $f'(y)$ — negative means stable (pulls back), positive means unstable
        (pushes away).

        Don't take that on faith — **change the rate law below and watch the equilibria
        and their stability re-solve symbolically**, live. Try `a*y` (spreading with no
        ceiling), or stack a second brake with `a*y*(1 - y/K)*(2 - y/K)` and see a third
        equilibrium appear.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    eq_input = mo.ui.text(value="a*y*(1 - y/K)", full_width=True, label="dy/dt =")
    eq_input
    return (eq_input,)


@app.cell(hide_code=True)
def _(delib, eq_input):
    delib.equilibria_report(eq_input.value)
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 4 — bridge into the visuals.
    mo.md(
        r"""
        ## See the whole flow at once — the slope field

        Solving the equation from one starting point gives one curve. But notice what
        the rule really hands us: $dy/dt$ *is a slope*. So at any point $(t, y)$ you
        care to pick, plug it into $f(t, y)$ and out comes the slope a solution would
        have right there — and you can draw a tiny line segment at that point, tilted to
        match. Pick a neighboring point and the rule usually gives a slightly different
        slope, so a slightly different tilt. Do this at a whole **grid** of points and
        those little segments together form the **slope field**: a sky full of arrows,
        each one a local instruction for *"which way is the flow heading here."* It's a
        picture of *every* possible spread-story at once, drawn without solving a thing.

        Read it like a current in water: drop a cork anywhere and it drifts along the
        arrows. The equilibria you just found by hand reappear here as flat, horizontal
        lanes — $y = 0$ (nobody knows) and $y = K$ (everybody does) — where the arrows
        lie perfectly level because the rate is zero. Everywhere between them the arrows
        tilt upward, carrying solutions from the empty rumor toward the full campus.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    def logistic_grid(a, K):
        """y' = a*y*(1 - y/K), vectorized over a slope-field grid."""
        return lambda x, y: a * y * (1.0 - y / K)

    # A static illustration with fixed parameters, before we make it interactive.
    _fig = delib.vector_field_plotly(
        logistic_grid(1.0, 4.0), (0, 10), (-1, 6), density=18,
        title="Vector field of the logistic equation (a = 1, K = 4)",
    )
    _fig.add_hline(y=4.0, line=dict(color="#2a9d8f", dash="dash", width=1.5),
                   annotation_text="K = 4", annotation_position="top right")
    _fig.add_hline(y=0.0, line=dict(color="#9aa7b5", dash="dot", width=1),
                   annotation_text="y = 0", annotation_position="bottom right")
    _fig
    return (logistic_grid,)


@app.cell(hide_code=True)
def _(delib):
    controls = delib.param_panel(
        [
            {"name": "a", "label": "growth rate a", "start": -2.0, "stop": 2.0, "step": 0.1, "value": 1.0},
            {"name": "K", "label": "carrying capacity K", "start": 0.5, "stop": 5.0, "step": 0.1, "value": 4.0},
            {"name": "y0", "label": "initial condition y₀", "start": -1.0, "stop": 6.0, "step": 0.1, "value": 0.5},
        ]
    )
    return (controls,)


@app.cell(hide_code=True)
def _(controls, mo):
    # Render the controls directly (not via mo.as_html inside an f-string), so the
    # slider stays bound to downstream cells reading controls.value.
    mo.vstack([
        mo.md(
            r"""
            ## Now make it your campus

            The picture so far used one set of numbers — grab the sliders and make the
            rumor your own. Here $a$ is how **chatty** the campus is (how fast word
            travels), $K$ is how many people are even reachable, and $y_0$ is how many
            were in on it from day zero. As you drag them the field redraws, and the
            **red curve** — the single rumor that starts at $y(0) = y_0$ — bends to
            follow the new flow. Try pushing $a$ below zero, or starting $y_0$ *above*
            $K$, and watch where the story ends up.
            """
        ),
        controls,
    ])
    return


@app.cell(hide_code=True)
def _(controls, delib, go, logistic_grid):
    a = controls.value["a"]
    K = controls.value["K"]
    y0 = controls.value["y0"]

    f_grid = logistic_grid(a, K)

    fig_explore = delib.vector_field_plotly(
        f_grid, (0, 10), (-1, 6), density=18,
        title=f"a = {a:.1f},  K = {K:.1f},  y₀ = {y0:.1f}",
    )
    # Equilibria flatten the field; show them for reference.
    fig_explore.add_hline(y=K, line=dict(color="#2a9d8f", dash="dash", width=1.5))
    fig_explore.add_hline(y=0.0, line=dict(color="#9aa7b5", dash="dot", width=1))

    # Integrate the single solution through y0 and overlay it on the flow.
    sol = delib.solve_ode(lambda t, y: a * y * (1.0 - y / K), (0.0, 10.0), y0)
    fig_explore.add_trace(go.Scatter(
        x=sol.t, y=sol.y[0], mode="lines",
        line=dict(color="#d1495b", width=3), hoverinfo="skip", showlegend=False,
    ))
    fig_explore.add_trace(go.Scatter(
        x=[sol.t[0]], y=[sol.y[0][0]], mode="markers",
        marker=dict(color="#d1495b", size=9), hoverinfo="skip", showlegend=False,
    ))
    fig_explore
    return K, a, f_grid, sol, y0


@app.cell(hide_code=True)
def _(K, a, delib, go, mo):
    # The dynamical view: the field is fixed (static arrows); particles ride along
    # it. Reshape the field with the a / K sliders above and re-watch.
    _eq = [
        go.Scatter(x=[0, 10], y=[K, K], mode="lines",
                   line=dict(color="#2a9d8f", dash="dash", width=1.5),
                   hoverinfo="skip", showlegend=False),
        go.Scatter(x=[0, 10], y=[0, 0], mode="lines",
                   line=dict(color="#9aa7b5", dash="dot", width=1),
                   hoverinfo="skip", showlegend=False),
    ]
    anim_fig = delib.flow_field(
        lambda x, y: a * y * (1.0 - y / K), (0, 10), (-1, 6),
        extra_lines=_eq,
        title=f"Particles riding the field  (a = {a:.1f},  K = {K:.1f})",
    )
    mo.md(
        "## Many rumors at once\n\nEach dot is a *different* rumor — a different "
        "number of people in on it at the start — set loose on the same campus. Press "
        "**▶ Play** and watch them all ride the arrows: every story, wherever it "
        "begins, is carried toward $y = K$ (everyone knows) and away from $y = 0$. "
        "That *many-starts, one-destiny* convergence is the signature of a **stable "
        "equilibrium** — and you can read it straight off the field, without solving a "
        "single curve. Reshape the field with the **$a$ / $K$ sliders above** and play "
        "again."
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

        You've watched the rumor off the field by eye; now pin it down with code. Each
        task below is a small code ground — type and run your own answer, or ask the
        tutor (the ✨ box) to write or edit it for you — then **Run & check**. (From
        here on we'll lean on the math directly; the campus is yours to experiment on.)
        """
    )
    return


# --- Challenge 1: the stable equilibrium when a < 0 -----------------------------
@app.cell
def _(mo):
    c1_get, c1_set = mo.state(
        "a, K = -1.0, 4.0\n"
        "# With a < 0, which equilibrium do solutions move toward?\n"
        "# Assign that equilibrium's y-value to `answer`.\n"
        "answer = ...\n"
    )
    return c1_get, c1_set


@app.cell
def _(c1_get, delib):
    c1_ai, c1_gen, c1_code, c1_run = delib.exercise_inputs(c1_get())
    return c1_ai, c1_code, c1_gen, c1_run


@app.cell
async def _(api_field, c1_ai, c1_code, c1_gen, c1_set, delib, key_bridge):
    await delib.exercise_ai(
        c1_gen, c1_ai, c1_code, c1_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="Logistic y'=a*y*(1-y/K). Task: which equilibrium is stable when a<0; put its y-value in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(c1_ai, c1_code, c1_gen, c1_run, delib):
    delib.exercise_view(
        "**1.** With $a<0$, which equilibrium becomes the **attractor**? Assign its "
        "$y$-value to `answer`.",
        c1_ai, c1_gen, c1_code, c1_run,
    )
    return


@app.cell(hide_code=True)
def _(c1_code, c1_run, delib):
    delib.run_exercise(c1_code.value, c1_run.value, check=lambda ns: delib.check_number(
        ns, target=0.0,
        ok="Right — for $a<0$, $y=0$ is the attractor (and $y=K$ repels).",
        hint="With $a<0$ the flow points toward $y=0$.",
    ))
    return


# --- Challenge 2: a solution starting above K ----------------------------------
@app.cell
def _(mo):
    c2_get, c2_set = mo.state(
        "a, K, y0 = 1.0, 4.0, 6.0   # start ABOVE the carrying capacity\n"
        "# Integrate to t = 10 and store the final value y(10) in `answer`.\n"
        "answer = ...\n"
    )
    return c2_get, c2_set


@app.cell
def _(c2_get, delib):
    c2_ai, c2_gen, c2_code, c2_run = delib.exercise_inputs(c2_get())
    return c2_ai, c2_code, c2_gen, c2_run


@app.cell
async def _(api_field, c2_ai, c2_code, c2_gen, c2_set, delib, key_bridge):
    await delib.exercise_ai(
        c2_gen, c2_ai, c2_code, c2_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="Logistic y'=a*y*(1-y/K), a=1, K=4, y0=6 (above K). Task: integrate to t=10 and put y(10) in `answer` (use delib.solve_ode).",
    )
    return


@app.cell(hide_code=True)
def _(c2_ai, c2_code, c2_gen, c2_run, delib):
    delib.exercise_view(
        "**2.** Start **above** the capacity ($y_0=6$, $a=1$, $K=4$). Integrate to "
        "$t=10$ and put the final value $y(10)$ in `answer`. Does it settle back onto "
        "the equilibrium $K$, or stray away from it?",
        c2_ai, c2_gen, c2_code, c2_run,
    )
    return


@app.cell(hide_code=True)
def _(c2_code, c2_run, delib):
    delib.run_exercise(c2_code.value, c2_run.value, check=lambda ns: delib.check_number(
        ns, target=4.0, tol=0.1,
        ok="Right — it settles back down onto the equilibrium $K=4$ rather than straying away.",
        hint="Integrate $y'=a y(1-y/K)$ from $y_0=6$; it approaches $4$.",
    ))
    return


# --- Challenge 3: where the growth is steepest ---------------------------------
@app.cell
def _(mo):
    c3_get, c3_set = mo.state(
        "a, K = 1.0, 4.0\n"
        "# The growth rate y' = a*y*(1 - y/K) is largest at one value of y.\n"
        "# Find that y (the steepest point) and store it in `answer`.\n"
        "answer = ...\n"
    )
    return c3_get, c3_set


@app.cell
def _(c3_get, delib):
    c3_ai, c3_gen, c3_code, c3_run = delib.exercise_inputs(c3_get())
    return c3_ai, c3_code, c3_gen, c3_run


@app.cell
async def _(api_field, c3_ai, c3_code, c3_gen, c3_set, delib, key_bridge):
    await delib.exercise_ai(
        c3_gen, c3_ai, c3_code, c3_set,
        api_field.value or (key_bridge.value or {}).get("key", ""),
        context="Logistic y'=a*y*(1-y/K), a=1, K=4. Task: find the y that maximizes the growth rate y'; put it in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(c3_ai, c3_code, c3_gen, c3_run, delib):
    delib.exercise_view(
        "**3.** No matter where a rising rumor starts (any $0<y_0<4$, with $a=1$, "
        "$K=4$), it races through its **fastest growth** at the *same* value of $y$ "
        "every time. Find that $y$ where the rate $y'=a\\,y(1-y/K)$ peaks and put it in "
        "`answer`.",
        c3_ai, c3_gen, c3_code, c3_run,
    )
    return


@app.cell(hide_code=True)
def _(c3_code, c3_run, delib):
    delib.run_exercise(c3_code.value, c3_run.value, check=lambda ns: delib.check_number(
        ns, target=2.0, tol=0.05,
        ok="Yes — growth peaks at $y=K/2=2$, halfway to capacity.",
        hint="Maximize $a y(1-y/K)$ over $y$; the peak is at $y=K/2$.",
    ))
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
        "This is Chapter 1 of a differential-equations course: first-order ODEs and "
        "slope fields, worked through the logistic equation y' = a*y*(1 - y/K) with "
        "growth rate a and carrying capacity K (equilibria at y=0 and y=K).",
        prompts=[
            "explain this chapter in a paragraph",
            "show the solution when the growth rate a is negative",
            "plot the phase line of the logistic equation",
        ],
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge, picker):
    delib.tutor_sidebar(api_field, key_bridge, picker, chatbox)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## Playground — free exploration

        No task, no grading. Type any Python, or ask the tutor (✨) to write it, then
        **Run** to see the result. Build whatever you're curious about.
        """
    )
    return


@app.cell
def _(mo):
    pg_get, pg_set = mo.state(
        "view = delib.vector_field_plotly(lambda x, y: 1.0*y*(1 - y/4.0), (0, 10), (-1, 6))\n"
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
        context="Open sandbox for chapter 1 (first-order ODEs, logistic). Write complete, runnable code; assign a Plotly figure to `view`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, pg_ai, pg_code, pg_gen, pg_run):
    delib.exercise_view(None, pg_ai, pg_gen, pg_code, pg_run)
    return


@app.cell(hide_code=True)
def _(delib, pg_code, pg_run):
    # No check -> run_exercise just renders the view (open sandbox).
    delib.run_exercise(pg_code.value, pg_run.value)
    return


@app.cell(hide_code=True)
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
