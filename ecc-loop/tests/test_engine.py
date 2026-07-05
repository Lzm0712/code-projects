"""Tests for ecc_loop.engine"""

import pytest
from ecc_loop import engine
from ecc_loop.models import TaskStatus, VerifyStatus, CircuitBreakerConfig


# ── run_one ───────────────────────────────────────────────────────────

def test_discover_single_goal(monkeypatch):
    import ecc_loop.seed as s
    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0", "skills": {}})
    result = engine.discover("分析我的工作模式")
    assert result.issue == "分析我的工作模式"
    assert len(result.goals) >= 1
    assert len(result.assumptions) >= 1


def test_discover_with_feedback(monkeypatch):
    import ecc_loop.seed as s
    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0", "skills": {}})
    result = engine.discover("fix bug", feedback="shell command failed")
    assert "shell command failed" in result.context["previous_feedback"]


def test_plan_one_goal():
    from ecc_loop.models import DiscoveryResult
    discovery = DiscoveryResult(issue="refactor X", context={}, goals=["goal a"], assumptions=[])
    plan = engine.plan(discovery)
    assert len(plan.tasks) == 1
    assert plan.tasks[0].description == "goal a"


def test_plan_multi_goal():
    from ecc_loop.models import DiscoveryResult
    discovery = DiscoveryResult(issue="multi", context={}, goals=["a", "b"], assumptions=[])
    plan = engine.plan(discovery)
    assert len(plan.tasks) == 2


def test_verify_all_pass():
    from ecc_loop.models import Task, Plan, ExecutionResult
    plan = Plan(tasks=[Task(name="t1"), Task(name="t2")])
    exec_result = ExecutionResult(results=[
        Task(name="t1", status=TaskStatus.PASS, output="ok"),
        Task(name="t2", status=TaskStatus.PASS, output="ok"),
    ])
    result = engine.verify(plan, exec_result)
    assert result.status == VerifyStatus.PASS


def test_verify_some_fail():
    from ecc_loop.models import Task, Plan, ExecutionResult
    plan = Plan(tasks=[Task(name="t1"), Task(name="t2")])
    exec_result = ExecutionResult(results=[
        Task(name="t1", status=TaskStatus.PASS),
        Task(name="t2", status=TaskStatus.FAIL, error="boom"),
    ])
    result = engine.verify(plan, exec_result)
    assert result.status == VerifyStatus.FAIL
    assert "t2" in result.failed_tasks


def test_run_one_pass(monkeypatch):
    import ecc_loop.engine as eng
    import ecc_loop.seed as s
    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task", lambda task: "done")
    result = engine.run_one("do the thing")
    assert result.status == VerifyStatus.PASS


def test_run_one_fail(monkeypatch):
    import ecc_loop.engine as eng
    import ecc_loop.seed as s
    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task", lambda task: (_ for _ in ()).throw(RuntimeError("fail")))
    result = engine.run_one("do the thing")
    assert result.status == VerifyStatus.FAIL


# ── loop (full closed loop) ───────────────────────────────────────────

def test_loop_pass_first_try(monkeypatch):
    """loop() returns PASS on first iteration when handler succeeds."""
    import ecc_loop.engine as eng
    import ecc_loop.seed as s
    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task", lambda task: "done")

    result = engine.loop("test goal", config=CircuitBreakerConfig(), run_verifier_on_pass=False)
    assert result.status == VerifyStatus.PASS


def test_loop_circuit_breaker_always_fails(monkeypatch):
    """loop() trips circuit breaker when handler always raises."""
    import ecc_loop.engine as eng
    import ecc_loop.seed as s
    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task",
        lambda task: (_ for _ in ()).throw(RuntimeError("always fail")))
    config = CircuitBreakerConfig(max_iterations=3, max_consecutive_failures=2)

    result = engine.loop("test goal", config=config, run_verifier_on_pass=False)
    assert result.status == VerifyStatus.FAIL
    assert "CIRCUIT BREAKER TRIPPED" in result.summary


def test_loop_succeeds_after_retry(monkeypatch):
    """loop() succeeds after first failure, second try passes."""
    import ecc_loop.engine as eng
    import ecc_loop.seed as s
    calls = [0]

    def flaky_handler(task):
        calls[0] += 1
        if calls[0] == 1:
            raise RuntimeError("first try fail")
        return "ok on retry"

    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task", flaky_handler)
    config = CircuitBreakerConfig(max_iterations=5, max_consecutive_failures=3)

    result = engine.loop("test goal", config=config, run_verifier_on_pass=False)
    assert result.status == VerifyStatus.PASS


def test_loop_same_goal_resets(monkeypatch):
    """New goal resets iteration counters."""
    import ecc_loop.engine as eng
    import ecc_loop.seed as s

    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task", lambda task: "done")

    result = engine.loop("same goal", config=CircuitBreakerConfig(), run_verifier_on_pass=False)
    assert result.status == VerifyStatus.PASS
