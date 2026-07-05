"""测试统计分析模块"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/Users/liuzimin/log-analyzer/src')

from log_analyzer.parser import LogLevel, LogEntry
from log_analyzer.stats import (
    count_by_level,
    calculate_percentages,
    count_by_time,
    top_n_errors,
    keyword_frequency,
    export_stats_json,
)


class TestCountByLevel:
    def test_count_by_level(self):
        entries = [
            LogEntry(datetime.now(), LogLevel.INFO, "msg1", "raw1"),
            LogEntry(datetime.now(), LogLevel.INFO, "msg2", "raw2"),
            LogEntry(datetime.now(), LogLevel.ERROR, "msg3", "raw3"),
            LogEntry(datetime.now(), LogLevel.ERROR, "msg4", "raw4"),
            LogEntry(datetime.now(), LogLevel.ERROR, "msg5", "raw5"),
        ]
        counts = count_by_level(entries)
        assert counts == {"INFO": 2, "ERROR": 3}

    def test_empty_entries(self):
        counts = count_by_level([])
        assert counts == {}


class TestCalculatePercentages:
    def test_calculate_percentages(self):
        counts = {"INFO": 2, "ERROR": 3}
        pct = calculate_percentages(counts)
        assert pct["INFO"] == 40.0
        assert pct["ERROR"] == 60.0

    def test_empty_counts(self):
        pct = calculate_percentages({})
        assert pct == {}


class TestCountByTime:
    def test_count_by_time_hour(self):
        entries = [
            LogEntry(datetime(2026, 6, 24, 10, 15, 32), LogLevel.INFO, "msg1", "raw1"),
            LogEntry(datetime(2026, 6, 24, 10, 20, 33), LogLevel.INFO, "msg2", "raw2"),
            LogEntry(datetime(2026, 6, 24, 11, 5, 33), LogLevel.ERROR, "msg3", "raw3"),
        ]
        counts = count_by_time(entries, "hour")
        assert counts == {"2026-06-24 10:00": 2, "2026-06-24 11:00": 1}

    def test_count_by_time_day(self):
        entries = [
            LogEntry(datetime(2026, 6, 24, 10, 15, 32), LogLevel.INFO, "msg1", "raw1"),
            LogEntry(datetime(2026, 6, 24, 20, 20, 33), LogLevel.INFO, "msg2", "raw2"),
            LogEntry(datetime(2026, 6, 25, 5, 5, 33), LogLevel.ERROR, "msg3", "raw3"),
        ]
        counts = count_by_time(entries, "day")
        assert counts == {"2026-06-24": 2, "2026-06-25": 1}


class TestTopNErrors:
    def test_top_n_errors(self):
        entries = [
            LogEntry(datetime.now(), LogLevel.ERROR, "Connection timeout", "raw1"),
            LogEntry(datetime.now(), LogLevel.ERROR, "Connection timeout", "raw2"),
            LogEntry(datetime.now(), LogLevel.ERROR, "Connection timeout", "raw3"),
            LogEntry(datetime.now(), LogLevel.ERROR, "File not found", "raw4"),
            LogEntry(datetime.now(), LogLevel.ERROR, "File not found", "raw5"),
            LogEntry(datetime.now(), LogLevel.CRITICAL, "System crash", "raw6"),
        ]
        top = top_n_errors(entries, 3)
        assert len(top) == 3
        assert top[0]["message"] == "Connection timeout"
        assert top[0]["count"] == 3
        assert top[1]["message"] == "File not found"
        assert top[1]["count"] == 2

    def test_no_errors(self):
        entries = [
            LogEntry(datetime.now(), LogLevel.INFO, "msg1", "raw1"),
        ]
        top = top_n_errors(entries, 5)
        assert top == []


class TestKeywordFrequency:
    def test_keyword_frequency(self):
        entries = [
            LogEntry(datetime(2026, 6, 24, 10, 15, 32), LogLevel.INFO, "Error occurred", "raw1"),
            LogEntry(datetime(2026, 6, 24, 10, 20, 33), LogLevel.ERROR, "Another error", "raw2"),
            LogEntry(datetime(2026, 6, 24, 11, 5, 34), LogLevel.ERROR, "Error in loop", "raw3"),
        ]
        freq = keyword_frequency(entries, "error")
        # "Error occurred" and "Another error" both contain "error" (case-insensitive)
        assert freq == {"2026-06-24 10:00": 2, "2026-06-24 11:00": 1}

    def test_keyword_not_found(self):
        entries = [
            LogEntry(datetime.now(), LogLevel.INFO, "App started", "raw1"),
        ]
        freq = keyword_frequency(entries, "error")
        assert freq == {}


class TestExportStatsJson:
    def test_export_stats_json(self):
        entries = [
            LogEntry(datetime(2026, 6, 24, 10, 15, 32), LogLevel.INFO, "App started", "raw1"),
            LogEntry(datetime(2026, 6, 24, 10, 15, 33), LogLevel.ERROR, "Error occurred", "raw2"),
        ]
        result = export_stats_json(entries)
        assert result["status"] == "success"
        assert result["total"] == 2
        assert result["level_counts"] == {"INFO": 1, "ERROR": 1}
        assert len(result["logs"]) == 2
