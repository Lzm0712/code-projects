"""Real integration tests — no monkeypatching, full D→P→E→V→I flow."""

import json
import textwrap
import tempfile
from pathlib import Path

from ecc_loop import engine
from ecc_loop.models import CircuitBreakerConfig, VerifyStatus


def test_real_flow_pass():
    """
    Full flow: execute Python code that creates a file, then verify it exists.
    Uses CodeHandler (default), no monkeypatch.
    """
    with tempfile.TemporaryDirectory() as tmp:
        test_path = Path(tmp) / "test_output.txt"
        code = textwrap.dedent(f"""
        from pathlib import Path
        p = Path({str(test_path)!r})
        p.write_text("ecc loop works")
        __result__ = "ok"
        """).strip()

        result = engine.loop(code, config=CircuitBreakerConfig(max_iterations=2))
        assert result.status == VerifyStatus.PASS, f"Expected PASS, got: {result.summary}"
        assert test_path.exists()
        assert test_path.read_text() == "ecc loop works"


def test_real_flow_fail():
    """
    Full flow: Python code that raises → VERIFY says FAIL → circuit breaker trips.
    """
    code = "__result__ = 1/0"
    config = CircuitBreakerConfig(max_iterations=2, max_consecutive_failures=2)
    result = engine.loop(code, config=config)
    assert result.status == VerifyStatus.FAIL
    assert "CIRCUIT BREAKER" in result.summary


def test_real_loop_succeeds_after_retry():
    """
    First attempt fails, retry succeeds.
    Uses marker file to track state across iterations.
    """
    with tempfile.TemporaryDirectory() as tmp:
        retry_marker = Path(tmp) / ".retry_count"

        code = textwrap.dedent(f"""
        from pathlib import Path
        marker = Path({str(retry_marker)!r})
        count = 0
        if marker.exists():
            count = int(marker.read_text())
        if count == 0:
            marker.write_text("1")
            raise RuntimeError("first attempt fails on purpose")
        marker.write_text(str(count + 1))
        __result__ = f"retry succeeded on attempt {{count}}"
        """).strip()

        result = engine.loop(code, config=CircuitBreakerConfig(max_iterations=5))
        assert result.status == VerifyStatus.PASS, f"Expected PASS, got: {result.summary}"
        assert retry_marker.exists()


def test_file_handler():
    """FileHandler via JSON spec."""
    from ecc_loop import handlers
    from ecc_loop.models import Task

    with tempfile.TemporaryDirectory() as tmp:
        spec = json.dumps({"path": f"{tmp}/hello.txt", "content": "world"})
        task = Task(name="task_file_write", description=spec)
        h = handlers.handler_for(task)
        result = h(task)
        assert "wrote" in result
        assert Path(f"{tmp}/hello.txt").read_text() == "world"
