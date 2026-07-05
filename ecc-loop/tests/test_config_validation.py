"""Tests for CircuitBreakerConfig validation."""

import pytest
from ecc_loop.models import CircuitBreakerConfig


def test_default_values_valid():
    cfg = CircuitBreakerConfig()
    assert cfg.max_iterations == 5
    assert cfg.max_consecutive_failures == 3


def test_zero_max_iterations_rejected():
    with pytest.raises(ValueError, match="max_iterations"):
        CircuitBreakerConfig(max_iterations=0)


def test_zero_consecutive_failures_rejected():
    with pytest.raises(ValueError, match="max_consecutive_failures"):
        CircuitBreakerConfig(max_consecutive_failures=0)


def test_negative_values_rejected():
    with pytest.raises(ValueError):
        CircuitBreakerConfig(max_iterations=-1)
