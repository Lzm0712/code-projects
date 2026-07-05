"""Tests for ecc_loop.precise_specs"""

from ecc_loop.precise_specs import Spec, Specs, verify_specs


def test_spec_pass():
    s = Spec("test passes", "python3 -c 'exit(0)'")
    ok, msg = s.verify()
    assert ok
    assert "✅" in msg


def test_spec_fail():
    s = Spec("test fails", "python3 -c 'exit(1)'")
    ok, msg = s.verify()
    assert not ok
    assert "❌" in msg


def test_file_exists_spec():
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "x.txt"
        f.write_text("hi")
        s = Specs.FILE_EXISTS(str(f))
        ok, _ = s.verify()
        assert ok


def test_verify_multiple_specs():
    specs = [
        Spec("always pass", "true"),
        Spec("always fail", "false"),
    ]
    all_pass, results = verify_specs(specs)
    assert not all_pass
    assert len(results) == 2
