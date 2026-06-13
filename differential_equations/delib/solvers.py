"""Pure-NumPy ODE integration — no SciPy.

These wrappers give every chapter one calling convention for integrating an
ODE or a first-order system, and return an object with the same ``.t`` /
``.y`` shape SciPy's ``OdeResult`` exposes (``.t`` is ``(n,)``, ``.y`` is
``(dim, n)``), so chapter code is unchanged.

We integrate with a fixed-step classical RK4 on a fine internal grid and
interpolate to the requested sample points. For the smooth ODEs these
chapters plot, that is visually identical to an adaptive solver — and it
drops the heavy SciPy wheel from the WebAssembly build, which was adding
~16 MB and a long cold-start to every page.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from types import SimpleNamespace
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

__all__ = ["solve_ode", "solve_system"]

# f(t, y) -> dy/dt. ``y`` is a length-1 array for a single ODE or a vector for
# a system; the return is array-like of the same length.
RHS = Callable[[float, "NDArray[np.float64]"], ArrayLike]


def _rk4_dense(f, t0, t1, y0, n_internal):
    """Classical RK4 over ``[t0, t1]`` with ``n_internal`` uniform steps.
    Returns ``(ts, ys)`` with ``ts`` shape ``(n_internal+1,)`` and ``ys``
    shape ``(n_internal+1, dim)``."""
    h = (t1 - t0) / n_internal
    dim = y0.size
    ts = np.empty(n_internal + 1, dtype=float)
    ys = np.empty((n_internal + 1, dim), dtype=float)
    ts[0] = t0
    ys[0] = y0
    y = y0.astype(float).copy()
    for i in range(n_internal):
        t = t0 + i * h
        k1 = np.asarray(f(t, y), dtype=float)
        k2 = np.asarray(f(t + 0.5 * h, y + 0.5 * h * k1), dtype=float)
        k3 = np.asarray(f(t + 0.5 * h, y + 0.5 * h * k2), dtype=float)
        k4 = np.asarray(f(t + h, y + h * k3), dtype=float)
        y = y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        ts[i + 1] = t0 + (i + 1) * h
        ys[i + 1] = y
    return ts, ys


def solve_ode(
    f: RHS,
    t_span: tuple[float, float],
    y0: float | Sequence[float],
    *,
    t_eval: ArrayLike | None = None,
    method: str = "RK45",   # accepted for call-compatibility; always RK4 here
    **kwargs: Any,
):
    """Integrate ``y' = f(t, y)`` over ``t_span`` from initial state ``y0``.

    Scalar ODE (scalar ``y0``) or vector system (sequence ``y0``). When
    ``t_eval`` is omitted, a dense 200-point grid across ``t_span`` is used so
    curves plot smoothly. Returns an object with ``.t`` (shape ``(n,)``) and
    ``.y`` (shape ``(dim, n)``); a scalar ODE still gives ``.y`` shape
    ``(1, n)``, so ``sol.y[0]`` works everywhere.
    """
    y0_arr = np.atleast_1d(np.asarray(y0, dtype=float))
    if t_eval is None:
        t_eval = np.linspace(t_span[0], t_span[1], 200)
    t_eval = np.asarray(t_eval, dtype=float)

    # Fine internal RK4 grid, then linear-interpolate to the requested points.
    # 8x oversampling (min 400 steps) keeps interpolation error invisible for
    # the gentle equations these chapters plot.
    n_internal = max(400, 8 * int(t_eval.size))
    ts, ys = _rk4_dense(f, float(t_span[0]), float(t_span[1]), y0_arr, n_internal)

    dim = y0_arr.size
    y_out = np.empty((dim, t_eval.size), dtype=float)
    for d in range(dim):
        y_out[d] = np.interp(t_eval, ts, ys[:, d])

    return SimpleNamespace(t=t_eval, y=y_out, success=True)


def solve_system(
    f: RHS,
    t_span: tuple[float, float],
    y0: Sequence[float],
    **kwargs: Any,
):
    """Integrate a first-order *system* ``y' = f(t, y)`` for vector ``y``.

    A semantic alias of :func:`solve_ode` for chapters dealing with
    multi-dimensional state (phase portraits, oscillators).
    """
    return solve_ode(f, t_span, y0, **kwargs)
