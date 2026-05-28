# CLI Reference

Hotix exposes one console script:

```bash
hotix
```

The script calls `hotix.run_daily:main`.

The CLI reports observed market structure only. It does not forecast, backtest, generate buy/sell signals, recommend positions, or execute trades.

## Required Data Argument

Every normal run requires `--data-dir`.

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures
```

The CLI does not silently fall back to fixture data. This prevents accidental production runs against sample files.

## Date Selection

Run one explicit date:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures
```

Run the latest common date across all registered index CSV files:

```bash
hotix --latest --data-dir tests/fixtures
```

Run a date range:

```bash
hotix --start 2026-04-02 --end 2026-04-03 --data-dir tests/fixtures
```

If only `--start` or only `--end` is supplied, the range is open on the missing side.

## Output Modes

Compact JSON summary:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures
```

Full JSON payload:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --dump-json
```

The full payload includes `universes` and `market.market_profile` for the market-structure summary.

Write JSON and Markdown reports:

```bash
hotix --start 2026-04-02 --end 2026-04-03 --data-dir tests/fixtures --write-files
```

Report paths:

```text
outputs/json/YYYY-MM-DD.json
outputs/markdown/YYYY-MM-DD.md
```

## Debug Modes

Index debug payload:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-index 000300
```

Pair debug payload:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-pair 000300_vs_399006
```

Market debug payload:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures --debug-market
```

Debug flags operate on a single target date. If `--write-files` is also provided, the normal report for that date is written before the debug payload is printed.

## Module Entry

For source-tree execution without installing the console script:

```bash
PYTHONPATH=src python3 -m hotix.run_daily --date 2026-04-03 --data-dir tests/fixtures
```

## Exit Behavior

The CLI exits with a message when:

- `--data-dir` is omitted
- no date selector is supplied
- the requested date is not available as a common date across all registered indices
- a required CSV file is missing
- a YAML DSL file fails validation
