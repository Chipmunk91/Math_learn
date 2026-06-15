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
        # Chapter 7 — Damping, forcing, resonance

        **When something pushes back, periodically.**

        By the end of this chapter you should be able to:

        - Write a damped, driven oscillator as
          $\ddot x + 2\gamma\dot x + \omega_0^2 x = F_0 \cos(\omega t)$,
          identifying each constant with a physical meaning
          (natural frequency, damping rate, drive amplitude and
          frequency).
        - Split a driven solution into a **transient** part (from
          Chapter 6, dies away) and a **steady-state** part (locked
          to the drive, lives forever); know that all the
          interesting long-time behaviour lives in the steady
          state.
        - Read the **amplitude curve** $A(\omega)$ and the
          **phase-lag curve** $\varphi(\omega)$: locate the peak,
          recognise the in-phase / quarter-phase / anti-phase
          regimes, and explain *why* a swing builds up only when
          pushed at the right rhythm.
        - Identify **resonance** as the peak of $A(\omega)$ near
          $\omega = \omega_0$, and understand both its practical
          value (every musical instrument, every transmitter) and
          its hazard (Tacoma Narrows).
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, mo):
    # Section 1 — hook: same swing, two drive frequencies. Right
    # rhythm climbs; wrong rhythm doesn't. The two animated panels are
    # the chapter's pitch: same equation, same damping, same push
    # amplitude — only the drive frequency differs.
    #
    # omega0 = 2 (so the natural period is pi ~ 3.14); gamma = 0.08 is
    # light damping; the right-rhythm drive matches omega0, the
    # wrong-rhythm drive is well off (omega ~ 0.7).
    _omega0 = 2.0
    _gamma = 0.08
    _F0 = 1.0
    _omega_right = 2.0   # exactly on resonance
    _omega_wrong = 0.7   # well below — off-rhythm

    _fig_right = delib.oscillator_animate(
        _omega0, _gamma, _F0, _omega_right,
        ic=(0.0, 0.0), t_end=40.0, n_points=600,
        title=f"Right rhythm: drive at ω = {_omega_right} (= ω₀)",
        ylim=(-7.5, 7.5),
    )
    _fig_wrong = delib.oscillator_animate(
        _omega0, _gamma, _F0, _omega_wrong,
        ic=(0.0, 0.0), t_end=40.0, n_points=600,
        title=f"Wrong rhythm: drive at ω = {_omega_wrong}",
        ylim=(-7.5, 7.5),
    )

    mo.vstack([
        mo.md(
            r"""
            ## Pushing at the right rhythm

            A parent pushing a child on a swing learns one rule on
            day one: **time the pushes right and the swing climbs;
            time them wrong and it doesn't.** Same parent, same
            arm strength, same swing — but a push at the right
            rhythm builds the arc into a soaring sweep, while a
            push at the wrong rhythm just jiggles the kid around
            the bottom.

            Watch the same idea in two panels below. Both panels
            integrate the **same equation** — the swing's position
            $x(t)$ obeys

            $$
            \ddot x + 2\gamma\,\dot x + \omega_0^2\,x \;=\; F_0\cos(\omega t),
            $$

            where the three constants are the swing's own rhythm
            $\omega_0$, the friction $\gamma$, and the push (amplitude
            $F_0$, rhythm $\omega$). Don't worry about where this
            comes from yet — we build it piece by piece two sections
            from now. For the panels, every constant is held fixed
            except the **drive frequency $\omega$**: the left panel
            pushes at $\omega = \omega_0$ (the swing's own rhythm),
            the right at a different $\omega$. Both start from rest
            at $x = 0$; the dashed curve is the push $\cos(\omega t)$,
            the solid is the motion $x(t)$. Press ▶ on each:
            """
        ),
        mo.hstack([_fig_right, _fig_wrong], justify="space-between",
                  widths="equal", gap=0.5),
        mo.md(
            r"""
            On the **left**, the push is at the swing's *natural*
            rhythm. Each cycle the response grows a little; after
            half a minute the swing is sweeping seven times the
            push amplitude. On the **right**, the push is at a
            different rhythm. The swing reaches some steady
            wiggle, but it's small — and that wiggle isn't even
            *with* the push; the swing is just being pulled around
            mechanically.

            Same equation, same energy input per push. What makes
            the left side win? That's what the chapter answers.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 2 — concept bridge. From Ch 6 (homogeneous, decays) to
    # Ch 7 (driven, doesn't). Earn the transient + steady-state
    # decomposition by *looking at the previous figure*.
    mo.md(
        r"""
        ## The decay we lost, and the rhythm we gained

        Take a quick look back at Chapter 6's recap. There, every
        damped equation we wrote down had the same fate: the motion
        eventually **decayed** to zero. Friction always won; given
        enough time, the swing came to rest no matter what.

        So why doesn't a **driven** swing just decay too? Same
        damping! What's different is that **something keeps adding
        energy to it**. The forcing term — the new $F_0\cos(\omega t)$
        on the right-hand side of the equation — is the parent pumping
        in fresh energy every cycle.

        Now the full motion **splits into two pieces** — and it's
        worth seeing *why*, because it isn't a trick. The equation
        forces it.

        **The picture first.** A pushed swing lives two lives at once:

        - the **rhythm the pushing locks it into** — a steady
          back-and-forth at the parent's pace, which it would keep up
          forever; and
        - the **leftover wobble from how it happened to start** — the
          same free, dying motion as Chapter 6.

        What you see is just these two **added together**: one stays,
        one fades.

        **Why we're allowed to add them.** The left side, $\ddot x +
        2\gamma\dot x + \omega_0^2 x$, only ever differentiates,
        scales, and adds. Do any of those to a *sum* and you get the
        *sum* of the results — so two motions stacked on top of each
        other still obey the law. (That property has a name:
        **linearity**.)

        That lets us build the hard motion out of two easy ones:

        - $x_p$ **rides the forcing** — feed it into the left side and
          out comes exactly $F_0\cos(\omega t)$;
        - $x_h$ is a **correction** we lay on top to fix the start.

        Stack them, $x = x_p + x_h$, and the left side returns
        $F_0\cos(\omega t) + (\text{what } x_h \text{ gives})$. For
        the total to stay correct, $x_h$ must give **zero** — it must
        solve the *unforced* equation

        $$
        \ddot x_h + 2\gamma\dot x_h + \omega_0^2 x_h \;=\; 0.
        $$

        Those are exactly **Chapter 6's free motions** — what the
        swing does on its own, nobody pushing — and they come with
        **two spare constants**: precisely the freedom to set the
        starting position and velocity right.

        That's the whole decomposition, and now it's earned:

        $$
        x(t) \;=\; \underbrace{x_h(t)}_{\text{transient}}
        \;+\; \underbrace{x_p(t)}_{\text{steady state}}.
        $$

        The piece $x_h$ — Chapter 6's free motion — had roots with
        negative real part whenever $\gamma > 0$, so it **decays
        away**. It's a fleeting adjustment that fixes the start and
        then dies: the "transient." In the first few seconds of a
        driven swing the motion wobbles and twitches as the initial
        conditions get sorted, then settles into a clean steady
        oscillation. That early wobble *is* $x_h$, dying off.

        The piece $x_p$ is the genuinely new thing the forcing makes
        possible. It doesn't decay; it locks onto the drive's rhythm
        and keeps going as long as the push keeps coming. After the
        transient has died, **all that's left is the steady state**.

        Watch the split *happen* in the panel just below. The
        choreography plays it as a four-act story: the full solution
        draws in, separates into its transient and steady-state
        pieces, the transient fades to nothing as time sweeps, and the
        steady state returns alone. Press ▶, or drag the scrubber to
        move through it at your own pace.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Section 2 (interactive) — GSAP anatomy of x = x_h + x_p,
    # graduated from the animation lab. Same constants as the prose
    # discusses (lightly damped, driven off-resonance).
    delib.solution_anatomy(omega0=2.0, gamma=0.25, omega=1.2, F0=1.0)
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 2 (wrap-up) — the two forward questions that motivate the
    # amplitude/phase story, placed AFTER the split animation so the
    # reader has just watched the decomposition they refer to.
    mo.md(
        r"""
        With the split in hand, two questions set up the rest of the
        chapter:

        1. *What does the steady state look like?* It will turn out to
           be a cosine at the drive frequency, with some amplitude $A$
           and some phase lag $\varphi$ relative to the push. Both are
           determined by the equation.
        2. *How big is $A$, and how does it depend on $\omega$?* That
           dependence is the resonance story. The off-rhythm swing
           settles to a small $A$; the resonant swing climbs to a huge
           one. We want the formula.

        The steady state is what we'll spend the rest of the chapter
        pinning down.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 3 — build the equation. Earn each term and the canonical
    # constants. Damping ratio mentioned but not over-emphasised.
    mo.md(
        r"""
        ## Building the equation

        The swing's bobbing-from-Chapter-6 part comes from the same
        two ingredients we used there: a restoring force
        proportional to displacement, and Newton's $F = m\ddot x$.
        Two new ingredients enter the equation now.

        **Damping.** Friction with the air (and at the swing's
        pivot) drags against motion. It's well-modelled as a force
        proportional to *velocity*, opposing it:
        $F_{\text{friction}} = -c\dot x$ with $c \ge 0$. A fast
        swing feels more drag than a slow one; a stationary swing
        feels none.

        **External forcing.** The parent's hand applies an extra,
        time-varying force — push, wait, push, wait. For the
        cleanest case (and a surprisingly accurate model for
        rhythmic pushing), take it sinusoidal:
        $F_{\text{drive}} = F_0 \cos(\omega t)$, with amplitude
        $F_0$ and frequency $\omega$.

        Newton's law $m\ddot x = \text{net force}$ assembles these:

        $$
        m\,\ddot x \;=\; -k\,x \;-\; c\,\dot x \;+\; F_0\cos(\omega t).
        $$

        Divide through by $m$ and rename constants for cleaner
        algebra later: let $\omega_0 = \sqrt{k/m}$ (the **natural
        frequency** — what the swing would do on its own with no
        friction and no push), $2\gamma = c/m$ (the **damping
        rate**), and absorb $F_0 / m \to F_0$. The canonical form
        is

        $$
        \boxed{\quad
        \ddot x + 2\gamma\,\dot x + \omega_0^2\,x \;=\; F_0\cos(\omega t)
        \quad}
        $$

        — and from here on out, "the equation" means this one.

        Three physical knobs you can turn:

        - $\omega_0$ — set by *what kind of swing it is*. Longer
          swing → smaller $\omega_0$, slower natural rhythm.
        - $\gamma$ — set by *how much friction*. Light damping is
          $\gamma \ll \omega_0$; heavy damping is $\gamma$
          comparable to $\omega_0$.
        - $\omega$ — set by *how you push*. Independent of the
          other two; the whole resonance story is about what
          happens as you sweep $\omega$.

        The factor of $2$ in $2\gamma$ looks awkward at first but
        makes the characteristic equation in Chapter 6 come out as
        $r^2 + 2\gamma r + \omega_0^2 = 0$, whose roots are
        $r = -\gamma \pm \sqrt{\gamma^2 - \omega_0^2}$. Convention.
        Live with it; the algebra rewards you.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 4 (intro) — frame the derivation that follows in the
    # Manim. The ansatz, the substitution, the matching, the
    # algebraic isolation.
    mo.md(
        r"""
        ## Pinning down the steady state

        Let's reconnect to where we are. Back in the bridge section
        we split the motion into two parts,
        $x(t) = x_h(t) + x_p(t)$: the **transient** $x_h$ (Chapter
        6's solution, which dies away) plus the **steady state**
        $x_p$ (the part locked to the push, which lives forever).
        After you wait a few seconds the transient is gone, so
        *the steady state is the motion you actually see* — the
        clean repeating swing in the animations above. "Find a
        formula for $x_p$" simply means: **write down what that
        long-term swinging motion is.** That's the goal of this
        section.

        We could grind it out, but there's a shortcut: we can
        *guess the shape* of $x_p$ from two facts, and then only
        have to find a couple of numbers. Here are the two facts.

        **Fact one: the answer is a sinusoid at the push's
        frequency.** Why? Look at the left side of the equation,
        $\ddot x + 2\gamma\dot x + \omega_0^2 x$. It does only three
        things to $x$: differentiate it, scale it, and add the
        pieces. None of those operations invents a new frequency.
        Differentiate $\cos(\omega t)$ and you get $-\omega
        \sin(\omega t)$ — still frequency $\omega$. Scale it,
        add two of them together — still frequency $\omega$. (This
        is what the word **linear** is buying us: $x$ and its
        derivatives appear only on their own, to the first power,
        never squared or multiplied together or stuffed inside
        another function. An equation built only from
        "differentiate, scale, add" can't turn one frequency into
        another.) So if the push on the right is a pure $\omega$
        sinusoid, the only way the left side can possibly match it
        is if $x_p$ is *also* a pure $\omega$ sinusoid. Any other
        frequency would have nothing on the right to balance
        against.

        **Fact two: it may be shifted in time.** The swing needn't
        peak at the same instant the push peaks — it can lag behind.
        A sinusoid at frequency $\omega$ has exactly two adjustable
        features: how *big* it is, and *when* it peaks. Call the
        size $A$ (the amplitude) and the timing offset $\varphi$
        (the phase lag). The general frequency-$\omega$ sinusoid
        with those two knobs is

        $$
        x_p(t) \;=\; A\cos(\omega t - \varphi).
        $$

        The $-\varphi$ inside is just a sign convention: a positive
        $\varphi$ shifts the peak *later* than the push's peak, so
        $\varphi$ reads directly as "how far the swing lags behind."

        So the shape is fixed, and only **two numbers** are left to
        find: the amplitude $A$ and the lag $\varphi$. We pin them
        down the only way available — substitute this guess into
        the equation and demand that it actually hold for all $t$.
        The video runs that substitution from start to finish; out
        the other end comes a formula for $A$ and one for $\varphi$,
        each in terms of the three knobs $\omega_0$, $\gamma$,
        $\omega$.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    # Section 4 — Manim hero: derive A(omega) and phi(omega) by
    # substitution and coefficient matching.
    delib.video(
        "forced_oscillator_steady_state.mp4",
        caption="Steady state of  ẍ + 2γẋ + ω₀²x = F₀ cos(ωt)  →  A(ω), φ(ω)",
        fallback="The steady-state derivation animation is being rendered "
                 "(see manim/forced_oscillator_steady_state.py).",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 4 (post-video) — name the formulas and the headline.
    mo.md(
        r"""
        Two formulas come out of that derivation. The amplitude is

        $$
        A(\omega) \;=\; \frac{F_0}{\sqrt{(\omega_0^2 - \omega^2)^2 + (2\gamma\omega)^2}},
        $$

        and the phase lag is

        $$
        \varphi(\omega) \;=\; \arctan\!\frac{2\gamma\omega}{\omega_0^2 - \omega^2}.
        $$

        Stare at $A(\omega)$ for a moment. The denominator's first
        piece, $(\omega_0^2 - \omega^2)^2$, vanishes when
        $\omega = \omega_0$ — exactly at the swing's natural
        frequency. With **no damping**, that would make $A$
        infinite at resonance. With damping turned on, the second
        piece $(2\gamma\omega)^2$ keeps the denominator from ever
        hitting zero — but when $\gamma$ is small, it stays *very*
        small near $\omega = \omega_0$, and the amplitude soars.

        That's the resonance story in one line. The next two
        figures make it visible.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 5 — hero #1: the amplitude curve, with omega_0 and
    # gamma sliders. The peak's location and height as a function
    # of damping is the whole content of this section.
    mo.md(
        r"""
        ## The amplitude curve — where the swing peaks

        Plot the amplitude $A$ as a function of the drive frequency
        $\omega$, for fixed system constants $\omega_0$ and
        $\gamma$. This is the **frequency response** — the single
        most-consulted figure in the linear-systems toolbox.

        Drag the sliders below:

        - **$\omega_0$ — natural frequency.** Sets *where* the
          peak sits on the $\omega$ axis. Big $\omega_0$ → fast
          system, peak on the right. The grey dotted line in the
          figure marks $\omega_0$ exactly.
        - **$\gamma$ — damping rate.** Sets the peak's *height*.
          Tiny $\gamma$ → a sharp, towering spike; large $\gamma$
          → a fat, low bump. Push $\gamma$ high enough and the
          peak vanishes altogether (an overdamped system has no
          resonance to peak at).

        Two limiting behaviours worth noticing as you scrub:

        - **At $\omega = 0$** (a "push" that doesn't change with
          time — a static pull), the response is the steady
          deflection $A(0) = F_0/\omega_0^2$. A stiff spring
          ($\omega_0$ big) deflects less under the same constant
          pull — the static spring constant from physics class.
        - **At $\omega \to \infty$** (a push so rapid the system
          can't keep up), $A \to 0$. The drive averages itself out
          before the mass has time to respond.

        Between those limits, the amplitude rises, peaks just
        slightly *below* $\omega_0$ (you can find the exact
        location yourself in Challenge 1), and falls again.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    fr_panel = delib.param_panel([
        {"name": "omega0", "label": "natural freq.  ω₀",
         "start": 0.5, "stop": 4.0, "step": 0.1, "value": 2.0},
        {"name": "gamma", "label": "damping rate  γ",
         "start": 0.05, "stop": 2.0, "step": 0.05, "value": 0.3},
    ])
    return (fr_panel,)


@app.cell(hide_code=True)
def _(delib, fr_panel, mo):
    _omega0 = float(fr_panel.value["omega0"])
    _gamma = float(fr_panel.value["gamma"])

    _fig = delib.frequency_response(
        _omega0, _gamma, F0=1.0,
        title=f"Frequency response   ω₀ = {_omega0:.2f}, γ = {_gamma:.2f}",
    )
    mo.vstack([fr_panel, _fig])
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 5 (interactive) — hear the same curve. The peak is far
    # more visceral as a swell of loudness than as a bump on a plot.
    mo.md(
        r"""
        You've *seen* the peak; now **hear** it. The widget below
        plays a tone whose pitch follows the drive frequency and
        whose loudness follows the very amplitude $A(\omega)$ plotted
        above. Enable sound and sweep $\omega$ slowly across $\omega_0$
        (the dotted line): the system swells loud right at resonance,
        then fades as you pass it. Tighten the damping and the loud
        band narrows to a knife-edge — that's a high-$Q$ resonator,
        the principle behind every tuned circuit and every string.
        """
    )
    return


@app.cell(hide_code=True)
def _(delib):
    delib.resonance_audio(omega0=2.0, gamma=0.15, F0=1.0)
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 6 — phase: why "right rhythm" matters. Animated
    # side-by-side comparison of drive vs response at two phases,
    # plus the prose connecting phase to energy transfer.
    mo.md(
        r"""
        ## Why the right rhythm works — the phase story

        The lower panel above is just as important as the upper
        one. It shows the **phase lag** $\varphi$, in units of
        $\pi$, vs the drive frequency $\omega$. Three regimes are
        worth naming:

        - **Below resonance ($\omega \ll \omega_0$):** $\varphi
          \approx 0$. The swing moves *in phase* with the push —
          pushing right, swing goes right. Intuitive.
        - **At resonance ($\omega = \omega_0$):** $\varphi =
          \pi/2$. The swing is **a quarter cycle behind** the
          push.
        - **Above resonance ($\omega \gg \omega_0$):** $\varphi
          \to \pi$. The swing moves *opposite* to the push — push
          right, swing goes left (and vice versa). Counter-
          intuitive but true: drive a slow system fast enough and
          it'll fight you on every cycle.

        The quarter-phase lag at resonance is the secret of the
        whole chapter. When the swing lags the push by exactly
        $\pi/2$, what does that mean for the *timing*? The push
        is at its maximum *when the swing is moving through zero
        at top speed*. So every push catches the swing exactly at
        its fastest moment — and pumping force × velocity is the
        rate of energy added. **Every cycle, every parent's push
        lands when it can transfer the most energy.** That's
        resonance: the geometry of phase makes energy transfer
        maximal.

        Below, two animated comparisons. Same system, same drive
        amplitude. Only the drive frequency differs. Watch the
        timing between the dashed line (push) and the solid line
        (swing):
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, mo):
    # Section 6 — two-panel animation: drive vs response, in-phase
    # case (omega well below resonance) and quarter-phase case
    # (omega at resonance). Same omega0 and gamma in both.
    _omega0 = 2.0
    _gamma = 0.15
    _F0 = 1.0

    _fig_inphase = delib.oscillator_animate(
        _omega0, _gamma, _F0, omega=0.6,
        ic=(0.0, 0.0), t_end=30.0, n_points=500,
        title="Below resonance  (ω = 0.6 ≪ ω₀ = 2): swing in phase with push",
        ylim=(-1.5, 1.5),
    )
    _fig_resonant = delib.oscillator_animate(
        _omega0, _gamma, _F0, omega=2.0,
        ic=(0.0, 0.0), t_end=30.0, n_points=500,
        title="At resonance  (ω = ω₀ = 2): swing a quarter cycle behind push",
        ylim=(-5.0, 5.0),
    )

    mo.vstack([
        mo.hstack([_fig_inphase, _fig_resonant],
                  justify="space-between", widths="equal", gap=0.5),
        mo.md(
            r"""
            On the **left**: push and swing rise and fall together,
            same rhythm. The swing's amplitude is small — there's
            no opportunity for the push to do much work because the
            push is fighting the velocity half the time it's
            applied. On the **right**: every push peak (dashed)
            lands during a swing zero-crossing (solid passes through
            $0$), which is exactly when the swing is fastest. Every
            push adds energy. The amplitude climbs and climbs until
            damping finally balances the energy input.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 7 — the gamma -> 0 limit. Resonance disaster, real
    # systems' nonlinear saturation, Tacoma Narrows.
    mo.md(
        r"""
        ## What happens at $\gamma = 0$ — the resonance disaster

        Look one more time at the amplitude formula:

        $$
        A(\omega) \;=\; \frac{F_0}{\sqrt{(\omega_0^2 - \omega^2)^2 + (2\gamma\omega)^2}}.
        $$

        Set $\gamma = 0$ (no damping at all) and drive the system
        at exactly $\omega = \omega_0$ (resonance). The
        denominator becomes $\sqrt{0 + 0} = 0$, and $A$ shoots to
        **infinity**.

        That's not a glitch in the math; it really does happen in
        the idealised model. A frictionless oscillator at
        resonance keeps absorbing energy without limit, and its
        amplitude grows **linearly with time**, not toward a
        steady value. The right ansatz at $\omega = \omega_0$ with
        $\gamma = 0$ is

        $$
        x_p(t) \;=\; \frac{F_0}{2\omega_0}\,t\,\sin(\omega_0 t)
        $$

        — a sine whose envelope $t$ rises straight up. (We won't
        derive this here; you can plug it in and check it works.
        Or: think of it as the boundary-case version of the
        repeated-root trick from Chapter 6, where one of the basis
        solutions needed an extra factor of $t$.)

        **In reality, two things rescue you.** First, real systems
        always have *some* damping, so the denominator never quite
        hits zero. Second, when the amplitude grows large enough,
        the linear approximation we made in Section 3 breaks down
        — a real spring stretched too far stops obeying Hooke's
        law, the swing's geometry gets non-planar, materials
        yield. The infinity in our formula is the math's way of
        warning you that linear theory is about to fail.

        It's *also* the math's way of warning **engineers**. On
        7 November 1940, the Tacoma Narrows suspension bridge
        oscillated itself to destruction in a moderate wind. The
        wind wasn't strong; what it *was* was at a frequency the
        bridge happened to resonate with, and the bridge's
        damping was very low. Same equation, same disaster. The
        amplitude climbed for nearly an hour before the deck tore
        free. (The post-mortem on the exact mechanism is more
        subtle than pure linear resonance, but the qualitative
        story is the one above.)

        Conversely, when you *want* large amplitude from a small
        push — every musical instrument, every radio transmitter,
        every MRI machine — you tune $\omega$ to $\omega_0$ on
        purpose. The same effect that destroyed Tacoma Narrows
        is what lets a flute resonate from a breath of air.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Try it — in code

        Three challenges, one per skill: find the peak frequency
        from the system constants; compute the steady-state
        amplitude at resonance; and read off the phase regime for
        a given drive. `delib.steady_state_amplitude(omega0, gamma,
        F0, omega)`, `delib.steady_state_phase(omega0, gamma,
        omega)`, and `delib.peak_frequency(omega0, gamma)` are
        available if you want to check yourself.
        """
    )
    return


# --- Challenge 1: peak frequency ------------------------------------------------
@app.cell
def _(mo):
    e1_get, e1_set = mo.state(
        "# For a system with omega0 = 3.0 and gamma = 0.5, find the\n"
        "# DRIVE frequency omega at which the steady-state amplitude\n"
        "# A(omega) peaks. (Hint: it is slightly below omega0.)\n"
        "# Closed form: omega_peak = sqrt(omega0**2 - 2*gamma**2).\n"
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
        context="omega_peak = sqrt(omega0**2 - 2*gamma**2) = "
                "sqrt(9 - 0.5) = sqrt(8.5) ~ 2.9155. "
                "delib.peak_frequency(3.0, 0.5) also gives this.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_ai, e1_code, e1_gen, e1_run):
    delib.exercise_view(
        "**1.** For $\\omega_0 = 3$ and $\\gamma = 0.5$, find the drive "
        "frequency $\\omega$ at which the amplitude $A(\\omega)$ peaks. "
        "(Closed form: $\\omega_{\\text{peak}} = \\sqrt{\\omega_0^2 - 2\\gamma^2}$.)",
        e1_ai, e1_gen, e1_code, e1_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e1_code, e1_run):
    delib.run_exercise(e1_code.value, e1_run.value, check=lambda ns: delib.check_number(
        ns, target=2.9155, tol=0.01,
        ok="Right — $\\omega_{\\text{peak}} = \\sqrt{9 - 0.5} = \\sqrt{8.5} "
           "\\approx 2.9155$, slightly below $\\omega_0 = 3$. Damping pulls "
           "the peak left of the natural frequency.",
        hint="Differentiate $A(\\omega)^2$ in $\\omega^2$, set it to zero, "
             "and solve. Or just plug $\\omega_0 = 3$ and $\\gamma = 0.5$ "
             "into the closed form.",
    ))
    return


# --- Challenge 2: amplitude at resonance ----------------------------------------
@app.cell
def _(mo):
    e2_get, e2_set = mo.state(
        "# A driven oscillator has omega0 = 2.0, gamma = 0.1, F0 = 1.0.\n"
        "# It is driven exactly at its natural frequency, omega = omega0.\n"
        "# What is the steady-state amplitude A(omega)? Put it in `answer`.\n"
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
        context="At omega = omega0, (omega0^2 - omega^2) = 0, so the "
                "amplitude is F0 / (2 gamma omega) = 1 / (2 * 0.1 * 2) "
                "= 1 / 0.4 = 2.5. Put 2.5 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_ai, e2_code, e2_gen, e2_run):
    delib.exercise_view(
        "**2.** A system has $\\omega_0 = 2$, $\\gamma = 0.1$, $F_0 = 1$, "
        "driven at exactly $\\omega = \\omega_0$. Compute the steady-state "
        "amplitude $A$.",
        e2_ai, e2_gen, e2_code, e2_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e2_code, e2_run):
    delib.run_exercise(e2_code.value, e2_run.value, check=lambda ns: delib.check_number(
        ns, target=2.5, tol=0.02,
        ok="Right — at $\\omega = \\omega_0$ the first term in the "
           "denominator vanishes and $A = F_0/(2\\gamma\\omega_0) = "
           "1/0.4 = 2.5$. Note: 2.5× the static deflection, with only "
           "$F_0 = 1$ driving it. Pure resonance gain.",
        hint="Plug $\\omega = \\omega_0$ into the amplitude formula. The "
             "$(\\omega_0^2 - \\omega^2)^2$ term zeros out.",
    ))
    return


# --- Challenge 3: phase regime --------------------------------------------------
@app.cell
def _(mo):
    e3_get, e3_set = mo.state(
        "# A system with omega0 = 1.0 and gamma = 0.2 is driven at\n"
        "# omega = 1.0 (exactly on resonance). What is the phase lag\n"
        "# phi (in units of pi) between the response and the drive?\n"
        "# Put the value of phi/pi in `answer`.\n"
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
        context="At omega = omega0, (omega0^2 - omega^2) = 0, so "
                "tan(phi) = 2 gamma omega / 0 -> infinity, hence "
                "phi = pi/2. In units of pi this is 0.5. "
                "Put 0.5 in `answer`.",
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_ai, e3_code, e3_gen, e3_run):
    delib.exercise_view(
        "**3.** A system with $\\omega_0 = 1$ and $\\gamma = 0.2$ is "
        "driven exactly at resonance, $\\omega = \\omega_0$. What is "
        "$\\varphi / \\pi$? (Phase lag in units of $\\pi$.)",
        e3_ai, e3_gen, e3_code, e3_run,
    )
    return


@app.cell(hide_code=True)
def _(delib, e3_code, e3_run):
    delib.run_exercise(e3_code.value, e3_run.value, check=lambda ns: delib.check_number(
        ns, target=0.5, tol=0.005,
        ok="Right — at resonance $\\tan\\varphi$ blows up, so "
           "$\\varphi = \\pi/2$ — the quarter-cycle lag that makes every "
           "push land at peak velocity. This value is *independent of "
           "$\\gamma$*: every resonant system has the same phase lag.",
        hint="Use the phase formula $\\tan\\varphi = 2\\gamma\\omega / "
             "(\\omega_0^2 - \\omega^2)$ and notice what happens to the "
             "denominator at $\\omega = \\omega_0$.",
    ))
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
        "This is Chapter 7 of a differential-equations course: the "
        "damped, driven harmonic oscillator. Canonical equation: "
        "x'' + 2 gamma x' + omega0^2 x = F0 cos(omega t). The story "
        "is built around a child on a swing: pushing at the natural "
        "rhythm (omega = omega0) builds large amplitude; pushing at "
        "a wrong rhythm doesn't. Key ideas: solution = transient (Ch "
        "6's homogeneous part, decays) + steady-state (locked to "
        "drive); steady-state x_p = A cos(omega t - phi) with closed "
        "forms A(omega) = F0 / sqrt((omega0^2 - omega^2)^2 + "
        "(2 gamma omega)^2) and tan(phi) = 2 gamma omega / "
        "(omega0^2 - omega^2); peak at omega_peak = "
        "sqrt(omega0^2 - 2 gamma^2) (slightly below omega0); at "
        "resonance phi = pi/2 makes every push land at peak "
        "velocity, maximising energy transfer. gamma = 0 limit gives "
        "unbounded growth (Tacoma Narrows). Earlier chapters: slope "
        "fields (Ch 1), separable/linear (Ch 2), exact equations "
        "(Ch 3), numerical methods (Ch 4), 1-D fixed points (Ch 5), "
        "second-order linear with constant coefficients (Ch 6).",
        prompts=[
            "explain this chapter in a paragraph",
            "why is the phase lag exactly pi/2 at resonance?",
            "why does the peak sit slightly below omega0?",
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
        ---
        ## Recap & what's next

        - **Forcing breaks the decay.** A damped, unforced
          oscillator always comes to rest. Add a periodic push and
          the motion splits as $x = x_h + x_p$: a transient from
          Chapter 6 (dies away) plus a steady state at the drive's
          frequency (lives forever).
        - **The canonical equation:**
          $\ddot x + 2\gamma\dot x + \omega_0^2 x = F_0\cos(\omega t)$.
          Three physical knobs — natural frequency $\omega_0$,
          damping $\gamma$, drive frequency $\omega$.
        - **The amplitude formula:**
          $A(\omega) = F_0 / \sqrt{(\omega_0^2 - \omega^2)^2 +
          (2\gamma\omega)^2}$. Peak at $\omega_{\text{peak}} =
          \sqrt{\omega_0^2 - 2\gamma^2}$, slightly below
          $\omega_0$; height $\sim F_0 / (2\gamma\omega_0)$
          at resonance.
        - **The phase formula:**
          $\tan\varphi = 2\gamma\omega / (\omega_0^2 - \omega^2)$.
          Below resonance the response is in phase with the drive;
          at resonance it lags by $\pi/2$ (peak push meets peak
          velocity, max energy transfer); above resonance it
          fights the drive ($\varphi \to \pi$).
        - **At $\gamma = 0$ and $\omega = \omega_0$** the
          amplitude grows linearly with time forever. Real systems
          are rescued by friction or by leaving the linear regime;
          engineers tune *toward* this point for instruments and
          *away* from it for bridges.

        **Next:** so far the system has had one mass and one
        spring. The next chapter introduces **Laplace transforms** —
        a third way to solve linear ODEs that turns initial
        conditions and forcing into algebraic operations on a
        transformed function $X(s)$, and explains the "guessed"
        exponentials of Chapter 6 as roots of a transformed
        denominator. After that we step into **systems of ODEs**,
        where two or more state variables interact.
        """
    )
    return


# --- Feedback (replaces the old playground) ------------------------------------
@app.cell(hide_code=True)
def _(delib):
    delib.feedback_form("Chapter 7 — Damping, forcing, resonance")
    return


if __name__ == "__main__":
    app.run()
