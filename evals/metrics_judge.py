"""Suite 2 — LLM-as-judge on reasoning + calibration vs human labels."""

from __future__ import annotations

import json
import re
from typing import Any, Optional

from opentriage.llm import LLMError, complete, mode


JUDGE_PROMPT = """You are grading an on-call triage assistant.
Given the alert, the human label, and the model's decision, score the model's reasoning.

Return ONLY JSON:
{{
  "reasoning_score": 0|1|2|3,
  "implied_act_now": true|false,
  "agree_with_human_act_now": true|false,
  "comment": "one sentence"
}}

Scoring:
3 = reasoning cites the decisive signal and matches a sound on-call call
2 = mostly sound but incomplete
1 = weak / generic
0 = contradicts the evidence or invents facts

Alert:
{alert}

Human label: act_now={label_act_now}, severity={label_severity}, rationale={label_rationale}

Model decision: act_now={pred_act_now}, severity={pred_severity}
Model reasoning: {pred_reasoning}
Model action: {pred_action}
"""


def judge_case(
    *,
    case_id: str,
    alert: str,
    label: dict[str, Any],
    pred: dict[str, Any],
) -> dict[str, Any]:
    prompt = JUDGE_PROMPT.format(
        alert=alert,
        label_act_now=label["act_now"],
        label_severity=label["severity"],
        label_rationale=label.get("rationale", ""),
        pred_act_now=pred["act_now"],
        pred_severity=pred["severity"],
        pred_reasoning=pred.get("reasoning", ""),
        pred_action=pred.get("suggested_action", ""),
    )
    fixture_key = f"judge::{case_id}"
    try:
        raw = complete(prompt, fixture_key=fixture_key if mode() == "fixture" else None)
        data = _parse(raw)
    except (LLMError, ValueError, KeyError) as exc:
        return {"case_id": case_id, "error": str(exc)}

    return {
        "case_id": case_id,
        "reasoning_score": int(data.get("reasoning_score", 0)),
        "implied_act_now": bool(data.get("implied_act_now", pred["act_now"])),
        "agree_with_human_act_now": bool(
            data.get("agree_with_human_act_now", False)
        ),
        "comment": str(data.get("comment", "")),
    }


def summarize_judge(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ok = [r for r in rows if "error" not in r]
    if not ok:
        return {
            "n": 0,
            "mean_reasoning_score": 0.0,
            "judge_human_agreement": 0.0,
            "errors": len(rows),
        }
    mean_score = sum(r["reasoning_score"] for r in ok) / len(ok)
    agree = sum(1 for r in ok if r["agree_with_human_act_now"]) / len(ok)
    return {
        "n": len(ok),
        "mean_reasoning_score": mean_score / 3.0,  # normalize 0-1
        "mean_reasoning_score_raw": mean_score,
        "judge_human_agreement": agree,
        "errors": len(rows) - len(ok),
    }


def _parse(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise ValueError(f"Judge output not JSON: {raw[:200]!r}")
        return json.loads(match.group(0))


def ensure_judge_fixtures(
    case_ids: list[str],
    fixture_path: Optional[str] = None,
) -> None:
    """No-op helper placeholder for docs; fixtures are checked into repo."""
    return None
