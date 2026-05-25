"""Unit tests for delib's computational core (no rendering / no UI)."""

import numpy as np

from delib.solvers import solve_ode
from delib.fields import slope_field_data


def test_solve_ode_exponential_decay():
    """y' = -y, y(0) = 1 should track e^{-t}."""
    sol = solve_ode(lambda t, y: -y, (0.0, 5.0), 1.0)
    assert sol.success
    assert sol.y.shape[0] == 1
    expected = np.exp(-sol.t)
    np.testing.assert_allclose(sol.y[0], expected, atol=1e-3)


def test_solve_ode_respects_t_eval():
    t_eval = np.linspace(0, 1, 11)
    sol = solve_ode(lambda t, y: y, (0.0, 1.0), 1.0, t_eval=t_eval)
    np.testing.assert_allclose(sol.t, t_eval)
    np.testing.assert_allclose(sol.y[0], np.exp(t_eval), rtol=1e-3)


def test_slope_field_data_shapes_and_normalization():
    f = lambda x, y: y  # slope grows with y
    X, Y, U, V = slope_field_data(f, (-2, 2), (-2, 2), density=15)
    for arr in (X, Y, U, V):
        assert arr.shape == (15, 15)
    # every arrow is a unit vector
    norms = np.hypot(U, V)
    np.testing.assert_allclose(norms, 1.0, atol=1e-12)


def test_slope_field_data_direction():
    """For y' = 1 every arrow points up-and-right at 45 degrees."""
    X, Y, U, V = slope_field_data(lambda x, y: np.ones_like(x), (0, 1), (0, 1), density=5)
    np.testing.assert_allclose(U, V)  # equal components => 45 degrees
    assert np.all(U > 0)
