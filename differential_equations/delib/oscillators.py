"""Helpers for forced second-order linear oscillators (Ch 7).

The canonical equation throughout is

    x'' + 2 gamma x' + omega0^2 x = F0 cos(omega t),

with three knobs: the natural frequency ``omega0``, the damping rate
``gamma``, and the drive frequency ``omega`` (plus an amplitude scale
``F0``). The exact steady-state response is the gain × cosine

    x_p(t) = A(omega) cos(omega t - phi(omega)),

with

    A(omega)   = F0 / sqrt( (omega0^2 - omega^2)^2 + (2 gamma omega)^2 )
    phi(omega) = atan2( 2 gamma omega, omega0^2 - omega^2 ).

Two visual helpers:

- :func:`oscillator_animate` — solve the IVP numerically and animate
  x(t) with Play / Pause / Reset (Ch 6 conventions). Optionally overlay
  the drive cos(omega t) so the phase relationship is visible.
- :func:`frequency_response` — paired A(omega) / phi(omega) panels, with
  the peak frequency annotated; this is the chapter's main 'map' figure.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

__all__ = ["oscillator_animate", "frequency_response",
           "steady_state_amplitude", "steady_state_phase",
           "peak_frequency"]


# --- analytic shortcuts ------------------------------------------------------

def steady_state_amplitude(omega0: float, gamma: float, F0: float,
                           omega: float | NDArray[np.float64]):
    """Return ``F0 / sqrt((omega0^2 - omega^2)^2 + (2 gamma omega)^2)``."""
    om = np.asarray(omega, dtype=float)
    return F0 / np.sqrt((omega0 ** 2 - om ** 2) ** 2 + (2 * gamma * om) ** 2)


def steady_state_phase(omega0: float, gamma: float,
                       omega: float | NDArray[np.float64]):
    """Phase lag ``phi(omega) = atan2(2 gamma omega, omega0^2 - omega^2)``
    in radians, in ``[0, pi]`` (the response always *lags* the drive)."""
    om = np.asarray(omega, dtype=float)
    return np.arctan2(2 * gamma * om, omega0 ** 2 - om ** 2)


def peak_frequency(omega0: float, gamma: float) -> float | None:
    """Frequency at which ``A(omega)`` is maximised:
    ``omega_peak = sqrt(omega0^2 - 2 gamma^2)`` when ``2 gamma^2 < omega0^2``,
    otherwise no interior peak (``A`` is monotone decreasing) and we return
    ``None``."""
    inside = omega0 ** 2 - 2 * gamma ** 2
    if inside <= 0:
        return None
    return float(np.sqrt(inside))


# --- numerical IVP solver (RK4, no scipy dependency) -------------------------

def _rk4(rhs, y0, t):
    """Hand-rolled RK4 on a 2-state system. ``rhs(t, y)`` returns a length-2
    list. ``y0`` is length-2. ``t`` is a 1-D array of evaluation times."""
    n = len(t)
    ys = np.empty((n, 2), dtype=float)
    ys[0] = y0
    for i in range(n - 1):
        h = float(t[i + 1] - t[i])
        y = ys[i]
        k1 = rhs(t[i], y)
        k2 = rhs(t[i] + 0.5 * h, [y[0] + 0.5 * h * k1[0], y[1] + 0.5 * h * k1[1]])
        k3 = rhs(t[i] + 0.5 * h, [y[0] + 0.5 * h * k2[0], y[1] + 0.5 * h * k2[1]])
        k4 = rhs(t[i] + h, [y[0] + h * k3[0], y[1] + h * k3[1]])
        ys[i + 1] = [
            y[0] + (h / 6.0) * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]),
            y[1] + (h / 6.0) * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]),
        ]
    return ys


def _solve_forced(omega0: float, gamma: float, F0: float, omega: float,
                  ic: Sequence[float], t: NDArray[np.float64]):
    def rhs(_t, y):
        x, v = y[0], y[1]
        return [v, F0 * np.cos(omega * _t) - 2 * gamma * v - omega0 ** 2 * x]
    return _rk4(rhs, list(ic), t)


# --- helper 1: animated trajectory ------------------------------------------

def oscillator_animate(
    omega0: float,
    gamma: float,
    F0: float,
    omega: float,
    *,
    ic: Sequence[float] = (0.0, 0.0),
    t_end: float = 30.0,
    n_points: int = 600,
    title: str | None = None,
    show_drive: bool = True,
    height: int = 280,
    ylim: tuple[float, float] | None = None,
    response_color: str = "#5b7db1",
    drive_color: str = "#d1495b",
):
    """Animate x(t) for the forced oscillator. Returns a Plotly figure with
    Play / Pause / Reset buttons.

    The full response curve sits faded behind; a moving marker rides along
    it. If ``show_drive`` is True (default), the unit-amplitude drive
    ``cos(omega t)`` is overlaid as a faint dashed line so phase
    relationships are visible.
    """
    import plotly.graph_objects as go

    t = np.linspace(0, t_end, n_points)
    ys = _solve_forced(omega0, gamma, F0, omega, ic, t)
    x = ys[:, 0]
    drive = np.cos(omega * t)  # unit-amplitude for visual reference

    if ylim is None:
        m = float(np.nanmax(np.abs(x))) * 1.15
        m = max(m, 1.2)
        ylim = (-m, m)

    traces = []
    # full response (faded)
    traces.append(go.Scatter(
        x=t, y=x, mode="lines",
        line=dict(color=response_color, width=2.5),
        opacity=0.30, hoverinfo="skip", showlegend=False,
    ))
    # full drive (dashed, fainter)
    if show_drive:
        traces.append(go.Scatter(
            x=t, y=drive, mode="lines",
            line=dict(color=drive_color, width=1.5, dash="dash"),
            opacity=0.55, name="drive  cos(ωt)",
        ))
    # animated marker on the response
    marker_idx_init = 0
    traces.append(go.Scatter(
        x=[float(t[marker_idx_init])], y=[float(x[marker_idx_init])],
        mode="markers",
        marker=dict(size=12, color=response_color,
                    line=dict(color="#333", width=1.4)),
        name="response x(t)",
        hoverinfo="skip",
    ))
    marker_trace_idx = len(traces) - 1

    step = max(1, n_points // 200)
    frames = [
        go.Frame(
            name=str(i),
            data=[go.Scatter(
                x=[float(t[i])], y=[float(x[i])], mode="markers",
                marker=dict(size=12, color=response_color,
                            line=dict(color="#333", width=1.4)),
            )],
            traces=[marker_trace_idx],
        )
        for i in range(0, n_points, step)
    ]

    fig = go.Figure(data=traces, frames=frames)
    fig.add_hline(y=0, line=dict(color="#9aa7b5", width=1))
    fig.update_layout(
        template="plotly_white",
        title=(dict(text=title, x=0.02, font=dict(size=13))
               if title else None),
        xaxis=dict(title="time  t", range=[0, t_end]),
        yaxis=dict(title="x(t)", range=list(ylim)),
        height=height,
        margin=dict(l=55, r=15, t=46, b=70),
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=show_drive,
        legend=(dict(x=0.62, y=0.98, bgcolor="rgba(255,255,255,0.85)",
                     font=dict(size=10)) if show_drive else None),
        updatemenus=[dict(
            type="buttons", showactive=False,
            x=0.02, y=-0.28, xanchor="left", yanchor="top",
            pad=dict(t=0, r=8),
            buttons=[
                dict(label="▶ Play", method="animate",
                     args=[None,
                           dict(frame=dict(duration=40, redraw=True),
                                fromcurrent=True,
                                transition=dict(duration=0))]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None],
                           dict(frame=dict(duration=0, redraw=False),
                                mode="immediate")]),
                dict(label="↺ Reset", method="animate",
                     args=[["0"],
                           dict(frame=dict(duration=0, redraw=True),
                                mode="immediate")]),
            ],
        )],
    )
    return fig


# --- helper 2: amplitude / phase response -----------------------------------

def transient_steady_figures(
    omega0: float = 2.0,
    gamma: float = 0.25,
    omega: float = 2.0,
    *,
    t_end: float = 28.0,
    n: int = 600,
    height: int = 240,
):
    """Two small static illustrations for the transient/steady-state split.

    Returns ``(fig_transient, fig_steady)``:

    * ``fig_transient`` shows the **natural sway** ``x_h`` — the Chapter 6
      underdamped motion ``e^{-gamma t} cos(omega_d t)`` (normalised to start
      at 1) with its decaying envelope ``+-e^{-gamma t}``. The point of the
      picture is that it *fades to zero*.
    * ``fig_steady`` shows the **push-locked response** ``x_p`` — a
      constant-amplitude sinusoid ``cos(omega t - phi)`` (normalised to unit
      amplitude) with the drive ``cos(omega t)`` overlaid dashed, so the
      reader sees it is locked to the push (and lags it) and never decays.

    Both share the same time axis so they read as two halves of one story.
    """
    import plotly.graph_objects as go

    transient_color = "#4e9a6b"   # green — the swing's own (Ch 6) motion
    response_color = "#5b7db1"    # blue — matches the response elsewhere
    drive_color = "#d1495b"       # red dashed — matches the drive elsewhere
    grey = "#9aa7b5"

    t = np.linspace(0.0, t_end, n)
    env = np.exp(-gamma * t)

    # --- transient: e^{-gamma t} cos(omega_d t), damped natural frequency ----
    omega_d = float(np.sqrt(max(omega0 ** 2 - gamma ** 2, 0.0)))
    x_h = env * np.cos(omega_d * t)

    fig_h = go.Figure()
    # decaying envelope (faint)
    fig_h.add_trace(go.Scatter(
        x=t, y=env, mode="lines",
        line=dict(color=grey, width=1, dash="dot"),
        hoverinfo="skip", showlegend=False,
    ))
    fig_h.add_trace(go.Scatter(
        x=t, y=-env, mode="lines",
        line=dict(color=grey, width=1, dash="dot"),
        hoverinfo="skip", showlegend=False,
    ))
    fig_h.add_trace(go.Scatter(
        x=t, y=x_h, mode="lines",
        line=dict(color=transient_color, width=2.5),
        name="natural sway  xₕ", hoverinfo="skip", showlegend=False,
    ))
    fig_h.add_hline(y=0, line=dict(color=grey, width=1))
    fig_h.add_annotation(
        x=t_end * 0.7, y=0.78, text="envelope  e^(−γt)  →  fades to 0",
        showarrow=False, font=dict(size=11, color="#6a6a6a"),
        xanchor="center",
    )
    fig_h.update_layout(
        template="plotly_white",
        title=dict(text="Its own natural sway  xₕ — a Chapter 6 motion that dies away",
                   x=0.02, font=dict(size=13)),
        xaxis=dict(title="time  t", range=[0, t_end]),
        yaxis=dict(title="xₕ(t)", range=[-1.15, 1.15]),
        height=height, margin=dict(l=55, r=15, t=40, b=45),
        paper_bgcolor="white", plot_bgcolor="white", showlegend=False,
    )

    # --- steady state: cos(omega t - phi), unit amplitude, never decays -----
    phi = float(steady_state_phase(omega0, gamma, omega))
    x_p = np.cos(omega * t - phi)
    drive = np.cos(omega * t)

    fig_p = go.Figure()
    fig_p.add_trace(go.Scatter(
        x=t, y=drive, mode="lines",
        line=dict(color=drive_color, width=1.5, dash="dash"),
        opacity=0.7, name="push  cos(ωt)",
    ))
    fig_p.add_trace(go.Scatter(
        x=t, y=x_p, mode="lines",
        line=dict(color=response_color, width=2.5),
        name="response  xₚ",
    ))
    fig_p.add_hline(y=0, line=dict(color=grey, width=1))
    fig_p.update_layout(
        template="plotly_white",
        title=dict(text="The response locked to your pushes  xₚ — same swing, forever",
                   x=0.02, font=dict(size=13)),
        xaxis=dict(title="time  t", range=[0, t_end]),
        yaxis=dict(title="xₚ(t)", range=[-1.35, 1.35]),
        height=height, margin=dict(l=55, r=15, t=40, b=45),
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=True,
        legend=dict(x=0.66, y=0.99, bgcolor="rgba(255,255,255,0.85)",
                    font=dict(size=10)),
    )

    return fig_h, fig_p


def frequency_response(
    omega0: float,
    gamma: float,
    *,
    F0: float = 1.0,
    omega_range: tuple[float, float] | None = None,
    n: int = 400,
    height: int = 460,
    title: str | None = None,
):
    """Two-panel frequency response of ``x'' + 2 gamma x' + omega0^2 x =
    F0 cos(omega t)``: amplitude ``A(omega)`` on top, phase lag
    ``phi(omega)`` below. The natural frequency ``omega0`` is marked with a
    grey dotted line; the peak frequency (when it exists) is annotated.
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    if omega_range is None:
        omega_range = (0.05 * omega0, 3.5 * omega0)
    om = np.linspace(omega_range[0], omega_range[1], n)
    A = steady_state_amplitude(omega0, gamma, F0, om)
    phi = steady_state_phase(omega0, gamma, om)
    om_peak = peak_frequency(omega0, gamma)
    A_peak = (float(steady_state_amplitude(omega0, gamma, F0, om_peak))
              if om_peak is not None else None)

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            "Amplitude  A(ω) = F₀ / √((ω₀² − ω²)² + (2γω)²)",
            "Phase lag  φ(ω) = atan2(2γω, ω₀² − ω²)",
        ),
    )

    # Amplitude panel
    fig.add_trace(go.Scatter(
        x=om, y=A, mode="lines",
        line=dict(color="#5b7db1", width=3),
        hoverinfo="x+y", showlegend=False,
        hovertemplate="ω = %{x:.3f}, A = %{y:.3f}<extra></extra>",
    ), row=1, col=1)
    # natural-frequency reference
    fig.add_vline(x=omega0, line=dict(color="#9aa7b5", width=1, dash="dot"),
                  row=1, col=1)
    fig.add_annotation(
        x=omega0, y=float(np.max(A)) * 1.02,
        text="ω₀", showarrow=False,
        font=dict(size=11, color="#666"),
        xanchor="left", yanchor="top",
        row=1, col=1,
    )
    if om_peak is not None and A_peak is not None:
        fig.add_trace(go.Scatter(
            x=[om_peak], y=[A_peak], mode="markers",
            marker=dict(size=12, color="#d1495b",
                        line=dict(color="#7a2a3a", width=1.5)),
            name="peak",
            hovertemplate=(f"peak at ω = {om_peak:.3f}<br>"
                           f"A = {A_peak:.3f}<extra></extra>"),
            showlegend=False,
        ), row=1, col=1)

    # Phase panel — render in units of pi for readability
    fig.add_trace(go.Scatter(
        x=om, y=phi / np.pi, mode="lines",
        line=dict(color="#e9a23b", width=3),
        hoverinfo="x+y", showlegend=False,
        hovertemplate="ω = %{x:.3f}, φ/π = %{y:.3f}<extra></extra>",
    ), row=2, col=1)
    fig.add_vline(x=omega0, line=dict(color="#9aa7b5", width=1, dash="dot"),
                  row=2, col=1)
    fig.add_hline(y=0.5, line=dict(color="#9aa7b5", width=1, dash="dot"),
                  row=2, col=1)

    fig.update_xaxes(title="drive frequency  ω", row=2, col=1,
                     range=list(omega_range))
    fig.update_xaxes(range=list(omega_range), row=1, col=1)
    fig.update_yaxes(title="A(ω)", row=1, col=1,
                     range=[0, float(np.max(A)) * 1.15])
    fig.update_yaxes(
        title="φ(ω) / π", row=2, col=1,
        range=[-0.05, 1.05],
        tickvals=[0, 0.25, 0.5, 0.75, 1.0],
        ticktext=["0", "π/4", "π/2", "3π/4", "π"],
    )
    fig.update_layout(
        template="plotly_white",
        title=(dict(text=title, x=0.02) if title else None),
        height=height,
        paper_bgcolor="white", plot_bgcolor="white",
        margin=dict(l=70, r=20, t=70, b=55),
        showlegend=False,
    )
    return fig
