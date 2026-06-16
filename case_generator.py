"""Deterministic test case generation and report export."""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path
from typing import Any

from spec_validator import compile_rules, evaluate_rule


def candidate_values(config: dict[str, Any]) -> list[Any]:
    """Build a compact set of candidate values for one parameter."""
    param_type = config.get("type", "int")
    explicit = list(config.get("values", []))

    if param_type == "bool":
        values = explicit or [False, True]
    elif param_type == "str":
        values = explicit or ["", "a", "test"]
    elif param_type in ("int", "float"):
        min_value = config.get("min", -10)
        max_value = config.get("max", 10)
        values = []
        if param_type == "int" and max_value - min_value <= 30:
            values.extend(range(int(min_value), int(max_value) + 1))
        else:
            mid = (min_value + max_value) / 2
            if param_type == "int":
                mid = int(mid)
            values.extend(
                [
                    min_value,
                    min_value + 1,
                    -1,
                    0,
                    1,
                    mid,
                    max_value - 1,
                    max_value,
                ]
            )
        values.extend(explicit)
    else:
        values = explicit

    deduped: list[Any] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def generate_input_combinations(
    params: dict[str, dict[str, Any]], max_total_search: int = 50_000
) -> list[dict[str, Any]]:
    names = list(params)
    pools = [candidate_values(params[name]) for name in names]
    combinations: list[dict[str, Any]] = []
    for idx, values in enumerate(itertools.product(*pools)):
        if idx >= max_total_search:
            break
        combinations.append(dict(zip(names, values, strict=True)))
    return combinations


def generate_cases(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate test cases by matching candidate inputs against spec rules."""
    rules = compile_rules(spec)
    max_cases_per_rule = int(spec.get("max_cases_per_rule", 3))
    max_total_search = int(spec.get("max_total_search", 50_000))
    combinations = generate_input_combinations(spec["params"], max_total_search)
    cases: list[dict[str, Any]] = []
    used_inputs: set[tuple[tuple[str, Any], ...]] = set()

    case_no = 1
    for rule in rules:
        matched = 0
        for values in combinations:
            input_key = tuple(sorted(values.items()))
            if input_key in used_inputs:
                continue
            if evaluate_rule(rule, values):
                case = {
                    "case_id": f"TC_{case_no:03d}",
                    "function": spec["function"],
                    "scenario_id": rule.id,
                    "scenario": rule.name,
                    "condition": rule.when,
                    "expected": rule.expect,
                    "inputs": values,
                }
                cases.append(case)
                used_inputs.add(input_key)
                case_no += 1
                matched += 1
                if matched >= max_cases_per_rule:
                    break
    return cases


def attach_results(cases: list[dict[str, Any]], function: Any) -> list[dict[str, Any]]:
    """Run generated cases against the target function."""
    for case in cases:
        try:
            actual = function(**case["inputs"])
            case["actual"] = actual
            case["pass"] = actual == case["expected"]
            case["error"] = ""
        except Exception as exc:  # noqa: BLE001 - execution errors are report data.
            case["actual"] = None
            case["pass"] = False
            case["error"] = f"{type(exc).__name__}: {exc}"
    return cases


def flatten_case(case: dict[str, Any], param_names: list[str]) -> dict[str, Any]:
    row = {
        "case_id": case["case_id"],
        "function": case["function"],
        "scenario_id": case["scenario_id"],
        "scenario": case["scenario"],
        "condition": case["condition"],
        "expected": case.get("expected"),
    }
    for name in param_names:
        row[name] = case["inputs"].get(name)
    if "actual" in case:
        row["actual"] = case.get("actual")
        row["pass"] = case.get("pass")
        row["error"] = case.get("error", "")
    return row


def export_cases(cases: list[dict[str, Any]], out_path: str | Path, param_names: list[str]) -> None:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    if suffix == ".json":
        path.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    elif suffix in (".md", ".markdown"):
        path.write_text(render_markdown(cases, param_names), encoding="utf-8")
    else:
        rows = [flatten_case(case, param_names) for case in cases]
        fieldnames = list(rows[0]) if rows else ["case_id", *param_names]
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def render_markdown(cases: list[dict[str, Any]], param_names: list[str]) -> str:
    headers = [
        "case_id",
        "scenario",
        *param_names,
        "expected",
        "actual",
        "pass",
    ]
    lines = ["# 测试用例报告", "", "|" + "|".join(headers) + "|"]
    lines.append("|" + "|".join(["---"] * len(headers)) + "|")
    for case in cases:
        row = {
            "case_id": case["case_id"],
            "scenario": case["scenario"],
            "expected": case.get("expected", ""),
            "actual": case.get("actual", ""),
            "pass": case.get("pass", ""),
        }
        for name in param_names:
            row[name] = case["inputs"].get(name, "")
        lines.append("|" + "|".join(str(row.get(header, "")) for header in headers) + "|")
    lines.append("")
    return "\n".join(lines)
