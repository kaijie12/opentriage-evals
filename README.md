# OpenTriage-Evals

> An open-source **evaluation harness** for an LLM **on-call / alert-triage agent** — golden set,
> LLM-as-judge with human calibration, trajectory + red-team + robustness suites, model cost/quality
> comparison, and a **CI regression gate** with Langfuse observability.

**The agent is the crash-test dummy. The eval harness + gate + dashboard is the crash-test lab — and the lab is the point.**
This project demonstrates how you actually *know* an AI agent is good and safe to ship, not just that one was built.

### 📊 [View the design diagram →](https://kaijie12.github.io/opentriage-evals/)

*(live on GitHub Pages — the one-screen visual of how every piece fits together)*

---

## What's here

| File | What it is |
|---|---|
| [`PLAN.md`](PLAN.md) | The full build plan — infra, data sources, 6 phases, the 8 eval suites |
| [`docs/index.html`](docs/index.html) | The design diagram (rendered live via the Pages link above) |

## The core idea in one table

A tiny agent turns an alert/log window into `{act_now, severity 1–4, reasoning, action}`. It exists only
to be measured. The real work is the **8 eval suites** that grade it against a 120–150 item golden set:

| # | Suite | Proves |
|---|---|---|
| 1 | Decision accuracy + **asymmetric FN/FP** | cost-aware correctness |
| 2 | **LLM-as-judge** + calibration vs human labels | can you trust the judge |
| 3 | Severity classification (ordinal) | right metric, not just accuracy |
| 4 | **Trajectory / tool-use** | agent-level evaluation |
| 5 | **Safety / red-team** (prompt injection) | unsafe-action testing |
| 6 | Robustness (paraphrase / noise) | stability under drift |
| 7 | **Model comparison** (quality × cost × latency) | tradeoff thinking |
| 8 | **Regression gate** in CI | eval-driven development — the headline |

## Built to be reproducible on a laptop

No proprietary data, no cloud account. **Ollama** (open-weight LLMs) + **DeepEval/Promptfoo** +
**Langfuse** (Docker) + **GitHub Actions**. Everything runs locally.

## Status

🚧 Planning → scaffolding. See [`PLAN.md`](PLAN.md) for the roadmap.
