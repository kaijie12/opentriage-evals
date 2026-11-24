from evals.metrics_decision import CaseResult, score_results
from evals.gate import check_gate


def test_asymmetric_penalizes_fn_more_than_fp():
    fn = [
        CaseResult("a", True, False, 3, 3, [], False),
        CaseResult("b", True, True, 3, 3, [], False),
    ]
    fp = [
        CaseResult("a", False, True, 2, 2, [], False),
        CaseResult("b", True, True, 3, 3, [], False),
    ]
    fn_score = score_results(fn)["asymmetric_score"]
    fp_score = score_results(fp)["asymmetric_score"]
    assert fn_score < fp_score


def test_severity_ordinal():
    exact = CaseResult("a", True, True, 3, 3, [], False)
    off = CaseResult("b", True, True, 3, 2, [], False)
    far = CaseResult("c", True, True, 1, 4, [], False)
    assert exact.severity_score == 1.0
    assert off.severity_score == 0.5
    assert far.severity_score == 0.0


def test_gate_detects_fn_regression():
    scorecard = {
        "decision": {
            "act_now_accuracy": 1.0,
            "asymmetric_score": 1.0,
            "fn_rate": 0.5,
            "severity_score": 1.0,
        }
    }
    baselines = {
        "min_act_now_accuracy": 0.9,
        "min_asymmetric_score": 0.9,
        "max_fn_rate": 0.0,
        "min_severity_score": 0.9,
    }
    failures = check_gate(scorecard, baselines)
    assert any("fn_rate" in f for f in failures)


def test_gate_passes_clean_scorecard():
    scorecard = {
        "decision": {
            "act_now_accuracy": 1.0,
            "asymmetric_score": 1.0,
            "fn_rate": 0.0,
            "severity_score": 1.0,
        }
    }
    baselines = {
        "min_act_now_accuracy": 0.9,
        "min_asymmetric_score": 0.9,
        "max_fn_rate": 0.0,
        "min_severity_score": 0.9,
    }
    assert check_gate(scorecard, baselines) == []
