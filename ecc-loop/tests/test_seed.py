"""Tests for ecc_loop.seed"""

from pathlib import Path
import tempfile

from ecc_loop import seed


def test_load_seed_returns_default_when_missing():
    state = seed.load_seed("/tmp/nonexistent/seed.json")
    assert state["version"] == seed.SEED_SCHEMA_VERSION
    assert state["execution_state"]["completed_tasks"] == []


def test_roundtrip_seed():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "seed.json"
        state = seed.load_seed(p)
        state["current_phase"] = "Phase A"
        seed.save_seed(state, p)

        loaded = seed.load_seed(p)
        assert loaded["current_phase"] == "Phase A"
        assert loaded["version"] == seed.SEED_SCHEMA_VERSION


def test_mark_complete():
    state = seed.load_seed("/tmp/_test.json")
    state = seed.mark_complete(state, "Task A1")
    assert "Task A1" in state["execution_state"]["completed_tasks"]


def test_track_skill():
    state = seed.load_seed("/tmp/_test.json")
    state = seed.track_skill(state, "test-skill", "1.0.0")
    assert state["skills"]["test-skill"]["version"] == "1.0.0"
