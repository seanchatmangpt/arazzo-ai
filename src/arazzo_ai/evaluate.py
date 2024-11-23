import json
import re
from jsonpath_ng.ext import parse as jsonpath_parse
from typing import Any, Dict, Union
from jsonpointer import resolve_pointer


class ExpressionEvaluator:
    def __init__(self, context: Dict[str, Any]):
        self.context = context
        print(f"Initialized ExpressionEvaluator with context: {json.dumps(self.context, indent=2)}")

    def __call__(self, expression: str) -> Union[str, None, float, bool]:
        print(f"Evaluating expression: {expression}")
        if "{" in expression and "}" in expression:
            result = self._evaluate_embedded(expression)
        elif expression.startswith("$"):
            result = self._evaluate(expression)
        else:
            result = self._evaluate_simple_expression(expression)
        print(f"Result of expression '{expression}': {result}")
        return result

    def _evaluate(self, expression: str) -> Any:
        # Handle JSON Pointer-based expressions (e.g., $response.body#/eligibilityCheckRequired)
        json_pointer_match = re.match(r"\$(.+)#/(.*)", expression)
        if json_pointer_match:
            base, pointer = json_pointer_match.groups()
            data = self._get_base(base)
            return self._evaluate_json_pointer(data, pointer)

        # Handle dot-notation based expressions (e.g., $response.body.eligibilityCheckRequired)
        dot_notation_match = re.match(r"\$(.+)", expression)
        if dot_notation_match:
            base = dot_notation_match.group(1)
            return self._evaluate_dot_notation(base)

        raise ValueError(f"Invalid expression format: {expression}")

    def _evaluate_embedded(self, expression: str) -> str:
        # Replace embedded expressions like "Hello, {$inputs.customer.firstName}!"
        def replacer(match):
            expr = match.group(1)
            try:
                return str(self._evaluate(f"${expr}"))
            except ValueError:
                return ""

        return re.sub(r"\{\$(.+?)\}", replacer, expression)

    def _get_base(self, base: str) -> Any:
        # Retrieve the base context for expressions like response.body, inputs, etc.
        parts = base.split(".")
        data = self.context
        for part in parts:
            if part not in data:
                raise ValueError(f"Unknown or missing base in expression: {base}")
            data = data[part]
        return data

    def _evaluate_json_pointer(self, data: Any, pointer: str) -> Any:
        # Handle JSON Pointer navigation
        try:
            return resolve_pointer(data, f"/{pointer}")
        except Exception as e:
            print(f"Error evaluating JSONPointer '{pointer}': {e}")
            return None

    def _evaluate_dot_notation(self, path: str) -> Any:
        # Navigate through the context using dot notation
        parts = path.split(".")
        data = self.context
        for part in parts:
            if isinstance(data, dict):
                data = data.get(part)
            elif isinstance(data, list):
                try:
                    index = int(part)
                    data = data[index]
                except (ValueError, IndexError):
                    return None
            else:
                return None
        return data
