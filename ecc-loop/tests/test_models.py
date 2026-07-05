"""Tests for ecc_loop.models"""

import pytest
from ecc_loop.models import (
    DiscoveryResult, Plan, ExecutionResult, VerifyResult,
    Task, TaskStatus, VerifyStatus,
)


def test_task_defaults():
    t = Task(name="test_task", description="do something")
    assert t.status == TaskStatus.PENDING
    assert t.output == ""
    assert t.error == ""
    d = t.to_dict()
    assert d["name"] == "test_task"
    assert d["status"] == "pending"


def test_task_to_dict_roundtrip():
    t = Task(name="x", description="y", status=TaskStatus.FAIL, error="boom")
    d = t.to_dict()
    assert d["status"] == "fail"
    assert d["error"] == "boom"


def test_discovery_result():
    dr = DiscoveryResult(
        issue="refactor X",
        context={"skills": 3},
        goals=["goal a", "goal b"],
        assumptions=["X exists"],
    )
    assert len(dr.goals) == 2
    assert dr.issue == "refactor X"


def test_plan_tasks():
    tasks = [Task(name="t1"), Task(name="t2")]
    p = Plan(tasks=tasks, summary="two tasks")
    assert len(p.to_dict()["tasks"]) == 2


def test_verify_pass():
    vr = VerifyResult(
        status=VerifyStatus.PASS,
        passed_tasks=["t1", "t2"],
        failed_tasks=[],
        summary="all good",
    )
    assert vr.status == VerifyStatus.PASS
    assert len(vr.passed_tasks) == 2


def test_verify_fail():
    vr = VerifyResult(
        status=VerifyStatus.FAIL,
        passed_tasks=["t1"],
        failed_tasks=["t2"],
        summary="1/2 passed",
        feedback="t2 errored",
    )
    assert vr.status == VerifyStatus.FAIL
    assert "t2" in vr.failed_tasks
    assert "t2 errored" in vr.feedback
