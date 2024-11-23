import re
from jsonpath_rw_ext import parse as jsonpath_parse
import json
from typing import Any, Dict


class ConditionEvaluator:
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        print(f"Initialized ConditionEvaluator with context: {json.dumps(self.context)}")

    def evaluate(self, condition: str, context: str = None, condition_type: str = 'simple') -> bool:
        if condition_type == 'simple':
            return self._evaluate_simple(condition)
        elif condition_type == 'regex':
            resolved_context = self._resolve_context(context)
            return self._evaluate_regex(condition, resolved_context)
        elif condition_type == 'jsonpath':
            resolved_context = self._resolve_context(context)
            return self._evaluate_jsonpath(condition, resolved_context)
        elif condition_type == 'xpath':
            resolved_context = self._resolve_context(context)
            return self._evaluate_xpath(condition, resolved_context)
        return False

    def _evaluate_simple(self, condition: str) -> Any:
        # Check if it's a simple path resolution (e.g., "$steps.loginStep.outputs.sessionToken")
        if self._is_simple_path(condition):
            return self._resolve_context(condition)

        # Otherwise, assume it's a comparison and evaluate it
        left_expr, operator, right_expr = self._parse_comparison(condition)
        return self._evaluate_comparison(left_expr, operator, right_expr)

    def _is_simple_path(self, condition: str) -> bool:
        """Checks if the condition is just a simple path without operators."""
        return re.match(r'^\$[A-Za-z0-9\._]+$', condition) is not None

    def _parse_comparison(self, condition: str):
        """Parses a condition with a comparison operator."""
        condition = condition.strip()
        pattern = r'(?P<left>[^!=<>]+)\s*(?P<operator>[!=<>]=?|<|>)\s*(?P<right>.+)'
        match = re.match(pattern, condition)

        if not match:
            raise ValueError(f"Failed to parse condition: {condition}")

        left_expr = match.group('left').strip()
        operator = match.group('operator').strip()
        right_expr = match.group('right').strip()

        return left_expr, operator, right_expr

    def _evaluate_comparison(self, left_expr: str, operator: str, right_expr: str) -> bool:
        """Evaluates a comparison between two expressions."""
        left_value = self._resolve_context(left_expr)
        right_value = self._resolve_context(right_expr)

        if operator == '==':
            return left_value == right_value
        elif operator == '!=':
            return left_value != right_value
        elif operator == '<':
            return left_value < right_value
        elif operator == '>':
            return left_value > right_value
        elif operator == '<=':
            return left_value <= right_value
        elif operator == '>=':
            return left_value >= right_value

        raise ValueError(f"Unknown operator: {operator} in condition: {left_expr} {operator} {right_expr}")

    def _resolve_context(self, context: str) -> Any:
        """Resolves context expressions like "$response.body.status"."""
        if context.startswith("'") and context.endswith("'"):
            return context.strip("'")  # Literal string value

        if re.match(r'^\d+(\.\d+)?$', context):
            return float(context) if '.' in context else int(context)

        # Handle paths like $response.body.status
        return self._resolve_path(context)

    def _resolve_path(self, path: str) -> Any:
        """Resolves a path expression from the context."""
        parts = path.strip("$").split(".")
        value = self.context

        for part in parts:
            if isinstance(value, list):
                part = int(part)
                value = value[part]
            else:
                value = value.get(part)
            if value is None:
                raise ValueError(f"Failed to resolve path '{path}': '{part}' does not exist")

        return value

    def _evaluate_regex(self, pattern: str, text: str) -> bool:
        if text is None:
            raise ValueError(f"Context resolved to None for regex pattern '{pattern}'")
        match = re.match(pattern, text)
        result = match is not None
        print(f"Regex condition '{pattern}' applied to '{text}': {result}")
        return result

    def _evaluate_jsonpath(self, jsonpath_expr: str, data: Any) -> bool:
        jsonpath_expr = jsonpath_parse(jsonpath_expr)
        matches = jsonpath_expr.find(data)
        return len(matches) > 0

    def _evaluate_xpath(self, xpath_expr: str, xml_data: str) -> bool:
        raise NotImplementedError("XPath evaluation is not yet implemented")
