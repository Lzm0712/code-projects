"""Tests for ecc_loop.safety"""

from ecc_loop.safety import safety_check, check_denylist, check_path


def test_blocks_env_file():
    ok, reason = safety_check("Path('.env').write_text('hacked')")
    assert not ok
    assert "denylist" in reason.lower() or "env" in reason.lower()


def test_allows_normal_file():
    ok, reason = safety_check("Path('ecc_loop/engine.py').read_text()")
    assert ok


def test_blocks_too_many_files():
    many = " ".join([f"Path('file{i}.py')" for i in range(15)])
    ok, reason = safety_check(many)
    assert not ok
    assert "10" in reason


def test_check_path_denylist():
    ok, _ = check_path(".env")
    assert not ok


def test_check_path_allowed():
    ok, _ = check_path("src/main.py")
    assert ok
