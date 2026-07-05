"""Tests for goal() — /goal pattern."""

import tempfile
from pathlib import Path

from ecc_loop import engine
from ecc_loop.models import CircuitBreakerConfig, VerifyStatus


def test_goal_met_first_try():
    """Task creates a file, condition checks it exists → PASS."""
    with tempfile.TemporaryDirectory() as tmp:
        marker = Path(tmp) / "done.txt"
        task = f"""from pathlib import Path
Path({str(marker)!r}).write_text('done')
__result__ = 'ok'"""
        condition = f"test -f {marker}"
        result = engine.goal(task, condition,
            config=CircuitBreakerConfig(max_iterations=3))
        assert result.status == VerifyStatus.PASS
        assert "1 iteration" in result.summary


def test_goal_never_met():
    """Task succeeds but condition never passes → breaker trips."""
    task = "__result__ = 'never done'"
    condition = "exit 1"
    config = CircuitBreakerConfig(max_iterations=2, max_consecutive_failures=2)
    result = engine.goal(task, condition, config=config)
    assert result.status == VerifyStatus.FAIL
    assert "CIRCUIT BREAKER" in result.summary


def test_goal_met_after_retry():
    """First attempt: condition fails. Second: task fixes it → PASS."""
    with tempfile.TemporaryDirectory() as tmp:
        marker = Path(tmp) / "retry.txt"
        task = f"""from pathlib import Path
Path({str(marker)!r}).write_text('done')
__result__ = 'ok'"""
        condition = f"test -f {marker}"

        result = engine.goal(task, condition,
            config=CircuitBreakerConfig(max_iterations=5))
        assert result.status == VerifyStatus.PASS
        assert "Goal met" in result.summary
