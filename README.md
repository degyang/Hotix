# Hotix

Hotix is a rules-and-DSL market structure analysis engine. It reads index CSV data, evaluates YAML-defined market structure rules, and outputs JSON or Markdown summaries for a single date or date range.

## Project Structure

```text
Hotix/
├─ src/hotix/
│  ├─ config/          # index registry
│  ├─ dsl/             # feature, state, regime, context, and policy rules
│  ├─ engine/          # core market analysis pipeline
│  ├─ paths.py         # package path constants
│  └─ run_daily.py     # CLI entry module
├─ tests/
│  ├─ fixtures/        # deterministic sample CSV data and golden output
│  ├─ golden/
│  ├─ integration/
│  └─ unit/
├─ docs/
└─ pyproject.toml
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
```

## Run

Use the fixture data:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures
hotix --date 2026-04-03 --data-dir tests/fixtures --dump-json
hotix --latest --data-dir tests/fixtures --dump-json
```

Write JSON and Markdown files under `src/hotix/outputs/`:

```bash
hotix --start 2026-04-02 --end 2026-04-03 --data-dir tests/fixtures --write-files
```

Debug a specific payload:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-index 000300
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-pair 000300_vs_399006
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-market
```

The module entry still works during development:

```bash
PYTHONPATH=src python3 -m hotix.run_daily --date 2026-04-03 --data-dir tests/fixtures
```

## Data Format

CSV files must provide these normalized columns:

```text
date, open, high, low, close, volume, amount, adv, decl
```

External vendor-style columns are also normalized by the loader:

```text
datetime -> date
vol -> volume
up_count -> adv
down_count -> decl
```

Each index in `src/hotix/config/index_registry.yaml` must have a matching CSV file in the data directory, named either by its `symbol` or index id.

## Test

```bash
python3 -m pytest
```

Tests marked `external` depend on a local data directory and are not part of the default fixture-based workflow.
