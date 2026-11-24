"""Suite 8 — compare scorecard against baselines; exit non-zero on regression."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINES = ROOT / "evals" / "baselines.json"


def load_baselines(path: Path = DEFAULT_BASELINES) -> dict[str, Any]:
    return json.loads(path.read_text())


def check_gate(scorecard: dict[str, Any], baselines: dict[str, Any]) -> list[str]:
    """Return list of failure messages (empty => pass)."""
    decision = scorecard.get("decision", {})
    failures: list[str] = []

    min_acc = baselines.get("min_act_now_accuracy")
    if min_acc is not None and decision.get("act_now_accuracy", 0) < min_acc:
        failures.append(
            f"act_now_accuracy {decision.get('act_now_accuracy'):.3f} < min {min_acc}"
        )

    min_asym = baselines.get("min_asymmetric_score")
    if min_asym is not None and decision.get("asymmetric_score", 0) < min_asym:
        failures.append(
            f"asymmetric_score {decision.get('asymmetric_score'):.3f} < min {min_asym}"
        )

    max_fn = baselines.get("max_fn_rate")
    if max_fn is not None and decision.get("fn_rate", 1) > max_fn:
        failures.append(f"fn_rate {decision.get('fn_rate'):.3f} > max {max_fn}")

    min_sev = baselines.get("min_severity_score")
    if min_sev is not None and decision.get("severity_score", 0) < min_sev:
        failures.append(
            f"severity_score {decision.get('severity_score'):.3f} < min {min_sev}"
        )

    return failures


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    scorecard_path = Path(argv[0]) if argv else ROOT / "artifacts" / "scorecard.json"
    baselines_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_BASELINES
    scorecard = json.loads(scorecard_path.read_text())
    baselines = load_baselines(baselines_path)
    failures = check_gate(scorecard, baselines)
    if failures:
        print("GATE FAILED")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
