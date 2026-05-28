# Development Guide

This guide covers the current development workflow for Hotix after the package restructuring.

## Environment

```bash
cd /Users/mac/Projects/Hotix
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
```

Use the virtual environment command explicitly when needed:

```bash
.venv/bin/python -m pytest
.venv/bin/hotix --date 2026-04-03 --data-dir tests/fixtures
```

## Quality Checks

Run these before claiming a change is complete:

```bash
python3 -m pytest
python3 -m ruff check .
python3 -m ruff format --check .
```

The default pytest configuration:

- discovers tests under `tests/`
- adds `src` to `PYTHONPATH`
- excludes `external` tests
- uses strict marker validation

## Test Categories

```text
tests/unit/          focused engine behavior
tests/integration/   pipeline and CLI behavior
tests/golden/        full payload regression checks
tests/fixtures/      deterministic sample CSV and expected JSON
```

Run a focused test:

```bash
python3 -m pytest tests/unit/test_loader.py
```

Run an external-data test explicitly:

```bash
python3 -m pytest -m external
```

The external test reads real local data from:

```text
~/data/index/daily
```

It should not assert a fixed latest date. It computes the latest common date from the loaded files and verifies the current output contract against that real dataset.

## Adding Or Changing Rules

When changing DSL behavior:

1. Update the relevant YAML file in `src/hotix/dsl/`.
2. Add or update validator coverage in `tests/unit/test_validator.py`.
3. Add focused engine tests for the affected engine.
4. Update integration or golden output if the final payload changes intentionally.

Important DSL files:

```text
features.yaml
states.yaml
patterns.yaml
transitions.yaml
salience.yaml
pairs.yaml
pair_features.yaml
pair_states.yaml
relation_tags.yaml
regimes.yaml
contexts.yaml
policies.yaml
universes.yaml
```

For `salience.yaml`, every scoring rule must include:

```text
id
group
when
score
bucket
polarity
reason
dimension
category
```

Optional Salience v2 fields include `severity`, `confidence`, `freshness`, `evidence_fields`, and `tags`. Engine tests should cover both the legacy score buckets and the structured `salience.items` output when these rules change.

For `universes.yaml`, every universe must include `id`, `name`, `type`, `role`, and a non-empty `members` list. Members must reference ids from `config/index_registry.yaml`.

## Adding A New Index

1. Add the index to `src/hotix/config/index_registry.yaml`.
2. Add a fixture CSV in `tests/fixtures/` if tests should cover it.
3. Ensure every test fixture date needed by integration tests exists for the new index.
4. Update pair DSL if the new index participates in pair logic.
5. Update expected golden output if the market payload changes.

## Changing CLI Behavior

CLI behavior is tested in:

```text
tests/integration/test_pipeline.py
```

If changing `src/hotix/run_daily.py`, update:

- `README.md`
- `docs/Quickstart.md`
- `docs/CLI.md`

## Generated Files

These are local generated artifacts and should not be committed:

```text
.venv/
.pytest_cache/
.ruff_cache/
.mypy_cache/
outputs/
**/__pycache__/
src/hotix.egg-info/
```

## Current Package Name

Use:

```text
hotix
```

Do not add new imports or commands using:

```text
market_system
```

Older docs may mention `market_system` as historical context only.
