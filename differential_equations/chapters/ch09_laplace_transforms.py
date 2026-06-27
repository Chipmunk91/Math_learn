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
        '<text x="595" y="90" text-anchor="middle" font-size="16" '
        ' fill="#16223a" font-family="serif">'
        ' an algebra equation for Y(s)</text>'
        '<text x="595" y="118" text-anchor="middle" font-size="12" '
        ' fill="#56636f" font-family="sans-serif" font-style="italic">'
        ' the y&#x2032;, y&#x2032;&#x2032; are gone</text>'

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
        '<text x="595" y="322" text-anchor="middle" font-size="22" '
        ' fill="#16223a" font-family="serif">'
        ' Y(s)</text>'
        '<text x="595" y="348" text-anchor="middle" font-size="12" '
        ' fill="#56636f" font-family="sans-serif" font-style="italic">'
        ' found by plain algebra</text>'

        # --- right arrow: divide ---
        '<line x1="595" y1="148" x2="595" y2="255" stroke="#16223a" '
        ' stroke-width="2" marker-end="url(#arr-dark)"/>'
        '<text x="610" y="200" text-anchor="start" font-size="13" '
        ' fill="#16223a" font-family="serif">solve for Y</text>'
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
            2. **Top arrow** is the Laplace transform $\mathcal{L}$ —
               the one new tool this chapter is about. For now treat
               it as a black box with a single, almost unreasonable
               gift: it takes an equation full of derivatives and
               hands back one that's pure **algebra**. *How* it pulls
               that off is the whole rest of the chapter; right here,
               just notice what it buys us.
            3. **Top-right** is the equation *after* the transform:
               no more $y'$, $y''$ — just algebra in $Y(s)$.
            4. **Right arrow** is exactly that payoff — solve for
               $Y(s)$ the way you'd solve any algebra problem.
            5. **Bottom-right** is the answer, still written in
               $s$-space.
            6. **Bottom arrow** is the inverse transform
               $\mathcal{L}^{-1}$ — carry $Y(s)$ back across the
               portal to recover the function $y(t)$.
            7. **Bottom-left** is the answer in $t$ — what we wanted
               all along.

            The dashed red curve is the route UC and VoP take — stay
            in $t$-space the whole way and fight the derivatives
            head-on. The whole bet of this chapter is that the long
            way round, *through* $s$-space, is perversely much
            shorter: the two $s$-space steps are easy algebra, and all
            the real work lives in the two **transform arrows**
            ($\mathcal{L}$ and $\mathcal{L}^{-1}$).

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
        """
    )
    return


# --- The two caveats, made concrete (convergence + starts at t=0) ----------
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Two things about that integral

        Both are worth a moment, because each turns out to be a
        *feature*, not a snag.

        **It has to converge — and that's a tug-of-war.** The integral
        runs all the way out to $t = \infty$, so to land on a finite
        number the integrand $e^{-st} f(t)$ has to **die away** as time
        goes on. The weight $e^{-st}$ (for positive $s$) is a
        *fader* — it drags everything toward zero — while $f(t)$ may be
        trying to grow. Convergence is just the question of who wins
        that race. Take $f(t) = e^{at}$: the integrand becomes
        $e^{-(s-a)t}$, which fades only when $s > a$. Push $s$ below
        $a$ and the function out-runs the fader, the area is infinite,
        and there's simply no transform. So a fast-growing $e^{5t}$
        needs $s > 5$; a tame $\sin t$ or a constant needs only
        $s > 0$, since the fader beats them on its own. The practical
        upshot: every function we'll meet has *some* threshold beyond
        which the transform exists — and for the ODE work ahead that
        threshold never actually bites, so we'll stop mentioning it.

        **It starts at $t = 0$, not $-\infty$ — the portal looks only
        forward.** That's on purpose. The problems we solve are
        *switch-it-on-and-watch* problems: release the mass, flip the
        battery, hit the pothole — all clocked from $t = 0$. Whatever
        happened earlier we either don't know or don't care about, and
        we don't have to: its *entire* leftover effect is summed up in
        the starting state $y(0)$ and $y'(0)$. Beginning the integral
        at $t = 0$ is what lets those two starting values enter the
        picture at all — keep them in mind; they'll have a role to
        play shortly. And a forcing that only switches on later, like a
        curb at $t = a$, still sits comfortably inside $[0, \infty)$.
        """
    )
    return


# --- What the portal does with f'(t): the derivative rule (sF(s) - f(0)) ---
# This is the cell that *delivers* the U-turn's promise. Send a
# derivative through the integral, integrate by parts once, watch
# d/dt collapse into multiplication by s (with a small f(0) memory).
# Kept under the KaTeX density threshold (3 displays + ~22 inline).
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### What does the portal do with $f'(t)$?

        We've defined what $F(s)$ is for a function $f(t)$. The next
        natural question — and it's the one this whole chapter turns
        on — is: **what comes out the other side if we send in the
        derivative $f'(t)$ instead?**

        Plug it straight into the integral, no clever tricks:

        $$
        \mathcal{L}\{f'(t)\} \;=\; \int_{0}^{\infty} e^{-st}\, f'(t)\, dt.
        $$

        The integrand is the weight $e^{-st}$ multiplied by $f'(t)$ —
        a product that practically begs for **integration by parts**.
        With $u = e^{-st}$ and $dv = f'(t)\, dt$ (so $du = -s\,e^{-st}\,dt$
        and $v = f(t)$):

        $$
        \mathcal{L}\{f'(t)\} \;=\; \bigl[\,e^{-st}\, f(t)\,\bigr]_{0}^{\infty} \;+\; s\!\int_{0}^{\infty} e^{-st}\, f(t)\, dt.
        $$

        Now read off the two pieces.

        - The **bracketed boundary term.** At $t = \infty$, the weight
          $e^{-st}$ kills $f(t)$ (we're in the convergence band — that's
          what the fine print bought us), so its value there is $0$. At
          $t = 0$, the weight is $1$, so its value there is $f(0)$. The
          whole bracket evaluates to $0 - f(0) = -f(0)$.
        - The **remaining integral** is exactly the Laplace transform
          of $f(t)$ — that is, $F(s)$ — multiplied out front by $s$.

        Put both together and the rule falls out:

        $$
        \boxed{\;\;\mathcal{L}\{f'(t)\} \;=\; s\,F(s) \;-\; f(0).\;\;}
        $$

        Stare at this for a second. **The derivative on the $t$ side
        became simple multiplication by $s$ on the $s$ side** — plus a
        small correction $f(0)$ that carries the initial condition
        along for the ride. The U-turn diagram promised "derivatives
        become algebra"; this is that promise written down for the
        first time. *Apply this rule once for each derivative in your
        ODE and the entire equation collapses to algebra in $Y(s)$* —
        which is precisely what the next move will do.
        """
    )
    return


# --- Second-derivative rule: L{f''} = s^2 F - s f(0) - f'(0) ----------------
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Once more, for $f''(t)$

        A second-order ODE carries a $y''$, so we need the rule for the
        *second* derivative too — and we get it for free, no new
        integral. Just apply the rule we already have to $f'$ in place
        of $f$. Writing $f'' = (f')'$:

        $$
        \mathcal{L}\{f''(t)\} \;=\; s\,\mathcal{L}\{f'(t)\} \;-\; f'(0).
        $$

        Then substitute $\mathcal{L}\{f'\} = sF(s) - f(0)$ from a moment
        ago:

        $$
        \boxed{\;\;\mathcal{L}\{f''(t)\} \;=\; s^2 F(s) \;-\; s\,f(0) \;-\; f'(0).\;\;}
        $$

        Same pattern: each derivative pulls down another factor of $s$,
        and each leaves behind a little memory of an initial value. Two
        derivatives, two leftovers $f(0)$ and $f'(0)$ — *exactly* the
        two numbers an initial-value problem hands you. The transform
        doesn't only turn calculus into algebra; it **swallows the
        initial conditions whole.**
        """
    )
    return


# --- Worked impulse example: y'' + y = delta(t), zero ICs ------------------
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### A worked example — the struck oscillator

        Enough rules; let's push a real equation through. Take the bare
        spring-mass from Chapter 6 and **strike it once** at $t = 0$ —
        the pothole from the intro, idealized to a single instantaneous
        unit kick:

        $$
        y'' + y \;=\; \delta(t), \qquad y(0) = 0,\;\; y'(0) = 0.
        $$

        The system sits at rest until, at $t = 0$, it gets one sharp
        tap and is left to ring. That tap is written $\delta(t)$ — the
        **Dirac impulse**. To send this equation through the portal we
        need $\mathcal{L}\{\delta\}$ — and for that we have to be
        honest about what $\delta$ actually *is*.
        """
    )
    return


# --- What delta is: bump-limit + sifting property, with a graphic ----------
@app.cell(hide_code=True)
def _(go, mo, np):
    from plotly.subplots import make_subplots as _msub

    _fig = _msub(
        rows=1, cols=2, horizontal_spacing=0.12,
        subplot_titles=(
            "δ(t): a unit-area bump — ever taller, ever narrower",
            "Sifting: δ samples e^(−st) at the one point t = 0",
        ),
    )

    # --- left: a family of unit-area bumps shrinking toward the spike ---
    _tt = np.linspace(-1.5, 1.5, 400)
    for _eps, _col in [(0.50, "#cdd6e0"), (0.28, "#7aa6ff"), (0.15, "#2a5d9c")]:
        _g = np.exp(-_tt**2 / (2*_eps**2)) / (_eps * np.sqrt(2*np.pi))
        _fig.add_trace(go.Scatter(x=_tt, y=_g, mode="lines",
            line=dict(color=_col, width=2), showlegend=False,
            hoverinfo="skip"), row=1, col=1)
    _fig.add_annotation(x=0.08, y=2.95, xref="x", yref="y", xanchor="left",
        text="height → ∞, area stays 1", showarrow=False,
        font=dict(size=11, color="#56636f"))

    # --- right: e^{-st} with the spike picking out its value at t=0 ---
    _s = 0.7
    _tr = np.linspace(-0.25, 4.0, 320)
    _w = np.exp(-_s * _tr)
    _fig.add_trace(go.Scatter(x=_tr, y=_w, mode="lines",
        line=dict(color="#2a5d9c", width=2.5), showlegend=False,
        hoverinfo="skip"), row=1, col=2)
    # the impulse: a red stem + arrowhead at t = 0
    _fig.add_trace(go.Scatter(x=[0, 0], y=[0, 1.2], mode="lines",
        line=dict(color="#c15a46", width=3), showlegend=False,
        hoverinfo="skip"), row=1, col=2)
    _fig.add_trace(go.Scatter(x=[0], y=[1.2], mode="markers",
        marker=dict(symbol="triangle-up", size=13, color="#c15a46"),
        showlegend=False, hoverinfo="skip"), row=1, col=2)
    # the sampled value sitting on the curve at (0, 1)
    _fig.add_trace(go.Scatter(x=[0], y=[1.0], mode="markers",
        marker=dict(size=10, color="#16223a"), showlegend=False,
        hoverinfo="skip"), row=1, col=2)
    _fig.add_annotation(x=0.18, y=1.34, xref="x2", yref="y2", xanchor="left",
        text="δ(t)", showarrow=False, font=dict(size=13, color="#c15a46"))
    _fig.add_annotation(x=0.22, y=0.98, xref="x2", yref="y2", xanchor="left",
        text="picks e^(−s·0) = 1", showarrow=False,
        font=dict(size=12, color="#16223a"))

    _fig.update_xaxes(title="t", range=[-1.5, 1.5], row=1, col=1)
    _fig.update_yaxes(range=[0, 3.6], row=1, col=1)
    _fig.update_xaxes(title="t", range=[-0.25, 4.0], row=1, col=2)
    _fig.update_yaxes(range=[0, 1.55], row=1, col=2)
    _fig.update_layout(
        height=330, template="plotly_white",
        margin=dict(l=10, r=10, t=46, b=10),
        paper_bgcolor="white", plot_bgcolor="white",
    )

    mo.vstack([
        mo.md(
            r"""
            ### Meet $\delta(t)$ — the unit impulse

            $\delta(t)$ isn't a function in the ordinary sense; no real
            function is infinite at a point. Picture it instead as the
            **limit of a unit-area bump that grows taller and narrower
            without end** (left). Every bump in the family has area
            exactly $1$; as the width shrinks to zero the height runs to
            infinity, but the *area stays pinned at $1$* — "a whole
            unit of push, delivered in an instant."

            The one property we ever use is what $\delta$ does *inside
            an integral*. Since the spike is zero everywhere except the
            single instant $t = a$, multiplying any smooth $g(t)$ by
            $\delta(t-a)$ and integrating just **plucks out the value
            $g(a)$**:

            $$
            \int_{-\infty}^{\infty} g(t)\,\delta(t-a)\,dt \;=\; g(a).
            $$

            That's the **sifting property** (right): the impulse is a
            *sampler*, reading off $g$ at the one point where the spike
            lives and ignoring it everywhere else.
            """
        ),
        _fig,
        mo.md(
            r"""
            Now the transform is no sleight of hand. The weight
            $e^{-st}$ plays the role of $g$, and our spike sits at
            $t = 0$, so sifting simply reads the weight off at that one
            instant:

            $$
            \mathcal{L}\{\delta(t)\} \;=\; \int_{0}^{\infty} e^{-st}\,\delta(t)\,dt \;=\; e^{-s\cdot 0} \;=\; 1.
            $$

            An impulse transforms to the constant $1$ — it samples
            $e^{-st}$ at $t = 0$, and $e^{0} = 1$. *That's* why the
            collapse in the next cell is so clean: the whole right-hand
            side of the ODE becomes just $1$.
            """
        ),
    ])
    return


# --- The collapse: transform every term, ICs vanish, divide ----------------
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Watch it collapse to algebra

        Now transform the equation term by term, using the three rules
        we just collected — $\mathcal{L}\{y''\} = s^2 Y - s\,y(0) - y'(0)$,
        $\mathcal{L}\{y\} = Y$, and $\mathcal{L}\{\delta\} = 1$:

        $$
        \underbrace{\bigl(s^2 Y - s\,y(0) - y'(0)\bigr)}_{\mathcal{L}\{y''\}} \;+\; \underbrace{Y}_{\mathcal{L}\{y\}} \;=\; \underbrace{1}_{\mathcal{L}\{\delta\}}.
        $$

        Both initial conditions are zero, so the $s\,y(0)$ and $y'(0)$
        terms simply drop. The differential equation — derivatives,
        impulse, and all — has become this:

        $$
        s^2 Y + Y \;=\; 1.
        $$

        Not a derivative in sight. It's a one-line algebra problem in
        $Y$, no harder than $5x = 1$: factor out $Y$ and divide.

        $$
        (s^2 + 1)\,Y \;=\; 1 \quad\Longrightarrow\quad \boxed{\;Y(s) \;=\; \frac{1}{s^2 + 1}.\;}
        $$
        """
    )
    return


# --- Step: what the inverse transform is, and how to apply it to Y(s) ------
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Going back — the inverse transform

        We have $Y(s) = \dfrac{1}{s^2 + 1}$: the answer, but written in
        $s$-space. It's the image sitting on the far side of the
        portal. To finish the job we have to carry it **back** to
        $t$-space and recover the actual function $y(t)$.

        That return trip is the **inverse Laplace transform**, written
        $\mathcal{L}^{-1}$:

        $$
        y(t) \;=\; \mathcal{L}^{-1}\{\,Y(s)\,\}.
        $$

        One trap to clear first: the inverse is **not** the forward
        transform run a second time. Feeding $Y(s)$ back through
        $\mathcal{L}$ gives $\int_0^\infty e^{-ps}Y(s)\,ds$ — just
        another forward transform, a different function of a new
        variable, not our $y(t)$. $\mathcal{L}^{-1}$ is its own
        operation. (It does have an explicit formula — a mirror-image
        integral that runs *up a vertical line in the complex plane* —
        but we will not need it even once.) Two simpler facts make it
        usable.

        **It is well-defined.** The forward transform is *one-to-one* —
        two different functions can't share the same image. (That's
        what made "the answer, in $s$-space" a meaningful phrase in the
        first place.) So there is exactly **one** $y(t)$ hiding behind
        $Y(s)$, and $\mathcal{L}^{-1}$ is just the name for "the
        function it came from."

        **We invert by recognition.** Rather than evaluate any formula,
        we read the forward dictionary **backwards**: the forward
        direction pairs each $f(t)$ with its $F(s)$; to invert, we hunt
        for a function whose forward transform is the $F(s)$ in front of
        us. By uniqueness, the moment we find one, it *is* the answer.

        So inverting our result collapses to a single, concrete
        question:

        > Which function of $t$ has Laplace transform
        > $\dfrac{1}{s^2 + 1}$?

        Pin that down and $y(t)$ falls out. That's the next step.
        """
    )
    return


# --- Build the pair sin t <-> 1/(s^2+1) via the f'' rule (no new integral) -
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Which function transforms to $\dfrac{1}{s^2+1}$?

        We could grind the forward integral
        $\int_0^\infty e^{-st} f(t)\,dt$ for candidate after candidate
        until one lands on $1/(s^2+1)$. But we just built a tool that
        shortcuts the search — the second-derivative rule — so let's use
        it.

        The denominator $s^2 + 1$ hints at an oscillation, so try
        $f(t) = \sin t$. It has $f(0) = 0$, $f'(0) = 1$, and the
        defining feature that it's the negative of its own second
        derivative, $f'' = -\sin t = -f$. Run that last fact through the
        rule from earlier, $\mathcal{L}\{f''\} = s^2 F - s f(0) - f'(0)$:

        $$
        \mathcal{L}\{f''\} \;=\; s^2 F - s\cdot 0 - 1 \;=\; s^2 F - 1, \qquad\text{but also}\qquad \mathcal{L}\{f''\} \;=\; \mathcal{L}\{-f\} \;=\; -F.
        $$

        Those two expressions are the same quantity, so set them equal
        and solve for $F$ — pure algebra again:

        $$
        s^2 F - 1 \;=\; -F \quad\Longrightarrow\quad (s^2 + 1)\,F \;=\; 1 \quad\Longrightarrow\quad \boxed{\;\mathcal{L}\{\sin t\} \;=\; \frac{1}{s^2 + 1}.\;}
        $$

        That's the entry we needed. The function whose transform is
        $1/(s^2+1)$ is $\sin t$ — and by the uniqueness from a moment
        ago, it's the *only* one. So we may read the dictionary
        backwards with confidence:

        $$
        \mathcal{L}^{-1}\!\left\{\frac{1}{s^2+1}\right\} = \sin t \quad\Longrightarrow\quad y(t) = \sin t.
        $$

        The struck oscillator's answer is $y(t) = \sin t$: hit it once
        and it rings — a clean unit oscillation at its natural
        frequency, the **impulse response.** We started with a
        differential equation and a hammer-blow forcing, and recovered
        the motion with nothing harder than the algebra of $s$.
        """
    )
    return


if __name__ == "__main__":
    app.run()
