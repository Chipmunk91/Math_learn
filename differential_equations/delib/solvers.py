"""Thin, well-typed wrappers around :func:`scipy.integrate.solve_ivp`.

These keep chapter notebooks free of solver boilerplate and give every
chapter the same calling convention for integrating ODEs and systems.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp

__all__ = ["solve_ode", "solve_system"]

# f(t, y) -> dy/dt. ``y`` is a scalar for a single ODE or a vector for a system.
RHS = Callable[[float, NDArray[np.float64]], ArrayLike]


def solve_ode(
    f: RHS,
    t_span: tuple[float, float],
    y0: float | Sequence[float],
    *,
    t_eval: ArrayLike | None = None,
    method: str = "RK45",
    **kwargs: Any,
):
    """Integrate ``y' = f(t, y)`` over ``t_span`` from initial state ``y0``.

    Works for a scalar first-order ODE (pass a scalar ``y0``) or a vector
    system (pass a sequence). When ``t_eval`` is omitted a dense, evenly
    spaced grid of 200 points across ``t_span`` is used so solution curves
    are smooth enough to plot directly.

    Returns the SciPy ``OdeResult`` (``.t`` is shape ``(n,)``, ``.y`` is shape
    ``(dim, n)``).
    """
    y0_arr = np.atleast_1d(np.asarray(y0, dtype=float))
    if t_eval is None:
        t_eval = np.linspace(t_span[0], t_span[1], 200)

    sol = solve_ivp(
        f,
        t_span,
        y0_arr,
        method=method,
        t_eval=t_eval,
        dense_output=True,
        **kwargs,
    )
    return sol


def solve_system(
    f: RHS,
    t_span: tuple[float, float],
    y0: Sequence[float],
    **kwargs: Any,
):
    """Integrate a first-order *system* ``y' = f(t, y)`` for vector ``y``.

    A semantic alias of :func:`solve_ode` for readability in chapters that
    deal with multi-dimensional state (phase portraits, oscillators, etc.).
    """
    return solve_ode(f, t_span, y0, **kwargs)
