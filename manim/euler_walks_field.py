"""Euler's method — walking the slope field of y' = y - x², one step at a time.

Visualises the Euler recipe geometrically: at each step, highlight the slope
of the equation at the current point, follow it for a width h, land at the
new point. After 8 steps, overlay the exact solution so the gap between the
polyline and the smooth curve is visible.

Anchors the chapter's first half of Ch 4 (Numerical methods). Same equation
and step size (h = 0.25) as the static hook figure in Beat 1, so the video
just brings that figure to life.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/euler_walks_field.py SceneEulerWalksField
    cp media/videos/euler_walks_field/1080p60/SceneEulerWalksField.mp4 \\
       assets/euler_walks_field.mp4

Then it appears in ch04 via delib.video("euler_walks_field.mp4").
"""

import pathlib
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import *  # noqa: F403,E402
import numpy as np  # noqa: E402
from derivation_kit import HIGHLIGHT  # noqa: E402


def _caption(anchor, text):
    """Small grey caption directly below `anchor` (the axes group), wrapped.
    Anchoring to the figure (not the frame's bottom edge) keeps the caption
    visually attached to the graph instead of floating low in the frame."""
    wrapped = "\n".join(
        textwrap.fill(para, width=70) for para in text.split("\n")
    )
    t = Text(wrapped, font_size=20, color=GREY_B)
    t.next_to(anchor, DOWN, buff=0.45)
    return t


def _step_label(text):
    """Step header placed where the title sits (top-centre). The title
    fades out as the first step's label fades in, so the header line is
    occupied by exactly one thing at a time."""
    t = Text(text, font_size=26, color=BLUE_D, weight=BOLD)
    t.to_edge(UP, buff=0.25)
    return t


class SceneEulerWalksField(Scene):
    """Euler's method on y' = y - x², h = 0.25, starting at (0, 1)."""

    def construct(self):
        # --- Setup: axes + slope field --------------------------------------
        # Axes are smaller and pushed up so there's clearance between the
        # x-tick labels and the bottom caption. (The previous version had
        # the caption colliding with the axis numbers.)
        axes = Axes(
            x_range=[-0.1, 2.2, 0.5],
            y_range=[0.4, 3.3, 0.5],
            x_length=8.0,
            y_length=3.8,
            tips=False,
            axis_config=dict(
                color=GREY_B, stroke_width=1.5,
                include_numbers=True,
                font_size=20,
            ),
        )
        axes.shift(UP * 0.5)
        axes_labels = axes.get_axis_labels(
            x_label=MathTex("x").scale(0.8),
            y_label=MathTex("y").scale(0.8),
        )

        # Slope field: small line segments aligned with the local slope of
        # f(x, y) = y - x². Each segment is centred on its grid point and
        # has a fixed length in axes units so the field reads cleanly.
        f = lambda x, y: y - x ** 2
        slope_lines = VGroup()
        seg_len = 0.18  # in axes units
        for xi in np.arange(0.0, 2.2, 0.25):
            for yi in np.arange(0.5, 3.3, 0.3):
                s = f(xi, yi)
                norm = (1 + s * s) ** 0.5
                dx = seg_len / norm
                dy = s * dx
                start = axes.c2p(xi - dx / 2, yi - dy / 2)
                end = axes.c2p(xi + dx / 2, yi + dy / 2)
                seg = Line(start, end, color=GREY, stroke_width=1.2, stroke_opacity=0.55)
                slope_lines.add(seg)

        title = Text("Euler's method on  y' = y − x²,   h = 0.25",
                     font_size=26).to_edge(UP, buff=0.25)
        cap = _caption(
            axes,
            "Slope field shows where the true solution heads at every "
            "point. Euler follows it in tiny straight-line steps."
        )

        self.play(Write(title))
        self.play(Create(axes), Write(axes_labels))
        self.play(Create(slope_lines, lag_ratio=0.005), run_time=2.0)
        self.play(FadeIn(cap))
        self.wait(2.0)

        # --- Euler walk -----------------------------------------------------
        h = 0.25
        n_steps = 8
        x, y = 0.0, 1.0

        # Starting dot
        dot = Dot(axes.c2p(x, y), color=RED_E, radius=0.09)
        dot_label = MathTex("(0, 1)").scale(0.7).next_to(dot, LEFT, buff=0.1)
        self.play(FadeIn(dot), Write(dot_label))
        self.wait(0.6)
        self.play(FadeOut(dot_label))

        polyline_segments = VGroup()
        for i in range(n_steps):
            slope = f(x, y)
            x_new = x + h
            y_new = y + h * slope

            slope_arrow = Arrow(
                start=axes.c2p(x, y),
                end=axes.c2p(x_new, y_new),
                color=HIGHLIGHT,
                buff=0,
                stroke_width=4,
                tip_length=0.18,
                max_tip_length_to_length_ratio=0.25,
            )

            new_lbl = _step_label(f"Step {i + 1}")
            # Short per-step caption so it stays on at most two lines and
            # doesn't crowd the axes.
            new_cap = _caption(
                axes,
                f"At ({x:.2f}, {y:.2f}): slope {slope:+.3f}. "
                f"Step h·slope = {h * slope:+.3f}. "
                f"Land at ({x_new:.2f}, {y_new:.2f})."
            )

            if i == 0:
                # Title fades out as the first step label fades in at
                # the same screen position, so the header line shows
                # exactly one heading at a time.
                self.play(FadeOut(title), FadeIn(new_lbl),
                          Transform(cap, new_cap),
                          GrowArrow(slope_arrow), run_time=1.3)
                step_lbl = new_lbl
            else:
                self.play(Transform(step_lbl, new_lbl),
                          Transform(cap, new_cap),
                          GrowArrow(slope_arrow), run_time=1.3)
            self.wait(0.5)

            poly_seg = Line(
                axes.c2p(x, y), axes.c2p(x_new, y_new),
                color=RED_E, stroke_width=3.5,
            )
            new_dot = Dot(axes.c2p(x_new, y_new), color=RED_E, radius=0.09)
            self.play(
                Transform(slope_arrow, poly_seg),
                Transform(dot, new_dot),
                run_time=0.55,
            )
            polyline_segments.add(slope_arrow)
            x, y = x_new, y_new

        # --- Reveal: exact solution overlay ---------------------------------
        new_lbl = _step_label("After 8 steps")
        new_cap = _caption(
            axes,
            "Exact solution y = 2 + 2x + x² − eˣ overlaid in blue. The "
            "polyline tracks below until x ≈ 1.5, then crosses above — "
            "per-step error compounding over the walk."
        )
        exact_curve = axes.plot(
            lambda u: 2 + 2 * u + u ** 2 - np.exp(u),
            x_range=[0, 2.0, 0.01],
            color=BLUE_D,
            stroke_width=3,
        )
        self.play(Transform(step_lbl, new_lbl), Transform(cap, new_cap),
                  Create(exact_curve), run_time=2.0)
        self.wait(4.0)
