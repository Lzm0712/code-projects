"""Tests for ecc_loop.goal_freeze"""

from ecc_loop import goal_freeze


def test_freeze_and_check_match():
    goal_freeze.freeze("fix bug")
    assert goal_freeze.check("fix bug")
    assert not goal_freeze.check("different bug")
    goal_freeze.unfreeze()


def test_unfreeze_allows_any():
    goal_freeze.freeze("task A")
    assert not goal_freeze.check("task B")
    goal_freeze.unfreeze()
    assert goal_freeze.check("task B")  # No freeze → allow anything
