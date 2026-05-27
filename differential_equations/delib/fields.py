"""Slope fields, vector fields, and phase portraits.

Plotting is split from data generation on purpose: ``*_data`` functions
return plain NumPy arrays (cheap to unit-test and to recompute on every
slider tick), while the drawing helpers turn that data into matplotlib axes.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
from numpy.typing import NDArray

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

__all__ = [
    "slope_field_data",
    "slope_field",
    "slope_field_plotly",
    "vector_field",
    "phase_portrait",
    "overlay_solution",
]

# y' = f(x, y) for a first-order scalar ODE.
ScalarRHS = Callable[[NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]]
# (u, v) = F(x, y) for a 2D vector field.
VectorRHS = Callable[
    [NDArray[np.float64], NDArray[np.float64]],
    tuple[NDArray[np.float64], NDArray[np.float64]],
]


def slope_field_data(
    f: ScalarRHS,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    *,
    density: int = 20,
) -> tuple[NDArray, NDArray, NDArray, NDArray]:
    """Compute a normalized slope-field grid for ``y' = f(x, y)``.

    Returns ``(X, Y, U, V)`` where each segment ``(U, V)`` is a unit vector
    pointing along the slope ``f(x, y)``. Normalizing keeps arrow lengths
    uniform so the *direction* of the flow reads cleanly regardless of how
    steep the slope gets.
    """
    xs = np.linspace(xlim[0], xlim[1], density)
    ys = np.linspace(ylim[0], ylim[1], density)
    X, Y = np.meshgrid(xs, ys)
    slope = f(X, Y)
    U = np.ones_like(X)
    V = slope
    norm = np.hypot(U, V)
    norm[norm == 0] = 1.0
    return X, Y, U / norm, V / norm


def slope_field(
    f: ScalarRHS,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    *,
    density: int = 20,
    ax: Axes | None = None,
) -> Axes:
    """Draw the slope field of a first-order ODE ``y' = f(x, y)``."""
    if ax is None:
        _, ax = plt.subplots(figsize=(7, 5))
    X, Y, U, V = slope_field_data(f, xlim, ylim, density=density)
    ax.quiver(
        X, Y, U, V,
        angles="xy",
        pivot="middle",
        color="#5b7db1",
        alpha=0.7,
        width=0.0025,
        headwidth=0,
        headlength=0,
        headaxislength=0,
    )
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return ax


def vector_field(
    F: VectorRHS,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    *,
    density: int = 20,
    ax: Axes | None = None,
    streamplot: bool = False,
) -> Axes:
    """Draw a 2D vector field ``(u, v) = F(x, y)`` as a quiver or streamplot."""
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
    xs = np.linspace(xlim[0], xlim[1], density)
    ys = np.linspace(ylim[0], ylim[1], density)
    X, Y = np.meshgrid(xs, ys)
    U, V = F(X, Y)
    if streamplot:
        ax.streamplot(X, Y, U, V, color="#5b7db1", density=1.2)
    else:
        ax.quiver(X, Y, U, V, color="#5b7db1", alpha=0.8)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return ax


def phase_portrait(
    F: VectorRHS,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    *,
    trajectories: Sequence[tuple[NDArray, NDArray]] | None = None,
    density: int = 20,
    ax: Axes | None = None,
) -> Axes:
    """Streamplot of a 2D system, optionally overlaying solution trajectories.

    ``trajectories`` is a sequence of ``(xs, ys)`` arrays (e.g. the rows of a
    :func:`delib.solvers.solve_system` result) drawn on top of the flow.
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(6, 6))
    vector_field(F, xlim, ylim, density=density, ax=ax, streamplot=True)
    if trajectories:
        for xs, ys in trajectories:
            ax.plot(xs, ys, lw=2, color="#d1495b")
            ax.plot(xs[0], ys[0], "o", color="#d1495b")
    return ax


def overlay_solution(
    ax: Axes,
    t: NDArray,
    y: NDArray,
    *,
    color: str = "#d1495b",
    label: str | None = None,
) -> Axes:
    """Draw a solution curve ``y(t)`` on an existing field axis.

    ``t`` is the independent variable (plotted on x) and ``y`` the solution.
    Marks the initial point so the start of the trajectory is obvious.
    """
    ax.plot(t, y, lw=2.5, color=color, label=label, zorder=5)
    ax.plot(t[0], y[0], "o", color=color, zorder=6)
    if label:
        ax.legend(loc="best")
    return ax


def slope_field_plotly(
    f: ScalarRHS,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    *,
    density: int = 18,
    color: str = "#5b7db1",
    title: str | None = None,
):
    """Light-theme Plotly slope field for ``y' = f(x, y)``; returns a go.Figure.

    The Plotly counterpart of :func:`slope_field`, so a chapter's static, slider,
    animated, and AI-generated views can all share one consistent look. Segments
    are uniform-length direction marks (no arrowheads), drawn as a single trace.
    """
    import plotly.graph_objects as go

    X, Y, U, V = slope_field_data(f, xlim, ylim, density=density)
    sx = (xlim[1] - xlim[0]) / density * 0.42
    sy = (ylim[1] - ylim[0]) / density * 0.42
    xs: list = []
    ys: list = []
    for xi, yi, ui, vi in zip(X.ravel(), Y.ravel(), U.ravel(), V.ravel()):
        xs += [xi - ui * sx, xi + ui * sx, None]
        ys += [yi - vi * sy, yi + vi * sy, None]
    fig = go.Figure(
        go.Scatter(
            x=xs, y=ys, mode="lines",
            line=dict(color=color, width=1.4), opacity=0.7,
            hoverinfo="skip", showlegend=False,
        )
    )
    fig.update_layout(
        template="plotly_white",
        title=(dict(text=title, x=0.02) if title else None),
        xaxis=dict(title="x", range=list(xlim), zeroline=False),
        yaxis=dict(title="y", range=list(ylim), zeroline=False),
        paper_bgcolor="white", plot_bgcolor="white",
        height=460, showlegend=False,
        margin=dict(l=55, r=20, t=50, b=45),
    )
    return fig
