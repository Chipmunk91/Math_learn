"""Variation of parameters worked end-to-end on  y'' + y = tan(x).

The chapter-8 §5 hero clip. Runs the VoP machine on a forcing UC
genuinely cannot touch (tan x), reusing the cos/sin basis from
Saga 8's state-plane figure (W = 1) so the integrals stay clean.

  1. Setup — the equation and the homogeneous basis (W = 1).
  2. Relic-rates — drop g = tan x into Saga 9's Cramer formula.
  3. Integrate — the trig rewrite sin x tan x = sec x - cos x makes
     u_1 doable; u_2 is immediate.
  4. Assemble — y_p = u_1 y_1 + u_2 y_2; the bare sin x cos x pieces
     annihilate, leaving one term.
  5. Reattach the homogeneous coordinates: full general solution.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/variation_of_parameters.py SceneVariationOfParameters
    cp media/videos/variation_of_parameters/1080p60/SceneVariationOfParameters.mp4 \\
       assets/variation_of_parameters.mp4

Then it appears in ch08 via delib.video("variation_of_parameters.mp4").
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


class SceneVariationOfParameters(Scene):
    """y'' + y = tan(x) solved by variation of parameters, start to end."""

    def construct(self):
        # ----------------------- Setup ------------------------------------
        title = Text(
            "Variation of parameters:  y'' + y = tan x",
            font_size=30,
        ).to_edge(UP, buff=0.6)
        given = MathTex(r"y'' + y \;=\; \tan x").scale(1.3)
        given.next_to(title, DOWN, buff=0.6)
        cap = _caption(
            "Method 1 can't touch tan x — differentiating it never "
            "closes on a finite family. Method 2 doesn't care; it "
            "needs only a basis and one Wronskian."
        )
        self.play(Write(title))
        self.play(Write(given), FadeIn(cap))
        self.wait(3.5)

        # ----------------------- Step 1: basis & Wronskian ----------------
        step_lbl = _step_label("Step 1 — the basis and its Wronskian")
        eq = MathTex(
            r"y_1 \;=\; \cos x, \qquad y_2 \;=\; \sin x, \qquad W \;=\; 1"
        ).scale(1.2)
        new_cap = _caption(
            "The homogeneous companion y'' + y = 0 has the basis we used "
            "all along. Its Wronskian — the state-plane area from Saga 8 "
            "— is identically 1."
        )
        self.play(FadeOut(title), FadeIn(step_lbl),
                  Transform(given, eq), Transform(cap, new_cap))
        self.wait(3.5)

        # ----------------------- Step 2: relic-rates ----------------------
        new_lbl = _step_label("Step 2 — relic-rates from Saga 9 (Cramer)")
        eq2 = MathTex(
            r"u_1' \;=\; -\,\tfrac{y_2 g}{W} \;=\; -\sin x\,\tan x,"
            r"\qquad "
            r"u_2' \;=\; \tfrac{y_1 g}{W} \;=\; \cos x\,\tan x \;=\; \sin x."
        ).scale(1.0)
        new_cap = _caption(
            "Drop y_1, y_2, W and g = tan x straight into the formula. "
            "u_2' simplifies on sight; u_1' will need one rewrite."
        )
        self.play(Transform(step_lbl, new_lbl),
                  Transform(given, eq2), Transform(cap, new_cap))
        self.wait(4.0)

        # ----------------------- Step 3a: the trig rewrite ----------------
        new_lbl = _step_label("Step 3 — the rewrite that unlocks the integral")
        eq3a = MathTex(
            r"\sin x\,\tan x \;=\;",
            r"\tfrac{\sin^2 x}{\cos x}",
            r"\;=\;",
            r"\tfrac{1 - \cos^2 x}{\cos x}",
            r"\;=\;",
            r"\sec x - \cos x",
        ).scale(1.05)
        eq3a[-1].set_color(HIGHLIGHT)
        new_cap = _caption(
            "Pull tan apart, use sin^2 = 1 - cos^2, split the fraction. "
            "Now u_1' is sec x minus a cosine — both standard integrals."
        )
        self.play(Transform(step_lbl, new_lbl),
                  Transform(given, eq3a), Transform(cap, new_cap))
        self.wait(4.5)

        # ----------------------- Step 3b: integrate -----------------------
        eq3b = MathTex(
            r"u_1 \;=\; \sin x \;-\; \ln\lvert\sec x + \tan x\rvert,"
            r"\qquad "
            r"u_2 \;=\; -\cos x."
        ).scale(1.05)
        new_cap = _caption(
            "Integrate each rate. The sec x term gives the classic "
            "ln|sec x + tan x|; everything else is elementary."
        )
        self.play(Transform(given, eq3b), Transform(cap, new_cap))
        self.wait(4.0)

        # ----------------------- Step 4: assemble & cancel ----------------
        new_lbl = _step_label("Step 4 — assemble and watch terms cancel")
        eq4a = MathTex(
            r"y_p \;=\; ",
            r"\bigl(\sin x - \ln\lvert\sec x + \tan x\rvert\bigr)\cos x",
            r"\;+\;",
            r"(-\cos x)\sin x",
        ).scale(0.95)
        # highlight the two pieces that will annihilate each other
        eq4a[3].set_color(HIGHLIGHT)
        new_cap = _caption(
            "Plug u_1, u_2 back into y_p = u_1 y_1 + u_2 y_2. The "
            "highlighted sin x · cos x and (-cos x) sin x pieces are "
            "equal and opposite."
        )
        self.play(Transform(step_lbl, new_lbl),
                  Transform(given, eq4a), Transform(cap, new_cap))
        self.wait(4.5)

        eq4b = MathTex(
            r"y_p \;=\; -\cos x \,\ln\lvert\sec x + \tan x\rvert"
        ).scale(1.2)
        new_cap = _caption(
            "One clean term out of the gauntlet. No table could have "
            "produced this — tan x was off the menu."
        )
        self.play(Transform(given, eq4b), Transform(cap, new_cap))
        self.wait(3.0)

        # ----------------------- Step 5: full general solution ------------
        new_lbl = _step_label("Step 5 — reattach the homogeneous coordinates")
        eq5 = MathTex(
            r"y \;=\; -\cos x\,\ln\lvert\sec x + \tan x\rvert"
            r"\;+\; c_1 \cos x \;+\; c_2 \sin x"
        ).scale(1.05).set_color(TEAL)
        box = SurroundingRectangle(eq5, color=TEAL, buff=0.25)
        new_cap = _caption(
            "Add y_h back on — the two free constants are exactly the "
            "coordinates from the Prologue, waiting for initial "
            "conditions. The whole method, in one pass."
        )
        self.play(Transform(step_lbl, new_lbl),
                  Transform(given, eq5), Transform(cap, new_cap))
        self.play(Create(box))
        self.wait(5.0)
