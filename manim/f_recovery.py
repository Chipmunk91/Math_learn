"""F-recovery — find F(x, y) from M = F_x and N = F_y by partial integration.

Worked example matches the chapter's running example:

    (2x + y) dx + (x + 2y) dy = 0
    => M = 2x + y, N = x + 2y
    => F(x, y) = x^2 + xy + y^2

Each algebraic move is per-atom so the symbol motion is deterministic and
transparent (no fades, no shape-matching heuristic). Teal marks the symbols
being actively manipulated, matching the convention in newton_cooling.py.
A small caption beneath the stage names the move; a step label above keeps
the reader oriented.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/f_recovery.py SceneFRecovery
    cp media/videos/f_recovery/1080p60/SceneFRecovery.mp4 \\
       assets/f_recovery.mp4

Then it appears in ch03 via delib.video("f_recovery.mp4").
"""

import pathlib
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import *  # noqa: F403,E402
from derivation_kit import HIGHLIGHT  # noqa: E402


def _caption(text):
    """Small grey caption below the stage. Auto-wraps to ~65 characters per
    line so long strings stay inside the Manim viewport. Pass explicit
    ``\\n`` in the input to force a break at a specific spot."""
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


class SceneFRecovery(Scene):
    """Recover F from M = 2x + y, N = x + 2y by partial integration."""

    def construct(self):
        # ----------------------- Setup ------------------------------------
        title = Text("Finding F from M and N", font_size=34).to_edge(UP, buff=0.6)
        given = MathTex(r"M(x, y) = 2x + y, \quad N(x, y) = x + 2y").scale(1.0)
        given.next_to(title, DOWN, buff=0.5)
        goal = MathTex(
            r"\text{Find } F(x, y) \text{ with } F_x = M,\; F_y = N."
        ).scale(0.9)
        goal.next_to(given, DOWN, buff=0.4)
        cap = _caption("We've verified the equation is exact. Now we recover F.")

        self.play(Write(title), FadeIn(cap))
        self.play(Write(given))
        self.play(Write(goal))
        self.wait(2.2)
        self.play(FadeOut(title), FadeOut(given), FadeOut(goal))

        # ----------------------- Step 1 -----------------------------------
        # Start with what we know about F: F_x = M.
        step_lbl = _step_label("Step 1 — start with what we know: F_x = M")
        eq = MathTex(r"F_x = 2x + y").scale(1.4)
        new_cap = _caption("F_x is one of the rates we already have. Use it.")
        self.play(FadeIn(step_lbl), Write(eq), Transform(cap, new_cap))
        self.wait(2.0)

        # ----------------------- Step 2 -----------------------------------
        # Integrate in x. The "constant" can depend on y -- call it g(y).
        new_lbl = _step_label("Step 2 — integrate in x")
        integral = MathTex(r"F \;=\; \int (2x + y)\, dx \;+\; g(y)").scale(1.2)
        new_cap = _caption(
            "Integrate. The 'constant' of integration can depend on y — call it g(y)."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, integral),
                  Transform(cap, new_cap))
        self.wait(2.2)

        evaluated = MathTex(r"F \;=\; x^2 + xy \;+\; ", r"g(y)").scale(1.3)
        evaluated[1].set_color(HIGHLIGHT)
        self.play(Transform(eq, evaluated))
        self.wait(2.5)

        # Tuck this F up so we can do the next move beneath it.
        F_top = MathTex(r"F \;=\; x^2 + xy \;+\; ", r"g(y)").scale(0.85)
        F_top[1].set_color(HIGHLIGHT)
        F_top.shift(UP * 1.6)
        self.play(Transform(eq, F_top))
        self.wait(0.4)

        # ----------------------- Step 3 -----------------------------------
        # Differentiate F in y: x^2 -> 0, xy -> x, g(y) -> g'(y).
        new_lbl = _step_label("Step 3 — differentiate this F in y")
        Fy = MathTex(r"F_y \;=\; x \;+\; ", r"g'(y)").scale(1.2)
        Fy[1].set_color(HIGHLIGHT)
        new_cap = _caption(
            "Term by term: x² → 0, xy → x, g(y) → g'(y)."
        )
        self.play(Transform(step_lbl, new_lbl), Write(Fy),
                  Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 4 -----------------------------------
        # Set F_y equal to N = x + 2y.
        new_lbl = _step_label("Step 4 — set F_y equal to N")
        eq_to_N = MathTex(r"x \;+\; ", r"g'(y)", r" \;=\; x + 2y").scale(1.2)
        eq_to_N[1].set_color(HIGHLIGHT)
        new_cap = _caption("F_y has to match N. So x + g'(y) = x + 2y.")
        self.play(Transform(Fy, eq_to_N), Transform(step_lbl, new_lbl),
                  Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 5 -----------------------------------
        # The x's cancel; what remains pins down g'(y).
        new_lbl = _step_label("Step 5 — the x's cancel, leaving g'(y)")
        gprime = MathTex(r"g'(y) \;=\; 2y").scale(1.4)
        gprime.set_color(HIGHLIGHT)
        new_cap = _caption(
            "The x's match — built-in consistency check — and g'(y) is what's left."
        )
        self.play(Transform(Fy, gprime), Transform(step_lbl, new_lbl),
                  Transform(cap, new_cap))
        self.wait(2.7)

        # ----------------------- Step 6 -----------------------------------
        # Integrate g'(y) in y.
        new_lbl = _step_label("Step 6 — integrate g'(y) to recover g(y)")
        g_done = MathTex(r"g(y) \;=\; y^2").scale(1.4)
        g_done.set_color(HIGHLIGHT)
        new_cap = _caption("Just an ordinary one-variable integration.")
        self.play(Transform(Fy, g_done), Transform(step_lbl, new_lbl),
                  Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 7 -----------------------------------
        # Plug g back into F.
        new_lbl = _step_label("Step 7 — plug g(y) back into F")
        F_full = MathTex(r"F(x, y) \;=\; x^2 + xy \;+\; ", r"y^2").scale(1.4)
        F_full[1].set_color(HIGHLIGHT)
        new_cap = _caption("Swap g(y) up top with y² — and we're done.")
        self.play(FadeOut(eq), Transform(Fy, F_full),
                  Transform(step_lbl, new_lbl), Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Result -----------------------------------
        new_lbl = _step_label("The hidden landscape")
        F_done = MathTex(r"F(x, y) \;=\; x^2 + xy + y^2", color=TEAL).scale(1.55)
        new_cap = _caption(
            "Solutions of the equation are the contours F(x, y) = C."
        )
        self.play(Transform(Fy, F_done), Transform(step_lbl, new_lbl),
                  Transform(cap, new_cap))
        self.wait(4.0)
