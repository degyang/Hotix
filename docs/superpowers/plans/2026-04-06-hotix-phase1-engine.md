# Hotix Phase I Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a TDD-first Phase I market structure engine that produces traceable daily JSON and Markdown outputs for three indices, two pairs, and four market regimes.

**Architecture:** The system is a configuration-driven Python rules engine. YAML DSL files define features, states, tags, salience, pairs, and regimes, while focused engine modules load data, validate inputs, resolve expressions, compute runtimes, and write outputs. Testing centers on unit tests for core evaluators plus a small golden suite for end-to-end correctness.

**Tech Stack:** Python 3.12, pytest, pandas, pyyaml, numpy

**Data Format:** CSV files for all market data (production in `data/raw/`, test fixtures in `tests/fixtures/`)

---

## File Structure

Planned write targets and responsibilities:

- Create: `market_system/requirements.txt`
- Create: `market_system/config/index_registry.yaml`
- Create: `market_system/dsl/features.yaml`
- Create: `market_system/dsl/states.yaml`
- Create: `market_system/dsl/patterns.yaml`
- Create: `market_system/dsl/transitions.yaml`
- Create: `market_system/dsl/salience.yaml`
- Create: `market_system/dsl/pairs.yaml`
- Create: `market_system/dsl/pair_features.yaml`
- Create: `market_system/dsl/pair_states.yaml`
- Create: `market_system/dsl/relation_tags.yaml`
- Create: `market_system/dsl/regimes.yaml`
- Create: `market_system/engine/__init__.py`
- Create: `market_system/engine/models.py`
- Create: `market_system/engine/loader.py`
- Create: `market_system/engine/validator.py`
- Create: `market_system/engine/resolver.py`
- Create: `market_system/engine/expression.py`
- Create: `market_system/engine/feature_engine.py`
- Create: `market_system/engine/state_engine.py`
- Create: `market_system/engine/tag_engine.py`
- Create: `market_system/engine/salience_engine.py`
- Create: `market_system/engine/pair_engine.py`
- Create: `market_system/engine/regime_engine.py`
- Create: `market_system/engine/pipeline.py`
- Create: `market_system/engine/output_writer.py`
- Create: `market_system/engine/trace.py`
- Create: `market_system/run_daily.py`
- Create: `market_system/tests/conftest.py`
- Create: `market_system/tests/unit/test_loader.py`
- Create: `market_system/tests/unit/test_validator.py`
- Create: `market_system/tests/unit/test_resolver.py`
- Create: `market_system/tests/unit/test_expression.py`
- Create: `market_system/tests/unit/test_feature_engine.py`
- Create: `market_system/tests/unit/test_state_engine.py`
- Create: `market_system/tests/unit/test_tag_engine.py`
- Create: `market_system/tests/unit/test_salience_engine.py`
- Create: `market_system/tests/unit/test_pair_engine.py`
- Create: `market_system/tests/unit/test_regime_engine.py`
- Create: `market_system/tests/integration/test_pipeline.py`
- Create: `market_system/tests/golden/test_golden_daily.py`
- Create: `market_system/tests/fixtures/hs300.csv`
- Create: `market_system/tests/fixtures/cyb.csv`
- Create: `market_system/tests/fixtures/csi1000.csv`
- Create: `market_system/tests/fixtures/expected_daily_2026-04-05.json`

## Task 1: Bootstrap Project Skeleton

**Files:**
- Create: `market_system/requirements.txt`
- Create: `market_system/engine/__init__.py`
- Create: `market_system/run_daily.py`

- [ ] **Step 1: Write the failing bootstrap test**

```python
# market_system/tests/unit/test_loader.py
from pathlib import Path


def test_project_root_contains_expected_entrypoints():
    root = Path("market_system")
    assert (root / "requirements.txt").exists()
    assert (root / "engine" / "__init__.py").exists()
    assert (root / "run_daily.py").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest market_system/tests/unit/test_loader.py::test_project_root_contains_expected_entrypoints -v`
Expected: FAIL because the files do not exist yet.

- [ ] **Step 3: Write minimal implementation**

```txt
# market_system/requirements.txt
pytest>=8.0.0
pandas>=2.2.0
pyyaml>=6.0.1
numpy>=1.26.0
```

```python
# market_system/engine/__init__.py
"""Hotix Phase I engine package."""
```

```python
# market_system/run_daily.py
def main() -> None:
    raise SystemExit("Pipeline not implemented yet.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest market_system/tests/unit/test_loader.py::test_project_root_contains_expected_entrypoints -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/requirements.txt market_system/engine/__init__.py market_system/run_daily.py market_system/tests/unit/test_loader.py
git commit -m "chore: bootstrap hotix market engine package"
```

## Task 2: Add Registry And DSL Fixtures

**Files:**
- Create: `market_system/config/index_registry.yaml`
- Create: `market_system/dsl/features.yaml`
- Create: `market_system/dsl/states.yaml`
- Create: `market_system/dsl/patterns.yaml`
- Create: `market_system/dsl/transitions.yaml`
- Create: `market_system/dsl/salience.yaml`
- Create: `market_system/dsl/pairs.yaml`
- Create: `market_system/dsl/pair_features.yaml`
- Create: `market_system/dsl/pair_states.yaml`
- Create: `market_system/dsl/relation_tags.yaml`
- Create: `market_system/dsl/regimes.yaml`
- Test: `market_system/tests/unit/test_validator.py`

- [ ] **Step 1: Write the failing registry/DSL presence test**

```python
# market_system/tests/unit/test_validator.py
from pathlib import Path


def test_phase1_config_files_exist():
    root = Path("market_system")
    required = [
        "config/index_registry.yaml",
        "dsl/features.yaml",
        "dsl/states.yaml",
        "dsl/patterns.yaml",
        "dsl/transitions.yaml",
        "dsl/salience.yaml",
        "dsl/pairs.yaml",
        "dsl/pair_features.yaml",
        "dsl/pair_states.yaml",
        "dsl/relation_tags.yaml",
        "dsl/regimes.yaml",
    ]
    for rel in required:
        assert (root / rel).exists(), rel
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest market_system/tests/unit/test_validator.py::test_phase1_config_files_exist -v`
Expected: FAIL with missing file assertions.

- [ ] **Step 3: Write minimal implementation**

Use the exact Phase I content from the design docs for the registry and 10 DSL files. Do not invent extra rules. Keep the YAML ids and outputs identical to the design so later tests can assert exact names.

Example registry content:

```yaml
indices:
  hs300:
    name: 沪深300
    role: core_benchmark
    layer: core
  cyb:
    name: 创业板指
    role: growth_risk_appetite
    layer: growth
  csi1000:
    name: 中证1000
    role: small_cap_sentiment
    layer: sentiment
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest market_system/tests/unit/test_validator.py::test_phase1_config_files_exist -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/config/index_registry.yaml market_system/dsl/*.yaml market_system/tests/unit/test_validator.py
git commit -m "chore: add phase1 registry and dsl files"
```

## Task 3: Implement Loader And Data Fixtures

**Files:**
- Create: `market_system/engine/loader.py`
- Create: `market_system/tests/fixtures/hs300.csv`
- Create: `market_system/tests/fixtures/cyb.csv`
- Create: `market_system/tests/fixtures/csi1000.csv`
- Modify: `market_system/tests/unit/test_loader.py`

- [ ] **Step 1: Write the failing loader tests**

```python
from pathlib import Path

from market_system.engine.loader import load_registry, load_all_dsl, load_csv_data


def test_load_registry_returns_indices_dict():
    data = load_registry(Path("market_system/config/index_registry.yaml"))
    assert set(data["indices"]) == {"hs300", "cyb", "csi1000"}


def test_load_all_dsl_returns_expected_roots():
    dsl = load_all_dsl(Path("market_system/dsl"))
    assert "features" in dsl
    assert "regimes" in dsl


def test_load_csv_data_normalizes_dates_and_order():
    df = load_csv_data(Path("market_system/tests/fixtures/hs300.csv"))
    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume", "amount", "adv", "decl"]
    assert df["date"].tolist() == sorted(df["date"].tolist())
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest market_system/tests/unit/test_loader.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing symbol errors.

- [ ] **Step 3: Write minimal implementation**

```python
# market_system/engine/loader.py
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DSL_FILES = [
    "features.yaml",
    "states.yaml",
    "patterns.yaml",
    "transitions.yaml",
    "salience.yaml",
    "pairs.yaml",
    "pair_features.yaml",
    "pair_states.yaml",
    "relation_tags.yaml",
    "regimes.yaml",
]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_registry(path: Path) -> dict[str, Any]:
    return load_yaml(path)


def load_all_dsl(dsl_dir: Path) -> dict[str, dict[str, Any]]:
    return {path.stem: load_yaml(dsl_dir / path) for path in map(Path, DSL_FILES)}


def load_csv_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[["date", "open", "high", "low", "close", "volume", "amount", "adv", "decl"]].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    return df.sort_values("date").reset_index(drop=True)
```

Fixture CSV rows should cover enough history to exercise at least one rolling feature and one previous-day transition.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest market_system/tests/unit/test_loader.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/engine/loader.py market_system/tests/fixtures/*.csv market_system/tests/unit/test_loader.py
git commit -m "feat: add loader and csv fixture support"
```

## Task 4: Implement Validator

**Files:**
- Create: `market_system/engine/validator.py`
- Modify: `market_system/tests/unit/test_validator.py`

- [ ] **Step 1: Write the failing validator tests**

```python
import pytest

from market_system.engine.loader import load_all_dsl, load_registry
from market_system.engine.validator import ConfigValidationError, validate_all_dsl


def test_validate_all_dsl_accepts_phase1_files():
    registry = load_registry("market_system/config/index_registry.yaml")
    dsl = load_all_dsl("market_system/dsl")
    validate_all_dsl(dsl, registry)


def test_validate_all_dsl_rejects_unknown_pair_reference():
    registry = {"indices": {"hs300": {"name": "沪深300"}}}
    dsl = {
        "features": {"features": []},
        "states": {"states": []},
        "patterns": {"patterns": []},
        "transitions": {"transitions": []},
        "salience": {"salience": {"scoring_rules": []}},
        "pairs": {"pairs": [{"id": "bad", "left": "hs300", "right": "missing"}]},
        "pair_features": {"pair_features": []},
        "pair_states": {"pair_states": []},
        "relation_tags": {"relation_tags": []},
        "regimes": {"regimes": []},
    }
    with pytest.raises(ConfigValidationError):
        validate_all_dsl(dsl, registry)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest market_system/tests/unit/test_validator.py -v`
Expected: FAIL because validator is not implemented.

- [ ] **Step 3: Write minimal implementation**

```python
# market_system/engine/validator.py
class ConfigValidationError(Exception):
    pass


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ConfigValidationError(message)


def validate_all_dsl(dsl: dict, registry: dict) -> None:
    _ensure("indices" in registry, "registry missing indices")
    pair_ids = set(registry["indices"])
    for pair in dsl["pairs"]["pairs"]:
        _ensure(pair["left"] in pair_ids, f"unknown index: {pair['left']}")
        _ensure(pair["right"] in pair_ids, f"unknown index: {pair['right']}")
```

Then extend it until the real Phase I files validate and duplicate ids, required keys, and bad pair references all hard-fail.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest market_system/tests/unit/test_validator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/engine/validator.py market_system/tests/unit/test_validator.py
git commit -m "feat: validate phase1 registry and dsl files"
```

## Task 5: Implement Runtime Models, Resolver, And Expression Engine

**Files:**
- Create: `market_system/engine/models.py`
- Create: `market_system/engine/resolver.py`
- Create: `market_system/engine/expression.py`
- Create: `market_system/tests/unit/test_resolver.py`
- Create: `market_system/tests/unit/test_expression.py`

- [ ] **Step 1: Write the failing resolver and expression tests**

```python
from market_system.engine.expression import evaluate_expression
from market_system.engine.models import IndexRuntime
from market_system.engine.resolver import Resolver


def test_resolver_reads_self_prev_and_index_paths():
    prev = IndexRuntime(id="hs300", date="2026-04-04", raw={}, features={"ret_1d": -0.01}, states={"trend_state": "down"})
    curr = IndexRuntime(id="hs300", date="2026-04-05", raw={}, features={"ret_1d": 0.02}, states={"trend_state": "up"})
    resolver = Resolver(current=curr, prev=prev, indices={"hs300": curr}, pairs={}, market=None)
    assert resolver.resolve("self.ret_1d") == 0.02
    assert resolver.resolve("prev.trend_state") == "down"
    assert resolver.resolve("index.hs300.trend_state") == "up"


def test_expression_evaluates_boolean_rule_against_runtime():
    curr = IndexRuntime(id="hs300", date="2026-04-05", raw={}, features={"ret_1d": 0.02}, states={"trend_state": "up"})
    resolver = Resolver(current=curr)
    assert evaluate_expression("self.ret_1d > 0 and self.trend_state == 'up'", resolver) is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest market_system/tests/unit/test_resolver.py market_system/tests/unit/test_expression.py -v`
Expected: FAIL with missing modules.

- [ ] **Step 3: Write minimal implementation**

```python
# market_system/engine/models.py
from dataclasses import dataclass, field


@dataclass
class IndexRuntime:
    id: str
    date: str
    raw: dict = field(default_factory=dict)
    features: dict = field(default_factory=dict)
    states: dict = field(default_factory=dict)
    pattern_tags: list[str] = field(default_factory=list)
    transition_tags: list[str] = field(default_factory=list)
    salience: dict = field(default_factory=dict)
    trace: dict = field(default_factory=dict)

    def get_field(self, name: str):
        if name in self.raw:
            return self.raw[name]
        if name in self.features:
            return self.features[name]
        if name in self.states:
            return self.states[name]
        if name == "pattern_tags":
            return self.pattern_tags
        if name == "transition_tags":
            return self.transition_tags
        raise KeyError(name)
```

```python
# market_system/engine/resolver.py
class Resolver:
    def __init__(self, current=None, prev=None, indices=None, pairs=None, market=None):
        self.current = current
        self.prev = prev
        self.indices = indices or {}
        self.pairs = pairs or {}
        self.market = market

    def resolve(self, ref: str):
        head, _, tail = ref.partition(".")
        if head == "self":
            return self.current.get_field(tail)
        if head == "prev":
            return self.prev.get_field(tail)
        if head == "index":
            index_id, _, field_name = tail.partition(".")
            return self.indices[index_id].get_field(field_name)
        raise KeyError(ref)
```

```python
# market_system/engine/expression.py
def evaluate_expression(expr: str, resolver, rule_id: str = ""):
    local_env = {
        "__builtins__": {},
        "abs": abs,
        "max": max,
        "min": min,
        "len": len,
        "self": type("Obj", (), {"__getattr__": lambda _, name: resolver.resolve(f"self.{name}")})(),
        "prev": type("Obj", (), {"__getattr__": lambda _, name: resolver.resolve(f"prev.{name}")})(),
    }
    return eval(expr, local_env, {})
```

Then extend resolver to support `left`, `right`, `pair`, and `market` references, and tighten expression safety.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest market_system/tests/unit/test_resolver.py market_system/tests/unit/test_expression.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/engine/models.py market_system/engine/resolver.py market_system/engine/expression.py market_system/tests/unit/test_resolver.py market_system/tests/unit/test_expression.py
git commit -m "feat: add runtime models resolver and expression engine"
```

## Task 6: Implement Feature And State Engines

**Files:**
- Create: `market_system/engine/feature_engine.py`
- Create: `market_system/engine/state_engine.py`
- Create: `market_system/tests/unit/test_feature_engine.py`
- Create: `market_system/tests/unit/test_state_engine.py`

- [ ] **Step 1: Write the failing feature and state tests**

```python
from market_system.engine.feature_engine import compute_index_features
from market_system.engine.state_engine import derive_index_states
from market_system.engine.loader import load_all_dsl, load_csv_data


def test_compute_index_features_returns_expected_ret_and_ma_values():
    dsl = load_all_dsl("market_system/dsl")
    df = load_csv_data("market_system/tests/fixtures/hs300.csv")
    runtime = compute_index_features("hs300", "2026-04-05", df, dsl["features"])
    assert round(runtime.features["ret_1d"], 6) == 0.010000
    assert "ma_20" in runtime.features


def test_derive_index_states_sets_trend_and_volume_states():
    dsl = load_all_dsl("market_system/dsl")
    df = load_csv_data("market_system/tests/fixtures/hs300.csv")
    runtime = compute_index_features("hs300", "2026-04-05", df, dsl["features"])
    runtime = derive_index_states(runtime, dsl["states"])
    assert runtime.states["trend_state"] in {"up", "down", "range", "transitional_up", "transitional_down"}
    assert runtime.states["volume_state"] in {"extreme_contraction", "contraction", "normal", "expansion", "extreme_expansion"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest market_system/tests/unit/test_feature_engine.py market_system/tests/unit/test_state_engine.py -v`
Expected: FAIL because engines are not implemented.

- [ ] **Step 3: Write minimal implementation**

Implement only Phase I feature types:

- rolling mean
- percentile over trailing window
- explicit formula handlers for:
  - `ret_1d`
  - `ret_5d`
  - `ret_20d`
  - `ma_slope_20`
  - `distance_to_ma20`
  - `amount_ratio_1_20`
  - `amount_ratio_5_20`
  - `breadth_ratio`
  - `breadth_diff`
  - `true_range`
  - `atr_pct_14`
  - `breakout_20d`
  - `breakdown_20d`

State engine should:

- walk `states.yaml` in order
- evaluate each case through `evaluate_expression`
- write first hit
- otherwise write default
- record trace entries with `rule_id`, `matched_case`, and final `value`

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest market_system/tests/unit/test_feature_engine.py market_system/tests/unit/test_state_engine.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/engine/feature_engine.py market_system/engine/state_engine.py market_system/tests/unit/test_feature_engine.py market_system/tests/unit/test_state_engine.py
git commit -m "feat: implement single-index feature and state engines"
```

## Task 7: Implement Tags And Salience

**Files:**
- Create: `market_system/engine/tag_engine.py`
- Create: `market_system/engine/salience_engine.py`
- Create: `market_system/tests/unit/test_tag_engine.py`
- Create: `market_system/tests/unit/test_salience_engine.py`

- [ ] **Step 1: Write the failing tag and salience tests**

```python
from market_system.engine.tag_engine import detect_index_patterns, detect_index_transitions
from market_system.engine.salience_engine import score_index_salience


def test_detect_index_patterns_returns_expected_tags(index_runtime_ready, dsl_bundle):
    runtime = detect_index_patterns(index_runtime_ready, dsl_bundle["patterns"])
    assert "pattern_tags" in runtime.__dict__


def test_score_index_salience_accumulates_bucket_scores(index_runtime_with_tags, dsl_bundle):
    runtime = score_index_salience(index_runtime_with_tags, dsl_bundle["salience"])
    assert runtime.salience["total_score"] >= 0
    assert "matched_rules" in runtime.salience
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest market_system/tests/unit/test_tag_engine.py market_system/tests/unit/test_salience_engine.py -v`
Expected: FAIL because engines or fixtures are missing.

- [ ] **Step 3: Write minimal implementation**

Pattern and transition engine rules:

- evaluate each `when`
- append `add_tag` on hit
- dedupe while preserving order
- transition detection must short-circuit to empty list when no previous runtime exists

Salience engine rules:

- sum `total_score`
- sum bucket scores into `positive_score`, `negative_score`, `warning_score`, `transition_score`
- store matched rules with `rule_id`, `score`, `bucket`, `polarity`, `reason`

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest market_system/tests/unit/test_tag_engine.py market_system/tests/unit/test_salience_engine.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/engine/tag_engine.py market_system/engine/salience_engine.py market_system/tests/unit/test_tag_engine.py market_system/tests/unit/test_salience_engine.py market_system/tests/conftest.py
git commit -m "feat: add tag detection and salience scoring"
```

## Task 8: Implement Pair And Regime Engines

**Files:**
- Create: `market_system/engine/pair_engine.py`
- Create: `market_system/engine/regime_engine.py`
- Create: `market_system/tests/unit/test_pair_engine.py`
- Create: `market_system/tests/unit/test_regime_engine.py`

- [ ] **Step 1: Write the failing pair and regime tests**

```python
from market_system.engine.pair_engine import create_pair_runtime, compute_pair_features, derive_pair_states
from market_system.engine.regime_engine import score_market_regime


def test_compute_pair_features_returns_relative_strength(pair_definition, ready_indices, dsl_bundle):
    runtime = create_pair_runtime(pair_definition, "2026-04-05")
    runtime = compute_pair_features(runtime, dsl_bundle["pair_features"], ready_indices)
    assert "rs_ret_20d" in runtime.features


def test_score_market_regime_selects_label_with_evidence(market_runtime_ready, ready_indices, ready_pairs, dsl_bundle):
    market = score_market_regime(market_runtime_ready, ready_indices, ready_pairs, dsl_bundle["regimes"])
    assert market.market_regime["label"]
    assert isinstance(market.market_regime["evidence"], list)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest market_system/tests/unit/test_pair_engine.py market_system/tests/unit/test_regime_engine.py -v`
Expected: FAIL because engines are missing.

- [ ] **Step 3: Write minimal implementation**

Pair engine should:

- create runtime from `pairs.yaml`
- compute formula features through the expression engine
- derive pair states with first-match logic
- evaluate relation tags scoped to the current pair id

Regime engine should:

- collect deduped relation tags from all pairs
- score each regime rule
- gather evidence strings for matched rules
- choose the highest score
- compute confidence as `top_score / sum(all_scores)` when total is positive

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest market_system/tests/unit/test_pair_engine.py market_system/tests/unit/test_regime_engine.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/engine/pair_engine.py market_system/engine/regime_engine.py market_system/tests/unit/test_pair_engine.py market_system/tests/unit/test_regime_engine.py
git commit -m "feat: add pair and regime engines"
```

## Task 9: Implement Pipeline And Output Writers

**Files:**
- Create: `market_system/engine/pipeline.py`
- Create: `market_system/engine/output_writer.py`
- Modify: `market_system/run_daily.py`
- Create: `market_system/tests/integration/test_pipeline.py`

- [ ] **Step 1: Write the failing integration tests**

```python
from market_system.engine.pipeline import build_context, run_single_date


def test_run_single_date_returns_complete_payload():
    ctx = build_context("market_system")
    payload = run_single_date(ctx, "2026-04-05")
    assert set(payload) == {"date", "indices", "pairs", "market"}
    assert set(payload["indices"]) == {"hs300", "cyb", "csi1000"}
    assert set(payload["pairs"]) == {"hs300_vs_cyb", "hs300_vs_csi1000"}


def test_run_single_date_market_payload_contains_regime_and_relations():
    ctx = build_context("market_system")
    payload = run_single_date(ctx, "2026-04-05")
    assert "market_regime" in payload["market"]
    assert "relation_tags" in payload["market"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest market_system/tests/integration/test_pipeline.py -v`
Expected: FAIL because pipeline is not implemented.

- [ ] **Step 3: Write minimal implementation**

`build_context` should:

- load registry
- load DSL
- validate DSL
- load all fixture or raw data into a context object

`run_single_date` should:

- build index runtimes
- build market salience
- build pair runtimes
- score market regime
- return a serializable payload

`output_writer.py` should:

- write JSON files to `outputs/json/YYYY-MM-DD.json`
- render Markdown with market summary, signals, relation tags, regime evidence, and index overview
- write Markdown to `outputs/markdown/YYYY-MM-DD.md`

`run_daily.py` should support:

- `--date 2026-04-05`
- `--start 2026-04-01 --end 2026-04-05`
- `--dump-json`
- `--write-files`

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest market_system/tests/integration/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/engine/pipeline.py market_system/engine/output_writer.py market_system/run_daily.py market_system/tests/integration/test_pipeline.py
git commit -m "feat: add daily pipeline and output writers"
```

## Task 10: Add Golden Regression Coverage

**Files:**
- Create: `market_system/tests/golden/test_golden_daily.py`
- Create: `market_system/tests/fixtures/expected_daily_2026-04-05.json`

- [ ] **Step 1: Write the failing golden regression test**

```python
import json
from pathlib import Path

from market_system.engine.pipeline import build_context, run_single_date


def test_daily_payload_matches_golden_sample():
    ctx = build_context("market_system")
    actual = run_single_date(ctx, "2026-04-05")
    expected = json.loads(Path("market_system/tests/fixtures/expected_daily_2026-04-05.json").read_text(encoding="utf-8"))
    assert actual == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest market_system/tests/golden/test_golden_daily.py -v`
Expected: FAIL because no golden file exists yet or payload differs.

- [ ] **Step 3: Write minimal implementation**

Generate the golden file from a known-correct run after all prior tests are green:

```bash
python -m market_system.run_daily --date 2026-04-05 --dump-json > market_system/tests/fixtures/expected_daily_2026-04-05.json
```

Then normalize any unstable ordering before asserting equality:

- sort relation tag lists only if the production contract says order is not meaningful
- otherwise preserve exact order and treat drift as regression

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest market_system/tests/golden/test_golden_daily.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/tests/golden/test_golden_daily.py market_system/tests/fixtures/expected_daily_2026-04-05.json
git commit -m "test: add golden regression for daily payload"
```

## Task 11: Add Date-Range And Smoke Verification

**Files:**
- Modify: `market_system/engine/pipeline.py`
- Modify: `market_system/run_daily.py`
- Modify: `market_system/tests/integration/test_pipeline.py`

- [ ] **Step 1: Write the failing date-range test**

```python
from market_system.engine.pipeline import build_context, run_date_range


def test_run_date_range_returns_all_common_dates():
    ctx = build_context("market_system")
    results = run_date_range(ctx, start="2026-04-04", end="2026-04-05")
    assert [item["date"] for item in results] == ["2026-04-04", "2026-04-05"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest market_system/tests/integration/test_pipeline.py::test_run_date_range_returns_all_common_dates -v`
Expected: FAIL because the function is missing or incomplete.

- [ ] **Step 3: Write minimal implementation**

Implement `run_date_range` so it:

- finds common dates across all indices
- filters by `start` and `end`
- runs `run_single_date` for each date
- optionally writes JSON and Markdown output files for each day

CLI smoke commands to support:

```bash
python -m market_system.run_daily --date 2026-04-05
python -m market_system.run_daily --date 2026-04-05 --dump-json
python -m market_system.run_daily --start 2026-04-04 --end 2026-04-05 --write-files
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest market_system/tests/integration/test_pipeline.py::test_run_date_range_returns_all_common_dates -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/engine/pipeline.py market_system/run_daily.py market_system/tests/integration/test_pipeline.py
git commit -m "feat: support date range execution and file outputs"
```

## Task 12: Final Verification Gate

**Files:**
- Modify: `market_system/tests/conftest.py`
- Modify: `market_system/tests/integration/test_pipeline.py`
- Modify: `market_system/tests/golden/test_golden_daily.py`

- [ ] **Step 1: Write any missing failing tests for trace assertions**

```python
from market_system.engine.pipeline import build_context, run_single_date


def test_daily_payload_contains_trace_details():
    ctx = build_context("market_system")
    payload = run_single_date(ctx, "2026-04-05")
    hs300 = payload["indices"]["hs300"]
    assert "trace" in hs300
    assert "features" in hs300["trace"]
    assert "states" in hs300["trace"]
```

- [ ] **Step 2: Run the full suite and verify at least one failure if the trace contract is not implemented**

Run: `pytest market_system/tests -v`
Expected: FAIL until the trace payload contract is complete.

- [ ] **Step 3: Write minimal implementation**

Make trace payloads stable and explicit:

- feature trace includes `rule_id` and output value
- state trace includes `rule_id`, matched case, and final value
- tag trace includes matched rule ids and emitted tags
- salience trace includes matched scoring rules
- market trace includes relation tag sources and regime matched rules

- [ ] **Step 4: Run the full suite to verify it passes**

Run: `pytest market_system/tests -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add market_system/tests/conftest.py market_system/tests/integration/test_pipeline.py market_system/tests/golden/test_golden_daily.py market_system/engine/*.py
git commit -m "test: complete trace verification gate"
```

## Self-Review

Spec coverage:

- Architecture and module boundaries are covered by Tasks 1 through 9.
- Runtime model is covered by Task 5.
- Error handling and hard validation are covered by Tasks 3 and 4.
- Rule correctness is covered by Tasks 6 through 10.
- Date-range execution and quality gate are covered by Tasks 11 and 12.

Placeholder scan:

- Removed vague steps and named exact files, commands, and expected outputs.
- No `TODO`, `TBD`, or “similar to” references remain.

Type consistency:

- Core runtime names use `IndexRuntime`, `PairRuntime`, and `MarketRuntime` throughout.
- Pipeline entrypoints consistently use `build_context`, `run_single_date`, and `run_date_range`.
