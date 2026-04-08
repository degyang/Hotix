# Hotix Phase II Market Context Design

**Date:** 2026-04-08

**Goal**

Upgrade Hotix from a Phase I market structure recognizer into a Phase II market context engine that can support broader index coverage, explicit trading constraints, and repeatable validation workflows. Phase II must preserve the explainability and TDD discipline established in Phase I while making the system usable as a decision boundary for later strategy and execution layers.

**Current Status**

The following Phase II capabilities have already been implemented in the codebase:

- context DSL in `market_system/dsl/contexts.yaml`
- market context scoring in `market_system/engine/context_engine.py`
- pipeline integration of `market_context`
- debug and markdown exposure of context results
- external `--data-dir` loading and `--latest` support
- package-directory CLI execution support via `market_system/paths.py`
- code-based index identifiers using real market codes
- expanded core panel using 8 indices and 7 key pair relationships

This document defines the intended Phase II architecture for both the delivered work and the remaining completion scope.

## Scope

- In scope:
  - expand index panel from Phase I's minimal set to the core market panel
  - map internal IDs to real market codes to remove semantic ambiguity
  - add a `context` layer above `regime`
  - support trading-constraint outputs such as `allowed_styles` and `risk_budget`
  - make runtime data input explicit through CLI and external data directories
  - improve DSL validation for context and code-based expressions
  - add validation/reporting hooks for later replay and calibration work
- Out of scope:
  - single-stock signal engine
  - position sizing engine beyond static context risk budgets
  - broker connectivity or live order routing
  - LLM-generated commentary as part of core evaluation
  - generalized quantitative platform abstractions

## Phase II Objectives

### Objective 1: Expand the Market Panel

Phase I only proved the engine on a narrow structure sample. Phase II must represent the market with a broader, but still curated, panel:

- `000001` 上证指数
- `399001` 深证成指
- `000016` 上证50
- `000300` 沪深300
- `000905` 中证500
- `000852` 中证1000
- `399006` 创业板指
- `000680` 科创综指

This panel is broad enough to characterize core vs growth, large vs small, and breadth vs concentration without exploding the pair space.

### Objective 2: Translate Structure Into Constraints

Phase I stops at structural description. Phase II adds a `market_context` layer that translates regime, relation, and salience into behavior constraints:

- `Offense`
- `Caution`
- `Defense`
- `Cash`

The context result is a bridge from observation to action. It does not generate trades; it defines what styles are currently permitted and how much risk the system should allow.

### Objective 3: Prepare the Engine for Calibration

Phase II must make later validation possible. The engine should expose enough structure and trace data to support:

- historical replay
- regime distribution statistics
- tag hit statistics
- mismatch review
- threshold adjustment workflows

The first implementation does not need a full analytics subsystem, but it must leave clean interfaces for it.

## Architecture

Phase II keeps Phase I's one-way evaluation flow and adds three new concerns on top:

```text
raw data
-> features
-> states
-> patterns / transitions
-> salience
-> pair relations
-> market regime
-> market context
-> validation / reporting hooks
```

The critical architectural choice is to keep `context` downstream from `regime`. Context is derived, not independent. This avoids duplicated logic and keeps the system easier to audit.

## Module Boundaries

Phase II extends the existing `market_system` package with a small set of focused changes:

- `market_system/config/index_registry.yaml`
  - authoritative mapping from internal runtime IDs to real market codes and panel roles
- `market_system/dsl/pairs.yaml`
  - curated key pair list, not full pair permutation
- `market_system/dsl/relation_tags.yaml`
  - pair-level structure rules for the expanded panel
- `market_system/dsl/regimes.yaml`
  - regime logic expressed against code-based index IDs
- `market_system/dsl/contexts.yaml`
  - context scoring rules and risk budgets
- `market_system/engine/context_engine.py`
  - deterministic scoring and tie-breaking for context results
- `market_system/engine/loader.py`
  - explicit external CSV loading, symbol-based path resolution, schema normalization
- `market_system/engine/pipeline.py`
  - orchestration of expanded panel, common-date selection, and context output
- `market_system/engine/expression.py`
  - support for code-based DSL references such as `index.000300.trend_state`
- `market_system/engine/validator.py`
  - syntax and schema validation for context and regime expressions
- `market_system/engine/output_writer.py`
  - markdown exposure of context output
- `market_system/engine/debug_report.py`
  - debug payload generation for index, pair, and market inspection
- `market_system/run_daily.py`
  - explicit `--data-dir`, `--latest`, and debug entry points
- `market_system/paths.py`
  - stable package-root resolution for both module execution and package-directory execution

## Data Model

Phase II adds one new durable payload:

- `market_context`
  - `label`
  - `score`
  - `confidence`
  - `allowed_styles`
  - `disallowed_styles`
  - `risk_budget`
  - `evidence`
  - `runner_up`
  - `runner_up_score`

This payload belongs under `payload["market"]` alongside `market_regime`, not under any index or pair. Context is a market-level conclusion.

## ID Strategy

Phase II intentionally replaces ambiguous aliases like `hs300`, `cyb`, and `sh_index` with real market-code IDs:

- `000300` instead of `hs300`
- `399006` instead of `cyb`
- `000001` instead of `sh_index`
- `399001` instead of `sz_index`
- `000680` instead of a generic `star`

Reasoning:

- removes naming ambiguity between DSL, fixtures, and real data files
- makes CLI and external data directory behavior more predictable
- aligns runtime IDs with actual CSV file naming
- reduces translation logic when adding more indices later

The tradeoff is that raw code-like IDs are not valid Python identifiers inside `eval`. Phase II resolves this by normalizing DSL expressions before evaluation while keeping the DSL readable.

## Pair Strategy

Phase II must not create a full matrix of pair relationships. Only structurally meaningful pairs should exist:

- `000300_vs_399006`
- `000300_vs_000680`
- `000300_vs_000905`
- `000300_vs_000852`
- `000016_vs_000852`
- `399006_vs_000680`
- `000905_vs_000852`

This keeps relation outputs interpretable and avoids rule sprawl.

## CLI and Data Input

Phase II changes the system boundary in an important way: runtime data must be explicit.

- `run_daily.py` no longer silently falls back to fixture data
- `--data-dir` is required for normal CLI execution
- `--latest` selects the latest common date across all registered indices
- CSV loading prefers `symbol.csv`, then falls back to `index_id.csv`
- external schemas are normalized into the internal column contract

This makes fixture data a test-only concern and avoids accidental production use of sample inputs.

## Validation and Traceability

Phase II keeps the same trust model as Phase I:

- bad DSL should fail early
- invalid market dates should fail explicitly
- context decisions must expose evidence
- golden tests should track stable end-to-end payloads

Additional Phase II validation targets:

- context DSL schema validation
- code-based regime expression validation
- common-date correctness across the expanded panel
- CLI correctness under external data directories
- CLI correctness when executed from the package directory itself

## Testing Strategy

Phase II continues the Phase I TDD discipline:

1. write failing tests for each new capability
2. verify the failure is for the expected reason
3. implement the minimal behavior
4. rerun targeted tests
5. rerun full regression suite
6. refresh golden payloads only after behavior is intentionally changed

Phase II adds coverage in four areas:

- panel expansion and pair expansion
- context scoring
- code-based expression resolution
- CLI data-dir and latest-date workflows

Current verification evidence:

- `pytest -q market_system/tests`
- `pytest -q` from `market_system/`

Both pass against the current Phase II codebase.

## Milestones

### Milestone 1: Context Layer

Deliver:

- `contexts.yaml`
- `context_engine.py`
- pipeline integration
- markdown/debug integration
- validation for context DSL

Status: implemented

### Milestone 2: Core Panel Expansion

Deliver:

- 8-index registry
- curated 7-pair relation set
- code-based IDs
- fixture refresh and golden refresh

Status: implemented

### Milestone 3: Validation and Calibration Hooks

Deliver:

- replay-oriented statistics hooks
- distribution reporting for regimes and context labels
- false-positive / false-negative review workflow

Status: not yet implemented

### Milestone 4: Reporting and Downstream Interfaces

Deliver:

- more stable debug/report outputs
- interfaces for Phase III strategy and execution consumers

Status: partially prepared, not complete

## Open Risks

- The expanded panel still depends on curated DSL heuristics; no statistical calibration loop exists yet.
- Context scoring is deterministic but still rule-weight-based, so weight drift remains a maintenance risk.
- Validation infrastructure is enough for correctness, not yet enough for historical robustness analysis.
- Real data schema assumptions are normalized, but new vendors may still require loader extensions.

## Completion Criteria

Phase II should be considered complete only when all of the following are true:

- the expanded core panel runs end-to-end on real external data
- market context output is stable and auditable
- context and regime rules are validated before execution
- replay and reporting hooks exist for calibration work
- Phase III consumers can read market context without depending on internal engine details
