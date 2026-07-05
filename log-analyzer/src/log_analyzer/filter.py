"""日志过滤逻辑"""

import re
from datetime import datetime
from typing import List, Optional, Iterator

from .parser import LogEntry, LogLevel, stream_parse


class LogFilter:
    """日志过滤器"""

    def __init__(
        self,
        filepath: str,
        levels: Optional[List[LogLevel]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        grep: Optional[str] = None,
        regex: Optional[str] = None,
        context_after: int = 0,
        context_before: int = 0,
        context_total: int = 0,
    ):
        self.filepath = filepath
        self.levels = levels
        self.since = since
        self.until = until
        self.grep = grep.lower() if grep else None
        self.regex = re.compile(regex) if regex else None
        self.context_after = context_after
        self.context_before = context_before
        self.context_total = context_total

        # 上下文行缓冲
        self.context_buffer: List[LogEntry] = []
        self.context_buffer_index = 0

    def _matches_criteria(self, entry: LogEntry) -> bool:
        """检查条目是否匹配过滤条件"""
        # 级别过滤
        if self.levels and entry.level not in self.levels:
            return False

        # 时间范围过滤
        if self.since and entry.timestamp and entry.timestamp < self.since:
            return False
        if self.until and entry.timestamp and entry.timestamp > self.until:
            return False
        if self.until and entry.timestamp and entry.timestamp == self.until:
            return False

        # 关键字搜索
        if self.grep and self.grep not in entry.message.lower():
            return False

        # 正则表达式搜索
        if self.regex and not self.regex.search(entry.message):
            return False

        return True

    def _should_output(self, entry: LogEntry) -> bool:
        """检查条目是否应该输出（考虑上下文）"""
        if self.context_total > 0:
            # 上下文模式：输出匹配项及其前后若干行
            if self._matches_criteria(entry):
                self.context_buffer_index = len(self.context_buffer)
            self.context_buffer.append(entry)

            # 保持缓冲区大小
            max_context = self.context_total
            if len(self.context_buffer) > max_context * 2 + 1:
                # 移除最老的条目
                remove_count = len(self.context_buffer) - (max_context * 2 + 1)
                self.context_buffer = self.context_buffer[remove_count:]

            # 检查当前条目是否在上下文范围内
            if self.context_buffer_index > 0:
                # 之前有匹配项，检查当前是否在上下文中
                match_pos = self.context_buffer_index
                current_pos = len(self.context_buffer) - 1
                if current_pos - match_pos <= max_context:
                    return True
            elif self.context_buffer_index == 0 and len(self.context_buffer) > 0:
                # 当前缓冲区最后一个是匹配项
                if len(self.context_buffer) == 1:
                    return True
                # 检查是否有新的匹配
                for i, e in enumerate(self.context_buffer[:-1]):
                    if self._matches_criteria(e):
                        self.context_buffer_index = i
                        break

            return False
        else:
            # 非上下文模式：严格匹配
            return self._matches_criteria(entry)

    def filter(self) -> Iterator[LogEntry]:
        """执行过滤，返回匹配的日志条目"""
        for entry in stream_parse(self.filepath):
            if self._should_output(entry):
                yield entry

    def filter_all(self) -> List[LogEntry]:
        """返回所有匹配的日志条目"""
        return list(self.filter())

    def get_context_entries(self) -> List[LogEntry]:
        """获取上下文缓冲区的所有条目（用于上下文模式）"""
        return self.context_buffer.copy()


def filter_logs(
    filepath: str,
    levels: Optional[List[LogLevel]] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    grep: Optional[str] = None,
    regex: Optional[str] = None,
    context_after: int = 0,
    context_before: int = 0,
    context_total: int = 0,
) -> List[LogEntry]:
    """便捷过滤函数"""
    f = LogFilter(
        filepath=filepath,
        levels=levels,
        since=since,
        until=until,
        grep=grep,
        regex=regex,
        context_after=context_after,
        context_before=context_before,
        context_total=context_total,
    )
    return f.filter_all()
