# Historical Notes

Hotix previously used `market_system` as the source package and nested its tests under `market_system/tests`.

The current structure is:

```text
src/hotix/
tests/
```

The current command is:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures
```

The old command no longer exists:

```bash
python3 -m market_system.run_daily
```

## How To Read Older Documents

Some older documents under these directories are design records or implementation plans:

```text
docs/SRS/
docs/superpowers/specs/
docs/superpowers/plans/
docs/ecc/
```

They may still mention:

- `market_system/`
- `market_system/tests`
- `market_system/requirements.txt`
- `python3 -m market_system.run_daily`
- `src/hotix/models/user.py`
- FastAPI, SQLAlchemy, Redis, or user-registration examples

Treat those references as historical unless they are repeated in the current operational docs:

- `README.md`
- `docs/README.md`
- `docs/Quickstart.md`
- `docs/CLI.md`
- `docs/Architecture.md`
- `docs/Data.md`
- `docs/Development.md`

## Path Mapping

Use this mapping when translating older notes:

```text
market_system/                       -> src/hotix/
market_system/tests/                 -> tests/
market_system/tests/fixtures/        -> tests/fixtures/
market_system/config/index_registry.yaml -> src/hotix/config/index_registry.yaml
market_system/dsl/                   -> src/hotix/dsl/
market_system/engine/                -> src/hotix/engine/
market_system/run_daily.py           -> src/hotix/run_daily.py
python3 -m market_system.run_daily   -> hotix
python3 -m pytest market_system/tests -q -> python3 -m pytest
```

## ECC Documents

The `docs/ecc/` files describe an older Claude/ECC workflow and a generic Python/FastAPI project shape. They are not the current runtime guide for the market analysis engine.

Use them only for process ideas, not for current file paths or commands.
