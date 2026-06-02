"""Integrating factor — derive μ(x) = exp(∫ (M_y - N_x)/N dx).

When M dx + N dy = 0 is NOT exact, multiply through by a clever factor
μ(x, y) and demand the rescaled equation pass the exactness test. That
gives a PDE for μ. The simplest possible guess — that μ depends on x
alone — collapses the PDE to a separable ODE that we can solve directly.

Eight steps:
  1. Multiply both sides by μ(x, y).
  2. Demand the rescaled equation pass the exactness test.
  3. Product rule on both sides -- four terms.
  4. Try μ = μ(x), so μ_y = 0. One term vanishes.
  5. Rearrange: μ_x N = μ(M_y - N_x).
  6. Separate: μ_x / μ = (M_y - N_x) / N.
  7. Integrate.
  8. Exponentiate -> the integrating-factor formula.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/integrating_factor.py SceneIntegratingFactor
    cp media/videos/integrating_factor/1080p60/SceneIntegratingFactor.mp4 \\
       assets/integrating_factor.mp4

Then it appears in ch03 via delib.video("integrating_factor.mp4").
"""

import pathlib
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import *  # noqa: F403,E402
from derivation_kit import HIGHLIGHT  # noqa: E402


def _caption(text):
    """Small grey caption below the stage. Auto-wraps to ~65 characters per
    line so long strings stay inside the Manim viewport at the default
    config. Pass explicit ``\\n`` in the input to force a break at a
    specific spot."""
    wrapped = "\n".join(
        textwrap.fill(para, width=65) for para in text.split("\n")
    )
    t = Text(wrapped, font_size=22, color=GREY_B)
    t.to_edge(DOWN, buff=1.0)
    return t


def _step_label(text):
    """Step header above the stage, fixed position."""
    t = Text(text, font_size=24, color=BLUE_D, weight=BOLD)
    t.to_edge(UP, buff=0.9)
    return t


class SceneIntegratingFactor(Scene):
    """Derive μ(x) = exp(∫ (M_y - N_x)/N dx) from the exactness condition on μM dx + μN dy = 0."""

    def construct(self):
        # ----------------------- Setup ------------------------------------
        title = Text("Integrating factor — when the test fails",
                     font_size=32).to_edge(UP, buff=0.6)
        problem = MathTex(r"M\,dx + N\,dy = 0").scale(1.2)
        problem.next_to(title, DOWN, buff=0.5)
        not_exact = MathTex(r"M_y \;\neq\; N_x").scale(1.0).set_color(RED_D)
        not_exact.next_to(problem, DOWN, buff=0.4)
        cap = _caption("The exactness test fails. Can we rescue the equation?")

        self.play(Write(title), FadeIn(cap))
        self.play(Write(problem))
        self.play(Write(not_exact))
        self.wait(2.5)
        self.play(FadeOut(title), FadeOut(problem), FadeOut(not_exact))

        # ----------------------- Step 1 -----------------------------------
        step_lbl = _step_label("Step 1 — multiply both sides by some μ(x, y)")
        eq = MathTex(r"\mu M\,dx \;+\; \mu N\,dy \;=\; 0").scale(1.25)
        new_cap = _caption(
            "We don't know what μ is yet — we'll find one that fixes the test."
        )
        self.play(FadeIn(step_lbl), Write(eq), Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 2 -----------------------------------
        new_lbl = _step_label("Step 2 — demand the rescaled equation pass the exactness test")
        eq2 = MathTex(r"(\mu M)_y \;=\; (\mu N)_x").scale(1.3)
        new_cap = _caption("The same test as before, now applied to the rescaled equation.")
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq2),
                  Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 3 -----------------------------------
        new_lbl = _step_label("Step 3 — expand using the product rule")
        eq3 = MathTex(
            r"\mu_y M", r"\;+\;", r"\mu M_y", r"\;=\;",
            r"\mu_x N", r"\;+\;", r"\mu N_x"
        ).scale(1.15)
        # Highlight the two terms with partial derivatives of μ -- the ones
        # we'll need to deal with.
        eq3[0].set_color(HIGHLIGHT)  # μ_y M
        eq3[4].set_color(HIGHLIGHT)  # μ_x N
        new_cap = _caption(
            "Product rule on each side gives four terms. Highlighted: the two with partial derivatives of μ."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq3),
                  Transform(cap, new_cap))
        self.wait(4.0)

        # ----------------------- Step 4 -----------------------------------
        # Step 4 is a GUESS, not a derivation -- the user is right that this
        # has to be flagged. The Side-condition card at the end of the scene
        # is the check; the prose after the video derives WHY (M_y - N_x)/N
        # being a function of x alone is exactly that check.
        new_lbl = _step_label("Step 4 — guess μ depends only on x (we'll verify the guess)")
        eq4 = MathTex(
            r"\mu M_y \;=\; ", r"\mu_x N", r"\;+\; \mu N_x"
        ).scale(1.2)
        eq4[1].set_color(HIGHLIGHT)  # μ_x N stays highlighted
        new_cap = _caption(
            "Just a guess: maybe μ has no y in it, so μ_y = 0 — the first term vanishes. "
            "We'll need to check this guess at the end."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq4),
                  Transform(cap, new_cap))
        self.wait(3.0)

        # ----------------------- Step 5 -----------------------------------
        new_lbl = _step_label("Step 5 — gather μ_x on one side, μ on the other")
        eq5 = MathTex(
            r"\mu_x N", r"\;=\;", r"\mu\,(M_y - N_x)"
        ).scale(1.3)
        eq5[0].set_color(HIGHLIGHT)
        new_cap = _caption("Subtract μN_x from both sides; factor μ out on the right.")
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq5),
                  Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 6 -----------------------------------
        new_lbl = _step_label("Step 6 — divide through to a separable form")
        eq6 = MathTex(
            r"\frac{\mu_x}{\mu} \;=\; \frac{M_y - N_x}{N}"
        ).scale(1.3).set_color(HIGHLIGHT)
        new_cap = _caption(
            "Divide by μN. Left: derivative of ln(μ). Right: a function of x alone (we hope)."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq6),
                  Transform(cap, new_cap))
        self.wait(3.5)

        # ----------------------- Step 7 -----------------------------------
        new_lbl = _step_label("Step 7 — integrate both sides")
        eq7 = MathTex(
            r"\ln \mu \;=\; \int \frac{M_y - N_x}{N}\, dx"
        ).scale(1.25)
        new_cap = _caption("Direct integration. The left side gives ln(μ).")
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq7),
                  Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 8 -----------------------------------
        new_lbl = _step_label("Step 8 — exponentiate")
        eq8 = MathTex(
            r"\mu(x) \;=\; \exp\!\left( \int \frac{M_y - N_x}{N}\, dx \right)"
        ).scale(1.25).set_color(TEAL)
        new_cap = _caption(
            "The integrating factor. Multiply your equation by this μ and it becomes exact."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq8),
                  Transform(cap, new_cap))
        self.wait(4.0)

        # ----------------------- Side condition ---------------------------
        # Tie the side condition back to Step 4 explicitly: this *is* the
        # consistency check on the guess. The post-video prose develops the
        # WHY (LHS depends only on x by the guess, so the RHS must too).
        new_lbl = _step_label("Checking the Step 4 guess")
        side_text = Text(
            "Our formula assumed μ depends only on x.\n"
            "It holds only if (M_y − N_x)/N is itself a function of x alone.\n"
            "If a y refuses to cancel, the guess fails — try μ(y) instead, with x and y swapped.",
            font_size=19, color=GREY_B,
        ).next_to(eq8, DOWN, buff=0.7)
        self.play(Transform(step_lbl, new_lbl), FadeIn(side_text),
                  FadeOut(cap))
        self.wait(5.0)
