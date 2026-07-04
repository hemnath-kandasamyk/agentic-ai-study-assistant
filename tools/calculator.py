import ast
import operator
from typing import Any

from langchain.tools import tool

from logging_config import get_logger

logger = get_logger()

_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate(node: ast.AST) -> float | int:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        return _BINARY_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate(node.operand))

    raise ValueError("Only normal arithmetic is allowed.")


@tool
def calculator(expression: str) -> str:
    """Safely calculate a basic arithmetic expression.

    Supports: +, -, *, /, //, %, **, parentheses, integers, and decimals.
    Example: '(25 * 17) / 5'
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result: Any = _evaluate(tree)
        logger.info("TOOL calculator | expression=%r | result=%r", expression, result)
        return f"Result: {result}"
    except ZeroDivisionError:
        logger.warning("TOOL calculator failed | division by zero | expression=%r", expression)
        return "Calculator error: division by zero is not allowed."
    except (SyntaxError, ValueError, TypeError) as exc:
        logger.warning("TOOL calculator failed | expression=%r | error=%s", expression, exc)
        return f"Calculator error: {exc}"
