"""One Heun's (RK2) step assembling itself on y' = y - x², from (0, 1), h = 0.5.

Builds the construction in five labelled stages:

  1. read k1, the slope at the start (teal arrow)
  2. take a tentative Euler step using k1 alone (dashed red, open circle)
  3. read k2, the slope at that tentative endpoint (teal arrow)
  4. take the real step with the averaged slope (solid red, filled dot)
  5. reveal the true solution endpoint (blue diamond) and compare gaps

Replaces an earlier Plotly frame-flip animation that was too subtle to read.
Same visual language as euler_walks_field.py: grey slope field, blue exact
curve, red steps, teal (HIGHLIGHT) slope reads.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/heun_step.py SceneHeunStep
    cp media/videos/heun_step/1080p60/SceneHeunStep.mp4 assets/heun_step.mp4

Then it appears in ch04 via delib.video("heun_step.mp4").
"""

import pathlib
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import *  # noqa: F403,E402
import numpy as np  # noqa: E402
from derivation_kit import HIGHLIGHT  # noqa: E402


def _caption(anchor, text):
    """Small grey caption directly below `anchor` (the axes), auto-wrapped."""
    wrapped = "\n".join(
        textwrap.fill(para, width=70) for para in text.split("\n")
    )
    t = Text(wrapped, font_size=20, color=GREY_B)
    t.next_to(anchor, DOWN, buff=0.45)
    return t


def _stage_label(text):
    """Stage header placed where the title sits (top-centre). The title
    fades out as the first stage label fades in, so the header line
    shows exactly one heading at a time."""
    t = Text(text, font_size=26, color=BLUE_D, weight=BOLD)
    t.to_edge(UP, buff=0.25)
    return t


class SceneHeunStep(Scene):
    """One Heun step on y' = y - x² from (0, 1) with h = 0.5."""

    def construct(self):
        f = lambda x, y: y - x ** 2
        x0, y0, h = 0.0, 1.0, 0.5

        k1 = f(x0, y0)                      # 1.000
        x_t, y_t = x0 + h, y0 + h * k1      # tentative Euler endpoint (0.5, 1.5)
        k2 = f(x_t, y_t)                    # 1.250
        k_avg = 0.5 * (k1 + k2)             # 1.125
        y_heun = y0 + h * k_avg             # 1.5625
        y_true = 2 + 2 * x_t + x_t ** 2 - float(np.exp(x_t))  # 1.6013

        # --- Setup: zoomed-in axes + slope field ------------------------------
        axes = Axes(
            x_range=[-0.08, 0.92, 0.25],
            y_range=[0.75, 2.05, 0.25],
            x_length=8.0,
            y_length=3.8,
            tips=False,
            axis_config=dict(
                color=GREY_B, stroke_width=1.5,
                include_numbers=True,
                font_size=20,
                decimal_number_config=dict(num_decimal_places=2),
            ),
        )
        axes.shift(UP * 0.5)
        axes_labels = axes.get_axis_labels(
            x_label=MathTex("x").scale(0.8),
            y_label=MathTex("y").scale(0.8),
        )

        slope_lines = VGroup()
        seg_len = 0.07  # in axes units (window is ~1 x 1.3)
        for xi in np.arange(0.0, 0.92, 0.1):
            for yi in np.arange(0.8, 2.05, 0.13):
                s = f(xi, yi)
                norm = (1 + s * s) ** 0.5
                dx = seg_len / norm
                dy = s * dx
                seg = Line(
                    axes.c2p(xi - dx / 2, yi - dy / 2),
                    axes.c2p(xi + dx / 2, yi + dy / 2),
                    color=GREY, stroke_width=1.2, stroke_opacity=0.5,
                )
                slope_lines.add(seg)

        exact_curve = axes.plot(
            lambda u: 2 + 2 * u + u ** 2 - np.exp(u),
            x_range=[-0.05, 0.9, 0.01],
            color=BLUE_D,
            stroke_width=3,
        )

        title = Text("One Heun (RK2) step on  y' = y − x²,   h = 0.5",
                     font_size=26).to_edge(UP, buff=0.25)
        start_dot = Dot(axes.c2p(x0, y0), color=RED_E, radius=0.09)
        start_lbl = MathTex("(0, 1)").scale(0.7).next_to(start_dot, LEFT, buff=0.12)

        cap = _caption(
            axes,
            "Start at (0, 1). The blue curve is the exact solution — "
            "the target our one step is trying to follow."
        )

        self.play(Write(title))
        self.play(Create(axes), Write(axes_labels))
        self.play(Create(slope_lines, lag_ratio=0.01), run_time=1.4)
        self.play(Create(exact_curve), FadeIn(start_dot), Write(start_lbl))
        self.play(FadeIn(cap))
        self.wait(2.0)
        self.play(FadeOut(start_lbl))

        # Helper: a teal slope arrow of fixed on-screen length at (x, y).
        def slope_arrow(x, y, slope, length=0.13):
            norm = (1 + slope * slope) ** 0.5
            dx = length / norm
            return Arrow(
                start=axes.c2p(x, y),
                end=axes.c2p(x + dx, y + slope * dx),
                color=HIGHLIGHT, buff=0,
                stroke_width=5, tip_length=0.16,
                max_tip_length_to_length_ratio=0.4,
            )

        # --- Stage 1: read k1 -------------------------------------------------
        # Title fades out as stage label fades in at the same screen
        # position, so the header line shows exactly one heading at a time.
        lbl = _stage_label("1 — read the slope at the start")
        k1_arrow = slope_arrow(x0, y0, k1)
        k1_tex = MathTex(r"k_1 = f(0, 1) = 1.000", font_size=30,
                         color=HIGHLIGHT).next_to(k1_arrow, UP, buff=0.18)
        new_cap = _caption(
            axes,
            "The equation gives the slope at our current point: "
            "k1 = f(0, 1) = 1 − 0² = 1. This is all Euler ever uses."
        )
        self.play(FadeOut(title), FadeIn(lbl), Transform(cap, new_cap),
                  GrowArrow(k1_arrow), Write(k1_tex), run_time=1.2)
        self.wait(2.0)

        # --- Stage 2: tentative Euler step ------------------------------------
        new_lbl = _stage_label("2 — tentative Euler step (k1 alone)")
        tent_line = DashedLine(
            axes.c2p(x0, y0), axes.c2p(x_t, y_t),
            color=RED_E, stroke_width=3.5, dash_length=0.12,
        )
        tent_dot = Circle(radius=0.09, color=RED_E, stroke_width=3
                          ).move_to(axes.c2p(x_t, y_t))
        new_cap = _caption(
            axes,
            "Follow k1 for the whole width h = 0.5, as Euler would. Land "
            "at (0.50, 1.500) — the open circle, visibly below the curve."
        )
        self.play(Transform(lbl, new_lbl), Transform(cap, new_cap),
                  Create(tent_line), run_time=1.2)
        self.play(FadeIn(tent_dot), FadeOut(k1_tex), run_time=0.5)
        self.wait(2.0)

        # --- Stage 3: read k2 at the tentative endpoint ------------------------
        new_lbl = _stage_label("3 — read the slope there")
        k2_arrow = slope_arrow(x_t, y_t, k2)
        k2_tex = MathTex(r"k_2 = f(0.5,\, 1.5) = 1.250", font_size=30,
                         color=HIGHLIGHT).next_to(k2_arrow, UP, buff=0.18)
        new_cap = _caption(
            axes,
            "Ask the equation again, at the tentative endpoint: "
            "k2 = 1.5 − 0.5² = 1.25. The slope grew while we stepped — "
            "that's the curvature Euler ignores."
        )
        self.play(Transform(lbl, new_lbl), Transform(cap, new_cap),
                  GrowArrow(k2_arrow), Write(k2_tex), run_time=1.2)
        self.wait(2.4)

        # --- Stage 4: the real step with the averaged slope --------------------
        new_lbl = _stage_label("4 — real step: average the two slopes")
        heun_line = Line(
            axes.c2p(x0, y0), axes.c2p(x_t, y_heun),
            color=RED_E, stroke_width=4.5,
        )
        heun_dot = Dot(axes.c2p(x_t, y_heun), color=RED_E, radius=0.09)
        # Anchor below the stage label since the title is gone by now.
        avg_tex = MathTex(
            r"\tfrac{k_1 + k_2}{2} = 1.125,\quad y_1 = 1 + 0.5 \cdot 1.125 = 1.5625",
            font_size=30,
        ).next_to(lbl, DOWN, buff=0.25)
        new_cap = _caption(
            axes,
            "Take the actual step with the average slope 1.125. Land at "
            "(0.50, 1.5625) — the filled dot, above the open circle."
        )
        self.play(Transform(lbl, new_lbl), Transform(cap, new_cap),
                  FadeOut(k2_tex), Write(avg_tex), run_time=1.0)
        self.play(Create(heun_line), FadeIn(heun_dot), run_time=1.2)
        self.wait(2.4)

        # --- Stage 5: reveal the true endpoint and compare ---------------------
        new_lbl = _stage_label("5 — compare with the truth")
        true_marker = Square(side_length=0.16, color=BLUE_D, stroke_width=3.5
                             ).rotate(PI / 4).move_to(axes.c2p(x_t, y_true))
        # Small braces showing the two gaps at x = 0.5.
        new_cap = _caption(
            axes,
            "True solution at x = 0.5 is y ≈ 1.601 (blue diamond). "
            "Euler's endpoint is off by 0.101; Heun's is off by 0.039 — "
            "2.6× closer, for one extra slope read."
        )
        self.play(Transform(lbl, new_lbl), Transform(cap, new_cap),
                  FadeOut(avg_tex), FadeIn(true_marker), run_time=1.2)

        gap_euler = MathTex(r"\text{Euler gap} = 0.101", font_size=26,
                            color=GREY_B).next_to(tent_dot, DOWN + RIGHT, buff=0.15)
        gap_heun = MathTex(r"\text{Heun gap} = 0.039", font_size=26,
                           color=RED_E).next_to(heun_dot, RIGHT, buff=0.2)
        self.play(Write(gap_euler), Write(gap_heun), run_time=1.0)
        self.wait(4.0)
