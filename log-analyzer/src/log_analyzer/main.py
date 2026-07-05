"""CLI 日志分析工具 - 主入口"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from loguru import logger

from .parser import LogEntry, LogLevel, stream_parse, detect_format
from .filter import LogFilter
from .stats import (
    count_by_level,
    calculate_percentages,
    count_by_time,
    top_n_errors,
    keyword_frequency,
    export_stats_csv,
    export_stats_json,
)
from .plot import (
    plot_level_distribution,
    plot_time_trend,
    plot_keyword_frequency,
    live_monitor,
)

app = typer.Typer(help="CLI 日志分析工具 - 解析、过滤、统计和可视化日志", add_completion=False)

# 全局参数默认值
_DEFAULT_LEVEL = "INFO"


def setup_logging(quiet: bool = False) -> None:
    """配置日志输出"""
    logger.remove()
    if not quiet:
        logger.add(sys.stderr, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>")


def print_log_entry(entry: LogEntry, quiet: bool = False) -> None:
    """打印单个日志条目"""
    ts = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") if entry.timestamp else "N/A"
    level = entry.level.value

    colors = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
    }
    reset = "\033[0m"
    color = colors.get(level, "")

    if quiet:
        print(f"{ts} {level:8s} {entry.message}")
    else:
        print(f"{color}[{ts}] {level:8s} | {entry.message}{reset}")


def load_filter_levels(level_str: Optional[List[str]]) -> Optional[List[LogLevel]]:
    """解析级别过滤参数"""
    if not level_str:
        return None
    levels = LogLevel.from_string_list(level_str)
    return levels if levels else None


def view_impl(
    log_file: Path,
    log_level: str,
    json_output: bool,
    quiet: bool,
    output: Optional[Path],
) -> None:
    """查看日志文件的实现"""
    setup_logging(quiet)

    if not Path(log_file).exists():
        typer.echo(f"Error: File not found: {log_file}", err=True)
        raise typer.Exit(1)

    levels = load_filter_levels([log_level]) if log_level else None

    entries = []
    for entry in stream_parse(str(log_file)):
        if levels and entry.level not in levels:
            continue
        entries.append(entry)

    if json_output:
        result = export_stats_json(entries)
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            typer.echo(f"Output written to {output}")
        else:
            typer.echo(json.dumps(result, indent=2))
    else:
        if not entries:
            typer.echo("No log entries found")
            return

        for entry in entries:
            print_log_entry(entry, quiet)

        if not quiet:
            typer.echo(f"\n--- Total: {len(entries)} entries ---")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    log_file: str = typer.Argument(None, help="日志文件路径"),
    log_level: str = typer.Option(_DEFAULT_LEVEL, "--log-level", help="日志级别过滤"),
    json_output: bool = typer.Option(False, "--json", help="JSON 结构化输出"),
    quiet: bool = typer.Option(False, "--quiet", help="简洁模式"),
    output: Optional[Path] = typer.Option(None, "--output", help="输出文件路径"),
) -> None:
    """CLI 日志分析工具 - 解析、过滤、统计和可视化日志
    
    无子命令时直接查看日志文件。
    """
    ctx.obj = {
        "log_level": log_level,
        "json_output": json_output,
        "quiet": quiet,
        "output": output,
    }
    
    if ctx.invoked_subcommand is None and log_file:
        view_impl(Path(log_file), log_level, json_output, quiet, output)
        raise typer.Exit()


@app.command("view")
def view_command(
    log_file: Path = typer.Argument(..., help="日志文件路径"),
    log_level: str = typer.Option(_DEFAULT_LEVEL, "--log-level", help="日志级别过滤"),
    json_output: bool = typer.Option(False, "--json", help="JSON 结构化输出"),
    quiet: bool = typer.Option(False, "--quiet", help="简洁模式"),
    output: Optional[Path] = typer.Option(None, "--output", help="输出文件路径"),
) -> None:
    """查看日志文件"""
    view_impl(log_file, log_level, json_output, quiet, output)


@app.command("filter")
def filter_command(
    ctx: typer.Context,
    log_file: Path = typer.Argument(..., help="日志文件路径"),
    level: Optional[List[str]] = typer.Option(None, "--level", "-l", help="按级别过滤（可重复）"),
    since: Optional[str] = typer.Option(None, "--since", help="起始时间 (YYYY-MM-DD HH:mm:ss)"),
    until: Optional[str] = typer.Option(None, "--until", help="结束时间 (YYYY-MM-DD HH:mm:ss)"),
    grep: Optional[str] = typer.Option(None, "--grep", help="关键字搜索"),
    regex: Optional[str] = typer.Option(None, "--regex", help="正则表达式搜索"),
    context_after: int = typer.Option(0, "-A", help="匹配后行数"),
    context_before: int = typer.Option(0, "-B", help="匹配前行数"),
    context_total: int = typer.Option(0, "-C", help="上下文行数"),
) -> None:
    """过滤日志条目"""
    params = ctx.parent.obj if ctx.parent and ctx.parent.obj else {}
    setup_logging(params.get("quiet", False))

    if not Path(log_file).exists():
        typer.echo(f"Error: File not found: {log_file}", err=True)
        raise typer.Exit(1)

    # 解析时间
    since_dt = None
    if since:
        try:
            since_dt = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                since_dt = datetime.strptime(since, "%Y-%m-%d")
            except ValueError:
                typer.echo(f"Error: Invalid since format: {since}", err=True)
                raise typer.Exit(1)

    until_dt = None
    if until:
        try:
            until_dt = datetime.strptime(until, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                until_dt = datetime.strptime(until, "%Y-%m-%d")
            except ValueError:
                typer.echo(f"Error: Invalid until format: {until}", err=True)
                raise typer.Exit(1)

    # 解析级别
    levels = load_filter_levels(level) if level else None

    # 创建过滤器
    log_filter = LogFilter(
        filepath=str(log_file),
        levels=levels,
        since=since_dt,
        until=until_dt,
        grep=grep,
        regex=regex,
        context_after=context_after,
        context_before=context_before,
        context_total=context_total,
    )

    entries = list(log_filter.filter())

    json_output_flag = params.get("json_output", False)
    output_path = params.get("output", None)
    quiet = params.get("quiet", False)

    if json_output_flag:
        result = {
            "status": "success",
            "total": len(entries),
            "filters": {
                "level": level,
                "since": since,
                "until": until,
                "grep": grep,
                "regex": regex,
            },
            "logs": [
                {
                    "timestamp": e.timestamp.strftime("%Y-%m-%dT%H:%M:%S") if e.timestamp else None,
                    "level": e.level.value,
                    "message": e.message,
                    "line_number": e.line_number,
                }
                for e in entries
            ],
        }
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            typer.echo(f"Output written to {output_path}")
        else:
            typer.echo(json.dumps(result, indent=2))
    else:
        if not entries:
            typer.echo("No matching entries found")
            return

        for entry in entries:
            print_log_entry(entry, quiet)

        if not quiet:
            typer.echo(f"\n--- Total: {len(entries)} entries ---")


@app.command("stats")
def stats_command(
    ctx: typer.Context,
    log_file: Path = typer.Argument(..., help="日志文件路径"),
    by_level: bool = typer.Option(False, "--by-level", help="按级别统计"),
    by_time: bool = typer.Option(False, "--by-time", help="按时间统计"),
    top: int = typer.Option(10, "--top", help="Top N 错误"),
    keyword: Optional[str] = typer.Option(None, "--keyword", help="关键词频率"),
    interval: str = typer.Option("hour", "--interval", help="时间间隔 (hour/day)"),
) -> None:
    """统计分析"""
    params = ctx.parent.obj if ctx.parent and ctx.parent.obj else {}
    setup_logging(params.get("quiet", False))

    if not Path(log_file).exists():
        typer.echo(f"Error: File not found: {log_file}", err=True)
        raise typer.Exit(1)

    entries = list(stream_parse(str(log_file)))

    result = {"total": len(entries)}

    if by_level:
        level_counts = count_by_level(entries)
        result["level_counts"] = level_counts
        result["level_percentages"] = calculate_percentages(level_counts)

    if by_time:
        result["time_counts"] = count_by_time(entries, interval)

    if top > 0:
        result["top_errors"] = top_n_errors(entries, top)

    if keyword:
        result["keyword_frequency"] = keyword_frequency(entries, keyword)

    result["format"] = detect_format(str(log_file))

    json_output_flag = params.get("json_output", False)
    output_path = params.get("output", None)

    if json_output_flag or output_path:
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            typer.echo(f"Output written to {output_path}")
        else:
            typer.echo(json.dumps(result, indent=2))
    else:
        typer.echo(f"=== Log Statistics ===")
        typer.echo(f"File: {log_file}")
        typer.echo(f"Format: {result['format']}")
        typer.echo(f"Total Entries: {result['total']}")

        if by_level and "level_counts" in result:
            typer.echo(f"\n--- Level Distribution ---")
            for level, count in result["level_counts"].items():
                pct = result["level_percentages"].get(level, 0)
                typer.echo(f"  {level:10s}: {count:6d} ({pct:5.2f}%)")

        if by_time and "time_counts" in result:
            typer.echo(f"\n--- Time Distribution ({interval}) ---")
            for time_key, count in list(result["time_counts"].items())[:20]:
                typer.echo(f"  {time_key}: {count}")

        if top > 0 and "top_errors" in result:
            typer.echo(f"\n--- Top {top} Errors ---")
            for i, err in enumerate(result["top_errors"], 1):
                typer.echo(f"  {i}. [{err['count']:3d}] {err['message'][:60]}")

        if keyword and "keyword_frequency" in result:
            typer.echo(f"\n--- Keyword '{keyword}' Frequency ---")
            for time_key, count in list(result["keyword_frequency"].items())[:10]:
                typer.echo(f"  {time_key}: {count}")


@app.command("plot")
def plot_command(
    ctx: typer.Context,
    log_file: Path = typer.Argument(..., help="日志文件路径"),
    plot_type: str = typer.Option("bar", "--type", help="图表类型 (bar/pie/line)"),
    data_type: str = typer.Option("level", "--data", help="数据类型 (level/time)"),
    live: bool = typer.Option(False, "--live", help="实时监控模式"),
    export: Optional[Path] = typer.Option(None, "--export", help="导出 PNG 路径"),
    width: int = typer.Option(80, "--width", help="图表宽度"),
    height: int = typer.Option(20, "--height", help="图表高度"),
    keyword: Optional[str] = typer.Option(None, "--keyword", help="关键词 (用于频率图)"),
    interval: str = typer.Option("hour", "--interval", help="时间间隔 (hour/day)"),
) -> None:
    """可视化图表"""
    params = ctx.parent.obj if ctx.parent and ctx.parent.obj else {}
    setup_logging(params.get("quiet", False))

    if not Path(log_file).exists():
        typer.echo(f"Error: File not found: {log_file}", err=True)
        raise typer.Exit(1)

    if live:
        live_monitor(str(log_file), width=width, height=height)
        return

    entries = list(stream_parse(str(log_file)))

    if not entries:
        typer.echo("No log entries found")
        return

    if data_type == "time":
        plot_time_trend(entries, interval, plot_type, width, height, str(export) if export else None)
    elif data_type == "keyword" and keyword:
        plot_keyword_frequency(entries, keyword, width, height, str(export) if export else None)
    else:
        plot_level_distribution(entries, plot_type, width, height, str(export) if export else None)


if __name__ == "__main__":
    app()
