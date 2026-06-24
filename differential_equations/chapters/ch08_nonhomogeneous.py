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
        # Chapter 8 — Non-homogeneous equations

        **Same machinery, any push.**

        By the end of this chapter you should be able to:

        - Read the canonical second-order non-homogeneous form
          $y'' + p(x)\,y' + q(x)\,y = g(x)$ and split its solution as
          $y = y_h + y_p$ (homogeneous + particular).
        - Use **undetermined coefficients** to find a particular
          solution for the standard forcings (constant, polynomial,
          exponential, sinusoid, and sums of these); know the
          multiply-by-$x$ rescue when the trial form collides with a
          homogeneous solution.
        - Apply **variation of parameters** for any continuous
          forcing $g(x)$ — including ones the guess table can't
          touch — using the Wronskian formula.
        - Use **superposition** to handle a sum of forcings by
          solving each piece separately and adding the results.
        - Justify the split $y = y_h + y_p$ as the **complete**
          general solution — settling the "we just assumed it"
          feeling Chapter 7 left behind.
        """
    )
    return


# === Section 1 — Hook: from one push to any push ==================================
@app.cell(hide_code=True)
def _(mo):
    # Hook prose, picking up Ch 7's thread. Two loose ends drive the
    # whole chapter: (1) Ch 7 drove with ONE cosine -- what if the push
    # is any shape? (2) Ch 7 *assumed* x = x_h + x_p -- this chapter
    # justifies that split as the complete general solution. The road
    # animation (delib.road_test, below) makes "any shape of push"
    # literal: road profile = forcing, chassis bob = response.
    mo.md(
        r"""
        ## From one push to any push

        Chapter 7 left two loose ends, and this chapter is about
        tying them off.

        **The first is a question we dodged.** We drove the swing
        with a single, tidy cosine — one rhythm — and found the
        response. But the world rarely pushes you with a clean
        cosine. A pothole is a single jolt. A washboard road is a
        sum of many rhythms. Pulling away from a stop is a steady
        ramp. So: **what if the push on the right-hand side is *any*
        shape at all?** That's the first thing we hunt down — a way
        to solve

        $$
        y'' + 2\gamma\, y' + \omega_0^2\, y \;=\; g(t)
        $$

        for a forcing $g(t)$ we get to *choose*, not just
        $\cos(\omega t)$.

        **The second is something we quietly assumed.** Back in
        Chapter 7 we wrote the answer as $x = x_h + x_p$ — transient
        plus steady state — and pressed on as if that were obviously
        the whole story. It worked, but it had an uncanny, too-good
        feeling: *who said the solution splits so cleanly, and who
        said those two pieces are all of it?* This chapter pays that
        debt. We'll see that $y = y_h + y_p$ isn't a lucky guess but
        the **complete** general solution — every solution, no more
        and no fewer — and that fact is exactly what licenses the
        whole hunt.

        Here's the picture to hold onto while we do it.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # The graduated road-test widget (delib.road_test, shared with the
    # animation Lab's Demo 15). Road profile u(t) = the forcing g(t);
    # chassis bob y(t) = the response. Opens on the wavy (sinusoidal)
    # road so it reads as a direct continuation of Ch 7's cosine drive.
    delib.road_test(road="wavy", omega0=1.5, gamma=0.3)
    return


@app.cell(hide_code=True)
def _(mo):
    # Narrative tying the animation to the chapter's two questions.
    mo.md(
        r"""
        A car rolls at a steady speed over a road. **The road's
        up-and-down profile *is* the push $g(t)$** — whatever shape
        you give the road is the shape of the forcing. **The car's
        chassis bobbing *is* the response $y(t)$.** One shape goes
        in (the road); another comes out (the ride). It's the same
        damped oscillator as Chapter 7 — *stiffness* sets the natural
        bounce $\omega_0$, *damping* is the shock absorbers $\gamma$ —
        only now the right-hand side can be any road you draw.

        Play with the **road** menu and watch how the response
        answers each kind of push:

        - **Flat road** — no push at all. Whatever bounce the car
          starts with dies away and it settles. That dying bounce is
          $y_h$ alone, the Chapter 6 homogeneous part.
        - **Single bump** — one sharp jolt. The car bounces once and
          recovers. (This is the "impulse" we'll meet properly in
          Chapter 9.)
        - **Wavy road** — a pure cosine push: *exactly* Chapter 7.
          Tune the stiffness so the car's natural bounce matches the
          road's rhythm and the ride blows up — resonance, the same
          peak as last chapter, now under your wheels.
        - **Stairs** — a sum of step-pushes. Watch each step kick a
          fresh bounce that rides on top of the ones already there.
          **That stacking is superposition**, happening in front of
          you — and it's the visual heart of why $y_h + y_p$ works.

        The chart underneath strips away the scenery and says the
        same thing as two curves on one time axis: the **amber
        dashed** line is the road $g(t)$ going *in*; the **cyan**
        line is the chassis $y(t)$ coming *out*. The whole rest of
        the chapter is about turning that "road in → ride out" arrow
        into formulas — for any road you can draw.
        """
    )
    return


# === Section 2 — One job, two methods (the short signpost) ========================
@app.cell(hide_code=True)
def _(mo):
    # Was a long re-derivation of x = x_h + x_p (redundant after Ch 7).
    # Now: one tight signpost. Recall the split in one line; pay the
    # one Ch 7 debt (completeness -- y_h + y_p is EVERY solution); then
    # name the chapter's actual job (find a particular y_p) and the two
    # methods that will do it, plus the *new* role of superposition.
    mo.md(
        r"""
        ## One job — find a particular solution

        Recall from Chapter 7 that the answer splits as

        $$
        y(x) \;=\; \underbrace{y_h(x)}_{\text{homogeneous}}
        \;+\; \underbrace{y_p(x)}_{\text{particular}},
        $$

        and Chapter 6 already hands us $y_h$ for free — it's the
        characteristic-equation business with its two free constants,
        and it doesn't depend on the forcing $g$ at all. So the only
        outstanding work in this chapter is finding **one** particular
        $y_p$ for the forcing $g(x)$.

        > **You only need one $y_p$ — any one will do.** That sounds
        > too easy, so here's why nothing is lost. Suppose you've
        > found one particular solution $y_p$, and let $Y$ be *any
        > other* solution of the full equation. Look at their
        > difference $Y - y_p$: plug it into the left side and the
        > forcing cancels, $g - g = 0$, so $Y - y_p$ solves the
        > *homogeneous* equation. In other words $Y - y_p$ is one of
        > Chapter 6's $y_h$'s — and rearranging, $Y = y_h + y_p$. So
        > every solution is your one $y_p$ plus some homogeneous
        > piece. (Note $y_h$ is *not* produced by finding $y_p$; it's
        > the separate Chapter 6 family, with the free constants that
        > later match initial conditions.)

        From here the chapter is two methods, each a way to pin down
        a particular $y_p$:

        - **Undetermined coefficients** (this section). When $g(x)$ is
          "nice" — a polynomial, an exponential, a sinusoid, a
          product, or a sum of these — you can write down the *shape*
          of $y_p$ in advance and pin it down with a little algebra.
          Chapter 7 did this for *one* case (the cosine); we're about
          to see the rest of the table.
        - **Variation of parameters** (next section). When $g(x)$
          isn't "nice", undetermined coefficients has no shape to
          guess. There's a universal formula that works for *any*
          continuous $g(x)$ — we build it from scratch next time.
        """
    )
    return


# === Section 3 — Undetermined coefficients ========================================
# Split into three cells (table / worked example / multiply-by-x rescue)
# to keep each below the KaTeX-triplication density threshold
# (AUTHORING.md §4.10: heavy inline math in a single mo.md block can
# trigger MathML triplication even in --mode run).
@app.cell(hide_code=True)
def _(mo):
    # §3a — name the method, give the closure-under-d/dt reason it works,
    # show the trial-form table, and unpack three things to read off it.
    mo.md(
        r"""
        ## Method 1 — Undetermined coefficients

        Chapter 7's cosine drive was a worked example of this method.
        We didn't name it then, but the move was: **guess that $y_p$
        has the same shape as the forcing** (a sinusoid at the same
        frequency, with two unknowns $A$ and $\varphi$), plug it in,
        and match coefficients to pin the unknowns down.

        That trick generalises to a whole table of "nice" forcings.
        The reason it works is one fact: each of these families is
        **closed under differentiation** — differentiate a polynomial
        and you get another polynomial; differentiate $e^{ax}$ and
        you get $a\,e^{ax}$; differentiate $\cos bx$ and you get
        $-b\sin bx$. The left side of the equation only
        differentiates, scales, and adds — so if you put in a member
        of the family, you get back another member of the same
        family. Match the unknown coefficients term by term, and the
        equation collapses into a small algebra problem.

        ### The trial-form table

        Pick the trial form on the right of the row that matches your
        forcing on the left. The capital letters are the unknowns to
        be solved for.

        | forcing $g(x)$ | trial $y_p$ |
        |---|---|
        | constant $c$ | $A$ |
        | polynomial of degree $n$ | full polynomial $A_n x^n + \cdots + A_1 x + A_0$ |
        | $e^{a x}$ | $A\, e^{a x}$ |
        | $\cos(b x)$ or $\sin(b x)$ | $A\cos(b x) + B\sin(b x)$ |
        | $e^{a x}\cos(b x)$ or $e^{a x}\sin(b x)$ | $e^{a x}\bigl(A\cos(b x) + B\sin(b x)\bigr)$ |
        | a sum like $g_1 + g_2$ | the sum of the trials for $g_1$ and $g_2$ &nbsp;*(see below)* |

        Two points to read off the table:

        1. **Always include the full family**, never just the term
           you see. For $g = \cos b x$, the trial is $A\cos b x +
           B\sin b x$ — because the left side produces a $\sin b x$
           piece from the $y'$ term and you'll need a $B$ to balance
           it. That's the lesson Chapter 7's "first attempt" beat
           into us.
        2. **For polynomials, include every lower power** down to
           the constant — differentiating the highest term feeds
           into all the lower ones.

        The last row (sums) needs its own paragraph — that's the
        next subsection.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # §3a-bis — superposition splits the FORCING. Moved here (was in §2)
    # so it sits right next to the trial-form table row that introduces
    # it, and immediately precedes the worked example that uses it.
    # Distinct from Ch 7's solution-side superposition (y = y_h + y_p).
    mo.md(
        r"""
        ### Superposition splits the *forcing*

        Method 1 has a built-in limitation: the trial table only has
        rows for single nice shapes. What if the push is a *sum*,
        like $g = x + 4 e^{2x}$? Linearity rescues us. Solve each
        piece **separately** — find a particular $y_{p,1}$ for the
        forcing $g_1$, and a particular $y_{p,2}$ for $g_2$ — and
        their sum is a particular solution for the whole forcing:

        $$
        y_p \;=\; y_{p,1} + y_{p,2}.
        $$

        Quick check: the left side is linear, so it sends
        $y_{p,1} + y_{p,2}$ to $g_1 + g_2 = g$. ✓

        Two cautions, because this is where it's easy to go wrong:

        - This produces only the **particular** part. There is **no**
          $y_{h,1} + y_{h,2}$ — the homogeneous solution $y_h$ is
          found **once** for the whole equation (it never saw $g$),
          and added at the very end.
        - The point isn't to make the problem bigger; it's that each
          piece $g_i$ now matches a **single row** of the table even
          when the sum $g$ matched none. Decompose into table-friendly
          pieces, solve each by the recipe, add the particulars.

        This is a *different* use of superposition from Chapter 7's
        $y = y_h + y_p$: that split decomposes the **solution**; this
        one decomposes the **forcing**.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # §3b — a fully worked example using superposition (the previous
    # subsection) to split a sum-of-forcings into table-friendly
    # pieces, solve each, add.
    mo.md(
        r"""
        ### A worked example — sum-of-forcings via superposition

        Take

        $$
        y'' - 3 y' + 2 y \;=\; 6 \;+\; e^{4x}.
        $$

        The forcing is a sum, so superposition lets us find
        $y_{p,1}$ for the $6$ piece and $y_{p,2}$ for the $e^{4x}$
        piece independently, then add.

        **Piece 1.** For $y'' - 3 y' + 2 y = 6$, the table says trial
        $y_{p,1} = A$ (constant). Then $y_{p,1}' = 0$ and $y_{p,1}''
        = 0$, so the equation reads $2A = 6$, giving $A = 3$. So
        $y_{p,1} = 3$.

        **Piece 2.** For $y'' - 3 y' + 2 y = e^{4x}$, the table says
        trial $y_{p,2} = B\,e^{4x}$. Differentiate: $y_{p,2}' = 4 B
        e^{4x}$ and $y_{p,2}'' = 16 B e^{4x}$. Plug in:

        $$
        (16 - 12 + 2)\,B\,e^{4x} \;=\; e^{4x}
        \;\Longrightarrow\; 6 B = 1
        \;\Longrightarrow\; B = \tfrac{1}{6}.
        $$

        So $y_{p,2} = \tfrac{1}{6} e^{4x}$.

        Add the pieces:

        $$
        y_p(x) \;=\; 3 \;+\; \tfrac{1}{6}\, e^{4x}.
        $$

        That's a particular solution of the original. The full
        general solution is $y = y_h + y_p$, with $y_h$ coming from
        the characteristic equation of the *homogeneous* part —
        Chapter 6's job, untouched by anything we just did.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # §3c-i — make 'trial is a homogeneous solution' bite. User feedback:
    # lead with the failing case (don't bother contrasting with a working
    # case first); the naive table-trial just doesn't work, and you can
    # see why in the algebra.
    mo.md(
        r"""
        ### When the trial collides with $y_h$ — multiply by $x$

        The trial-form table is a recipe, and the recipe occasionally
        breaks. The cleanest way to see how is to push the same
        operator from the worked example one step harder.

        Consider

        $$
        y'' - 3 y' + 2 y \;=\; e^{2x}.
        $$

        The table says trial $y_p = A e^{2x}$. Differentiate twice
        and substitute:

        $$
        y_p'' - 3 y_p' + 2 y_p
        \;=\; (4 - 6 + 2)\, A\, e^{2x} \;=\; 0.
        $$

        The left side sends our trial to **zero**, not to $e^{2x}$.
        The coefficient $A$ has dropped out entirely, so there's
        nothing left to solve for — and the equation $0 = e^{2x}$
        obviously can't hold. The recipe has failed.

        Why? Look at the characteristic equation of the homogeneous
        part: $r^2 - 3 r + 2 = (r-1)(r-2) = 0$, with roots $r = 1$
        and $r = 2$. So

        $$
        y_h \;=\; C_1\, e^{x} + C_2\, e^{2x}.
        $$

        Our naive trial $A\, e^{2x}$ is **one of those homogeneous
        pieces** (the $r = 2$ one). And homogeneous solutions are
        *exactly* the functions the left side sends to zero — that's
        their defining property. So the operator annihilates our
        trial, and an annihilated trial can never match a non-zero
        forcing on the right. **That** is what "the trial is already
        a solution of the homogeneous equation" means.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # §3c-ii — the fix, worked on the same e^{2x} case. Ch 7 callback
    # now makes the structural parallel explicit (cos/sin IS the
    # homogeneous family of the undamped oscillator, so a cosine
    # forcing at omega_0 collides for exactly the same reason).
    mo.md(
        r"""
        **The fix: multiply by $x$.** Try $y_p = A\, x\, e^{2x}$
        instead. Differentiating, $y_p' = A\, e^{2x}(1 + 2x)$ and
        $y_p'' = A\, e^{2x}(4 + 4x)$, so

        $$
        y_p'' - 3 y_p' + 2 y_p
        \;=\; A\, e^{2x}\bigl[(4 + 4x) - 3(1 + 2x) + 2x\bigr]
        \;=\; A\, e^{2x}.
        $$

        The $x$-terms cancel ($4x - 6x + 2x = 0$), leaving a clean
        $A\, e^{2x} = e^{2x}$, so $A = 1$ and $y_p = x\, e^{2x}$.
        The extra factor of $x$ is precisely what produces a
        leftover the operator *doesn't* annihilate. (If the root
        were doubled — both characteristic roots equal to $2$ —
        $x\, e^{2x}$ would also be homogeneous and you'd need
        $x^2 e^{2x}$, one rung higher again.)
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # §3c-iii — the Ch 7 resonance disaster as the SAME rule,
    # structural parallel made explicit (cos/sin IS the homogeneous
    # family of the undamped oscillator). Split out for KaTeX density.
    mo.md(
        r"""
        ### Chapter 7's resonance disaster is the same trap

        The connection to Chapter 7 isn't an analogy — it's
        literally the same rule applied to a different operator.
        Chapter 7's equation was

        $$
        \ddot x + 2\gamma\,\dot x + \omega_0^2\, x \;=\; F_0\cos(\omega\, t).
        $$

        With $\gamma = 0$, the homogeneous equation reduces to
        $\ddot x + \omega_0^2\, x = 0$, whose solutions are
        $\cos(\omega_0 t)$ and $\sin(\omega_0 t)$. So the
        homogeneous family is

        $$
        x_h \;=\; C_1 \cos(\omega_0 t) + C_2 \sin(\omega_0 t).
        $$

        Now drive at $\omega = \omega_0$. The forcing $F_0\cos(\omega_0 t)$
        is *exactly the shape* of $x_h$, and the table's trial
        $A\cos(\omega_0 t) + B\sin(\omega_0 t)$ is the **whole**
        homogeneous family. Apply the operator and every coefficient
        cancels — same collision as the $e^{2x}$ case above, just
        with cosines and sines instead of exponentials.

        Multiply by $t$ (the independent variable here is time) —
        the same fix — and the honest particular solution is

        $$
        x_p(t) \;=\; \frac{F_0}{2\omega_0}\, t\, \sin(\omega_0 t),
        $$

        a sinusoid with a linearly-growing envelope. That envelope
        is the resonance disaster, and it appears for one and only
        one reason: the natural trial family was already the
        homogeneous solution. Push the trial up one rung — by $t$
        here, by $x$ over there — and the recipe works again.
        """
    )
    return


# === Section 4 — Variation of parameters ==========================================
# Being written from scratch around a linear-algebra framing (Wronskian
# = determinant / linear-independence test; the 2x2 system as "express the
# forcing's demand in the basis of homogeneous states"). This cell is the
# trailhead: a gentle sign that we're about to detour into linear algebra.
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Method 2 — Variation of parameters

        Method 1 only works when the forcing belongs to that small,
        closed-under-differentiation family. The moment the push is
        something like $g(x) = \sec x$, or $\tan x$, or a signal read
        off a sensor, there's no shape to guess — the table has no
        row for it.

        This second method has no such limit. Give it the homogeneous
        solutions $y_1, y_2$ (Chapter 6's job) and **any** continuous
        forcing $g(x)$, and it returns a particular solution by a
        fixed formula. It's the universal fallback. It also happens to
        be the most beautiful idea in the chapter — but the beauty is
        linear-algebraic, so it asks a little more of us.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # The "trailhead sign" — slow down, short detour into linear algebra.
    mo.md(
        r"""
        > ### 🪧 Trailhead — a short detour into linear algebra
        >
        > Up to here the chapter has been pure calculus. From this
        > point on, the natural way to *understand* (not just execute)
        > variation of parameters runs through a few ideas from
        > **linear algebra**:
        >
        > - **Linear independence** — when two solutions are genuinely
        >   different versus secretly the same one rescaled.
        > - **The determinant of a $2\times 2$** — and its meaning as
        >   an *area*.
        > - **Solving a small linear system** — when it has a unique
        >   solution, and the role of the **null space** in deciding
        >   that.
        >
        > You don't need to be fluent. We'll re-introduce each idea in
        > a sentence as we reach for it, and only the $2\times 2$ case
        > matters here. But it *is* worth slowing down: the engine of
        > this method — the quantity called the **Wronskian** — is
        > nothing but a determinant that tests linear independence.
        > Meet that idea first and the whole formula stops looking
        > like magic; skip it and you'll be memorising symbols.
        >
        > So take the detour. The next few cells step off the calculus
        > trail into the linear-algebra realm, just long enough to
        > pick up the three ideas above — then we come back and let
        > them solve the ODE.
        """
    )
    return


# === Section 4.1 — Prologue: c1 y1 + c2 y2 as a basis expansion ===================
# First step of the LA detour. Re-see y_h = c1*y1 + c2*y2 as a basis
# decomposition (same idea as P = 3*e1 + 2*e2 in R^2). The side-by-side
# figure makes the analogy visceral: same coefficients on both sides.
@app.cell(hide_code=True)
def _(go, mo, np):
    from plotly.subplots import make_subplots

    _fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "In ℝ²:  P = 3·e₁ + 2·e₂",
            "In span(y₁, y₂):  y = 3·y₁ + 2·y₂",
        ),
        horizontal_spacing=0.12,
    )

    # --- left: 2-D vector decomposition --------------------------------
    # gridlines (faint)
    _fig.add_trace(go.Scatter(x=[-0.5, 4], y=[0, 0], mode="lines",
        line=dict(color="#e0e6ee", width=1), showlegend=False, hoverinfo="skip"),
        row=1, col=1)
    _fig.add_trace(go.Scatter(x=[0, 0], y=[-0.5, 3], mode="lines",
        line=dict(color="#e0e6ee", width=1), showlegend=False, hoverinfo="skip"),
        row=1, col=1)
    # basis e1 (red, horizontal)
    _fig.add_trace(go.Scatter(x=[0, 1], y=[0, 0], mode="lines+markers",
        line=dict(color="#c15a46", width=4),
        marker=dict(symbol=["circle", "triangle-right"], size=[6, 14], color="#c15a46"),
        showlegend=False, hoverinfo="skip"), row=1, col=1)
    # basis e2 (blue, vertical)
    _fig.add_trace(go.Scatter(x=[0, 0], y=[0, 1], mode="lines+markers",
        line=dict(color="#2a5d9c", width=4),
        marker=dict(symbol=["circle", "triangle-up"], size=[6, 14], color="#2a5d9c"),
        showlegend=False, hoverinfo="skip"), row=1, col=1)
    # vector P
    _fig.add_trace(go.Scatter(x=[0, 3], y=[0, 2], mode="lines+markers",
        line=dict(color="#16223a", width=3),
        marker=dict(symbol=["circle", "circle"], size=[1, 10], color="#16223a"),
        showlegend=False, hoverinfo="skip"), row=1, col=1)
    # decomposition helper lines
    _fig.add_trace(go.Scatter(x=[3, 3], y=[0, 2], mode="lines",
        line=dict(color="#16223a", width=1, dash="dot"),
        showlegend=False, hoverinfo="skip"), row=1, col=1)
    _fig.add_trace(go.Scatter(x=[0, 3], y=[2, 2], mode="lines",
        line=dict(color="#16223a", width=1, dash="dot"),
        showlegend=False, hoverinfo="skip"), row=1, col=1)
    # labels (annotations bound to first subplot)
    for _ann in [
        dict(x=1.15, y=-0.22, text="<b>e₁</b>", color="#c15a46", size=14),
        dict(x=-0.18, y=1.15, text="<b>e₂</b>", color="#2a5d9c", size=14),
        dict(x=3.15, y=2.25, text="<b>P</b>", color="#16223a", size=14),
        dict(x=1.5, y=-0.4, text="3 steps right", color="#6c7a90", size=10),
        dict(x=3.42, y=1.0, text="2 steps up", color="#6c7a90", size=10),
    ]:
        _fig.add_annotation(x=_ann["x"], y=_ann["y"], text=_ann["text"],
            showarrow=False, font=dict(color=_ann["color"], size=_ann["size"]),
            xref="x", yref="y")

    # --- right: function-basis decomposition ---------------------------
    _x = np.linspace(0, 2*np.pi, 220)
    _y1 = np.cos(_x)
    _y2 = np.sin(_x)
    _ycombo = 3*_y1 + 2*_y2
    _fig.add_trace(go.Scatter(x=_x, y=_y1, mode="lines",
        name="y₁(x) = cos x",
        line=dict(color="#c15a46", width=2)), row=1, col=2)
    _fig.add_trace(go.Scatter(x=_x, y=_y2, mode="lines",
        name="y₂(x) = sin x",
        line=dict(color="#2a5d9c", width=2)), row=1, col=2)
    _fig.add_trace(go.Scatter(x=_x, y=_ycombo, mode="lines",
        name="y = 3·y₁ + 2·y₂",
        line=dict(color="#16223a", width=2.5)), row=1, col=2)

    _fig.update_xaxes(range=[-0.6, 4.2], row=1, col=1,
        showgrid=False, zeroline=False)
    _fig.update_yaxes(range=[-0.7, 3], row=1, col=1,
        showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1)
    _fig.update_xaxes(title="x", row=1, col=2, range=[0, 2*np.pi])

    _fig.update_layout(
        template="plotly_white",
        height=340,
        margin=dict(l=40, r=20, t=60, b=70),
        showlegend=True,
        legend=dict(orientation="h", x=0.78, xanchor="center", y=-0.18,
                    font=dict(size=11)),
        paper_bgcolor="white", plot_bgcolor="white",
    )

    mo.vstack([
        mo.md(
            r"""
            ### Prologue — coordinates, in space and in functions

            Before we wade into the linear-algebra realm, take this
            one conceptual leap with me. It's not new math — it's a
            *re-seeing* of math you already know.

            You wouldn't think twice about writing the point
            $\mathbf{P} = (3, 2)$ as a *recipe* — three steps right,
            two steps up:

            $$
            \mathbf{P} \;=\; 3\,\mathbf{e}_1 \;+\; 2\,\mathbf{e}_2.
            $$

            Here $\mathbf{e}_1 = (1, 0)$ and $\mathbf{e}_2 = (0, 1)$
            are the **basis** — the two directions you're allowed to
            combine — and the numbers $(3, 2)$ are the **coordinates**
            in that basis. The two coordinates don't mix: "three
            steps right" is a separate fact from "two steps up".

            Now look at what Chapter 6 wrote as the homogeneous
            solution:

            $$
            y_h(x) \;=\; c_1\, y_1(x) \;+\; c_2\, y_2(x).
            $$

            It is the **same recipe** — only the "directions" are
            now whole *functions* instead of unit arrows. $y_1$ and
            $y_2$ play the role of $\mathbf{e}_1, \mathbf{e}_2$;
            $c_1$ and $c_2$ are the coordinates in this new basis.
            The figure below shows the analogy with the same
            coefficients $(3, 2)$ on both sides.
            """
        ),
        _fig,
        mo.md(
            r"""
            Pick a $(c_1, c_2)$ and you've picked a specific
            function. The set of *all* such choices sweeps out a
            whole **two-dimensional space of functions**, with basis
            $(y_1, y_2)$.

            That's the lens for the rest of this section. $y_h$
            isn't a clever family someone discovered — it's the
            **2-D function space spanned by your basis**.
            Everything that follows (variation of parameters, the
            Wronskian, the formula) is linear algebra done inside
            this function space.
            """
        ),
    ])
    return


# === Section 4.2 — Saga 1: y_h is the null space of "evil" L ======================
# Name the operator L; show it's linear ("a matrix acting on functions");
# derive y_h as the null space of L. Set up the next saga (y_p is the
# survivor that L can't crush to zero).
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Saga 1 — $y_h$ is the **null space** of an "evil" operator $L$

        Let's give the differential operator a name and a personality.
        Call it $L$:

        $$
        L[y] \;=\; y'' \;+\; p(x)\, y' \;+\; q(x)\, y.
        $$

        $L$ is a machine. Feed it a function — it differentiates
        twice, mixes the results according to the recipe, and hands
        back another function. The chapter's whole equation is just

        $$
        L[y] \;=\; g(x),
        $$

        — find a $y$ whose $L$-output is exactly the forcing $g$.

        Through the linear-algebra lens, **$L$ is a kind of matrix
        that acts on functions** instead of on column vectors. That
        is the whole detour, in one sentence: *let matrices act on
        functions.* Like every respectable matrix, $L$ is
        **linear** — it distributes over sums and scalar multiples:

        $$
        L[c\, y] \;=\; c\, L[y],
        \qquad
        L[y + z] \;=\; L[y] + L[z].
        $$

        And linearity is exactly the property that turns the
        homogeneous family into something with a *name* — that's
        the next cell.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Saga 1 continued — derive y_h = null(L) from linearity.
    # Split out so each cell stays under the KaTeX density threshold
    # (§4.10): the 'L is linear' setup + this null-space derivation
    # together carry 5 displays, which is past the safe band.
    mo.md(
        r"""
        Chapter 6 handed us two basis functions $y_1, y_2$ that $L$
        annihilates, $L[y_1] = L[y_2] = 0$. By linearity, *every*
        combination of them is annihilated too:

        $$
        L\bigl[c_1 y_1 + c_2 y_2\bigr]
        \;=\; c_1 L[y_1] + c_2 L[y_2]
        \;=\; c_1\!\cdot\!0 + c_2\!\cdot\!0
        \;=\; 0.
        $$

        Every function in the 2-D space we just named in the
        Prologue gets crushed to zero by $L$.

        This crushing has a name in linear algebra. The set of all
        vectors a matrix sends to zero is called the **null space**
        (or *kernel*) of that matrix. We've just seen that the
        homogeneous family $y_h$ — the *entire* 2-D function space
        spanned by $(y_1, y_2)$ — is the null space of $L$:

        $$
        \boxed{\; y_h \;=\; \mathrm{null}(L). \;}
        $$

        That is the headline of this saga, and worth sitting with.
        The homogeneous family from Chapter 6 isn't a side-quest;
        it's the **null space of the operator that defines this
        whole chapter**. Every function in it is $L$-fragile — the
        evil machine smashes it to zero. Picture $L$ as a kind of
        annihilating magic in a fable: any pure-homogeneous
        combination it touches simply *vanishes*.

        But not everything in the world is fragile. The forcing
        $g(x)$ isn't zero, so the $y_p$ we're hunting can't be in
        the null space — it has to *survive* $L$ and come out the
        other side as $g$. That's where the next saga goes.
        """
    )
    return


# === Section 4.3 — Saga 2: y_p is the survivor (L[y_p] = g, not 0) ================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Saga 2 — $y_p$ is the **survivor**

        Everything in the null space dies: $L$ sends it to zero.
        But the equation we actually need to solve is

        $$
        L[y_p] \;=\; g(x), \qquad g \not\equiv 0.
        $$

        Read that as a demand the null space *cannot meet*. If $y_p$
        were one of those fragile homogeneous combinations, $L$ would
        crush it to $0$ — and $0 \neq g$. So the particular solution
        we're after is, by definition, **not** in the null space. It
        has to be the rare kind of function that $L$ touches and
        *doesn't* annihilate: one that comes out the far side
        carrying exactly the forcing $g$.

        Call $y_p$ the **survivor**. Where the homogeneous
        functions vanish under $L$'s magic, the survivor walks
        through it and emerges as $g$. The whole rest of the method
        is one question:

        > **What does a function have to be made of to survive $L$?**

        It clearly can't be built the homogeneous way — plain
        constants $c_1, c_2$ in front of $y_1, y_2$ — because we
        just saw that construction is exactly what dies. The
        survivor needs something stronger. Finding out what is
        Saga 3.
        """
    )
    return


# === Section 4.4 — Saga 3: the ansatz — constants become functions (relics) =======
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Saga 3 — arm the survivor with relics

        We know the survivor can't be the homogeneous build,
        $c_1 y_1 + c_2 y_2$ with *constant* $c_1, c_2$. Look again
        at exactly why it dies:

        $$
        L\bigl[c_1 y_1 + c_2 y_2\bigr]
        \;=\; c_1\, L[y_1] + c_2\, L[y_2] \;=\; 0.
        $$

        The constants slide straight out through $L$'s linearity and
        leave only $L[y_1], L[y_2]$ — both zero. The constants never
        *interact* with $L$; they just ride along and get
        annihilated with their basis functions.

        So here's the upgrade. Keep the same humble basis $y_1, y_2$,
        but replace the inert constants with **functions** of $x$ —
        call them $u_1(x), u_2(x)$:

        $$
        \boxed{\; y_p \;=\; u_1(x)\, y_1 \;+\; u_2(x)\, y_2. \;}
        $$

        Think of $u_1, u_2$ as *relics* fastened onto the basis. The
        functions $y_1, y_2$ are the same fragile things as before —
        but now, when $L$ differentiates $y_p$, the product rule
        forces it to also differentiate the relics, producing
        $u_1', u_2'$ terms that the constant version simply did not
        have. Those new terms are the foothold: they're what can
        come out the other side as $g$ instead of as $0$. The relics
        let the survivor *interact* with $L$ rather than ride
        through it untouched.

        This move — letting the constants of the homogeneous
        solution vary as functions — is the whole idea, and it's
        where the method gets its name: **variation of parameters**.
        The "parameters" are $c_1, c_2$; we let them vary.

        Of course, smuggling two unknown functions into one equation
        is a lot of new freedom — more than one equation can pin
        down. We'll spend that surplus freedom deliberately in
        Saga 4, where we finally put $y_p$ through $L$ and watch the
        relics go to work.
        """
    )
    return


# === Section 4.5 — Saga 4: the survivor's first move (y_p') =======================
# Apply L to y_p in pieces. First: differentiate once via product rule;
# group the four terms into "relic-derived" vs "basis-derived" buckets;
# spend the surplus freedom from the ansatz by zeroing the relic-derived
# group. The result -- y_p' looks like the constant-coefficient version.
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Saga 4 — the survivor's first move

        We've armed $y_p$. Now we feed it through $L$ and watch the
        algebra unfold. $L$ begins by differentiating $y_p$ once,
        and the product rule on each term gives **four** pieces:

        $$
        y_p' \;=\; u_1' y_1 + u_1 y_1' + u_2' y_2 + u_2 y_2'.
        $$

        Four pieces, but they sort cleanly into two kinds. Group:

        $$
        y_p'
        \;=\; \underbrace{\,u_1' y_1 + u_2' y_2\,}_{\text{relic-derived (the } u_i' \text{ terms)}}
        \;+\; \underbrace{\,u_1 y_1' + u_2 y_2'\,}_{\text{basis-derived (the } y_i' \text{ terms)}}.
        $$

        The first bracket touches the **relics' derivatives**
        ($u_1', u_2'$); the second touches the **basis's
        derivatives** ($y_1', y_2'$). In shape they're symmetric,
        but they play very different roles when we differentiate
        a second time: the relic-derived bracket would, on the
        next round, drag in $u_1'', u_2''$. That's a tangle we
        don't need — and as we'll see in a moment, we have just
        enough freedom to outlaw it.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Saga 4 continued — spend the surplus freedom (the convenience
    # constraint) and simplify y_p'. Split out so each cell stays
    # under the KaTeX density threshold (§4.10).
    mo.md(
        r"""
        Remember Saga 3 noted a surplus: two unknown functions
        $u_1, u_2$ against only one equation, $L[y_p] = g$. We get
        to spend exactly one extra constraint. Spend it here, by
        **declaring the relic-derived bracket to be zero**:

        $$
        \boxed{\; u_1' y_1 \;+\; u_2' y_2 \;=\; 0. \;}
        $$

        This is a *choice*, not a derivation — we have the freedom
        to impose it, and we use that freedom now because we know
        it will save us from $u_i''$ terms in a moment.

        With the relic-derived bracket annulled, the first
        derivative simplifies to

        $$
        y_p' \;=\; u_1 y_1' \;+\; u_2 y_2'.
        $$

        Notice it now *looks* exactly like the constant-coefficient
        first derivative $(c_1 y_1 + c_2 y_2)' = c_1 y_1' + c_2 y_2'$ —
        the relics $u_1, u_2$ sit there as if they weren't varying
        at all. That's the gift of the choice we just made: from
        here, the first-derivative algebra reads as if the relics
        were constants.

        In the next saga we differentiate once more and finally
        push the whole thing through $L$.
        """
    )
    return


# === Section 4.6 — Saga 5: the second derivative (y_p'') ==========================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Saga 5 — look closer: the second derivative

        $L$ also needs $y_p''$. Differentiate the simplified first
        derivative $y_p' = u_1 y_1' + u_2 y_2'$ once more — product
        rule again, on each of its two terms:

        $$
        y_p'' \;=\; u_1' y_1' + u_1 y_1'' \;+\; u_2' y_2' + u_2 y_2''.
        $$

        This time we *keep* all four pieces — we already spent our
        one free constraint back in Saga 4, so there's no second
        bracket to set to zero. We now hold all three ingredients
        $L$ wants:

        $$
        \begin{aligned}
        y_p   &= u_1 y_1 + u_2 y_2, \\
        y_p'  &= u_1 y_1' + u_2 y_2', \\
        y_p'' &= u_1' y_1' + u_1 y_1'' + u_2' y_2' + u_2 y_2''.
        \end{aligned}
        $$
        """
    )
    return


# === Section 4.7 — Saga 6: push y_p through L; the null space collapses it =========
@app.cell(hide_code=True)
def _(mo):
    # Saga 6a — substitute the three pieces into L and regroup into the
    # "u_i' " survivor term plus two u_i * L[y_i] groups.
    mo.md(
        r"""
        ### Saga 6 — through the gauntlet

        Now assemble $L[y_p] = y_p'' + p\,y_p' + q\,y_p$ from the
        three ingredients and demand it equal $g$. Substituting:

        $$
        L[y_p] = \bigl(u_1' y_1' + u_1 y_1'' + u_2' y_2' + u_2 y_2''\bigr) + p\bigl(u_1 y_1' + u_2 y_2'\bigr) + q\bigl(u_1 y_1 + u_2 y_2\bigr).
        $$

        It looks like a wall of symbols, but it sorts itself the
        moment you group by relic. Collect everything multiplying
        $u_1$, everything multiplying $u_2$, and the leftover
        $u_i'$ pieces:

        $$
        L[y_p] = \underbrace{\bigl(u_1' y_1' + u_2' y_2'\bigr)}_{\text{survivor term}} + u_1\underbrace{\bigl(y_1'' + p y_1' + q y_1\bigr)}_{L[y_1]} + u_2\underbrace{\bigl(y_2'' + p y_2' + q y_2\bigr)}_{L[y_2]}.
        $$

        Look at the two braced groups: each is exactly $L$ applied
        to a *basis* function.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Saga 6b — invoke the null space (Saga 1) to kill the L[y_i] terms,
    # collapsing L[y_p] to the survivor term; set = g for the 2nd eqn.
    mo.md(
        r"""
        And here Saga 1 pays off. The basis functions $y_1, y_2$
        live in the **null space** of $L$ — that was the whole point
        — so $L[y_1] = 0$ and $L[y_2] = 0$. Both of those big groups
        simply **vanish**:

        $$
        L[y_p] = \bigl(u_1' y_1' + u_2' y_2'\bigr) + u_1\!\cdot\!0 + u_2\!\cdot\!0 = u_1' y_1' + u_2' y_2'.
        $$

        Everything built from the fragile basis got annihilated, as
        it always does. The **only** thing $L$ couldn't destroy is
        the relic-derivative term $u_1' y_1' + u_2' y_2'$ — the
        survivor's true substance. And that survivor must equal the
        forcing:

        $$
        \boxed{\; u_1' y_1' \;+\; u_2' y_2' \;=\; g. \;}
        $$

        We now have **two** equations in the two relic-rates
        $u_1', u_2'$ — the convenience choice from Saga 4 and the
        survivor equation from just now:

        $$
        \begin{aligned}
        u_1' y_1 \;+\; u_2' y_2 &\;=\; 0, \\
        u_1' y_1' \;+\; u_2' y_2' &\;=\; g.
        \end{aligned}
        $$

        Two equations, two unknowns. This is precisely where the
        linear algebra we signed up for finally does the work — the
        next saga writes it as a matrix and the Wronskian appears.
        """
    )
    return


# === Section 4.8 — Saga 7: write the pair as a matrix equation ====================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Saga 7 — name the matrix

        The two equations from Saga 6 are a linear system in the two
        unknown rates $u_1', u_2'$. Stack them as a single matrix
        equation:

        $$
        \underbrace{\begin{bmatrix} y_1 & y_2 \\ y_1' & y_2' \end{bmatrix}}_{Y(x)}\,\underbrace{\begin{bmatrix} u_1' \\ u_2' \end{bmatrix}}_{\mathbf{u}'} \;=\; \underbrace{\begin{bmatrix} 0 \\ g \end{bmatrix}}_{\text{demand}}.
        $$

        Read each column of $Y(x)$ as a **state vector** of one basis
        solution: the top row is the value $y_i$, the bottom row is
        the velocity $y_i'$. Together they say "in $(y,\,y')$ space,
        here is where basis function $i$ sits *and* where it's
        heading right now."

        On the right, the forcing $g$ shows up *only* in the velocity
        slot — the convenience constraint from Saga 4 zeroed the
        position slot. The matrix equation is the entire story so
        far, compressed:

        > **In the basis of homogeneous states, what mixture of rates
        > produces a position-change of $0$ and a velocity-change of
        > $g$?**

        That mixture is $\mathbf{u}'$. To solve for it, we need to
        invert $Y(x)$ — and the moment we ask that, the determinant
        walks on stage.
        """
    )
    return


# === Section 4.9 — Saga 8: the Wronskian is det(Y) ================================
# Twin state-plane figure: independent basis -> nondegenerate
# parallelogram with W = area > 0; dependent basis -> collapsed line
# with W = 0. Makes "Wronskian = linear-independence test" visceral.
@app.cell(hide_code=True)
def _(go, mo, np):
    from plotly.subplots import make_subplots as _make_subplots

    _fig = _make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Independent basis:  W = area ≠ 0",
            "Dependent basis:  W = 0 (line, no area)",
        ),
        horizontal_spacing=0.14,
    )

    # ---- LEFT: independent basis -- y1 = cos x, y2 = sin x at x = pi/4 ----
    # state vectors: v1 = (cos, -sin) = (0.707, -0.707)
    #                v2 = (sin,  cos) = (0.707,  0.707)
    _c, _s = np.cos(np.pi/4), np.sin(np.pi/4)
    _v1 = np.array([_c, -_s])
    _v2 = np.array([_s,  _c])
    # parallelogram polygon: 0 -> v1 -> v1+v2 -> v2 -> 0
    _poly_x = [0, _v1[0], _v1[0]+_v2[0], _v2[0], 0]
    _poly_y = [0, _v1[1], _v1[1]+_v2[1], _v2[1], 0]
    _fig.add_trace(go.Scatter(
        x=_poly_x, y=_poly_y, mode="lines", fill="toself",
        line=dict(color="#16223a", width=1.5),
        fillcolor="rgba(120,150,200,0.22)",
        showlegend=False, hoverinfo="skip"), row=1, col=1)
    # axes (faint)
    for _xy in [([-1.2, 1.6], [0, 0]), ([0, 0], [-1.2, 1.6])]:
        _fig.add_trace(go.Scatter(x=_xy[0], y=_xy[1], mode="lines",
            line=dict(color="#e0e6ee", width=1),
            showlegend=False, hoverinfo="skip"), row=1, col=1)
    # vector v1 (red)
    _fig.add_trace(go.Scatter(x=[0, _v1[0]], y=[0, _v1[1]],
        mode="lines+markers",
        line=dict(color="#c15a46", width=4),
        marker=dict(symbol=["circle", "triangle-right"], size=[1, 14],
                    angle=[0, -45], color="#c15a46"),
        showlegend=False, hoverinfo="skip"), row=1, col=1)
    # vector v2 (blue)
    _fig.add_trace(go.Scatter(x=[0, _v2[0]], y=[0, _v2[1]],
        mode="lines+markers",
        line=dict(color="#2a5d9c", width=4),
        marker=dict(symbol=["circle", "triangle-up"], size=[1, 14],
                    angle=[0, 45], color="#2a5d9c"),
        showlegend=False, hoverinfo="skip"), row=1, col=1)
    for _ann in [
        dict(x=_v1[0]+0.12, y=_v1[1]-0.10, text="<b>(y₁, y₁′)</b>", color="#c15a46"),
        dict(x=_v2[0]+0.12, y=_v2[1]+0.12, text="<b>(y₂, y₂′)</b>", color="#2a5d9c"),
        dict(x=(_v1[0]+_v2[0])/2, y=(_v1[1]+_v2[1])/2 + 0.05,
             text="area = |W| = 1", color="#16223a"),
    ]:
        _fig.add_annotation(x=_ann["x"], y=_ann["y"], text=_ann["text"],
            showarrow=False, font=dict(color=_ann["color"], size=12),
            xref="x", yref="y")

    # ---- RIGHT: dependent basis -- y2 = 2 y1, so v2 = 2*v1 ----
    _w1 = np.array([_c, -_s])
    _w2 = 2 * _w1
    for _xy in [([-1.2, 2.2], [0, 0]), ([0, 0], [-1.8, 1.2])]:
        _fig.add_trace(go.Scatter(x=_xy[0], y=_xy[1], mode="lines",
            line=dict(color="#e0e6ee", width=1),
            showlegend=False, hoverinfo="skip"), row=1, col=2)
    # vector w2 first (longer, blue) so red overlays it
    _fig.add_trace(go.Scatter(x=[0, _w2[0]], y=[0, _w2[1]],
        mode="lines+markers",
        line=dict(color="#2a5d9c", width=4),
        marker=dict(symbol=["circle", "triangle-right"], size=[1, 14],
                    angle=[0, -45], color="#2a5d9c"),
        showlegend=False, hoverinfo="skip"), row=1, col=2)
    _fig.add_trace(go.Scatter(x=[0, _w1[0]], y=[0, _w1[1]],
        mode="lines+markers",
        line=dict(color="#c15a46", width=4),
        marker=dict(symbol=["circle", "triangle-right"], size=[1, 14],
                    angle=[0, -45], color="#c15a46"),
        showlegend=False, hoverinfo="skip"), row=1, col=2)
    for _ann in [
        dict(x=_w1[0]+0.10, y=_w1[1]+0.15, text="<b>(y₁, y₁′)</b>", color="#c15a46"),
        dict(x=_w2[0]+0.10, y=_w2[1]-0.18, text="<b>(2y₁, 2y₁′)</b>", color="#2a5d9c"),
        dict(x=0.75, y=-1.35, text="collinear → no area", color="#6c7a90"),
    ]:
        _fig.add_annotation(x=_ann["x"], y=_ann["y"], text=_ann["text"],
            showarrow=False, font=dict(color=_ann["color"], size=12),
            xref="x2", yref="y2")

    _fig.update_xaxes(range=[-1.2, 1.8], row=1, col=1, title="y",
        showgrid=False, zeroline=False)
    _fig.update_yaxes(range=[-1.2, 1.8], row=1, col=1, title="y′",
        showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1)
    _fig.update_xaxes(range=[-1.2, 2.4], row=1, col=2, title="y",
        showgrid=False, zeroline=False)
    _fig.update_yaxes(range=[-1.8, 1.4], row=1, col=2, title="y′",
        showgrid=False, zeroline=False, scaleanchor="x2", scaleratio=1)

    _fig.update_layout(
        template="plotly_white",
        height=360,
        margin=dict(l=50, r=30, t=60, b=50),
        showlegend=False,
        paper_bgcolor="white", plot_bgcolor="white",
    )

    mo.vstack([
        mo.md(
            r"""
            ### Saga 8 — the Wronskian, finally named

            The determinant of $Y(x)$ has a name we've been ducking
            for two chapters. Define

            $$
            W(x) \;=\; \det Y(x) \;=\; y_1\,y_2' \;-\; y_2\,y_1'.
            $$

            This is the **Wronskian**. It is not new machinery — it
            is the determinant of the state matrix you already had.

            Geometrically (left panel), the columns of $Y(x)$ are
            two state vectors $(y_i,\,y_i')$ in the $(y, y')$ plane.
            Their determinant is the **signed area of the parallelogram**
            they span. If the basis is genuinely independent, that
            parallelogram has real area — and $W \ne 0$.

            Geometrically (right panel), if one basis function is a
            multiple of the other, the two state vectors point along
            the **same line**. The parallelogram collapses; area is
            zero; $W = 0$.

            So $W(x) \ne 0$ is exactly the statement **"the two basis
            functions are linearly independent at $x$"** — the
            condition you've quietly relied on since Chapter 6 every
            time you wrote "the general solution is $c_1 y_1 + c_2 y_2$."
            Now it has a name.
            """
        ),
        _fig,
    ])
    return


# === Section 4.10 — Saga 9: Cramer's rule + integrate =============================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Saga 9 — Cramer's rule unlocks the rates

        Because $W \ne 0$, the matrix $Y(x)$ is invertible and the
        system has a unique solution. The cleanest way to read it off
        is **Cramer's rule** — replace one column of $Y$ with the
        right-hand side $(0, g)^\top$ and divide by $\det Y = W$:

        $$
        u_1' \;=\; \frac{1}{W}\,\det\!\begin{bmatrix} 0 & y_2 \\ g & y_2' \end{bmatrix} \;=\; \frac{0\cdot y_2' - y_2\cdot g}{W} \;=\; -\,\frac{y_2\,g}{W},
        $$

        $$
        u_2' \;=\; \frac{1}{W}\,\det\!\begin{bmatrix} y_1 & 0 \\ y_1' & g \end{bmatrix} \;=\; \frac{y_1\cdot g - 0\cdot y_1'}{W} \;=\; \;\;\,\frac{y_1\,g}{W}.
        $$

        These are the **relic-rates** — how fast each coefficient
        must change at every $x$ to keep the survivor $y_p$ tuned to
        the forcing. To get the relics themselves we just integrate:

        $$
        u_1(x) \;=\; -\!\int \frac{y_2(x)\,g(x)}{W(x)}\,dx, \qquad u_2(x) \;=\; \;\;\int \frac{y_1(x)\,g(x)}{W(x)}\,dx.
        $$

        (Any constants of integration just shift $y_p$ by a piece of
        $y_h$, which gets absorbed into the $c_1 y_1 + c_2 y_2$ part
        later — they cost us nothing.)
        """
    )
    return


# === Section 4.11 — Saga 10: equip the relics, get y_p ============================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Saga 10 — equip the relics

        Plug $u_1(x)$ and $u_2(x)$ back into the armored form
        $y_p = u_1\,y_1 + u_2\,y_2$ from Saga 3. The survivor walks
        out of the gauntlet carrying the closed-form answer:

        $$
        \boxed{\;\; y_p(x) \;=\; -\,y_1(x)\!\int \frac{y_2(x)\,g(x)}{W(x)}\,dx \;\;+\;\; y_2(x)\!\int \frac{y_1(x)\,g(x)}{W(x)}\,dx \;\;}
        $$

        Read this slowly — every piece is something you already have:

        - $y_1, y_2$ are the basis you found in Chapter 7 (or by
          characteristic equation, or by guess).
        - $W = y_1 y_2' - y_2 y_1'$ is one determinant of those two.
        - $g$ is the forcing you were handed.

        No guess table. No collision rule. **Any** continuous $g(x)$
        — $\tan x$, $\sec x$, $1/x$, a sampled road profile — goes
        through the same machine and produces a particular solution.
        """
    )
    return


# === Section 4.12 — Finale: assemble the general solution ========================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Finale — the full general solution

        We came in chasing $y_p$. The general solution of the
        non-homogeneous equation is then exactly what Chapter 7
        promised — the survivor plus the basis you started from:

        $$
        \boxed{\;\; y(x) \;=\; \underbrace{y_p(x)}_{\text{forced response}} \;+\; \underbrace{c_1\,y_1(x) \;+\; c_2\,y_2(x)}_{\text{free response}\,=\,y_h} \;\;}
        $$

        The two constants $c_1, c_2$ are the same two coordinates in
        the homogeneous basis we re-met in the Prologue — pinned
        down by initial conditions, exactly as before.

        **Looking back at the climb.** Saga 1 named the basis as a
        null space. Saga 2 named $y_p$ as the survivor $L$ couldn't
        crush. Sagas 3–6 armed the survivor with relic-functions and
        pushed it through $L$ until only the survivor-equation
        remained. Saga 7 packaged the two equations as a matrix; Saga
        8 read its determinant as area, and gave it the name
        Wronskian. Saga 9 inverted with Cramer; Saga 10 integrated
        and equipped. The Finale just reattaches the homogeneous
        coordinates.

        The detour into linear-algebra realm is over. You now have
        the one method that works on *every* continuous forcing — and
        you can see exactly *why* it works.
        """
    )
    return


# === Section 6 — Try it (3 graded exercises) ======================================

# --- Challenge 1: pick the right trial form -------------------------------------
@app.cell
def _(mo):
    # TODO: refine prompt + check once Section 3's table is filled in.
    e1_get, e1_set = mo.state(
        "# For  y'' + 4y = 3 e^{2x},  the standard trial form is\n"
        "# y_p = C e^{2x}. Substitute and solve for C.\n"
        "# Hint: 4 C e^{2x} (second derivative) + 4 C e^{2x} = 3 e^{2x},\n"
        "# so 8 C = 3 -> C = 3/8 = 0.375.\n"
        "# Put C in `answer`.\n"
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
        context="The forcing is 3 e^{2x}. Trial: y_p = C e^{2x}. "
                "Then y_p'' = 4 C e^{2x}. Substitute: 4 C e^{2x} + "
                "4 C e^{2x} = 3 e^{2x} -> 8 C = 3 -> C = 0.375. "
                "Put 0.375 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_ai, e1_code, e1_gen, e1_run):
    delib.exercise_view(
        "**1.** For $y'' + 4y = 3\\, e^{2x}$, find the coefficient $C$ "
        "in the particular solution $y_p = C\\, e^{2x}$.",
        e1_ai, e1_gen, e1_code, e1_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_code, e1_run):
    delib.run_exercise(e1_code.value, e1_run.value, check=lambda ns: delib.check_number(
        ns, target=0.375, tol=0.005,
        ok="Right — $y_p'' + 4 y_p = (4C + 4C) e^{2x} = 8C e^{2x} = "
           "3 e^{2x}$, so $C = 3/8 = 0.375$.",
        hint="Differentiate the trial twice, substitute into the LHS, "
             "match the coefficient of $e^{2x}$ on both sides.",
    ))
    return


# --- Challenge 2: superposition --------------------------------------------------
@app.cell
def _(mo):
    e2_get, e2_set = mo.state(
        "# For  y'' - y = 6 + e^{2x},  superposition says split the\n"
        "# forcing: y_p = y_{p,1} + y_{p,2} with\n"
        "#   y_{p,1} solves y'' - y = 6    (constant; try y_{p,1} = A)\n"
        "#   y_{p,2} solves y'' - y = e^{2x}  (try y_{p,2} = B e^{2x})\n"
        "# Compute y_p(0) = A + B.\n"
        "# Put the answer in `answer`.\n"
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
        context="Piece 1: y'' - y = 6, try y = A constant. Then "
                "y'' = 0 so -A = 6 -> A = -6. "
                "Piece 2: y'' - y = e^{2x}, try y = B e^{2x}. Then "
                "y'' = 4B e^{2x} so 4B - B = 1 -> B = 1/3. "
                "y_p(0) = -6 + 1/3 = -17/3 ~= -5.6667. "
                "Put -5.6667 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_ai, e2_code, e2_gen, e2_run):
    delib.exercise_view(
        "**2.** Use superposition: for $y'' - y = 6 + e^{2x}$, find "
        "$y_p(0)$.",
        e2_ai, e2_gen, e2_code, e2_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_code, e2_run):
    delib.run_exercise(e2_code.value, e2_run.value, check=lambda ns: delib.check_number(
        ns, target=-17/3, tol=0.01,
        ok="Right — constant piece: $-A = 6 \\Rightarrow A = -6$; "
           "exponential piece: $4B - B = 1 \\Rightarrow B = 1/3$; "
           "$y_p(0) = A + B = -17/3 \\approx -5.667$.",
        hint="Solve each forcing piece separately, then add the two "
             "particular solutions. Evaluate the sum at $x = 0$.",
    ))
    return


# --- Challenge 3: variation of parameters (Wronskian) ----------------------------
@app.cell
def _(mo):
    e3_get, e3_set = mo.state(
        "# For  y'' + y = 0,  a homogeneous basis is\n"
        "#   y_1 = cos(x),  y_2 = sin(x).\n"
        "# Compute the Wronskian W(x) = y_1 y_2' - y_2 y_1'.\n"
        "# (For sin/cos, this should be a constant.)\n"
        "# Put W in `answer`.\n"
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
        context="y_1 = cos x, y_2 = sin x. Then y_1' = -sin x, "
                "y_2' = cos x. W = y_1 y_2' - y_2 y_1' = "
                "cos(x) cos(x) - sin(x) (-sin x) = cos^2 + sin^2 = 1. "
                "Put 1 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_ai, e3_code, e3_gen, e3_run):
    delib.exercise_view(
        "**3.** For $y'' + y = g(x)$, the homogeneous basis is "
        "$y_1 = \\cos x$, $y_2 = \\sin x$. Compute the Wronskian "
        "$W = y_1 y_2' - y_2 y_1'$.",
        e3_ai, e3_gen, e3_code, e3_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_code, e3_run):
    delib.run_exercise(e3_code.value, e3_run.value, check=lambda ns: delib.check_number(
        ns, target=1.0, tol=0.001,
        ok="Right — $W = \\cos(x)\\cos(x) - \\sin(x)(-\\sin x) = "
           "\\cos^2 + \\sin^2 = 1$. The Wronskian is identically $1$, "
           "which makes the VoP integrals especially clean for this basis.",
        hint="Plug in $y_1' = -\\sin x$ and $y_2' = \\cos x$, then use "
             "$\\cos^2 + \\sin^2 = 1$.",
    ))
    return


# === Section 7 — Recap & what's next ==============================================
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ---
        ## Recap & what's next

        - **The split.** For a linear non-homogeneous equation,
          $y = y_h + y_p$. The freedom (two constants from initial
          conditions) lives entirely in $y_h$; $y_p$ is determined
          by the forcing.
        - **Superposition.** Sum of forcings → sum of particular
          responses. Solve each piece with whichever method is
          easiest, add at the end.
        - **Undetermined coefficients** — fast, mechanical, works
          for polynomials / exponentials / sinusoids / sums.
          Resonance overlap: multiply by $x$.
        - **Variation of parameters** — slower (two integrals) but
          works for any continuous $g(x)$.
        - **Same equation, many worlds.** A swing, a car over a
          road, an RLC circuit — all linear oscillators wear this
          form; once you know the method, you know all of them.

        **Next.** Chapter 9 introduces the **Laplace transform** —
        the natural tool for *switched* and *impulse* inputs (a
        battery flipping on at $t = 1\,\text{s}$, a sudden kick) —
        which UC and VoP handle awkwardly. Laplace turns the ODE
        itself into an algebraic equation in $s$, and the
        characteristic-equation "guessed" exponentials of Ch 6
        reappear as the **poles** of a transfer function.
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
def _(delib):
    picker = delib.cell_picker_widget()
    return (picker,)


@app.cell
def _(mo):
    picked_get, picked_set = mo.state({"text": "", "title": ""})
    return picked_get, picked_set


@app.cell
def _(picked_set, picker):
    _val = picker.value or {}
    picked_set({"text": _val.get("picked_text", ""),
                "title": _val.get("picked_title", "")})
    return


@app.cell
def _(api_field, delib, key_bridge, picked_get):
    chatbox = delib.tutor_chat(
        api_field, key_bridge,
        "This is Chapter 8 of a differential-equations course: "
        "non-homogeneous second-order linear equations of the form "
        "y'' + 2 gamma y' + omega0^2 y = g(t). It picks up Ch 7's "
        "two loose ends: (1) Ch 7 drove with a single cosine -- now "
        "the forcing g(t) can be ANY shape; (2) Ch 7 assumed "
        "x = x_h + x_p -- this chapter proves y = y_h + y_p is the "
        "COMPLETE general solution (it's a solution by linearity, and "
        "every solution has this form since Y - y_p solves the "
        "homogeneous equation). The hook is a car driving over a road "
        "whose vertical profile IS the forcing g(t) and whose chassis "
        "bob IS the response y(t) (same damped oscillator as the "
        "swing; stiffness = omega0, shocks = gamma). Key ideas: "
        "general solution splits as y = y_h + y_p with y_h handling "
        "initial conditions and y_p set entirely by the forcing; "
        "linearity gives superposition (sum of forcings -> sum of "
        "particulars); undetermined coefficients (guess-and-match) "
        "works for polynomials / exponentials / sinusoids / sums, "
        "with the multiply-by-x rescue when the trial collides with "
        "a homogeneous solution (the Ch 7 gamma=0 resonance case is "
        "the canonical example); variation of parameters handles ANY "
        "continuous g(x) via the Wronskian formula y_p = -y_1 int "
        "(y_2 g / W) dx + y_2 int (y_1 g / W) dx, derived in the "
        "chapter's Manim. Ch 9 next: Laplace transforms for switched / "
        "impulse inputs.",
        prompts=[
            "explain this chapter in a paragraph",
            "when should I use UC vs variation of parameters?",
            "why does the multiply-by-x trick work at resonance?",
        ],
        picked_get=picked_get,
    )
    return (chatbox,)


@app.cell(hide_code=True)
def _(api_field, chatbox, delib, key_bridge, picker):
    delib.tutor_sidebar(api_field, key_bridge, chatbox, picker=picker)
    return


# --- Feedback ------------------------------------------------------------------
@app.cell(hide_code=True)
def _(delib):
    delib.feedback_form("Chapter 8 — Non-homogeneous equations")
    return


if __name__ == "__main__":
    app.run()
