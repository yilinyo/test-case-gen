"""Validation and safe evaluation for function test specifications."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any


class SpecValidationError(ValueError):
    """Raised when a test specification is invalid."""


@dataclass(frozen=True)
class CompiledRule:
    id: str
    name: str
    when: str
    expect: Any
    code: Any


ALLOWED_EXPR_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.UnaryOp,
    ast.BinOp,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
)

ALLOWED_OPERATORS = (
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.USub,
    ast.UAdd,
)


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Validate the shape of a test spec and all rule expressions."""
    if not isinstance(spec, dict):
        raise SpecValidationError("spec must be a JSON object")

    for field in ("function", "params", "rules"):
        if field not in spec:
            raise SpecValidationError(f"missing required field: {field}")

    if not isinstance(spec["function"], str) or not spec["function"].strip():
        raise SpecValidationError("function must be a non-empty string")

    params = spec["params"]
    if not isinstance(params, dict) or not params:
        raise SpecValidationError("params must be a non-empty object")

    for name, config in params.items():
        if not isinstance(name, str) or not name.isidentifier():
            raise SpecValidationError(f"invalid parameter name: {name!r}")
        if not isinstance(config, dict):
            raise SpecValidationError(f"parameter {name} config must be an object")
        if config.get("type", "int") not in ("int", "float", "str", "bool"):
            raise SpecValidationError(f"parameter {name} has unsupported type")

    rules = spec["rules"]
    if not isinstance(rules, list) or not rules:
        raise SpecValidationError("rules must be a non-empty array")

    param_names = set(params)
    seen_ids: set[str] = set()
    for idx, rule in enumerate(rules, start=1):
        if not isinstance(rule, dict):
            raise SpecValidationError(f"rule #{idx} must be an object")
        for field in ("id", "name", "when", "expect"):
            if field not in rule:
                raise SpecValidationError(f"rule #{idx} missing field: {field}")
        if not isinstance(rule["id"], str) or not rule["id"].strip():
            raise SpecValidationError(f"rule #{idx} id must be a non-empty string")
        if rule["id"] in seen_ids:
            raise SpecValidationError(f"duplicate rule id: {rule['id']}")
        seen_ids.add(rule["id"])
        if not isinstance(rule["name"], str):
            raise SpecValidationError(f"rule {rule['id']} name must be a string")
        if not isinstance(rule["when"], str) or not rule["when"].strip():
            raise SpecValidationError(f"rule {rule['id']} when must be a non-empty string")
        validate_expression(rule["when"], param_names)

    return spec


def validate_expression(expression: str, allowed_names: set[str]) -> ast.Expression:
    """Parse and validate a safe Python boolean expression."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise SpecValidationError(f"invalid expression {expression!r}: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.operator | ast.unaryop | ast.boolop | ast.cmpop):
            if not isinstance(node, ALLOWED_OPERATORS):
                raise SpecValidationError(f"unsupported operator in expression: {expression}")
            continue
        if not isinstance(node, ALLOWED_EXPR_NODES):
            raise SpecValidationError(
                f"unsupported expression node {type(node).__name__} in {expression!r}"
            )
        if isinstance(node, ast.Name) and node.id not in allowed_names:
            raise SpecValidationError(
                f"unknown name {node.id!r} in expression {expression!r}"
            )
    return tree


def compile_rules(spec: dict[str, Any]) -> list[CompiledRule]:
    """Validate and compile all rule expressions."""
    validate_spec(spec)
    compiled: list[CompiledRule] = []
    for rule in spec["rules"]:
        tree = validate_expression(rule["when"], set(spec["params"]))
        compiled.append(
            CompiledRule(
                id=rule["id"],
                name=rule["name"],
                when=rule["when"],
                expect=rule["expect"],
                code=compile(tree, f"<rule:{rule['id']}>", "eval"),
            )
        )
    return compiled


def evaluate_rule(rule: CompiledRule, values: dict[str, Any]) -> bool:
    """Evaluate a compiled rule against one parameter assignment."""
    return bool(eval(rule.code, {"__builtins__": {}}, values))
