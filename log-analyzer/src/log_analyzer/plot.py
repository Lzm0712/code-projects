"""可视化模块 - 终端 ASCII 图表"""

import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import plotext as plt
except ImportError:
    plt = None

from .parser import LogEntry, LogLevel, stream_parse
from .stats import count_by_level, count_by_time


def plot_level_distribution(
    entries: List[LogEntry],
    plot_type: str = "bar",
    width: int = 80,
    height: int = 20,
    export_path: Optional[str] = None,
) -> None:
    """绘制日志级别分布图"""
    if plt is None:
        print("Error: plotext not installed. Run: pip install plotext", file=sys.stderr)
        return

    level_counts = count_by_level(entries)
    if not level_counts:
        print("No data to plot", file=sys.stderr)
        return

    labels = list(level_counts.keys())
    values = list(level_counts.values())

    plt.figure()  # 创建新图表
    plt.plotsize(width, height)

    if plot_type == "pie":
        plt.pie(values, labels=labels)
    elif plot_type == "line":
        plt.plot(labels, values)
    else:  # bar (default)
        plt.bar(labels, values)

    plt.title("Log Level Distribution")
    plt.xlabel("Level")
    plt.ylabel("Count")

    if export_path:
        plt.save(export_path)
        print(f"Chart saved to {export_path}")
    else:
        plt.show()


def plot_time_trend(
    entries: List[LogEntry],
    interval: str = "hour",
    plot_type: str = "line",
    width: int = 80,
    height: int = 20,
    export_path: Optional[str] = None,
) -> None:
    """绘制时间趋势图"""
    if plt is None:
        print("Error: plotext not installed. Run: pip install plotext", file=sys.stderr)
        return

    time_counts = count_by_time(entries, interval)
    if not time_counts:
        print("No data to plot", file=sys.stderr)
        return

    # 为了图表可读性，可能需要限制数据点数量
    max_points = 100
    if len(time_counts) > max_points:
        # 降采样
        step = len(time_counts) // max_points
        items = list(time_counts.items())
        time_counts = dict(items[::step])

    labels = list(time_counts.keys())
    values = list(time_counts.values())

    plt.figure()
    plt.plotsize(width, height)

    if plot_type == "bar":
        plt.bar(labels, values)
    elif plot_type == "scatter":
        plt.scatter(labels, values)
    else:  # line
        plt.plot(labels, values)

    plt.title(f"Log Trend ({interval})")
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.xticks(rotation=45)

    if export_path:
        plt.save(export_path)
        print(f"Chart saved to {export_path}")
    else:
        plt.show()


def plot_keyword_frequency(
    entries: List[LogEntry],
    keyword: str,
    width: int = 80,
    height: int = 20,
    export_path: Optional[str] = None,
) -> None:
    """绘制关键词频率图"""
    if plt is None:
        print("Error: plotext not installed. Run: pip install plotext", file=sys.stderr)
        return

    from .stats import keyword_frequency
    freq = keyword_frequency(entries, keyword)

    if not freq:
        print(f"No occurrences of keyword '{keyword}' found", file=sys.stderr)
        return

    labels = list(freq.keys())
    values = list(freq.values())

    plt.figure()
    plt.plotsize(width, height)
    plt.plot(labels, values)
    plt.title(f"Keyword Frequency: '{keyword}'")
    plt.xlabel("Time")
    plt.ylabel("Count")
    plt.xticks(rotation=45)

    if export_path:
        plt.save(export_path)
        print(f"Chart saved to {export_path}")
    else:
        plt.show()


def live_monitor(
    filepath: str,
    interval: float = 1.0,
    width: int = 80,
    height: int = 20,
    level: Optional[LogLevel] = None,
) -> None:
    """实时监控模式"""
    if plt is None:
        print("Error: plotext not installed. Run: pip install plotext", file=sys.stderr)
        return

    import time

    print(f"Monitoring {filepath}... Press Ctrl+C to stop")

    last_position = 0

    while True:
        try:
            # 读取新内容
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                last_position = f.tell()

            if new_lines:
                from .parser import parse_line
                new_entries = []
                for i, line in enumerate(new_lines):
                    entry = parse_line(line, line_number=last_position + i)
                    if entry and (level is None or entry.level == level):
                        new_entries.append(entry)

                if new_entries:
                    # 更新图表
                    level_counts = count_by_level(new_entries)
                    labels = list(level_counts.keys())
                    values = list(level_counts.values())

                    plt.clear_figure()
                    plt.plotsize(width, height)
                    plt.bar(labels, values)
                    plt.title(f"Live Log Monitor - {datetime.now().strftime('%H:%M:%S')}")
                    plt.show()
                    plt.sleep(interval)
            else:
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nMonitor stopped.")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            time.sleep(interval)


def generate_plot(
    filepath: str,
    plot_type: str = "bar",
    data_type: str = "level",
    width: int = 80,
    height: int = 20,
    export_path: Optional[str] = None,
    keyword: Optional[str] = None,
    interval: str = "hour",
) -> None:
    """生成图表的便捷函数"""
    entries = list(stream_parse(filepath))

    if data_type == "time":
        plot_time_trend(entries, interval, plot_type, width, height, export_path)
    elif data_type == "keyword" and keyword:
        plot_keyword_frequency(entries, keyword, width, height, export_path)
    else:
        plot_level_distribution(entries, plot_type, width, height, export_path)
