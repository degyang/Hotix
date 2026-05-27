# Hotix Quickstart

This is the shortest path from a fresh checkout to a working market summary.

Hotix describes current market structure. It does not forecast, backtest, generate buy/sell signals, recommend positions, or execute trades.

## 1. Install

```bash
cd /Users/mac/Projects/Hotix
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[dev]"
```

Use `.venv/bin/hotix` directly if another `hotix` command exists on your system.

## 2. Run A Single Date

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures
```

The compact output contains:

- `date`
- `market.date`
- `market.relation_tags`
- `market.top_positive`
- `market.top_negative`
- `market.top_warning`
- `market.top_transition`
- `market.market_regime`
- `market.market_context`
- `market.market_profile`
- `market.policy`
- `market.trace`

## 3. Print Full JSON

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --dump-json
```

Use this when checking index features, states, tags, pair results, policy output, or trace details.

## 4. Use Latest Common Date

```bash
hotix --latest --data-dir tests/fixtures --dump-json
```

`--latest` selects the latest date that exists in every registered index CSV.

## 5. Write Report Files

```bash
hotix --start 2026-04-02 --end 2026-04-03 --data-dir tests/fixtures --write-files
```

Files are written to:

```text
src/hotix/outputs/json/YYYY-MM-DD.json
src/hotix/outputs/markdown/YYYY-MM-DD.md
```

The output directory is generated runtime data. It does not need to be committed.

## 6. Debug Payloads

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-index 000300
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-pair 000300_vs_399006
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-market
```

Use debug output to inspect rule inputs, computed features, states, matched tags, regime evidence, market context, or policy permissions.

## 7. Run Tests

```bash
python3 -m pytest
```

Expected default behavior:

```text
54 passed, 1 deselected
```

The deselected test is marked `external` and depends on a local real-data directory.

## 8. Common Problems

If `hotix --date ...` prints an unexpected error or help text, you may be running a system command instead of this project's console script. Use:

```bash
.venv/bin/hotix --date 2026-04-03 --data-dir tests/fixtures
```

If data loading fails, confirm that every index in `src/hotix/config/index_registry.yaml` has a matching CSV in the data directory.
