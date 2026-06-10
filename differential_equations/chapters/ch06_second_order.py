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
        # Chapter 6 — Second-order ODEs

        **When one number isn't enough.**

        By the end of this chapter you should be able to:

        - Explain why oscillation is **impossible** for the 1-D flows
          of Chapter 5, and why describing a vibrating system takes
          **two** numbers — a position *and* a velocity.
        - Turn a force law into a **second-order** differential
          equation ($m\ddot x = F$), and solve the frictionless
          spring by guessing trig functions.
        - Solve **any** constant-coefficient linear second-order
          equation $\ddot x + b\dot x + c x = 0$ with the exponential
          guess $x = e^{rt}$ and its **characteristic equation**.
        - Classify the three behaviours — pure decay, decaying
          oscillation, and the borderline between them — from the
          **roots** of the characteristic equation, and pin the two
          free constants with **initial conditions**.
        """
    )
    return


@app.cell(hide_code=True)
def _(go, mo, np):
    # Section 1 — hook: a mass bobbing on a spring. The new phenomenon
    # is oscillation, which the entire 1-D toolkit of Ch 5 provably
    # cannot produce: arrows on a line never turn around. The figure
    # shows x(t) = cos(2t) with the same position visited over and
    # over with different velocities — planting the idea that the
    # state needs two numbers.
    _t = np.linspace(0, 8, 400)
    _x = np.cos(2 * _t)
    _fig = go.Figure()
    _fig.add_trace(go.Scatter(
        x=_t, y=_x, mode="lines",
        line=dict(color="#5b7db1", width=3),
        hoverinfo="skip", showlegend=False,
    ))
    _fig.add_hline(y=0, line=dict(color="#9aa7b5", width=1))
    # Mark two passes through x = 0 with opposite velocities.
    _fig.add_trace(go.Scatter(
        x=[np.pi / 4], y=[0], mode="markers",
        marker=dict(size=13, color="#d1495b",
                    line=dict(color="#7a2a3a", width=1.5)),
        name="passing x = 0, moving down",
        hovertemplate="t = π/4: x = 0, velocity < 0<extra></extra>",
    ))
    _fig.add_trace(go.Scatter(
        x=[3 * np.pi / 4], y=[0], mode="markers",
        marker=dict(size=13, color="#2a9d8f",
                    line=dict(color="#1d6e64", width=1.5)),
        name="passing x = 0, moving up",
        hovertemplate="t = 3π/4: x = 0, velocity > 0<extra></extra>",
    ))
    _fig.update_layout(
        template="plotly_white",
        title=dict(text="A mass on a spring: position vs time", x=0.02),
        xaxis=dict(title="time  t"),
        yaxis=dict(title="displacement  x(t)", range=[-1.4, 1.4]),
        height=340, showlegend=True,
        legend=dict(x=0.62, y=0.02, bgcolor="rgba(255,255,255,0.85)",
                    font=dict(size=11)),
        margin=dict(l=60, r=20, t=46, b=42),
        paper_bgcolor="white", plot_bgcolor="white",
    )

    mo.vstack([
        mo.md(
            r"""
            ## Something Chapter 5 cannot do

            Hang a weight from a spring, pull it down an inch, and
            let go. It bobs: up past the resting height, slows,
            comes back down, overshoots again — back and forth,
            over and over. (A real spring's bobbing slowly fades;
            for now, picture an ideal one that keeps going.)

            Here's the puzzle. Look at the trace below and try to
            describe this motion with last chapter's machinery —
            a rule $\dot x = f(x)$ assigning one velocity to each
            position. You can't, and not because the right $f$ is
            hard to find. **No such $f$ exists.** On a phase line,
            arrows never turn around: between two fixed points the
            flow goes one way, so a 1-D trajectory can only drift
            monotonically toward a rest point. It can never come
            *back*. Oscillation — the most common motion in the
            physical world — is structurally impossible in
            Chapter 5's framework.
            """
        ),
        _fig,
        mo.md(
            r"""
            The two marked dots say *why* it's impossible. Both
            sit at the same position, $x = 0$ — and the mass is
            doing two different things there: at the red dot it's
            falling, at the teal dot it's rising. So "where is
            the mass?" does **not** determine "what happens
            next?" A rule of the form $\dot x = f(x)$ — one
            future per position — can't tell those two moments
            apart.

            What *would* distinguish them is the **velocity**.
            Position $0$, moving down, and position $0$, moving
            up, are different states even though they're the
            same place. To predict this system you must track
            **two numbers** — and that one change unlocks
            everything in this chapter.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 2 — concept bridge: from force law to second-order ODE.
    # Earn Hooke's law and assemble m x'' = -k x; name 'second-order';
    # note the doubled state (two initial conditions).
    mo.md(
        r"""
        ## From force to equation

        Where does the spring's equation of motion come from? Two
        physical facts, both worth stating carefully.

        **Fact 1 — what the spring does.** Stretch a spring and it
        pulls back; compress it and it pushes back. Measure
        carefully and the restoring force is *proportional* to how
        far you've displaced it: stretch twice as far, feel twice
        the pull. With $x$ the displacement from rest and $k > 0$
        the spring's stiffness,

        $$
        F \;=\; -k\,x.
        $$

        The minus sign is the spring's whole personality: the force
        always points *back toward* $x = 0$, opposing the
        displacement.

        **Fact 2 — what a force does.** Newton's second law: a net
        force $F$ on a mass $m$ produces acceleration $F/m$.
        Acceleration is the rate of change of velocity, which is
        itself the rate of change of position — the **second
        derivative** $\ddot x$. (Dots are time-derivatives:
        $\dot x = dx/dt$, $\ddot x = d^2x/dt^2$.)

        Put the two together:

        $$
        m\,\ddot x \;=\; -k\,x
        \qquad\Longleftrightarrow\qquad
        \ddot x \;=\; -\frac{k}{m}\,x.
        $$

        Read it as a sentence: *the further the mass sits from
        rest, the harder it accelerates back toward rest.* That's
        the bobbing, in one line.

        Because the highest derivative appearing is the second,
        this is a **second-order** differential equation — our
        first. And the order isn't bookkeeping; it's exactly the
        two-numbers observation from the hook wearing algebraic
        clothes:

        - To launch the system you must specify **two** initial
          conditions — the starting position $x(0)$ *and* the
          starting velocity $\dot x(0)$. (Pull down an inch and
          release from rest, or strike the resting mass with a
          hammer: same equation, different starts, different
          motions.)
        - So expect the general solution to carry **two free
          constants**, one per initial condition — where Chapters
          1–5 always had one.

        Now let's actually solve it.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, mo):
    # Section 3 — guess and check on the frictionless spring, then the
    # k, m sliders. Guessing cos/sin is honest here (the hook trace
    # looks like a cosine); the general method comes next section.
    mo.md(
        r"""
        ## Solving the spring — by guessing

        The trace in the hook figure *looks* like a cosine. Take
        that seriously: guess $x(t) = \cos(\omega t)$ with the
        frequency $\omega$ left unknown, and test the guess by
        substituting it into $\ddot x = -(k/m)\,x$.

        Differentiate twice:

        $$
        x = \cos(\omega t), \qquad
        \dot x = -\omega \sin(\omega t), \qquad
        \ddot x = -\omega^2 \cos(\omega t).
        $$

        Substitute:

        $$
        \underbrace{-\omega^2 \cos(\omega t)}_{\ddot x}
        \;=\; -\frac{k}{m}\,\underbrace{\cos(\omega t)}_{x}.
        $$

        The cosines match on both sides — so the guess works,
        *provided* the constants agree:

        $$
        \omega^2 = \frac{k}{m}
        \qquad\Longrightarrow\qquad
        \boxed{\;\omega = \sqrt{k/m}\;}
        $$

        The guess didn't just survive; it came back with a
        prediction. The bobbing frequency is set by the physical
        constants: **stiffer spring** (bigger $k$) → faster
        bobbing; **heavier mass** (bigger $m$) → slower. You can
        feel both in your hands — a stiff spring twangs, a heavy
        weight lumbers.

        Two more checks, each quick:

        - $x = \sin(\omega t)$ passes the same test (differentiate
          twice: $-\omega^2 \sin$, same cancellation). A second,
          genuinely different solution — it starts at $x = 0$
          moving *upward*, where cosine starts at the top at rest.
        - Any combination $x = C_1 \cos(\omega t) + C_2
          \sin(\omega t)$ also passes: differentiating term by
          term, each piece separately returns $-\omega^2$ times
          itself. (This works because the equation is **linear** —
          $x$ and its derivatives appear to the first power only,
          never squared or multiplied together.)

        And there are our **two free constants**, right on
        schedule: $C_1$ is the starting position and, after one
        differentiation, $C_2 \omega$ is the starting velocity.
        Two knobs, two initial conditions, exactly as the bridge
        predicted.

        Feel the frequency formula with the sliders: $\omega =
        \sqrt{k/m}$, starting from $x(0) = 1$, $\dot x(0) = 0$.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    spring_panel = delib.param_panel([
        {"name": "k", "label": "spring stiffness  k",
         "start": 0.5, "stop": 8.0, "step": 0.25, "value": 4.0},
        {"name": "m", "label": "mass  m",
         "start": 0.25, "stop": 4.0, "step": 0.25, "value": 1.0},
    ])
    return (spring_panel,)


@app.cell(hide_code=True)
def _(go, mo, np, spring_panel):
    _k = float(spring_panel.value["k"])
    _m = float(spring_panel.value["m"])
    _w = float(np.sqrt(_k / _m))
    _t = np.linspace(0, 12, 600)
    _x = np.cos(_w * _t)

    _fig = go.Figure()
    _fig.add_trace(go.Scatter(
        x=_t, y=_x, mode="lines",
        line=dict(color="#5b7db1", width=3),
        hoverinfo="skip", showlegend=False,
    ))
    _fig.add_hline(y=0, line=dict(color="#9aa7b5", width=1))
    _fig.update_layout(
        template="plotly_white",
        title=dict(
            text=f"x(t) = cos(ωt)   with   ω = √(k/m) = {_w:.2f}",
            x=0.02,
        ),
        xaxis=dict(title="time  t"),
        yaxis=dict(title="x(t)", range=[-1.4, 1.4]),
        height=320,
        margin=dict(l=60, r=20, t=46, b=42),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    mo.vstack([spring_panel, _fig])
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 4 (intro) — motivate the exponential ansatz: friction
    # breaks the trig guess, and the universal reason e^{rt} works is
    # that differentiation maps it to a multiple of itself. Hands off
    # to the Manim that runs the derivation.
    mo.md(
        r"""
        ## The universal guess

        Guessing $\cos$ worked because the frictionless spring's
        solution *is* a cosine. But add friction — a force
        proportional to velocity, dragging against the motion —
        and the equation becomes

        $$
        m\ddot x \;=\; -k x - \beta \dot x
        \qquad\text{i.e.}\qquad
        \ddot x + b\,\dot x + c\,x = 0
        $$

        (dividing through by $m$ and renaming constants). Try
        $x = \cos(\omega t)$ here and it fails: the $\dot x$ term
        produces a *sine*, and a cosine plus a sine can't cancel
        to zero at every instant. The trig guess was a lucky fit
        for one equation, not a method.

        Here's the guess that *is* a method. What makes an
        equation like this hard is that it mixes $x$, $\dot x$,
        and $\ddot x$ — three different-looking functions that
        must conspire to cancel forever. So pick the one function
        in mathematics whose derivatives all look like itself:

        $$
        x = e^{rt}
        \quad\Longrightarrow\quad
        \dot x = r\,e^{rt},
        \quad
        \ddot x = r^2\,e^{rt}.
        $$

        Every derivative of $e^{rt}$ is just a *multiple* of
        $e^{rt}$. Substitute it in, and all three terms become
        (number) × $e^{rt}$ — the conspiracy reduces to one
        algebraic condition on the number $r$. The video below
        runs the computation; watch the calculus dissolve into a
        quadratic.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Section 4 — Manim hero: the exponential ansatz and the
    # characteristic equation.
    delib.video(
        "characteristic_equation.mp4",
        caption="The exponential guess:  ẍ + bẋ + cx = 0  →  r² + br + c = 0",
        fallback="The characteristic-equation animation is being rendered "
                 "(see manim/characteristic_equation.py).",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 4 (post-video) — name the characteristic equation and
    # set up the three-case fork on the discriminant.
    mo.md(
        r"""
        The quadratic at the end of the video,

        $$
        r^2 + b\,r + c \;=\; 0,
        $$

        is called the **characteristic equation** of
        $\ddot x + b\dot x + cx = 0$, and solving it is now just
        the quadratic formula:

        $$
        r \;=\; \frac{-b \pm \sqrt{\,b^2 - 4c\,}}{2}.
        $$

        Each root $r$ gives a working solution $e^{rt}$, and
        linearity lets us combine them with the two free constants
        we've been expecting:

        $$
        x(t) \;=\; C_1 e^{r_1 t} + C_2 e^{r_2 t}.
        $$

        But look inside the square root. The quantity $b^2 - 4c$
        can be positive, zero, or negative — and those three signs
        produce **three genuinely different kinds of motion**.
        That's not a technicality; it's the chapter's payoff.
        """
    )
    return


@app.cell(hide_code=True)
def _(go, mo, np):
    # Section 5 — the three cases, each earned from its roots, with a
    # one-figure gallery (three example solutions, one per case). The
    # complex case states Euler's formula and pushes the wherefrom
    # into a collapsed accordion so the main flow keeps moving.
    def _xt(b, c, t):
        # Closed-form solution of x'' + b x' + c x = 0, x(0)=1, x'(0)=0,
        # via complex roots (handles all three cases; tiny eps splits
        # the repeated-root case).
        disc = complex(b * b - 4 * c)
        sq = np.sqrt(disc)
        r1 = (-b + sq) / 2
        r2 = (-b - sq) / 2
        if abs(r1 - r2) < 1e-9:
            return np.real((1 - r1 * t) * np.exp(r1 * t))
        c1 = -r2 / (r1 - r2)
        c2 = r1 / (r1 - r2)
        return np.real(c1 * np.exp(r1 * t) + c2 * np.exp(r2 * t))

    _t = np.linspace(0, 10, 500)
    _fig = go.Figure()
    for _b, _c, _name, _color in [
        (3.0, 2.0, "b² − 4c > 0 :  two real roots — pure decay", "#b5651d"),
        (2.0, 1.0, "b² − 4c = 0 :  repeated root — fastest clean decay", "#7c8aa0"),
        (0.5, 4.0, "b² − 4c < 0 :  complex roots — decaying oscillation", "#5b7db1"),
    ]:
        _fig.add_trace(go.Scatter(
            x=_t, y=_xt(_b, _c, _t), mode="lines",
            line=dict(width=2.8, color=_color),
            name=_name,
            hovertemplate="t = %{x:.2f}, x = %{y:.3f}<extra></extra>",
        ))
    _fig.add_hline(y=0, line=dict(color="#9aa7b5", width=1))
    _fig.update_layout(
        template="plotly_white",
        title=dict(text="Three signs of b² − 4c, three motions  "
                        "(all from x(0) = 1, ẋ(0) = 0)", x=0.02),
        xaxis=dict(title="time  t"),
        yaxis=dict(title="x(t)", range=[-0.8, 1.2]),
        height=400, showlegend=True,
        legend=dict(x=0.35, y=0.98, bgcolor="rgba(255,255,255,0.85)",
                    font=dict(size=11)),
        margin=dict(l=60, r=20, t=50, b=42),
        paper_bgcolor="white", plot_bgcolor="white",
    )

    mo.vstack([
        mo.md(
            r"""
            ## Three signs, three motions

            ### Case 1 — $b^2 - 4c > 0$: two real roots

            The square root is an honest real number, and we get two
            distinct real roots $r_1 \neq r_2$. The solution is a sum
            of two plain exponentials:

            $$
            x(t) = C_1 e^{r_1 t} + C_2 e^{r_2 t}.
            $$

            Example: $\ddot x + 3\dot x + 2x = 0$ has characteristic
            equation $r^2 + 3r + 2 = (r+1)(r+2) = 0$, roots $-1$
            and $-2$. Both negative, so both pieces decay and the
            solution slumps to zero **without ever oscillating** —
            think of releasing a spring submerged in honey. Friction
            so dominates that the mass oozes home and stops.

            ### Case 2 — $b^2 - 4c = 0$: one repeated root

            The square root vanishes and both roots collapse onto
            $r = -b/2$ — one root, but the equation still owes us
            *two* independent solutions. The second one turns out to
            be $t\,e^{rt}$ (check it: substitute and watch the terms
            cancel — it works precisely *because* the root is
            repeated), giving

            $$
            x(t) = (C_1 + C_2\,t)\,e^{rt}.
            $$

            This knife-edge case is the **fastest decay without
            overshoot** — which is why engineers tune for it: a door
            closer that neither slams nor crawls is sitting on this
            exact borderline.

            ### Case 3 — $b^2 - 4c < 0$: complex roots

            Now the square root holds a negative number, and the
            roots come out as a complex pair $r = a \pm i\,\beta$
            with $a = -b/2$ and $\beta = \sqrt{4c - b^2}/2$. An
            exponential with an *imaginary* number upstairs has a
            beautiful meaning, given by **Euler's formula**:

            $$
            e^{i\beta t} \;=\; \cos(\beta t) + i \sin(\beta t)
            $$

            — a complex exponential doesn't blow up or die; it
            **circles**, and its real-world shadow is a pure
            oscillation. (Where the formula comes from is a lovely
            story — see the fold-out below.) Carrying it through and
            collecting real parts gives the real solution

            $$
            x(t) \;=\; e^{a t}\bigl(C_1 \cos \beta t + C_2 \sin \beta t\bigr):
            $$

            an oscillation at frequency $\beta$, inside an
            exponential envelope $e^{at}$. For a damped spring
            $a < 0$: the bobbing persists but its amplitude dies
            away — exactly what a real spring does.

            And run the frictionless spring through this case as a
            check: $\ddot x + \omega^2 x = 0$ means $b = 0$,
            $c = \omega^2$, roots $\pm i\omega$, so $a = 0$ (no
            envelope) and $\beta = \omega$ — recovering precisely
            the $\cos / \sin$ solutions we guessed earlier. The trig
            guess wasn't a separate trick; it was the complex case
            in disguise.
            """
        ),
        mo.accordion({
            "Where Euler's formula comes from (optional)": mo.md(
                r"""
                Write down the Taylor series — the same expansions
                Chapter 4 used — for the three functions involved:

                $$
                e^{u} = 1 + u + \frac{u^2}{2!} + \frac{u^3}{3!} + \frac{u^4}{4!} + \cdots
                $$

                $$
                \cos\theta = 1 - \frac{\theta^2}{2!} + \frac{\theta^4}{4!} - \cdots
                \qquad
                \sin\theta = \theta - \frac{\theta^3}{3!} + \frac{\theta^5}{5!} - \cdots
                $$

                Now substitute $u = i\theta$ into the first series,
                using $i^2 = -1$, $i^3 = -i$, $i^4 = +1$, repeating:

                $$
                e^{i\theta}
                = 1 + i\theta - \frac{\theta^2}{2!} - i\frac{\theta^3}{3!}
                + \frac{\theta^4}{4!} + i\frac{\theta^5}{5!} - \cdots
                $$

                Collect the terms without $i$ and the terms with $i$:
                the first group is exactly the cosine series, the
                second is exactly $i$ times the sine series. Hence
                $e^{i\theta} = \cos\theta + i\sin\theta$.
                """
            ),
        }),
        mo.md("One picture with all three cases, same starting "
              "condition, so the shapes are directly comparable:"),
        _fig,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 6 (intro) — hero: roots in the complex plane vs the
    # response. Frame what the student should watch while scrubbing.
    mo.md(
        r"""
        ## The map of all motions

        Time to put the whole classification on two axes. For
        $\ddot x + b\dot x + cx = 0$, everything about the motion is
        encoded in **where the two roots sit in the complex plane**:

        - **Horizontal position = growth/decay.** Roots to the left
          of the imaginary axis have $e^{rt}$ shrinking; further
          left, faster. (Right of the axis would mean growth.)
        - **Vertical position = oscillation.** Roots off the real
          axis come in mirror pairs $a \pm i\beta$, and the height
          $\beta$ is the oscillation frequency. On the axis: no
          oscillation at all.

        Scrub the **friction slider** $b$ and watch both panels:

        - At $b = 0$, the roots sit *on* the imaginary axis —
          pure oscillation, no decay (the ideal spring).
        - Increasing $b$ pulls the pair left into the plane:
          decay *plus* oscillation, the envelope tightening.
        - At $b^2 = 4c$ the pair **collides on the real axis** —
          the repeated root, fastest clean decay.
        - Push further and the collided pair **splits along the
          real axis** — two real roots, the honey regime; the
          slow root (the one closer to zero) controls how long
          the slump takes.

        The stiffness slider $c$ moves the collision point: stiffer
        systems need more friction to stop ringing.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    hero_panel = delib.param_panel([
        {"name": "b", "label": "friction  b",
         "start": 0.0, "stop": 5.0, "step": 0.1, "value": 0.6},
        {"name": "c", "label": "stiffness  c",
         "start": 0.5, "stop": 4.0, "step": 0.25, "value": 2.0},
    ])
    return (hero_panel,)


@app.cell(hide_code=True)
def _(go, hero_panel, mo, np):
    # Section 6 — hero figure: complex-plane root positions (left)
    # and the response x(t) with x(0)=1, x'(0)=0 (right), live off
    # the b and c sliders.
    from plotly.subplots import make_subplots as _make_subplots

    _b = float(hero_panel.value["b"])
    _c = float(hero_panel.value["c"])

    _disc = complex(_b * _b - 4 * _c)
    _sq = np.sqrt(_disc)
    _r1 = (-_b + _sq) / 2
    _r2 = (-_b - _sq) / 2

    if abs(_disc) < 1e-12:
        _case = "repeated root — critical"
    elif _disc.real > 0:
        _case = "two real roots — pure decay"
    else:
        _case = "complex pair — decaying oscillation"

    _t = np.linspace(0, 14, 700)
    if abs(_r1 - _r2) < 1e-9:
        _x = np.real((1 - _r1 * _t) * np.exp(_r1 * _t))
    else:
        _c1 = -_r2 / (_r1 - _r2)
        _c2 = _r1 / (_r1 - _r2)
        _x = np.real(_c1 * np.exp(_r1 * _t) + _c2 * np.exp(_r2 * _t))

    _fig = _make_subplots(
        cols=2, rows=1,
        column_widths=[0.38, 0.62],
        subplot_titles=("roots of  r² + br + c", "response  x(t)"),
        horizontal_spacing=0.10,
    )
    # Left panel: complex plane.
    _fig.add_trace(go.Scatter(
        x=[0, 0], y=[-2.4, 2.4], mode="lines",
        line=dict(color="#9aa7b5", width=1, dash="dot"),
        hoverinfo="skip", showlegend=False,
    ), row=1, col=1)
    _fig.add_trace(go.Scatter(
        x=[-5.2, 0.6], y=[0, 0], mode="lines",
        line=dict(color="#9aa7b5", width=1),
        hoverinfo="skip", showlegend=False,
    ), row=1, col=1)
    _fig.add_trace(go.Scatter(
        x=[_r1.real, _r2.real], y=[_r1.imag, _r2.imag],
        mode="markers",
        marker=dict(size=15, color="#d1495b", symbol="x-thin",
                    line=dict(color="#d1495b", width=3.5)),
        name="roots",
        hovertemplate="r = %{x:.3f} %{y:+.3f}i<extra></extra>",
        showlegend=False,
    ), row=1, col=1)
    # Right panel: response.
    _fig.add_trace(go.Scatter(
        x=_t, y=_x, mode="lines",
        line=dict(color="#5b7db1", width=3),
        hoverinfo="skip", showlegend=False,
    ), row=1, col=2)
    _fig.add_hline(y=0, line=dict(color="#9aa7b5", width=1),
                   row=1, col=2)

    _fig.update_xaxes(title="Re r", range=[-5.2, 0.6], row=1, col=1)
    _fig.update_yaxes(title="Im r", range=[-2.4, 2.4], row=1, col=1)
    _fig.update_xaxes(title="t", row=1, col=2)
    _fig.update_yaxes(title="x(t)", range=[-1.1, 1.3], row=1, col=2)
    _fig.update_layout(
        template="plotly_white",
        title=dict(
            text=f"b = {_b:.1f},  c = {_c:.2f}   →   {_case}",
            x=0.02,
        ),
        height=420, showlegend=False,
        margin=dict(l=60, r=20, t=80, b=45),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    mo.vstack([hero_panel, _fig])
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 7 — pinning the constants with initial conditions:
    # one fully worked example.
    mo.md(
        r"""
        ## Pinning the two constants

        The general solution always arrives with $C_1$ and $C_2$
        dangling — the two knobs the bridge section promised. The
        initial conditions pin them. One worked example, start to
        finish.

        **Problem.** Solve $\ddot x + 4x = 0$ with $x(0) = 1$ and
        $\dot x(0) = 0$ — the ideal spring with $\omega = 2$,
        pulled to $+1$ and released from rest.

        **Step 1 — general solution.** Characteristic equation
        $r^2 + 4 = 0$, roots $r = \pm 2i$. Complex case with
        $a = 0$, $\beta = 2$:

        $$
        x(t) = C_1 \cos 2t + C_2 \sin 2t.
        $$

        **Step 2 — apply $x(0) = 1$.** Set $t = 0$: the sine
        vanishes, the cosine is $1$, so $x(0) = C_1 = 1$.

        **Step 3 — apply $\dot x(0) = 0$.** Differentiate first:
        $\dot x = -2 C_1 \sin 2t + 2 C_2 \cos 2t$. At $t = 0$:
        $\dot x(0) = 2 C_2 = 0$, so $C_2 = 0$.

        **Answer.** $x(t) = \cos 2t$. Released from rest at $+1$,
        the mass bobs forever with frequency $2$ — the hook
        figure's exact trace.

        The pattern generalises: the position condition feeds the
        un-differentiated solution, the velocity condition feeds
        its derivative, and the two equations always determine the
        two constants. (Two conditions, two unknowns, one linear
        solve — never worse than that.)
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it — in code

        Three challenges, one per skill: solve a characteristic
        equation, carry initial conditions through, and use the
        frequency formula. SymPy is pre-loaded as `sp`, and
        `print()` works for inspecting intermediate values.
        """
    )
    return


# --- Challenge 1: roots of the characteristic equation -------------------------
@app.cell
def _(mo):
    e1_get, e1_set = mo.state(
        "# For x'' + 5x' + 6x = 0, write down the characteristic\n"
        "# equation and find its two roots. Put the LARGER root\n"
        "# (closer to zero) in `answer`.\n"
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
        context="x'' + 5x' + 6x = 0 has characteristic equation "
                "r^2 + 5r + 6 = (r+2)(r+3) = 0, roots -2 and -3. The "
                "larger (closer to zero) is -2. sp.solve(r**2 + 5*r + 6, r) "
                "also works. Put -2 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_ai, e1_code, e1_gen, e1_run):
    delib.exercise_view(
        "**1.** For $\\ddot x + 5\\dot x + 6x = 0$, find the two roots "
        "of the characteristic equation and put the **larger** one "
        "(closer to zero) in `answer`. Which of the three cases is "
        "this equation in?",
        e1_ai, e1_gen, e1_code, e1_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_code, e1_run):
    delib.run_exercise(e1_code.value, e1_run.value, check=lambda ns: delib.check_number(
        ns, target=-2.0, tol=1e-3,
        ok="Right — $r^2 + 5r + 6 = (r+2)(r+3)$, roots $-2$ and $-3$. "
           "Two distinct real roots: the pure-decay case. The $-2$ root "
           "decays slower, so it dominates the long-time behaviour.",
        hint="Factor $r^2 + 5r + 6$ (or use `sp.solve`). Both roots are "
             "negative; 'larger' means closer to zero.",
    ))
    return


# --- Challenge 2: initial conditions through to a value ------------------------
@app.cell
def _(mo):
    e2_get, e2_set = mo.state(
        "# Solve x'' + 4x = 0 with x(0) = 0 and x'(0) = 6.\n"
        "# (Note: starts AT REST POSITION, struck with velocity 6.)\n"
        "# Evaluate x at t = pi/4 and put the value in `answer`.\n"
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
        context="x'' + 4x = 0: roots ±2i, general solution "
                "C1 cos 2t + C2 sin 2t. x(0)=0 gives C1=0. "
                "x' = 2 C2 cos 2t so x'(0) = 2 C2 = 6, C2 = 3. "
                "x(t) = 3 sin 2t. x(pi/4) = 3 sin(pi/2) = 3. "
                "Put 3 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_ai, e2_code, e2_gen, e2_run):
    delib.exercise_view(
        "**2.** Solve $\\ddot x + 4x = 0$ with $x(0) = 0$ and "
        "$\\dot x(0) = 6$ — the mass starts at rest position and is "
        "struck. Evaluate $x(\\pi/4)$ and put it in `answer`.",
        e2_ai, e2_gen, e2_code, e2_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_code, e2_run):
    delib.run_exercise(e2_code.value, e2_run.value, check=lambda ns: delib.check_number(
        ns, target=3.0, tol=1e-3,
        ok="Right — $x(0) = 0$ kills the cosine, $\\dot x(0) = 6$ gives "
           "$C_2 = 3$, so $x = 3\\sin 2t$ and $x(\\pi/4) = 3\\sin(\\pi/2) = 3$.",
        hint="General solution $C_1 \\cos 2t + C_2 \\sin 2t$. The position "
             "condition pins $C_1$; differentiate before applying the "
             "velocity condition.",
    ))
    return


# --- Challenge 3: the frequency formula -----------------------------------------
@app.cell
def _(mo):
    e3_get, e3_set = mo.state(
        "# A mass m = 0.25 kg hangs on a spring with stiffness\n"
        "# k = 4 N/m (no friction). What is the angular frequency\n"
        "# of its bobbing? Put it in `answer`.\n"
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
        context="omega = sqrt(k/m) = sqrt(4/0.25) = sqrt(16) = 4 rad/s. "
                "Put 4 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_ai, e3_code, e3_gen, e3_run):
    delib.exercise_view(
        "**3.** A mass $m = 0.25$ kg hangs on a frictionless spring of "
        "stiffness $k = 4$ N/m. What is the angular frequency $\\omega$ "
        "of its bobbing? Put it in `answer`.",
        e3_ai, e3_gen, e3_code, e3_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_code, e3_run):
    delib.run_exercise(e3_code.value, e3_run.value, check=lambda ns: delib.check_number(
        ns, target=4.0, tol=1e-3,
        ok="Right — $\\omega = \\sqrt{k/m} = \\sqrt{16} = 4$ rad/s. Light "
           "mass + stiff spring = fast bobbing.",
        hint="The frequency formula from the guess-and-check section: "
             "$\\omega = \\sqrt{k/m}$.",
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
        "# Solve x'' + b x' + c x = 0 numerically and plot. Try your\n"
        "# own b, c — or set b = 0 and watch it ring forever.\n"
        "b, c = 0.4, 4.0\n"
        "sol = delib.solve_system(\n"
        "    lambda t, s: [s[1], -c*s[0] - b*s[1]],\n"
        "    (0.0, 20.0), [1.0, 0.0],\n"
        ")\n"
        "view = go.Figure(go.Scatter(x=list(sol.t), y=list(sol.y[0]),\n"
        "                            mode='lines'))\n"
        "view.update_layout(title=f'x(t) for b={b}, c={c}',\n"
        "                   template='plotly_white')\n"
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
        context="Open sandbox for chapter 6 (second-order linear ODEs, "
                "x'' + b x' + c x = 0, characteristic equation, three "
                "cases). Helpers: delib.solve_system(F, t_span, s0) where "
                "F(t, s) returns [s1', s2'] and s = [x, v] — use "
                "[s[1], -c*s[0] - b*s[1]] for the oscillator. Plotly via "
                "go.Figure. Write complete runnable code; assign a Plotly "
                "figure to `view`.",
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

        - **Oscillation needs two numbers.** A 1-D flow
          $\dot x = f(x)$ can only drift monotonically — it cannot
          come back. The spring's state is (position, velocity), and
          tracking both is what makes bobbing describable.
        - **Force laws give second-order equations.** Newton's
          $m\ddot x = F$ plus the spring's $F = -kx$ gives
          $\ddot x = -(k/m)x$, with frequency $\omega = \sqrt{k/m}$
          falling out of a guess-and-check with $\cos(\omega t)$.
        - **The exponential guess is the method.** For
          $\ddot x + b\dot x + cx = 0$, substituting $x = e^{rt}$
          collapses the calculus into the **characteristic
          equation** $r^2 + br + c = 0$.
        - **Three signs of $b^2 - 4c$, three motions**: two real
          roots — pure decay; a repeated root — fastest clean decay
          (the door-closer borderline); a complex pair $a \pm
          i\beta$ — oscillation at frequency $\beta$ inside an
          $e^{at}$ envelope, courtesy of Euler's formula.
        - **Roots are a map.** Horizontal position in the complex
          plane = decay rate; vertical = oscillation frequency. Two
          **initial conditions** pin the two free constants — the
          position condition feeds $x$, the velocity condition feeds
          $\dot x$.

        **Next:** we kept the forcing at zero — nobody pushes the
        mass after launch. The next chapter turns on pushing:
        periodic forcing, the full damping story in physical units,
        and the phenomenon every engineer fears and every swing-set
        child exploits — **resonance**.
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
def _(api_field, delib, key_bridge):
    chatbox = delib.tutor_chat(
        api_field, key_bridge,
        "This is Chapter 6 of a differential-equations course: "
        "second-order linear ODEs with constant coefficients, built "
        "around the mass-on-a-spring story. Key ideas: oscillation is "
        "impossible for 1-D flows (state needs position AND velocity); "
        "m x'' = -k x from Newton + Hooke, frequency omega = sqrt(k/m); "
        "the exponential ansatz x = e^{rt} reduces x'' + b x' + c x = 0 "
        "to the characteristic equation r^2 + b r + c = 0; three cases "
        "by the discriminant b^2 - 4c (two real roots = pure decay, "
        "repeated root = critical/fastest clean decay, complex pair "
        "a ± i beta = oscillation at frequency beta inside envelope "
        "e^{at}, via Euler's formula); two initial conditions pin the "
        "two constants. Earlier chapters: slope fields (Ch 1), "
        "separable/linear (Ch 2), exact equations (Ch 3a/3b), numerical "
        "methods (Ch 4), 1-D fixed points and stability (Ch 5).",
        prompts=[
            "explain this chapter in a paragraph",
            "why does the repeated root need a factor of t?",
            "what happens if b is negative?",
        ],
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge):
    delib.tutor_sidebar(api_field, key_bridge, chatbox)
    return


if __name__ == "__main__":
    app.run()
