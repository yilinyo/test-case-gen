"""Dynamic loading helpers for tested functions."""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path
from typing import Any


def load_function(target: str) -> Any:
    """Load a function from 'module:function' or 'path/to/file.py:function'."""
    if ":" not in target:
        raise ValueError("--call must use module:function or file.py:function format")
    module_name, function_name = target.split(":", 1)
    module_name = module_name.strip()
    function_name = function_name.strip()
    if not module_name or not function_name:
        raise ValueError("--call must include both module and function name")

    if module_name.endswith(".py") or "/" in module_name:
        path = Path(module_name).resolve()
        sys.path.insert(0, str(path.parent))
        module = importlib.import_module(path.stem)
    else:
        cwd = str(Path.cwd())
        if cwd not in sys.path:
            sys.path.insert(0, cwd)
        module = importlib.import_module(module_name)

    function = getattr(module, function_name)
    if not callable(function):
        raise TypeError(f"{target} is not callable")
    return function


def get_function_source(target: str) -> str:
    function = load_function(target)
    return inspect.getsource(function)


def infer_params_from_signature(function: Any) -> dict[str, dict[str, Any]]:
    params: dict[str, dict[str, Any]] = {}
    signature = inspect.signature(function)
    for name, parameter in signature.parameters.items():
        if parameter.kind not in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            continue
        annotation = parameter.annotation
        if annotation is int:
            params[name] = {"type": "int", "min": -10, "max": 10}
        elif annotation is float:
            params[name] = {"type": "float", "min": -10, "max": 10}
        elif annotation is bool:
            params[name] = {"type": "bool"}
        elif annotation is str:
            params[name] = {"type": "str"}
        else:
            params[name] = {"type": "int", "min": -10, "max": 10}
    return params
