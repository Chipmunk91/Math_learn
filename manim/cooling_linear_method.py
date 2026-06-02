"""Newton's cooling — the linear / integrating-factor route.

Solves T' + k T = k T_r by the integrating-factor method, in parallel to the
separation-of-variables walkthrough in newton_cooling.py. Both methods land on
the same closed form T = T_r + A e^{-k t}; this animation lets ch02 show the
second route without dumping a wall of symbolic steps into the prose.

Nine steps:
  1. Multiply both sides by some μ(t).
  2. Demand the LHS equal d/dt(μT).
  3. Expand d/dt(μT) via the product rule.
  4. Match: μT' cancels both sides; divide by T to get μ' = k μ.
  5. Solve: μ = e^(kt).
  6. Substitute back into the cooling equation.
  7. Recognise the LHS as d/dt(e^(kt) T).
  8. Integrate both sides.
  9. Divide by e^(kt) -- same closed form the separable method gave.

Same per-atom Transform convention as f_recovery.py and integrating_factor.py:
each state is a fresh MathTex block (auto-centred at creation), so the equation
morphs cleanly between states without per-glyph bookkeeping.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/cooling_linear_method.py SceneCoolingLinearMethod
    cp media/videos/cooling_linear_method/1080p60/SceneCoolingLinearMethod.mp4 \\
       assets/cooling_linear_method.mp4

Then it appears in ch02 via delib.video("cooling_linear_method.mp4").
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
    """Step header above the stage."""
    t = Text(text, font_size=24, color=BLUE_D, weight=BOLD)
    t.to_edge(UP, buff=0.9)
    return t


class SceneCoolingLinearMethod(Scene):
    """Solve T' + k T = k T_r by the integrating-factor / linear method."""

    def construct(self):
        # ----------------------- Setup ------------------------------------
        title = Text(
            "The linear method on the cooling equation",
            font_size=30,
        ).to_edge(UP, buff=0.6)
        given = MathTex(r"T' \;+\; k\,T \;=\; k\,T_r").scale(1.3)
        given.next_to(title, DOWN, buff=0.5)
        cap = _caption(
            "Same cooling equation, second method: multiply by an integrating factor."
        )
        self.play(Write(title), FadeIn(cap))
        self.play(Write(given))
        self.wait(2.5)
        self.play(FadeOut(title), FadeOut(given))

        # ----------------------- Step 1 -----------------------------------
        step_lbl = _step_label("Step 1 — multiply both sides by some μ(t)")
        eq = MathTex(
            r"\mu\,T' \;+\; \mu\,k\,T \;=\; \mu\,k\,T_r"
        ).scale(1.25)
        new_cap = _caption(
            "We don't know μ yet — we'll pick it so the left side collapses into a single derivative."
        )
        self.play(FadeIn(step_lbl), Write(eq), Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 2 -----------------------------------
        # Plain `=` here (no \stackrel{!}{=}): the step label "demand" carries
        # the intent that this is the equality we're requiring, not one we've
        # already proved. The \stackrel{!}{=} notation rendered as a literal "!"
        # above the equals in marimo's KaTeX pipeline, which read as a glitch.
        new_lbl = _step_label("Step 2 — demand the LHS equal d/dt(μT)")
        eq2 = MathTex(
            r"\mu\,T' \;+\; \mu\,k\,T \;=\; \frac{d}{dt}\bigl(\mu\,T\bigr)"
        ).scale(1.15)
        # Caption uses plain text (no subscripts), so write the right side
        # without T_r — that underscore renders literally in Manim Text.
        new_cap = _caption(
            "If this works, the LHS collapses into a single derivative — "
            "directly integrable in t."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq2),
                  Transform(cap, new_cap))
        self.wait(3.0)

        # ----------------------- Step 3 -----------------------------------
        new_lbl = _step_label("Step 3 — expand d/dt(μT) using the product rule")
        eq3 = MathTex(
            r"\mu\,T' \;+\; \mu\,k\,T \;=\; \mu'\,T \;+\; \mu\,T'"
        ).scale(1.15)
        new_cap = _caption(
            "Product rule: d/dt(μT) = μ'T + μT'. Look across the equals sign — what matches?"
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq3),
                  Transform(cap, new_cap))
        self.wait(3.5)

        # ----------------------- Step 4 -----------------------------------
        new_lbl = _step_label("Step 4 — μT' cancels both sides; what's left pins down μ")
        eq4 = MathTex(r"\mu\,k\,T \;=\; \mu'\,T").scale(1.35)
        new_cap = _caption(
            "Cancel the matching μT' on each side. Both surviving terms have a T — divide it off."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq4),
                  Transform(cap, new_cap))
        self.wait(2.5)

        eq4b = MathTex(r"\mu' \;=\; k\,\mu").scale(1.5).set_color(HIGHLIGHT)
        new_cap = _caption("A tiny ODE for μ itself: its derivative is k times itself.")
        self.play(Transform(eq, eq4b), Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 5 — solve μ' = kμ explicitly --------
        # (Previously this jumped straight from μ' = kμ to μ = e^(kt) by
        # inspection -- "the simplest function whose derivative is k times
        # itself." That sweeps the integration under the carpet, which is
        # exactly where the chapter prose's μ = exp(∫p dt) formula comes
        # from. Now we show the three moves explicitly: separate,
        # integrate, exponentiate -- and the final caption ties the result
        # back to the integral form.)
        new_lbl = _step_label("Step 5a — separate variables")
        eq5a = MathTex(r"\frac{d\mu}{\mu} \;=\; k\,dt").scale(1.4)
        new_cap = _caption(
            "μ' = kμ is separable. Move μ to the left, t to the right."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq5a),
                  Transform(cap, new_cap))
        self.wait(2.5)

        new_lbl = _step_label("Step 5b — integrate both sides")
        eq5b = MathTex(
            r"\int \frac{d\mu}{\mu} \;=\; \int k\,dt"
            r"\quad\Longrightarrow\quad \ln|\mu| \;=\; k\,t + C"
        ).scale(1.05)
        new_cap = _caption(
            "Left integral gives ln|μ|; right gives kt + C."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq5b),
                  Transform(cap, new_cap))
        self.wait(2.8)

        new_lbl = _step_label("Step 5c — exponentiate")
        eq5c = MathTex(r"\mu(t) \;=\; e^{k\,t}").scale(1.6).set_color(HIGHLIGHT)
        new_cap = _caption(
            "μ = e^(kt + C) = e^C · e^(kt). Set A = e^C: the general "
            "solution is μ(t) = A·e^(kt) for any nonzero A. We don't really "
            "need to pick A — when we multiply both sides of the cooling "
            "equation by μ in Step 6, the A appears on both sides and "
            "cancels out, so every choice of A produces the same rescaled "
            "equation. We just write A = 1 for the cleanest form. "
            "Equivalently, μ(t) = exp(∫k dt) — the general "
            "integrating-factor formula with p(t) = k."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq5c),
                  Transform(cap, new_cap))
        self.wait(5.0)

        # ----------------------- Step 6 -----------------------------------
        new_lbl = _step_label("Step 6 — multiply the cooling equation through by e^(kt)")
        eq6 = MathTex(
            r"e^{k t}\,T' \;+\; k\,e^{k t}\,T \;=\; k\,T_r\,e^{k t}"
        ).scale(1.15)
        new_cap = _caption(
            "By construction, the left side is exactly d/dt(e^(kt) T) — the whole reason we chose this μ."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq6),
                  Transform(cap, new_cap))
        self.wait(3.5)

        # ----------------------- Step 7 -----------------------------------
        new_lbl = _step_label("Step 7 — collapse the LHS into a single derivative")
        eq7 = MathTex(
            r"\frac{d}{dt}\bigl(e^{k t}\,T\bigr) \;=\; k\,T_r\,e^{k t}"
        ).scale(1.25)
        new_cap = _caption(
            "One derivative on the left. Now we can integrate both sides directly."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq7),
                  Transform(cap, new_cap))
        self.wait(3.0)

        # ----------------------- Step 8 -----------------------------------
        new_lbl = _step_label("Step 8 — integrate both sides in t")
        eq8 = MathTex(
            r"e^{k t}\,T \;=\; T_r\,e^{k t} \;+\; A"
        ).scale(1.3)
        new_cap = _caption("A is the integration constant. Now isolate T.")
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq8),
                  Transform(cap, new_cap))
        self.wait(2.5)

        # ----------------------- Step 9 -----------------------------------
        new_lbl = _step_label("Step 9 — divide by e^(kt)")
        eq9 = MathTex(
            r"T(t) \;=\; T_r \;+\; A\,e^{-k t}"
        ).scale(1.5).set_color(TEAL)
        new_cap = _caption(
            "The same closed form the separable method gave — recovered by a different route."
        )
        self.play(Transform(step_lbl, new_lbl), Transform(eq, eq9),
                  Transform(cap, new_cap))
        self.wait(4.5)
