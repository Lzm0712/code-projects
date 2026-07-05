"""测试按类型搜索功能"""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fsearch import search_by_type


def test_type_search_single_extension(tmp_path):
    """测试单扩展名搜索"""
    (tmp_path / "file1.py").write_text("python code")
    (tmp_path / "file2.txt").write_text("text content")
    (tmp_path / "file3.md").write_text("# markdown")
    (tmp_path / "file4.py").write_text("more python")
    
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.py").write_text("nested python")
    (sub_dir / "nested.js").write_text("javascript")
    
    results = search_by_type("py", tmp_path, recursive=True, verbose=False)
    result_names = [p.name for p in results]
    assert "file1.py" in result_names
    assert "file4.py" in result_names
    assert "nested.py" in result_names


def test_type_search_multiple_extensions(tmp_path):
    """测试多扩展名搜索"""
    (tmp_path / "file1.py").write_text("python code")
    (tmp_path / "file2.txt").write_text("text content")
    (tmp_path / "file3.md").write_text("# markdown")
    (tmp_path / "file4.py").write_text("more python")
    
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.py").write_text("nested python")
    (sub_dir / "nested.js").write_text("javascript")
    
    results = search_by_type("py,txt", tmp_path, recursive=True, verbose=False)
    result_names = [p.name for p in results]
    assert "file1.py" in result_names
    assert "file2.txt" in result_names
    assert "file4.py" in result_names
    assert "nested.py" in result_names


def test_type_search_no_match(tmp_path):
    """测试无匹配情况"""
    (tmp_path / "file1.py").write_text("python code")
    
    results = search_by_type("xyz", tmp_path, recursive=True, verbose=False)
    assert len(results) == 0


def test_type_search_recursive(tmp_path):
    """测试递归搜索"""
    (tmp_path / "file1.py").write_text("python code")
    (tmp_path / "file4.py").write_text("more python")
    
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.py").write_text("nested python")
    
    results = search_by_type("py", tmp_path, recursive=True, verbose=False)
    assert len(results) == 3  # file1.py, file4.py, nested.py


def test_type_search_non_recursive(tmp_path):
    """测试非递归搜索"""
    (tmp_path / "file1.py").write_text("python code")
    (tmp_path / "file4.py").write_text("more python")
    
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.py").write_text("nested python")
    
    results = search_by_type("py", tmp_path, recursive=False, verbose=False)
    result_names = [p.name for p in results]
    assert "file1.py" in result_names
    assert "file4.py" in result_names
    assert "nested.py" not in result_names  # in subdir


def test_type_search_with_dot_prefix(tmp_path):
    """测试带点扩展名前缀"""
    (tmp_path / "file1.py").write_text("python code")
    (tmp_path / "file2.py").write_text("more python")
    
    sub_dir = tmp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.py").write_text("nested python")
    
    results = search_by_type(".py", tmp_path, recursive=True, verbose=False)
    assert len(results) == 3


def test_type_search_space_handling(tmp_path):
    """测试空格处理"""
    (tmp_path / "file1.py").write_text("python code")
    (tmp_path / "file2.txt").write_text("text content")
    
    results = search_by_type(" py , txt ", tmp_path, recursive=True, verbose=False)
    assert len(results) >= 2
