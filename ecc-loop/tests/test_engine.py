"""Tests for ecc_loop.engine"""

import pytest
from ecc_loop import engine
from ecc_loop.models import TaskStatus, VerifyStatus


def test_discover_single_goal(monkeypatch):
    import ecc_loop.seed as s
    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0", "skills": {}})
    result = engine.discover("分析我的工作模式")
    assert result.issue == "分析我的工作模式"
    assert len(result.goals) >= 1
    assert len(result.assumptions) >= 1


def test_plan_one_goal_one_task():
    from ecc_loop.models import DiscoveryResult
    discovery = DiscoveryResult(
        issue="refactor X",
        context={},
        goals=["goal a"],
        assumptions=[],
    )
    plan = engine.plan(discovery)
    assert len(plan.tasks) == 1
    assert plan.tasks[0].description == "goal a"


def test_plan_multi_goal_multi_task():
    from ecc_loop.models import DiscoveryResult
    discovery = DiscoveryResult(
        issue="multi",
        context={},
        goals=["goal 1", "goal 2"],
        assumptions=[],
    )
    plan = engine.plan(discovery)
    assert len(plan.tasks) == 2


def test_verify_all_pass():
    from ecc_loop.models import Task, Plan, ExecutionResult
    tasks = [Task(name="t1"), Task(name="t2")]
    plan = Plan(tasks=tasks)
    exec_results = [
        Task(name="t1", status=TaskStatus.PASS, output="ok"),
        Task(name="t2", status=TaskStatus.PASS, output="ok"),
    ]
    execution = ExecutionResult(results=exec_results)
    result = engine.verify(plan, execution)
    assert result.status == VerifyStatus.PASS
    assert len(result.failed_tasks) == 0


def test_verify_some_fail():
    from ecc_loop.models import Task, Plan, ExecutionResult
    tasks = [Task(name="t1"), Task(name="t2")]
    plan = Plan(tasks=tasks)
    exec_results = [
        Task(name="t1", status=TaskStatus.PASS),
        Task(name="t2", status=TaskStatus.FAIL, error="boom"),
    ]
    execution = ExecutionResult(results=exec_results)
    result = engine.verify(plan, execution)
    assert result.status == VerifyStatus.FAIL
    assert "t2" in result.failed_tasks
    assert result.feedback == "Failed tasks: t2"


def test_run_full_flow_pass(tmp_path, monkeypatch):
    """Full run with stub handler that doesn't raise."""
    import ecc_loop.engine as eng
    import ecc_loop.seed as s

    def stub_pass(task):
        return "done"

    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task", stub_pass)

    result = engine.run("do the thing")
    assert result.status == VerifyStatus.PASS


def test_run_full_flow_fail(tmp_path, monkeypatch):
    """Full run with stub handler that raises."""
    import ecc_loop.engine as eng
    import ecc_loop.seed as s

    def stub_fail(task):
        raise RuntimeError("intentional failure")

    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task", stub_fail)

    result = engine.run("do the thing")
    assert result.status == VerifyStatus.FAIL
    assert len(result.failed_tasks) == 1
