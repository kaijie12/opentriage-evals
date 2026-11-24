"""Optional DeepEval BaseMetric adapters around suite-1 scoring.

Install with: pip install -e ".[judge]"
CI does not require DeepEval — deterministic metrics in metrics_decision.py
are the source of truth for the regression gate.
"""

from __future__ import annotations

import json
from typing import Optional

try:
    from deepeval.metrics import BaseMetric
    from deepeval.test_case import LLMTestCase
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "deepeval is optional. Install with: pip install -e '.[judge]'"
    ) from exc

from evals.metrics_decision import FN_WEIGHT, FP_WEIGHT


class ActNowExactMatchMetric(BaseMetric):
    def __init__(self, threshold: float = 1.0) -> None:
        self.threshold = threshold
        self.score: Optional[float] = None
        self.success: Optional[bool] = None
        self.reason: Optional[str] = None

    def measure(self, test_case: LLMTestCase) -> float:
        pred = json.loads(test_case.actual_output)
        exp = json.loads(test_case.expected_output)
        self.score = 1.0 if bool(pred.get("act_now")) == bool(exp.get("act_now")) else 0.0
        self.success = self.score >= self.threshold
        self.reason = f"pred={pred.get('act_now')} expected={exp.get('act_now')}"
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return bool(self.success)


class AsymmetricDecisionCostMetric(BaseMetric):
    """Per-case contribution to asymmetric cost (1 if OK, lower if FN/FP)."""

    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold
        self.score: Optional[float] = None
        self.success: Optional[bool] = None
        self.reason: Optional[str] = None

    def measure(self, test_case: LLMTestCase) -> float:
        pred = json.loads(test_case.actual_output)
        exp = json.loads(test_case.expected_output)
        label = bool(exp.get("act_now"))
        got = bool(pred.get("act_now"))
        if label == got:
            self.score = 1.0
            self.reason = "correct"
        elif label and not got:
            self.score = max(0.0, 1.0 - FN_WEIGHT / FN_WEIGHT)  # 0.0 for FN
            self.reason = f"false negative (weight={FN_WEIGHT})"
        else:
            self.score = max(0.0, 1.0 - FP_WEIGHT / FN_WEIGHT)
            self.reason = f"false positive (weight={FP_WEIGHT})"
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return bool(self.success)
