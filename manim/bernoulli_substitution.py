"""Bernoulli substitution — derive v = y^(1-n) and linearise.

Starts with the Bernoulli equation y' + p(x) y = q(x) y^n (with n ≠ 0, 1)
and walks the substitution that linearises it. Result:

    v' + (1-n) p(x) v = (1-n) q(x)

— linear in v, ready for the integrating-factor recipe.

Six steps:
  1. Divide both sides by y^n.
  2. Identify y^(1-n) sitting in the middle term — define v = y^(1-n).
  3. Differentiate v to get v' = (1-n) y^(-n) y' = (1-n) y' / y^n.
  4. Multiply the divided equation through by (1-n) so the first term
     matches v'.
  5. Substitute v and v' to get v' + (1-n) p v = (1-n) q.
  6. Box the linearised form.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/bernoulli_substitution.py SceneBernoulliSubstitution
    cp media/videos/bernoulli_substitution/1080p60/SceneBernoulliSubstitution.mp4 \\
       assets/bernoulli_substitution.mp4

Then it appears in ch03b via delib.video("bernoulli_substitution.mp4").
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import *  # noqa: F403,E402
from derivation_kit import HIGHLIGHT  # noqa: E402


def _caption(text):
    """Small grey caption below the stage."""
    t = Text(text, font_size=22, color=GREY_B)
    t.to_edge(DOWN, buff=1.0)
    return t


def _step_label(text):
    """Step header above the stage."""
    t = Text(text, font_size=24, color=BLUE_D, weight=BOLD)
    t.to_edge(UP, buff=0.9)
    return t


class SceneBernoulliSubstitution(Scene):
    """Substitution v = y^(1-n) turns y' + p y = q y^n into linear in v."""

    def construct(self):
        # ----------------------- Setup ------------------------------------
        title = Text(
            "Bernoulli substitution — linearising y' + p y = q y^n",
            font_size=30,
        ).to_edge(UP, buff=0.6)
        given = MathTex(r"y' + p(x)\,y \;=\; q(x)\,y^n").scale(1.3)
        given.next_to(title, DOWN, buff=0.5)
        cap = _caption(
            "Nonlinear in y (n ≠ 0, 1). We'll choose a substitution that flattens it."
        )
        self.play(Write(title), FadeIn(cap))
        self.play(Write(given))
        self.wait(2.5)
        self.play(FadeOut(title), FadeOut(given))

        # ----------------------- Step 1: divide by y^n --------------------
        step_lbl = _step_label("Step 1 — divide both sides by y^n")
        eq = MathTex(
            r"\frac{y'}{y^n} \;+\; p(x)\,y^{1-n} \;=\; q(x)"
        ).scale(1.25)
        new_cap = _caption(
            "Isolate the nonlinear piece. Now the middle term has y^(1-n) in it."
        )
        self.play(FadeIn(step_lbl), Write(eq), Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 2: define v -------------------------
        new_lbl = _step_label("Step 2 — define v = y^(1-n)")
        # Highlight y^(1-n) in the equation, then write the definition.
        eq2 = MathTex(
            r"\frac{y'}{y^n} \;+\; p(x)\,", r"y^{1-n}", r" \;=\; q(x)"
        ).scale(1.25)
        eq2[1].set_color(HIGHLIGHT)
        new_cap = _caption(
            "Define v to be that y^(1-n) piece — then the middle term becomes p(x)v, which is linear in v."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq2),
                  Transform(cap, new_cap))
        self.wait(2.5)

        defn = MathTex(r"v \;\equiv\; y^{1-n}").scale(1.4).set_color(HIGHLIGHT)
        defn.shift(DOWN * 1.2)
        self.play(Write(defn))
        self.wait(2.0)

        # ----------------------- Step 3: differentiate v ------------------
        new_lbl = _step_label("Step 3 — differentiate v")
        eq3 = MathTex(
            r"v' \;=\; (1-n)\,y^{-n}\,y' \;=\; (1-n)\,\frac{y'}{y^n}"
        ).scale(1.2)
        new_cap = _caption(
            "Chain rule on v = y^(1-n). The result looks just like the first term of the equation, up to a factor (1-n)."
        )
        self.play(Transform(step_lbl, new_lbl), FadeOut(defn),
                  Transform(eq, eq3), Transform(cap, new_cap))
        self.wait(3.5)

        # ----------------------- Step 4: multiply through by (1-n) --------
        new_lbl = _step_label("Step 4 — multiply the divided equation by (1-n)")
        eq4 = MathTex(
            r"(1-n)\,\frac{y'}{y^n} \;+\; (1-n)\,p(x)\,y^{1-n} \;=\; (1-n)\,q(x)"
        ).scale(1.05)
        new_cap = _caption(
            "Now the first term matches v', and the middle term has v sitting in it. Ready to substitute."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq4),
                  Transform(cap, new_cap))
        self.wait(3.5)

        # ----------------------- Step 5: substitute v, v' -----------------
        new_lbl = _step_label("Step 5 — substitute v = y^(1-n) and v' = (1-n) y' / y^n")
        eq5 = MathTex(
            r"v' \;+\; (1-n)\,p(x)\,v \;=\; (1-n)\,q(x)"
        ).scale(1.3)
        new_cap = _caption(
            "Substitution is done. The result has v and v' only — no y, no y^n."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq5),
                  Transform(cap, new_cap))
        self.wait(3.0)

        # ----------------------- Step 6: box the linear form --------------
        new_lbl = _step_label("Step 6 — linear in v")
        eq6 = MathTex(
            r"v' \;+\; (1-n)\,p(x)\,v \;=\; (1-n)\,q(x)"
        ).scale(1.4).set_color(TEAL)
        # Add a box around the equation
        box = SurroundingRectangle(eq6, color=TEAL, buff=0.25)
        new_cap = _caption(
            "Linear first-order ODE in v. Apply the integrating-factor recipe; then recover y from v = y^(1-n)."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq6),
                  Transform(cap, new_cap))
        self.play(Create(box))
        self.wait(4.5)
