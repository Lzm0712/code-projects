"""Self-evolution tests — ECC modifies ECC, then verifies itself."""

import textwrap
from pathlib import Path

from ecc_loop import engine
from ecc_loop.models import CircuitBreakerConfig, VerifyStatus

MARKER = "# ECC self-evolution marker"


def test_self_evolution_add_comment():
    """ECC adds a comment to scanner.py, verifies file changed."""
    scanner_path = Path(__file__).parent.parent / "ecc_loop" / "scanner.py"
    original = scanner_path.read_text()
    try:
        code = textwrap.dedent(f"""
        from pathlib import Path
        p = Path({str(scanner_path)!r})
        content = p.read_text()
        if {MARKER!r} in content:
            __result__ = "already present"
        else:
            p.write_text(content.rstrip() + chr(10) + chr(10) + {MARKER!r} + chr(10))
            __result__ = "added marker"
        """).strip()
        result = engine.loop(code, config=CircuitBreakerConfig(max_iterations=2))
        assert result.status == VerifyStatus.PASS
        assert MARKER in scanner_path.read_text()
    finally:
        scanner_path.write_text(original)


def test_self_evolution_already_present():
    """Already-evolved code: detects marker, skips, passes."""
    scanner_path = Path(__file__).parent.parent / "ecc_loop" / "scanner.py"
    original = scanner_path.read_text()
    try:
        scanner_path.write_text(original.rstrip() + "\n\n" + MARKER + "\n")
        code = textwrap.dedent(f"""
        from pathlib import Path
        p = Path({str(scanner_path)!r})
        if {MARKER!r} in p.read_text():
            __result__ = "already present"
        else:
            __result__ = "should not reach"
        """).strip()
        result = engine.loop(code, config=CircuitBreakerConfig(max_iterations=2))
        assert result.status == VerifyStatus.PASS
    finally:
        scanner_path.write_text(original)


def test_self_evolution_fail_breaker():
    """Task fails → breaker trips."""
    code = "__result__ = 1/0"
    config = CircuitBreakerConfig(max_iterations=2, max_consecutive_failures=2)
    result = engine.loop(code, config=config)
    assert result.status == VerifyStatus.FAIL


def test_self_evolution_modify_and_tests_pass():
    """
    ECC modifies its own code (init.py), then we verify project tests pass.
    Cleanup in finally block restores original.
    """
    import subprocess
    project_root = Path(__file__).parent.parent
    init_path = project_root / "ecc_loop" / "__init__.py"
    original = init_path.read_text()

    try:
        # Self-evolution task: modify __init__.py
        marker = "# ECC self-evolved on " + __import__("datetime").datetime.now().isoformat()
        code = textwrap.dedent(f"""
        from pathlib import Path
        p = Path({str(init_path)!r})
        p.write_text(p.read_text().rstrip() + chr(10) + {marker!r} + chr(10))
        __result__ = "evolved"
        """).strip()

        result = engine.loop(code, config=CircuitBreakerConfig(max_iterations=2))
        assert result.status == VerifyStatus.PASS
        assert marker in init_path.read_text()

        # Verify project tests still pass
        post = subprocess.run(
            ["uv", "run", "python", "-m", "pytest", "-q"],
            cwd=project_root, capture_output=True, text=True, timeout=30
        )
        assert post.returncode == 0, f"Post-evolution tests failed:\n{post.stderr}"
    finally:
        init_path.write_text(original)
        # Verify restoration
        post = subprocess.run(
            ["uv", "run", "python", "-m", "pytest", "-q"],
            cwd=project_root, capture_output=True, text=True, timeout=30
        )
        assert post.returncode == 0, "Failed to restore after self-evolution test"
