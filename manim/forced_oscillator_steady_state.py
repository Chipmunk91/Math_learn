"""Steady-state response of the forced oscillator — derivation.

Walks the substitution x_p(t) = A cos(omega t - phi) through
x'' + 2 gamma x' + omega0^2 x = F0 cos(omega t), expands using the
angle-subtraction identities, matches coefficients of cos(omega t) and
sin(omega t), and isolates A and phi as

    A(omega)   = F0 / sqrt( (omega0^2 - omega^2)^2 + (2 gamma omega)^2 )
    tan(phi)   = 2 gamma omega / (omega0^2 - omega^2)

This is the Ch 7 hero derivation, used right before the amplitude /
phase frequency-response figure.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/forced_oscillator_steady_state.py SceneForcedOscillatorSteadyState
    cp media/videos/forced_oscillator_steady_state/1080p60/SceneForcedOscillatorSteadyState.mp4 \\
       assets/forced_oscillator_steady_state.mp4
"""

import pathlib
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import *  # noqa: F403,E402
from derivation_kit import HIGHLIGHT  # noqa: E402


def _caption(text):
    """Small grey caption below the stage, auto-wrapped to ~65 chars."""
    wrapped = "\n".join(
        textwrap.fill(para, width=65) for para in text.split("\n")
    )
    t = Text(wrapped, font_size=22, color=GREY_B)
    t.to_edge(DOWN, buff=1.0)
    return t


def _step_label(text):
    """Stage header in the title slot; title fades into it on stage 1."""
    t = Text(text, font_size=26, color=BLUE_D, weight=BOLD)
    t.to_edge(UP, buff=0.4)
    return t


class SceneForcedOscillatorSteadyState(Scene):
    """Solve for the steady-state amplitude and phase."""

    def construct(self):
        # --- Setup --------------------------------------------------------
        title = Text(
            "Steady-state response of  ẍ + 2γẋ + ω₀²x = F₀ cos(ωt)",
            font_size=28,
        ).to_edge(UP, buff=0.5)
        given = MathTex(
            r"\ddot x + 2\gamma\,\dot x + \omega_0^2\,x \;=\; F_0\cos(\omega t)"
        ).scale(1.2)
        given.next_to(title, DOWN, buff=0.5)
        cap = _caption(
            "Once the transient has died, the system oscillates at the drive "
            "frequency. So try an ansatz of that shape, with an amplitude A "
            "and a phase lag φ to be determined."
        )
        self.play(Write(title))
        self.play(Write(given), FadeIn(cap))
        self.wait(3.0)
        self.play(FadeOut(title), FadeOut(given))

        # --- Step 1: the ansatz -------------------------------------------
        step_lbl = _step_label("Step 1 — try the ansatz")
        ansatz = MathTex(
            r"x_p(t) \;=\; A \cos(\omega t - \varphi)"
        ).scale(1.35).set_color(HIGHLIGHT)
        new_cap = _caption(
            "Same frequency ω as the drive (the equation is linear, so the "
            "answer can't have any other frequency). A and φ are unknowns we "
            "will pin down by demanding the equation hold."
        )
        self.play(FadeIn(step_lbl), Write(ansatz), Transform(cap, new_cap))
        self.wait(3.0)

        # --- Step 2: derivatives ------------------------------------------
        new_lbl = _step_label("Step 2 — differentiate twice")
        derivs = MathTex(
            r"\dot x_p \;=\; -A\omega \sin(\omega t - \varphi),"
            r"\quad "
            r"\ddot x_p \;=\; -A\omega^2 \cos(\omega t - \varphi)"
        ).scale(1.0)
        new_cap = _caption(
            "Each derivative just brings down ω and swaps cos ↔ sin (with a "
            "sign). Both derivatives are still at the same frequency."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(ansatz, derivs),
                  Transform(cap, new_cap))
        self.wait(3.0)

        # --- Step 3: substitute and collect -------------------------------
        new_lbl = _step_label("Step 3 — substitute, collect like terms")
        sub = MathTex(
            r"A\,(\omega_0^2 - \omega^2)\,\cos(\omega t - \varphi)"
            r"\;-\;"
            r"2\gamma A\omega\,\sin(\omega t - \varphi)"
            r"\;=\; F_0 \cos(\omega t)"
        ).scale(0.95)
        new_cap = _caption(
            "Plug x_p, ẋ_p, ẍ_p into the left-hand side. The two cos pieces "
            "(from ẍ_p and ω₀²x) combine into the (ω₀² − ω²) coefficient; "
            "the sin piece comes from the 2γẋ_p term."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(ansatz, sub),
                  Transform(cap, new_cap))
        self.wait(4.0)

        # --- Step 4: expand the shifted cos / sin -------------------------
        new_lbl = _step_label("Step 4 — open up cos(ωt − φ) and sin(ωt − φ)")
        expand = MathTex(
            r"\bigl[A(\omega_0^2 - \omega^2)\cos\varphi + 2\gamma A\omega \sin\varphi\bigr] \cos\omega t",
            r"\;+\;",
            r"\bigl[A(\omega_0^2 - \omega^2)\sin\varphi - 2\gamma A\omega \cos\varphi\bigr] \sin\omega t",
            r"\;=\; F_0 \cos\omega t",
        ).scale(0.78).arrange_in_grid(rows=2, cols=2, buff=0.15, col_alignments="cc")
        # arrange_in_grid won't suit this — fall back to a simple linear arrange.
        expand = VGroup(
            MathTex(
                r"\bigl[A(\omega_0^2 - \omega^2)\cos\varphi + 2\gamma A\omega \sin\varphi\bigr]\cos\omega t",
            ).scale(0.85),
            MathTex(
                r"+\,\bigl[A(\omega_0^2 - \omega^2)\sin\varphi - 2\gamma A\omega \cos\varphi\bigr]\sin\omega t \;=\; F_0\cos\omega t",
            ).scale(0.85),
        ).arrange(DOWN, buff=0.25)
        new_cap = _caption(
            "Use cos(α−β) = cos α cos β + sin α sin β (and similarly for sin) "
            "to split everything into pure cos(ωt) and pure sin(ωt) pieces."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(ansatz, expand),
                  Transform(cap, new_cap))
        self.wait(4.5)

        # --- Step 5: match coefficients (two equations) -------------------
        new_lbl = _step_label("Step 5 — match cos and sin coefficients")
        match = VGroup(
            MathTex(
                r"\cos\omega t:\quad A(\omega_0^2 - \omega^2)\cos\varphi + 2\gamma A\omega \sin\varphi \;=\; F_0",
            ).scale(0.9),
            MathTex(
                r"\sin\omega t:\quad A(\omega_0^2 - \omega^2)\sin\varphi - 2\gamma A\omega \cos\varphi \;=\; 0",
            ).scale(0.9),
        ).arrange(DOWN, buff=0.35)
        new_cap = _caption(
            "cos(ωt) and sin(ωt) are linearly independent, so the equation "
            "splits into two scalar equations — one for each. Two equations "
            "for the two unknowns A and φ."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(ansatz, match),
                  Transform(cap, new_cap))
        self.wait(4.5)

        # --- Step 6: solve for phi (from sin equation) --------------------
        new_lbl = _step_label("Step 6 — phase from the sin equation")
        phi_eq = MathTex(
            r"\tan\varphi \;=\; \frac{2\gamma\omega}{\omega_0^2 - \omega^2}"
        ).scale(1.3).set_color(HIGHLIGHT)
        new_cap = _caption(
            "The sin equation has no F₀ on the right. Divide by A cos φ and "
            "rearrange: φ is determined entirely by ω, ω₀ and γ — no force "
            "needed. The phase lag is purely a property of the system."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(ansatz, phi_eq),
                  Transform(cap, new_cap))
        self.wait(4.0)

        # --- Step 7: solve for A (square-and-add) -------------------------
        new_lbl = _step_label("Step 7 — amplitude by square-and-add")
        A_eq = MathTex(
            r"A(\omega) \;=\; \frac{F_0}{\sqrt{(\omega_0^2 - \omega^2)^2 + (2\gamma\omega)^2}}"
        ).scale(1.2).set_color(TEAL)
        box = SurroundingRectangle(A_eq, color=TEAL, buff=0.3)
        new_cap = _caption(
            "Square both matching equations and add. The cross terms with "
            "cos φ sin φ cancel, leaving A² times (the sum of squares) = F₀². "
            "Pull A out and we have the amplitude as a clean function of ω."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(ansatz, A_eq),
                  Transform(cap, new_cap))
        self.play(Create(box))
        self.wait(5.0)
