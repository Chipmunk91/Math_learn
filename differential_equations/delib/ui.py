"""Standardized marimo UI controls so every chapter feels consistent."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import marimo as mo

__all__ = ["param_slider", "param_panel", "run_exercise", "ai_code"]


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


async def ai_code(instruction, current_code, key, *, context="",
                  model="claude-haiku-4-5-20251001"):
    """Ask Claude to write or edit a code answer for a single exercise.

    Given the student's plain-language ``instruction`` and their ``current_code``,
    returns the FULL updated program as a string (the python block extracted from
    the reply). On any error or empty key, returns ``current_code`` unchanged so
    the editor is never wiped. BYO key, called client-side.
    """
    import json
    import re

    if not (key and instruction and instruction.strip()):
        return current_code
    system = (
        "You write and edit Python for a math notebook. Given the student's request "
        "and their current code, reply with the FULL updated program as exactly one "
        "```python fenced block and nothing else. Use only mo, np, plt, go, delib "
        "(helpers: vector_field_plotly, flow_field, solution_surface, solve_ode). "
        "Assign what the task needs — a number to `answer`, and/or a Plotly figure to "
        "`view`. Do no file or network I/O. " + context
    )
    user = f"Current code:\n```python\n{current_code}\n```\n\nRequest: {instruction}"
    body = json.dumps({
        "model": model, "max_tokens": 800, "system": system,
        "messages": [{"role": "user", "content": user}],
    })
    headers = {
        "content-type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "anthropic-dangerous-direct-browser-access": "true",
    }
    url = "https://api.anthropic.com/v1/messages"
    try:
        from pyodide.http import pyfetch

        resp = await pyfetch(url, method="POST", headers=headers, body=body)
        data = await resp.json()
    except ModuleNotFoundError:
        import urllib.request
        import urllib.error

        req = urllib.request.Request(url, data=body.encode(), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as exc:
            data = json.loads(exc.read().decode())
    except Exception:
        return current_code

    if not (isinstance(data, dict) and data.get("content")):
        return current_code
    full = "".join(b.get("text", "") for b in data["content"])
    m = re.search(r"```(?:python)?\s*\n(.*?)```", full, re.S)
    return m.group(1).strip() if m else (full.strip() or current_code)
