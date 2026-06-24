"""Variation of parameters — hero derivation (TO BE REBUILT).

The previous five-step derivation has been removed: Chapter 8's Method 2
is being rewritten from scratch around a linear-algebra framing (the
Wronskian as a determinant / linear-independence test, the 2x2 system as
"express the forcing's demand in the basis of homogeneous states"). A new
scene will be authored to match that narrative.

For now this file holds only a placeholder card so the CI render target
``SceneVariationOfParameters`` still exists. The chapter does not embed
this clip while Method 2 is under construction.

Render (Manim Community v0.18+, needs LaTeX + ffmpeg):

    manim render -qh manim/variation_of_parameters.py SceneVariationOfParameters
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from manim import *  # noqa: F403,E402


class SceneVariationOfParameters(Scene):
    """Placeholder — the real derivation is being rewritten."""

    def construct(self):
        title = Text(
            "Variation of parameters",
            font_size=34,
        )
        sub = Text(
            "derivation being rebuilt around a linear-algebra framing",
            font_size=20, color=GREY_B,
        ).next_to(title, DOWN, buff=0.4)
        self.add(title, sub)
        self.wait(1.0)
