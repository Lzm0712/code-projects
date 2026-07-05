"""Tests for circuit breaker in ecc_loop.engine"""

from ecc_loop.engine import check_circuit_breaker
from ecc_loop.models import CircuitBreakerConfig


def test_cb_no_trip_fresh_state():
    state = {"consecutive_failures": 0, "last_error": "", "total_attempts": 0}
    cb = check_circuit_breaker(state, CircuitBreakerConfig())
    assert not cb.tripped


def test_cb_trip_max_iterations():
    state = {"consecutive_failures": 0, "last_error": "", "total_attempts": 6}
    cb = check_circuit_breaker(state, CircuitBreakerConfig(max_iterations=5))
    assert cb.tripped
    assert "Max iterations" in cb.trip_reason


def test_cb_max_iterations_not_exceeded():
    state = {"consecutive_failures": 0, "last_error": "", "total_attempts": 3}
    cb = check_circuit_breaker(state, CircuitBreakerConfig(max_iterations=5))
    assert not cb.tripped
