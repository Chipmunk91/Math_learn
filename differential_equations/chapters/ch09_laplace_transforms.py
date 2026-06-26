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
    # §6 after we have the machinery to do it justice.
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


# === Section 2 — The portal: why bother, then what it is ==========================
# Rewritten to lead with the *usefulness* (escape the y', y'' guess
# game / decoding gauntlet), show the canonical U-turn diagram, and
# only then drop the integral definition -- so the definition lands
# as the answer to a question rather than as a cold formula. Each
# table-entry derivation stays in its own cell to respect the KaTeX
# density threshold.

@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## The portal — why bother?

        Every method we've used for second-order ODEs has fought the
        same enemy: **the derivatives themselves.** Undetermined
        coefficients is a *guess game* — pick a trial $y_p$,
        differentiate it (twice), substitute it into
        $y'' + 2\gamma y' + \omega_0^2 y$, and see whether the
        operator spits the right thing out; if not, guess again.
        Variation of parameters is more honest but more pesky:
        Wronskians, integration by parts, piecewise glue at switch
        times. Both methods *deal with derivatives by computing them*.

        Wouldn't it be nicer if we could *avoid* taking derivatives
        at all? Send the whole equation off to a place where
        "derivative" is just "multiply." Solve the much easier
        equation there. Then bring the answer home.

        That is the entire idea of the Laplace transform — and the
        geometry of the trick fits on a single diagram.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # The U-turn diagram. SVG (light theme, ~760x380 viewBox); arrows
    # carry the LHS->RHS movement of the chapter, dashed red curve
    # marks the direct (hard) path that UC/VoP take.
    _svg = mo.Html(
        '<svg viewBox="0 0 760 400" xmlns="http://www.w3.org/2000/svg" '
        'style="max-width:760px;display:block;margin:0 auto;height:auto">'
        '<defs>'
        '<marker id="arr-dark" viewBox="0 0 10 10" refX="9" refY="5" '
        ' markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#16223a"/></marker>'
        '<marker id="arr-warn" viewBox="0 0 10 10" refX="9" refY="5" '
        ' markerWidth="6" markerHeight="6" orient="auto">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#c15a46"/></marker>'
        '</defs>'

        # --- top-left box: ODE in t ---
        '<rect x="30" y="30" width="270" height="110" rx="10" '
        ' fill="#fff4ec" stroke="#c15a46" stroke-width="2"/>'
        '<text x="165" y="55" text-anchor="middle" font-size="12" '
        ' fill="#8a96a5" font-family="sans-serif">t-space</text>'
        '<text x="165" y="88" text-anchor="middle" font-size="18" '
        ' fill="#16223a" font-family="serif">'
        ' y&#x2032;&#x2032; + 2&#x03B3; y&#x2032; + &#x03C9;&#x2080;&#xB2; y = g(t)</text>'
        '<text x="165" y="118" text-anchor="middle" font-size="12" '
        ' fill="#56636f" font-family="sans-serif" font-style="italic">'
        ' an ODE -- derivatives everywhere</text>'

        # --- top-right box: algebraic eq in s ---
        '<rect x="460" y="30" width="270" height="110" rx="10" '
        ' fill="#eef7fb" stroke="#2a5d9c" stroke-width="2"/>'
        '<text x="595" y="55" text-anchor="middle" font-size="12" '
        ' fill="#8a96a5" font-family="sans-serif">s-space</text>'
        '<text x="595" y="88" text-anchor="middle" font-size="18" '
        ' fill="#16223a" font-family="serif">'
        ' (s&#xB2; + 2&#x03B3; s + &#x03C9;&#x2080;&#xB2;) Y = G(s)</text>'
        '<text x="595" y="118" text-anchor="middle" font-size="12" '
        ' fill="#56636f" font-family="sans-serif" font-style="italic">'
        ' an algebraic equation</text>'

        # --- top arrow: transform L ---
        '<line x1="305" y1="85" x2="455" y2="85" stroke="#16223a" '
        ' stroke-width="2" marker-end="url(#arr-dark)"/>'
        '<text x="380" y="72" text-anchor="middle" font-size="14" '
        ' fill="#16223a" font-family="serif">'
        ' &#x2112;  (transform)</text>'
        '<text x="380" y="105" text-anchor="middle" font-size="11" '
        ' fill="#0f8a6a" font-family="sans-serif">'
        ' one integral &#xB7; then look up</text>'

        # --- bottom-right box: solved Y(s) ---
        '<rect x="460" y="260" width="270" height="110" rx="10" '
        ' fill="#eef7fb" stroke="#2a5d9c" stroke-width="2"/>'
        '<text x="595" y="285" text-anchor="middle" font-size="12" '
        ' fill="#8a96a5" font-family="sans-serif">s-space (solved)</text>'
        '<text x="595" y="318" text-anchor="middle" font-size="18" '
        ' fill="#16223a" font-family="serif">'
        ' Y(s) = G(s) / (s&#xB2; + 2&#x03B3; s + &#x03C9;&#x2080;&#xB2;)</text>'
        '<text x="595" y="348" text-anchor="middle" font-size="12" '
        ' fill="#56636f" font-family="sans-serif" font-style="italic">'
        ' a rational function in s</text>'

        # --- right arrow: divide ---
        '<line x1="595" y1="148" x2="595" y2="255" stroke="#16223a" '
        ' stroke-width="2" marker-end="url(#arr-dark)"/>'
        '<text x="610" y="200" text-anchor="start" font-size="14" '
        ' fill="#16223a" font-family="serif">divide</text>'
        '<text x="610" y="218" text-anchor="start" font-size="11" '
        ' fill="#0f8a6a" font-family="sans-serif">just algebra</text>'

        # --- bottom-left box: y(t) ---
        '<rect x="30" y="260" width="270" height="110" rx="10" '
        ' fill="#fff4ec" stroke="#c15a46" stroke-width="2"/>'
        '<text x="165" y="285" text-anchor="middle" font-size="12" '
        ' fill="#8a96a5" font-family="sans-serif">t-space (solved)</text>'
        '<text x="165" y="320" text-anchor="middle" font-size="20" '
        ' fill="#16223a" font-family="serif">y(t)</text>'
        '<text x="165" y="348" text-anchor="middle" font-size="12" '
        ' fill="#56636f" font-family="sans-serif" font-style="italic">'
        ' the answer we wanted</text>'

        # --- bottom arrow: inverse transform ---
        '<line x1="455" y1="315" x2="305" y2="315" stroke="#16223a" '
        ' stroke-width="2" marker-end="url(#arr-dark)"/>'
        '<text x="380" y="303" text-anchor="middle" font-size="14" '
        ' fill="#16223a" font-family="serif">'
        ' &#x2112;&#x207B;&#xB9;  (inverse)</text>'
        '<text x="380" y="335" text-anchor="middle" font-size="11" '
        ' fill="#0f8a6a" font-family="sans-serif">'
        ' split &amp; look up each piece</text>'

        # --- the hard path: dashed red curve, top-left -> bottom-left ---
        '<path d="M 100 148 Q 0 205 100 252" '
        ' stroke="#c15a46" stroke-width="2" stroke-dasharray="6 4" '
        ' fill="none" marker-end="url(#arr-warn)"/>'
        '<text x="18" y="195" font-size="12" fill="#c15a46" '
        ' font-family="sans-serif" font-style="italic">UC / VoP</text>'
        '<text x="18" y="212" font-size="12" fill="#c15a46" '
        ' font-family="sans-serif" font-style="italic">(the hard way)</text>'

        '</svg>'
    )

    mo.vstack([
        mo.md(r"""### The U-turn"""),
        _svg,
        mo.md(
            r"""
            Read it counter-clockwise from the top-left:

            1. **Top-left** is where we live: an ODE in $t$,
               derivatives everywhere.
            2. **Top arrow** is the Laplace transform $\mathcal{L}$.
               It rewrites every derivative as multiplication by $s$
               — the operator $\tfrac{d}{dt}$ literally becomes a
               polynomial in $s$.
            3. **Top-right** is the equation *after* the transform:
               algebraic, no calculus.
            4. **Right arrow** is simple algebra — divide both sides
               by the polynomial in $s$.
            5. **Bottom-right** is the answer, written in $s$-space.
            6. **Bottom arrow** is the inverse transform
               $\mathcal{L}^{-1}$ — split $Y(s)$ into pieces our
               table knows, look each one up.
            7. **Bottom-left** is the answer in $t$ — what we wanted
               all along.

            The dashed red curve is the route UC and VoP take — stay
            in $t$-space the whole way and fight the derivatives
            head-on. The point of Laplace is that the long way round,
            through $s$-space, is perversely much shorter. The two
            $s$-space steps are easy; only the two **transform
            arrows** ($\mathcal{L}$ and $\mathcal{L}^{-1}$) carry any
            real work — and once we have the table, even those become
            lookups.

            So: what *is* this transform $\mathcal{L}$?
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### What the portal actually is

        It's an integral. Pick a function $f(t)$ on $t \ge 0$,
        multiply it by an exponential weight $e^{-st}$, and integrate
        over the whole future:

        $$
        \boxed{\;\; F(s) \;=\; \mathcal{L}\{f(t)\} \;=\; \int_{0}^{\infty} e^{-st}\, f(t)\, dt. \;\;}
        $$

        For each value of $s$, the integral spits out one number —
        so $F(s)$ is a brand-new function, this time of $s$ instead
        of $t$. That $F(s)$ is the image of $f(t)$ on the other side
        of the portal.

        Two pieces of fine print, and we move on. **First**, $s$ has
        to be large enough that the integral converges; for $f(t) =
        e^{at}$, for example, the weight $e^{-st}$ only wins if
        $s > a$. We won't fuss about it — for every function we'll
        meet there's some half-plane $\mathrm{Re}(s) > s_0$ where the
        integral converges, and we just live there. **Second**, the
        lower limit is $0$, not $-\infty$. The portal sees only the
        *future*. That's not a flaw — it's exactly why Laplace is the
        right tool for problems that **start at $t = 0$** with initial
        conditions, and for forcings (like a curb at $t = a$) that
        *switch on* somewhere along the way.
        """
    )
    return


if __name__ == "__main__":
    app.run()
