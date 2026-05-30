"""delib — the shared library for the differential-equations playground.

The *only* code shared between chapters. Chapters import from here; they
never import one another.
"""

from __future__ import annotations

from delib.solvers import solve_ode, solve_system
from delib.fields import (
    slope_field,
    slope_field_data,
    slope_field_plotly,
    vector_field_plotly,
    vector_field,
    phase_portrait,
    overlay_solution,
    phase_line,
    potential_plot,
)
from delib.animate import (
    animate_time,
    animate_plotly,
    flow_field,
    solution_surface,
    frame_index,
)
from delib.ui import (
    param_slider,
    param_panel,
    run_exercise,
    ai_code,
    equilibria_report,
    exercise_inputs,
    exercise_ai,
    exercise_view,
    check_number,
    closed_form_report,
    solve_steps,
    derivation,
    video,
    key_field,
    key_bridge_widget,
    cell_picker_widget,
    persist_key,
    tutor_chat,
    tutor_sidebar,
)

__all__ = [
    "solve_ode",
    "solve_system",
    "slope_field",
    "slope_field_data",
    "slope_field_plotly",
    "vector_field_plotly",
    "vector_field",
    "phase_portrait",
    "overlay_solution",
    "phase_line",
    "potential_plot",
    "animate_time",
    "animate_plotly",
    "flow_field",
    "solution_surface",
    "frame_index",
    "param_slider",
    "param_panel",
    "run_exercise",
    "ai_code",
    "equilibria_report",
    "exercise_inputs",
    "exercise_ai",
    "exercise_view",
    "check_number",
    "closed_form_report",
    "solve_steps",
    "derivation",
    "video",
    "key_field",
    "key_bridge_widget",
    "cell_picker_widget",
    "persist_key",
    "tutor_chat",
    "tutor_sidebar",
]
