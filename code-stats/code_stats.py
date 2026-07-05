#!/usr/bin/env python3
"""
代码行数统计工具

统计指定目录中代码文件的行数，按编程语言分类，支持跳过空行和注释行
"""

import argparse
import sys
from typing import Dict

from src.counter import count_directory


def format_stats(stats: Dict[str, Dict[str, int]]) -> str:
    """格式化统计输出"""
    lines = []
    lines.append(f"{'Language':<15} {'Files':>6} {'Lines':>8}")
    lines.append('-' * 33)

    total_files = 0
    total_lines = 0

    # 按语言名称排序输出
    for lang in sorted(stats.keys()):
        data = stats[lang]
        file_count = data['files']
        code_lines = data['code_lines']
        lines.append(f"{lang:<15} {file_count:>6} {code_lines:>8}")
        total_files += file_count
        total_lines += code_lines

    lines.append('-' * 33)
    lines.append(f"{'Total':<15} {total_files:>6} {total_lines:>8}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='统计代码文件的行数，按语言分类',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python code_stats.py ./src
  python code_stats.py ./src --verbose
  python code_stats.py /path/to/project --verbose
        """
    )

    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='要统计的代码目录（默认: 当前目录）'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细输出（每个文件的行数）'
    )

    args = parser.parse_args()

    # 检查目录是否存在
    import os
    if not os.path.isdir(args.directory):
        print(f"错误: 目录不存在或不是有效目录: {args.directory}", file=sys.stderr)
        sys.exit(1)

    # 统计并输出
    try:
        stats = count_directory(args.directory, verbose=args.verbose)
        output = format_stats(stats)
        print(output)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
