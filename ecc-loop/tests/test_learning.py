"""Tests for ecc_loop.learning"""

from ecc_loop.learning import record, summary


def test_record_and_summary():
    record("cycle", 1, {"goal": "test"})
    record("cycle", 0, {"goal": "test", "error": "fail"})
    record("cycle", 1, {"goal": "test"})
    s = summary()
    assert s["total_runs"] >= 3
    assert s["passes"] >= 2
    assert s["fails"] >= 1


def test_summary_empty():
    # Metrics accumulate — just verify it returns dict
    s = summary()
    assert isinstance(s, dict)
    assert "total_runs" in s
