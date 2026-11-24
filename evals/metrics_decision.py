"""Suite 1 — decision accuracy + asymmetric FN/FP + ordinal severity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


FN_WEIGHT = 3.0
FP_WEIGHT = 1.0


@dataclass
class CaseResult:
    case_id: str
    label_act_now: bool
    pred_act_now: bool
    label_severity: int
    pred_severity: int
    tool_calls: list[str]
    expect_tool_call: bool
    error: Optional[str] = None

    @property
    def act_now_correct(self) -> bool:
        return self.error is None and self.label_act_now == self.pred_act_now

    @property
    def is_fn(self) -> bool:
        return self.error is None and self.label_act_now and not self.pred_act_now

    @property
    def is_fp(self) -> bool:
        return self.error is None and (not self.label_act_now) and self.pred_act_now

    @property
    def severity_score(self) -> float:
        if self.error is not None:
            return 0.0
        delta = abs(self.label_severity - self.pred_severity)
        if delta == 0:
            return 1.0
        if delta == 1:
            return 0.5
        return 0.0


def score_results(results: list[CaseResult]) -> dict[str, Any]:
    n = len(results)
    if n == 0:
        return {
            "n": 0,
            "act_now_accuracy": 0.0,
            "fn_rate": 0.0,
            "fp_rate": 0.0,
            "asymmetric_score": 0.0,
            "severity_score": 0.0,
            "parse_errors": 0,
            "tool_call_recall": None,
        }

    correct = sum(1 for r in results if r.act_now_correct)
    fns = sum(1 for r in results if r.is_fn)
    fps = sum(1 for r in results if r.is_fp)
    parse_errors = sum(1 for r in results if r.error)
    sev = sum(r.severity_score for r in results) / n
    asymmetric = 1.0 - ((FN_WEIGHT * fns + FP_WEIGHT * fps) / (n * FN_WEIGHT))
    asymmetric = max(0.0, min(1.0, asymmetric))

    need_tool = [r for r in results if r.expect_tool_call and r.error is None]
    tool_recall = None
    if need_tool:
        hits = sum(1 for r in need_tool if "fetch_recent_metrics" in r.tool_calls)
        tool_recall = hits / len(need_tool)

    return {
        "n": n,
        "act_now_accuracy": correct / n,
        "fn_rate": fns / n,
        "fp_rate": fps / n,
        "fn_count": fns,
        "fp_count": fps,
        "asymmetric_score": asymmetric,
        "severity_score": sev,
        "parse_errors": parse_errors,
        "tool_call_recall": tool_recall,
        "fn_weight": FN_WEIGHT,
        "fp_weight": FP_WEIGHT,
    }
