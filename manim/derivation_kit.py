"""Shared helpers for hand-choreographed Manim derivations (rendered OFFLINE).

Each derivation keeps a persistent mobject per glyph so every symbol's path is
deterministic (no shape-matching heuristic). These helpers carry the bits every
such scene reuses: fraction-bar sizing, a standard glyph scale, and the accent
color used to highlight the symbol currently being manipulated.
"""

from manim import *  # noqa: F403  (offline-only; manim is not a project dependency)

GLYPH_SCALE = 1.3
HIGHLIGHT = TEAL  # color for symbols being actively manipulated (a tracking aid)


def vinc(*parts, pad=0.2):
    """A fraction bar (Line) wide enough to span the widest neighbour."""
    w = max(p.width for p in parts) + pad
    return Line(LEFT * w / 2, RIGHT * w / 2)


def glyph(tex, *, color=None, scale=GLYPH_SCALE):
    """A single persistent ``MathTex`` glyph, scaled (and optionally highlighted)."""
    m = MathTex(tex).scale(scale)
    if color is not None:
        m.set_color(color)
    return m
