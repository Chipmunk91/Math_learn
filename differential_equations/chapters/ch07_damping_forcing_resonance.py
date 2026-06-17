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
    # Section 3 — build the equation, recap-first. Newton's law; recall
    # Ch 6's TWO forces (restoring + damping — damping is NOT new, Ch 6
    # already did it); add the one genuinely new term (the push); tidy to
    # the canonical form.
    mo.md(
        r"""
        ## Building the equation

        Back to **Newton's second law**: a mass obeys $F = m\ddot x$,
        where $F$ is the *total* force on it. So writing the swing's
        equation is just a matter of listing the forces — and
        Chapter 6 already found most of them.

        **Recall Chapter 6.** A swing left to itself feels two forces:

        - a **restoring pull** back toward the bottom, proportional to
          how far it has swung and always pointing home: $-k\,x$;
        - a **damping** drag from friction and the air, proportional to
          how *fast* it moves and always opposing it: $-c\,\dot x$.

        Newton's law adds them into Chapter 6's swing:

        $$
        m\ddot x \;=\; -k\,x \;-\; c\,\dot x.
        $$

        Left alone, that swing only ever coasts to rest — the damping
        drains it, every time. (Chapter 6 is where we solved it and saw
        the decay.)

        **Chapter 7 adds exactly one thing: the push.** The parent's
        hand puts an extra force on the swing that wasn't there before.
        For rhythmic pushing — shove, let it swing, shove again — the
        clean model is a cosine:

        $$
        F_{\text{push}}(t) \;=\; F_0\cos(\omega t),
        $$

        where $F_0$ is **how hard** each push is and $\omega$ is **how
        often** the pushes come (the *drive frequency*). Drop it onto
        the end of the force list:

        $$
        m\ddot x \;=\; -k\,x \;-\; c\,\dot x \;+\; F_0\cos(\omega t).
        $$

        That's the whole equation: everything from Chapter 6, plus the
        one new term on the right.

        **Tidy it up.** Divide through by $m$ and rename constants for
        cleaner algebra: let $\omega_0 = \sqrt{k/m}$ (the **natural
        frequency** — the rhythm the swing keeps on its own), let
        $2\gamma = c/m$ (the **damping rate**), and fold the leftover
        $F_0/m$ back into $F_0$. The canonical form is

        $$
        \boxed{\quad
        \ddot x + 2\gamma\,\dot x + \omega_0^2\,x \;=\; F_0\cos(\omega t)
        \quad}
        $$

        — and from here on, "the equation" means this one. Notice the
        left-hand side is **Chapter 6's, untouched**; all that's new is
        the push on the right.

        Three knobs you can turn:

        - $\omega_0$ — set by *what kind of swing it is* (a longer swing
          has a smaller $\omega_0$, a slower natural rhythm);
        - $\gamma$ — set by *how much friction* (light damping is
          $\gamma \ll \omega_0$);
        - $\omega$ — set by *how you push*, independent of the other
          two. The whole resonance story is about what happens as you
          sweep $\omega$.

        (The factor of $2$ in $2\gamma$ is just convention — it makes
        Chapter 6's characteristic equation
        $r^2 + 2\gamma r + \omega_0^2 = 0$ come out tidy, with roots
        $r = -\gamma \pm \sqrt{\gamma^2 - \omega_0^2}$.)
        """
    )
    return


@app.cell(hide_code=True)
def _(delib, mo):
    # Section 4 (motivation) — math-first reorder. Start from the
    # equation we just built. Split the unknown into x = x_h + x_p,
    # *choose* x_h to absorb the unforced equation (Ch 6, decays),
    # and derive that x_p must satisfy the full forced equation.
    # Only THEN show the figures so the labels "transient" and
    # "steady state" carry a picture, and only THEN tie back to
    # Section 1's building-up swing as the payoff.
    #
    # NOTE on structure: the algebra is kept in DISPLAY-ONLY md
    # blocks (A1, A2) and the prose in INLINE-ONLY blocks (A3+).
    # Cramming many $$ displays and many inline $...$ into a single
    # md block made KaTeX leak its MathML fallback in the browser
    # (math appeared tripled). Smaller, separated blocks render
    # cleanly.
    _fig_h, _fig_p = delib.transient_steady_figures(
        omega0=2.0, gamma=0.25, omega=2.0, t_end=28.0,
    )
    mo.vstack([
        mo.md(  # A1 — setup + the split (display equations only)
            r"""
            ## Two motions in one — and which one we care about

            We've just built the equation of motion:

            $$
            \ddot x + 2\gamma\dot x + \omega_0^2 x \;=\; F_0\cos(\omega t).
            $$

            Solving it all in one go — a single function that answers
            the push, matches how the swing started, and holds for
            all time — is a lot to ask at once. There's a trick that
            breaks the job into two easier pieces, each with a clean
            physical meaning.

            ### Split the unknown into two pieces

            Write the solution as a sum of two functions we haven't
            pinned down yet:

            $$
            x(t) \;=\; x_h(t) \;+\; x_p(t).
            $$

            Since the solution is a sum, its first and second
            derivatives are sums in exactly the same way:

            $$
            \dot x \;=\; \dot x_h + \dot x_p,
            \qquad
            \ddot x \;=\; \ddot x_h + \ddot x_p.
            $$
            """
        ),
        mo.md(  # A2 — regroup, the one choice, underbraced split (display only)
            r"""
            Now feed these into the left side and gather the terms by
            which function they came from. We are free to split the
            solution any way we like, so we spend that freedom on the
            one choice that pays off: **require the first piece to
            solve the equation with the push switched off** — Chapter
            6's oscillator, no driving force. That makes its entire
            group vanish, and the second piece is left to reproduce
            the drive on its own:

            $$
            \ddot x + 2\gamma\dot x + \omega_0^2 x
            \;=\;
            \underbrace{\left(\ddot x_h + 2\gamma\dot x_h + \omega_0^2 x_h\right)}_{=\;0}
            \;+\;
            \underbrace{\left(\ddot x_p + 2\gamma\dot x_p + \omega_0^2 x_p\right)}_{=\;F_0\cos(\omega t)}
            \;=\; F_0\cos(\omega t).
            $$

            Reading off the two braces, the one hard equation has
            split into two familiar ones — an unforced equation for
            the first (transient) piece, and the full forced equation
            for the second (steady-state) piece:

            $$
            \ddot x_h + 2\gamma\dot x_h + \omega_0^2 x_h \;=\; 0,
            $$

            $$
            \ddot x_p + 2\gamma\dot x_p + \omega_0^2 x_p \;=\; F_0\cos(\omega t).
            $$
            """
        ),
        mo.md(  # A3 — linearity aside + which half is interesting + Motion 1 (inline only)
            r"""
            That regrouping was legal for one reason. Every operation
            on the left side — differentiate, scale by a constant,
            add — distributes over a sum, so the $x_h$ terms and the
            $x_p$ terms stay in their own brackets and never mix.
            (Had the equation carried a *nonlinear* term, say an
            $x^2$, this would fail: $(x_h+x_p)^2 \neq x_h^2 + x_p^2$,
            and the two pieces would cross-talk.) The word for the
            property that saves us is **linear** — linearity is
            precisely the permission to add.

            ### Which half is interesting?

            The first equation is one we've already met: it's
            Chapter 6's damped oscillator with no driving force. Its
            solution carries whatever initial conditions the swing
            had at $t=0$, and whatever it carries, damping drains to
            zero within a few times $1/\gamma$. We call this dying
            piece the **transient**, $x_h$.

            The second equation is the new thing. Its solution must
            keep pace with the push *forever*: a swing at the drive's
            frequency that neither grows nor decays. The initial
            conditions never entered how we built it — they were all
            absorbed into $x_h$ — so $x_p$ depends only on the push
            and the swing's own constants $\omega_0$ and $\gamma$. We
            call this survivor the **steady state**, $x_p$.

            After a few times $1/\gamma$ the transient is gone and
            $x_p$ *is* the motion. All the long-term behaviour lives
            in $x_p$, so $x_p$ is what we'll chase for the rest of
            the section.

            ### What the two pieces look like

            Before going after $x_p$ with algebra, here's what each
            piece looks like on its own, so the words *transient* and
            *steady state* carry a picture.

            **Motion 1 — the transient $x_h$.** A Chapter 6
            oscillation tucked inside a shrinking envelope, headed
            for zero. Whatever its starting size, the swing forgets
            it after a few damping times.
            """
        ),
        _fig_h,
        mo.md(
            r"""
            **Motion 2 — the steady state $x_p$.** A constant-
            amplitude swing at the drive's frequency, locked to
            the push (dashed) and possibly lagging behind it. It
            doesn't grow, doesn't fade, and would keep going
            forever as long as the push keeps going.
            """
        ),
        _fig_p,
        mo.md(
            r"""
            With those two pictures in mind, go back to the
            **left panel of Section 1** (the right-rhythm swing)
            and watch its first few seconds. The small first
            cycle growing into the steady soaring sweep is exactly
            $x_h + x_p$ playing out: early on the transient
            (Motion 1) is still substantial and overlaps the
            steady state, so the visible motion is the
            not-yet-settled sum of the two. After a few times
            $1/\gamma$ the transient has faded out and only
            Motion 2 is left — the clean repeating sweep you
            remember.

            Time to find $x_p$.
            """
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 4 (shape) — B1 of 3: first attempt at x_p. Try the
    # simplest possible thing (x_p = a cos(wt)), compute the
    # derivatives, plug into the left side, and SEE that the damping
    # term produces an uncancellable sin(wt). That diagnosis tells us
    # what to do next.
    mo.md(
        r"""
        ### What $x_p$ has to look like

        We need a specific $x_p(t)$ that satisfies the forced
        equation

        $$
        \ddot x_p + 2\gamma\dot x_p + \omega_0^2 x_p \;=\; F_0\cos(\omega t).
        $$

        Where do we even start guessing? The right side is a cosine
        at frequency $\omega$. The simplest possible move is to try
        the same kind of thing on the left — let $x_p$ be a cosine
        at the same frequency, scaled by some unknown amplitude —
        and see what breaks.

        **First attempt: $x_p(t) = a\cos(\omega t)$.** Then
        $\dot x_p = -a\omega\sin(\omega t)$ and
        $\ddot x_p = -a\omega^2\cos(\omega t)$. Plug those into the
        left side and gather $\cos$ and $\sin$ terms:

        $$
        \ddot x_p + 2\gamma\dot x_p + \omega_0^2 x_p
        \;=\; a(\omega_0^2 - \omega^2)\cos(\omega t)
        \;-\; 2\gamma a\omega\sin(\omega t).
        $$

        We wanted this to equal $F_0\cos(\omega t)$. The cosine
        terms cooperated — pick $a$ to make the cosine coefficient
        equal $F_0$ and we're done on that side. But the damping
        term has produced a leftover $\sin(\omega t)$ piece with
        coefficient $-2\gamma a\omega$, and there is nothing on the
        right side to absorb it. With only one knob $a$, we cannot
        zero out two coefficients at the same time.

        The diagnosis: **the damping term — the one that touches
        $\dot x$ — turns $\cos$ into $\sin$.** A pure-cosine ansatz
        simply lacks the vocabulary to answer back. The fix is to
        include a sine term from the start.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 4 (shape) — B2 of 3: second attempt, x_p = a cos + b sin.
    # Substitute, gather cos and sin, and get a 2x2 linear system in
    # (a, b). The form works -- two equations, two unknowns, unique
    # solution.
    mo.md(
        r"""
        **Second attempt: $x_p(t) = a\cos(\omega t) + b\sin(\omega t)$.**
        Two unknowns now. Differentiating as before and substituting
        into the left side, then collecting cosine terms apart from
        sine terms, gives

        $$
        \bigl[a(\omega_0^2 - \omega^2) + 2\gamma b\omega\bigr]\cos(\omega t)
        \;+\;
        \bigl[b(\omega_0^2 - \omega^2) - 2\gamma a\omega\bigr]\sin(\omega t).
        $$

        The output has *exactly* the same vocabulary as the right
        side: one $\cos(\omega t)$ piece plus one $\sin(\omega t)$
        piece. And the right side, $F_0\cos(\omega t)$, is itself
        $F_0\cos(\omega t) + 0\cdot\sin(\omega t)$. For the two
        sides to agree at every instant $t$, their cosine
        coefficients must match and their sine coefficients must
        match — two equations:

        $$
        \begin{aligned}
        a(\omega_0^2 - \omega^2) + 2\gamma b\omega &\;=\; F_0, \\
        b(\omega_0^2 - \omega^2) - 2\gamma a\omega &\;=\; 0.
        \end{aligned}
        $$

        **Two equations, two unknowns** — a $2\times 2$ linear
        system in $(a, b)$. The form has worked: $x_p$ is some
        specific cosine-plus-sine combination at the drive
        frequency, with $a$ and $b$ determined uniquely by the
        system above.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 4 (shape) — B3 of 3: repackage (a, b) as (A, phi). Trig
    # identity to convert; (A, phi) is what we physically care about
    # (amplitude and phase lag), so use that form going into cell C.
    mo.md(
        r"""
        **Repackaging in amplitude and phase.** The pair $(a, b)$
        holds the answer, but they're not the numbers a physicist
        cares about. What we'd like to read off the answer are the
        **amplitude** $A$ (how big the swing gets) and the **phase
        lag** $\varphi$ (how much the swing trails the push). A
        standard trig identity converts between the two:

        $$
        a\cos(\omega t) + b\sin(\omega t) \;=\; A\cos(\omega t - \varphi),
        $$

        with $A = \sqrt{a^2 + b^2}$ and $\tan\varphi = b/a$.
        (Picture $(a, b)$ as a point in the plane: $A$ is its
        distance from the origin and $\varphi$ is its angle to the
        $a$-axis. Same information, different coordinates.)

        So the steady state takes the clean form

        $$
        x_p(t) \;=\; A\cos(\omega t - \varphi),
        $$

        a sinusoid at the drive's frequency, shifted in time. The
        minus sign is just a convention: a positive $\varphi$
        shifts the peak *later* than the push's peak, so $\varphi$
        reads directly as "how far the swing lags behind the push."

        Two numbers left to find — $A$ and $\varphi$ — and the
        linear system above already contains them. The next
        subsection solves it.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Section 4 (result) — solve the 2x2 system from B for (a, b),
    # convert to (A, phi), box the result. Resonance setup unchanged.
    # (The previous prose re-did the substitution in (A, phi) form;
    # after the B rewrite, B already does the substitution in (a, b)
    # form, so C now just solves the system.)
    mo.md(
        r"""
        ### Pinning down $A$ and $\varphi$

        The $2\times 2$ system from above is now a small piece of
        linear algebra. The second equation rearranges to
        $b/a = 2\gamma\omega / (\omega_0^2 - \omega^2)$ — and that
        ratio is exactly $\tan\varphi$, so the phase lag drops out
        immediately. Substituting back into the first equation pins
        down $a$, then $b$, and the magnitude
        $A = \sqrt{a^2 + b^2}$ comes out by the Pythagorean
        theorem. The two formulas we'll spend the rest of the
        chapter living with are

        $$
        \boxed{\;\,
          A(\omega) \;=\; \frac{F_0}{\sqrt{(\omega_0^2 - \omega^2)^2 + (2\gamma\omega)^2}},
          \qquad
          \tan\varphi(\omega) \;=\; \frac{2\gamma\omega}{\omega_0^2 - \omega^2}.
        \,\;}
        $$

        Stare at $A(\omega)$ for a moment. The first piece of the
        denominator, $(\omega_0^2 - \omega^2)^2$, vanishes when the
        drive frequency equals the swing's natural frequency,
        $\omega = \omega_0$. With **no damping**, that would send
        $A$ to infinity — push at the swing's natural rhythm and
        the amplitude grows without bound. With damping turned on,
        the second piece $(2\gamma\omega)^2$ keeps the denominator
        from ever hitting zero — but when $\gamma$ is small, it
        stays *very* small near $\omega = \omega_0$, and the
        amplitude soars.

        That's the resonance story in one line. The next two
        sections turn each of these two formulas into a picture.
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
