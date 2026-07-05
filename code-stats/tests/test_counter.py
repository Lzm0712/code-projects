"""测试行数统计模块"""

import os
import tempfile
import pytest
from src.counter import count_file_lines, count_directory
from src.classifier import is_blank_line


class TestCountFileLines:
    """测试单文件行数统计"""

    def test_python_file(self):
        # 创建临时 Python 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def foo():\n')
            f.write('    # comment\n')
            f.write('    pass\n')
            f.write('\n')
            f.write('x = 1\n')
            temp_path = f.name

        try:
            total, code, comment = count_file_lines(temp_path, 'Python')
            assert total == 5
            # def foo(), pass, x = 1 是有效代码行
            assert code == 3
            # # comment 是注释行
            assert comment == 1
        finally:
            os.unlink(temp_path)

    def test_javascript_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write('// comment\n')
            f.write('function foo() {\n')
            f.write('  /* block */\n')
            f.write('  return 1;\n')
            f.write('}\n')
            temp_path = f.name

        try:
            total, code, comment = count_file_lines(temp_path, 'JavaScript')
            assert total == 5
            # function foo(), return 1, } 是有效代码行
            assert code == 3
            # // comment 和 /* block */ 是注释行
            assert comment == 2
        finally:
            os.unlink(temp_path)

    def test_yaml_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('# comment\n')
            f.write('key: value\n')
            f.write('  nested: true\n')
            temp_path = f.name

        try:
            total, code, comment = count_file_lines(temp_path, 'YAML')
            assert total == 3
            assert code == 2  # key: value 和 nested: true
            assert comment == 1
        finally:
            os.unlink(temp_path)

    def test_json_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"key": "value"}\n')
            f.write('[1, 2, 3]\n')
            temp_path = f.name

        try:
            total, code, comment = count_file_lines(temp_path, 'JSON')
            assert total == 2
            assert code == 2
            assert comment == 0
        finally:
            os.unlink(temp_path)


class TestCountDirectory:
    """测试目录统计"""

    def test_count_directory(self):
        # 创建临时目录结构
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 Python 文件
            py_file = os.path.join(tmpdir, 'test.py')
            with open(py_file, 'w') as f:
                f.write('def foo():\n')
                f.write('    pass\n')

            # 创建 JS 文件
            js_file = os.path.join(tmpdir, 'test.js')
            with open(js_file, 'w') as f:
                f.write('// comment\n')
                f.write('const x = 1;\n')

            # 统计
            stats = count_directory(tmpdir)

            assert 'Python' in stats
            assert 'JavaScript' in stats
            assert stats['Python']['files'] == 1
            assert stats['JavaScript']['files'] == 1

    def test_skip_hidden_dirs(self):
        """测试跳过隐藏目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 .git 目录
            git_dir = os.path.join(tmpdir, '.git')
            os.makedirs(git_dir)
            py_file = os.path.join(git_dir, 'test.py')
            with open(py_file, 'w') as f:
                f.write('def foo():\n')

            # 创建正常文件
            normal_file = os.path.join(tmpdir, 'normal.py')
            with open(normal_file, 'w') as f:
                f.write('def bar():\n')

            stats = count_directory(tmpdir)
            # 应该只统计到 normal.py，不统计 .git/test.py
            assert stats['Python']['files'] == 1


class TestIsBlankLine:
    """测试空行判断"""

    def test_blank_lines(self):
        assert is_blank_line('') is True
        assert is_blank_line('   ') is True
        assert is_blank_line('\t') is True
        assert is_blank_line('\n') is True

    def test_non_blank_lines(self):
        assert is_blank_line('code') is False
        assert is_blank_line(' # comment') is False
