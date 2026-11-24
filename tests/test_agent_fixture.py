import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def fixture_mode(monkeypatch):
    monkeypatch.setenv("OPENTRIAGE_MODE", "fixture")
    monkeypatch.setenv(
        "OPENTRIAGE_FIXTURES", str(ROOT / "data" / "fixtures" / "outputs.json")
    )


def test_triage_fixture_outage():
    from opentriage.agent import TriageAgent

    agent = TriageAgent()
    decision = agent.triage(
        "[PAGER] postgres-primary down",
        case_id="t01",
    )
    assert decision.act_now is True
    assert decision.severity == 4


def test_tool_call_when_need_metrics():
    from opentriage.agent import TriageAgent

    agent = TriageAgent()
    decision = agent.triage("sparse cpu alert", case_id="t15")
    assert "fetch_recent_metrics" in decision.tool_calls
