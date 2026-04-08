# Hotix Phase I Engine Design

**Date:** 2026-04-06

**Goal**

Build a robust Phase I market structure engine for three China A-share indices, two pair relationships, and four market regimes. The first version must prioritize rule correctness over breadth, with every important conclusion traceable to rule ids and verified through TDD.

**Scope**

- In scope:
  - `hs300`, `cyb`, `csi1000`
  - `hs300_vs_cyb`, `hs300_vs_csi1000`
  - Daily JSON output
  - Daily Markdown output
  - Feature, state, pattern, transition, salience, pair, relation, and regime evaluation
  - Explainable traces for rule hits
  - Automated tests for engine correctness
- Out of scope:
  - LLM-written commentary
  - Full 8-index coverage
  - Backtesting platform
  - Web UI
  - General-purpose AST engine beyond what Phase I needs

## Architecture

The Phase I system is a configuration-driven rules engine with a small Python runtime. DSL YAML files define features, states, tags, pair logic, and regimes. Python modules load data, validate configuration, evaluate rules, and generate daily outputs.

The architecture follows one-way data flow:

1. Load and validate registry, DSL, and raw data.
2. Build single-index runtime objects for a target date.
3. Derive pair runtime objects from completed index runtimes.
4. Build market runtime from index and pair outputs.
5. Emit JSON and Markdown.

This keeps each layer easy to reason about and makes failures local. Pair logic never mutates index state. Market logic never recomputes index or pair logic.

## Module Boundaries

Recommended package root:

```text
market_system/
├─ config/
├─ data/
│  ├─ raw/           # Production CSV files (hs300.csv, cyb.csv, csi1000.csv)
│  └─ snapshots/
├─ dsl/
├─ engine/
│  ├─ loader.py
│  ├─ validator.py
│  ├─ models.py
│  ├─ resolver.py
│  ├─ expression.py
│  ├─ feature_engine.py
│  ├─ state_engine.py
│  ├─ tag_engine.py
│  ├─ salience_engine.py
│  ├─ pair_engine.py
│  ├─ regime_engine.py
│  ├─ pipeline.py
│  ├─ output_writer.py
│  └─ trace.py
├─ outputs/
├─ tests/
│  ├─ fixtures/      # Test CSV files
│  ├─ unit/
│  ├─ integration/
│  └─ golden/
├─ run_daily.py
└─ requirements.txt
```

Module responsibilities:

- `loader.py`: load YAML, registry, and raw market CSV data into normalized in-memory structures. Supports both production CSV files in `data/raw/` and test fixtures in `tests/fixtures/`.
- `validator.py`: hard-fail on schema issues, unknown references, duplicate ids, invalid outputs, or bad pair references.
- `models.py`: define runtime objects for index, pair, market, and salience payloads.
- `resolver.py`: resolve `self`, `prev`, `left`, `right`, `index`, and `market` references in a single place.
- `expression.py`: safe, minimal expression execution for state, tag, salience, and regime conditions.
- `feature_engine.py`: compute daily features in DSL order and record trace entries.
- `state_engine.py`: map features to discrete states using first-match logic.
- `tag_engine.py`: detect pattern, transition, and relation tags.
- `salience_engine.py`: apply scoring rules and compute ranked market salience buckets.
- `pair_engine.py`: compute pair features and pair states from completed index runtimes.
- `regime_engine.py`: score market regimes and compute confidence plus evidence.
- `pipeline.py`: orchestrate full single-day and date-range execution.
- `output_writer.py`: write JSON and Markdown outputs from finished runtime objects.
- `trace.py`: keep trace payload shape stable across modules.

## Runtime Model

Three runtime objects are sufficient:

- `IndexRuntime`
  - raw inputs for one index on one date
  - derived features
  - derived states
  - pattern tags
  - transition tags
  - salience payload
  - trace payload
- `PairRuntime`
  - left and right index ids
  - pair features
  - pair states
  - relation tags
  - trace payload
- `MarketRuntime`
  - top positive, negative, warning, and transition signals
  - combined relation tags
  - selected regime with confidence and evidence
  - trace payload

The data model should stay small and explicit. Phase I does not need inheritance-heavy runtime classes or a generic plugin system.

## Data Flow

Single-index execution order:

1. Normalize raw row for a target date.
2. Compute features using historical slice up to target date.
3. Derive states from features.
4. Detect pattern tags.
5. Detect transition tags using previous runtime when available.
6. Compute salience score buckets and matched rules.

Pair execution order:

1. Create pair runtime from pair definition.
2. Compute pair features from already-computed index runtimes.
3. Derive pair states.
4. Detect relation tags.

Market execution order:

1. Aggregate index salience into ranked market buckets.
2. Collect relation tags from pairs.
3. Score each regime.
4. Select top regime and compute confidence.
5. Render JSON and Markdown outputs.

## Error Handling

Phase I should prefer explicit hard failure over silent fallback.

- Configuration errors must fail during startup, not mid-pipeline.
- Missing required raw columns must fail load.
- Invalid expression references must fail validation when possible, otherwise fail evaluation with rule id attached.
- Unsupported feature formulas should fail with the exact rule id and date context.
- Output writing should fail loudly rather than partially succeed without notice.

This is important for trust. A rules engine that keeps running after bad configuration is worse than one that stops.

## Testing Strategy

Primary goal: rule correctness.

Test stack:

- `pytest`
- `pandas`
- `pyyaml`

Recommended test pyramid:

- `tests/unit/`
  - `test_loader.py`
  - `test_validator.py`
  - `test_resolver.py`
  - `test_expression.py`
  - `test_feature_engine.py`
  - `test_state_engine.py`
  - `test_tag_engine.py`
  - `test_salience_engine.py`
  - `test_pair_engine.py`
  - `test_regime_engine.py`
- `tests/integration/`
  - pipeline tests for one date and a short range
- `tests/golden/`
  - 2 to 3 curated end-to-end fixtures with expected JSON outputs

TDD rules for this project:

1. No production code before a failing test.
2. Every new rule evaluator path must have at least one direct test.
3. Every major milestone must add or update a golden sample.
4. Bug fixes require a reproducing failing test before code changes.

What the tests should prove:

- DSL files load and validate correctly.
- Invalid DSL fails for the expected reason.
- Reference resolution is correct across all supported namespaces.
- Expression evaluation is safe and deterministic.
- Feature calculations match expected numeric outputs on fixture data.
- State and tag rules produce exact expected labels.
- Regime selection matches expected label, score, and evidence for sample dates.
- Full single-day output is stable against golden JSON fixtures.

## TDD Implementation Order

The recommended build order is:

1. `validator` and `loader`
2. `models`
3. `resolver`
4. `expression`
5. `feature_engine`
6. `state_engine`
7. `tag_engine`
8. `salience_engine`
9. `pair_engine`
10. `regime_engine`
11. `pipeline`
12. `output_writer`

Reasoning:

- `validator` and `loader` lock down the system boundary first.
- `resolver` and `expression` are the trust core for all later logic.
- `feature_engine` and `state_engine` establish the single-index backbone.
- Remaining modules then compose on top of verified primitives.

## Milestones

### Milestone 1: Trusted Core

Deliver:

- project skeleton
- dependency file
- loader
- validator
- runtime models
- resolver
- expression engine
- unit tests for these modules

Exit criteria:

- invalid DSL fails with clear errors
- valid DSL loads successfully
- expression evaluation tests all pass

### Milestone 2: Single-Index Correctness

Deliver:

- feature engine
- state engine
- tag engine for patterns and transitions
- salience engine
- fixture data for at least one target date per index

Exit criteria:

- single-index outputs are correct for curated fixtures
- traces include feature, state, tag, and salience hits

### Milestone 3: Market Structure Closure

Deliver:

- pair engine
- regime engine
- pipeline
- JSON output
- Markdown output
- golden end-to-end samples

Exit criteria:

- one-day pipeline passes golden tests
- selected regime is correct and traceable
- JSON and Markdown are written successfully

### Milestone 4: Quality Gate

Deliver:

- short date-range execution
- regression test fixtures
- basic CI command set

Exit criteria:

- unit, integration, and golden tests all pass
- a short range run completes without schema or runtime surprises

## Non-Goals for Phase I

- maximizing abstraction
- building a universal rules platform
- supporting dynamic user-authored arbitrary Python
- optimizing prematurely for speed before correctness is proven

## Decisions

- Use `pytest + pandas + pyyaml`.
- Use CSV format for all data files (both production and test environments) for simplicity and transparency.
- Prioritize rule correctness over feature breadth.
- Prefer core engine unit tests plus a small number of end-to-end golden samples.
- Use hard validation and explicit failures.
- Keep Phase I implementation narrow and inspectable.

## Risks And Mitigations

- Risk: feature formulas become too generic too early.
  - Mitigation: implement only the formula types Phase I actually uses.
- Risk: expressions drift from DSL assumptions.
  - Mitigation: validate references and keep a constrained evaluator.
- Risk: e2e tests are too sparse.
  - Mitigation: maintain a small golden suite that covers bullish, bearish, and mixed-structure dates.
- Risk: output appears correct but trace is incomplete.
  - Mitigation: require trace assertions in integration tests, not just result assertions.

## Immediate Next Step

Write a detailed implementation plan that breaks Milestone 1 through Milestone 4 into TDD-first tasks, including exact test files, exact commands, and expected failures before implementation.
