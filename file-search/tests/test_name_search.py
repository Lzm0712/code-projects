"""测试按名称搜索功能"""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsearch import search_by_name, is_binary_file


@pytest.fixture
def temp_dir(tmp_path):
    """创建临时测试目录"""
    # 创建测试文件
    (tmp_path / "test_file.py").write_text("print('hello')")
    (tmp_path / "another_file.txt").write_text("text content")
    (tmp_path / "script.js").write_text("console.log('js')")
    (tmp_path / ".hidden_file").write_text("hidden")
    
    # 创建子目录
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.py").write_text("nested python")
    
    return tmp_path


def test_name_search_basic(temp_dir):
    """测试基本文件名搜索"""
    results = search_by_name(r"test_file\.py", temp_dir, recursive=True, verbose=False)
    result_names = [p.name for p in results]
    assert "test_file.py" in result_names


def test_name_search_regex(temp_dir):
    """测试正则表达式匹配"""
    results = search_by_name(r"\.py$", temp_dir, recursive=True, verbose=False)
    result_names = [p.name for p in results]
    assert "test_file.py" in result_names
    assert "nested.py" in result_names


def test_name_search_no_match(temp_dir):
    """测试无匹配情况"""
    results = search_by_name(r"nonexistent", temp_dir, recursive=True, verbose=False)
    assert len(results) == 0


def test_name_search_recursive(temp_dir):
    """测试递归搜索"""
    results = search_by_name(r"\.py$", temp_dir, recursive=True, verbose=False)
    assert len(results) == 2  # test_file.py and nested.py


def test_name_search_non_recursive(temp_dir):
    """测试非递归搜索"""
    results = search_by_name(r"\.py$", temp_dir, recursive=False, verbose=False)
    result_names = [p.name for p in results]
    assert "test_file.py" in result_names
    assert "nested.py" not in result_names  # in subdir


def test_name_search_hidden_files(temp_dir):
    """测试隐藏文件包含"""
    results = search_by_name(r"hidden", temp_dir, recursive=True, verbose=False)
    assert len(results) == 1
    assert results[0].name == ".hidden_file"


def test_is_binary_file():
    """测试二进制文件判断"""
    # 创建临时文本文件和二进制文件
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("text content")
        text_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
        f.write(bytes(range(128, 140)))
        bin_file = f.name
    
    try:
        assert not is_binary_file(Path(text_file))
        assert is_binary_file(Path(bin_file))
    finally:
        os.unlink(text_file)
        os.unlink(bin_file)
