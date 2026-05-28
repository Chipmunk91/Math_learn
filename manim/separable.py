"""Sample Manim scene — a hero derivation, rendered OFFLINE.

Manim cannot run in the browser/WASM, so hero derivations are rendered on a
machine that has Manim + ffmpeg + LaTeX, then committed as a video.

Render (example):

    manim render -qh manim/separable.py SeparableCooling
    # output lands in media/videos/...; move/rename it into assets/:
    cp media/videos/separable/1080p60/SeparableCooling.mp4 assets/cooling_separable.mp4

Then embed it in a chapter's concept beat:

    delib.video("cooling_separable.mp4", caption="Solving by separation of variables")

For non-hero derivations, prefer the serverless in-browser player
``delib.derivation([...])`` instead of rendering a video.
"""

from manim import *  # noqa: F403  (offline-only; manim is not a project dependency)


class SeparableCooling(Scene):
    """Newton's law of cooling solved by separation of variables, with the terms
    morphing from each line into the next (Manim TransformMatchingTex)."""

    def construct(self):
        e1 = MathTex(r"\frac{dT}{dt}", "=", "-k", "(T - T_r)")
        e2 = MathTex(r"\frac{dT}{T - T_r}", "=", "-k", r"\,dt")
        e3 = MathTex(r"\ln|T - T_r|", "=", "-k", "t + C")
        e4 = MathTex("T(t)", "=", "T_r", "+ (T_0 - T_r) e^{-kt}")

        self.play(Write(e1))
        self.wait(0.6)
        self.play(TransformMatchingTex(e1, e2))
        self.wait(0.6)
        self.play(TransformMatchingTex(e2, e3))
        self.wait(0.6)
        self.play(TransformMatchingTex(e3, e4))
        self.wait(1.2)
