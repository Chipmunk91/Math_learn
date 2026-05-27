"""Standardized marimo UI controls so every chapter feels consistent."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import marimo as mo

__all__ = ["param_slider", "param_panel", "run_exercise"]


def param_slider(
    label: str,
    start: float,
    stop: float,
    step: float,
    value: float,
):
    """A labelled :func:`marimo.ui.slider` with the value shown inline."""
    return mo.ui.slider(
        start=start,
        stop=stop,
        step=step,
        value=value,
        label=label,
        show_value=True,
    )


def param_panel(specs: Sequence[Mapping]):
    """Build a group of sliders keyed by name.

    ``specs`` is a sequence of dicts like
    ``{"name": "a", "label": "growth a", "start": -2, "stop": 2,
       "step": 0.1, "value": 1.0}``.

    Returns a :func:`marimo.ui.dictionary`; read individual values via
    ``panel.value["a"]`` and display the controls with ``mo.vstack`` over
    ``panel.values()`` (or just render ``panel``).
    """
    sliders = {
        spec["name"]: param_slider(
            spec.get("label", spec["name"]),
            spec["start"],
            spec["stop"],
            spec["step"],
            spec["value"],
        )
        for spec in specs
    }
    return mo.ui.dictionary(sliders)


def run_exercise(code: str, run_pressed: bool, *, check=None, ns_extra: Mapping | None = None):
    """Run a student's code answer and auto-grade it.

    Pair with a ``mo.ui.code_editor`` and a ``mo.ui.run_button`` in the chapter::

        delib.run_exercise(editor.value, run_btn.value, check=my_check)

    Execs ``code`` in the standard namespace (``mo, np, plt, go, delib`` plus any
    ``ns_extra``), renders a ``view`` if the code assigns one, and runs
    ``check(ns) -> (ok: bool, message: str)`` to show a pass/fail callout. The
    student code runs in the visitor's own browser sandbox, so it can only affect
    their session. Returns a marimo object to display.
    """
    if not run_pressed:
        return mo.md("*Write your answer above and press **Run**.*")

    import traceback
    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go
    import delib as _delib

    ns = {"mo": mo, "np": np, "plt": plt, "go": go, "delib": _delib}
    if ns_extra:
        ns.update(ns_extra)
    try:
        exec(code, ns)
    except Exception:
        return mo.callout(mo.md(f"```\n{traceback.format_exc()}\n```"), kind="danger")

    out = []
    view = ns.get("view")
    if isinstance(view, matplotlib.axes.Axes):
        view = view.figure
    if view is not None:
        out.append(view)
    if check is not None:
        try:
            ok, msg = check(ns)
        except Exception as exc:
            ok, msg = False, f"checker error: {exc}"
        out.append(mo.callout(mo.md(("✅ " if ok else "❌ ") + msg),
                              kind=("success" if ok else "warn")))
    return mo.vstack(out) if out else mo.md("*(ran with no output)*")
