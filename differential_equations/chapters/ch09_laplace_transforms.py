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
        the starting state $y(0)$ and $y'(0)$. Those are exactly the
        two numbers the derivative rule pulled in a moment ago — the
        transform was built to take them as input. And a forcing that
        only switches on later, like a curb at $t = a$, still sits
        comfortably inside $[0, \infty)$.
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

        That $\delta(t)$ is the **Dirac impulse** — picture an
        infinitely tall, infinitely thin spike at $t = 0$ whose total
        area is exactly $1$: a full unit of "push" delivered in zero
        time. Its transform is the simplest object in the whole
        subject. Drop it into the integral and the spike samples the
        weight at the single instant $t = 0$:

        $$
        \mathcal{L}\{\delta(t)\} \;=\; \int_0^{\infty} e^{-st}\,\delta(t)\,dt \;=\; e^{-s\cdot 0} \;=\; 1.
        $$

        An impulse transforms to the constant $1$. That clean
        right-hand side is exactly why the impulse is the friendliest
        forcing to start with.
        """
    )
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


# --- How it turned out: invert (gesture), tie denominator to Ch6 -----------
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### How it turned out

        That was the *entire* solve. All the calculus got spent inside
        the transform rules; what remained in $s$-space was a single
        division. Compare that to undetermined coefficients or
        variation of parameters trying to wrestle a delta function in
        $t$-space — there isn't even a contest.

        One step is still owed: carrying $Y(s) = \dfrac{1}{s^2 + 1}$
        **back** across the portal to recover $y(t)$. That's the
        inverse transform, and we'll build the dictionary for it next.
        But here's the punchline in advance — $\dfrac{1}{s^2 + 1}$ is
        the transform of $\sin t$, so the struck oscillator answers
        with

        $$
        y(t) \;=\; \sin t.
        $$

        Hit it once and it rings: a clean unit-amplitude oscillation at
        its natural frequency — the **impulse response**. And notice
        the denominator we divided by, $s^2 + 1$. That's no
        coincidence: it's exactly the characteristic polynomial of
        $y'' + y = 0$ from Chapter 6. The shape of the answer was
        hiding in the denominator all along — a thread we'll pull hard
        on later.
        """
    )
    return


# --- Why poles? The probe/resonance argument on the worked example --------
# The user-requested explanation: pole addresses aren't decoration --
# each one is the complex rate of a building block of y(t). Anchored
# on the specific example we just solved (sin t, poles at s = +/- i)
# so the mechanism is shown, not asserted.
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Why does $Y(s)$ blow up exactly at $s = \pm i$?

        We landed on $Y(s) = 1/(s^2+1)$ — finite everywhere in the
        $s$-plane except at the two points $s = \pm i$, where the
        denominator vanishes. Why those *specific* addresses?

        The honest answer is **resonance with a probe.** Look at the
        definition one more time:

        $$
        Y(s) \;=\; \int_0^\infty e^{-st}\, y(t)\, dt.
        $$

        Think of $e^{-st}$ as a **tunable probe** you can slide
        anywhere in the complex plane. Writing $s = -\gamma + i\omega$
        for a general point, the probe both decays (rate $\gamma$) and
        oscillates (frequency $\omega$). The integral asks: integrated
        over all of time, *how much does $y(t)$ line up with this
        particular probe?*

        The integral can only blow up when the probe **exactly
        cancels** an ingredient of $y(t)$, so the integrand never
        decays and the area piles up forever. Try it on our answer.
        By Euler,

        $$
        \sin t \;=\; \frac{e^{it} - e^{-it}}{2i}.
        $$

        So $y(t)$ is secretly two complex exponentials, with rates
        $+i$ and $-i$. Probe the first one at $s = +i$:

        $$
        e^{-st}\cdot e^{it}\,\Big|_{s = i} \;=\; e^{-it}\cdot e^{it} \;=\; 1.
        $$

        The probe undid the mode exactly. Integrand $\equiv 1$, area
        $= \infty$. **That blow-up is the pole at $s = +i$.** Same
        story at $s = -i$ for the other mode.

        So pole addresses aren't arbitrary. Each one is the **complex
        rate of a building block of $y(t)$** — its **real part** is
        that mode's decay rate, its **imaginary part** is that mode's
        frequency. For our example: real parts $0$ (no decay),
        imaginary parts $\pm 1$ (oscillation at frequency $1$). Read
        backwards from the two poles alone, that's an undying
        oscillation at frequency $1$ — exactly $\sin t$.
        """
    )
    return


# --- The 3-D landscape of |Y(s)| for the worked example -------------------
@app.cell(hide_code=True)
def _(go, mo, np):
    _re = np.linspace(-1.8, 1.8, 130)
    _im = np.linspace(-3.0, 3.0, 200)
    _RE, _IM = np.meshgrid(_re, _im)
    _S = _RE + 1j * _IM
    _mag = 1.0 / np.abs(_S**2 + 1.0)
    _Z = np.clip(_mag, 0, 5.0)

    _fig = go.Figure(data=[go.Surface(
        x=_re, y=_im, z=_Z,
        colorscale="Viridis", showscale=False, opacity=0.98,
        contours={"z": {"show": True, "usecolormap": True, "width": 1}},
    )])
    _fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[1, -1], z=[5.0, 5.0],
        mode="markers+text",
        marker=dict(size=4, color="#c15a46", symbol="diamond"),
        text=["pole at s = +i", "pole at s = −i"],
        textposition="top center",
        textfont=dict(color="#c15a46", size=11), showlegend=False,
    ))
    _fig.update_layout(
        height=460, margin=dict(l=0, r=0, t=10, b=0),
        scene=dict(
            xaxis_title="Re(s)", yaxis_title="Im(s)", zaxis_title="|Y(s)|",
            camera=dict(eye=dict(x=1.6, y=1.5, z=1.05)),
            aspectratio=dict(x=1, y=1.4, z=0.8),
        ),
        template="plotly_white",
    )

    mo.vstack([
        mo.md(
            r"""
            ### The landscape of $Y(s)$

            Same idea, picturable. Plot the height $|Y(s)|$ over the
            complex $s$-plane — real part one way, imaginary part the
            other. Everywhere the integral converges to a finite value,
            the surface is finite; at the two poles, it shoots up into
            **towers**. Drag to spin it.
            """
        ),
        _fig,
        mo.md(
            r"""
            The towers stand at $s = +i$ and $s = -i$ — squarely on the
            **imaginary axis**, equal heights, mirror images. Their
            *addresses* tell you the answer in time-domain language
            without inverting anything: zero real part (no exponential
            decay or growth), imaginary parts $\pm 1$ (oscillation at
            frequency $1$). Together, an undying oscillation at
            frequency $1$ — and that's the entire signature of $\sin t$.

            This is what "the poles encode the answer" actually means.
            We didn't have to invert the transform to see that $y(t)$
            was a pure unit-frequency oscillation; the two pole
            locations *already said so.* Inverting was just attaching
            the right amplitude.
            """
        ),
    ])
    return


if __name__ == "__main__":
    app.run()
