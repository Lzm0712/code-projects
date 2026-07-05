"""
Unit tests for the Calculator
"""

import pytest
from calculator import calculate, CalculatorError


class TestBasicOperations:
    """Test basic arithmetic operations."""
    
    def test_addition(self):
        assert calculate("2 + 3") == 5
    
    def test_subtraction(self):
        assert calculate("5 - 3") == 2
    
    def test_multiplication(self):
        assert calculate("4 * 3") == 12
    
    def test_division(self):
        assert calculate("10 / 2") == 5
    
    def test_multiple_operations(self):
        assert calculate("1 + 2 + 3") == 6
        assert calculate("10 - 3 - 2") == 5
        assert calculate("2 * 3 * 4") == 24
        assert calculate("24 / 3 / 2") == 4


class TestPrecedence:
    """Test operator precedence (* / before + -)."""
    
    def test_multiplication_before_addition(self):
        assert calculate("2 + 3 * 4") == 14  # 2 + 12 = 14
    
    def test_division_before_subtraction(self):
        assert calculate("10 - 6 / 2") == 7  # 10 - 3 = 7
    
    def test_left_to_right_same_precedence(self):
        assert calculate("12 / 3 * 2") == 8   # 4 * 2 = 8
        assert calculate("10 - 3 + 2") == 9   # 7 + 2 = 9


class TestParentheses:
    """Test parentheses for grouping."""
    
    def test_simple_parentheses(self):
        assert calculate("(2 + 3) * 4") == 20
    
    def test_nested_parentheses(self):
        assert calculate("((2 + 3))") == 5
    
    def test_parentheses_override_precedence(self):
        assert calculate("(2 + 3) * (4 + 1)") == 25
    
    def test_complex_expression(self):
        assert calculate("2 * (3 + 4) - 6 / 2") == 11  # 2*7 - 3 = 11


class TestFloats:
    """Test floating point numbers."""
    
    def test_float_division(self):
        assert calculate("7 / 2") == 3.5
    
    def test_float_numbers(self):
        assert calculate("2.5 + 3.5") == 6.0
        assert calculate("3.14 * 2") == 6.28


class TestNegativeNumbers:
    """Test negative numbers."""
    
    def test_negative_result(self):
        assert calculate("3 - 8") == -5
    
    def test_unary_minus(self):
        assert calculate("-5 + 3") == -2
        assert calculate("-2 * -3") == 6


class TestEdgeCases:
    """Test edge cases."""
    
    def test_single_number(self):
        assert calculate("42") == 42
    
    def test_zero(self):
        assert calculate("0") == 0
        assert calculate("0 + 0") == 0
    
    def test_whole_number_result(self):
        assert calculate("10 / 2") == 5  # Should return int, not float


class TestErrors:
    """Test error handling."""
    
    def test_division_by_zero(self):
        with pytest.raises(CalculatorError, match="Division by zero"):
            calculate("1 / 0")
    
    def test_empty_expression(self):
        with pytest.raises(CalculatorError, match="Empty expression"):
            calculate("")
    
    def test_whitespace_only(self):
        with pytest.raises(CalculatorError, match="Empty expression"):
            calculate("   ")
    
    def test_missing_parenthesis(self):
        with pytest.raises(CalculatorError, match="Missing closing parenthesis"):
            calculate("(2 + 3")
    
    def test_extra_parenthesis(self):
        with pytest.raises(CalculatorError, match="Unexpected token"):
            calculate("2 + 3)")
    
    def test_invalid_character(self):
        with pytest.raises(CalculatorError, match="Unexpected token"):
            calculate("2 & 3")
    
    def test_invalid_number(self):
        with pytest.raises(CalculatorError, match="No valid tokens found"):
            calculate("abc")
    
    def test_empty_parentheses(self):
        with pytest.raises(CalculatorError, match="Unexpected token"):
            calculate("()")


class TestMainIntegration:
    """Integration test simulating command-line usage."""
    
    def test_cli_example(self):
        result = calculate("(2 + 3) * 4")
        assert result == 20
