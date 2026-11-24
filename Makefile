PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip

.PHONY: venv install test eval eval-ci eval-judge split-check

venv:
	python3 -m venv .venv
	$(PIP) install -U pip setuptools wheel

install: venv
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest -q

eval:
	OPENTRIAGE_MODE=$${OPENTRIAGE_MODE:-fixture} \
	OPENTRIAGE_FIXTURES=$${OPENTRIAGE_FIXTURES:-data/fixtures/outputs.json} \
	$(PYTHON) -m evals.runner --split all --judge

eval-ci:
	OPENTRIAGE_MODE=fixture \
	OPENTRIAGE_FIXTURES=data/fixtures/outputs.json \
	$(PYTHON) -m evals.runner --split test --gate

eval-judge:
	OPENTRIAGE_MODE=$${OPENTRIAGE_MODE:-fixture} \
	OPENTRIAGE_FIXTURES=$${OPENTRIAGE_FIXTURES:-data/fixtures/outputs.json} \
	EVAL_JUDGE=1 \
	$(PYTHON) -m evals.runner --split test --judge

split-check:
	$(PYTHON) scripts/split_check.py
