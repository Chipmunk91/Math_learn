"""Variation of parameters worked end-to-end on  y'' + y = tan(x).

The chapter-8 §5 hero clip. Runs the VoP machine on a forcing UC
genuinely cannot touch (tan x), reusing the cos/sin basis from
Saga 8's state-plane figure (W = 1) so the integrals stay clean.

Pacing note: this is the "kind but boring pathfinder" — one idea per
beat, nothing squished. Every equation is width-fit to the frame so
nothing clips off the edges (the earlier draft packed both relic-rate
equalities onto one line and it ran off both sides).

  1. Setup — the equation; why Method 1 can't touch it.
  2. Basis, then the Wronskian computed to 1.
  3. Relic-rates: Cramer template -> substitute -> simplify, stacked
     as two lines u_1', u_2'.
  4. The trig rewrite that makes u_1' integrable, then integrate both.
  5. Assemble y_p, expand, and strike the two equal-and-opposite
     sin x cos x terms.
  6. Reattach the homogeneous coordinates: full general solution.

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

# Stage geometry. The frame is ~14.22 wide; keep equations inside this
# so nothing clips. STAGE is the centre of the equation area, nudged
# up to clear the bottom caption.
SAFE_W = 12.4
SAFE_H = 4.2
STAGE = UP * 0.25


def _fit(mob, max_w=SAFE_W, max_h=SAFE_H):
    """Scale a mobject down (never up) so it fits inside the safe area."""
    if mob.width > max_w:
        mob.scale_to_fit_width(max_w)
    if mob.height > max_h:
        mob.scale_to_fit_height(max_h)
    return mob


def _caption(text):
    """Small grey caption below the stage, auto-wrapped to ~65 chars."""
    wrapped = "\n".join(
        textwrap.fill(para, width=65) for para in text.split("\n")
    )
    t = Text(wrapped, font_size=22, color=GREY_B)
    t.to_edge(DOWN, buff=0.9)
    return t


def _step_label(text):
    """Step header in the title slot; one heading at a time."""
    t = Text(text, font_size=26, color=BLUE_D, weight=BOLD)
    t.to_edge(UP, buff=0.6)
    return t


class SceneVariationOfParameters(Scene):
    """y'' + y = tan(x) solved by variation of parameters, step by step."""

    def construct(self):
        # ======================= Setup ====================================
        title = Text(
            "Variation of parameters:  y'' + y = tan x",
            font_size=30,
        ).to_edge(UP, buff=0.6)
        given = _fit(MathTex(r"y'' + y \;=\; \tan x").scale(1.4)).move_to(STAGE)
        cap = _caption(
            "Method 1 can't touch tan x — differentiating it never "
            "closes on a finite family. Method 2 needs only a basis "
            "and one Wronskian. Let's go slowly."
        )
        self.play(Write(title))
        self.play(Write(given), FadeIn(cap))
        self.wait(3.5)

        step = _step_label("Step 1 — the homogeneous basis")

        # ======================= Step 1a: basis ===========================
        e = _fit(
            MathTex(r"y_1 \;=\; \cos x, \qquad y_2 \;=\; \sin x").scale(1.3)
        ).move_to(STAGE)
        cap2 = _caption(
            "The homogeneous companion y'' + y = 0 has the basis we've "
            "used all along — a cosine and a sine."
        )
        self.play(FadeOut(title), FadeIn(step),
                  FadeTransform(given, e), Transform(cap, cap2))
        given = e
        self.wait(3.0)

        # ======================= Step 1b: compute W =======================
        new_step = _step_label("Step 1 — the basis and its Wronskian")
        e = _fit(VGroup(
            MathTex(r"W \;=\; y_1 y_2' \;-\; y_2 y_1'"),
            MathTex(r"\phantom{W} \;=\; \cos x\cos x \;-\; \sin x\,(-\sin x)"),
            MathTex(r"\phantom{W} \;=\; \cos^2 x + \sin^2 x \;=\; 1"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).scale(1.15)).move_to(STAGE)
        cap2 = _caption(
            "Its Wronskian — the state-plane area from Saga 8 — works "
            "out to exactly 1. That clean denominator is about to pay off."
        )
        self.play(Transform(step, new_step),
                  FadeTransform(given, e), Transform(cap, cap2))
        given = e
        self.wait(4.0)

        # ======================= Step 2a: Cramer template =================
        new_step = _step_label("Step 2 — relic-rates from Saga 9 (Cramer)")
        e = _fit(VGroup(
            MathTex(r"u_1' \;=\; -\,\frac{y_2\,g}{W}"),
            MathTex(r"u_2' \;=\; +\,\frac{y_1\,g}{W}"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6).scale(1.25)).move_to(STAGE)
        cap2 = _caption(
            "Cramer's rule gave us the two relic-rates. This is the "
            "general template — now feed in our specific basis and forcing."
        )
        self.play(Transform(step, new_step),
                  FadeTransform(given, e), Transform(cap, cap2))
        given = e
        self.wait(3.5)

        # ======================= Step 2b: substitute ======================
        e = _fit(VGroup(
            MathTex(r"u_1' \;=\; -\,\sin x\,\tan x"),
            MathTex(r"u_2' \;=\; +\,\cos x\,\tan x"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6).scale(1.25)).move_to(STAGE)
        cap2 = _caption(
            "Substitute y_1 = cos x, y_2 = sin x, g = tan x, and W = 1. "
            "The denominators vanish because W = 1."
        )
        self.play(FadeTransform(given, e), Transform(cap, cap2))
        given = e
        self.wait(3.5)

        # ======================= Step 2c: simplify u_2' ===================
        e = _fit(VGroup(
            MathTex(r"u_1' \;=\; -\,\sin x\,\tan x"),
            MathTex(r"u_2' \;=\; \cos x\,\tan x \;=\; \sin x"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6).scale(1.25)).move_to(STAGE)
        e[1].set_color(HIGHLIGHT)
        cap2 = _caption(
            "u_2' simplifies on sight: cos x · tan x = sin x. "
            "u_1' still has that awkward sin x · tan x — handle it next."
        )
        self.play(FadeTransform(given, e), Transform(cap, cap2))
        given = e
        self.wait(3.5)

        # ======================= Step 3a: the rewrite =====================
        new_step = _step_label("Step 3 — the rewrite that unlocks u_1")
        e = _fit(VGroup(
            MathTex(r"\sin x\,\tan x \;=\; \frac{\sin^2 x}{\cos x} \;=\; \frac{1 - \cos^2 x}{\cos x}"),
            MathTex(r"\;=\; \sec x \;-\; \cos x"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).scale(1.15)).move_to(STAGE)
        e[1].set_color(HIGHLIGHT)
        cap2 = _caption(
            "Pull tan apart, use sin^2 = 1 - cos^2, split the fraction. "
            "Now u_1' is just sec x minus a cosine — both standard."
        )
        self.play(Transform(step, new_step),
                  FadeTransform(given, e), Transform(cap, cap2))
        given = e
        self.wait(4.5)

        # ======================= Step 3b: integrate =======================
        new_step = _step_label("Step 3 — integrate each rate")
        e = _fit(VGroup(
            MathTex(r"u_1 \;=\; \sin x \;-\; \ln\lvert\sec x + \tan x\rvert"),
            MathTex(r"u_2 \;=\; -\,\cos x"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.6).scale(1.2)).move_to(STAGE)
        cap2 = _caption(
            "Integrate. The sec x term gives the classic "
            "ln|sec x + tan x|; the cosine and the sine are elementary."
        )
        self.play(Transform(step, new_step),
                  FadeTransform(given, e), Transform(cap, cap2))
        given = e
        self.wait(4.0)

        # ======================= Step 4a: assembly template ===============
        new_step = _step_label("Step 4 — equip the relics onto the basis")
        e = _fit(
            MathTex(r"y_p \;=\; u_1\,y_1 \;+\; u_2\,y_2").scale(1.35)
        ).move_to(STAGE)
        cap2 = _caption(
            "Back to the armored form from Saga 3: y_p = u_1 y_1 + u_2 y_2. "
            "Drop in everything we just found."
        )
        self.play(Transform(step, new_step),
                  FadeTransform(given, e), Transform(cap, cap2))
        given = e
        self.wait(3.0)

        # ======================= Step 4b: substitute ======================
        e = _fit(
            MathTex(
                r"y_p \;=\; \bigl(\sin x - \ln\lvert\sec x + \tan x\rvert\bigr)\cos x"
                r"\;+\;(-\cos x)\sin x"
            ).scale(1.1)
        ).move_to(STAGE)
        cap2 = _caption(
            "Substitute u_1, y_1 = cos x and u_2 = -cos x, y_2 = sin x. "
            "Now multiply the first bracket through."
        )
        self.play(FadeTransform(given, e), Transform(cap, cap2))
        given = e
        self.wait(4.0)

        # ======================= Step 4c: expand, mark cancelling pair ====
        e = _fit(MathTex(
            r"y_p \;=\;",
            r"\sin x\,\cos x",
            r"\;-\; \cos x\,\ln\lvert\sec x + \tan x\rvert",
            r"\;-\;",
            r"\cos x\,\sin x",
        ).scale(1.1)).move_to(STAGE)
        e[1].set_color(HIGHLIGHT)
        e[4].set_color(HIGHLIGHT)
        cap2 = _caption(
            "Expanded, the two highlighted pieces are sin x · cos x and "
            "its exact negative. They cancel."
        )
        self.play(FadeTransform(given, e), Transform(cap, cap2))
        self.wait(2.0)
        # strike them out, then drop them
        strike1 = Line(e[1].get_left(), e[1].get_right(),
                       color=RED, stroke_width=5)
        strike2 = Line(e[4].get_left(), e[4].get_right(),
                       color=RED, stroke_width=5)
        self.play(Create(strike1), Create(strike2))
        self.wait(2.0)

        # ======================= Step 4d: clean result ====================
        e2 = _fit(
            MathTex(r"y_p \;=\; -\,\cos x \,\ln\lvert\sec x + \tan x\rvert").scale(1.3)
        ).move_to(STAGE)
        cap2 = _caption(
            "One clean term out of the gauntlet. No guess table could "
            "have produced it — tan x was off the menu."
        )
        self.play(FadeOut(strike1), FadeOut(strike2),
                  FadeTransform(e, e2), Transform(cap, cap2))
        given = e2
        self.wait(3.0)

        # ======================= Step 5: general solution =================
        new_step = _step_label("Step 5 — reattach the homogeneous coordinates")
        e = _fit(VGroup(
            MathTex(r"y \;=\; -\cos x\,\ln\lvert\sec x + \tan x\rvert"),
            MathTex(r"\phantom{y} \;+\; c_1 \cos x \;+\; c_2 \sin x"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).scale(1.2)).move_to(STAGE)
        e.set_color(TEAL)
        box = SurroundingRectangle(e, color=TEAL, buff=0.3)
        cap2 = _caption(
            "Add y_h back on. The two free constants are exactly the "
            "coordinates from the Prologue, waiting for initial "
            "conditions. The whole method, in one pass."
        )
        self.play(Transform(step, new_step),
                  FadeTransform(given, e), Transform(cap, cap2))
        self.play(Create(box))
        self.wait(5.0)
