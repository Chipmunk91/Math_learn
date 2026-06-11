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
        # Chapter 5 — Fixed points & stability (the phase line)

        **Where does motion stop, and does the stop hold?**

        By the end of this chapter you should be able to:

        - Find every **fixed point** of $\dot x = f(x)$ — every place
          on the line where motion can rest — and classify each as
          **stable** (a small nudge dies away) or **unstable** (a
          small nudge runs away).
        - Draw and read a **phase line**: a single picture that
          captures the long-term fate of every starting point on the
          1-D real line, without integrating anything.
        - See the same dynamics as a **potential landscape** $V(x)$:
          stable fixed points are valleys, unstable ones are hills, a
          marble rolls downhill.
        - Identify the **basin of attraction** of each stable
          point — which starting positions end up there.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, go, mo, np):
    # Section 1 — hook: bistable switches. Six trajectories of a 1-D ODE
    # released from different starts, all converging to +1 or -1. The
    # middle position is technically a place where motion can stop, but
    # nothing settles there — that's the gap the chapter will explain.
    # Annotations are deliberately *descriptive* ("none settle here")
    # rather than interpretive ("hill") so the metaphor isn't pre-spoiled.
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
                   annotation_text="rest height  +1",
                   annotation_position="top right")
    _fig.add_hline(y=-1, line=dict(color="#2a9d8f", dash="dash", width=1.5),
                   annotation_text="rest height  −1",
                   annotation_position="bottom right")
    _fig.add_hline(y=0, line=dict(color="#d1495b", dash="dot", width=1),
                   annotation_text="0  (none settle here)",
                   annotation_position="top right")
    _fig.update_layout(
        template="plotly_white",
        title=dict(text="Six starting positions, two destinations", x=0.02),
        xaxis=dict(title="time  t"),
        yaxis=dict(title="x(t)"),
        height=360, margin=dict(l=60, r=20, t=46, b=42),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    mo.vstack([
        mo.md(
            r"""
            ## Where motion comes to rest

            Flick a wall light switch halfway and let go. It doesn't
            sit halfway — it snaps decisively to *on* or *off* and
            stays put. You can run the same experiment with a clicky
            pen, a tipping kayak, a relay: anything with two settled
            positions and a balance point between them. The middle is
            technically a place where the object *could* rest if you
            placed it there perfectly, but in practice the slightest
            bias picks a side and the system commits.

            Now imagine sliding six identical objects along the same
            one-dimensional rail, releasing each from a different
            starting position, and recording their motion in time:
            """
        ),
        _fig,
        mo.md(
            r"""
            Six different starts, three possible heights at which the
            velocity is zero ($-1$, $0$, $+1$), but only **two**
            destinations actually used. Every trajectory ends parked
            at $+1$ or $-1$, and none — not even the one that started
            at $x = 0.1$, just a hair away from the middle — settles
            at $x = 0$. The middle is on the list of places where
            motion could stop, but in practice nothing stays there.

            That observation is the whole chapter in miniature. We're
            going to learn how to answer, for any 1-D system
            $\dot x = f(x)$:

            1. *Where can motion stop?* — the **fixed points** of the
               equation.
            2. *Which stops actually hold?* — the **stable** ones.

            The punchline is that you can answer both questions
            **without computing a single full trajectory**. The
            figure above used Chapter 4's machinery to integrate six
            initial conditions forward in time, but that was the long
            way around. Once you know what to look for, the equation
            itself — the formula $f(x)$ — tells you the long-term
            fate of every starting point on the line, no simulation
            required. That's the trade Chapter 4 ended by promising,
            and Chapter 5 cashes it in.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 2 — concept bridge. Earn the terms 'fixed point' and
    # 'stable / unstable' from the hook figure rather than declaring
    # them. The big move: notice that the time axis was wasted ink —
    # every trajectory's *destination* is the only thing that mattered.
    # That sets up the phase line (next section, Manim) as the picture
    # that keeps the information and throws away the rest.
    mo.md(
        r"""
        ## What the picture is really telling us

        Look at those six trajectories again. The time axis stretches
        all the way across the figure, but ask honestly: how much of
        that horizontal width do you actually need?

        For each trajectory, the *destination* — the height it
        converges to — is the only thing the picture is conveying.
        The wiggle in the middle of the figure is just the system
        "deciding," and given a starting position, it always decides
        the same thing. Most of the figure's ink is showing the
        *route*, but the chapter's question only cares about the
        *endpoint*.

        Strip the time axis away and the entire figure collapses to
        just three numbers — the heights where motion ends up:
        $-1$, $0$, $+1$. Those are exactly the heights where the
        velocity $\dot x = x - x^3$ happens to be zero. *(For
        $\dot x = x - x^3 = x(1 - x)(1 + x)$, the velocity vanishes
        precisely at $x \in \{-1, 0, +1\}$ — solve $f(x) = 0$.)* At
        those three values, the equation says "no motion here."

        But the hook also showed something stronger: not all three
        zeros are equal. The two outer ones, $\pm 1$, **hold** —
        every trajectory that gets near them stays near them. The
        middle one, $0$, **does not** — even the trajectory that
        started at $x = 0.1$ ran away from it.

        Two ideas have just done all the work, and they're worth
        naming:

        > A **fixed point** of $\dot x = f(x)$ is any value $x^*$
        > with $f(x^*) = 0$ — a place where the velocity vanishes,
        > so a system starting exactly there doesn't move.

        > A fixed point $x^*$ is **stable** if a small nudge away
        > from it is *undone* (the flow pulls back toward $x^*$),
        > and **unstable** if a small nudge is *amplified* (the
        > flow pushes farther away).

        For our equation, three fixed points $\{-1, 0, +1\}$, two
        stable ($\pm 1$), one unstable ($0$). The rest of the
        chapter is about how to spot fixed points without solving
        anything, how to tell stable from unstable at a glance
        rather than by integrating six trajectories, and how to
        pack all of this into a single picture that contains
        everything we just spent six time-traces to see.
        """
    )
    return


@app.cell(hide_code=True)
def _(go, mo, np):
    # Section 3 — build the model. Translate the switch story into sign
    # requirements on the velocity rule f, then show the simplest
    # polynomial that meets them is the cubic x - x^3. Figure: graph of
    # f vs x with the four sign bands annotated ("x increases / x
    # decreases") and the three zeros marked on the axis. Deliberately
    # no arrows-on-a-line yet — that's the phase line, earned next
    # section.
    _xs = np.linspace(-1.5, 1.5, 300)
    _fs = _xs - _xs**3

    _fig = go.Figure()
    # Sign bands: where f > 0 the motion goes right, where f < 0 left.
    for _x0, _x1, _txt in [
        (-1.5, -1.0, "f > 0:  x increases  →"),
        (-1.0,  0.0, "←  f < 0:  x decreases"),
        ( 0.0,  1.0, "f > 0:  x increases  →"),
        ( 1.0,  1.5, "←  f < 0:  x decreases"),
    ]:
        _fig.add_vrect(
            x0=_x0, x1=_x1,
            fillcolor=("#eaf3fb" if "increases" in _txt else "#fdf3e7"),
            line_width=0, layer="below",
        )
        _fig.add_annotation(
            x=(_x0 + _x1) / 2, y=1.75, text=_txt, showarrow=False,
            font=dict(size=11, color="#666"),
        )
    _fig.add_hline(y=0, line=dict(color="#9aa7b5", width=1))
    _fig.add_trace(go.Scatter(
        x=_xs, y=_fs, mode="lines",
        line=dict(color="#5b7db1", width=3),
        name="f(x) = x − x³",
        hovertemplate="f(%{x:.2f}) = %{y:.3f}<extra></extra>",
    ))
    _fig.add_trace(go.Scatter(
        x=[-1, 0, 1], y=[0, 0, 0], mode="markers",
        marker=dict(size=12, color="#d1495b",
                    line=dict(color="#7a2a3a", width=1.5)),
        name="zeros of f  (rest points)",
        hovertemplate="f(%{x}) = 0<extra></extra>",
    ))
    _fig.update_layout(
        template="plotly_white",
        title=dict(text="The velocity rule:  f(x) = x − x³", x=0.02),
        xaxis=dict(title="position  x", range=[-1.5, 1.5], zeroline=False),
        yaxis=dict(title="velocity  f(x)", range=[-2.0, 2.0],
                   zeroline=False),
        height=420, showlegend=True,
        legend=dict(x=0.02, y=0.02, bgcolor="rgba(255,255,255,0.85)"),
        margin=dict(l=60, r=20, t=50, b=45),
        paper_bgcolor="white", plot_bgcolor="white",
    )

    mo.vstack([
        mo.md(
            r"""
            ## Building the switch equation

            Time to write the equation behind the hook figure. We
            want the *simplest* velocity rule $\dot x = f(x)$ that
            behaves like the switch. Translate the story into
            demands on $f$, one by one:

            1. **Three resting places.** Motion can stop at the two
               settled positions and at the balance point between
               them. Choosing units so the settled positions sit at
               $x = \pm 1$, we need
               $f(-1) = f(0) = f(+1) = 0$, and no other zeros.
            2. **The outer rests hold.** Just *below* $+1$ the
               velocity must be positive (motion climbs back up
               toward $+1$); just *above* $+1$ it must be negative
               (motion falls back down). Same on both sides of $-1$,
               mirrored.
            3. **The middle rest breaks.** Just *above* $0$ the
               velocity must be positive — away from $0$, toward
               $+1$. Just *below* $0$, negative — away from $0$,
               toward $-1$.

            Put the three demands together and you've pinned down
            the **sign** of $f$ everywhere on the line:

            $$
            \underbrace{f > 0}_{x < -1}
            \qquad
            \underbrace{f < 0}_{-1 < x < 0}
            \qquad
            \underbrace{f > 0}_{0 < x < 1}
            \qquad
            \underbrace{f < 0}_{x > 1}
            $$

            A function that crosses zero exactly at $-1, 0, +1$ and
            alternates sign $+,-,+,-$ across the four intervals: the
            simplest polynomial that does this is a **cubic** with
            those three roots and a negative leading coefficient,

            $$
            f(x) \;=\; -\,x\,(x - 1)\,(x + 1) \;=\; x - x^3.
            $$

            That's the equation that generated every trajectory in
            the hook figure: $\dot x = x - x^3$. Here is its graph,
            with the sign structure made visible:
            """
        ),
        _fig,
        mo.md(
            r"""
            Check the demands against the picture. The curve crosses
            zero at exactly three places — the red dots — and the
            shaded bands alternate: blue means $f > 0$ (whatever is
            at that position moves **right**), tan means $f < 0$
            (moves **left**). Stand anywhere in the blue band between
            $0$ and $1$: you drift right until you hit $+1$, where
            the velocity hits zero and the drift stops. Stand
            anywhere just left of $0$: tan band, you drift left,
            away from $0$ and into $-1$'s grip.

            Notice what we just did. **We read off the direction of
            motion at every point on the line without solving the
            differential equation** — no integration, no Chapter 4
            machinery, nothing but the *sign* of $f$. The six
            trajectories in the hook figure took a numerical solver
            to draw; the sentence "everything between $0$ and $1$
            drifts right into $+1$" took one glance at the graph.

            One glance is still more ink than necessary. The next
            section compresses this entire figure into a single
            decorated line.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 4 (intro) — frame the phase line as the compression of
    # everything seen so far, then hand off to the Manim that performs
    # the compression on screen: trajectories -> endpoints -> a single
    # decorated line.
    mo.md(
        r"""
        ## The phase line — the whole story in one picture

        Let's assemble the compression we've been circling. Two
        observations are on the table:

        - From the hook: the **time axis is wasted ink** — each
          trajectory's only payload is its destination.
        - From the velocity graph: the **sign of $f$** tells you the
          direction of motion at every point, no integration needed.

        Combine them. Take the position line itself — just the
        $x$-axis, nothing else. Mark the places where $f = 0$ with
        dots: motion can rest there. In each interval between the
        dots, draw one arrow: right where $f > 0$, left where
        $f < 0$. Finally, make the dots tell the stability story at
        a glance — **fill** the dots that hold (arrows point *into*
        them from both sides) and leave **open** the ones that break
        (arrows point *away*).

        The result is called the **phase line**, and the video below
        builds it from the raw material — watch the six trajectories
        give up their time axis and collapse into it.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Section 4 — Manim hero: trajectories collapse into the phase line.
    delib.video(
        "phase_line_collapse.mp4",
        caption="From six trajectories to one phase line  —  ẋ = x − x³",
        fallback="The phase-line animation is being rendered "
                 "(see manim/phase_line_collapse.py).",
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Section 4 — the live phase line (FIRST hero visual).
    delib.phase_line(lambda x: x - x**3, (-2.0, 2.0),
                     title="Phase line of  ẋ = x − x³")
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 4 (reading guide) — how to read the phase line, and what
    # it buys: every starting point's fate, read directly off one line.
    mo.md(
        r"""
        Reading the phase line takes three rules, all of which you
        already know:

        - **Dots** are the fixed points — the values where
          $f(x) = 0$ and motion can rest.
        - **Arrows** show the flow between the dots — right where
          $f > 0$, left where $f < 0$.
        - **Filled vs open** is stability: a filled dot has the
          arrows on both sides pointing *in* (a nudge gets pushed
          back — the rest holds); an open dot has them pointing
          *out* (a nudge gets amplified — the rest breaks).

        Now use it. Put your finger anywhere on the line and follow
        the arrow you land on: from $x_0 = 0.1$, the arrow carries
        you right, into $+1$, where you stop. From $x_0 = -1.6$,
        right again, into $-1$. From *any* starting point, the
        phase line hands you the destination by inspection.

        Compare what went into the two pictures of this system. The
        hook figure cost six numerical integrations and showed six
        specific fates. The phase line cost one factoring
        ($f = 0$ at $-1, 0, +1$) and four sign checks — and it
        answers the fate question for **every** starting point at
        once. That's the trade this chapter is about: stop following
        individual journeys, and read the geography instead.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 5 — the stability test from f'. Linearise at a fixed
    # point; the nudge obeys Ch 4's decay/growth equation, so the sign
    # of f'(x*) settles stability. Earns the derivative test rather
    # than declaring it; Taylor is familiar from Ch 4.
    mo.md(
        r"""
        ## Stability without pictures — read it off $f'$

        The phase line settles stability by looking at arrows. That
        works beautifully when you can draw the picture — but it's
        worth having a version of the test that's pure calculation,
        both for speed and because in later chapters (two-dimensional
        systems, where pictures get harder) the calculation is what
        survives.

        Here's the question, sharpened. Stand at a fixed point $x^*$
        and apply a small nudge: the state becomes
        $x = x^* + \eta$, where $\eta$ (eta) is tiny — think of it
        as the "error" between where you are and the rest point.
        Does $\eta$ shrink back to zero, or grow?

        Watch what the differential equation says about $\eta$.
        Since $x^*$ is a constant, $\dot x = \dot\eta$, so

        $$
        \dot\eta \;=\; f(x^* + \eta).
        $$

        Now Taylor-expand $f$ around $x^*$ — the same move Chapter 4
        used on the true solution, and we only need the first two
        terms:

        $$
        f(x^* + \eta) \;=\; \underbrace{f(x^*)}_{=\,0}
        \;+\; f'(x^*)\,\eta \;+\; \mathcal{O}(\eta^2).
        $$

        The first term vanishes — that's exactly what made $x^*$ a
        fixed point. And while $\eta$ stays small, the $\eta^2$ term
        is negligible next to the $\eta$ term. What's left is
        startlingly simple:

        $$
        \dot\eta \;\approx\; f'(x^*)\,\eta.
        $$

        Look at the shape of that equation: *the rate of change of
        $\eta$ is a constant times $\eta$.* You've met it twice
        already — it's Chapter 2's exponential growth/decay, and it's
        the very equation Chapter 4's stability story was built on,
        with $f'(x^*)$ playing the role that $-\lambda$ played
        there. Its solution is

        $$
        \eta(t) \;\approx\; \eta(0)\, e^{f'(x^*)\,t},
        $$

        and everything hangs on the **sign of the exponent**:

        > - $f'(x^*) < 0$ — the nudge **decays exponentially**. The
        >   rest holds: $x^*$ is **stable**.
        > - $f'(x^*) > 0$ — the nudge **grows exponentially**. The
        >   rest breaks: $x^*$ is **unstable**.
        > - $f'(x^*) = 0$ — the linear term gives no verdict; the
        >   discarded $\eta^2$ term decides, so you must look closer
        >   (the phase-line arrows still work).

        Run the test on the switch equation. With
        $f(x) = x - x^3$ we get $f'(x) = 1 - 3x^2$, so:

        - $f'(0) = 1 > 0$ — unstable. The middle rest breaks, just
          as the hook showed.
        - $f'(\pm 1) = 1 - 3 = -2 < 0$ — stable. The outer rests
          hold.

        Three derivative evaluations, and the entire phase line's
        dot-filling is reproduced — no picture required. Even
        better, the *magnitude* tells you something the picture
        doesn't: near $\pm 1$ the nudge dies like $e^{-2t}$, so the
        switch doesn't just return to its settled position, it
        returns at a known exponential rate.

        Try it yourself below: edit the rate law and the equilibria
        and their classifications re-solve symbolically, live.
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
    # Section 6 — the potential landscape (SECOND hero visual). Make
    # the marble-rolls-downhill metaphor precise: define V by f = -V',
    # then stable = valley, unstable = hilltop, and the barrier height
    # becomes a meaningful physical quantity (the effort to flip the
    # switch).
    mo.md(
        r"""
        ## Same dynamics, second picture — the landscape

        All chapter long we've been saying things like "the marble
        rolls into the $+1$ valley" — borrowing the language of
        hills and valleys without ever drawing the hill. Let's earn
        the metaphor.

        We want a landscape — a height function $V(x)$ — such that
        a marble rolling downhill on $V$ moves exactly the way our
        equation says. "Rolling downhill" means: velocity points
        opposite to the slope of the ground. Steep downhill to the
        right → move right; steep downhill to the left → move left;
        flat ground → no motion. As an equation, that's

        $$
        \dot x \;=\; -\,V'(x).
        $$

        Match it against our system $\dot x = f(x)$ and the
        landscape is pinned down:

        $$
        f(x) = -V'(x)
        \qquad\Longleftrightarrow\qquad
        V(x) \;=\; -\int_0^{x} f(s)\,ds.
        $$

        For the switch equation $f(x) = x - x^3$, integrate:

        $$
        V(x) \;=\; -\frac{x^2}{2} + \frac{x^4}{4}.
        $$

        Every fact we've established now has a terrain reading:

        - **Fixed points** ($f = 0$) are where the ground is flat
          ($V' = 0$): the bottoms of valleys and the tops of hills.
        - **Stable** fixed points ($f' < 0$) are **valley bottoms** —
          a nudged marble rolls back down.
        - **Unstable** fixed points ($f' > 0$) are **hilltops** — a
          nudged marble rolls away, accelerating.
        - And one genuinely new quantity appears: the **barrier
          height**, the climb from a valley floor up to the hilltop
          that separates it from the neighbouring valley. That climb
          is the effort needed to *flip the switch* — to kick the
          system from one settled state into the other. A shallow
          barrier means an easy flip (a twitchy switch); a deep one
          means the state is locked in.

        Here's the landscape for the switch, with the same
        colour-coding as the phase line:
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
            ## Drop the marble yourself

            One slider, three synchronized views. Drag the starting
            position $x_0$ and watch the same experiment from three
            angles at once: the **phase line** shows which arrow the
            marble lands on, the **landscape** shows where it sits on
            the terrain, and the **time-trace** below shows the
            journey it actually takes.

            Two experiments worth running:

            - Sweep $x_0$ slowly across $0$, say from $-0.10$ to
              $+0.10$. The marble's *position* barely changes, but
              its *fate* flips completely — from the $-1$ valley to
              the $+1$ valley. The watershed is razor-thin.
            - Park the marble far out at $x_0 = 1.8$ and compare its
              time-trace with one from $x_0 = 0.2$. Both end at
              $+1$, but the approaches differ — the far marble rides
              a steep slope in fast, the near one crawls out of the
              flat neighbourhood of $0$ before committing.
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
def _(go, mo):
    # Section 7 — basins of attraction. The unstable point as the
    # watershed dividing the line into two catchments. Small dedicated
    # figure: the position line with the two basins shaded, fixed
    # points marked. Ends with the two-sentence bifurcation teaser
    # (next-chapter pointer, deliberately not opened here).
    _fig = go.Figure()
    _fig.add_vrect(x0=-2, x1=0, fillcolor="#f7ead9", line_width=0,
                   layer="below")
    _fig.add_vrect(x0=0, x1=2, fillcolor="#e3edf8", line_width=0,
                   layer="below")
    _fig.add_annotation(x=-1, y=0.6, text="basin of −1<br>every start here ends at −1",
                        showarrow=False, font=dict(size=12, color="#8a5c2e"))
    _fig.add_annotation(x=1, y=0.6, text="basin of +1<br>every start here ends at +1",
                        showarrow=False, font=dict(size=12, color="#2e5d8a"))
    _fig.add_trace(go.Scatter(
        x=[-2, 2], y=[0, 0], mode="lines",
        line=dict(color="#7c8aa0", width=1.5),
        hoverinfo="skip", showlegend=False,
    ))
    _fig.add_trace(go.Scatter(
        x=[-1, 1], y=[0, 0], mode="markers",
        marker=dict(color="#2a9d8f", size=15,
                    line=dict(color="#2a9d8f", width=2)),
        name="stable", hovertemplate="stable: x = %{x}<extra></extra>",
    ))
    _fig.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers",
        marker=dict(color="white", size=15,
                    line=dict(color="#d1495b", width=2.5)),
        name="unstable (the divide)",
        hovertemplate="unstable: x = 0<extra></extra>",
    ))
    _fig.update_layout(
        template="plotly_white",
        title=dict(text="Two basins, one divide", x=0.02),
        xaxis=dict(title="x", range=[-2, 2], zeroline=False),
        yaxis=dict(visible=False, range=[-0.5, 1.0]),
        height=240, showlegend=True,
        legend=dict(x=0.01, y=-0.35, orientation="h"),
        margin=dict(l=30, r=20, t=46, b=30),
        paper_bgcolor="white", plot_bgcolor="white",
    )

    mo.vstack([
        mo.md(
            r"""
            ## Who ends up where — basins of attraction

            The marble experiment showed it: every starting point is
            already committed. Start anywhere left of $0$ and you end
            at $-1$; start anywhere right of $0$ and you end at $+1$.
            The set of starting points that flow to a given stable
            fixed point is called its **basin of attraction** — the
            word picture is rainfall: every drop that lands in a
            river's catchment basin ends up in that river.

            For the switch, the unstable point at $0$ is the
            **divide** — the ridgeline between catchments:
            """
        ),
        _fig,
        mo.md(
            r"""
            This gives the unstable fixed point a real job. It never
            *collects* anything — no trajectory ends there — but it
            **organises** everything: it is the boundary that decides
            which fate each starting point gets. Two marbles released
            at $x_0 = -0.01$ and $x_0 = +0.01$ are nearly identical,
            yet they part ways forever. When a system has multiple
            settled states, the question "which one will I get?" is
            answered entirely by *which side of the divide you start
            on* — and near the divide, tiny causes pick between very
            different effects.

            One loose end, deliberately left loose. Our switch's
            landscape was fixed. But many real systems carry a
            **knob** — a temperature, a voltage, a drug dose — and
            turning the knob *tilts the landscape*. Tilt it far
            enough and a valley can become shallow, then flatten,
            then vanish entirely — and a system that had two settled
            states suddenly has one. What happens to a marble that
            was sitting in the valley that disappeared? That story
            — equations with a parameter, and the sudden
            rearrangements of their fixed points — is the
            *bifurcations* chapter, later in the course.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it — in code

        Three challenges, one per skill the chapter built: classify
        fixed points with the derivative test, predict a fate from
        the basin picture, and measure a barrier height on the
        landscape. SymPy is pre-loaded as `sp`, and `print()` works
        for inspecting intermediate values.
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

        - A **fixed point** of $\dot x = f(x)$ is any $x^*$ with
          $f(x^*) = 0$ — a place where motion can rest. Whether the
          rest *holds* is a separate question, and it's answered by
          what the flow does just next door.
        - The **phase line** packs the answer for every starting
          point into one picture: dots where $f = 0$, arrows
          following the sign of $f$, filled dots collecting their
          arrows (stable), open dots shedding them (unstable). No
          integration required — that's the chapter's trade: stop
          following individual journeys, read the geography.
        - The **derivative test** is the picture-free version: a
          small nudge $\eta$ off a fixed point obeys
          $\dot\eta \approx f'(x^*)\,\eta$, the exponential
          growth/decay equation. $f'(x^*) < 0$ — stable;
          $f'(x^*) > 0$ — unstable; $f'(x^*) = 0$ — look closer.
        - The **potential landscape** $V$ (with $f = -V'$) retells
          everything in terrain: valleys are stable, hilltops
          unstable, and the **barrier height** between valleys is
          the effort needed to flip the system from one settled
          state to the other.
        - Each stable point owns a **basin of attraction** — the
          set of starts that flow to it — and the unstable points
          are the **divides** between basins: they collect nothing
          but decide everything.

        **Next:** so far each chapter's equations had one state
        variable. Next we meet systems that need **two** — a
        position *and* a velocity, a predator *and* its prey — where
        solutions become curves in a plane rather than points on a
        line, and a new cast of behaviours (spirals, orbits, saddle
        points) becomes possible.
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
        "This is Chapter 5 of a differential-equations course: 1-D fixed "
        "points and stability, worked through the bistable equation "
        "x' = x - x^3 (the wall-light-switch story: two settled states, "
        "one balance point that doesn't hold). Key ideas: fixed points "
        "where f(x) = 0; stability via the linearisation eta' ~ f'(x*) eta "
        "(f' < 0 stable, f' > 0 unstable, f' = 0 inconclusive); the phase "
        "line (filled dot = stable, open = unstable, arrows = sign of f); "
        "the potential V with f = -V' (valley = stable, hilltop = "
        "unstable, barrier height = effort to flip states); basins of "
        "attraction with unstable points as divides. Earlier chapters: "
        "slope fields (Ch 1), separable/linear + integrating factor "
        "(Ch 2), exact equations (Ch 3a/3b), numerical methods — Euler, "
        "RK4, order of accuracy, stiffness (Ch 4).",
        prompts=[
            "explain this chapter in a paragraph",
            "show another bistable system and its phase line",
            "plot the potential for x' = sin(x)",
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
