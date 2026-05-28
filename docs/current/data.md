# Data Contract

Hotix reads daily index CSV files from the directory passed to `--data-dir`.

## Registry

Registered indices live in:

```text
src/hotix/config/index_registry.yaml
```

## Universes

Configured analysis groups live in:

```text
src/hotix/dsl/universes.yaml
```

Every universe member must be a registered index id. Universe profiles are derived from the already-computed index runtimes, so they do not introduce a second data-loading path.

The built-in universes are:

- `broad_indices`: all currently registered index proxies.
- `growth_proxy`: the growth-oriented subset `399006` and `000680`.

Each registry entry has an index id and a `symbol`. The loader searches for CSV files in this order:

1. `<symbol>.csv`
2. `<index_id>.csv`

For example, an index with id `000300` and symbol `000300` can be loaded from:

```text
tests/fixtures/000300.csv
```

## Required Columns

After normalization, every CSV must contain:

```text
date, open, high, low, close, volume, amount, adv, decl
```

Column meanings:

- `date`: trading date
- `open`: open price
- `high`: high price
- `low`: low price
- `close`: close price
- `volume`: traded volume
- `amount`: traded amount
- `adv`: advancing constituent count or breadth numerator
- `decl`: declining constituent count or breadth denominator component

## Accepted Input Aliases

The loader normalizes these vendor-style fields:

```text
datetime -> date
vol -> volume
up_count -> adv
down_count -> decl
```

Date values are parsed by pandas with mixed date formats and normalized to:

```text
YYYY-MM-DD
```

Rows are sorted by date after loading.

## Common Date Rule

Pipeline runs operate only on dates that exist in every registered index DataFrame.

`--latest` means:

```text
the max date in the intersection of all registered index dates
```

If a date exists for one index but not another, `run_single_date` rejects it.

## Fixture Data

Fixture CSV files live in:

```text
tests/fixtures/
```

These files are deterministic sample data for tests and local demonstrations. They are not production market data.

## Real Data

To run against real data:

1. Create a directory containing one CSV per registered index.
2. Ensure each CSV satisfies the normalized column contract.
3. Pass that directory with `--data-dir`.

Example:

```bash
hotix --latest --data-dir ~/data/index/daily --dump-json
```

Tests that depend on a local real-data directory are marked `external` and are excluded by the default pytest command.

The external test computes the latest common date dynamically and verifies that real data can produce both structured salience and the `broad_indices` universe profile.
