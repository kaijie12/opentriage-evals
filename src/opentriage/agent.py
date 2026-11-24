"""Specimen triage agent — exists to be measured."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional, Union

from opentriage.llm import complete
from opentriage.models import TriageDecision
from opentriage.tools import fetch_recent_metrics

PromptSource = Union[str, Path]

_PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "triage_v1.txt"


class TriageAgent:
    def __init__(self, prompt_path: Optional[PromptSource] = None) -> None:
        path = Path(prompt_path) if prompt_path else _PROMPT_PATH
        self.prompt_template = path.read_text()

    def triage(self, alert: str, *, case_id: Optional[str] = None) -> TriageDecision:
        prompt = self.prompt_template.replace("{{ALERT}}", alert.strip())
        raw = complete(prompt, fixture_key=case_id)
        draft = self._parse(raw)

        tool_calls: list[str] = []
        if draft.pop("_need_metrics", False):
            metrics = fetch_recent_metrics(case_id or "unknown")
            tool_calls.append("fetch_recent_metrics")
            follow = (
                prompt
                + "\n\nTool result fetch_recent_metrics:\n"
                + json.dumps(metrics)
                + "\n\nRevise your JSON decision using the metrics. "
                "Do not include need_metrics."
            )
            # Fixture mode: second call uses case_id + "::metrics" if present,
            # else reuses the same fixture (already final).
            follow_key = f"{case_id}::metrics" if case_id else None
            try:
                raw2 = complete(follow, fixture_key=follow_key or case_id)
                draft = self._parse(raw2)
            except Exception:
                # Keep first draft if follow-up fixture missing.
                pass

        return TriageDecision(
            act_now=bool(draft["act_now"]),
            severity=int(draft["severity"]),
            reasoning=str(draft["reasoning"]),
            suggested_action=str(draft["suggested_action"]),
            tool_calls=tool_calls,
        )

    def _parse(self, raw: str) -> dict:
        data = _extract_json(raw)
        need = bool(data.get("need_metrics", False))
        severity = int(data.get("severity", 2))
        severity = max(1, min(4, severity))
        return {
            "act_now": bool(data.get("act_now", False)),
            "severity": severity,
            "reasoning": str(data.get("reasoning", "")).strip() or "no reasoning",
            "suggested_action": str(data.get("suggested_action", "")).strip()
            or "review alert",
            "_need_metrics": need,
        }


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise ValueError(f"Model output is not JSON: {raw[:200]!r}")
        return json.loads(match.group(0))


# Re-export for convenience
__all__ = ["TriageAgent", "TriageDecision"]
