"""
ECC Loop — Five-Stage Engine (Phase 1)

DISCOVER → PLAN → EXECUTE → VERIFY → ITERATE

Following Karpathy principles:
- Think Before Coding: DISCOVER surfaces assumptions first
- Simplicity First: PLAN breaks into minimal tasks only
- Surgical Changes: EXECUTE touches only what PLAN defines
- Goal-Driven: VERIFY defined per task; FAIL loops back to DISCOVER
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

def discover(goal: str, seed_path: str = "~/.hermes/ecc-loop-seed.json") -> DiscoveryResult:
    """
    Stage 1: Understand the problem, gather context, identify goals.

    Surfaces assumptions (Think Before Coding) before planning anything.
    """
    state = seed.load_seed(seed_path)
    context: dict = {}

    # Gather context via reflection analyzer
    obs_info = reflection.analyze_observations()
    context["observations_count"] = obs_info["count"]
    context["recent_observations"] = obs_info["recent"]
    context["patterns"] = obs_info.get("patterns", [])
    context["tracked_skills"] = len(state.get("skills", {}))

    # Scan skills for relevant context
    skill_changes = scanner.detect_changes()
    context["skill_changes"] = {
        "new": skill_changes["new"],
        "modified": skill_changes["modified"],
    }

    # Build goals list — simple: single goal string split by common delimiters
    goals = _extract_goals(goal)

    # Surface assumptions (Think Before Coding)
    assumptions = [
        "Goal is achievable via skill/code execution in this environment",
        "EXECUTE can invoke handlers: shell, skill, code",
        "Observations available for context gathering",
    ]

    return DiscoveryResult(
        issue=goal,
        context=context,
        goals=goals,
        assumptions=assumptions,
    )


def _extract_goals(goal: str) -> list[str]:
    """Split a goal string into sub-goals. Minimal implementation."""
    # For now: treat as single goal. Extensible via delimiters.
    if not goal:
        return []
    # Split on newlines or " and " for simple multi-goal
    parts = goal.split("\n")
    goals = []
    for p in parts:
        p = p.strip()
        if p and not p.startswith("-"):
            goals.append(p)
    if not goals:
        goals = [goal.strip()]
    return goals


# ── Stage 2: PLAN ────────────────────────────────────────────────────

def plan(discovery: DiscoveryResult) -> Plan:
    """
    Stage 2: Break down the problem into minimal ordered tasks.

    Simplicity First: only tasks that directly solve the goal.
    """
    tasks: list[Task] = []

    for i, goal_text in enumerate(discovery.goals):
        task_name = f"task_{i+1}"
        # Minimal: one Task per goal. Handled later by execute().
        tasks.append(Task(
            name=task_name,
            description=goal_text,
            status=TaskStatus.PENDING,
        ))

    return Plan(
        tasks=tasks,
        summary=f"{len(tasks)} task(s) to achieve goal: {discovery.issue}",
    )


# ── Stage 3: EXECUTE ─────────────────────────────────────────────────

def execute(plan: Plan) -> ExecutionResult:
    """
    Stage 3: Run tasks in order. Collect output/error.

    Surgical Changes: only touches tasks defined in plan.
    """
    import ecc_loop.engine as _eng  # resolved at call time for monkeypatchability
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
    """Execute a single task using the appropriate handler.

    Raises on failure; caught by execute() → TaskStatus.FAIL.
    """
    from ecc_loop.handlers import handler_for
    h = handler_for(task)
    return h(task)


# ── Stage 4: VERIFY ─────────────────────────────────────────────────

def verify(plan: Plan, execution: ExecutionResult) -> VerifyResult:
    """
    Stage 4: Check each task's status against success criteria.

    Goal-Driven: PASS → ship. FAIL → feed into ITERATE.
    """
    passed: list[str] = []
    failed: list[str] = []

    for task, result in zip(plan.tasks, execution.results):
        if result.status == TaskStatus.PASS:
            passed.append(task.name)
        else:
            failed.append(task.name)

    if failed:
        feedback = f"Failed tasks: {', '.join(failed)}"
        return VerifyResult(
            status=VerifyStatus.FAIL,
            passed_tasks=passed,
            failed_tasks=failed,
            summary=f"{len(passed)}/{len(passed)+len(failed)} tasks passed",
            feedback=feedback,
        )

    return VerifyResult(
        status=VerifyStatus.PASS,
        passed_tasks=passed,
        failed_tasks=[],
        summary=f"All {len(passed)} task(s) passed. Ready to ship.",
        feedback="",
    )


# ── Stage 5: ITERATE ─────────────────────────────────────────────────

def iterate(
    verify_result: VerifyResult,
    state: dict,
    seed_path: str = "~/.hermes/ecc-loop-seed.json",
) -> dict:
    """
    Stage 5: On FAIL, record failure in seed and return updated state.
    On PASS, mark goal complete.

    Returns updated seed state.
    """
    if verify_result.status == VerifyStatus.FAIL:
        # Update seed: record failure, bump iteration
        state["iteration"] = state.get("iteration", 0) + 1
        seed.mark_complete(state, f"iteration_{state['iteration']}")
    else:
        # All clear: mark goal complete, reset iteration
        if state.get("current_goal"):
            seed.mark_complete(state, state["current_goal"])
        state["iteration"] = 0

    seed.save_seed(state, seed_path)
    return state


# ── Main Dispatcher ──────────────────────────────────────────────────

def check_circuit_breaker(
    state: dict,
    last_error: str,
    config: Optional[CircuitBreakerConfig] = None,
) -> CircuitBreakerState:
    """
    Check if the circuit breaker should trip.

    Called at start of each run(). Returns tripped=True with reason if
    any threshold is exceeded.
    """
    cfg = config or CircuitBreakerConfig()
    cb = CircuitBreakerState(
        consecutive_failures=state.get("consecutive_failures", 0),
        last_error=state.get("last_error", ""),
        total_attempts=state.get("total_attempts", 0),
    )

    # Check total iterations
    if cb.total_attempts > cfg.max_iterations:
        cb.tripped = True
        cb.trip_reason = f"Max iterations ({cfg.max_iterations}) exceeded"
        return cb

    # Check consecutive failures (same error in a row)
    if last_error and last_error == cb.last_error:
        cb.consecutive_failures += 1
        cb.last_error = last_error
    else:
        cb.consecutive_failures = 1 if last_error else 0
        cb.last_error = last_error

    if cb.consecutive_failures >= cfg.max_consecutive_failures:
        cb.tripped = True
        cb.trip_reason = (
            f"Same error {cb.consecutive_failures} times: {last_error[:100]}"
        )
        return cb

    return cb


def run(goal: str, config: Optional[CircuitBreakerConfig] = None) -> VerifyResult:
    """
    Full five-stage run:
        DISCOVER → PLAN → EXECUTE → VERIFY → [ITERATE]

    Returns VerifyResult. On FAIL, caller can re-run with same goal
    to trigger the iteration loop.

    Circuit breaker: trips if max_iterations or consecutive failures
    are exceeded. Pass config to customize thresholds.
    """
    cfg = config or CircuitBreakerConfig()
    seed_path = "~/.hermes/ecc-loop-seed.json"
    state = seed.load_seed(seed_path)

    # ── Circuit breaker check ──
    state["total_attempts"] = state.get("total_attempts", 0) + 1
    last_error = state.get("last_error", "")
    cb = check_circuit_breaker(state, last_error, cfg)
    # Persist circuit breaker state to seed
    state["consecutive_failures"] = cb.consecutive_failures
    state["last_error"] = cb.last_error
    if cb.tripped:
        return VerifyResult(
            status=VerifyStatus.FAIL,
            passed_tasks=[],
            failed_tasks=[],
            summary=f"CIRCUIT BREAKER TRIPPED — {cb.trip_reason}",
            feedback=cb.trip_reason,
        )

    state["current_goal"] = goal
    seed.save_seed(state, seed_path)

    # Stage 1: DISCOVER
    discovery = discover(goal, seed_path)

    # Stage 2: PLAN
    plan_result = plan(discovery)

    # Stage 3: EXECUTE
    execution = execute(plan_result)

    # Stage 4: VERIFY
    verify_result = verify(plan_result, execution)

    # Update circuit breaker state in seed
    if verify_result.status == VerifyStatus.FAIL:
        state["last_error"] = verify_result.feedback
    else:
        state["last_error"] = ""
        state["consecutive_failures"] = 0

    # Stage 5: ITERATE (update seed based on result)
    iterate(verify_result, state, seed_path)

    return verify_result
