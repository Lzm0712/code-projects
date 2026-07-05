"""os.walk 遍历模块"""

import os
from typing import Iterator, Tuple

from .languages import get_language, SKIP_DIRS


def walk_directory(root_path: str) -> Iterator[Tuple[str, list, list]]:
    """
    递归遍历目录，跳过隐藏目录和常见非源码目录

    Args:
        root_path: 根目录路径

    Yields:
        (dirpath, dirnames, filenames) - 与 os.walk 相同
    """
    for dirpath, dirnames, filenames in os.walk(root_path):
        # 过滤需要跳过的目录（原地修改 dirnames）
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.startswith('.')
        ]

        yield dirpath, dirnames, filenames


def get_code_files(root_path: str) -> Iterator[Tuple[str, str]]:
    """
    获取所有代码文件

    Args:
        root_path: 根目录路径

    Yields:
        (filepath, language) - 文件路径和语言类型
    """
    for dirpath, _, filenames in walk_directory(root_path):
        for filename in filenames:
            language = get_language(filename)
            if language:
                filepath = os.path.join(dirpath, filename)
                yield filepath, language
