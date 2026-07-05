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


def cmd_run(goal: str) -> int:
    """Execute the full five-stage loop."""
    result = engine.run(goal)
    if result.status == VerifyStatus.PASS:
        print(f"✅ PASS — {result.summary}")
        print(f"   Tasks: {result.passed_tasks}")
        return 0
    else:
        print(f"❌ FAIL — {result.summary}")
        print(f"   Failed: {result.failed_tasks}")
        print(f"   Feedback: {result.feedback}")
        print()
        print("   Rerun with same goal to iterate.")
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
        return 1

    cmd = sys.argv[1]

    if cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: ecc run <goal>")
            return 1
        return cmd_run(" ".join(sys.argv[2:]))

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
