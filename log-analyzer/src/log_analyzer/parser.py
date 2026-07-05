"""日志解析器 - 支持标准格式、Loguru格式、JSON格式"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Iterator, Optional, Dict, Any, List


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_string(cls, s: str) -> Optional["LogLevel"]:
        try:
            return cls(s.upper())
        except ValueError:
            return None

    @classmethod
    def from_string_list(cls, levels: List[str]) -> List["LogLevel"]:
        result = []
        for l in levels:
            lv = cls.from_string(l.strip().upper())
            if lv:
                result.append(lv)
        return result


@dataclass
class LogEntry:
    timestamp: Optional[datetime]
    level: LogLevel
    message: str
    raw_line: str
    line_number: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)


# 标准日志格式: [2026-06-24 10:15:32] INFO    | message
STANDARD_PATTERN = re.compile(
    r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)\]\s+(\w+)\s+\|\s*(.*)'
)

# Loguru 格式: 2026-06-24 10:15:32 | INFO | message
LOGURU_PATTERN = re.compile(
    r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s+\|\s*(\w+)\s*\|\s*(.*)'
)

# JSON 格式
JSON_PATTERN = re.compile(r'^\s*\{.*\}\s*$')


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """解析时间戳字符串"""
    formats = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(ts_str.strip(), fmt)
        except ValueError:
            continue
    return None


def parse_loguru_format(line: str, line_number: int) -> Optional[LogEntry]:
    """解析 Loguru 格式日志"""
    match = LOGURU_PATTERN.match(line)
    if match:
        ts_str, level_str, message = match.groups()
        timestamp = parse_timestamp(ts_str)
        level = LogLevel.from_string(level_str) or LogLevel.INFO
        return LogEntry(timestamp=timestamp, level=level, message=message.strip(), raw_line=line, line_number=line_number)
    return None


def parse_standard_format(line: str, line_number: int) -> Optional[LogEntry]:
    """解析标准格式日志"""
    match = STANDARD_PATTERN.match(line)
    if match:
        ts_str, level_str, message = match.groups()
        timestamp = parse_timestamp(ts_str)
        level = LogLevel.from_string(level_str) or LogLevel.INFO
        return LogEntry(timestamp=timestamp, level=level, message=message.strip(), raw_line=line, line_number=line_number)
    return None


def parse_json_format(line: str, line_number: int) -> Optional[LogEntry]:
    """解析 JSON 格式日志"""
    try:
        data = json.loads(line)
        ts_str = data.get("time") or data.get("timestamp") or data.get("@timestamp")
        level_str = data.get("level") or data.get("severity") or "INFO"
        message = data.get("message") or data.get("msg") or data.get("log")

        timestamp = parse_timestamp(str(ts_str)) if ts_str else None
        level = LogLevel.from_string(str(level_str)) or LogLevel.INFO

        extra = {k: v for k, v in data.items() if k not in ("time", "timestamp", "@timestamp", "level", "severity", "message", "msg", "log")}

        return LogEntry(timestamp=timestamp, level=level, message=str(message), raw_line=line, line_number=line_number, extra=extra)
    except (json.JSONDecodeError, ValueError):
        return None


def parse_line(line: str, line_number: int) -> Optional[LogEntry]:
    """自动检测并解析日志行"""
    if line is None:
        return None
    line = line.rstrip('\n\r')
    if not line:
        return None

    # 尝试 JSON 格式
    if JSON_PATTERN.match(line):
        entry = parse_json_format(line, line_number)
        if entry:
            return entry

    # 尝试 Loguru 格式
    entry = parse_loguru_format(line, line_number)
    if entry:
        return entry

    # 尝试标准格式
    entry = parse_standard_format(line, line_number)
    if entry:
        return entry

    # 无法解析，返回 None
    return None


def stream_parse(filepath: str, chunk_size: int = 8192) -> Iterator[LogEntry]:
    """流式解析大文件日志"""
    line_number = 0
    buffer = ""

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            buffer += chunk
            lines = buffer.split('\n')
            buffer = lines[-1]  # 保留未完成的行

            for line in lines[:-1]:
                line_number += 1
                entry = parse_line(line, line_number)
                if entry:
                    yield entry

        # 处理最后一行
        if buffer:
            line_number += 1
            entry = parse_line(buffer, line_number)
            if entry:
                yield entry


def parse_file(filepath: str) -> List[LogEntry]:
    """解析整个日志文件（适用于小文件）"""
    return list(stream_parse(filepath))


def detect_format(filepath: str, sample_lines: int = 10) -> str:
    """检测日志文件格式"""
    count = 0
    formats = {"standard": 0, "loguru": 0, "json": 0, "unknown": 0}

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if count >= sample_lines:
                break
            count += 1
            line = line.strip()
            if not line:
                continue
            if JSON_PATTERN.match(line):
                formats["json"] += 1
            elif LOGURU_PATTERN.match(line):
                formats["loguru"] += 1
            elif STANDARD_PATTERN.match(line):
                formats["standard"] += 1
            else:
                formats["unknown"] += 1

    return max(formats, key=formats.get)
