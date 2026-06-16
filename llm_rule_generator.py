"""OpenAI-compatible LLM rule generation."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
RESPONSES_PATH = "responses"


def build_prompt(function_source: str, requirement: str, target: str) -> str:
    return f"""你是一个软件测试用例设计助手。

请根据以下函数源码和需求说明，生成函数测试规格 JSON。

要求：
1. 输出必须是合法 JSON；
2. 不要输出 Markdown；
3. 不要添加解释文字；
4. 每个测试场景必须包含 id、name、when、expect；
5. when 字段必须是 Python 布尔表达式；
6. rules 必须覆盖正常情况、异常情况、边界情况；
7. 参数名必须与函数参数一致；
8. 不要使用函数调用、属性访问、下标访问；
9. 不要生成工具不支持的表达式；
10. 如果需求说明和函数源码冲突，以需求说明为准。

目标函数：{target}

函数源码：
{function_source}

需求说明：
{requirement}

输出 JSON 格式：
{{
  "function": "...",
  "target": "{target}",
  "max_cases_per_rule": 3,
  "params": {{
    "参数名": {{
      "type": "int",
      "min": -10,
      "max": 10
    }}
  }},
  "rules": [
    {{
      "id": "...",
      "name": "...",
      "when": "...",
      "expect": "..."
    }}
  ]
}}
"""


def generate_spec_with_llm(function_source: str, requirement: str, target: str) -> dict[str, Any]:
    """Call an OpenAI-compatible Responses API and parse its JSON result."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "LLM mode requires OPENAI_API_KEY. You can also use hybrid mode with "
            "--out-prompt to save the prompt for manual model use."
        )

    base_url = os.getenv("OPENAI_BASE_URL", DEFAULT_BASE_URL).strip()
    request_url = build_responses_url(base_url)
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    prompt = build_prompt(function_source, requirement, target)
    payload = {
        "model": model,
        "input": prompt,
        "temperature": 0.2,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        request_url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Function-TestCase-Generator/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_text = response.read().decode("utf-8", errors="replace")
            body = parse_llm_response_body(
                response_text,
                status_code=response.status,
                content_type=response.headers.get("Content-Type", ""),
                url=request_url,
            )
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        hint = build_http_error_hint(exc.code, detail, base_url)
        raise RuntimeError(
            f"LLM API request failed: HTTP {exc.code}\n"
            f"base_url: {base_url}\n"
            f"request_url: {request_url}\n"
            f"model: {model}\n"
            f"detail: {detail}\n"
            f"{hint}"
        ) from exc

    content = extract_response_text(body)
    return extract_json_object(content)


def build_responses_url(base_url: str) -> str:
    """Build the Responses endpoint URL from a base URL ending at /v1."""
    normalized = base_url.rstrip("/")
    if normalized.endswith(f"/{RESPONSES_PATH}"):
        return normalized
    return f"{normalized}/{RESPONSES_PATH}"


def parse_llm_response_body(
    response_text: str, status_code: int, content_type: str, url: str
) -> dict[str, Any]:
    """Parse JSON or SSE-style JSON responses with useful diagnostics."""
    text = response_text.strip()
    if not text:
        raise RuntimeError(
            "LLM API returned an empty response body.\n"
            f"status: {status_code}\n"
            f"content_type: {content_type}\n"
            f"url: {url}\n"
            "hint: check OPENAI_BASE_URL. It should point to the API base path, "
            "for example https://api.openai.com/v1 or https://your-provider/v1."
        )

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        sse_body = parse_sse_response(text)
        if sse_body is not None:
            return sse_body

        preview = text[:1000]
        raise RuntimeError(
            "LLM API returned a non-JSON response body.\n"
            f"status: {status_code}\n"
            f"content_type: {content_type}\n"
            f"url: {url}\n"
            f"body_preview: {preview}\n"
            "hint: the endpoint may be wrong, or the provider may not support the "
            "Responses API format at this URL."
        )


def parse_sse_response(text: str) -> dict[str, Any] | None:
    """Parse a server-sent-events response and return the last JSON data event."""
    parsed_events: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if not data or data == "[DONE]":
            continue
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            parsed_events.append(parsed)

    if not parsed_events:
        return None

    for event in reversed(parsed_events):
        if isinstance(event.get("response"), dict):
            return event["response"]
        if event.get("type") in ("response.completed", "response.output_text.done"):
            return event
    return parsed_events[-1]

def extract_response_text(body: dict[str, Any]) -> str:
    """Extract text from Responses API or compatible response bodies."""
    if isinstance(body.get("output_text"), str):
        return body["output_text"]
    if isinstance(body.get("text"), str):
        return body["text"]

    output = body.get("output")
    if isinstance(output, list):
        text_parts: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                if isinstance(part.get("text"), str):
                    text_parts.append(part["text"])
        if text_parts:
            return "\n".join(text_parts)

    choices = body.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {})
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return message["content"]

    raise RuntimeError(
        "LLM response does not contain text output: "
        f"{json.dumps(body, ensure_ascii=False)}"
    )


def build_http_error_hint(status_code: int, detail: str, base_url: str) -> str:
    if status_code == 403 and "1010" in detail:
        return (
            "hint: 403 error code 1010 usually means the API gateway or Cloudflare "
            "blocked this request. Check whether OPENAI_BASE_URL is correct, whether "
            "the provider allows server-side API calls, and whether your API key/IP "
            "is permitted by that provider."
        )
    if status_code == 401:
        return "hint: check whether OPENAI_API_KEY is correct and not expired."
    if status_code == 404:
        return (
            "hint: check OPENAI_BASE_URL. It should point to the API base path, "
            "for example https://api.openai.com/v1. The tool automatically appends /responses."
        )
    if status_code == 429:
        return "hint: request was rate limited or quota is insufficient."
    if "api.openai.com" not in base_url:
        return "hint: this is a third-party OpenAI-compatible endpoint; verify its URL and model name."
    return "hint: verify API key, base URL, model name, quota, and provider status."


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract and parse the first JSON object from LLM output."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(stripped[start : end + 1])


def write_prompt_file(path: str | Path, function_source: str, requirement: str, target: str) -> None:
    prompt = build_prompt(function_source, requirement, target)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(prompt, encoding="utf-8")
