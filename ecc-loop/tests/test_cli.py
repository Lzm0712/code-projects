"""Tests for ecc_loop.cli"""

import pytest
from ecc_loop import cli


def test_cmd_run_pass(monkeypatch):
    """CLI run returns 0 on PASS."""
    import ecc_loop.engine as eng

    def stub_pass(task):
        return "done"

    monkeypatch.setattr(eng, "_execute_task", stub_pass)

    rc = cli.cmd_run("test goal")
    assert rc == 0


def test_cmd_run_fail(monkeypatch):
    """CLI run returns 1 on FAIL."""
    import ecc_loop.engine as eng

    def stub_fail(task):
        raise RuntimeError("test failure")

    monkeypatch.setattr(eng, "_execute_task", stub_fail)

    rc = cli.cmd_run("test goal")
    assert rc == 1


def test_cmd_scan():
    rc = cli.cmd_scan()
    assert rc == 0


def test_cmd_seed():
    rc = cli.cmd_seed()
    assert rc == 0


def test_cmd_status():
    rc = cli.cmd_status()
    assert rc == 0
