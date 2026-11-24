from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TriageDecision(BaseModel):
    """Structured output of the triage agent."""

    act_now: bool = Field(description="Whether a human should act immediately")
    severity: int = Field(ge=1, le=4, description="1=low … 4=critical")
    reasoning: str = Field(description="Short rationale for the decision")
    suggested_action: str = Field(description="Concrete next step for the on-call")
    tool_calls: list[str] = Field(
        default_factory=list,
        description="Names of tools invoked during this triage turn",
    )


class MetricsSnapshot(BaseModel):
    alert_id: str
    cpu_pct: list[float]
    error_rate: list[float]
    p95_latency_ms: list[float]
    notes: Optional[str] = None
