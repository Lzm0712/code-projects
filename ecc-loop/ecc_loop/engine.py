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
)
from ecc_loop import seed, scanner


# ── Stage 1: DISCOVER ────────────────────────────────────────────────

def discover(goal: str, seed_path: str = "~/.hermes/ecc-loop-seed.json") -> DiscoveryResult:
    """
    Stage 1: Understand the problem, gather context, identify goals.

    Surfaces assumptions (Think Before Coding) before planning anything.
    """
    state = seed.load_seed(seed_path)
    context: dict = {}

    # Gather context from observations
    obs_path = Path.home() / ".hermes" / "observations.jsonl"
    recent_obs: list[dict] = []
    if obs_path.exists():
        try:
            with open(obs_path) as f:
                lines = [l.strip() for l in f if l.strip()]
                # Last 10 observations
                for line in lines[-10:]:
                    recent_obs.append(json.loads(line))
        except (json.JSONDecodeError, OSError):
            pass
    context["recent_observations"] = len(recent_obs)
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
        f"Goal is achievable via skill/code execution in this environment",
        f"EXECUTE can invoke handlers: skill, shell, code",
        f"Observations available at {obs_path}",
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
    """
    Execute a single task. Phase 2: replace with real handlers.
    Currently a stub that returns task description.
    """
    return f"[stub] executed: {task.description}"


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

def run(goal: str) -> VerifyResult:
    """
    Full five-stage run:
        DISCOVER → PLAN → EXECUTE → VERIFY → [ITERATE]

    Returns VerifyResult. On FAIL, caller can re-run with same goal
    to trigger the iteration loop.
    """
    seed_path = "~/.hermes/ecc-loop-seed.json"
    state = seed.load_seed(seed_path)
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

    # Stage 5: ITERATE (update seed based on result)
    iterate(verify_result, state, seed_path)

    return verify_result
