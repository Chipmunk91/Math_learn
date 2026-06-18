"""Variation of parameters — derivation.

When the right-hand side of  y'' + p(x) y' + q(x) y = g(x)  is ugly enough
that the "undetermined coefficients" guess table can't handle it, we let
the constants in the homogeneous solution become *functions* of x and ask
what they must be.

This scene walks the textbook derivation, in five steps:

  1. Start from x_p = u1(x) y1(x) + u2(x) y2(x), with y1, y2 a known
     homogeneous basis and u1, u2 unknown functions to determine.
  2. Differentiate; impose the convenience constraint
        u1' y1 + u2' y2 = 0
     to keep the second derivative tidy.
  3. Differentiate again; substitute into the original ODE; the
     homogeneous parts in (u1, u2) vanish because y1, y2 each solve the
     homogeneous equation. What is left is
        u1' y1' + u2' y2' = g(x).
  4. Stack the two equations in (u1', u2'); the coefficient matrix is
     the Wronskian W = y1 y2' - y2 y1'.
  5. Solve by Cramer's rule:
        u1' = - y2 g / W,    u2' =   y1 g / W,
     then integrate. Hence
        x_p = -y1 ∫(y2 g / W) dx  +  y2 ∫(y1 g / W) dx.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/variation_of_parameters.py SceneVariationOfParameters
    cp media/videos/variation_of_parameters/1080p60/SceneVariationOfParameters.mp4 \\
       assets/variation_of_parameters.mp4
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


class SceneVariationOfParameters(Scene):
    """Derive the variation-of-parameters formula from scratch."""

    def construct(self):
        # --- Setup --------------------------------------------------------
        title = Text(
            "Variation of parameters for  y'' + p(x) y' + q(x) y = g(x)",
            font_size=26,
        ).to_edge(UP, buff=0.5)
        given = MathTex(
            r"y'' + p(x)\, y' + q(x)\, y \;=\; g(x)"
        ).scale(1.2)
        given.next_to(title, DOWN, buff=0.5)
        homog = MathTex(
            r"y_h(x) \;=\; C_1\, y_1(x) \;+\; C_2\, y_2(x)"
        ).scale(1.0).set_color(GREY_B)
        homog.next_to(given, DOWN, buff=0.5)
        cap = _caption(
            "We already know a basis  y_1, y_2  of homogeneous solutions. "
            "Variation of parameters lets the two constants C_1, C_2 vary "
            "with x — and pins down what they must be so the result solves "
            "the non-homogeneous equation."
        )
        self.play(Write(title))
        self.play(Write(given))
        self.play(FadeIn(homog), FadeIn(cap))
        self.wait(3.5)
        self.play(FadeOut(title), FadeOut(given), FadeOut(homog), FadeOut(cap))

        # --- Step 1: the ansatz -------------------------------------------
        step_lbl = _step_label("Step 1 — let the constants vary")
        ansatz = MathTex(
            r"x_p(x) \;=\; u_1(x)\, y_1(x) \;+\; u_2(x)\, y_2(x)"
        ).scale(1.25).set_color(HIGHLIGHT)
        cap1 = _caption(
            "Replace C_1, C_2 with unknown functions u_1(x), u_2(x). One "
            "ansatz, two unknowns: we'll need two equations to determine them."
        )
        self.play(FadeIn(step_lbl), FadeIn(ansatz), FadeIn(cap1))
        self.wait(3.0)

        # Tuck the ansatz to the upper left so the work has room.
        anchor = MathTex(
            r"x_p \;=\; u_1 y_1 + u_2 y_2"
        ).scale(0.85).set_color(HIGHLIGHT)
        anchor.to_corner(UL, buff=0.7).shift(DOWN * 0.5)
        self.play(
            FadeOut(cap1),
            FadeOut(step_lbl),
            ReplacementTransform(ansatz, anchor),
        )

        # --- Step 2: differentiate, then choose the convenience constraint
        step_lbl = _step_label("Step 2 — differentiate, then make a smart choice")
        # Product rule.
        deriv = MathTex(
            r"x_p' \;=\; u_1' y_1 + u_1 y_1'",
            r"\;+\; u_2' y_2 + u_2 y_2'"
        ).scale(1.1).move_to(ORIGIN + UP * 0.4)
        cap2 = _caption(
            "Product rule on each term. Four pieces now — but two of them "
            "(in u_1', u_2') will cause a u_1'' and u_2'' in the next "
            "derivative. We'd rather avoid that."
        )
        self.play(FadeIn(step_lbl), Write(deriv), FadeIn(cap2))
        self.wait(3.5)

        # Impose the constraint that kills the u_i' pieces.
        constraint = MathTex(
            r"\boxed{\;u_1' y_1 + u_2' y_2 \;=\; 0\;}"
        ).scale(1.05).set_color(HIGHLIGHT)
        constraint.next_to(deriv, DOWN, buff=0.6)
        cap2b = _caption(
            "We have the freedom to impose ONE extra equation on (u_1, u_2) — "
            "the ansatz only carries one solution's worth of constraint. Set "
            "the u_i'-pieces to zero, by hand. (We'll see why this pays off "
            "in a moment.)"
        )
        self.play(FadeOut(cap2), FadeIn(cap2b), Write(constraint))
        self.wait(3.5)

        # After the constraint, the surviving x_p' has only u_i pieces.
        deriv_clean = MathTex(
            r"x_p' \;=\; u_1 y_1' \;+\; u_2 y_2'"
        ).scale(1.15).move_to(deriv.get_center())
        self.play(
            FadeOut(cap2b),
            ReplacementTransform(deriv, deriv_clean),
        )
        self.wait(1.5)

        # --- Step 3: second derivative + substitution ---------------------
        step_lbl_new = _step_label("Step 3 — differentiate again, substitute")
        cap3 = _caption(
            "Differentiate x_p' once more (again product rule). Then plug "
            "x_p, x_p', x_p'' into the original ODE  y'' + p y' + q y = g."
        )
        self.play(FadeOut(step_lbl), FadeIn(step_lbl_new), FadeIn(cap3))
        deriv2 = MathTex(
            r"x_p'' \;=\; u_1' y_1' + u_1 y_1''",
            r"\;+\; u_2' y_2' + u_2 y_2''"
        ).scale(1.05).next_to(deriv_clean, DOWN, buff=0.4)
        self.play(Write(deriv2))
        self.wait(3.0)

        # After substitution, all u_i terms collect into u_i (y_i'' + p y_i' + q y_i),
        # which is zero because y_i are homogeneous solutions. Display this collapse.
        collapse = MathTex(
            r"\underbrace{u_1\bigl(y_1'' + p\,y_1' + q\,y_1\bigr)}_{=\,0}",
            r"\;+\;",
            r"\underbrace{u_2\bigl(y_2'' + p\,y_2' + q\,y_2\bigr)}_{=\,0}",
            r"\;+\; u_1' y_1' + u_2' y_2' \;=\; g(x)"
        ).scale(0.85)
        collapse.move_to(ORIGIN + DOWN * 0.4)
        cap3b = _caption(
            "Group the u_1- and u_2-only terms. Each parenthesis is "
            "y_i'' + p y_i' + q y_i = 0 — because y_1 and y_2 SOLVE the "
            "homogeneous equation. They drop out. The non-homogeneous "
            "right side is left equal to the only surviving pieces:"
        )
        self.play(
            FadeOut(deriv_clean), FadeOut(deriv2),
            FadeOut(cap3), FadeIn(cap3b),
            Write(collapse),
        )
        self.wait(4.0)

        # What survives, on its own line, highlighted.
        survive = MathTex(
            r"\boxed{\;u_1' y_1' + u_2' y_2' \;=\; g(x)\;}"
        ).scale(1.05).set_color(HIGHLIGHT)
        survive.move_to(ORIGIN + DOWN * 0.5)
        self.play(FadeOut(cap3b), FadeOut(collapse), Write(survive))
        self.wait(2.0)

        # --- Step 4: the 2x2 system in (u_1', u_2') -----------------------
        step_lbl_new2 = _step_label("Step 4 — stack the two equations")
        cap4 = _caption(
            "We have two equations in two unknowns (u_1', u_2'): the "
            "convenience constraint from Step 2, and the survivor from "
            "Step 3. Stack them as a 2×2 linear system."
        )
        self.play(FadeOut(step_lbl_new), FadeIn(step_lbl_new2),
                  FadeOut(constraint), FadeOut(survive), FadeIn(cap4))
        system = MathTex(
            r"\begin{pmatrix} y_1 & y_2 \\ y_1' & y_2' \end{pmatrix}",
            r"\begin{pmatrix} u_1' \\ u_2' \end{pmatrix}",
            r"\;=\;",
            r"\begin{pmatrix} 0 \\ g(x) \end{pmatrix}"
        ).scale(1.2)
        self.play(Write(system))
        self.wait(2.5)

        # Name the Wronskian.
        wronskian = MathTex(
            r"W(x) \;=\; \det\begin{pmatrix} y_1 & y_2 \\ y_1' & y_2' \end{pmatrix}",
            r"\;=\; y_1 y_2' - y_2 y_1'"
        ).scale(0.95)
        wronskian.next_to(system, DOWN, buff=0.6).set_color(HIGHLIGHT)
        cap4b = _caption(
            "The determinant of the coefficient matrix is the Wronskian, "
            "W(x). For a linearly-independent basis y_1, y_2 the Wronskian "
            "is never zero — so the 2×2 system is invertible."
        )
        self.play(FadeOut(cap4), FadeIn(cap4b), Write(wronskian))
        self.wait(3.5)

        # --- Step 5: Cramer's rule ----------------------------------------
        step_lbl_new3 = _step_label("Step 5 — solve, then integrate")
        cap5 = _caption(
            "Cramer's rule on the 2×2: replace the i-th column of the "
            "coefficient matrix with the right-hand side, divide by W."
        )
        self.play(FadeOut(step_lbl_new2), FadeIn(step_lbl_new3),
                  FadeOut(system), FadeOut(wronskian), FadeOut(cap4b),
                  FadeIn(cap5))
        cramer = MathTex(
            r"u_1' \;=\; \frac{\det\begin{pmatrix} 0 & y_2 \\ g & y_2' \end{pmatrix}}{W}",
            r"\;=\; -\,\frac{y_2\, g}{W},",
            r"\qquad",
            r"u_2' \;=\; \frac{\det\begin{pmatrix} y_1 & 0 \\ y_1' & g \end{pmatrix}}{W}",
            r"\;=\; \frac{y_1\, g}{W}"
        ).scale(0.9).move_to(ORIGIN + UP * 0.3)
        self.play(Write(cramer))
        self.wait(3.5)

        # Integrate.
        integrate = MathTex(
            r"u_1 \;=\; -\!\int\! \frac{y_2\, g}{W}\, dx,",
            r"\qquad",
            r"u_2 \;=\; \int\! \frac{y_1\, g}{W}\, dx"
        ).scale(1.0)
        integrate.next_to(cramer, DOWN, buff=0.5)
        cap5b = _caption(
            "Integrate each. (No constants of integration are needed — they "
            "would just add a homogeneous-solution piece, which is already "
            "covered by y_h.)"
        )
        self.play(FadeOut(cap5), FadeIn(cap5b), Write(integrate))
        self.wait(3.5)

        # --- Final form ---------------------------------------------------
        self.play(FadeOut(step_lbl_new3), FadeOut(cramer), FadeOut(integrate),
                  FadeOut(cap5b), FadeOut(anchor))
        final_lbl = _step_label("The variation-of-parameters formula")
        final = MathTex(
            r"x_p(x) \;=\; -\, y_1(x)\!\int\! \frac{y_2(x)\, g(x)}{W(x)}\, dx",
            r"\;+\; y_2(x)\!\int\! \frac{y_1(x)\, g(x)}{W(x)}\, dx"
        ).scale(1.0).set_color(HIGHLIGHT)
        final.move_to(ORIGIN)
        final_cap = _caption(
            "Plug in any homogeneous basis (y_1, y_2), compute the "
            "Wronskian W = y_1 y_2' - y_2 y_1', then do the two integrals. "
            "This works for ANY forcing g(x) — including the ones the "
            "guess table cannot handle."
        )
        self.play(FadeIn(final_lbl), Write(final), FadeIn(final_cap))
        self.wait(5.0)
