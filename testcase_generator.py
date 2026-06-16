#!/usr/bin/env python3
"""CLI entry point for the function test case generation tool."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from case_generator import attach_results, export_cases, generate_cases
from code_analyzer import build_auto_spec
from env_loader import load_env_file
from function_runner import get_function_source, load_function
from llm_rule_generator import generate_spec_with_llm, write_prompt_file
from spec_validator import validate_spec


def main() -> None:
    args = parse_args()
    load_env_file(args.env_file)
    spec = resolve_spec(args)

    if args.out_spec:
        write_json(args.out_spec, spec)
        print(f"spec written: {args.out_spec}")

    if not args.out:
        return

    cases = generate_cases(spec)
    if args.call or spec.get("target"):
        function = load_function(args.call or spec["target"])
        attach_results(cases, function)

    param_names = list(spec["params"])
    export_cases(cases, args.out, param_names)
    print(f"cases written: {args.out} ({len(cases)} cases)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate function-level test cases from rules, AST analysis, or LLM specs."
    )
    parser.add_argument("--mode", choices=["rule", "auto", "llm", "hybrid"], required=True)
    parser.add_argument("--spec", help="test_spec.json for rule mode")
    parser.add_argument("--params", help="params.json for auto mode")
    parser.add_argument("--call", help="target function as module:function or file.py:function")
    parser.add_argument("--requirement", help="natural language requirement file")
    parser.add_argument("--out", help="output report path: .csv, .json, or .md")
    parser.add_argument("--out-spec", help="write generated spec JSON to this path")
    parser.add_argument(
        "--out-prompt",
        help="write the LLM prompt to this path; useful when OPENAI_API_KEY is not configured",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="load LLM configuration from this .env file, default: .env",
    )
    return parser.parse_args()


def resolve_spec(args: argparse.Namespace) -> dict[str, Any]:
    if args.mode == "rule":
        if not args.spec:
            raise SystemExit("rule mode requires --spec")
        spec = read_json(args.spec)
        validate_spec(spec)
        return spec

    if args.mode == "auto":
        if not args.call:
            raise SystemExit("auto mode requires --call")
        params_config = read_json(args.params) if args.params else None
        spec = build_auto_spec(args.call, params_config)
        validate_spec(spec)
        return spec

    if args.mode in ("llm", "hybrid"):
        if not args.call or not args.requirement:
            raise SystemExit(f"{args.mode} mode requires --call and --requirement")
        function_source = get_function_source(args.call)
        requirement = Path(args.requirement).read_text(encoding="utf-8")
        if args.out_prompt:
            write_prompt_file(args.out_prompt, function_source, requirement, args.call)
        if args.mode == "hybrid" and not args.out:
            if not args.out_prompt:
                default_prompt = args.out_spec or "outputs/llm_rule_generation_prompt.md"
                write_prompt_file(default_prompt, function_source, requirement, args.call)
                print(f"prompt written: {default_prompt}")
            print("hybrid draft created; review LLM output as a spec, then run rule mode")
            raise SystemExit(0)
        spec = generate_spec_with_llm(function_source, requirement, args.call)
        validate_spec(spec)
        return spec

    raise SystemExit(f"unsupported mode: {args.mode}")


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, data: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
