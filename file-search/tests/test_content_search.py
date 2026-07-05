"""测试按内容搜索功能"""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsearch import search_by_content


@pytest.fixture
def temp_dir(tmp_path):
    """创建临时测试目录"""
    (tmp_path / "file1.py").write_text("def main():\n    print('hello')")
    (tmp_path / "file2.txt").write_text("just some text")
    (tmp_path / "file3.py").write_text("import re\n\nclass Test:\n    pass")
    
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.py").write_text("def nested_func():\n    return 42")
    
    # 创建二进制文件
    bin_file = tmp_path / "binary.bin"
    bin_file.write_bytes(bytes(range(128, 256)))
    
    return tmp_path


def test_content_search_basic(temp_dir):
    """测试基本内容搜索"""
    results = search_by_content(r"def main", temp_dir, recursive=True, verbose=False)
    assert len(results) == 1
    assert results[0].name == "file1.py"


def test_content_search_multiple_matches(temp_dir):
    """测试多文件匹配"""
    results = search_by_content(r"def ", temp_dir, recursive=True, verbose=False)
    result_names = [p.name for p in results]
    assert "file1.py" in result_names
    # Note: "class Test" line in file3.py contains "def " - nested.py has "def nested_func"
    assert "nested.py" in result_names


def test_content_search_no_match(temp_dir):
    """测试无匹配情况"""
    results = search_by_content(r"THIS_DOES_NOT_EXIST", temp_dir, recursive=True, verbose=False)
    assert len(results) == 0


def test_content_search_recursive(temp_dir):
    """测试递归搜索包含子目录"""
    results = search_by_content(r"nested_func", temp_dir, recursive=True, verbose=False)
    assert len(results) == 1
    assert results[0].name == "nested.py"


def test_content_search_non_recursive(temp_dir):
    """测试非递归搜索"""
    results = search_by_content(r"nested_func", temp_dir, recursive=False, verbose=False)
    assert len(results) == 0  # nested.py is in subdir


def test_content_search_skips_binary(temp_dir):
    """测试跳过二进制文件"""
    results = search_by_content(r".", temp_dir, recursive=True, verbose=False)
    result_names = [p.name for p in results]
    assert "binary.bin" not in result_names


def test_content_search_import_statement(temp_dir):
    """测试搜索 import 语句"""
    results = search_by_content(r"import re", temp_dir, recursive=True, verbose=False)
    assert len(results) == 1
    assert results[0].name == "file3.py"
