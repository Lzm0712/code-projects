"""测试注释/空行分类器"""

import pytest
from src.classifier import LineClassifier, is_blank_line


class TestIsBlankLine:
    def test_empty_string(self):
        assert is_blank_line('') is True

    def test_whitespace_only(self):
        assert is_blank_line('   \t\n') is True

    def test_newline_only(self):
        assert is_blank_line('\n') is True

    def test_with_content(self):
        assert is_blank_line('print("hello")') is False

    def test_indent_only(self):
        assert is_blank_line('    ') is True


class TestLineClassifierPython:
    """测试 Python 代码分类"""

    def test_single_line_comment(self):
        clf = LineClassifier('Python')
        assert clf.classify('# comment') == 'comment'
        assert clf.classify('  # indented comment') == 'comment'
        # 内联注释行算作 code（因为有有效代码）
        assert clf.classify('code # inline comment') == 'code'

    def test_code_line(self):
        clf = LineClassifier('Python')
        assert clf.classify('def foo():') == 'code'
        assert clf.classify('    def foo():') == 'code'
        assert clf.classify('x = 1 + 2') == 'code'

    def test_blank_line(self):
        clf = LineClassifier('Python')
        assert clf.classify('') == 'blank'
        assert clf.classify('   ') == 'blank'

    def test_docstring_double_quote(self):
        clf = LineClassifier('Python')
        assert clf.classify('"""docstring"""') == 'comment'
        assert clf.classify('"""multi\nline\ndocstring"""') == 'comment'
        assert clf.classify('x = """string"""') == 'code'

    def test_docstring_single_quote(self):
        clf = LineClassifier('Python')
        assert clf.classify("'''docstring'''") == 'comment'
        assert clf.classify("'''multi\nline\ndocstring'''") == 'comment'

    def test_multi_line_docstring(self):
        clf = LineClassifier('Python')
        # Start of docstring
        assert clf.classify('"""Start') == 'comment'
        # Middle of docstring (simulate continuation by re-creating classifier)
        clf2 = LineClassifier('Python')
        clf2.in_block_comment = True
        assert clf2.classify('middle line') == 'comment'
        # End of docstring
        clf3 = LineClassifier('Python')
        clf3.in_block_comment = True
        assert clf3.classify('""" end') == 'comment'


class TestLineClassifierJavaScript:
    """测试 JavaScript 代码分类"""

    def test_single_line_comment(self):
        clf = LineClassifier('JavaScript')
        assert clf.classify('// comment') == 'comment'
        assert clf.classify('  // indented') == 'comment'
        # 内联注释行算作 code
        assert clf.classify('const x = 1; // inline comment') == 'code'

    def test_code_line(self):
        clf = LineClassifier('JavaScript')
        assert clf.classify('function foo() {') == 'code'
        assert clf.classify('const x = 1;') == 'code'

    def test_block_comment(self):
        clf = LineClassifier('JavaScript')
        assert clf.classify('/* block comment */') == 'comment'
        assert clf.classify('/* multi\nline\ncomment */') == 'comment'


class TestLineClassifierGo:
    """测试 Go 代码分类"""

    def test_single_line_comment(self):
        clf = LineClassifier('Go')
        assert clf.classify('// comment') == 'comment'

    def test_code_line(self):
        clf = LineClassifier('Go')
        assert clf.classify('func main() {') == 'code'
        assert clf.classify('fmt.Println("hello")') == 'code'


class TestLineClassifierYAML:
    """测试 YAML 代码分类"""

    def test_single_line_comment(self):
        clf = LineClassifier('YAML')
        assert clf.classify('# comment') == 'comment'

    def test_code_line(self):
        clf = LineClassifier('YAML')
        assert clf.classify('key: value') == 'code'
        assert clf.classify('  nested: true') == 'code'


class TestLineClassifierMarkdown:
    """测试 Markdown 代码分类"""

    def test_heading(self):
        clf = LineClassifier('Markdown')
        # # at start is heading, but we classify as comment
        assert clf.classify('# Heading') == 'comment'

    def test_code_block(self):
        clf = LineClassifier('Markdown')
        assert clf.classify('```python') == 'code'

    def test_html_comment(self):
        clf = LineClassifier('Markdown')
        assert clf.classify('<!-- comment -->') == 'comment'


class TestLineClassifierJSON:
    """测试 JSON 代码分类"""

    def test_code_lines(self):
        clf = LineClassifier('JSON')
        assert clf.classify('{"key": "value"}') == 'code'
        assert clf.classify('[1, 2, 3]') == 'code'
        # No comment support
