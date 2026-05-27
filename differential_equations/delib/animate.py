"""Time-animation helpers.

Two playback strategies, matching how marimo actually behaves:

* :func:`animate_plotly` builds a figure with native play/pause + a frame
  slider. This is the recommended path for *inline* playback in a notebook.
* :func:`animate_time` builds a matplotlib ``FuncAnimation``. Inline live
  playback is unreliable under marimo's reactive model, so treat this as the
  *export* path (``.to_html5_video`` / ``.save`` to gif or mp4).
* :func:`frame_index` turns a ``mo.ui.refresh`` tick count into a looping
  frame index for pure-Python autoplay without any animation object.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure

__all__ = ["animate_time", "animate_plotly", "frame_index"]


def animate_time(
    update_fn: Callable[[int], Any],
    frames: int,
    *,
    fps: int = 30,
    fig: Figure | None = None,
    backend: str = "matplotlib",
) -> FuncAnimation:
    """Build a matplotlib ``FuncAnimation`` for export to gif/mp4.

    ``update_fn(i)`` draws frame ``i`` (0-indexed). Save the result with
    ``anim.save("assets/foo.gif", writer="pillow", fps=fps)``.
    """
    if backend != "matplotlib":
        raise ValueError(
            f"animate_time only supports the matplotlib backend; "
            f"use animate_plotly for inline play/pause (got {backend!r})."
        )
    if fig is None:
        fig = plt.gcf()
    interval = 1000 / fps
    return FuncAnimation(fig, update_fn, frames=frames, interval=interval, blit=False)


def animate_plotly(
    frames_data: Sequence[dict],
    *,
    layout: dict | None = None,
    fps: int = 30,
    transition_ms: int | None = None,
    easing: str = "cubic-in-out",
    template: str | None = None,
):
    """Build a Plotly figure with play/pause buttons and a frame slider.

    ``frames_data`` is a sequence of dicts, each holding the traces for one
    frame, e.g. ``{"data": [go.Scatter(...)], "name": "0"}``. The first
    frame's data seeds the initial view.

    Set ``transition_ms`` (defaults to one frame) to tween between frames for
    fluid motion, ``easing`` for the tween curve, and ``template`` (e.g.
    ``"plotly_dark"``) for a themed look.
    """
    import plotly.graph_objects as go

    if not frames_data:
        raise ValueError("frames_data must contain at least one frame.")

    frames = [
        go.Frame(data=fd["data"], name=fd.get("name", str(i)))
        for i, fd in enumerate(frames_data)
    ]
    duration = int(1000 / fps)
    tween = duration if transition_ms is None else int(transition_ms)
    transition = {"duration": tween, "easing": easing}

    fig = go.Figure(data=frames_data[0]["data"], frames=frames)
    fig.update_layout(
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "showactive": False,
                "x": 0.0,
                "y": 1.12,
                "xanchor": "left",
                "yanchor": "top",
                "pad": {"r": 8, "t": 4, "b": 4, "l": 8},
                "bgcolor": "rgba(127,127,127,0.12)",
                "bordercolor": "rgba(127,127,127,0.35)",
                "borderwidth": 1,
                "font": {"size": 13},
                "buttons": [
                    {
                        "label": "▶  Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": duration, "redraw": True},
                                "fromcurrent": True,
                                "transition": transition,
                            },
                        ],
                    },
                    {
                        "label": "❚❚  Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                            },
                        ],
                    },
                ],
            }
        ],
        sliders=[
            {
                "x": 0.0,
                "len": 1.0,
                "pad": {"t": 36, "b": 8},
                "currentvalue": {"prefix": "t = ", "font": {"size": 13}},
                "transition": transition,
                "steps": [
                    {
                        "label": f.name,
                        "method": "animate",
                        "args": [
                            [f.name],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "transition": transition,
                                "mode": "immediate",
                            },
                        ],
                    }
                    for f in frames
                ],
            }
        ],
    )
    if template:
        fig.update_layout(template=template)
    if layout:
        fig.update_layout(**layout)
    return fig


def frame_index(tick: int, frames: int) -> int:
    """Map a monotonically increasing ``mo.ui.refresh`` tick to a loop frame.

    Lets a chapter autoplay from pure Python state: bind a ``mo.ui.refresh``,
    read its value as ``tick``, and use ``frame_index(tick, n)`` to pick which
    frame to render on each reactive re-run.
    """
    if frames <= 0:
        raise ValueError("frames must be positive.")
    return tick % frames
