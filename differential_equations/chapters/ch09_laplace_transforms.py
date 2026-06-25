import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import plotly.graph_objects as go
    import sympy as sp

    import delib
    return delib, go, mo, np, sp


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Chapter 9 — Laplace transforms

        **A portal to where derivatives are just multiplication.**

        By the end of this chapter you should be able to:

        - Compute the **Laplace transform** of the standard pieces
          (constants, polynomials, exponentials, sinusoids) and use
          linearity to combine them.
        - Apply the **derivative rule**
          $\mathcal{L}\{y'\} = sY - y(0)$ to turn a constant-coefficient
          ODE into a single *algebraic* equation for $Y(s)$ — with the
          initial conditions baked in automatically.
        - Read the **poles** of $Y(s)$ as the characteristic roots of
          Chapter 6, and recover the time-domain response by
          **partial-fraction** inversion.
        - Handle **switched** inputs (Heaviside $u(t-a)$) and
          **impulse** inputs (Dirac $\delta(t-a)$) using the t-shift
          rule — the inputs UC and VoP can't reach cleanly.
        - Pick the right tool for the job: characteristic equation
          for plain homogeneous; UC/VoP for smooth forcings; **Laplace
          for switched, impulsive, or initial-condition-heavy
          problems.**
        """
    )
    return


# === Section 1 — Hook: the pothole and the curb ===================================
# The chassis from Ch7/Ch8 is back, but the forcings are now the kinds
# UC and VoP genuinely cannot touch cleanly: a single sharp jolt (a
# pothole, modelled by Dirac delta) and a sudden permanent step (a
# curb, modelled by Heaviside). Sets up the chapter's reason for being.
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Same chassis, sharper road

        We're back at the suspension from Chapters 7 and 8:

        $$
        m\,\ddot x \;+\; c\,\dot x \;+\; k\,x \;=\; g(t),
        $$

        same mass, same damper, same spring. What's new is the road.
        Up to now $g(t)$ has been *smooth* — a clean cosine, an
        exponential, at worst a $\tan x$ or $\sec x$. Functions you
        could differentiate without flinching.

        Real roads aren't like that. Two profiles haunt every
        suspension engineer, and neither of them is smooth:

        - **A pothole.** The wheel drops and rises back in a fraction
          of a second. From the chassis's point of view it's a
          single, instantaneous **jolt** — energy delivered all at
          once, the road back to normal before you've reacted.
        - **A curb.** You drive up onto a raised section. The road
          doesn't return; it *stays* lifted. From now on the
          equilibrium has shifted — a **sudden, permanent step**.

        These are exactly the forcings yesterday's methods don't
        handle gracefully — and that's the whole reason this chapter
        exists.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Same chassis as Ch7/Ch8's road_test; new presets land the two
    # specific forcings -- a periodic impulse train (POTHOLE) and a
    # smoothed step staircase (CURB) -- that motivate this chapter.
    delib.pothole_curb()
    return


@app.cell(hide_code=True)
def _(mo):
    # Why the inherited toolbox stumbles on pothole/curb -- motivates
    # the portal. Kept short; the *real* technical comparison lives in
    # §5 after we have the machinery to do it justice.
    mo.md(
        r"""
        ### Why our old tools struggle here

        **Undetermined coefficients** lives on a tiny menu: exponentials,
        sinusoids, polynomials, and sums of them. There is no row for
        "an instantaneous spike," and no row for "a function that's $0$
        before $t = a$ and $1$ after." The trial-form game simply has
        no card to play.

        **Variation of parameters** technically *can* survive a step
        forcing — you split the time axis at $t = a$ and run the
        integrals on each piece — but the answer comes out as a
        Frankensteined union of cases, glued at $t = a$ with hand-checked
        continuity conditions. Worse, *initial conditions* live
        separately from the method; you solve for $y_p$, then
        re-solve for $c_1, c_2$ from $y(0), y'(0)$ in a second pass.
        Possible, ugly, easy to get wrong.

        What we want is a single tool that takes
        **(equation, initial conditions, switched/impulsive forcing)**
        as one bundle and returns the answer in one pass. That tool
        exists, and it's been waiting since the 1780s.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # The portal promise -- the central metaphor for the whole chapter.
    # Short, vivid, and forward-pointing; the actual definition arrives
    # in §2.
    mo.md(
        r"""
        ### The plan — step through a portal

        Here's the idea, in one sentence. We're going to build a
        **portal** out of the time axis.

        Call the world we've lived in so far **$t$-space**: the
        variable is time, the operations are derivatives and integrals,
        and the equation $m\ddot x + c\dot x + k x = g(t)$ is a
        statement *in* $t$-space. Through the portal lies a different
        world — call it **$s$-space** — where every function $f(t)$
        has a counterpart $F(s)$, every initial condition has a
        place to live, and — this is the magic —

        > **$t$-space differentiation becomes $s$-space multiplication.**

        On the other side, our ODE collapses into a single *algebraic*
        equation for $X(s)$ — no calculus left. We solve that
        equation (high-school algebra, plus a partial-fraction
        decomposition), then step **back** through the inverse portal
        and read off $x(t)$.

        Pothole and curb, the two forcings that broke our old tools,
        turn out to have the simplest possible $s$-space images. The
        portal was built for them.

        Time to walk through.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Companion-video callout. 3Blue1Brown's Laplace video tells the
    # same forced-oscillator/poles story; we borrow its s-plane
    # landscape visual in §2 and §4, credited there too.
    mo.md(
        r"""
        > **📺 Companion video.** This chapter pairs beautifully with
        > 3Blue1Brown's
        > [*Why Laplace transforms are so useful*](https://www.youtube.com/watch?v=FE-hM1kRK4Y)
        > (Grant Sanderson). It builds the very same story — the forced
        > oscillator, the transform, and the **poles** that decide its
        > behaviour — with his signature animation. We borrow one of its
        > visual ideas (the $s$-plane landscape) in §2 and §4, with
        > thanks.
        """
    )
    return


# === Section 2 — The portal: defining the Laplace transform =======================
# Cross from t-space to s-space. Definition + half-line caveat, then
# derive 4 canonical pairs from the integral so the table feels
# earned (not memorised). Each derivation gets its own cell to stay
# under the KaTeX density threshold.

@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## The portal — defining $\mathcal{L}$

        Pick a function $f(t)$ on $t \ge 0$. Multiply it by an
        exponential weight $e^{-st}$, integrate over the whole future,
        and call the result $F(s)$:

        $$
        \boxed{\;\; F(s) \;=\; \mathcal{L}\{f(t)\} \;=\; \int_{0}^{\infty} e^{-st}\, f(t)\, dt. \;\;}
        $$

        That's the entire portal. For each value of $s$, the integral
        spits out one number — so $F(s)$ is a brand-new function, this
        time of $s$ instead of $t$. We say $F(s)$ is the **Laplace
        transform** of $f(t)$, and we'll picture it as $f$'s image on
        the other side of the door.

        Two pieces of fine print, and we move on. **First**, $s$ has
        to be large enough that the integral converges; for $f(t) =
        e^{at}$, for example, the weight $e^{-st}$ only wins if
        $s > a$. We won't fuss about it — for every function we'll meet
        there's some half-plane $\mathrm{Re}(s) > s_0$ where the
        integral converges, and we just live there. **Second**, the
        lower limit is $0$, not $-\infty$. The portal sees only the
        *future*. That's not a flaw — it's why Laplace is the right
        tool for problems that **start at $t = 0$** with initial
        conditions, and for forcings (like a curb at $t = a$) that
        *switch on* somewhere along the way.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### The first two pairs — constants and exponentials

        Two transforms do all the work in this chapter, and both fall
        out of the integral with one line of calculus.

        **A constant.** For $f(t) = 1$:

        $$
        \mathcal{L}\{1\} \;=\; \int_0^{\infty} e^{-st}\, dt \;=\; \left[-\tfrac{1}{s} e^{-st}\right]_0^{\infty} \;=\; \frac{1}{s} \qquad (s > 0).
        $$

        A function that is identically $1$ in $t$-space is just
        $1/s$ in $s$-space. Tiny, but exactly the image we'll need
        when we transform an initial condition.

        **An exponential.** For $f(t) = e^{at}$, the two exponentials
        merge:

        $$
        \mathcal{L}\{e^{at}\} \;=\; \int_0^{\infty} e^{-(s-a)t}\, dt \;=\; \frac{1}{s - a} \qquad (s > a).
        $$

        Look at what just happened. In $t$-space, $e^{at}$ is the
        function that "remembers itself" under differentiation
        ($\frac{d}{dt} e^{at} = a\,e^{at}$). In $s$-space, it became
        the **simplest possible** rational function — a single pole
        at $s = a$. That correspondence is the chapter's load-bearing
        beam. Hold onto it.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Sine and cosine — one Euler-trick away

        The third pair we'll need over and over is $\sin$ and $\cos$.
        Instead of integrating by parts twice, run a complex
        $e^{i\omega t}$ through the exponential rule from above:

        $$
        \mathcal{L}\{e^{i\omega t}\} \;=\; \frac{1}{s - i\omega} \;=\; \frac{s + i\omega}{s^2 + \omega^2}.
        $$

        But $e^{i\omega t} = \cos\omega t + i\sin\omega t$, and
        $\mathcal{L}$ is **linear** — it distributes over the real
        and imaginary parts. So reading off real and imaginary
        pieces:

        $$
        \mathcal{L}\{\cos\omega t\} \;=\; \frac{s}{s^2 + \omega^2}, \qquad \mathcal{L}\{\sin\omega t\} \;=\; \frac{\omega}{s^2 + \omega^2}.
        $$

        Note where those $s$-images live: both have denominators
        $s^2 + \omega^2$ — the very same polynomial that's the
        **characteristic polynomial** of the undamped oscillator
        $\ddot x + \omega^2 x = 0$ from Chapter 6. The portal already
        knows the answer. We just don't quite see *why* yet — that
        comes in §3.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### The starter dictionary

        Five entries cover almost every example in this chapter
        (and a sixth is one differentiation away). The first three
        are the ones we just derived; the others fall out of exactly
        the same machinery if you want to do them yourself.

        | $f(t)$ | $F(s) = \mathcal{L}\{f(t)\}$ | converges for |
        |---|---|---|
        | $1$ | $\displaystyle \frac{1}{s}$ | $s > 0$ |
        | $e^{at}$ | $\displaystyle \frac{1}{s - a}$ | $s > a$ |
        | $\cos\omega t$ | $\displaystyle \frac{s}{s^2 + \omega^2}$ | $s > 0$ |
        | $\sin\omega t$ | $\displaystyle \frac{\omega}{s^2 + \omega^2}$ | $s > 0$ |
        | $t$ | $\displaystyle \frac{1}{s^2}$ | $s > 0$ |
        | $t^n$ | $\displaystyle \frac{n!}{s^{n+1}}$ | $s > 0$ |

        And one structural rule we'll lean on without saying:
        **linearity.** Because the integral is linear,

        $$
        \mathcal{L}\{a\,f(t) + b\,g(t)\} \;=\; a\,F(s) + b\,G(s).
        $$

        Combinations on the $t$ side become the *same* combinations on
        the $s$ side — no surprises. Six pairs and one rule. With that
        much in hand, you can already transform any sum of
        polynomials, exponentials, and sinusoids — the whole UC table
        from Chapter 8, basically.

        What you *can't* yet do is transform an ODE. For that we need
        one more piece — the derivative rule, $\mathcal{L}\{y'\}$ —
        and it's the rule that gives the portal its whole point.
        """
    )
    return


# === Section 2.5 — Borrowed visualization: the s-plane landscape ===================
# Credit: 3Blue1Brown, "Why Laplace transforms are so useful"
# (https://www.youtube.com/watch?v=FE-hM1kRK4Y). The idea borrowed is
# picturing |F(s)| as a surface over the complex s-plane, where poles
# rise as towers and a pole's *location* encodes the time-behaviour.
# Honest to §2 content: we plot the sin/cos transform 1/(s^2+omega^2),
# whose two poles sit on the imaginary axis. §4 reuses the technique
# on the chassis transfer function with an interactive damping knob.
@app.cell(hide_code=True)
def _(go, mo, np):
    _omega = 1.5
    _re = np.linspace(-2.0, 2.0, 130)
    _im = np.linspace(-3.6, 3.6, 200)
    _RE, _IM = np.meshgrid(_re, _im)
    _S = _RE + 1j * _IM
    _mag = 1.0 / np.abs(_S**2 + _omega**2)
    _Z = np.clip(_mag, 0, 5.0)

    _fig = go.Figure(data=[go.Surface(
        x=_re, y=_im, z=_Z,
        colorscale="Viridis", showscale=False, opacity=0.98,
        contours={"z": {"show": True, "usecolormap": True, "width": 1}},
    )])
    _fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[_omega, -_omega], z=[5.0, 5.0],
        mode="markers+text",
        marker=dict(size=4, color="#c15a46", symbol="diamond"),
        text=["pole at s = +iω", "pole at s = −iω"],
        textposition="top center",
        textfont=dict(color="#c15a46", size=11), showlegend=False,
    ))
    _fig.update_layout(
        height=460, margin=dict(l=0, r=0, t=10, b=0),
        scene=dict(
            xaxis_title="Re(s)", yaxis_title="Im(s)", zaxis_title="|F(s)|",
            camera=dict(eye=dict(x=1.6, y=1.5, z=1.05)),
            aspectratio=dict(x=1, y=1.4, z=0.8),
        ),
        template="plotly_white",
    )

    mo.vstack([
        mo.md(
            r"""
            ### A peek through the portal — the $s$-plane landscape

            Here's a way to *see* what the portal produces, borrowed
            (with thanks) from 3Blue1Brown's
            [*Why Laplace transforms are so useful*](https://www.youtube.com/watch?v=FE-hM1kRK4Y).
            Every entry in our dictionary is a **rational function of
            $s$**, and a rational function has a landscape: plot the
            height $|F(s)|$ over the complex $s$-plane — real part one
            way, imaginary part the other — and wherever the
            denominator hits zero the surface shoots up into a
            **tower**. Those towers are the **poles**.

            Below is the landscape of $F(s) = \dfrac{1}{s^2 + \omega^2}$
            — the transform of $\cos\omega t$ and $\sin\omega t$, with
            $\omega = 1.5$. Drag to orbit it.
            """
        ),
        _fig,
        mo.md(
            r"""
            Read the towers' **addresses**, not just their heights.
            They stand at $s = \pm i\omega$ — squarely on the
            **imaginary axis**. That location *is* the message: a pole
            on the imaginary axis means a response that **oscillates
            forever and never decays** — exactly what undamped
            $\sin\omega t$ does.

            Slide a pole **left** of the axis (a negative real part)
            and you'd be looking at a *decaying* oscillation; push it
            onto the **real axis** and you'd get pure exponential
            growth or decay — the $e^{at}$ entry, whose single tower
            sits at $s = a$. A pole's position in the plane encodes the
            behaviour in time. That correspondence is what makes the
            whole method tick — and in §4 we'll turn the damping knob
            on our car and **watch its poles migrate** across this very
            plane: Chapter 6's three-case fork, redrawn in $s$.
            """
        ),
    ])
    return


# === Section 3 — Why the portal works on ODEs: d/dt → s ===========================
# TODO: derive L{y'} = sY - y(0) and L{y''} = s²Y - s y(0) - y'(0)
# from integration by parts. Land the central trick: t-derivatives
# become s-multiplications, with the initial conditions automatically
# baked in. Then run one tiny worked example end-to-end.
