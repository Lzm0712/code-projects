"""统计分析模块"""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from .parser import LogEntry, LogLevel, stream_parse


def count_by_level(entries: List[LogEntry]) -> Dict[str, int]:
    """按级别统计日志数量"""
    counter = Counter(e.level.value for e in entries)
    return dict(counter)


def calculate_percentages(counts: Dict[str, int]) -> Dict[str, float]:
    """计算各级别的百分比"""
    total = sum(counts.values())
    if total == 0:
        return {}
    return {k: round(v / total * 100, 2) for k, v in counts.items()}


def count_by_time(entries: List[LogEntry], interval: str = "hour") -> Dict[str, int]:
    """按时间统计日志数量

    Args:
        entries: 日志条目列表
        interval: 时间间隔 "hour" 或 "day"
    """
    counter = Counter()
    for entry in entries:
        if entry.timestamp:
            if interval == "hour":
                key = entry.timestamp.strftime("%Y-%m-%d %H:00")
            else:  # day
                key = entry.timestamp.strftime("%Y-%m-%d")
            counter[key] += 1
    return dict(sorted(counter.items()))


def top_n_errors(entries: List[LogEntry], n: int = 10) -> List[Dict[str, Any]]:
    """统计 Top N 错误日志"""
    error_entries = [e for e in entries if e.level in (LogLevel.ERROR, LogLevel.CRITICAL)]

    # 按消息分组
    message_counter = Counter(e.message for e in error_entries)
    top_messages = message_counter.most_common(n)

    return [
        {"message": msg, "count": count, "level": "ERROR"}
        for msg, count in top_messages
    ]


def keyword_frequency(entries: List[LogEntry], keyword: str) -> Dict[str, int]:
    """统计关键词出现频率（按时间）"""
    keyword = keyword.lower()
    counter = defaultdict(int)

    for entry in entries:
        if keyword in entry.message.lower():
            if entry.timestamp:
                key = entry.timestamp.strftime("%Y-%m-%d %H:00")
            else:
                key = "unknown"
            counter[key] += 1

    return dict(sorted(counter.items()))


def get_statistics(
    filepath: str,
    by_level: bool = False,
    by_time: bool = False,
    top_n: int = 10,
    keyword: Optional[str] = None,
    interval: str = "hour",
) -> Dict[str, Any]:
    """获取日志统计信息"""
    entries = list(stream_parse(filepath))
    result = {"total": len(entries)}

    if by_level:
        level_counts = count_by_level(entries)
        result["level_counts"] = level_counts
        result["level_percentages"] = calculate_percentages(level_counts)

    if by_time:
        result["time_counts"] = count_by_time(entries, interval)

    if top_n > 0:
        result["top_errors"] = top_n_errors(entries, top_n)

    if keyword:
        result["keyword_frequency"] = keyword_frequency(entries, keyword)

    return result


def export_stats_csv(entries: List[LogEntry], output_path: str) -> None:
    """导出统计结果为 CSV"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("timestamp,level,message\n")
        for entry in entries:
            ts = entry.timestamp.strftime("%Y-%m-%dT%H:%M:%S") if entry.timestamp else ""
            level = entry.level.value
            msg = entry.message.replace('"', '""')
            f.write(f'"{ts}","{level}","{msg}"\n')


def export_stats_json(entries: List[LogEntry]) -> Dict[str, Any]:
    """导出统计结果为 JSON 结构"""
    level_counts = count_by_level(entries)
    logs_data = []

    for entry in entries:
        logs_data.append({
            "timestamp": entry.timestamp.strftime("%Y-%m-%dT%H:%M:%S") if entry.timestamp else None,
            "level": entry.level.value,
            "message": entry.message,
        })

    return {
        "status": "success",
        "total": len(entries),
        "level_counts": level_counts,
        "logs": logs_data,
    }
