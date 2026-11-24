"""LLM backends: live Ollama HTTP, or fixture replay for CI."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import httpx

DEFAULT_MODEL = os.environ.get("OPENTRIAGE_MODEL", "llama3.2")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")


class LLMError(RuntimeError):
    pass


def mode() -> str:
    return os.environ.get("OPENTRIAGE_MODE", "fixture").lower()


def complete(prompt: str, *, fixture_key: Optional[str] = None) -> str:
    """Return model text. In fixture mode, look up recorded output by key."""
    if mode() == "fixture":
        return _fixture_complete(fixture_key)
    return _ollama_complete(prompt)


def _ollama_complete(prompt: str) -> str:
    url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }
    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMError(
            f"Ollama request failed ({exc}). "
            "Is Ollama running, or set OPENTRIAGE_MODE=fixture?"
        ) from exc
    data = resp.json()
    text = data.get("response")
    if not text:
        raise LLMError(f"Empty Ollama response: {data!r}")
    return text


def _fixture_complete(fixture_key: Optional[str]) -> str:
    if not fixture_key:
        raise LLMError("fixture mode requires fixture_key / case id")
    path = Path(os.environ.get("OPENTRIAGE_FIXTURES", "data/fixtures/outputs.json"))
    if not path.exists():
        raise LLMError(f"Fixture file missing: {path}")
    fixtures = json.loads(path.read_text())
    if fixture_key not in fixtures:
        raise LLMError(f"No fixture for case id={fixture_key!r}")
    value = fixtures[fixture_key]
    if isinstance(value, dict):
        return json.dumps(value)
    return str(value)
