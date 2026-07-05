"""测试日志过滤器"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/Users/liuzimin/log-analyzer/src')

from log_analyzer.parser import LogLevel, stream_parse
from log_analyzer.filter import LogFilter, filter_logs


class TestLogFilter:
    @pytest.fixture
    def sample_log_file(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text(
            "[2026-06-24 10:15:32] INFO    | App started on port 8080\n"
            "[2026-06-24 10:15:33] DEBUG   | Debug message\n"
            "[2026-06-24 10:15:34] ERROR   | Connection failed: timeout\n"
            "[2026-06-24 10:15:35] WARNING | Retrying connection\n"
            "[2026-06-24 10:15:36] ERROR   | Connection refused\n"
            "[2026-06-24 10:15:37] INFO    | App running\n"
        )
        return log_file

    def test_filter_by_level(self, sample_log_file):
        f = LogFilter(str(sample_log_file), levels=[LogLevel.ERROR])
        entries = f.filter_all()
        assert len(entries) == 2
        assert all(e.level == LogLevel.ERROR for e in entries)

    def test_filter_by_multiple_levels(self, sample_log_file):
        f = LogFilter(str(sample_log_file), levels=[LogLevel.ERROR, LogLevel.WARNING])
        entries = f.filter_all()
        assert len(entries) == 3
        assert all(e.level in (LogLevel.ERROR, LogLevel.WARNING) for e in entries)

    def test_filter_by_grep(self, sample_log_file):
        f = LogFilter(str(sample_log_file), grep="connection")
        entries = f.filter_all()
        assert len(entries) == 3  # timeout, Retrying, refused

    def test_filter_by_regex(self, sample_log_file):
        f = LogFilter(str(sample_log_file), regex=r"Connection (failed|refused)")
        entries = f.filter_all()
        assert len(entries) == 2

    def test_filter_by_time_since(self, sample_log_file):
        since = datetime(2026, 6, 24, 10, 15, 35)
        f = LogFilter(str(sample_log_file), since=since)
        entries = f.filter_all()
        assert len(entries) == 3  # WARNING, ERROR, INFO after 10:15:35

    def test_filter_by_time_until(self, sample_log_file):
        until = datetime(2026, 6, 24, 10, 15, 35)
        f = LogFilter(str(sample_log_file), until=until)
        entries = f.filter_all()
        assert len(entries) == 3  # INFO, DEBUG, ERROR, WARNING before 10:15:35

    def test_filter_by_time_range(self, sample_log_file):
        since = datetime(2026, 6, 24, 10, 15, 34)
        until = datetime(2026, 6, 24, 10, 15, 36)
        f = LogFilter(str(sample_log_file), since=since, until=until)
        entries = f.filter_all()
        assert len(entries) == 2  # ERROR (10:15:34), WARNING (10:15:35); ERROR at 10:15:36 is excluded (until is exclusive)

    def test_filter_no_match(self, sample_log_file):
        f = LogFilter(str(sample_log_file), grep="nonexistent")
        entries = f.filter_all()
        assert len(entries) == 0

    def test_filter_combined(self, sample_log_file):
        f = LogFilter(
            str(sample_log_file),
            levels=[LogLevel.ERROR],
            grep="connection"
        )
        entries = f.filter_all()
        assert len(entries) == 2


class TestFilterLogsFunction:
    def test_filter_logs_convenience(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text(
            "[2026-06-24 10:15:32] INFO    | App started\n"
            "[2026-06-24 10:15:33] ERROR   | Error occurred\n"
        )
        entries = filter_logs(str(log_file), levels=[LogLevel.ERROR])
        assert len(entries) == 1
        assert entries[0].level == LogLevel.ERROR
