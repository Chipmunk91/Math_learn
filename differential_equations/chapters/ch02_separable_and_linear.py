import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import plotly.graph_objects as go

    import delib
    return delib, go, mo, np


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
def _(delib, mo):
    # Beat 1 — the observation, opened by the live cooling-coffee hook
    # (delib.cooling_coffee, shared with the animation Lab): drag the room,
    # toggle the candle, pour milk — the curve is the exact ODE.
    mo.vstack([
        mo.md(
            r"""
            ## Cooling coffee

            Pour a coffee at **90°C** in a **20°C** room and watch it cool below —
            fast at first, then ever more slowly, easing toward room temperature but
            (in principle) never quite arriving. The curve is a **decaying
            exponential**, the mirror image of Chapter 1's S-curve. *(Drag* room T_r
            *to change the room; tap* candle warmer *to add a heater; tap* pour milk
            *for a sudden mix — the same equation handles every move.)*

            Why this shape? Because the coffee cools in proportion to how far it is
            *above* the room. A scalding cup dumps heat quickly; a lukewarm one barely
            cools at all. The bigger the gap, the faster it shrinks — and a quantity
            whose rate of decrease is proportional to itself decays exponentially.
            """
        ),
        delib.cooling_coffee(T0=90.0, Tr=20.0, k=0.20),
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
    # Quick self-check: classify each equation. An equation can be BOTH.
    _opts = ["Separable only", "Linear only", "Both", "Neither"]
    family_quiz = mo.ui.dictionary(
        {k: mo.ui.dropdown(_opts, label="your answer") for k in ("a", "b", "c", "d")}
    )
    return (family_quiz,)


@app.cell(hide_code=True)
def _(family_quiz, mo):
    _key = {"a": "Separable only", "b": "Linear only", "c": "Both", "d": "Neither"}

    def _mark(k):
        v = family_quiz[k].value
        if not v:
            return ""
        return " &nbsp;✅" if v == _key[k] else " &nbsp;❌"

    mo.md(
        f"""
        ### Quick check — which family?

        Decide whether each equation is **separable**, **linear**, **both**, or
        **neither**. (Separable means it factors as $g(t)\\,h(y)$; linear means $y$ and
        $y'$ appear only to the first power, never multiplied together.)

        **(a)** $\\dfrac{{dy}}{{dt}} = y\\,(1 - y)$ &nbsp; {mo.as_html(family_quiz['a'])}{_mark('a')}

        **(b)** $\\dfrac{{dy}}{{dt}} + 2y = \\sin t$ &nbsp; {mo.as_html(family_quiz['b'])}{_mark('b')}

        **(c)** $\\dfrac{{dy}}{{dt}} = t\\,y$ &nbsp; {mo.as_html(family_quiz['c'])}{_mark('c')}

        **(d)** $\\dfrac{{dy}}{{dt}} = y^2 + t$ &nbsp; {mo.as_html(family_quiz['d'])}{_mark('d')}
        """
    )
    return


@app.cell(hide_code=True)
def _(family_quiz, mo):
    _key = {"a": "Separable only", "b": "Linear only", "c": "Both", "d": "Neither"}
    _why = {
        "a": "separable ($g(t)=1$, $h(y)=y(1-y)$), but the $y^2$ hidden in $y(1-y)$ makes it **nonlinear**.",
        "b": "**linear** ($y$ and $y'$ are first-power), but not separable — $\\sin t - 2y$ won't split into (only-$t$)$\\times$(only-$y$).",
        "c": "**both**: $\\dfrac{dy}{y} = t\\,dt$ separates, and $y' - t\\,y = 0$ is linear.",
        "d": "**neither**: the $y^2$ rules out linear, and $y^2 + t$ won't factor for separable.",
    }
    # Underscore-prefixed loop variables stay cell-private; without the underscore,
    # the for-loop leaks `k` as a marimo global, colliding with the chart cell's
    # `k = controls.value["k"]` and silently breaking the slider chain.
    _answered = [_k for _k in _key if family_quiz[_k].value]
    if not _answered:
        _out = mo.md("*Pick a family for each equation to check your answers.*")
    else:
        _rows = []
        for _k in ("a", "b", "c", "d"):
            _v = family_quiz[_k].value
            if not _v:
                continue
            _ok = _v == _key[_k]
            _verdict = "Correct" if _ok else "Not quite"
            _rows.append(f"{'✅' if _ok else '❌'} **({_k})** {_verdict} — it's {_why[_k]}")
        _out = mo.md("\n\n".join(_rows))
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3a — build the model.
    mo.md(
        r"""
        ## Building the cooling equation

        We don't need to already *know* a law for this — we can build the equation
        from the one observation we just made: **a cup cools in proportion to how far
        its temperature sits above the room.** Let's turn that sentence into symbols,
        piece by piece.

        - Call the coffee's temperature $T(t)$ and the room's $T_r$ (a constant). The
          **gap** above the room is $T - T_r$.
        - "Cools in proportion to the gap" means the rate $\dfrac{dT}{dt}$ is
          *proportional to* that gap:
          $\dfrac{dT}{dt} = (\text{constant})\times(T - T_r)$.
        - While the coffee is hotter than the room ($T > T_r$) the gap is positive, yet
          $T$ must *fall* — so $dT/dt$ has to be negative there. That forces the
          constant to be negative; we write it as $-k$ with $k > 0$:

        $$ \frac{dT}{dt} = -k\,(T - T_r), \qquad k > 0. $$

        That equation has a name — **Newton's law of cooling** — and the constant $k$
        sets *how fast* (a thin paper cup has a larger $k$ than an insulated mug). Notice
        it is **separable** — we can group the $T$'s and the $t$'s — and also
        **linear**: rearranged, it's $T' + kT = kT_r$. One equation, both recipes apply.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3b — watch the separable method unfold (Manim clip, rendered offline).
    mo.md(
        r"""
        ## Solve it — watch the method

        A computer could spit out the answer in one line, but that hides *how* it's
        found. Because the equation is **separable**, we can watch the algebra move
        instead: $(T - T_r)$ slides into a denominator, integral signs appear on both
        sides and evaluate, and finally $T$ is isolated. The highlighted symbols are the
        ones being manipulated at each step. Press **▶** to play.
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
    # Beat 3c — read the closed form: what is the formula actually telling us?
    mo.md(
        r"""
        ### What the formula is telling us

        Out of all that algebra came

        $$ T(t) \;=\; T_r \;+\; A\,e^{-k t}, $$

        and once the starting temperature $T(0) = T_0$ pins $A = T_0 - T_r$,

        $$ T(t) \;=\; T_r \;+\; (T_0 - T_r)\,e^{-k t}. $$

        Read it slowly. The $T_r$ out front is the **room** — the temperature the cup is
        heading toward. The piece $(T_0 - T_r)$ is the **initial gap** above (or below)
        the room. The factor $e^{-k t}$ is a **decay knob** that starts at $1$ when
        $t = 0$ and shrinks toward $0$ as time grows. So the formula is just one sentence
        in symbols:

        > the cup's temperature equals the room plus a leftover gap that **shrinks
        > exponentially** — closing in on $T_r$ fast at first, then ever more slowly,
        > but never quite reaching it.

        Two reads pop out immediately. **(1)** As $t \to \infty$, $e^{-kt} \to 0$, so
        $T \to T_r$ regardless of how hot or cold it started — every cup forgets its
        past. **(2)** Doubling $k$ halves the time to close any given fraction of the
        gap, which is what "$k$ is how fast" really means.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3e (intro) — frame the linear-method route as the second recipe
    # the chapter promised. Symbolic derivation moves into the Manim cell
    # immediately after, so the prose stays brief.
    mo.md(
        r"""
        ### A second way to the same answer — the linear method

        The recipe we just watched — *separate, then integrate* — worked
        because the cooling equation lets us shove all the $T$s to one
        side and all the $t$s to the other once we divide. Not every
        linear-looking equation cooperates that way; many don't. So
        there's a second recipe, specifically for **linear** first-order
        equations

        $$
        y' + p(t)\,y \;=\; q(t),
        $$

        that handles cases the separable method can't touch. The cooling
        equation happens to be in this shape too — rearrange
        $dT/dt = -k(T - T_r)$ as $T' + kT = kT_r$, and you have
        $p(t) = k$, $q(t) = kT_r$. So we can run the linear recipe on it
        and watch the same closed form fall out by a different door.

        **The idea, in one sentence.** Multiply both sides of
        $T' + kT = kT_r$ by a cleverly-chosen function $\mu(t)$, picked
        so that the left side collapses into a single derivative
        $\dfrac{d}{dt}(\mu T)$. Once that happens, the equation reads
        $(\mu T)' = (\text{something integrable})$, and we just
        integrate.

        The video below walks the algebra through one move at a time —
        pick $\mu$, substitute back into the cooling equation, recognise
        the derivative, integrate, divide. We end up at the same
        closed form $T(t) = T_r + A\,e^{-kt}$ the separable method gave.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Beat 3e (cont.) — Manim derivation: the integrating-factor method
    # applied to T' + kT = kT_r, landing on the same closed form as the
    # separation walkthrough.
    delib.video(
        "cooling_linear_method.mp4",
        caption="The linear / integrating-factor route to the same closed form",
        fallback="The linear-method derivation is being rendered "
                 "(see manim/cooling_linear_method.py).",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Beat 3e (cont.) — after the video: the general 3-step recipe and a
    # forward pointer to Ch 3 where the same integrating factor reappears
    # as the simplest case of a more general rescue.
    mo.md(
        r"""
        **Two recipes, one answer.** The general version of what the
        video just walked through — applied to *any* linear first-order
        equation $y' + p(t)\,y = q(t)$, not just the cooling equation —
        is the three-step recipe at the heart of every textbook
        treatment of linear ODEs:

        > 1. Compute $\mu(t) = \exp\bigl(\int p(t)\,dt\bigr)$. This is
        >    called the **integrating factor**.
        > 2. Multiply the equation through by $\mu$. The left side
        >    becomes $(\mu y)'$ automatically.
        > 3. Integrate both sides, then divide by $\mu$.

        For the cooling equation, $p(t) = k$ is constant, so
        $\int k\,dt = kt$ and $\mu = e^{kt}$ — exactly the multiplier
        the video derived from first principles.

        The integrating factor is worth knowing as its own object, and
        not just as a step in this recipe — in Chapter 3 we'll see it
        reappear as the simplest case of a much more general idea, where
        the trick of multiplying through by a clever $\mu$ rescues
        equations that aren't even linear to begin with.
        """
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
def _(delib):
    controls = delib.param_panel(
        [
            {"name": "k", "label": "cooling rate k", "start": 0.05, "stop": 0.6, "step": 0.05, "value": 0.2},
            {"name": "Tr", "label": "room temperature Tr", "start": 0.0, "stop": 40.0, "step": 1.0, "value": 20.0},
            {"name": "T0", "label": "starting temp T₀", "start": 40.0, "stop": 100.0, "step": 1.0, "value": 90.0},
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
            ## Make it your kitchen

            Drag the sliders: $k$ is how fast it cools, $T_r$ is the room, and $T_0$ is
            how hot it started. The field redraws and the **red curve** — the exact
            solution from $T(0) = T_0$ — bends to follow it. Notice every curve, hot or
            cold, slides onto the room-temperature line.
            """
        ),
        controls,
    ])
    return


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
        "This is Chapter 2 of a differential-equations course: separable & linear "
        "first-order equations, worked through Newton's law of cooling "
        "dT/dt = -k(T - Tr) (room temperature Tr, cooling rate k), with closed-form "
        "solution T(t) = Tr + (T0 - Tr) e^(-k t).",
        prompts=[
            "explain separable vs linear",
            "solve the cooling equation by hand",
            "plot a few cooling curves",
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

        A separable or linear first-order equation hands you a real formula — and it
        threads exactly through the slope field, with every solution sliding onto the
        equilibrium $T = T_r$.

        **Next:** *Fixed points & stability* — we'll stop tracking one curve and ask
        which equilibria **attract** and which **repel**, reading stability straight off
        the rate.
        """
    )
    return


# --- Feedback (replaces the old playground) ------------------------------------
@app.cell(hide_code=True)
def _(delib):
    delib.feedback_form("Chapter 2 — Separable & linear")
    return


if __name__ == "__main__":
    app.run()
