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


# --- The s-plane landscape (visual companion to the definition above) -----
# Folded in here so the picture of "what an image looks like" lands
# at the moment the definition is read. Uses the sin/cos transform
# 1/(s^2 + omega^2) -- the visually clearest case, with two clean
# towers on the imaginary axis. The derivation comes two cells later,
# so we frame this as a preview. Idea borrowed from 3Blue1Brown
# (credited in §99 at the end of the chapter).
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
            So what does an "image on the other side" actually look
            like? Every transform we'll meet turns out to be a
            **rational function of $s$**, and a rational function has
            a landscape. Plot the height $|F(s)|$ over the complex
            $s$-plane — real part one way, imaginary part the other —
            and wherever the denominator hits zero the surface shoots
            up into a **tower**. Those towers are the **poles**.

            Here's a preview — the landscape of
            $F(s) = \dfrac{1}{s^2 + \omega^2}$ with $\omega = 1.5$.
            (We'll derive this exact image two cells from now; it's
            the transform of $\cos\omega t$ and $\sin\omega t$.) Drag
            to spin it.
            """
        ),
        _fig,
        mo.md(
            r"""
            These two towers stand at $s = \pm i\omega$, on the
            **imaginary axis**. Hold that thought — a pole's *address*
            in this plane turns out to say something precise and
            surprising about the original $f(t)$. We come back to it
            below, once the dictionary is in hand.
            """
        ),
    ])
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
        """
    )
    return


# === Section 2.6 — A pole is a basis note: what a pole says about f(t) =============
# The user-requested deep dive: a pole isn't just "oscillates forever"
# -- its location names an elementary exponential MODE of f(t), and
# the full pole set IS the exponential basis of f(t) (residues = how
# much of each). Ties straight back to Ch6 characteristic roots. Two
# cells: the read-it-backwards dictionary, then the basis reframe with
# an s-plane -> time-waveform atlas figure.
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Reading the dictionary backwards — a pole is a *note*

        Look down the right column of the table and notice every entry
        has the same skeleton: a fraction whose **denominator** is the
        whole story. $e^{at}$ sits over $s - a$. The sinusoids sit over
        $s^2 + \omega^2 = (s - i\omega)(s + i\omega)$. The roots of
        those denominators — the **poles** — aren't incidental
        bookkeeping. They are a *readout of what $f(t)$ is made of.*

        Read each pair **backwards**:

        - a pole at $s = a$ on the real axis $\;\leftrightarrow\;$ the mode $e^{at}$ — pure growth ($a > 0$) or decay ($a < 0$);
        - a pole pair at $s = \pm i\omega$ on the imaginary axis $\;\leftrightarrow\;$ the mode $\cos\omega t$ / $\sin\omega t$ — pure, undying oscillation;
        - a pole pair at $s = -\gamma \pm i\omega$ off the axis $\;\leftrightarrow\;$ the mode $e^{-\gamma t}\cos\omega t$ — a decaying oscillation.

        A pole's **address** carries two coordinates and each one means
        something *in time*: its **horizontal** position (the real
        part) is a growth/decay rate, and its **vertical** position
        (the imaginary part) is an oscillation frequency. Left of the
        axis decays, right of it grows, on it neither; higher up
        oscillates faster.
        """
    )
    return


@app.cell(hide_code=True)
def _(go, mo, np):
    from plotly.subplots import make_subplots as _msub

    _red, _blue, _grn = "#c15a46", "#2a5d9c", "#2e8b6f"
    _fig = _msub(
        rows=1, cols=2, column_widths=[0.46, 0.54], horizontal_spacing=0.13,
        subplot_titles=("a pole's location in the s-plane …", "… is the mode it adds to f(t)"),
    )

    # --- left: the s-plane with three representative poles ---
    _fig.add_vrect(x0=-3.4, x1=0, fillcolor=_grn, opacity=0.05, line_width=0, row=1, col=1)
    _fig.add_trace(go.Scatter(x=[-3.4, 2.2], y=[0, 0], mode="lines",
        line=dict(color="#b9c2cf", width=1), showlegend=False, hoverinfo="skip"), row=1, col=1)
    _fig.add_trace(go.Scatter(x=[0, 0], y=[-4.2, 4.2], mode="lines",
        line=dict(color="#b9c2cf", width=1), showlegend=False, hoverinfo="skip"), row=1, col=1)
    _fig.add_trace(go.Scatter(x=[-0.6], y=[0], mode="markers",
        marker=dict(symbol="x", size=12, color=_red, line=dict(width=2)),
        name="s = −0.6 → decaying exp"), row=1, col=1)
    _fig.add_trace(go.Scatter(x=[0, 0], y=[2, -2], mode="markers",
        marker=dict(symbol="x", size=12, color=_blue, line=dict(width=2)),
        name="s = ±2i → pure oscillation"), row=1, col=1)
    _fig.add_trace(go.Scatter(x=[-0.5, -0.5], y=[3, -3], mode="markers",
        marker=dict(symbol="x", size=12, color=_grn, line=dict(width=2)),
        name="s = −0.5 ± 3i → decaying oscillation"), row=1, col=1)

    # --- right: the matching time-domain modes (color-locked to poles) ---
    _t = np.linspace(0, 7, 400)
    _fig.add_trace(go.Scatter(x=_t, y=np.exp(-0.6*_t), mode="lines",
        line=dict(color=_red, width=2.4), showlegend=False), row=1, col=2)
    _fig.add_trace(go.Scatter(x=_t, y=np.cos(2*_t), mode="lines",
        line=dict(color=_blue, width=2.4), showlegend=False), row=1, col=2)
    _fig.add_trace(go.Scatter(x=_t, y=np.exp(-0.5*_t)*np.cos(3*_t), mode="lines",
        line=dict(color=_grn, width=2.4), showlegend=False), row=1, col=2)

    _fig.update_xaxes(title="Re(s)", range=[-3.4, 2.2], zeroline=False, row=1, col=1)
    _fig.update_yaxes(title="Im(s)", range=[-4.2, 4.2], zeroline=False, row=1, col=1)
    _fig.update_xaxes(title="t", row=1, col=2)
    _fig.update_yaxes(title="f(t)", range=[-1.12, 1.12], row=1, col=2)
    _fig.update_layout(
        height=400, template="plotly_white",
        margin=dict(l=10, r=10, t=54, b=10),
        legend=dict(orientation="h", x=0.0, y=-0.2, font=dict(size=11)),
        paper_bgcolor="white", plot_bgcolor="white",
    )

    mo.vstack([
        mo.md(
            r"""
            ### The basis hidden in every function

            Here's the punchline, and it's *why the whole method
            works.* Any $f(t)$ you can build from exponentials and
            sinusoids is a sum of these elementary modes,

            $$
            f(t) \;=\; c_1\, e^{p_1 t} \;+\; c_2\, e^{p_2 t} \;+\; \cdots
            $$

            and its transform is then a sum of simple fractions, **one
            per mode**,

            $$
            F(s) \;=\; \frac{c_1}{s - p_1} \;+\; \frac{c_2}{s - p_2} \;+\; \cdots
            $$

            The exponents $p_1, p_2, \dots$ are *exactly the poles* of
            $F(s)$. So the poles **are the basis** of $f(t)$ — the
            list of elementary exponential ingredients it's built from
            — and the residues $c_1, c_2, \dots$ say how much of each.
            It's the same move you met in Chapter 6, where the
            characteristic roots were the exponents of the homogeneous
            basis $e^{rt}$. Laplace just makes that hidden exponential
            basis **visible**, as a constellation of dots in a plane.

            The atlas below is the whole dictionary in one picture:
            pick a spot in the $s$-plane (left), and the curve on the
            right is the mode that pole contributes to $f(t)$ —
            color-locked so you can see which goes with which.
            """
        ),
        _fig,
        mo.md(
            r"""
            This is why everything that follows becomes a **hunt for
            poles.** When we solve an ODE in §3–§4, the answer arrives
            as a rational $Y(s)$; finding *where its poles sit* hands
            you the basis of $y(t)$ — its modes, their decay rates,
            their frequencies — before you've written down a single
            exponential. (And in §4 we'll turn the damping knob on the
            car and literally **watch those poles slide** across this
            plane.)

            But first: how does an ODE turn into a rational $Y(s)$ at
            all? That's the one rule still missing — the derivative
            rule $\mathcal{L}\{y'\}$, and it's the rule that gives the
            portal its whole point. On to §3.
            """
        ),
    ])
    return


# === Section 3 — Why the portal works on ODEs: d/dt → s ===========================
# TODO: derive L{y'} = sY - y(0) and L{y''} = s²Y - s y(0) - y'(0)
# from integration by parts. Land the central trick: t-derivatives
# become s-multiplications, with the initial conditions automatically
# baked in. Then run one tiny worked example end-to-end.


# === Section 99 — Credits & further viewing =======================================
# KEEP THIS CELL LAST. New sections (§3-§8) go ABOVE this banner.
# The companion video is deferred to the end on purpose: it's framed
# as acknowledgement (we borrow its visual ideas heavily), and it
# embeds via mo.iframe -- a raw <iframe> inside mo.Html gets stripped
# by marimo's HTML sanitizer, so mo.iframe (srcdoc-based) is the
# working path.
@app.cell(hide_code=True)
def _(mo):
    _player = mo.iframe(
        '<style>html,body{margin:0;padding:0;background:#000;overflow:hidden}</style>'
        '<iframe width="100%" height="100%"'
        ' src="https://www.youtube-nocookie.com/embed/FE-hM1kRK4Y?rel=0"'
        ' title="3Blue1Brown — Why Laplace transforms are so useful"'
        ' frameborder="0"'
        ' allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"'
        ' allowfullscreen></iframe>',
        width="100%",
        height="430px",
    )
    mo.vstack([
        mo.md(
            r"""
            ---
            ## Credits & further viewing

            A confession: much of this chapter's *visual* intuition is
            not original. The idea of treating the transform as a
            **portal** between worlds, of reading a system's behaviour
            straight off the **poles** of its $s$-space image, and of
            drawing $|F(s)|$ as a **landscape** over the complex plane
            — all of it is borrowed, with gratitude, from Grant
            Sanderson's video below.

            We've added the interactivity (orbit the landscape
            yourself; in §4, drag the damping and watch the poles
            migrate) and stitched the ideas into our running
            car-and-road story — but the pictures come from here. If
            they clicked for you, this is where they came from. Watch
            it to see the same ideas in motion.
            """
        ),
        _player,
        mo.md(
            r"""
            <div style="text-align:center;color:#56636f;font-size:13px">
            3Blue1Brown — <em>Why Laplace transforms are so useful</em> ·
            Grant Sanderson ·
            <a href="https://www.youtube.com/watch?v=FE-hM1kRK4Y" target="_blank" rel="noopener">open on YouTube</a>
            </div>
            """
        ),
    ])
    return


if __name__ == "__main__":
    app.run()
