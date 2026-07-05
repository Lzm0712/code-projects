#!/usr/bin/env python3
"""
Simple Python Calculator
Supports: +, -, *, / with parentheses for precedence
"""

import sys
import re
from typing import Union

__version__ = "1.0.0"


class CalculatorError(Exception):
    """Custom exception for calculator errors."""
    pass


def tokenize(expression: str) -> list:
    """
    Tokenize the input expression into numbers and operators.
    """
    # Remove whitespace
    expr = expression.replace(" ", "")
    
    # Pattern to match numbers (including floats) and operators
    pattern = r'(\d+\.?\d*|\+|\-|\*|\/|\(|\))'
    tokens = re.findall(pattern, expr)
    
    # Validate tokens
    for token in tokens:
        if token and not re.match(r'(\d+\.?\d*|\+|\-|\*|\/|\(|\))', token):
            raise CalculatorError(f"Invalid character or token: '{token}'")
    
    return tokens


def parse_number(token: str) -> float:
    """Convert a token to a number."""
    try:
        return float(token)
    except ValueError:
        raise CalculatorError(f"Invalid number: '{token}'")


def evaluate(tokens: list) -> float:
    """
    Evaluate a tokenized expression using a simple recursive descent parser.
    Supports: +, -, *, /, and parentheses for precedence.
    """
    pos = [0]  # Use list to allow modification in nested function
    
    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None
    
    def consume():
        token = tokens[pos[0]]
        pos[0] += 1
        return token
    
    def parse_expression():
        """Parse addition and subtraction (lowest precedence)."""
        result = parse_term()
        while peek() in ('+', '-'):
            op = consume()
            right = parse_term()
            if op == '+':
                result += right
            else:
                result -= right
        return result
    
    def parse_term():
        """Parse multiplication and division (higher precedence)."""
        result = parse_factor()
        while peek() in ('*', '/'):
            op = consume()
            right = parse_factor()
            if op == '*':
                result *= right
            else:
                if right == 0:
                    raise CalculatorError("Division by zero")
                result /= right
        return result
    
    def parse_factor():
        """Parse parentheses or numbers (highest precedence)."""
        token = peek()
        
        if token == '(':
            consume()
            result = parse_expression()
            if peek() != ')':
                raise CalculatorError("Missing closing parenthesis")
            consume()  # consume ')'
            return result
        elif token and re.match(r'-?\d+\.?\d*$', token):
            return parse_number(consume())
        elif token == '-':
            # Handle unary minus
            consume()
            return -parse_factor()
        else:
            if token is None:
                raise CalculatorError("Unexpected end of expression")
            raise CalculatorError(f"Unexpected token: '{token}'")
    
    result = parse_expression()
    
    if pos[0] < len(tokens):
        raise CalculatorError(f"Unexpected token after expression: '{tokens[pos[0]]}'")
    
    return result


def calculate(expression: str) -> Union[float, int]:
    """
    Main entry point: parse and evaluate an expression string.
    Returns an integer if the result is a whole number, otherwise a float.
    """
    if not expression or not expression.strip():
        raise CalculatorError("Empty expression")
    
    tokens = tokenize(expression)
    if not tokens:
        raise CalculatorError("No valid tokens found")
    
    result = evaluate(tokens)
    
    # Return int if whole number
    if result == int(result):
        return int(result)
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python calculator.py \"<expression>\"")
        print("Example: python calculator.py \"2 + 3 * 4\"")
        print("         python calculator.py \"(2 + 3) * 4\"")
        sys.exit(1)
    
    expression = sys.argv[1]
    
    try:
        result = calculate(expression)
        print(f"{expression} = {result}")
    except CalculatorError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
