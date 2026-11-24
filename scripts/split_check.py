#!/usr/bin/env python3
"""Assert golden-set stratification mins so the set cannot silently skew."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "data" / "golden" / "cases.jsonl"

MIN_TOTAL = 30
MIN_TEST = 8
MIN_ACT_TRUE = 10
MIN_ACT_FALSE = 10


def main() -> int:
    cases = [json.loads(l) for l in CASES.read_text().splitlines() if l.strip()]
    splits = Counter(c["split"] for c in cases)
    acts = Counter(bool(c["label"]["act_now"]) for c in cases)
    sevs = Counter(int(c["label"]["severity"]) for c in cases)

    errors = []
    if len(cases) < MIN_TOTAL:
        errors.append(f"total {len(cases)} < {MIN_TOTAL}")
    if splits.get("test", 0) < MIN_TEST:
        errors.append(f"test {splits.get('test', 0)} < {MIN_TEST}")
    if acts.get(True, 0) < MIN_ACT_TRUE:
        errors.append(f"act_now true {acts.get(True, 0)} < {MIN_ACT_TRUE}")
    if acts.get(False, 0) < MIN_ACT_FALSE:
        errors.append(f"act_now false {acts.get(False, 0)} < {MIN_ACT_FALSE}")
    if len(sevs) < 3:
        errors.append(f"severity diversity too low: {dict(sevs)}")

    print(f"n={len(cases)} splits={dict(splits)} act_now={dict(acts)} severity={dict(sevs)}")
    if errors:
        print("SPLIT CHECK FAILED")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("SPLIT CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
