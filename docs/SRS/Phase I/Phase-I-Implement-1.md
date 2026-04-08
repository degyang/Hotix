先把**第一批基础骨架**搭起来。
这一轮只做最底层 5 个文件，保证你项目能“站起来”：

* `requirements.txt`
* `engine/models.py`
* `engine/loader.py`
* `engine/validator.py`
* `run_daily.py`

这样你先能做到：

1. 读取原始数据
2. 读取 DSL
3. 校验配置
4. 初始化运行入口

下面代码可直接落地。

---

## 1. `requirements.txt`

```txt
pandas>=2.2.0
pyyaml>=6.0.1
pyarrow>=15.0.0
numpy>=1.26.0
```

---

## 2. `engine/models.py`

```python
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


JsonDict = Dict[str, Any]


@dataclass
class SalienceResult:
    total_score: float = 0.0
    positive_score: float = 0.0
    negative_score: float = 0.0
    warning_score: float = 0.0
    transition_score: float = 0.0
    matched_rules: List[JsonDict] = field(default_factory=list)

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass
class MarketRegimeResult:
    label: str = ""
    score: float = 0.0
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    runner_up: str = ""
    runner_up_score: float = 0.0

    def to_dict(self) -> JsonDict:
        return asdict(self)


@dataclass
class IndexRuntime:
    id: str
    date: str
    raw: JsonDict = field(default_factory=dict)
    features: JsonDict = field(default_factory=dict)
    states: JsonDict = field(default_factory=dict)
    pattern_tags: List[str] = field(default_factory=list)
    transition_tags: List[str] = field(default_factory=list)
    salience: SalienceResult = field(default_factory=SalienceResult)
    trace: JsonDict = field(default_factory=lambda: {
        "features": {},
        "states": {},
        "patterns": [],
        "transitions": [],
        "salience": [],
    })

    def get_field(self, name: str) -> Any:
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
        if name == "salience":
            return self.salience.to_dict()
        raise KeyError(f"IndexRuntime[{self.id}] field not found: {name}")

    def to_dict(self) -> JsonDict:
        return {
            "id": self.id,
            "date": self.date,
            "raw": self.raw,
            "features": self.features,
            "states": self.states,
            "pattern_tags": self.pattern_tags,
            "transition_tags": self.transition_tags,
            "salience": self.salience.to_dict(),
            "trace": self.trace,
        }


@dataclass
class PairRuntime:
    id: str
    date: str
    left: str
    right: str
    features: JsonDict = field(default_factory=dict)
    states: JsonDict = field(default_factory=dict)
    relation_tags: List[str] = field(default_factory=list)
    trace: JsonDict = field(default_factory=lambda: {
        "features": {},
        "states": {},
        "relation_tags": [],
    })

    def get_field(self, name: str) -> Any:
        if name in self.features:
            return self.features[name]
        if name in self.states:
            return self.states[name]
        if name == "relation_tags":
            return self.relation_tags
        raise KeyError(f"PairRuntime[{self.id}] field not found: {name}")

    def to_dict(self) -> JsonDict:
        return {
            "id": self.id,
            "date": self.date,
            "left": self.left,
            "right": self.right,
            "features": self.features,
            "states": self.states,
            "relation_tags": self.relation_tags,
            "trace": self.trace,
        }


@dataclass
class MarketRuntime:
    date: str
    top_positive: List[JsonDict] = field(default_factory=list)
    top_negative: List[JsonDict] = field(default_factory=list)
    top_warning: List[JsonDict] = field(default_factory=list)
    top_transition: List[JsonDict] = field(default_factory=list)
    relation_tags: List[str] = field(default_factory=list)
    market_regime: MarketRegimeResult = field(default_factory=MarketRegimeResult)
    trace: JsonDict = field(default_factory=lambda: {
        "relations": [],
        "regimes": {},
    })

    def to_dict(self) -> JsonDict:
        return {
            "date": self.date,
            "top_positive": self.top_positive,
            "top_negative": self.top_negative,
            "top_warning": self.top_warning,
            "top_transition": self.top_transition,
            "relation_tags": self.relation_tags,
            "market_regime": self.market_regime.to_dict(),
            "trace": self.trace,
        }


@dataclass
class RuntimeStore:
    indices: Dict[str, IndexRuntime] = field(default_factory=dict)
    pairs: Dict[str, PairRuntime] = field(default_factory=dict)
    market: Optional[MarketRuntime] = None

    def to_dict(self) -> JsonDict:
        return {
            "indices": {k: v.to_dict() for k, v in self.indices.items()},
            "pairs": {k: v.to_dict() for k, v in self.pairs.items()},
            "market": self.market.to_dict() if self.market else None,
        }
```

---

## 3. `engine/loader.py`

```python
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

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


def load_yaml(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_registry(path: str | Path) -> Dict[str, Any]:
    data = load_yaml(path)
    if "indices" not in data:
        raise ValueError(f"index registry missing 'indices': {path}")
    return data


def load_all_dsl(dsl_dir: str | Path) -> Dict[str, Dict[str, Any]]:
    dsl_dir = Path(dsl_dir)
    if not dsl_dir.exists():
        raise FileNotFoundError(f"DSL directory not found: {dsl_dir}")

    result: Dict[str, Dict[str, Any]] = {}
    for filename in DSL_FILES:
        path = dsl_dir / filename
        key = path.stem
        result[key] = load_yaml(path)
    return result


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    required_cols = [
        "date", "open", "high", "low", "close", "volume", "amount", "adv", "decl"
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

    numeric_cols = ["open", "high", "low", "close", "volume", "amount", "adv", "decl"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("date").reset_index(drop=True)

    if df["date"].duplicated().any():
        duplicated_dates = df.loc[df["date"].duplicated(), "date"].tolist()
        raise ValueError(f"Duplicated dates found: {duplicated_dates[:10]}")

    return df


def load_parquet_data(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Parquet file not found: {path}")
    df = pd.read_parquet(path)
    return _normalize_dataframe(df)


def load_all_data(raw_dir: str | Path, registry: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    raw_dir = Path(raw_dir)
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw data directory not found: {raw_dir}")

    data: Dict[str, pd.DataFrame] = {}
    for index_id in registry["indices"].keys():
        path = raw_dir / f"{index_id}.parquet"
        data[index_id] = load_parquet_data(path)
    return data
```

---

## 4. `engine/validator.py`

```python
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Set


class ConfigValidationError(Exception):
    """Raised when DSL or registry validation fails."""


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ConfigValidationError(message)


def _collect_ids(items: Iterable[Dict[str, Any]], label: str) -> Set[str]:
    seen: Set[str] = set()
    for item in items:
        _ensure("id" in item and item["id"], f"{label}: missing non-empty 'id'")
        _ensure(item["id"] not in seen, f"{label}: duplicated id '{item['id']}'")
        seen.add(item["id"])
    return seen


def validate_registry(registry: Dict[str, Any]) -> None:
    _ensure("indices" in registry, "registry missing 'indices'")
    _ensure(isinstance(registry["indices"], dict), "'indices' must be a dict")
    _ensure(len(registry["indices"]) > 0, "registry.indices cannot be empty")

    for index_id, meta in registry["indices"].items():
        _ensure(index_id, "index id cannot be empty")
        _ensure(isinstance(meta, dict), f"registry.indices.{index_id} must be a dict")
        _ensure("name" in meta, f"registry.indices.{index_id} missing 'name'")


def validate_features_dsl(dsl: Dict[str, Any]) -> None:
    _ensure("features" in dsl, "features.yaml missing 'features'")
    _ensure(isinstance(dsl["features"], list), "'features' must be a list")
    _collect_ids(dsl["features"], "features")

    for rule in dsl["features"]:
        _ensure("type" in rule, f"feature[{rule['id']}] missing 'type'")
        _ensure("output" in rule, f"feature[{rule['id']}] missing 'output'")
        _ensure("input" in rule and isinstance(rule["input"], list), f"feature[{rule['id']}] missing or invalid 'input'")

        rule_type = rule["type"]
        _ensure(rule_type in {"formula", "rolling", "percentile", "boolean"}, f"feature[{rule['id']}] invalid type '{rule_type}'")

        if rule_type in {"formula", "boolean"}:
            _ensure("formula" in rule, f"feature[{rule['id']}] missing 'formula'")
        if rule_type == "rolling":
            _ensure("window" in rule, f"feature[{rule['id']}] missing 'window'")
            _ensure("method" in rule, f"feature[{rule['id']}] missing 'method'")
        if rule_type == "percentile":
            _ensure("window" in rule, f"feature[{rule['id']}] missing 'window'")


def validate_states_dsl(dsl: Dict[str, Any]) -> None:
    _ensure("states" in dsl, "states.yaml missing 'states'")
    _ensure(isinstance(dsl["states"], list), "'states' must be a list")
    _collect_ids(dsl["states"], "states")

    for rule in dsl["states"]:
        _ensure("output" in rule, f"state[{rule['id']}] missing 'output'")
        _ensure(str(rule["output"]).endswith("_state"), f"state[{rule['id']}] output must end with '_state'")
        _ensure("cases" in rule and isinstance(rule["cases"], list), f"state[{rule['id']}] missing or invalid 'cases'")
        _ensure("default" in rule, f"state[{rule['id']}] missing 'default'")

        for i, case in enumerate(rule["cases"]):
            _ensure("when" in case, f"state[{rule['id']}].cases[{i}] missing 'when'")
            _ensure("value" in case, f"state[{rule['id']}].cases[{i}] missing 'value'")


def validate_tag_rules_dsl(dsl: Dict[str, Any], root_key: str, label: str) -> None:
    _ensure(root_key in dsl, f"{label} missing '{root_key}'")
    _ensure(isinstance(dsl[root_key], list), f"'{root_key}' must be a list")
    _collect_ids(dsl[root_key], label)

    for rule in dsl[root_key]:
        _ensure("when" in rule, f"{label}[{rule['id']}] missing 'when'")
        _ensure("add_tag" in rule, f"{label}[{rule['id']}] missing 'add_tag'")


def validate_salience_dsl(dsl: Dict[str, Any]) -> None:
    _ensure("salience" in dsl, "salience.yaml missing 'salience'")
    salience = dsl["salience"]
    _ensure(isinstance(salience, dict), "'salience' must be a dict")
    _ensure("scoring_rules" in salience, "salience.scoring_rules missing")
    _ensure(isinstance(salience["scoring_rules"], list), "salience.scoring_rules must be a list")
    _collect_ids(salience["scoring_rules"], "salience.scoring_rules")

    for rule in salience["scoring_rules"]:
        for required in ("when", "score", "bucket", "polarity", "reason"):
            _ensure(required in rule, f"salience[{rule['id']}] missing '{required}'")


def validate_pairs_dsl(dsl: Dict[str, Any], registry: Dict[str, Any]) -> None:
    _ensure("pairs" in dsl, "pairs.yaml missing 'pairs'")
    _ensure(isinstance(dsl["pairs"], list), "'pairs' must be a list")
    _collect_ids(dsl["pairs"], "pairs")

    valid_indices = set(registry["indices"].keys())
    for pair in dsl["pairs"]:
        for field in ("left", "right"):
            _ensure(field in pair, f"pair[{pair['id']}] missing '{field}'")
            _ensure(pair[field] in valid_indices, f"pair[{pair['id']}] unknown index '{pair[field]}'")


def validate_pair_features_dsl(dsl: Dict[str, Any]) -> None:
    _ensure("pair_features" in dsl, "pair_features.yaml missing 'pair_features'")
    _ensure(isinstance(dsl["pair_features"], list), "'pair_features' must be a list")
    _collect_ids(dsl["pair_features"], "pair_features")

    for rule in dsl["pair_features"]:
        _ensure("type" in rule, f"pair_feature[{rule['id']}] missing 'type'")
        _ensure("output" in rule, f"pair_feature[{rule['id']}] missing 'output'")
        _ensure("input" in rule and isinstance(rule["input"], list), f"pair_feature[{rule['id']}] missing or invalid 'input'")
        _ensure("formula" in rule, f"pair_feature[{rule['id']}] missing 'formula'")


def validate_pair_states_dsl(dsl: Dict[str, Any]) -> None:
    _ensure("pair_states" in dsl, "pair_states.yaml missing 'pair_states'")
    _ensure(isinstance(dsl["pair_states"], list), "'pair_states' must be a list")
    _collect_ids(dsl["pair_states"], "pair_states")

    for rule in dsl["pair_states"]:
        _ensure("output" in rule, f"pair_state[{rule['id']}] missing 'output'")
        _ensure("cases" in rule and isinstance(rule["cases"], list), f"pair_state[{rule['id']}] missing or invalid 'cases'")
        _ensure("default" in rule, f"pair_state[{rule['id']}] missing 'default'")


def validate_relation_tags_dsl(dsl: Dict[str, Any], pairs_dsl: Dict[str, Any]) -> None:
    _ensure("relation_tags" in dsl, "relation_tags.yaml missing 'relation_tags'")
    _ensure(isinstance(dsl["relation_tags"], list), "'relation_tags' must be a list")
    _collect_ids(dsl["relation_tags"], "relation_tags")

    pair_ids = {pair["id"] for pair in pairs_dsl["pairs"]}
    for rule in dsl["relation_tags"]:
        _ensure("pair" in rule, f"relation_tag[{rule['id']}] missing 'pair'")
        _ensure(rule["pair"] in pair_ids, f"relation_tag[{rule['id']}] unknown pair '{rule['pair']}'")
        _ensure("when" in rule, f"relation_tag[{rule['id']}] missing 'when'")
        _ensure("add_tag" in rule, f"relation_tag[{rule['id']}] missing 'add_tag'")


def validate_regimes_dsl(dsl: Dict[str, Any]) -> None:
    _ensure("regimes" in dsl, "regimes.yaml missing 'regimes'")
    _ensure(isinstance(dsl["regimes"], list), "'regimes' must be a list")
    _collect_ids(dsl["regimes"], "regimes")

    for regime in dsl["regimes"]:
        _ensure("label" in regime, f"regime[{regime['id']}] missing 'label'")
        _ensure("rules" in regime and isinstance(regime["rules"], list), f"regime[{regime['id']}] missing or invalid 'rules'")
        _collect_ids(regime["rules"], f"regime[{regime['id']}].rules")

        for rule in regime["rules"]:
            for required in ("when", "score", "evidence"):
                _ensure(required in rule, f"regime[{regime['id']}].rule[{rule['id']}] missing '{required}'")


def validate_all_dsl(dsl: Dict[str, Any], registry: Dict[str, Any]) -> None:
    validate_registry(registry)
    validate_features_dsl(dsl["features"])
    validate_states_dsl(dsl["states"])
    validate_tag_rules_dsl(dsl["patterns"], "patterns", "patterns")
    validate_tag_rules_dsl(dsl["transitions"], "transitions", "transitions")
    validate_salience_dsl(dsl["salience"])
    validate_pairs_dsl(dsl["pairs"], registry)
    validate_pair_features_dsl(dsl["pair_features"])
    validate_pair_states_dsl(dsl["pair_states"])
    validate_relation_tags_dsl(dsl["relation_tags"], dsl["pairs"])
    validate_regimes_dsl(dsl["regimes"])
```

---

## 5. `run_daily.py`

先做成可运行入口，不做实际计算。

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.loader import load_all_data, load_all_dsl, load_registry
from engine.validator import validate_all_dsl, ConfigValidationError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run market structure daily pipeline.")
    parser.add_argument("--date", type=str, default=None, help="Run single date, e.g. 2026-04-05")
    parser.add_argument("--start", type=str, default=None, help="Run start date")
    parser.add_argument("--end", type=str, default=None, help="Run end date")
    parser.add_argument("--print-summary", action="store_true", help="Print loaded config summary")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    project_root = Path(__file__).resolve().parent
    dsl_dir = project_root / "dsl"
    raw_dir = project_root / "data" / "raw"
    registry_path = project_root / "config" / "index_registry.yaml"

    print("[1/4] Loading registry...")
    registry = load_registry(registry_path)

    print("[2/4] Loading DSL files...")
    dsl = load_all_dsl(dsl_dir)

    print("[3/4] Validating configuration...")
    try:
        validate_all_dsl(dsl, registry)
    except ConfigValidationError as e:
        raise SystemExit(f"Configuration validation failed: {e}") from e

    print("[4/4] Loading raw market data...")
    data = load_all_data(raw_dir, registry)

    if args.print_summary:
        summary = {
            "indices": list(registry["indices"].keys()),
            "dsl_rule_counts": {
                "features": len(dsl["features"]["features"]),
                "states": len(dsl["states"]["states"]),
                "patterns": len(dsl["patterns"]["patterns"]),
                "transitions": len(dsl["transitions"]["transitions"]),
                "salience": len(dsl["salience"]["salience"]["scoring_rules"]),
                "pairs": len(dsl["pairs"]["pairs"]),
                "pair_features": len(dsl["pair_features"]["pair_features"]),
                "pair_states": len(dsl["pair_states"]["pair_states"]),
                "relation_tags": len(dsl["relation_tags"]["relation_tags"]),
                "regimes": len(dsl["regimes"]["regimes"]),
            },
            "data_rows": {k: len(v) for k, v in data.items()},
            "date_range": {
                k: {
                    "start": v["date"].min(),
                    "end": v["date"].max(),
                }
                for k, v in data.items()
            },
            "run_args": {
                "date": args.date,
                "start": args.start,
                "end": args.end,
            },
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    print("Bootstrap completed successfully.")
    print("Next step: implement feature/state/pipeline engines.")


if __name__ == "__main__":
    main()
```

---

# 现在你要做的事

按顺序执行：

1. 把这 5 个文件建好
2. 把前一条里的 10 个 DSL 文件也建好
3. 准备 `config/index_registry.yaml` 和 `data/raw/*.parquet`
4. 运行：

```bash
python run_daily.py --print-summary
```

你预期应该看到：

* registry 加载成功
* DSL 校验成功
* 原始数据行数与日期范围
* Bootstrap completed successfully

---

# 下一轮最应该继续搭的 4 个文件

跑通这一步后，下一轮直接搭：

* `engine/resolver.py`
* `engine/expression.py`
* `engine/feature_engine.py`
* `engine/state_engine.py`

这 4 个一接上，你就能开始真正产出单指数状态。
