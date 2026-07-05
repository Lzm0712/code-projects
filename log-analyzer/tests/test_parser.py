"""测试日志解析器"""

import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/Users/liuzimin/log-analyzer/src')

from log_analyzer.parser import (
    LogEntry,
    LogLevel,
    parse_line,
    parse_standard_format,
    parse_loguru_format,
    parse_json_format,
    stream_parse,
    detect_format,
)


class TestLogLevel:
    def test_from_string(self):
        assert LogLevel.from_string("INFO") == LogLevel.INFO
        assert LogLevel.from_string("error") == LogLevel.ERROR
        assert LogLevel.from_string("Warning") == LogLevel.WARNING
        assert LogLevel.from_string("DEBUG") == LogLevel.DEBUG
        assert LogLevel.from_string("CRITICAL") == LogLevel.CRITICAL
        assert LogLevel.from_string("invalid") is None

    def test_from_string_list(self):
        result = LogLevel.from_string_list(["info", "ERROR", "warning"])
        assert LogLevel.INFO in result
        assert LogLevel.ERROR in result
        assert LogLevel.WARNING in result


class TestStandardFormat:
    def test_parse_valid(self):
        line = "[2026-06-24 10:15:32] INFO    | App started on port 8080"
        entry = parse_standard_format(line, 1)
        assert entry is not None
        assert entry.level == LogLevel.INFO
        assert entry.message == "App started on port 8080"
        assert entry.line_number == 1

    def test_parse_with_milliseconds(self):
        line = "[2026-06-24 10:15:32.123] ERROR   | Connection failed"
        entry = parse_standard_format(line, 1)
        assert entry is not None
        assert entry.level == LogLevel.ERROR


class TestLoguruFormat:
    def test_parse_valid(self):
        line = "2026-06-24 10:15:32 | INFO | App started"
        entry = parse_loguru_format(line, 1)
        assert entry is not None
        assert entry.level == LogLevel.INFO
        assert entry.message == "App started"

    def test_parse_no_space(self):
        line = "2026-06-24 10:15:32 |ERROR| Error occurred"
        entry = parse_loguru_format(line, 1)
        assert entry is not None
        assert entry.level == LogLevel.ERROR


class TestJsonFormat:
    def test_parse_valid(self):
        line = '{"time": "2026-06-24 10:15:32", "level": "INFO", "message": "App started"}'
        entry = parse_json_format(line, 1)
        assert entry is not None
        assert entry.level == LogLevel.INFO
        assert entry.message == "App started"

    def test_parse_loguru_style(self):
        line = '{"timestamp": "2026-06-24T10:15:32", "severity": "ERROR", "msg": "Error occurred"}'
        entry = parse_json_format(line, 1)
        assert entry is not None
        assert entry.level == LogLevel.ERROR
        assert entry.message == "Error occurred"

    def test_parse_invalid(self):
        line = "not json at all"
        entry = parse_json_format(line, 1)
        assert entry is None


class TestParseLine:
    def test_auto_detect_standard(self):
        line = "[2026-06-24 10:15:32] INFO    | Test message"
        entry = parse_line(line, 1)
        assert entry is not None
        assert entry.level == LogLevel.INFO

    def test_auto_detect_loguru(self):
        line = "2026-06-24 10:15:32 | INFO | Test message"
        entry = parse_line(line, 1)
        assert entry is not None
        assert entry.level == LogLevel.INFO

    def test_auto_detect_json(self):
        line = '{"time": "2026-06-24 10:15:32", "level": "INFO", "message": "Test"}'
        entry = parse_line(line, 1)
        assert entry is not None
        assert entry.level == LogLevel.INFO

    def test_empty_line(self):
        entry = parse_line("", 1)
        assert entry is None

    def test_none_line(self):
        entry = parse_line(None, 1)
        assert entry is None


class TestStreamParse:
    def test_parse_sample_log(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text(
            "[2026-06-24 10:15:32] INFO    | App started\n"
            "[2026-06-24 10:15:33] ERROR   | Connection failed\n"
            "[2026-06-24 10:15:34] WARNING | Retrying\n"
        )

        entries = list(stream_parse(str(log_file)))
        assert len(entries) == 3
        assert entries[0].level == LogLevel.INFO
        assert entries[1].level == LogLevel.ERROR
        assert entries[2].level == LogLevel.WARNING


class TestDetectFormat:
    def test_detect_standard(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text(
            "[2026-06-24 10:15:32] INFO    | App started\n"
            "[2026-06-24 10:15:33] ERROR   | Error\n"
        )
        assert detect_format(str(log_file)) == "standard"

    def test_detect_loguru(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text(
            "2026-06-24 10:15:32 | INFO | App started\n"
            "2026-06-24 10:15:33 | ERROR | Error\n"
        )
        assert detect_format(str(log_file)) == "loguru"

    def test_detect_json(self, tmp_path):
        log_file = tmp_path / "test.log"
        log_file.write_text(
            '{"time": "2026-06-24 10:15:32", "level": "INFO", "message": "App started"}\n'
            '{"time": "2026-06-24 10:15:33", "level": "ERROR", "message": "Error"}\n'
        )
        assert detect_format(str(log_file)) == "json"
