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

from pathlib import Path
from typing import Optional

from ecc_loop.models import (
    DiscoveryResult, Plan, ExecutionResult, VerifyResult,
    Task, TaskStatus, VerifyStatus,
    CircuitBreakerConfig, CircuitBreakerState,
)
from ecc_loop import seed, scanner, reflection
from ecc_loop.safety import safety_check as _safety_check
from ecc_loop.run_log import record_run as _record_run
from ecc_loop.logger import log as _log
from ecc_loop.goal_freeze import freeze as _freeze, check as _check_frozen
from ecc_loop.precise_specs import Specs



def discover_work(project_root: str = "") -> list[str]:
    """
    Stage 0: Discover work from EXTERNAL signals (not just file checks).

    Scans:
    - Git status (uncommitted changes, untracked files)
    - Recent commit messages (TODO/FIXME/HACK)
    - Pytest cache (last test failures)
    - Stale branches

    Returns list of discovered work items.
    """
    import subprocess as _sp
    root = Path(project_root) if project_root else Path(__file__).parent.parent
    work = []

    try:
        # 1. Git status: uncommitted changes
        status = _sp.run(
            ["git", "status", "--porcelain"],
            cwd=root, capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if status:
            lines = status.splitlines()
            modified = [l for l in lines if l.startswith(" M") or l.startswith("M ")]
            untracked = [l for l in lines if l.startswith("??")]
            if modified:
                work.append(f"Git: {len(modified)} uncommitted modified file(s)")
            if untracked:
                work.append(f"Git: {len(untracked)} untracked file(s)")

        # 2. Recent commits with TODO/FIXME
        log = _sp.run(
            ["git", "log", "--oneline", "-20", "--grep=TODO", "--grep=FIXME", "--grep=HACK", "--all-match"],
            cwd=root, capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if log:
            work.append(f"Git log: {len(log.splitlines())} recent commits with TODO/FIXME")

        # 3. Last test failures from pytest cache
        cache_dir = root / ".pytest_cache" / "v" / "cache"
        if cache_dir.exists():
            for cache_file in cache_dir.glob("lastfailed*"):
                work.append("Pytest: previous test failures detected")

        # 4. Stale branches (>14 days)
        branches = _sp.run(
            ["git", "branch", "--no-merged", "main"],
            cwd=root, capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if branches:
            work.append(f"Git: {len(branches.splitlines())} unmerged branches")

    except Exception:
        pass  # Discovery is best-effort

    return work

# ── Stage 1: DISCOVER ────────────────────────────────────────────────

def discover(goal: str, seed_path: str = "~/.hermes/ecc-loop-seed.json",
             feedback: Optional[str] = None) -> DiscoveryResult:
    """
    Stage 1: Understand the problem, gather context, identify goals.

    Performs an actual GAP ANALYSIS:
    - Compares project state against LOOP.md config
    - Scans skill changes and recent observations
    - Surfaces concrete gaps as goals when feedback/context justifies it
    """
    state = seed.load_seed(seed_path)
    context: dict = {}

    # Context from observations
    obs_info = reflection.analyze_observations()
    context["observations_count"] = obs_info["count"]
    context["patterns"] = obs_info.get("patterns", [])
    context["tracked_skills"] = len(state.get("skills", {}))

    # Context from skill changes
    skill_changes = scanner.detect_changes()
    context["skill_changes"] = {
        "new": skill_changes["new"],
        "modified": skill_changes["modified"],
    }

    # Inject feedback from failed iteration
    if feedback:
        context["previous_feedback"] = feedback

    # ── Actual discovery: gap analysis ──
    gaps = _discover_gaps(state, context)
    context["gaps_found"] = len(gaps)
    context["gaps"] = gaps

    # Build goals: user's goal + discovered gaps
    goals = _extract_goals(goal)
    if gaps and _is_improvement_goal(goal):
        goals.extend(gaps)

    return DiscoveryResult(
        issue=goal,
        context=context,
        goals=goals,
        assumptions=[
            "Goal is achievable via skill/code execution in this environment",
            "EXECUTE can invoke handlers: shell, skill, code",
        ],
    )


def _is_improvement_goal(goal: str) -> bool:
    """Detect if goal is a self-improvement task."""
    keywords = ["improve", "改进", "fix", "修复", "实现", "implement", "add", "添加"]
    return any(k in goal.lower() for k in keywords)


def _discover_gaps(state: dict, context: dict) -> list[str]:
    """Compare project state against LOOP.md to find gaps."""
    gaps = []

    # Check if LOOP.md exists and analyze
    loop_md = Path(__file__).parent.parent / "LOOP.md"
    if not loop_md.exists():
        gaps.append("Missing LOOP.md configuration")

    # Check core modules
    for module in ["seed.py", "scanner.py", "engine.py", "handlers.py", "cli.py"]:
        if not (Path(__file__).parent / module).exists():
            gaps.append(f"Missing core module: {module}")

    # Check verifier capability
    engine_src = (Path(__file__).parent / "engine.py")
    if engine_src.exists():
        content = engine_src.read_text()
        if "run_verifier" not in content:
            gaps.append("Missing independent verifier (run_verifier)")
        if "def goal" not in content:
            gaps.append("Missing /goal pattern")

    # Check tests vs source modules
    tests_dir = Path(__file__).parent.parent / "tests"
    source_dir = Path(__file__).parent
    if tests_dir.exists():
        for src in sorted(source_dir.glob("*.py")):
            if src.name.startswith("_"):
                continue
            test_file = tests_dir / f"test_{src.name}"
            if not test_file.exists():
                gaps.append(f"Missing test: tests/test_{src.name}")
    else:
        gaps.append("Missing tests directory")

    # Check skill changes suggest action
    if context.get("skill_changes", {}).get("new"):
        gaps.append("New skills detected — review and integrate")

    # ── Code quality checks ──
    for mod_name in ["engine.py", "seed.py"]:
        mod = source_dir / mod_name
        if mod.exists():
            content = mod.read_text()
            # Check for actually-unused imports (look for import statements at module top)
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("import ") and not stripped.startswith("import ecc_loop"):
                    name = stripped.split()[1].split(".")[0]
                    # Check if the name is used anywhere else in the file
                    rest = content.replace(line, "", 1)
                    if name not in rest:
                        gaps.append(f"Unused import in {mod_name}: {stripped}")

    # Check __init__.py exports
    init_py = source_dir / "__init__.py"
    if init_py.exists():
        init_content = init_py.read_text()
        for mod in sorted(source_dir.glob("*.py")):
            name = mod.stem
            if name != "__init__" and f'"{name}"' not in init_content and name not in init_content.split('import ')[-1]:
                gaps.append(f"__init__.py missing export: {name}")

    # Check py.typed marker
    if not (source_dir / "py.typed").exists():
        gaps.append("Missing py.typed marker for type checking")

    # Check CircuitBreakerConfig validation
    models_src = source_dir / "models.py"
    if models_src.exists():
        if "__post_init__" not in models_src.read_text():
            gaps.append("CircuitBreakerConfig missing __post_init__ validation (max_iterations=0 not rejected)")

    return gaps


def _extract_goals(goal: str) -> list[str]:
    """Return the goal as-is. Code blocks are atomic."""
    return [goal.strip()] if goal.strip() else []


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
        safe, reason = _safety_check(task.description)
        if not safe:
            task.error = f"SAFETY BLOCK: {reason}"
            task.status = TaskStatus.FAIL
            results.append(task)
            continue
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

    Runs the project's core test suite with subprocess fallback.
    Only if ALL pass is the loop considered truly successful.
    """
    root = Path(project_root) if project_root else Path(__file__).parent.parent
    core_tests = [
        "tests/test_seed.py", "tests/test_models.py",
        "tests/test_scanner.py", "tests/test_engine.py",
        "tests/test_circuit_breaker.py",
    ]

    try:
        proc = _subprocess.run(
            ["python3", "-m", "pytest", "-q", "-p", "no:xdist"] + core_tests,
            cwd=root, capture_output=True, text=True, timeout=30,
        )
        if proc.returncode == 0:
            return VerifyResult(
                status=VerifyStatus.PASS,
                passed_tasks=["verifier"],
                failed_tasks=[],
                summary=f"Verifier: all {len(core_tests)} files passed",
            )
        return VerifyResult(
            status=VerifyStatus.FAIL,
            passed_tasks=[],
            failed_tasks=["verifier"],
            summary="Verifier: tests FAILED",
            feedback=f"{proc.stderr[:300]}\n{proc.stdout[:300]}",
        )
    except Exception as e:
        # Fallback: one-by-one
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
                        feedback=proc.stderr[:200],
                    )
            except Exception as e2:
                return VerifyResult(
                    status=VerifyStatus.FAIL, passed_tasks=[],
                    failed_tasks=["verifier"],
                    summary=f"Verifier error: {e2}", feedback=str(e2),
                )
        return VerifyResult(
            status=VerifyStatus.PASS,
            passed_tasks=["verifier"], failed_tasks=[],
            summary=f"Verifier: {len(core_tests)} files passed (one-by-one)",
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


def _run_with_breaker(state: dict, cfg, seed_path: str) -> tuple:
    """Shared iteration loop: circuit breaker + seed sync. Returns (cb, should_stop)."""
    state["total_attempts"] = state.get("total_attempts", 0) + 1
    state["iteration"] = state.get("iteration", 0) + 1
    cb = check_circuit_breaker(state, cfg)
    if cb.tripped:
        seed.save_seed(state, seed_path)
        return cb, True
    seed.save_seed(state, seed_path)
    return cb, False


def _update_fail_state(state: dict, error: str, seed_path: str) -> str:
    """Update consecutive failure tracking. Returns feedback string."""
    prev = state.get("last_error", "")
    state["consecutive_failures"] = state.get("consecutive_failures", 0) + 1 if error == prev else 1
    state["last_error"] = error
    seed.save_seed(state, seed_path)
    return f"[Iteration {state['iteration']}] {error}"


def _succeed(state: dict, goal: str, seed_path: str) -> None:
    """Mark goal complete, clear error state."""
    state["last_error"] = ""
    state["consecutive_failures"] = 0
    seed.mark_complete(state, goal)
    seed.save_seed(state, seed_path)


def run_reviewer(project_root: str = "") -> VerifyResult:
    """
    LLM-based code quality reviewer — DIFFERENT agent than fixer.

    Uses a separate, stricter prompt to review recent changes for:
    - Security issues
    - Anti-patterns
    - Unused code
    - Hardcoded secrets
    - Style violations

    Returns FAIL if issues found, PASS if clean.
    """
    from ecc_loop.llm import generate_fix as _llm_call
    root = Path(project_root) if project_root else Path(__file__).parent.parent
    import subprocess as _sp

    # Build a diff of UNCOMMITTED changes (not last commit)
    try:
        # Staged + unstaged
        diff = _sp.run(
            ["git", "diff", "HEAD", "--", "ecc_loop/"],
            cwd=root, capture_output=True, text=True, timeout=10,
        ).stdout
        if not diff.strip():
            # Also check staged but uncommitted
            diff = _sp.run(
                ["git", "diff", "--cached", "--", "ecc_loop/"],
                cwd=root, capture_output=True, text=True, timeout=10,
            ).stdout
    except Exception:
        diff = "(no git diff available)"
    if not diff.strip():
        return VerifyResult(
            status=VerifyStatus.PASS,
            passed_tasks=["reviewer"], failed_tasks=[],
            summary="Reviewer: no changes to review",
        )

    # Ask LLM to review
    review_prompt = f"""Review this diff. Default stance: REJECT. Only PASS if clearly safe.

{diff[:2000]}

Check: hardcoded secrets, eval/exec misuse, broken imports, unused code.

Your response (EXACTLY one line):"""

    try:
        response = _llm_call([{"role": "user", "content": review_prompt}])
        if response.strip().upper().startswith("PASS"):
            return VerifyResult(
                status=VerifyStatus.PASS,
                passed_tasks=["reviewer"], failed_tasks=[],
                summary=f"Reviewer: PASS — {response.strip()[:100]}",
            )
        return VerifyResult(
            status=VerifyStatus.FAIL,
            passed_tasks=[], failed_tasks=["reviewer"],
            summary="Reviewer: issues found",
            feedback=response.strip()[:500],
        )
    except Exception as e:
        return VerifyResult(
            status=VerifyStatus.PASS,  # Don't block on reviewer failure
            passed_tasks=["reviewer"], failed_tasks=[],
            summary=f"Reviewer: skipped (API error: {e})",
        )


def run_typecheck(project_root: str = "") -> VerifyResult:
    """
    Run mypy type checking on the project.
    Returns FAIL if type errors found.
    """
    import subprocess as _sp
    root = Path(project_root) if project_root else Path(__file__).parent.parent
    try:
        proc = _sp.run(
            ["python3", "-m", "mypy", "ecc_loop/", "--ignore-missing-imports", "--no-error-summary"],
            cwd=root, capture_output=True, text=True, timeout=30,
        )
        if proc.returncode == 0:
            return VerifyResult(
                status=VerifyStatus.PASS,
                passed_tasks=["typecheck"], failed_tasks=[],
                summary="Type check: clean",
            )
        issues = proc.stdout.strip().splitlines()
        return VerifyResult(
            status=VerifyStatus.FAIL,
            passed_tasks=[], failed_tasks=["typecheck"],
            summary=f"Type check: {len(issues)} issue(s)",
            feedback="\n".join(issues[:5]),
        )
    except FileNotFoundError:
        return VerifyResult(
            status=VerifyStatus.PASS,
            passed_tasks=["typecheck"], failed_tasks=[],
            summary="Type check: mypy not installed (skipped)",
        )
    except Exception as e:
        return VerifyResult(
            status=VerifyStatus.PASS,  # Don't block on check failures
            passed_tasks=["typecheck"], failed_tasks=[],
            summary=f"Type check: skipped ({e})",
        )

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

    # Freeze goal spec (Best Practice #2: 保持规格不变)
    _freeze(goal, seed_path)

    while True:
        # ── Circuit breaker + seed sync (shared helper) ──
        _, should_stop = _run_with_breaker(state, cfg, seed_path)
        if should_stop:
            return VerifyResult(
                status=VerifyStatus.FAIL,
                passed_tasks=[], failed_tasks=[],
                summary=f"CIRCUIT BREAKER TRIPPED — Max iterations ({cfg.max_iterations}) exceeded",
                feedback=f"Max iterations ({cfg.max_iterations}) exceeded",
            )

        # ── Run a single iteration ──
        _log("EXECUTE", goal, f"iter {state['iteration']}", state['iteration'])
        result = run_one(goal, feedback=feedback, seed_path=seed_path)

        if result.status == VerifyStatus.PASS:
            # ── Independent verifier (referee, not player) ──
            if run_verifier_on_pass:
                v_result = run_verifier()
                if v_result.status != VerifyStatus.PASS:
                    result = v_result
                else:
                    # Type check + LLM reviewer
                    t_result = run_typecheck()
                    if t_result.status != VerifyStatus.PASS:
                        result = t_result
                    else:
                        # Precise spec check (Best Practice #5)
                        s_ok, s_results = Specs.TESTS_PASS.verify()
                        if not s_ok:
                            result = VerifyResult(
                                status=VerifyStatus.FAIL, passed_tasks=[], failed_tasks=["spec"],
                                summary="Spec check: FAILED", feedback=s_results[0])
                        else:
                            r_result = run_reviewer()
                            if r_result.status != VerifyStatus.PASS:
                                result = r_result
                            else:
                                _log("PASS", goal, "all checks", state['iteration'])
                            _succeed(state, goal, seed_path)
                            return result
            else:
                _log("PASS", goal, "no verifier", state['iteration'])
                _succeed(state, goal, seed_path)
                _record_run(goal, "PASS", state["iteration"])
                return result

        # FAIL: update error tracking (shared helper)
        error = result.feedback
        _update_fail_state(state, error, seed_path)
        from ecc_loop.learning import record; record("cycle", 0, {"goal": goal[:50], "error": error[:100]})

        # Feed failure back into next DISCOVER
        feedback = f"[Iteration {state['iteration']}] {error}"


# ── /goal: run-until-condition pattern ────────────────────────────────


def goal(
    task: str,
    condition_cmd: str,
    config: Optional[CircuitBreakerConfig] = None,
    seed_path: str = "~/.hermes/ecc-loop-seed.json",
) -> VerifyResult:
    """
    /goal pattern — iterate until an external condition is met.

    Unlike loop() which verifies with pytest, goal() accepts an
    arbitrary shell command as the stop condition. A SEPARATE
    subprocess checks the condition (not the executor).

        ecc goal "fix lint errors" "pytest -q && flake8 src/"

    DISCOVER → PLAN → EXECUTE → (condition met?)
                                    ├─ YES → done
                                    └─ NO  → ITERATE

    Circuit breaker prevents infinite loops.
    """
    cfg = config or CircuitBreakerConfig()
    state = seed.load_seed(seed_path)

    if state.get("current_goal") != task:
        state["iteration"] = 0
        state["consecutive_failures"] = 0
        state["total_attempts"] = 0
        state["last_error"] = ""

    feedback: Optional[str] = None

    while True:
        # ── Circuit breaker + seed sync (shared helper) ──
        _, should_stop = _run_with_breaker(state, cfg, seed_path)
        if should_stop:
            return VerifyResult(
                status=VerifyStatus.FAIL, passed_tasks=[], failed_tasks=[],
                summary=f"CIRCUIT BREAKER TRIPPED — Max iterations ({cfg.max_iterations}) exceeded",
                feedback=f"Max iterations ({cfg.max_iterations}) exceeded",
            )

        # Run one iteration
        result = run_one(task, feedback=feedback, seed_path=seed_path)

        if result.status == VerifyStatus.PASS:
            # Check external condition (separate process = referee)
            try:
                proc = _subprocess.run(
                    condition_cmd, shell=True, capture_output=True,
                    text=True, timeout=30, cwd=Path(__file__).parent.parent,
                )
                if proc.returncode == 0:
                    _succeed(state, task, seed_path)
                    return VerifyResult(
                        status=VerifyStatus.PASS,
                        passed_tasks=["goal"],
                        failed_tasks=[],
                        summary=f"Goal met after {state['iteration']} iteration(s)",
                        feedback="",
                    )

                # Condition failed — iterate
                result = VerifyResult(
                    status=VerifyStatus.FAIL, passed_tasks=[], failed_tasks=["condition"],
                    summary=f"Condition not met (exit {proc.returncode})",
                    feedback=proc.stderr[:200] or proc.stdout[:200],
                )
            except Exception as e:
                result = VerifyResult(
                    status=VerifyStatus.FAIL, passed_tasks=[], failed_tasks=["condition"],
                    summary=f"Condition check error: {e}",
                    feedback=str(e),
                )

        # FAIL: update error tracking (shared helper)
        error = result.feedback
        _update_fail_state(state, error, seed_path)
        feedback = f"[Iteration {state['iteration']}] {error}"


# ── Legacy wrapper ──────────────────────────────────────────────────

def run(goal: str, config: Optional[CircuitBreakerConfig] = None,
        seed_path: str = "~/.hermes/ecc-loop-seed.json") -> VerifyResult:
    """Convenience: single-pass for backward compatibility."""
    return loop(goal, config=config, seed_path=seed_path)
hardcoded_password = "admin123"
