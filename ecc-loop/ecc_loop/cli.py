#!/usr/bin/env python3
"""
ECC Loop — CLI Entry Point

Usage:
    ecc run <goal>            Run the full five-stage loop
    ecc scan                  Scan skills for changes
    ecc seed                  Show current seed state
    ecc status                Show live iteration status
"""

import sys
import json
from pathlib import Path

# Ensure project is importable
sys.path.insert(0, str(Path.home() / "projects" / "ecc-loop"))

from ecc_loop import engine, seed, scanner
from ecc_loop.models import VerifyStatus


def cmd_run(goal: str, max_attempts: int = 1) -> int:
    """Execute the full five-stage loop.

    With --loop, retry up to max_attempts with circuit breaker.
    """
    from ecc_loop.models import CircuitBreakerConfig

    config = CircuitBreakerConfig(
        max_iterations=max_attempts,
        max_consecutive_failures=min(max_attempts, 3),
    )

    for attempt in range(1, max_attempts + 1):
        result = engine.run(goal, config=config)

        if result.status == VerifyStatus.PASS:
            print(f"✅ PASS — {result.summary}")
            print(f"   Tasks: {result.passed_tasks}")
            print(f"   Attempt: {attempt}/{max_attempts}")
            return 0

        print(f"[Attempt {attempt}/{max_attempts}] ❌ FAIL — {result.summary}")
        print(f"   {result.feedback}")

        if "CIRCUIT BREAKER" in result.summary:
            print(f"   ⚡ Circuit breaker tripped.")
            return 1

        if attempt < max_attempts:
            print(f"   Retrying...")
            print()

    return 1


def cmd_scan() -> int:
    """Scan skills for changes."""
    report = scanner.report_changes()
    print(report)
    return 0


def cmd_seed() -> int:
    """Show current seed state."""
    state = seed.load_seed("~/.hermes/ecc-loop-seed.json")
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return 0


def cmd_status() -> int:
    """Show live iteration status."""
    state = seed.load_seed("~/.hermes/ecc-loop-seed.json")
    stage = state.get("stage", "idle")
    iteration = state.get("iteration", 0)
    goal = state.get("current_goal", "—")
    completed = len(state.get("execution_state", {}).get("completed_tasks", []))
    active = len(state.get("execution_state", {}).get("active_tasks", []))
    blocked = len(state.get("execution_state", {}).get("blocked_tasks", []))

    print(f"ECC Loop Status")
    print(f"  Stage:     {stage}")
    print(f"  Goal:      {goal}")
    print(f"  Iteration: {iteration}")
    print(f"  Tasks:     {completed} completed / {active} active / {blocked} blocked")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: ecc <run|scan|seed|status> [arguments]")
        print("  ecc run [--loop N] <goal>    Run loop (--loop=5 auto-retries with circuit breaker)")
        return 1

    cmd = sys.argv[1]

    if cmd == "run":
        max_attempts = 1
        args = sys.argv[2:]
        if args and args[0] == "--loop":
            if len(args) > 1 and args[1].isdigit():
                max_attempts = int(args[1])
                args = args[2:]
            else:
                max_attempts = 3  # default loop attempts
                args = args[1:] if len(args) > 1 else []
        if not args:
            print("Usage: ecc run [--loop N] <goal>")
            return 1
        return cmd_run(" ".join(args), max_attempts=max_attempts)

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
