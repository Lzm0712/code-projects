"""注释/空行分类器 - 使用状态机追踪多行注释"""

import re
from typing import List, Optional


class LineClassifier:
    """单文件内行的分类器，使用状态机处理多行注释"""

    def __init__(self, language: str):
        self.language = language
        self.in_block_comment = False
        self.block_end_patterns: List[re.Pattern] = []
        self._setup_patterns()

    def _setup_patterns(self):
        """根据语言设置注释模式"""
        if self.language == 'Python':
            # Python 多行注释: """ 或 '''
            self.block_end_patterns = [
                re.compile(r'"""'),
                re.compile(r"'''"),
            ]
        elif self.language in ('JavaScript', 'TypeScript', 'Go', 'Rust'):
            # /* ... */ 块注释
            self.block_end_patterns = [re.compile(r'\*/')]
        elif self.language == 'Markdown':
            # <!-- ... --> 块注释
            self.block_end_patterns = [re.compile(r'-->')]

    def _find_inline_comment(self, line: str) -> Optional[int]:
        """
        查找内联注释的起始位置
        Returns the index of comment start, or None if no inline comment
        """
        stripped = line.strip()

        if self.language == 'Python':
            # 查找 # 并排除字符串内的 #
            # 简单策略：从右往左找 #，但要排除引号内的
            return self._find_python_inline_comment(line)
        elif self.language in ('JavaScript', 'TypeScript', 'Go', 'Rust'):
            # 查找 // 并排除字符串内的
            return self._find_cStyle_inline_comment(line, '//')
        elif self.language == 'YAML':
            return self._find_cStyle_inline_comment(line, '#')
        elif self.language == 'Markdown':
            return self._find_cStyle_inline_comment(line, '#')
        return None

    def _find_python_inline_comment(self, line: str) -> Optional[int]:
        """查找 Python 内联注释位置"""
        quote_count = 0
        in_string = False
        string_char = None

        i = 0
        while i < len(line):
            char = line[i]

            if not in_string:
                if char in ('"', "'"):
                    in_string = True
                    string_char = char
                    # 检查三引号
                    if i + 2 < len(line) and line[i:i+3] in ('"""', "'''"):
                        i += 3
                        continue
                elif char == '#':
                    return i
            else:
                if char == string_char and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                    string_char = None
            i += 1

        return None

    def _find_cStyle_inline_comment(self, line: str, comment_marker: str) -> Optional[int]:
        """查找 C 风格内联注释位置（// 或 #）"""
        in_string = False
        i = 0
        while i < len(line):
            char = line[i]

            if not in_string:
                if char == '"':
                    in_string = True
                elif char == "'":
                    in_string = True
                elif i + 1 < len(line) and line[i:i+2] == comment_marker:
                    return i
            else:
                if char == '"' and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                elif char == "'" and (i == 0 or line[i-1] != '\\'):
                    in_string = False

            i += 1

        return None

    def _is_single_line_comment(self, line: str) -> bool:
        """判断是否整行都是单行注释"""
        stripped = line.strip()
        if not stripped:
            return False

        if self.language == 'Python':
            return stripped.startswith('#')
        elif self.language in ('JavaScript', 'TypeScript', 'Go', 'Rust'):
            return stripped.startswith('//')
        elif self.language == 'YAML':
            return stripped.startswith('#')
        elif self.language == 'Markdown':
            return stripped.startswith('#')
        elif self.language == 'JSON':
            return False
        return False

    def _block_starts(self, line: str) -> bool:
        """检测块注释开始"""
        if self.language == 'Python':
            stripped = line.strip()
            # 只有当 """ 或 ''' 独立出现（不在字符串赋值中）时才认为是 docstring
            # 简化处理：如果行首是 """ 或 ''' 则认为是块注释开始
            if stripped.startswith('"""') or stripped.startswith("'''"):
                return True
            return False
        elif self.language in ('JavaScript', 'TypeScript', 'Go', 'Rust'):
            stripped = line.strip()
            return '/*' in stripped
        elif self.language == 'Markdown':
            return '<!--' in line
        return False

    def _block_ends(self, line: str) -> bool:
        """检测块注释结束"""
        if not self.in_block_comment:
            return False

        for pattern in self.block_end_patterns:
            if pattern.search(line):
                return True
        return False

    def _is_single_line_block_comment(self, line: str) -> bool:
        """检测单行块注释（开始和结束在同一行）"""
        if self.language == 'Python':
            stripped = line.strip()
            # 单独的 """ 或 ''' 行
            if stripped == '"""' or stripped == "'''":
                return True
        elif self.language in ('JavaScript', 'TypeScript', 'Go', 'Rust'):
            stripped = line.strip()
            # 单独的 /* ... */ 行
            if stripped.startswith('/*') and '*/' in stripped:
                return True
        elif self.language == 'Markdown':
            stripped = line.strip()
            if stripped.startswith('<!--') and '-->' in stripped:
                return True
        return False

    def classify(self, line: str) -> str:
        """分类单行：'code', 'comment', 'blank'"""
        stripped = line.strip()

        # 空行判断
        if is_blank_line(line):
            return 'blank'

        # 单行块注释（开始和结束在同一行）
        if self._is_single_line_block_comment(line):
            return 'comment'

        # 处理块注释状态
        if self.in_block_comment:
            if self._block_ends(line):
                self.in_block_comment = False
            return 'comment'

        # 检测块注释开始
        if self._block_starts(line):
            self.in_block_comment = True
            return 'comment'

        # 检查内联注释
        comment_pos = self._find_inline_comment(line)
        if comment_pos is not None:
            # 检查是否整行都是注释
            stripped_pos = len(line) - len(line.lstrip())
            if stripped_pos >= comment_pos:
                # 注释在行首或缩进后
                return 'comment'
            else:
                # 内联注释，返回 code（行中代码部分）
                return 'code'

        # 单行注释（整行）
        if self._is_single_line_comment(line):
            return 'comment'

        return 'code'


def is_blank_line(line: str) -> bool:
    """判断是否为空行"""
    return line.strip() == ''
