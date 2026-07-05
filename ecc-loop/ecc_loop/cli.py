#!/usr/bin/env python3
"""
ECC Loop — CLI Entry Point

Usage:
    ecc run <goal>      Run a single D→P→E→V pass
    ecc loop <goal>     Run full closed loop (iterate on FAIL)
    ecc scan            Scan skills for changes
    ecc seed            Show current seed state
    ecc status          Show live iteration status
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path.home() / "projects" / "ecc-loop"))

from ecc_loop import engine, seed, scanner
from ecc_loop.models import VerifyStatus, CircuitBreakerConfig


def cmd_run(goal: str) -> int:
    """Single pass: DISCOVER → PLAN → EXECUTE → VERIFY."""
    result = engine.run_one(goal)
    return _print_result(result, attempt=1, total=1)


def cmd_loop(goal: str) -> int:
    """Full closed loop: iterate on FAIL until PASS or circuit breaker."""
    config = CircuitBreakerConfig(max_iterations=5, max_consecutive_failures=3)
    result = engine.loop(goal, config=config)
    return _print_result(result, attempt=1, total=1)


def _print_result(result, attempt: int = 1, total: int = 1) -> int:
    if result.status == VerifyStatus.PASS:
        print(f"✅ PASS — {result.summary}")
        print(f"   Tasks: {result.passed_tasks}")
        return 0

    if "CIRCUIT BREAKER" in result.summary:
        print(f"⚠️  CIRCUIT BREAKER TRIPPED — {result.feedback}")
        return 1

    print(f"❌ FAIL — {result.summary}")
    print(f"   {result.feedback}")
    return 1


def cmd_scan() -> int:
    print(scanner.report_changes())
    return 0


def cmd_seed() -> int:
    state = seed.load_seed("~/.hermes/ecc-loop-seed.json")
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return 0


def cmd_status() -> int:
    state = seed.load_seed("~/.hermes/ecc-loop-seed.json")
    stage = state.get("stage", "idle")
    iteration = state.get("iteration", 0)
    goal = state.get("current_goal", "—")
    completed = len(state.get("execution_state", {}).get("completed_tasks", []))
    cb = f"{state.get('consecutive_failures', 0)} consecutive fails"

    print(f"ECC Loop Status")
    print(f"  Goal:         {goal}")
    print(f"  Iterations:   {iteration}")
    print(f"  Circuit:      {cb}")
    print(f"  Tasks:        {completed} completed")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: ecc <run|loop|scan|seed|status> [goal]")
        print("  ecc run  <goal>   Single pass (D→P→E→V)")
        print("  ecc loop <goal>   Full closed loop (iterate on FAIL)")
        return 1

    cmd = sys.argv[1]

    if cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: ecc run <goal>")
            return 1
        return cmd_run(" ".join(sys.argv[2:]))

    if cmd == "loop":
        if len(sys.argv) < 3:
            print("Usage: ecc loop <goal>")
            return 1
        return cmd_loop(" ".join(sys.argv[2:]))

    if cmd == "scan":
        return cmd_scan()

    if cmd == "seed":
        return cmd_seed()

    if cmd == "status":
        return cmd_status()

    print(f"Unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
