"""Tests for auto-detecting task handlers."""

import json
import tempfile
from pathlib import Path

from ecc_loop import handlers
from ecc_loop.models import Task


def test_shell_auto_detect():
    t = Task(name="t1", description="echo hello")
    h = handlers.handler_for(t)
    assert isinstance(h, handlers.ShellHandler)


def test_shell_auto_detect_git():
    t = Task(name="t1", description="git status")
    assert isinstance(handlers.handler_for(t), handlers.ShellHandler)


def test_file_auto_detect():
    with tempfile.TemporaryDirectory() as tmp:
        spec = json.dumps({"path": f"{tmp}/x.txt", "content": "hi"})
        t = Task(name="t1", description=spec)
        h = handlers.handler_for(t)
        assert isinstance(h, handlers.FileHandler)
        h(t)
        assert Path(f"{tmp}/x.txt").read_text() == "hi"


def test_code_default():
    t = Task(name="t1", description="x = 1")
    assert isinstance(handlers.handler_for(t), handlers.CodeHandler)


def test_explicit_shell_trumps_auto():
    """Name 'task_shell' forces ShellHandler even if content looks like code."""
    t = Task(name="task_shell_backup", description="x = 1")
    assert isinstance(handlers.handler_for(t), handlers.ShellHandler)


def test_code_handler_actually_works():
    code = "from pathlib import Path\nPath('/tmp/ecc_handler_test.txt').write_text('works')\n__result__ = 'ok'\n"
    t = Task(name="t1", description=code)
    h = handlers.handler_for(t)
    result = h(t)
    assert result == "ok"
    assert Path("/tmp/ecc_handler_test.txt").read_text() == "works"
