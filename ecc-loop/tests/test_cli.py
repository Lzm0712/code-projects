"""Tests for ecc_loop.cli"""

import pytest
from ecc_loop import cli


def test_cmd_run_pass(monkeypatch):
    """Single pass returns 0 on PASS."""
    import ecc_loop.engine as eng
    import ecc_loop.seed as s

    def stub_pass(task):
        return "done"

    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task", stub_pass)

    rc = cli.cmd_run("test goal")
    assert rc == 0


def test_cmd_run_fail(monkeypatch):
    """Single pass returns 1 on FAIL."""
    import ecc_loop.engine as eng
    import ecc_loop.seed as s

    def stub_fail(task):
        raise RuntimeError("test failure")

    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task", stub_fail)

    rc = cli.cmd_run("test goal")
    assert rc == 1


def test_cmd_loop_pass(monkeypatch):
    """Full loop returns 0 on PASS."""
    import ecc_loop.engine as eng
    import ecc_loop.seed as s

    def stub_pass(task):
        return "done"

    monkeypatch.setattr(s, "load_seed", lambda p: {"version": "1.0"})
    monkeypatch.setattr(eng, "_execute_task", stub_pass)

    rc = cli.cmd_loop("test loop goal")
    assert rc == 0


def test_cmd_scan():
    assert cli.cmd_scan() == 0


def test_cmd_seed():
    assert cli.cmd_seed() == 0


def test_cmd_status():
    assert cli.cmd_status() == 0
