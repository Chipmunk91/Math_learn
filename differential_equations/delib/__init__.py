"""delib — the shared library for the differential-equations playground.

The *only* code shared between chapters. Chapters import from here; they
never import one another.
"""

from __future__ import annotations

from delib.solvers import solve_ode, solve_system
from delib.fields import (
    slope_field,
    slope_field_data,
    vector_field,
    phase_portrait,
    overlay_solution,
)
from delib.animate import animate_time, animate_plotly, frame_index
from delib.ui import param_slider, param_panel
from delib.tutor import tutor, TUTOR_ENDPOINT

__all__ = [
    "solve_ode",
    "solve_system",
    "slope_field",
    "slope_field_data",
    "vector_field",
    "phase_portrait",
    "overlay_solution",
    "animate_time",
    "animate_plotly",
    "frame_index",
    "param_slider",
    "param_panel",
    "tutor",
    "TUTOR_ENDPOINT",
]
