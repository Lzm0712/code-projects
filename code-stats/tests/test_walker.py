"""测试目录遍历模块"""

import os
import tempfile
import pytest
from src.walker import walk_directory, get_code_files
from src.languages import get_language, SKIP_DIRS


class TestGetLanguage:
    """测试语言识别"""

    def test_python(self):
        assert get_language('test.py') == 'Python'
        assert get_language('module.py') == 'Python'

    def test_javascript(self):
        assert get_language('app.js') == 'JavaScript'

    def test_typescript(self):
        assert get_language('app.ts') == 'TypeScript'

    def test_go(self):
        assert get_language('main.go') == 'Go'

    def test_rust(self):
        assert get_language('lib.rs') == 'Rust'

    def test_yaml(self):
        assert get_language('config.yaml') == 'YAML'
        assert get_language('config.yml') == 'YAML'

    def test_markdown(self):
        assert get_language('README.md') == 'Markdown'

    def test_json(self):
        assert get_language('package.json') == 'JSON'

    def test_unknown(self):
        assert get_language('test.txt') is None
        assert get_language('image.png') is None
        assert get_language('executable') is None


class TestWalkDirectory:
    """测试目录遍历"""

    def test_walk_basic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建文件
            file1 = os.path.join(tmpdir, 'test.py')
            with open(file1, 'w') as f:
                f.write('pass\n')

            subdir = os.path.join(tmpdir, 'subdir')
            os.makedirs(subdir)
            file2 = os.path.join(subdir, 'test.js')
            with open(file2, 'w') as f:
                f.write('// test\n')

            paths = list(walk_directory(tmpdir))
            # 应该包含根目录和子目录
            assert len(paths) >= 2

    def test_skip_hidden_dirs(self):
        """测试跳过隐藏目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 .git 目录
            git_dir = os.path.join(tmpdir, '.git')
            os.makedirs(git_dir)
            with open(os.path.join(git_dir, 'config'), 'w') as f:
                f.write('test\n')

            # 创建正常目录
            normal_dir = os.path.join(tmpdir, 'src')
            os.makedirs(normal_dir)
            with open(os.path.join(normal_dir, 'test.py'), 'w') as f:
                f.write('pass\n')

            paths = list(walk_directory(tmpdir))
            path_strs = [str(p[0]) for p in paths]

            # 不应该包含 .git 路径
            assert not any('.git' in p for p in path_strs)


class TestGetCodeFiles:
    """测试代码文件获取"""

    def test_get_code_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建代码文件
            py_file = os.path.join(tmpdir, 'test.py')
            with open(py_file, 'w') as f:
                f.write('def foo():\n')

            js_file = os.path.join(tmpdir, 'app.js')
            with open(js_file, 'w') as f:
                f.write('const x = 1;\n')

            # 创建非代码文件
            txt_file = os.path.join(tmpdir, 'readme.txt')
            with open(txt_file, 'w') as f:
                f.write('This is text\n')

            files = list(get_code_files(tmpdir))

            # 应该只包含 .py 和 .js 文件
            assert len(files) == 2
            paths, langs = zip(*files)
            assert 'Python' in langs
            assert 'JavaScript' in langs

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            files = list(get_code_files(tmpdir))
            assert len(files) == 0


class TestSkipDirs:
    """测试跳过的目录集合"""

    def test_skip_dirs_contains_expected(self):
        expected = {'.git', 'node_modules', '__pycache__', 'venv', 'env'}
        for d in expected:
            assert d in SKIP_DIRS
