# Hotix Documentation

This directory contains both current operational documentation and historical design records.

## Current Docs

Use these documents for current commands, paths, and development workflow:

- [Quickstart](Quickstart.md): fastest way to install and run the engine
- [CLI Reference](CLI.md): command options and output modes
- [Architecture](Architecture.md): package layout, pipeline flow, and engine boundaries
- [Data Contract](Data.md): CSV format, registry behavior, and fixture data
- [Development Guide](Development.md): tests, linting, generated files, and change workflow
- [Historical Notes](Historical-Notes.md): how to translate old `market_system` references

The root [README](../README.md) is the top-level project overview.

## Current Canonical Facts

Package:

```text
hotix
```

Source:

```text
src/hotix/
```

Tests:

```text
tests/
```

Install:

```bash
python3 -m pip install -e ".[dev]"
```

Run:

```bash
hotix --date 2026-04-03 --data-dir tests/fixtures
```

Verify:

```bash
python3 -m pytest
python3 -m ruff check .
python3 -m ruff format --check .
```

## Historical Docs

The following directories contain historical planning, requirements, and setup records:

```text
docs/SRS/
docs/superpowers/
docs/ecc/
```

They are useful for understanding product intent and previous implementation phases, but they may contain old paths or commands. In particular, `market_system` is no longer a live package or command.

When historical docs conflict with current docs, follow the current docs.
