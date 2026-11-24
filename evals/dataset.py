from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Optional


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "data" / "golden" / "cases.jsonl"


def load_cases(
    path: Optional[Path] = None,
    *,
    split: Optional[str] = None,
) -> list[dict[str, Any]]:
    path = path or DEFAULT_CASES
    cases: list[dict[str, Any]] = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if split and row.get("split") != split:
                continue
            cases.append(row)
    return cases


def iter_splits(cases: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for c in cases:
        counts[c.get("split", "unknown")] = counts.get(c.get("split", "unknown"), 0) + 1
    return counts
