"""Run eval suites and print / write a scorecard."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Ensure src/ is importable when run as a module without install.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from evals.dataset import load_cases  # noqa: E402
from evals.gate import check_gate, load_baselines  # noqa: E402
from evals.metrics_decision import CaseResult, score_results  # noqa: E402
from evals.metrics_judge import judge_case, summarize_judge  # noqa: E402
from opentriage.agent import TriageAgent  # noqa: E402


def run_decision(
    *,
    split: Optional[str],
    case_ids: Optional[list[str]] = None,
) -> tuple[dict[str, Any], list[CaseResult], list[dict[str, Any]]]:
    os.environ.setdefault("OPENTRIAGE_MODE", "fixture")
    os.environ.setdefault(
        "OPENTRIAGE_FIXTURES", str(ROOT / "data" / "fixtures" / "outputs.json")
    )

    cases = load_cases(split=split)
    if case_ids:
        want = set(case_ids)
        cases = [c for c in cases if c["id"] in want]

    agent = TriageAgent()
    results: list[CaseResult] = []
    predictions: list[dict[str, Any]] = []

    for case in cases:
        try:
            decision = agent.triage(case["input"], case_id=case["id"])
            results.append(
                CaseResult(
                    case_id=case["id"],
                    label_act_now=bool(case["label"]["act_now"]),
                    pred_act_now=decision.act_now,
                    label_severity=int(case["label"]["severity"]),
                    pred_severity=decision.severity,
                    tool_calls=list(decision.tool_calls),
                    expect_tool_call=bool(case.get("expect_tool_call", False)),
                )
            )
            predictions.append(
                {
                    "case_id": case["id"],
                    "input": case["input"],
                    "label": case["label"],
                    "pred": decision.model_dump(),
                }
            )
        except Exception as exc:  # noqa: BLE001 — collect per-case failures
            results.append(
                CaseResult(
                    case_id=case["id"],
                    label_act_now=bool(case["label"]["act_now"]),
                    pred_act_now=False,
                    label_severity=int(case["label"]["severity"]),
                    pred_severity=0,
                    tool_calls=[],
                    expect_tool_call=bool(case.get("expect_tool_call", False)),
                    error=str(exc),
                )
            )
            predictions.append(
                {
                    "case_id": case["id"],
                    "input": case["input"],
                    "label": case["label"],
                    "pred": None,
                    "error": str(exc),
                }
            )

    return score_results(results), results, predictions


def run_judge(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for row in predictions:
        if not row.get("pred"):
            rows.append({"case_id": row["case_id"], "error": row.get("error", "no pred")})
            continue
        rows.append(
            judge_case(
                case_id=row["case_id"],
                alert=row["input"],
                label=row["label"],
                pred=row["pred"],
            )
        )
    summary = summarize_judge(rows)
    summary["cases"] = rows
    return summary


def print_scorecard(scorecard: dict[str, Any]) -> None:
    d = scorecard["decision"]
    print("=" * 60)
    print("OpenTriage-Evals scorecard")
    print("=" * 60)
    print(f"mode:     {scorecard.get('mode')}")
    print(f"split:    {scorecard.get('split')}")
    print(f"n:        {d.get('n')}")
    print(f"act_now:  accuracy={d.get('act_now_accuracy'):.3f}")
    print(f"errors:   FN={d.get('fn_count')} ({d.get('fn_rate'):.3f})  "
          f"FP={d.get('fp_count')} ({d.get('fp_rate'):.3f})")
    print(f"asym:     {d.get('asymmetric_score'):.3f}  "
          f"(fn_weight={d.get('fn_weight')}, fp_weight={d.get('fp_weight')})")
    print(f"severity: {d.get('severity_score'):.3f}")
    if d.get("tool_call_recall") is not None:
        print(f"tools:    recall={d.get('tool_call_recall'):.3f}")
    if scorecard.get("judge"):
        j = scorecard["judge"]
        print(f"judge:    agreement={j.get('judge_human_agreement'):.3f}  "
              f"reasoning={j.get('mean_reasoning_score'):.3f}")
    print("=" * 60)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run OpenTriage eval suites")
    parser.add_argument(
        "--split",
        choices=["train", "test", "all"],
        default="all",
        help="Which golden split to evaluate",
    )
    parser.add_argument(
        "--gate",
        action="store_true",
        help="Fail if scorecard regresses vs evals/baselines.json",
    )
    parser.add_argument(
        "--judge",
        action="store_true",
        help="Also run LLM-as-judge suite (uses judge fixtures in fixture mode)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "artifacts" / "scorecard.json",
        help="Scorecard output path",
    )
    args = parser.parse_args(argv)

    split = None if args.split == "all" else args.split
    # CI gate defaults to test split unless overridden
    if args.gate and args.split == "all":
        split = "test"

    decision, _results, predictions = run_decision(split=split)
    scorecard: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": os.environ.get("OPENTRIAGE_MODE", "fixture"),
        "split": split or "all",
        "decision": decision,
    }

    if args.judge or os.environ.get("EVAL_JUDGE") == "1":
        scorecard["judge"] = run_judge(predictions)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(scorecard, indent=2) + "\n")
    print_scorecard(scorecard)
    print(f"wrote {args.out}")

    if args.gate:
        failures = check_gate(scorecard, load_baselines())
        if failures:
            print("GATE FAILED")
            for f in failures:
                print(f"  - {f}")
            return 1
        print("GATE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
