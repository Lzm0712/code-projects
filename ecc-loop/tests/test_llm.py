"""Tests for ecc_loop.llm"""

import pytest
from ecc_loop.llm import generate_fix, LLMHandler
from ecc_loop.models import Task


@pytest.mark.skip(reason="requires live API key and network")
def test_generate_fix_returns_code():
    code = generate_fix("test_llm.py is missing")
    assert code
    assert len(code) > 20


@pytest.mark.skip(reason="requires live API key and network")
def test_llm_handler_generates_and_executes():
    task = Task(name="test_fix", description="Create a file at /tmp/ecc_llm_test.txt with 'hello'")
    handler = LLMHandler()
    result = handler(task)
    assert result
    from pathlib import Path
    assert Path("/tmp/ecc_llm_test.txt").exists()
    Path("/tmp/ecc_llm_test.txt").unlink()
