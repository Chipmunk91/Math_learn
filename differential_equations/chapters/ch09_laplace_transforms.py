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


# === Section 2 — The portal: defining the Laplace transform =======================
# TODO: build out next. Definition + linearity + table of canonical
# pairs (1, t, e^{at}, cos omega t, sin omega t). Each pair derived
# from the integral, not just asserted, so the table feels earned.
