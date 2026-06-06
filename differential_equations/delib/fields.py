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
    "vector_field_plotly",
    "vector_field",
    "phase_portrait",
    "overlay_solution",
    "phase_line",
    "potential_plot",
    "level_curves",
    "euler_steps",
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


def _field_arrows(GX, GY, S, xspan, yspan, *, density, aspect=2.2, scale=1.0,
                  head: float = 0.32, spread: float = 0.5):
    """Build (xs, ys) for a single Scatter of arrows with heads.

    Arrows are sized in *display-pixel* space, not per-axis data space: the
    direction ``(1, S)`` is converted to pixels using an assumed plot-box
    width:height ``aspect`` (the x- and y-axes are scaled to very different
    pixels-per-unit when their ranges differ — e.g. temperature 10..95 vs time
    0..30), normalised to a uniform on-screen length, then mapped back to data
    units. So every arrow reads the same visual length and the heads stay
    undistorted, regardless of the axis ranges. Each arrow emits a fixed 9
    coordinates (shaft + two head strokes, None-separated) so the count is
    identical regardless of direction, which lets Plotly tween the field
    smoothly between animation frames.
    """
    import numpy as np

    ca, sa = float(np.cos(spread)), float(np.sin(spread))
    pxx = aspect / xspan          # pixels per x-unit (treat box height as 1)
    pxy = 1.0 / yspan             # pixels per y-unit
    length = scale / density      # uniform arrow length, in box-height fractions
    xs: list = []
    ys: list = []
    for xi, yi, si in zip(GX.ravel(), GY.ravel(), S.ravel()):
        vx, vy = pxx, pxy * si
        n = (vx * vx + vy * vy) ** 0.5 or 1.0
        ux, uy = vx / n, vy / n               # unit direction in pixel space
        hx, hy = xi + ux * length / pxx, yi + uy * length / pxy
        bx, by = -ux * length * head, -uy * length * head
        w1x, w1y = hx + (bx * ca - by * sa) / pxx, hy + (bx * sa + by * ca) / pxy
        w2x, w2y = hx + (bx * ca + by * sa) / pxx, hy + (-bx * sa + by * ca) / pxy
        xs += [xi, hx, None, hx, w1x, None, hx, w2x, None]
        ys += [yi, hy, None, hy, w1y, None, hy, w2y, None]
    return xs, ys


def vector_field_plotly(
    f: ScalarRHS,
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    *,
    density: int = 16,
    color: str = "#5b7db1",
    title: str | None = None,
    scale: float = 1.0,
    aspect: float = 2.2,
):
    """Light-theme Plotly *vector* field (arrows with heads) for ``y' = f(x, y)``.

    Like :func:`slope_field_plotly` but draws true arrows pointing along the flow
    direction ``(1, f)``, for a 3b1b-style vector-field look. Arrows are sized in
    display-pixel space (see :func:`_field_arrows`) so they read at a uniform
    on-screen length even when the axes have very different ranges; ``aspect`` is
    the assumed plot width:height and ``scale`` tunes the arrow length. Returns a
    go.Figure.
    """
    import plotly.graph_objects as go

    xs_grid = np.linspace(xlim[0], xlim[1], density)
    ys_grid = np.linspace(ylim[0], ylim[1], density)
    X, Y = np.meshgrid(xs_grid, ys_grid)
    S = f(X, Y) * np.ones_like(X)
    xs, ys = _field_arrows(X, Y, S, xlim[1] - xlim[0], ylim[1] - ylim[0],
                           density=density, aspect=aspect, scale=scale)
    fig = go.Figure(
        go.Scatter(x=xs, y=ys, mode="lines",
                   line=dict(color=color, width=1.4), opacity=0.85,
                   hoverinfo="skip", showlegend=False)
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


# --- Euler walk: a polyline from the slope rule ------------------------------

def euler_steps(
    f: Callable[[float, float], float],
    x0: float,
    y0: float,
    h: float,
    n: int,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Apply Euler's method to ``y' = f(x, y)`` for ``n`` steps of width ``h``.

    Returns ``(xs, ys)`` arrays of length ``n + 1`` (including the starting
    point). At each step the slope is read at the *current* point — the
    simplest possible recipe, exactly as derived in Chapter 4.
    """
    xs = np.empty(n + 1, dtype=float)
    ys = np.empty(n + 1, dtype=float)
    xs[0], ys[0] = float(x0), float(y0)
    for i in range(n):
        xs[i + 1] = xs[i] + h
        ys[i + 1] = ys[i] + h * float(f(xs[i], ys[i]))
    return xs, ys


# --- 1-D dynamics: phase line + potential ------------------------------------
# Shared palette so the phase line and the potential plot mark the same fixed
# point the same way (filled teal = stable, open red = unstable).
_STABLE = "#2a9d8f"
_UNSTABLE = "#d1495b"
_MARBLE = "#d1495b"


def _eval(f, xs):
    """Evaluate f(xs), trying vectorised first; fall back to per-point."""
    try:
        return np.asarray(f(xs), dtype=float)
    except Exception:
        return np.asarray([float(f(xi)) for xi in xs])


def _find_zeros(xs, fs):
    """Linear-interp the zeros of f from samples (xs, fs)."""
    sign = np.sign(fs)
    idx = np.where(sign[:-1] * sign[1:] < 0)[0]  # strict crossings only
    out = []
    for i in idx:
        denom = fs[i + 1] - fs[i]
        out.append(float(xs[i] - fs[i] * (xs[i + 1] - xs[i]) / denom))
    # Also pick up exact zeros that aren't crossings (rare; flat touches).
    for i in np.where(fs == 0)[0]:
        x0 = float(xs[i])
        if all(abs(x0 - z) > 1e-9 for z in out):
            out.append(x0)
    out.sort()
    return out


def _fprime(f, x, h=1e-4):
    """Central-difference derivative of f at x."""
    return (float(f(x + h)) - float(f(x - h))) / (2.0 * h)


def phase_line(
    f,
    xrange: tuple[float, float],
    *,
    density: int = 200,
    marker_x: float | None = None,
    title: str | None = None,
):
    """1-D phase line for ``dx/dt = f(x)`` — the chapter-3 hero visual.

    Draws a horizontal axis from ``xrange[0]`` to ``xrange[1]`` with fixed
    points marked: filled teal for **stable** (``f'(x*) < 0``, the flow pulls
    back), open red for **unstable** (``f'(x*) > 0``, a nudge pushes away).
    One arrow per interval points in the direction of the flow. An optional
    ``marker_x`` puts a marble above the line for the chapter's slider.
    """
    import plotly.graph_objects as go

    x0, x1 = xrange
    xs = np.linspace(x0, x1, density)
    fs = _eval(f, xs)
    fps = _find_zeros(xs, fs)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[x0, x1], y=[0, 0], mode="lines",
        line=dict(color="#7c8aa0", width=1.4),
        hoverinfo="skip", showlegend=False,
    ))

    # One arrow per interval between fixed points (and the endpoints), drawn
    # via Plotly annotations so the arrowheads render crisply at any zoom.
    boundaries = [x0] + list(fps) + [x1]
    arrow_len = (x1 - x0) * 0.06
    for j in range(len(boundaries) - 1):
        mid = 0.5 * (boundaries[j] + boundaries[j + 1])
        if boundaries[j + 1] - boundaries[j] < arrow_len * 0.6:
            continue
        sgn = float(np.sign(f(mid)))
        if sgn == 0:
            continue
        ax_x = mid - sgn * arrow_len / 2
        x_x = mid + sgn * arrow_len / 2
        fig.add_annotation(
            x=x_x, y=0, ax=ax_x, ay=0,
            xref="x", yref="y", axref="x", ayref="y",
            arrowhead=2, arrowsize=1.4, arrowwidth=1.6,
            arrowcolor="#5b7db1", showarrow=True,
        )

    stable_x, unstable_x = [], []
    for xp in fps:
        slope = _fprime(f, xp)
        (stable_x if slope < 0 else unstable_x).append(xp)
    if stable_x:
        fig.add_trace(go.Scatter(
            x=stable_x, y=[0] * len(stable_x), mode="markers",
            marker=dict(color=_STABLE, size=14, symbol="circle",
                        line=dict(color=_STABLE, width=2)),
            name="stable", hovertemplate="stable: x = %{x:.3f}<extra></extra>",
        ))
    if unstable_x:
        fig.add_trace(go.Scatter(
            x=unstable_x, y=[0] * len(unstable_x), mode="markers",
            marker=dict(color="white", size=14, symbol="circle",
                        line=dict(color=_UNSTABLE, width=2)),
            name="unstable", hovertemplate="unstable: x = %{x:.3f}<extra></extra>",
        ))
    if marker_x is not None:
        fig.add_trace(go.Scatter(
            x=[marker_x], y=[0.18], mode="markers",
            marker=dict(color=_MARBLE, size=18, symbol="circle",
                        line=dict(color="#7a2a3a", width=1.4)),
            hoverinfo="skip", showlegend=False,
        ))

    fig.update_layout(
        template="plotly_white",
        title=(dict(text=title, x=0.02) if title else None),
        xaxis=dict(title="x", range=[x0, x1], zeroline=False),
        yaxis=dict(visible=False, range=[-0.55, 0.55]),
        paper_bgcolor="white", plot_bgcolor="white",
        height=220, showlegend=True,
        legend=dict(x=0, y=1.18, orientation="h"),
        margin=dict(l=20, r=20, t=60, b=40),
    )
    return fig


def potential_plot(
    f,
    xrange: tuple[float, float],
    *,
    n: int = 300,
    marker_x: float | None = None,
    title: str | None = None,
):
    """The potential landscape ``V(x) = -∫_{x0}^{x} f(s) ds`` (so ``f = -V'``).

    Draws ``V`` over ``xrange`` (cumulative-trapezoid integration of ``-f``)
    and marks every fixed point on the curve with the same colour code as
    :func:`phase_line`: filled teal at the valleys (stable), open red at the
    hills (unstable). An optional ``marker_x`` puts a marble on the landscape
    at that position so the slider can show which valley it falls into.
    """
    import plotly.graph_objects as go

    x0, x1 = xrange
    xs = np.linspace(x0, x1, n)
    fs = _eval(f, xs)
    seg = 0.5 * (fs[:-1] + fs[1:]) * np.diff(xs)
    V = np.concatenate([[0.0], -np.cumsum(seg)])  # V(x0) = 0

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=V, mode="lines",
        line=dict(color="#5b7db1", width=2.5),
        name="V(x)", hovertemplate="V(%{x:.3f}) = %{y:.3f}<extra></extra>",
    ))

    def V_at(x):
        return float(np.interp(x, xs, V))

    fps = _find_zeros(xs, fs)
    stable_x, stable_V, unstable_x, unstable_V = [], [], [], []
    for xp in fps:
        slope = _fprime(f, xp)
        if slope < 0:
            stable_x.append(xp); stable_V.append(V_at(xp))
        else:
            unstable_x.append(xp); unstable_V.append(V_at(xp))
    if stable_x:
        fig.add_trace(go.Scatter(
            x=stable_x, y=stable_V, mode="markers",
            marker=dict(color=_STABLE, size=14, symbol="circle",
                        line=dict(color=_STABLE, width=2)),
            name="stable (valley)",
            hovertemplate="stable: x = %{x:.3f}, V = %{y:.3f}<extra></extra>",
        ))
    if unstable_x:
        fig.add_trace(go.Scatter(
            x=unstable_x, y=unstable_V, mode="markers",
            marker=dict(color="white", size=14, symbol="circle",
                        line=dict(color=_UNSTABLE, width=2)),
            name="unstable (hill)",
            hovertemplate="unstable: x = %{x:.3f}, V = %{y:.3f}<extra></extra>",
        ))
    if marker_x is not None:
        fig.add_trace(go.Scatter(
            x=[marker_x], y=[V_at(marker_x)], mode="markers",
            marker=dict(color=_MARBLE, size=18, symbol="circle",
                        line=dict(color="#7a2a3a", width=1.4)),
            hoverinfo="skip", showlegend=False,
        ))

    fig.update_layout(
        template="plotly_white",
        title=(dict(text=title, x=0.02) if title else None),
        xaxis=dict(title="x", range=[x0, x1], zeroline=False),
        yaxis=dict(title="V(x)", zeroline=False),
        paper_bgcolor="white", plot_bgcolor="white",
        height=380, showlegend=True,
        legend=dict(x=0, y=1.10, orientation="h"),
        margin=dict(l=55, r=20, t=60, b=45),
    )
    return fig


# --- Exact equations: level curves ------------------------------------------

def level_curves(
    F,
    xrange: tuple[float, float],
    yrange: tuple[float, float],
    *,
    n: int = 80,
    levels=None,
    field=None,  # None | True | (M, N) callables
    title: str | None = None,
    height: int = 460,
    aspect: float = 1.0,
):
    """Contour plot of ``F(x, y)`` — the chapter-3 hero visual.

    For an exact ODE ``M dx + N dy = 0`` with conserved quantity ``F`` (so
    ``F_x = M``, ``F_y = N``), the **solution curves are the level sets**
    ``F(x, y) = C``. This helper draws those level sets over the rectangle
    ``xrange x yrange``. Optionally overlays the slope field:
    ``field=(M, N)`` uses your callables; ``field=True`` finite-differences
    them from ``F``. In both cases the field arrows should ride the contours.
    """
    import plotly.graph_objects as go

    xs = np.linspace(xrange[0], xrange[1], n)
    ys = np.linspace(yrange[0], yrange[1], n)
    X, Y = np.meshgrid(xs, ys)
    try:
        Z = np.asarray(F(X, Y), dtype=float)
    except Exception:
        Z = np.empty_like(X)
        for i in range(n):
            for j in range(n):
                Z[i, j] = float(F(X[i, j], Y[i, j]))

    contour_kwargs = dict(
        x=xs, y=ys, z=Z,
        colorscale=[[0.0, "#dceaf6"], [1.0, "#5b7db1"]],
        showscale=False,
        line=dict(width=1.6),
        contours=dict(showlabels=False, coloring="lines"),
        hovertemplate="F(%{x:.2f}, %{y:.2f}) = %{z:.3f}<extra></extra>",
    )
    if levels is not None:
        levels = sorted(set(float(v) for v in levels))
        if len(levels) >= 2:
            step = (levels[-1] - levels[0]) / (len(levels) - 1)
            contour_kwargs["contours"] = dict(
                start=levels[0], end=levels[-1], size=step,
                showlabels=False, coloring="lines",
            )
        else:
            contour_kwargs["contours"] = dict(
                start=levels[0], end=levels[0], size=1.0,
                showlabels=False, coloring="lines",
            )

    fig = go.Figure()
    fig.add_trace(go.Contour(**contour_kwargs))

    if field is not None:
        if field is True:
            def _slope(x, y):
                h = 1e-4
                Fx = (float(F(x + h, y)) - float(F(x - h, y))) / (2 * h)
                Fy = (float(F(x, y + h)) - float(F(x, y - h))) / (2 * h)
                return -Fx / Fy if abs(Fy) > 1e-10 else float("nan")
        elif isinstance(field, tuple) and len(field) == 2:
            M_, N_ = field
            def _slope(x, y):
                m = float(M_(x, y)); nn = float(N_(x, y))
                return -m / nn if abs(nn) > 1e-10 else float("nan")
        else:
            raise ValueError("field must be None, True, or (M, N) callables")

        density = 18
        xg = np.linspace(xrange[0], xrange[1], density)
        yg = np.linspace(yrange[0], yrange[1], density)
        Xg, Yg = np.meshgrid(xg, yg)
        S = np.zeros_like(Xg)
        for i in range(density):
            for j in range(density):
                S[i, j] = _slope(Xg[i, j], Yg[i, j])
        ax_xs, ax_ys = _field_arrows(
            Xg, Yg, S,
            xrange[1] - xrange[0], yrange[1] - yrange[0],
            density=density, aspect=aspect, scale=1.0,
        )
        fig.add_trace(go.Scatter(
            x=ax_xs, y=ax_ys, mode="lines",
            line=dict(color="#7c8aa0", width=1.0),
            opacity=0.55, hoverinfo="skip", showlegend=False,
        ))

    fig.update_layout(
        template="plotly_white",
        title=(dict(text=title, x=0.02) if title else None),
        xaxis=dict(title="x", range=list(xrange), zeroline=False),
        yaxis=dict(title="y", range=list(yrange), zeroline=False),
        paper_bgcolor="white", plot_bgcolor="white",
        height=height, showlegend=False,
        margin=dict(l=55, r=20, t=50, b=45),
    )
    return fig

