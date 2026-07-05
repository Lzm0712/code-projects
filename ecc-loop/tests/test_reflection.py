"""Tests for ecc_loop.reflection"""

from ecc_loop import reflection


def test_fast_path_short_query():
    assert reflection.should_use_fast_path("hello world") is True


def test_fast_path_complex_keyword():
    assert reflection.should_use_fast_path("分析一下系统") is False


def test_fast_path_long_query():
    long_q = "this is a very long query that should definitely exceed the short limit"
    assert reflection.should_use_fast_path(long_q) is False


def test_reflect_auto_select():
    assert "[ECC Fast]" in reflection.reflect("status")
    assert "[ECC Full]" in reflection.reflect("请分析系统的架构设计方案")
