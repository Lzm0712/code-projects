"""行数统计模块"""

import os
from typing import Dict, Tuple

from .classifier import LineClassifier, is_blank_line
from .languages import get_comment_style


# 大文件阈值: 10MB
LARGE_FILE_THRESHOLD = 10 * 1024 * 1024


def count_file_lines(filepath: str, language: str) -> Tuple[int, int, int]:
    """
    统计单个文件的代码行数

    Returns:
        (total_lines, code_lines, comment_lines) - 总行数、有效代码行数、注释行数
    """
    file_size = os.path.getsize(filepath)

    if file_size > LARGE_FILE_THRESHOLD:
        return count_large_file(filepath, language)
    else:
        return count_small_file(filepath, language)


def count_small_file(filepath: str, language: str) -> Tuple[int, int, int]:
    """统计小文件（直接读取全部内容）"""
    total_lines = 0
    code_lines = 0
    comment_lines = 0

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    classifier = LineClassifier(language)

    for line in lines:
        total_lines += 1
        classification = classifier.classify(line)

        if classification == 'code':
            code_lines += 1
        elif classification == 'comment':
            comment_lines += 1
        # blank 行不计入任何类别

    return total_lines, code_lines, comment_lines


def count_large_file(filepath: str, language: str) -> Tuple[int, int, int]:
    """统计大文件（逐行迭代）"""
    total_lines = 0
    code_lines = 0
    comment_lines = 0

    classifier = LineClassifier(language)

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            total_lines += 1
            classification = classifier.classify(line)

            if classification == 'code':
                code_lines += 1
            elif classification == 'comment':
                comment_lines += 1

    return total_lines, code_lines, comment_lines


def count_directory(root_path: str, verbose: bool = False) -> Dict[str, Dict[str, int]]:
    """
    统计目录中所有代码文件的行数

    Returns:
        {
            'Python': {'files': 5, 'code_lines': 100, 'comment_lines': 20},
            ...
        }
    """
    from .walker import get_code_files

    stats: Dict[str, Dict[str, int]] = {}

    for filepath, language in get_code_files(root_path):
        total, code, comment = count_file_lines(filepath, language)

        if language not in stats:
            stats[language] = {'files': 0, 'code_lines': 0, 'comment_lines': 0}

        stats[language]['files'] += 1
        stats[language]['code_lines'] += code
        stats[language]['comment_lines'] += comment

        if verbose:
            print(f"{filepath}: {code} lines")

    return stats
