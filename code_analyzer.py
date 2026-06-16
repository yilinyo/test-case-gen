"""Simple AST-based rule extraction for auto mode."""

from __future__ import annotations

import ast
import inspect
import textwrap
from typing import Any

from function_runner import infer_params_from_signature, load_function


def build_auto_spec(target: str, params_config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create a test spec from simple sequential if-return functions."""
    function = load_function(target)
    source = textwrap.dedent(inspect.getsource(function))
    tree = ast.parse(source)
    func_def = next((node for node in tree.body if isinstance(node, ast.FunctionDef)), None)
    if func_def is None:
        raise ValueError("target source does not contain a function definition")

    params = (params_config or {}).get("params") or infer_params_from_signature(function)
    rules: list[dict[str, Any]] = []
    previous_conditions: list[str] = []
    rule_no = 1

    for stmt in func_def.body:
        if isinstance(stmt, ast.If):
            condition = ast.unparse(stmt.test)
            returned = _constant_return(stmt.body)
            if returned is not _MISSING:
                when = _join_conditions([*previous_conditions, condition])
                rules.append(
                    {
                        "id": f"branch_{rule_no:02d}",
                        "name": f"分支 {rule_no}: {condition}",
                        "when": when,
                        "expect": returned,
                    }
                )
                previous_conditions.append(f"not ({condition})")
                rule_no += 1
        elif isinstance(stmt, ast.Return):
            returned = _return_value(stmt)
            when = _join_conditions(previous_conditions) if previous_conditions else "True"
            rules.append(
                {
                    "id": f"branch_{rule_no:02d}",
                    "name": "默认返回分支",
                    "when": when,
                    "expect": returned,
                }
            )
            break

    if not rules:
        raise ValueError("auto mode currently supports simple if/return functions only")

    return {
        "function": function.__name__,
        "target": target,
        "max_cases_per_rule": 3,
        "params": params,
        "rules": rules,
    }


_MISSING = object()


def _constant_return(statements: list[ast.stmt]) -> Any:
    for stmt in statements:
        if isinstance(stmt, ast.Return):
            return _return_value(stmt)
    return _MISSING


def _return_value(stmt: ast.Return) -> Any:
    if stmt.value is None:
        return None
    if isinstance(stmt.value, ast.Constant):
        return stmt.value.value
    return ast.unparse(stmt.value)


def _join_conditions(conditions: list[str]) -> str:
    return " and ".join(f"({condition})" for condition in conditions) or "True"
