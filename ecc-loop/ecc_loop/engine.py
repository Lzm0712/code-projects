"""
ECC Loop — Five-Stage Engine

Task-driven closed loop:
    DISCOVER → PLAN → EXECUTE → VERIFY → [PASS: done | FAIL: back to DISCOVER]

Following Karpathy principles:
- Think Before Coding: DISCOVER surfaces assumptions first
- Simplicity First: PLAN breaks into minimal tasks only
- Surgical Changes: EXECUTE touches only what PLAN defines
- Goal-Driven: VERIFY defined per task; FAIL loops back to DISCOVER

Circuit breaker prevents runaway loops (loop-engineering inspired).
"""

import json
from pathlib import Path
from typing import Optional

from ecc_loop.models import (
    DiscoveryResult, Plan, ExecutionResult, VerifyResult,
    Task, TaskStatus, VerifyStatus,
    CircuitBreakerConfig, CircuitBreakerState,
)
from ecc_loop import seed, scanner, reflection


# ── Stage 1: DISCOVER ────────────────────────────────────────────────

def discover(goal: str, seed_path: str = "~/.hermes/ecc-loop-seed.json",
             feedback: Optional[str] = None) -> DiscoveryResult:
    """
    Stage 1: Understand the problem, gather context, identify goals.

    When feedback is provided (from a failed iteration), it is injected
    as additional context for the next planning cycle.
    """
    state = seed.load_seed(seed_path)
    context: dict = {}

    obs_info = reflection.analyze_observations()
    context["observations_count"] = obs_info["count"]
    context["recent_observations"] = obs_info["recent"]
    context["patterns"] = obs_info.get("patterns", [])
    context["tracked_skills"] = len(state.get("skills", {}))

    skill_changes = scanner.detect_changes()
    context["skill_changes"] = {
        "new": skill_changes["new"],
        "modified": skill_changes["modified"],
    }

    # Inject iteration feedback
    if feedback:
        context["previous_feedback"] = feedback

    goals = _extract_goals(goal)

    return DiscoveryResult(
        issue=goal,
        context=context,
        goals=goals,
        assumptions=[
            "Goal is achievable via skill/code execution in this environment",
            "EXECUTE can invoke handlers: shell, skill, code",
            "Observations available for context gathering",
        ],
    )


def _extract_goals(goal: str) -> list[str]:
    """Split goal into sub-goals. Double-newline separates, single newline stays.

    Code blocks stay together as one task. Use blank lines to separate
    multiple independent tasks.
    """
    if not goal:
        return []
    parts = [p.strip() for p in goal.split("\n\n") if p.strip()]
    return parts or [goal.strip()]


# ── Stage 2: PLAN ────────────────────────────────────────────────────

def plan(discovery: DiscoveryResult) -> Plan:
    tasks = [
        Task(name=f"task_{i+1}", description=goal_text, status=TaskStatus.PENDING)
        for i, goal_text in enumerate(discovery.goals)
    ]
    return Plan(
        tasks=tasks,
        summary=f"{len(tasks)} task(s) to achieve goal: {discovery.issue}",
    )


# ── Stage 3: EXECUTE ─────────────────────────────────────────────────

def execute(plan: Plan) -> ExecutionResult:
    import ecc_loop.engine as _eng
    results: list[Task] = []

    for task in plan.tasks:
        task.status = TaskStatus.RUNNING
        try:
            output = _eng._execute_task(task)
            task.output = output
            task.status = TaskStatus.PASS
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAIL
        results.append(task)

    return ExecutionResult(results=results)


def _execute_task(task: Task) -> str:
    from ecc_loop.handlers import handler_for
    return handler_for(task)(task)


# ── Stage 4: VERIFY ─────────────────────────────────────────────────

def verify(plan: Plan, execution: ExecutionResult) -> VerifyResult:
    """Internal check: did tasks complete without error?"""
    passed, failed = [], []
    for task, result in zip(plan.tasks, execution.results):
        (passed if result.status == TaskStatus.PASS else failed).append(task.name)

    if failed:
        return VerifyResult(
            status=VerifyStatus.FAIL,
            passed_tasks=passed,
            failed_tasks=failed,
            summary=f"{len(passed)}/{len(passed)+len(failed)} tasks passed",
            feedback=f"Failed tasks: {', '.join(failed)}",
        )

    return VerifyResult(
        status=VerifyStatus.PASS,
        passed_tasks=passed,
        failed_tasks=[],
        summary=f"All {len(passed)} task(s) passed. Ready to ship.",
        feedback="",
    )


# ── Independent Verifier ─────────────────────────────────────────────

import subprocess as _subprocess


def run_verifier(project_root: str = "") -> VerifyResult:
    """
    Independent verification — external to EXECUTE.

    Runs the project's core test suite file-by-file. Only if ALL pass
    is the loop considered truly successful.
    """
    root = Path(project_root) if project_root else Path(__file__).parent.parent
    core_tests = [
        "tests/test_seed.py", "tests/test_models.py",
        "tests/test_scanner.py", "tests/test_engine.py",
        "tests/test_circuit_breaker.py",
    ]

    for test_file in core_tests:
        try:
            proc = _subprocess.run(
                ["python3", "-m", "pytest", "-q", test_file],
                cwd=root, capture_output=True, text=True, timeout=15,
            )
            if proc.returncode != 0:
                return VerifyResult(
                    status=VerifyStatus.FAIL,
                    passed_tasks=[],
                    failed_tasks=["verifier"],
                    summary=f"Verifier: {test_file} FAILED",
                    feedback=f"{test_file}:\n{proc.stderr[:200]}\n{proc.stdout[:200]}",
                )
        except Exception as e:
            return VerifyResult(
                status=VerifyStatus.FAIL,
                passed_tasks=[],
                failed_tasks=["verifier"],
                summary=f"Verifier: {test_file} error — {e}",
                feedback=str(e),
            )

    return VerifyResult(
        status=VerifyStatus.PASS,
        passed_tasks=["verifier"],
        failed_tasks=[],
        summary=f"Verifier: {len(core_tests)} test files passed",
    )


# ── Circuit Breaker ─────────────────────────────────────────────────


def check_circuit_breaker(
    state: dict,
    config: Optional[CircuitBreakerConfig] = None,
) -> CircuitBreakerState:
    """Check if circuit breaker should trip. Updates state dict in place."""
    cfg = config or CircuitBreakerConfig()
    cb = CircuitBreakerState(
        consecutive_failures=state.get("consecutive_failures", 0),
        last_error=state.get("last_error", ""),
        total_attempts=state.get("total_attempts", 0),
    )

    if cb.total_attempts > cfg.max_iterations:
        cb.tripped = True
        cb.trip_reason = f"Max iterations ({cfg.max_iterations}) exceeded"
        return cb

    return cb


# ── Single pass (one D→P→E→V iteration) ─────────────────────────────


def run_one(goal: str, feedback: Optional[str] = None,
            seed_path: str = "~/.hermes/ecc-loop-seed.json") -> VerifyResult:
    """Single pass: DISCOVER → PLAN → EXECUTE → VERIFY.

    Returns VerifyResult with PASS or FAIL.
    Does NOT iterate — use loop() for the full closed loop.
    """
    state = seed.load_seed(seed_path)
    state["current_goal"] = goal
    seed.save_seed(state, seed_path)

    discovery = discover(goal, seed_path, feedback=feedback)
    plan_result = plan(discovery)
    execution = execute(plan_result)
    return verify(plan_result, execution)


# ── Full closed loop (D→P→E→V, iterate on FAIL) ──────────────────────


def loop(
    goal: str,
    config: Optional[CircuitBreakerConfig] = None,
    seed_path: str = "~/.hermes/ecc-loop-seed.json",
    run_verifier_on_pass: bool = True,
) -> VerifyResult:
    """
    Task-driven closed loop:
        DISCOVER → PLAN → EXECUTE → VERIFY
                     ↑                    │
                     └───── FAIL ─────────┘

    On FAIL: re-enters DISCOVER with feedback, replans, re-executes.
    Circuit breaker prevents runaway loops.

    Returns the FINAL VerifyResult (PASS, or FAIL with trip reason).
    """
    cfg = config or CircuitBreakerConfig()
    state = seed.load_seed(seed_path)

    # Reset iteration counter for new goal
    if state.get("current_goal") != goal:
        state["iteration"] = 0
        state["consecutive_failures"] = 0
        state["total_attempts"] = 0
        state["last_error"] = ""

    feedback: Optional[str] = None

    while True:
        # ── Circuit breaker before each iteration ──
        state["total_attempts"] = state.get("total_attempts", 0) + 1
        state["iteration"] = state.get("iteration", 0) + 1

        cb = check_circuit_breaker(state, cfg)
        if cb.tripped:
            seed.save_seed(state, seed_path)
            return VerifyResult(
                status=VerifyStatus.FAIL,
                passed_tasks=[],
                failed_tasks=[],
                summary=f"CIRCUIT BREAKER TRIPPED — {cb.trip_reason}",
                feedback=cb.trip_reason,
            )

        seed.save_seed(state, seed_path)

        # ── Run a single iteration ──
        result = run_one(goal, feedback=feedback, seed_path=seed_path)

        if result.status == VerifyStatus.PASS:
            # ── Independent verifier (referee, not player) ──
            if run_verifier_on_pass:
                v_result = run_verifier()
                if v_result.status != VerifyStatus.PASS:
                    result = v_result  # Verifier failed — iterate
                else:
                    state["last_error"] = ""
                    state["consecutive_failures"] = 0
                    seed.mark_complete(state, goal)
                    seed.save_seed(state, seed_path)
                    return result
            else:
                state["last_error"] = ""
                state["consecutive_failures"] = 0
                seed.mark_complete(state, goal)
                seed.save_seed(state, seed_path)
                return result

        # FAIL: update error tracking, prepare feedback for re-entry
        error = result.feedback
        prev_error = state.get("last_error", "")
        if error == prev_error:
            state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1
        else:
            state["consecutive_failures"] = 1
        state["last_error"] = error
        seed.save_seed(state, seed_path)

        # Feed failure back into next DISCOVER
        feedback = f"[Iteration {state['iteration']}] {error}"


# ── Legacy wrapper ──────────────────────────────────────────────────

def run(goal: str, config: Optional[CircuitBreakerConfig] = None,
        seed_path: str = "~/.hermes/ecc-loop-seed.json") -> VerifyResult:
    """Convenience: single-pass for backward compatibility."""
    return loop(goal, config=config, seed_path=seed_path)
