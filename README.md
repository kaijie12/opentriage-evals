# OpenTriage-Evals

> An open-source **evaluation harness** for an LLM **on-call / alert-triage agent** — golden set,
> asymmetric FN/FP metrics, LLM-as-judge with human calibration, and a **CI regression gate**.

**The agent is the crash-test dummy. The eval harness + gate is the crash-test lab — and the lab is the point.**

### Design diagram → [kaijie12.github.io/opentriage-evals](https://kaijie12.github.io/opentriage-evals/)

---

## Quickstart

```bash
make install     # creates .venv + editable install
make split-check
make test
make eval        # scorecard (fixture mode by default)
make eval-ci     # test-split + regression gate
```

Scorecard lands in `artifacts/scorecard.json`.

### Live model (optional)

```bash
# requires Ollama: https://ollama.com
ollama pull llama3.2
OPENTRIAGE_MODE=live OPENTRIAGE_MODEL=llama3.2 make eval
```

CI always uses **fixture mode** so the gate needs no API key.

---

## What is measured

| Suite | Metric | Why |
| --- | --- | --- |
| 1 | `act_now` accuracy, FN/FP, **asymmetric score** (FN×3) | Cost-aware correctness |
| 1 | Ordinal severity score | Off-by-one tolerant |
| 2 | Judge reasoning score + judge↔human agreement | Can you trust the judge |
| 8 | CI gate vs `evals/baselines.json` | Eval-driven development |

Details: [`METHODOLOGY.md`](METHODOLOGY.md). Full roadmap: [`PLAN.md`](PLAN.md).

---

## Layout

```
src/opentriage/     # specimen agent + mock fetch_recent_metrics
data/golden/        # rubric + labeled JSONL (train/test)
data/fixtures/      # recorded outputs for CI / laptop-without-GPU
evals/              # suites, runner, baselines, gate
tests/              # unit tests (no live LLM)
.github/workflows/  # PR eval gate
```

---

## Status

Runnable laptop harness: agent · 35-case golden set · suites 1/2/8 · `make eval` scorecard · GitHub Actions gate.

Still growing toward the full [`PLAN.md`](PLAN.md) set (120–150 cases, Langfuse, suites 3–7).
