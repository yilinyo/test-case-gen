"""Minimal .env loader for local configuration."""

from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: str | Path = ".env", override: bool = False) -> None:
    """Load KEY=VALUE pairs from a .env file into os.environ."""
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = _strip_inline_comment(value.strip())
        value = _strip_quotes(value)

        if not key:
            continue
        if override or key not in os.environ:
            os.environ[key] = value


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _strip_inline_comment(value: str) -> str:
    if not value or value[0] in ("'", '"'):
        return value
    comment_index = value.find(" #")
    if comment_index == -1:
        return value
    return value[:comment_index].strip()
