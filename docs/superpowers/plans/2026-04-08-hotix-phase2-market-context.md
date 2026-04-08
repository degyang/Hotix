# Hotix Phase II Market Context Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver Phase II of Hotix by expanding the market panel, introducing a market context layer, standardizing real-code index identifiers, and preparing the engine for later validation/reporting work.

**Architecture:** Phase II is an extension of the existing configuration-driven Python rules engine. It broadens the panel with a curated set of code-based indices and pair relations, layers deterministic context scoring on top of regime output, and tightens the CLI/data boundary by requiring explicit external data input. Remaining work focuses on replay-oriented validation and richer reporting.

**Tech Stack:** Python 3.12, pytest, pandas, pyyaml, numpy

---

## File Structure

Phase II write targets and responsibilities:

- Modify: `market_system/config/index_registry.yaml`
- Modify: `market_system/dsl/pairs.yaml`
- Modify: `market_system/dsl/relation_tags.yaml`
- Modify: `market_system/dsl/regimes.yaml`
- Create: `market_system/dsl/contexts.yaml`
- Modify: `market_system/engine/loader.py`
- Modify: `market_system/engine/expression.py`
- Modify: `market_system/engine/resolver.py`
- Create: `market_system/engine/context_engine.py`
- Modify: `market_system/engine/validator.py`
- Modify: `market_system/engine/pipeline.py`
- Modify: `market_system/engine/output_writer.py`
- Modify: `market_system/engine/debug_report.py`
- Modify: `market_system/run_daily.py`
- Create: `market_system/paths.py`
- Modify: `market_system/tests/conftest.py`
- Modify: `market_system/tests/unit/test_expression.py`
- Modify: `market_system/tests/unit/test_validator.py`
- Modify: `market_system/tests/unit/test_loader.py`
- Modify: `market_system/tests/unit/test_context_engine.py`
- Modify: `market_system/tests/unit/test_debug_report.py`
- Modify: `market_system/tests/unit/test_pair_engine.py`
- Modify: `market_system/tests/integration/test_pipeline.py`
- Modify: `market_system/tests/golden/test_golden_daily.py`
- Modify: `market_system/tests/fixtures/expected_daily_2026-04-03.json`
- Create or refresh: `market_system/tests/fixtures/*.csv`
- Create: `docs/superpowers/specs/2026-04-08-hotix-phase2-market-context-design.md`
- Create: `docs/superpowers/plans/2026-04-08-hotix-phase2-market-context.md`

## Implementation Status

Already completed in the current codebase:

- [x] Context DSL and context engine
- [x] Context output in pipeline and reports
- [x] Debug output for index, pair, and market context inspection
- [x] CLI `--data-dir` and `--latest`
- [x] Package-directory CLI execution support
- [x] Explicit runtime data source requirement
- [x] Core panel expansion to 8 indices
- [x] Code-based ID migration
- [x] TDD coverage and golden refresh for delivered behavior

Remaining completion scope for full Phase II:

- [ ] Replay-oriented validation commands or modules
- [ ] Regime/context distribution reporting
- [ ] Formal calibration workflow docs and outputs
- [ ] Phase III consumer-facing interface notes

## Task 1: Add Phase II Context Layer

**Files:**
- Create: `market_system/dsl/contexts.yaml`
- Create: `market_system/engine/context_engine.py`
- Modify: `market_system/engine/pipeline.py`
- Modify: `market_system/engine/output_writer.py`
- Test: `market_system/tests/unit/test_context_engine.py`
- Test: `market_system/tests/integration/test_pipeline.py`

- [x] **Step 1: Write the failing tests**

Add assertions that:

- `payload["market"]["market_context"]` exists
- context output contains `label`, `allowed_styles`, `disallowed_styles`, `risk_budget`, and `evidence`
- markdown output contains a dedicated market context section

- [x] **Step 2: Run targeted tests to verify they fail**

Run:

```bash
pytest -q market_system/tests/unit/test_context_engine.py market_system/tests/integration/test_pipeline.py
```

Expected before implementation: missing `market_context` assertions fail.

- [x] **Step 3: Implement the minimal context layer**

Implement:

- `contexts.yaml` with `Offense`, `Caution`, `Defense`, `Cash`
- deterministic context scoring in `context_engine.py`
- pipeline integration under `payload["market"]["market_context"]`
- markdown/report exposure

- [x] **Step 4: Run targeted and full tests**

Run:

```bash
pytest -q market_system/tests/unit/test_context_engine.py market_system/tests/integration/test_pipeline.py
pytest -q market_system/tests
```

Expected: PASS

- [x] **Step 5: Commit**

```bash
git add market_system/dsl/contexts.yaml market_system/engine/context_engine.py market_system/engine/pipeline.py market_system/engine/output_writer.py market_system/tests/unit/test_context_engine.py market_system/tests/integration/test_pipeline.py
git commit -m "feat: add phase2 market context layer"
```

## Task 2: Expand the Core Market Panel

**Files:**
- Modify: `market_system/config/index_registry.yaml`
- Modify: `market_system/dsl/pairs.yaml`
- Modify: `market_system/dsl/relation_tags.yaml`
- Test: `market_system/tests/integration/test_pipeline.py`
- Test: `market_system/tests/unit/test_pair_engine.py`

- [x] **Step 1: Write the failing tests**

Add assertions that:

- pipeline returns the full 8-index panel
- pipeline returns the curated 7-pair set
- relation tags can be produced for the newly added structural pairs

- [x] **Step 2: Run targeted tests to verify they fail**

Run:

```bash
pytest -q market_system/tests/unit/test_pair_engine.py market_system/tests/integration/test_pipeline.py
```

Expected before implementation: missing index IDs or pair IDs fail.

- [x] **Step 3: Implement the minimal panel expansion**

Add the following indices:

- `000001`
- `399001`
- `000016`
- `000300`
- `000905`
- `000852`
- `399006`
- `000680`

Add the following pairs:

- `000300_vs_399006`
- `000300_vs_000680`
- `000300_vs_000905`
- `000300_vs_000852`
- `000016_vs_000852`
- `399006_vs_000680`
- `000905_vs_000852`

- [x] **Step 4: Run targeted and full tests**

Run:

```bash
pytest -q market_system/tests/unit/test_pair_engine.py market_system/tests/integration/test_pipeline.py
pytest -q market_system/tests
```

Expected: PASS

- [x] **Step 5: Commit**

```bash
git add market_system/config/index_registry.yaml market_system/dsl/pairs.yaml market_system/dsl/relation_tags.yaml market_system/tests/unit/test_pair_engine.py market_system/tests/integration/test_pipeline.py
git commit -m "feat: expand phase2 market panel and pair coverage"
```

## Task 3: Migrate Runtime IDs to Real Market Codes

**Files:**
- Modify: `market_system/config/index_registry.yaml`
- Modify: `market_system/dsl/regimes.yaml`
- Modify: `market_system/engine/expression.py`
- Modify: `market_system/engine/resolver.py`
- Modify: `market_system/engine/validator.py`
- Modify: `market_system/tests/conftest.py`
- Modify: `market_system/tests/unit/test_expression.py`
- Modify: `market_system/tests/unit/test_validator.py`
- Modify: `market_system/tests/unit/test_loader.py`
- Modify: `market_system/tests/unit/test_debug_report.py`
- Modify: `market_system/tests/unit/test_pair_engine.py`
- Modify: `market_system/tests/unit/test_resolver.py`
- Modify: `market_system/tests/unit/test_context_engine.py`
- Modify: `market_system/tests/integration/test_pipeline.py`

- [x] **Step 1: Write the failing tests**

Add tests that:

- code-based expressions such as `index.000300.trend_state == 'up'` evaluate successfully
- pipeline payload keys use code IDs, not aliases
- debug commands accept code IDs
- registry keys are the real market codes

- [x] **Step 2: Run targeted tests to verify they fail**

Run:

```bash
pytest -q market_system/tests/unit/test_expression.py market_system/tests/unit/test_validator.py market_system/tests/integration/test_pipeline.py
```

Expected before implementation: syntax errors around `index.000300...` and alias-mismatch assertion failures.

- [x] **Step 3: Implement the minimal code-ID migration**

Implement:

- registry and DSL references using real codes
- expression normalization for `index.000300` style references
- resolver support that keeps code-based lookups deterministic
- validator support for normalized expression compilation

- [x] **Step 4: Run targeted and full tests**

Run:

```bash
pytest -q market_system/tests/unit/test_expression.py market_system/tests/unit/test_validator.py market_system/tests/integration/test_pipeline.py
pytest -q market_system/tests
```

Expected: PASS

- [x] **Step 5: Commit**

```bash
git add market_system/config/index_registry.yaml market_system/dsl/regimes.yaml market_system/engine/expression.py market_system/engine/resolver.py market_system/engine/validator.py market_system/tests
git commit -m "refactor: switch phase2 runtime ids to real market codes"
```

## Task 4: Make External Data Input Explicit

**Files:**
- Modify: `market_system/engine/loader.py`
- Modify: `market_system/engine/pipeline.py`
- Modify: `market_system/run_daily.py`
- Create: `market_system/paths.py`
- Test: `market_system/tests/unit/test_loader.py`
- Test: `market_system/tests/integration/test_pipeline.py`

- [x] **Step 1: Write the failing tests**

Add tests that:

- `--data-dir` loads symbol-named CSV files
- `--latest` chooses the latest common trading date
- CLI refuses to run without `--data-dir`
- `python run_daily.py` works from inside `market_system/`
- loader accepts vendor schema columns like `datetime`, `vol`, `up_count`, `down_count`

- [x] **Step 2: Run targeted tests to verify they fail**

Run:

```bash
pytest -q market_system/tests/unit/test_loader.py market_system/tests/integration/test_pipeline.py
```

Expected before implementation: CLI and loader assertions fail.

- [x] **Step 3: Implement the minimal external data boundary**

Implement:

- symbol-aware CSV path resolution
- schema normalization in `load_csv_data`
- `build_context(..., data_dir=...)` as the only runtime path
- CLI `--latest`
- CLI requirement that `--data-dir` be explicit
- stable package-root resolution for package-directory execution

- [x] **Step 4: Run targeted and full tests**

Run:

```bash
pytest -q market_system/tests/unit/test_loader.py market_system/tests/integration/test_pipeline.py
pytest -q market_system/tests
```

Expected: PASS

- [x] **Step 5: Commit**

```bash
git add market_system/engine/loader.py market_system/engine/pipeline.py market_system/run_daily.py market_system/paths.py market_system/tests/unit/test_loader.py market_system/tests/integration/test_pipeline.py
git commit -m "feat: require explicit external data input for phase2 cli"
```

## Task 5: Refresh Fixtures and Golden Baseline

**Files:**
- Modify: `market_system/tests/fixtures/*.csv`
- Modify: `market_system/tests/fixtures/expected_daily_2026-04-03.json`
- Modify: `market_system/tests/golden/test_golden_daily.py`

- [x] **Step 1: Write or update the failing golden assertion**

Ensure the golden test compares the full updated payload for the current fixture date:

```bash
pytest -q market_system/tests/golden/test_golden_daily.py
```

Expected before refresh: payload mismatch.

- [x] **Step 2: Regenerate fixtures and golden payload**

Refresh:

- code-named fixture CSV files
- common-date expectation
- golden sample for `2026-04-03`

- [x] **Step 3: Run targeted and full tests**

Run:

```bash
pytest -q market_system/tests/golden/test_golden_daily.py
pytest -q market_system/tests
```

Expected: PASS

- [x] **Step 4: Commit**

```bash
git add market_system/tests/fixtures market_system/tests/golden/test_golden_daily.py
git commit -m "test: refresh phase2 fixtures and golden baseline"
```

## Task 6: Add Remaining Validation and Reporting Hooks

**Files:**
- Create: `market_system/engine/validation_report.py`
- Modify: `market_system/engine/pipeline.py`
- Modify: `market_system/run_daily.py`
- Create: `market_system/tests/unit/test_validation_report.py`
- Create: `market_system/tests/integration/test_validation_cli.py`

- [ ] **Step 1: Write the failing tests**

Add tests for:

- replay window statistics by `market_regime`
- context label frequency report
- relation tag hit counts
- CLI output for a validation summary command

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
pytest -q market_system/tests/unit/test_validation_report.py market_system/tests/integration/test_validation_cli.py
```

Expected: missing module or missing command failures.

- [ ] **Step 3: Implement the minimal validation/reporting layer**

Implement:

- a replay helper that runs the pipeline across a date range
- summary aggregation by regime, context, and relation tags
- a CLI command or flag that emits a compact validation report

- [ ] **Step 4: Run targeted and full tests**

Run:

```bash
pytest -q market_system/tests/unit/test_validation_report.py market_system/tests/integration/test_validation_cli.py
pytest -q market_system/tests
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/engine/validation_report.py market_system/run_daily.py market_system/tests/unit/test_validation_report.py market_system/tests/integration/test_validation_cli.py
git commit -m "feat: add phase2 validation and reporting hooks"
```

## Task 7: Document Phase II for Future Workers

**Files:**
- Create: `docs/superpowers/specs/2026-04-08-hotix-phase2-market-context-design.md`
- Create: `docs/superpowers/plans/2026-04-08-hotix-phase2-market-context.md`

- [x] **Step 1: Write the design document**

Capture:

- goals
- scope
- architecture
- module boundaries
- testing strategy
- milestone status

- [x] **Step 2: Write the implementation plan**

Capture:

- exact files
- TDD task sequence
- current completion state
- remaining Phase II work

- [x] **Step 3: Verify the docs exist**

Run:

```bash
ls docs/superpowers/specs docs/superpowers/plans
```

Expected: both new files are present.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-04-08-hotix-phase2-market-context-design.md docs/superpowers/plans/2026-04-08-hotix-phase2-market-context.md
git commit -m "docs: add phase2 design and implementation plan"
```

## Self-Review

Spec coverage vs Phase II requirements:

- panel expansion: covered
- context layer: covered
- explicit runtime data boundary: covered
- code-based identifiers: covered
- validation/reporting hooks: covered as remaining work

Placeholder scan:

- no `TODO`, `TBD`, or deferred pseudocode placeholders in task steps

Type consistency:

- file paths, runtime payload names, and CLI flags match the current codebase naming
- current plan status matches the implemented Phase II features and leaves validation/reporting explicitly unchecked

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-08-hotix-phase2-market-context.md`. Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, fast iteration
2. Inline Execution - Execute tasks in this session using executing-plans, batch execution with checkpoints
