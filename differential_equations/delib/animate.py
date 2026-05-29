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

__all__ = [
    "animate_time",
    "animate_plotly",
    "flow_field",
    "solution_surface",
    "frame_index",
]


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


def _arrows_xy(GX, GY, S, xspan, yspan, *, density, aspect=2.2, scale=1.0,
               head: float = 0.32, spread: float = 0.5):
    """(xs, ys) for one Scatter of arrows with heads; fixed coords per arrow.

    Arrows are sized in display-pixel space (the direction ``(1, S)`` converted
    to pixels via an assumed box ``aspect``, normalised to a uniform on-screen
    length, then mapped back to data) so they read uniformly regardless of how
    differently the axes are scaled. Mirrors ``fields._field_arrows``.
    """
    import numpy as _np

    ca, sa = float(_np.cos(spread)), float(_np.sin(spread))
    pxx = aspect / xspan
    pxy = 1.0 / yspan
    length = scale / density
    xs: list = []
    ys: list = []
    for xi, yi, si in zip(GX.ravel(), GY.ravel(), S.ravel()):
        vx, vy = pxx, pxy * si
        n = (vx * vx + vy * vy) ** 0.5 or 1.0
        ux, uy = vx / n, vy / n
        hx, hy = xi + ux * length / pxx, yi + uy * length / pxy
        bx, by = -ux * length * head, -uy * length * head
        w1x, w1y = hx + (bx * ca - by * sa) / pxx, hy + (bx * sa + by * ca) / pxy
        w2x, w2y = hx + (bx * ca + by * sa) / pxx, hy + (-bx * sa + by * ca) / pxy
        xs += [xi, hx, None, hx, w1x, None, hx, w2x, None]
        ys += [yi, hy, None, hy, w1y, None, hy, w2y, None]
    return xs, ys


def flow_field(
    f: Callable,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    *,
    n_particles: int = 160,
    n_frames: int = 70,
    density: int = 16,
    particle_color: str = "#d1495b",
    field_color: str = "rgba(91,125,177,0.55)",
    extra_lines: Sequence | None = None,
    title: str | None = None,
    seed: int = 0,
):
    """Animate the *flow* of ``y' = f(x, y)``: a cloud of particles advected
    along the (static) field, streaming and converging onto its attractors.

    The field is drawn as arrows for context; particles ride along them. Change
    the parameters of ``f`` to reshape the field. ``extra_lines`` (e.g.
    equilibria) sit underneath. Returns a light-theme go.Figure with play/slider.

    The static field is drawn once in the base figure and each frame updates only
    the particle trace, so the payload stays small (no per-frame field copies).
    """
    import numpy as _np
    import plotly.graph_objects as go

    rng = _np.random.default_rng(seed)
    x0, x1 = xlim
    y0, y1 = ylim
    dx = (x1 - x0) / (n_frames * 0.8)
    px = rng.uniform(x0, x1, n_particles)
    py = rng.uniform(y0, y1, n_particles)

    # static field of arrows — drawn ONCE in the base, never per frame
    GX, GY = _np.meshgrid(_np.linspace(x0, x1, density), _np.linspace(y0, y1, density))
    S = f(GX, GY) * _np.ones_like(GX)
    fxs, fys = _arrows_xy(GX, GY, S, x1 - x0, y1 - y0, density=density)
    field = go.Scatter(x=fxs, y=fys, mode="lines",
                       line=dict(color=field_color, width=1.2),
                       hoverinfo="skip", showlegend=False)
    base = [field] + (list(extra_lines) if extra_lines else [])
    p_idx = len(base)  # index of the particle trace we animate

    def dots(xs, ys):
        return go.Scatter(x=xs.copy(), y=ys.copy(), mode="markers",
                          marker=dict(color=particle_color, size=6, opacity=0.85),
                          hoverinfo="skip", showlegend=False)

    positions = [(px.copy(), py.copy())]
    for _ in range(n_frames - 1):
        py = py + f(px, py) * dx
        px = px + dx
        out = (px > x1) | (py < y0 - 1.5) | (py > y1 + 1.5)
        m = int(out.sum())
        if m:
            px[out] = x0
            py[out] = rng.uniform(y0, y1, m)
        positions.append((px.copy(), py.copy()))

    frames = [
        go.Frame(data=[dots(xs, ys)], traces=[p_idx], name=str(k))
        for k, (xs, ys) in enumerate(positions)
    ]
    duration = int(1000 / 24)
    play = {"frame": {"duration": duration, "redraw": False}, "fromcurrent": True,
            "transition": {"duration": 0}}
    fig = go.Figure(data=base + [dots(*positions[0])], frames=frames)
    fig.update_layout(
        template="plotly_white",
        title=(dict(text=title, x=0.02) if title else None),
        xaxis=dict(title="x", range=[x0, x1], zeroline=False),
        yaxis=dict(title="y", range=[y0, y1], zeroline=False),
        paper_bgcolor="white", plot_bgcolor="white",
        height=460, showlegend=False, margin=dict(l=55, r=20, t=70, b=45),
        updatemenus=[{
            "type": "buttons", "direction": "left", "showactive": False,
            "x": 0.0, "y": 1.12, "xanchor": "left", "yanchor": "top",
            "pad": {"r": 8, "t": 4, "b": 4, "l": 8},
            "bgcolor": "rgba(127,127,127,0.12)", "bordercolor": "rgba(127,127,127,0.35)",
            "borderwidth": 1, "font": {"size": 13},
            "buttons": [
                {"label": "▶  Play", "method": "animate", "args": [None, play]},
                {"label": "❚❚  Pause", "method": "animate",
                 "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]},
            ],
        }],
        sliders=[{
            "x": 0.0, "len": 1.0, "pad": {"t": 36, "b": 8},
            "currentvalue": {"prefix": "frame ", "font": {"size": 13}},
            "steps": [
                {"label": str(k), "method": "animate",
                 "args": [[str(k)], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
                for k in range(n_frames)
            ],
        }],
    )
    return fig


def solution_surface(
    f: Callable,
    t_span: tuple[float, float],
    y0_values: Sequence[float],
    *,
    n_t: int = 60,
    colorscale: str = "Tealrose",
    title: str | None = None,
):
    """3D surface ``z = y(t; y0)`` over ``(t, y0)``: every initial condition's
    trajectory at once, so you can see them all bend toward the attractor.

    ``f`` is ``f(t, y)`` and must be vectorized over an array ``y`` (the ensemble
    of initial conditions is integrated together with RK4). Returns a go.Figure.
    """
    import numpy as _np
    import plotly.graph_objects as go

    t0, t1 = t_span
    ts = _np.linspace(t0, t1, n_t)
    dt = (t1 - t0) / (n_t - 1)
    y = _np.asarray(y0_values, dtype=float).copy()
    rows = [y.copy()]
    tt = t0
    for _ in range(n_t - 1):
        k1 = f(tt, y)
        k2 = f(tt + 0.5 * dt, y + 0.5 * dt * k1)
        k3 = f(tt + 0.5 * dt, y + 0.5 * dt * k2)
        k4 = f(tt + dt, y + dt * k3)
        y = y + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        tt += dt
        rows.append(y.copy())
    Z = _np.array(rows).T  # (len(y0), n_t): row = y0, col = t

    fig = go.Figure(
        go.Surface(
            x=ts, y=_np.asarray(y0_values, dtype=float), z=Z,
            colorscale=colorscale, showscale=False,
            contours={"z": {"show": True, "usecolormap": True, "project": {"z": True}}},
        )
    )
    fig.update_layout(
        template="plotly_white",
        title=(dict(text=title, x=0.02) if title else None),
        scene=dict(
            xaxis_title="t", yaxis_title="y₀", zaxis_title="y(t)",
            camera=dict(eye=dict(x=1.6, y=-1.6, z=0.9)),
        ),
        height=520, margin=dict(l=0, r=0, t=40, b=0),
    )
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
