# Architecture

Hotix is a configuration-driven market structure pipeline. YAML files define the rules; Python modules load data, validate configuration, execute rules, and render outputs.

## Package Layout

```text
src/hotix/
├─ config/
│  └─ index_registry.yaml
├─ dsl/
│  ├─ features.yaml
│  ├─ states.yaml
│  ├─ patterns.yaml
│  ├─ transitions.yaml
│  ├─ salience.yaml
│  ├─ pairs.yaml
│  ├─ pair_features.yaml
│  ├─ pair_states.yaml
│  ├─ relation_tags.yaml
│  ├─ regimes.yaml
│  ├─ contexts.yaml
│  ├─ policies.yaml
│  └─ universes.yaml
├─ engine/
│  ├─ loader.py
│  ├─ validator.py
│  ├─ expression.py
│  ├─ resolver.py
│  ├─ feature_engine.py
│  ├─ state_engine.py
│  ├─ tag_engine.py
│  ├─ salience_engine.py
│  ├─ pair_engine.py
│  ├─ regime_engine.py
│  ├─ context_engine.py
│  ├─ policy_engine.py
│  ├─ universe_engine.py
│  ├─ output_writer.py
│  ├─ debug_report.py
│  ├─ models.py
│  └─ pipeline.py
├─ paths.py
└─ run_daily.py
```

## Main Flow

```text
CLI args
  -> build_context()
  -> load registry
  -> load DSL YAML
  -> validate DSL
  -> load all CSV data
  -> select date or date range
  -> compute index runtimes
  -> compute universe profiles
  -> compute pair runtimes
  -> compute market salience
  -> score market regime
  -> score market context
  -> score policy
  -> print JSON or write JSON/Markdown
```

## Core Runtime Objects

Runtime objects are defined in `src/hotix/engine/models.py`:

- `IndexRuntime`: raw row, features, states, pattern tags, transition tags, salience, trace
- `SalienceItem`: structured salience evidence with scope, asset, dimension, category, polarity, score, severity, confidence, reason, evidence, and optional rank metadata
- `PairRuntime`: pair features, pair states, relation tags, trace
- `MarketRuntime`: market relation tags, signal buckets, regime, context, policy, trace
- `PolicyOutput`: policy permissions, execution constraints, vetoes, trace

`MarketRuntime` is an explicit dataclass. The project no longer uses dynamically-created market objects in the pipeline.

## Salience V2 Core

Salience is the engine layer that turns market observations into ranked "what matters today" evidence. It has two complementary forms:

- Rule salience: DSL rules score notable states, patterns, divergences, and transitions for each asset.
- Cross-section salience: `build_cross_section_salience()` ranks the strongest and weakest assets for metrics such as price return, volume expansion, volatility, breadth, and position.

The rule salience output keeps the original compatibility fields:

```text
total_score
positive_score
negative_score
warning_score
transition_score
matched_rules
```

It also emits `items`, a list of structured `SalienceItem` dictionaries. These items preserve the original score bucket behavior while adding explicit dimension, category, polarity, confidence, freshness, evidence fields, and tags for downstream universe and report layers.

## Universe Analysis

Universe Analysis makes a configured asset group the unit of market analysis. A universe is defined in `universes.yaml` with an id, name, type, role, and member list. The first built-in universes are:

- `broad_indices`: all 8 registered broad index proxies.
- `growth_proxy`: `399006` and `000680` as a growth-risk appetite proxy.

`universe_engine.py` consumes already-computed `IndexRuntime` objects. It does not recalculate features or depend on pair logic. Each universe profile contains:

- member list and participation counts
- trend, position, volume, breadth, and volatility state distributions
- grouped structured salience items
- cross-section TOPN rankings for price, volume, volatility, breadth, and position
- short descriptive summaries

## DSL Execution

DSL expressions are evaluated by:

- `expression.py`: normalizes and evaluates expression strings
- `resolver.py`: resolves `self`, `prev`, `left`, `right`, `index`, `pair`, and `market` references
- `validator.py`: validates YAML structure and compiles normalized expressions before runtime

The expression evaluator is intentionally small and assumes DSL files are trusted repository configuration, not user-submitted code.

## Pipeline Boundaries

`pipeline.py` is the application orchestration layer. It should coordinate engines, not contain rule-specific logic.

Specialized modules own domain-specific calculations:

- feature calculations: `feature_engine.py`
- index states: `state_engine.py`
- index tags: `tag_engine.py`
- salience buckets: `salience_engine.py`
- universe analysis: `universe_engine.py`
- pair logic: `pair_engine.py`
- market regime: `regime_engine.py`
- market context: `context_engine.py`
- policy output: `policy_engine.py`

## Outputs

Compact CLI output contains:

- `date`
- `market`

Full JSON output includes:

- `date`
- `indices`
- `universes`
- `pairs`
- `market`

Report files are written to:

```text
src/hotix/outputs/json/
src/hotix/outputs/markdown/
```

The `outputs/` directory is generated runtime data and should not be treated as source.

## Tests

The test suite is organized by behavior:

```text
tests/unit/
tests/integration/
tests/golden/
tests/fixtures/
```

Golden tests compare the complete daily payload against:

```text
tests/fixtures/expected_daily_2026-04-03.json
```
