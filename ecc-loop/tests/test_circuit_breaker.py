"""Tests for circuit breaker in ecc_loop.engine"""

import pytest
from ecc_loop.engine import check_circuit_breaker
from ecc_loop.models import CircuitBreakerConfig


def test_cb_no_trip_fresh_state():
    state = {"consecutive_failures": 0, "last_error": "", "total_attempts": 0}
    cb = check_circuit_breaker(state, "", CircuitBreakerConfig())
    assert not cb.tripped


def test_cb_trip_max_iterations():
    state = {"consecutive_failures": 0, "last_error": "", "total_attempts": 6}
    cb = check_circuit_breaker(state, "", CircuitBreakerConfig(max_iterations=5))
    assert cb.tripped
    assert "Max iterations" in cb.trip_reason


def test_cb_trip_consecutive_failures():
    state = {"consecutive_failures": 2, "last_error": "boom", "total_attempts": 2}
    cb = check_circuit_breaker(state, "boom", CircuitBreakerConfig(max_consecutive_failures=3))
    assert cb.tripped
    assert "Same error 3 times" in cb.trip_reason
    assert "boom" in cb.trip_reason


def test_cb_reset_on_different_error():
    """Different error resets consecutive counter."""
    state = {"consecutive_failures": 2, "last_error": "error A", "total_attempts": 2}
    cb = check_circuit_breaker(state, "error B", CircuitBreakerConfig(max_consecutive_failures=3))
    assert not cb.tripped
    assert cb.consecutive_failures == 1  # reset to 1


def test_cb_max_iterations_not_exceeded():
    state = {"consecutive_failures": 0, "last_error": "", "total_attempts": 3}
    cb = check_circuit_breaker(state, "", CircuitBreakerConfig(max_iterations=5))
    assert not cb.tripped


def test_cb_trip_with_custom_config():
    """Custom config: trip after 2 consecutive failures."""
    config = CircuitBreakerConfig(max_consecutive_failures=2, max_iterations=10)
    state = {"consecutive_failures": 1, "last_error": "oops", "total_attempts": 1}
    cb = check_circuit_breaker(state, "oops", config)
    assert cb.tripped
