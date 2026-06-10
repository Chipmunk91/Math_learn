"""From trajectories to the phase line — the signature construction of Ch 5.

Six trajectories of x' = x - x³ are drawn in the (t, x) plane (the chapter's
hook figure, brought to life). Then the compression happens on screen:

  1. mark the destinations — every trajectory parks at +1 or -1
  2. collapse time — each curve gives up its route and becomes its endpoint
  3. lay the line flat — the vertical position axis becomes a horizontal line
  4. add the flow — arrows from the sign of f, filled/open dots for stability

The end state is the phase line exactly as delib.phase_line draws it in the
chapter, so the video terminates on the picture the reader scrolls to next.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/phase_line_collapse.py ScenePhaseLineCollapse
    cp media/videos/phase_line_collapse/1080p60/ScenePhaseLineCollapse.mp4 \\
       assets/phase_line_collapse.mp4

Then it appears in ch05 via delib.video("phase_line_collapse.mp4").
"""

import pathlib
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import *  # noqa: F403,E402
import numpy as np  # noqa: E402

STABLE = "#2a9d8f"
UNSTABLE = "#d1495b"
FLOW = "#5b7db1"


def _caption(text):
    """Small grey caption in the lower band, auto-wrapped. Fixed position
    (the figure morphs between stages, so anchoring to a mobject would
    make captions jump around)."""
    wrapped = "\n".join(
        textwrap.fill(para, width=70) for para in text.split("\n")
    )
    t = Text(wrapped, font_size=20, color=GREY_B)
    t.move_to(DOWN * 3.0)
    return t


def _stage_label(text):
    """Stage header at the title slot (top-centre); the title fades out as
    the first stage label fades in, so the slot holds one heading at a time."""
    t = Text(text, font_size=26, color=BLUE_D, weight=BOLD)
    t.to_edge(UP, buff=0.25)
    return t


def _integrate(f, x0, t_end=6.0, n=240):
    """Hand-rolled RK4 so the scene has no scipy dependency."""
    h = t_end / n
    xs = [x0]
    x = x0
    for _ in range(n):
        k1 = f(x)
        k2 = f(x + 0.5 * h * k1)
        k3 = f(x + 0.5 * h * k2)
        k4 = f(x + h * k3)
        x = x + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        xs.append(x)
    return np.linspace(0.0, t_end, n + 1), np.array(xs)


class ScenePhaseLineCollapse(Scene):
    """Trajectories of x' = x - x³ collapse into the phase line."""

    def construct(self):
        f = lambda x: x - x ** 3
        starts = [-1.6, -0.8, -0.1, 0.1, 0.8, 1.6]

        # --- Setup: (t, x) axes + six trajectories ---------------------------
        axes = Axes(
            x_range=[0, 6, 1],
            y_range=[-2, 2, 1],
            x_length=8.0,
            y_length=4.0,
            tips=False,
            axis_config=dict(
                color=GREY_B, stroke_width=1.5,
                include_numbers=True, font_size=20,
            ),
        )
        axes.shift(UP * 0.4)
        axes_labels = axes.get_axis_labels(
            x_label=MathTex("t").scale(0.8),
            y_label=MathTex("x").scale(0.8),
        )

        curves = VGroup()
        for x0 in starts:
            ts, xs = _integrate(f, x0)
            pts = [axes.c2p(t, x) for t, x in zip(ts[::6], xs[::6])]
            c = VMobject(color=("#2f6fb0" if x0 > 0 else "#b5651d"),
                         stroke_width=2.5)
            c.set_points_smoothly(pts)
            curves.add(c)

        title = Text("Six trajectories of  ẋ = x − x³",
                     font_size=26).to_edge(UP, buff=0.25)
        cap = _caption(
            "Six starting positions, integrated forward in time — the "
            "hook figure, redrawn. Watch where each one ends."
        )

        self.play(Write(title))
        self.play(Create(axes), Write(axes_labels))
        self.play(Create(curves, lag_ratio=0.15), run_time=2.5)
        self.play(FadeIn(cap))
        self.wait(2.0)

        # --- Stage 1: mark the destinations ----------------------------------
        lbl = _stage_label("1 — the destinations")
        rest_lines = VGroup(
            DashedLine(axes.c2p(0, 1), axes.c2p(6, 1),
                       color=STABLE, stroke_width=2, dash_length=0.12),
            DashedLine(axes.c2p(0, -1), axes.c2p(6, -1),
                       color=STABLE, stroke_width=2, dash_length=0.12),
            DashedLine(axes.c2p(0, 0), axes.c2p(6, 0),
                       color=UNSTABLE, stroke_width=1.5, dash_length=0.06),
        )
        new_cap = _caption(
            "Every trajectory parks at +1 or −1. The middle height 0 is "
            "also a rest height of the equation — but nothing settles "
            "there, not even the start at 0.1."
        )
        self.play(FadeOut(title), FadeIn(lbl), Transform(cap, new_cap),
                  Create(rest_lines), run_time=1.4)
        self.wait(2.4)

        # --- Stage 2: collapse time ------------------------------------------
        new_lbl = _stage_label("2 — throw away the time axis")
        # Each curve contracts to a dot at its destination on the x-axis
        # (the vertical position axis at t = 0).
        end_dots = VGroup()
        for x0, c in zip(starts, curves):
            dest = 1.0 if x0 > 0 else -1.0
            d = Dot(axes.c2p(0, dest), color=STABLE, radius=0.10)
            end_dots.add(d)
        middle_open = Circle(radius=0.10, color=UNSTABLE, stroke_width=3
                             ).move_to(axes.c2p(0, 0))
        new_cap = _caption(
            "Each trajectory's only payload is its destination. Collapse "
            "every curve to its endpoint: two filled rest points used, "
            "one untouched in the middle."
        )
        self.play(Transform(lbl, new_lbl), Transform(cap, new_cap),
                  *[Transform(c, d) for c, d in zip(curves, end_dots)],
                  FadeOut(rest_lines),
                  FadeIn(middle_open),
                  FadeOut(axes_labels),
                  axes.animate.set_opacity(0.25),
                  run_time=1.8)
        self.wait(2.4)

        # --- Stage 3: lay the line flat ---------------------------------------
        new_lbl = _stage_label("3 — lay the position line flat")
        phase_axis = NumberLine(
            x_range=[-2, 2, 1],
            length=9.0,
            color=GREY_B, stroke_width=2,
            include_numbers=True, font_size=24,
        )
        phase_axis.move_to(ORIGIN + UP * 0.2)
        dot_m1 = Dot(phase_axis.n2p(-1), color=STABLE, radius=0.11)
        dot_p1 = Dot(phase_axis.n2p(1), color=STABLE, radius=0.11)
        dot_0 = Circle(radius=0.11, color=UNSTABLE, stroke_width=3.5
                       ).move_to(phase_axis.n2p(0))
        new_cap = _caption(
            "Rotate the surviving axis to horizontal. This line is the "
            "system's entire world: every state it can be in, and every "
            "place it can rest."
        )
        self.play(Transform(lbl, new_lbl), Transform(cap, new_cap),
                  FadeOut(axes),
                  ReplacementTransform(curves, VGroup(dot_m1, dot_p1)),
                  ReplacementTransform(middle_open, dot_0),
                  Create(phase_axis),
                  run_time=1.8)
        self.wait(2.0)

        # --- Stage 4: add the flow --------------------------------------------
        new_lbl = _stage_label("4 — add the flow")
        # One arrow per interval, direction from the sign of f at the
        # interval midpoint: -> <- -> <-
        arrows = VGroup()
        for x_mid, sign in [(-1.5, +1), (-0.5, -1), (0.5, +1), (1.5, -1)]:
            a = Arrow(
                start=phase_axis.n2p(x_mid - sign * 0.22),
                end=phase_axis.n2p(x_mid + sign * 0.22),
                color=FLOW, buff=0,
                stroke_width=5, tip_length=0.18,
                max_tip_length_to_length_ratio=0.5,
            )
            a.shift(UP * 0.45)
            arrows.add(a)
        legend = VGroup(
            Dot(color=STABLE, radius=0.09),
            Text("stable — arrows point in", font_size=20, color=GREY_B),
            Circle(radius=0.09, color=UNSTABLE, stroke_width=3),
            Text("unstable — arrows point out", font_size=20, color=GREY_B),
        ).arrange(RIGHT, buff=0.25)
        legend.next_to(phase_axis, DOWN, buff=0.9)
        new_cap = _caption(
            "Right where f > 0, left where f < 0. Both outer dots collect "
            "their arrows: stable. The middle dot sheds them: unstable. "
            "This is the phase line — every starting point's fate, in one "
            "picture."
        )
        self.play(Transform(lbl, new_lbl), Transform(cap, new_cap),
                  *[GrowArrow(a) for a in arrows],
                  run_time=1.6)
        self.play(FadeIn(legend))
        self.wait(4.0)
