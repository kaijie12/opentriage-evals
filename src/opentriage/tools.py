"""Mock tools available to the triage agent (for trajectory evals)."""

from __future__ import annotations

from opentriage.models import MetricsSnapshot

# Deterministic canned series keyed by alert id substring hints.
_SERIES = {
    "spike": MetricsSnapshot(
        alert_id="spike",
        cpu_pct=[42, 55, 78, 91, 95],
        error_rate=[0.1, 0.4, 2.1, 8.5, 12.0],
        p95_latency_ms=[120, 180, 400, 900, 1500],
        notes="Sharp error-rate and latency climb over 25m",
    ),
    "flat": MetricsSnapshot(
        alert_id="flat",
        cpu_pct=[31, 33, 30, 32, 31],
        error_rate=[0.2, 0.1, 0.2, 0.15, 0.2],
        p95_latency_ms=[110, 105, 115, 108, 112],
        notes="Stable; no corroborating signal",
    ),
    "default": MetricsSnapshot(
        alert_id="default",
        cpu_pct=[40, 45, 50, 48, 52],
        error_rate=[0.5, 0.7, 1.0, 1.2, 1.1],
        p95_latency_ms=[200, 220, 250, 240, 260],
        notes="Mild upward drift",
    ),
}


def fetch_recent_metrics(alert_id: str) -> dict:
    """Return recent metric windows for an alert id (mock)."""
    key = "default"
    lower = alert_id.lower()
    if any(tok in lower for tok in ("sev1", "outage", "page", "critical", "spike")):
        key = "spike"
    elif any(tok in lower for tok in ("info", "noise", "test", "flat", "flaky")):
        key = "flat"
    snap = _SERIES[key].model_copy(update={"alert_id": alert_id})
    return snap.model_dump()
