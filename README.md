# Hotix

Hotix is a Python rules-and-DSL market structure analysis engine. It loads index CSV data, evaluates YAML-defined rules, and produces structured JSON or Markdown summaries for one date or a date range.

Hotix is a market follower, not a market predictor. It does not forecast future returns, run backtests, generate buy/sell signals, recommend positions, or execute trades.

Current package name: `hotix`

Deprecated package name: `market_system`

## What It Does

Hotix currently supports:

- loading registered index CSV files from an explicit `--data-dir`
- calculating index features, states, pattern tags, transition tags, and salience
- building universe profiles and a market profile from observed structure
- calculating pair features, pair states, and relation tags
- scoring market regime, market context, and policy permissions
- printing compact or full JSON payloads
- writing JSON and Markdown daily reports
- producing debug payloads for an index, a pair, or the market layer

## Repository Layout

```text
Hotix/
├─ src/hotix/
│  ├─ config/                 # index registry
│  ├─ dsl/                    # YAML rule definitions
│  ├─ engine/                 # core loading, validation, scoring, output logic
│  ├─ paths.py                # package path constants
│  ├─ py.typed                # typing marker
│  └─ run_daily.py            # CLI module and console-script target
├─ tests/
│  ├─ fixtures/               # deterministic sample CSV data and golden output
│  ├─ golden/
│  ├─ integration/
│  └─ unit/
├─ docs/
│  ├─ README.md               # documentation map
│  ├─ Quickstart.md           # fastest operational path
│  ├─ Architecture.md         # code and data-flow overview
│  ├─ CLI.md                  # command reference
│  ├─ Data.md                 # input data contract
│  ├─ Development.md          # development and verification workflow
│  └─ Historical-Notes.md     # how to read older design docs
└─ pyproject.toml             # package metadata, dependencies, pytest, ruff, mypy
```

## Install

Use an activated virtual environment so the project-local `hotix` command is used instead of any system command with the same name.

```bash
cd /Users/mac/Projects/Hotix
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
```

If you do not activate the environment, run the CLI explicitly:

```bash
.venv/bin/hotix --date 2026-04-03 --data-dir tests/fixtures
```

## Quick Run

Run a compact market summary from fixture data:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures
```

Run the latest common date available across all registered fixture CSV files:

```bash
hotix --latest --data-dir tests/fixtures --dump-json
```

Print the full payload:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --dump-json
```

Write JSON and Markdown reports:

```bash
hotix --start 2026-04-02 --end 2026-04-03 --data-dir tests/fixtures --write-files
```

Generated files are written under:

```text
outputs/json/
outputs/markdown/
```

## Debug Commands

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-index 000300
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-pair 000300_vs_399006
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-market
```

The module entry is also available:

```bash
PYTHONPATH=src python3 -m hotix.run_daily --date 2026-04-03 --data-dir tests/fixtures
```

## Data Contract

Each CSV must provide these normalized columns:

```text
date, open, high, low, close, volume, amount, adv, decl
```

The loader also normalizes these external field names:

```text
datetime -> date
vol -> volume
up_count -> adv
down_count -> decl
```

Every index in `src/hotix/config/index_registry.yaml` must have a matching CSV file in `--data-dir`. The file can be named by either the registry `symbol` or the index id.

## Verify

```bash
python3 -m pytest
python3 -m ruff check .
python3 -m ruff format --check .
```

The default test run excludes tests marked `external`; those depend on a local, non-fixture market data directory.

## Documentation

- [Documentation Map](docs/README.md)
- [Quickstart](docs/Quickstart.md)
- [CLI Reference](docs/CLI.md)
- [Architecture](docs/Architecture.md)
- [Data Contract](docs/Data.md)
- [Development Guide](docs/Development.md)
- [Historical Notes](docs/Historical-Notes.md)

Older SRS, ECC, and superpowers plan/spec documents may mention `market_system`. Treat those as historical context unless a current document above says otherwise.
