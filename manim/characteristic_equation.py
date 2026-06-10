"""The exponential guess — x'' + b x' + c x = 0 collapses to a quadratic.

The chapter-6 hero derivation. Walks the ansatz x = e^{rt}:

  1. The guess: x = e^{rt} — the one function whose derivatives are
     multiples of itself.
  2. Differentiate: x' = r e^{rt}, x'' = r² e^{rt}.
  3. Substitute into the equation — every term is (number) · e^{rt}.
  4. Factor out e^{rt}; it is never zero, so divide it away. The
     calculus is gone.
  5. Box the characteristic equation r² + b r + c = 0 and solve with
     the quadratic formula.
  6. Closing fork: the sign of b² − 4c sorts all equations into three
     behaviours (handing off to the chapter's three-case section).

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/characteristic_equation.py SceneCharacteristicEquation
    cp media/videos/characteristic_equation/1080p60/SceneCharacteristicEquation.mp4 \\
       assets/characteristic_equation.mp4

Then it appears in ch06 via delib.video("characteristic_equation.mp4").
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
    """Step header placed at the title slot; the title fades out as the
    first step label fades in, so the slot holds one heading at a time."""
    t = Text(text, font_size=26, color=BLUE_D, weight=BOLD)
    t.to_edge(UP, buff=0.6)
    return t


class SceneCharacteristicEquation(Scene):
    """x = e^{rt} turns x'' + b x' + c x = 0 into r² + b r + c = 0."""

    def construct(self):
        # ----------------------- Setup ------------------------------------
        title = Text(
            "Solving  x'' + b x' + c x = 0  with one good guess",
            font_size=30,
        ).to_edge(UP, buff=0.6)
        given = MathTex(r"\ddot x + b\,\dot x + c\,x \;=\; 0").scale(1.3)
        given.next_to(title, DOWN, buff=0.6)
        cap = _caption(
            "Three different-looking terms — x, its first derivative, its "
            "second — must cancel at every instant. We need a function "
            "whose derivatives all look alike."
        )
        self.play(Write(title))
        self.play(Write(given), FadeIn(cap))
        self.wait(3.0)

        # ----------------------- Step 1: the guess ------------------------
        step_lbl = _step_label("Step 1 — guess  x = e^{rt}")
        eq = MathTex(r"x \;=\; e^{rt}").scale(1.4).set_color(HIGHLIGHT)
        new_cap = _caption(
            "The exponential is the one function whose every derivative "
            "is a multiple of itself. That property is the entire plan."
        )
        self.play(FadeOut(title), FadeIn(step_lbl),
                  Transform(given, eq), Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 2: differentiate --------------------
        new_lbl = _step_label("Step 2 — differentiate the guess, twice")
        eq2 = MathTex(
            r"\dot x \;=\; r\,e^{rt},\qquad \ddot x \;=\; r^2\,e^{rt}"
        ).scale(1.25)
        new_cap = _caption(
            "Each derivative just brings down one factor of r. Both "
            "derivatives are plain multiples of e^{rt}."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(given, eq2),
                  Transform(cap, new_cap))
        self.wait(3.0)

        # ----------------------- Step 3: substitute -----------------------
        new_lbl = _step_label("Step 3 — substitute into the equation")
        eq3 = MathTex(
            r"r^2 e^{rt} \;+\; b\,r\,e^{rt} \;+\; c\,e^{rt} \;=\; 0"
        ).scale(1.2)
        new_cap = _caption(
            "Every term is now (a number) times e^{rt}. The three terms "
            "that looked different are suddenly the same shape."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(given, eq3),
                  Transform(cap, new_cap))
        self.wait(3.0)

        # ----------------------- Step 4: factor ---------------------------
        new_lbl = _step_label("Step 4 — factor out e^{rt}")
        eq4 = MathTex(
            r"e^{rt}", r"\,\bigl(r^2 + b\,r + c\bigr) \;=\; 0"
        ).scale(1.25)
        eq4[0].set_color(HIGHLIGHT)
        new_cap = _caption(
            "An exponential is never zero — for any r and any t. So the "
            "highlighted factor can be divided away. The calculus is gone."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(given, eq4),
                  Transform(cap, new_cap))
        self.wait(3.5)

        # ----------------------- Step 5: characteristic equation ----------
        new_lbl = _step_label("Step 5 — the characteristic equation")
        eq5 = MathTex(r"r^2 + b\,r + c \;=\; 0").scale(1.4).set_color(TEAL)
        box = SurroundingRectangle(eq5, color=TEAL, buff=0.25)
        new_cap = _caption(
            "A quadratic in r. The differential equation has been reduced "
            "to high-school algebra: each root r gives a solution e^{rt}."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(given, eq5),
                  Transform(cap, new_cap))
        self.play(Create(box))
        self.wait(3.0)

        # ----------------------- Step 6: quadratic formula + fork ---------
        new_lbl = _step_label("Step 6 — solve, and meet the fork")
        eq6 = MathTex(
            r"r \;=\; \frac{-b \;\pm\; \sqrt{\,",
            r"b^2 - 4c",
            r"\,}}{2}"
        ).scale(1.25)
        eq6[1].set_color(HIGHLIGHT)
        new_cap = _caption(
            "Everything hangs on the highlighted quantity. Positive: two "
            "real roots. Zero: one repeated root. Negative: a complex "
            "pair — and oscillation. Three signs, three motions."
        )
        self.play(Transform(step_lbl, new_lbl), FadeOut(box),
                  Transform(given, eq6), Transform(cap, new_cap))
        self.wait(4.5)
