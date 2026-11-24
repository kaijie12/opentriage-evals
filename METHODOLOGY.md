# Methodology

How OpenTriage-Evals **measures** triage-agent performance — and what the numbers mean.

## What is under test

A small on-call triage agent maps an alert/log window to:

```json
{"act_now": true, "severity": 1-4, "reasoning": "...", "suggested_action": "..."}
```

It may call one mock tool, `fetch_recent_metrics`, when corroboration is needed. The agent is the crash-test dummy. The harness is the product.

## Golden set

- **Size (v0):** 35 labeled cases (25 train / 10 test), ~synthetic public-pattern alerts — no proprietary data.
- **Rubric:** [`data/golden/RUBRIC.md`](data/golden/RUBRIC.md) — two labelers should agree on `act_now`; severity may be off-by-one at boundaries.
- **Stratification:** mix of `act_now` true/false and severities 1–4; enforced by `make split-check`.
- **Growth path:** same JSONL schema toward 120–150 items (Loghub / public post-mortems / controlled synthetic edge cases).

## Suite 1 — Decision accuracy + asymmetric FN/FP

| Metric | Definition |
| --- | --- |
| `act_now_accuracy` | Exact match on `act_now` |
| `fn_rate` / `fp_rate` | Missed real pages / false pages, over N |
| `asymmetric_score` | `1 - (3·FN + 1·FP) / (N·3)` — **false negatives cost 3× false positives** |
| `severity_score` | Mean ordinal score: 1.0 exact, 0.5 off-by-one, else 0 |

**Why asymmetric:** missing a real incident is worse than waking someone for noise. The gate tracks FN rate explicitly so a “more conservative” prompt that stops paging cannot look like an improvement on raw accuracy alone.

## Suite 2 — LLM-as-judge + calibration

A judge model scores reasoning quality (0–3) and states whether it agrees with the human `act_now` label. We report:

- mean reasoning score (normalized 0–1)
- **judge ↔ human agreement** on `act_now` (calibration)

In fixture mode, judge outputs are checked into `data/fixtures/outputs.json` under `judge::<case_id>` so CI stays deterministic. Live judging uses Ollama (`OPENTRIAGE_MODE=live`).

## Suite 8 — CI regression gate

`evals/baselines.json` stores minimum `act_now_accuracy` / `asymmetric_score` / `severity_score` and maximum `fn_rate` (fixture test-split bar: **0 FN allowed**).

```bash
make eval-ci   # test split + fixture mode + gate
```

GitHub Actions runs the same command on every PR. **Fail the build** if accuracy drops or FN rate rises past the baseline.

### How to demo a failing gate

1. Edit a test-split fixture in `data/fixtures/outputs.json` so a true `act_now` case returns `false` (inject an FN).
2. Run `make eval-ci` — expect non-zero exit and an `fn_rate` failure.
3. Revert the fixture.

### How to raise baselines after a real improvement

1. Improve the prompt or model; refresh fixtures from live runs if needed.
2. Run `make eval` / `make eval-ci` and confirm metrics moved for the right reason.
3. Update `evals/baselines.json` in the same PR with a short note — never lower a bar to silence a regression.

## Local vs CI

| Mode | Env | Use |
| --- | --- | --- |
| Fixture (default) | `OPENTRIAGE_MODE=fixture` | CI, unit tests, laptop without Ollama |
| Live | `OPENTRIAGE_MODE=live` + Ollama | Real model measurement |

```bash
ollama pull llama3.2
OPENTRIAGE_MODE=live OPENTRIAGE_MODEL=llama3.2 make eval
```

## Limitations (say these in interviews)

- v0 golden set is small and mostly synthetic — good for wiring the lab, not for claiming production-grade coverage.
- Fixture mode measures harness + gate correctness; live mode measures the model.
- Judge calibration on fixtures is illustrative until refreshed against a live judge and held-out humans.
- Suites 3–7 (deep severity, trajectory depth, red-team, robustness, model Pareto) and Langfuse are roadmap items in [`PLAN.md`](PLAN.md).

## What “good” looks like for this repo

A reviewer can clone, run `make eval-ci`, see a scorecard, and understand from this file **what would fail a PR and why FN is weighted harder than FP**.
