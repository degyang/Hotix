下面继续，把**单指数可运行的核心 4 个文件**搭起来：

* `engine/resolver.py`
* `engine/expression.py`
* `engine/feature_engine.py`
* `engine/state_engine.py`

这一轮的目标很明确：

1. 能在单日上下文里解析 `self.xxx` / `prev.xxx`
2. 能安全执行 state/pattern 用到的布尔表达式
3. 能计算第一版 feature
4. 能推导第一版 state

先不做 pattern / transition / salience。
先把 **feature + state** 跑通。

---

# 1. `engine/resolver.py`

```python
from __future__ import annotations

from typing import Any, Dict, Optional

from engine.models import IndexRuntime, PairRuntime, MarketRuntime


class ResolveError(Exception):
    """Raised when a reference path cannot be resolved."""


class Resolver:
    """
    Resolve DSL field references.

    Supported contexts:
    - index layer: self.xxx, prev.xxx
    - pair layer: self.xxx, left.xxx, right.xxx
    - market/regime layer: index.xxx.yyy, pair.xxx.yyy, market.xxx
    """

    def __init__(
        self,
        current: Any | None = None,
        prev: Any | None = None,
        indices: Dict[str, IndexRuntime] | None = None,
        pairs: Dict[str, PairRuntime] | None = None,
        market: MarketRuntime | None = None,
    ) -> None:
        self.current = current
        self.prev = prev
        self.indices = indices or {}
        self.pairs = pairs or {}
        self.market = market

    def resolve(self, ref: str) -> Any:
        ref = ref.strip()
        if not ref:
            raise ResolveError("Empty reference")

        if "." not in ref:
            return self._resolve_from_current(ref)

        head, tail = ref.split(".", 1)

        if head == "self":
            if self.current is None:
                raise ResolveError(f"No current context for reference: {ref}")
            return self._resolve_object_path(self.current, tail)

        if head == "prev":
            if self.prev is None:
                raise ResolveError(f"No previous context for reference: {ref}")
            return self._resolve_object_path(self.prev, tail)

        if head == "left":
            if not isinstance(self.current, PairRuntime):
                raise ResolveError(f"'left' only valid in pair context: {ref}")
            left_id = self.current.left
            if left_id not in self.indices:
                raise ResolveError(f"Left index runtime not found: {left_id}")
            return self._resolve_object_path(self.indices[left_id], tail)

        if head == "right":
            if not isinstance(self.current, PairRuntime):
                raise ResolveError(f"'right' only valid in pair context: {ref}")
            right_id = self.current.right
            if right_id not in self.indices:
                raise ResolveError(f"Right index runtime not found: {right_id}")
            return self._resolve_object_path(self.indices[right_id], tail)

        if head == "index":
            index_id, subpath = self._split_first(tail)
            if index_id not in self.indices:
                raise ResolveError(f"Unknown index id in reference: {ref}")
            return self._resolve_object_path(self.indices[index_id], subpath)

        if head == "pair":
            pair_id, subpath = self._split_first(tail)
            if pair_id not in self.pairs:
                raise ResolveError(f"Unknown pair id in reference: {ref}")
            return self._resolve_object_path(self.pairs[pair_id], subpath)

        if head == "market":
            if self.market is None:
                raise ResolveError(f"No market context for reference: {ref}")
            return self._resolve_object_path(self.market, tail)

        raise ResolveError(f"Unsupported reference head: {head}")

    def _split_first(self, path: str) -> tuple[str, str]:
        if "." not in path:
            raise ResolveError(f"Reference missing nested path: {path}")
        return path.split(".", 1)

    def _resolve_from_current(self, name: str) -> Any:
        if self.current is None:
            raise ResolveError(f"No current context for bare reference: {name}")
        return self._resolve_object_path(self.current, name)

    def _resolve_object_path(self, obj: Any, path: str) -> Any:
        parts = path.split(".")
        value = obj

        for part in parts:
            value = self._resolve_one(value, part)

        return value

    def _resolve_one(self, obj: Any, name: str) -> Any:
        if hasattr(obj, "get_field"):
            try:
                return obj.get_field(name)
            except KeyError:
                pass

        if hasattr(obj, name):
            return getattr(obj, name)

        if isinstance(obj, dict):
            if name in obj:
                return obj[name]

        raise ResolveError(f"Cannot resolve '{name}' from object type {type(obj).__name__}")
```

---

# 2. `engine/expression.py`

这一版先做**受限安全表达式执行器**。
不要做完整 AST。
只允许：

* `self.xxx`, `prev.xxx` 等字段引用
* `and or not in`
* 比较运算
* 基本算术
* 白名单函数：`abs max min len`

```python
from __future__ import annotations

import re
from typing import Any, Dict

from engine.resolver import Resolver, ResolveError


class ExpressionError(Exception):
    """Raised when expression evaluation fails."""


SAFE_GLOBALS: Dict[str, Any] = {
    "__builtins__": {},
    "abs": abs,
    "max": max,
    "min": min,
    "len": len,
    "true": True,
    "false": False,
    "True": True,
    "False": False,
}


REF_PATTERN = re.compile(
    r"\b("
    r"self\.[A-Za-z_][A-Za-z0-9_\.]*|"
    r"prev\.[A-Za-z_][A-Za-z0-9_\.]*|"
    r"left\.[A-Za-z_][A-Za-z0-9_\.]*|"
    r"right\.[A-Za-z_][A-Za-z0-9_\.]*|"
    r"index\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_\.]*|"
    r"pair\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_\.]*|"
    r"market\.[A-Za-z_][A-Za-z0-9_\.]*"
    r")\b"
)

BARE_IDENTIFIER_PATTERN = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")


RESERVED_WORDS = {
    "and", "or", "not", "in",
    "True", "False", "true", "false",
    "abs", "max", "min", "len",
}


def _replace_refs(expr: str, resolver: Resolver) -> tuple[str, Dict[str, Any]]:
    env: Dict[str, Any] = {}

    def replacer(match: re.Match[str]) -> str:
        ref = match.group(1)
        key = f"__ref_{len(env)}"
        env[key] = resolver.resolve(ref)
        return key

    new_expr = REF_PATTERN.sub(replacer, expr)
    return new_expr, env


def _replace_bare_identifiers(expr: str, resolver: Resolver, env: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """
    Replace bare names like close, ma_20, trend_state with current-context values.
    Excludes:
    - reserved words
    - already replaced __ref_x variables
    """
    def replacer(match: re.Match[str]) -> str:
        name = match.group(1)

        if name in RESERVED_WORDS:
            return name
        if name.startswith("__ref_"):
            return name

        # numeric-like field names not expected here
        try:
            value = resolver.resolve(name)
        except ResolveError:
            return name  # may be part of string content or unsupported token

        key = f"__ref_{len(env)}"
        env[key] = value
        return key

    new_expr = BARE_IDENTIFIER_PATTERN.sub(replacer, expr)
    return new_expr, env


def evaluate_expression(expr: str, resolver: Resolver, rule_id: str = "") -> Any:
    """
    Evaluate a restricted expression against runtime context.
    """
    try:
        replaced, env = _replace_refs(expr, resolver)
        replaced, env = _replace_bare_identifiers(replaced, resolver, env)
        return eval(replaced, SAFE_GLOBALS, env)
    except Exception as e:
        label = f" [rule_id={rule_id}]" if rule_id else ""
        raise ExpressionError(f"Failed to evaluate expression{label}: {expr}\nError: {e}") from e
```

---

# 3. `engine/feature_engine.py`

这里做第一版 feature 计算。
遵循两个原则：

1. `features.yaml` 顺序执行
2. 依赖字段从：

   * raw 列
   * 已算好的 features
     中读取

这一版不走 `expression.py` 处理 feature formula，原因是 feature 里有 `delay / rolling_* / percentile`，用 DataFrame 更稳。

```python
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd

from engine.models import IndexRuntime


class FeatureEngineError(Exception):
    """Raised when feature computation fails."""


def _safe_float(value: Any) -> float | bool | None:
    if pd.isna(value):
        return None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value)
    return value


def _rolling_percentile_last(series: pd.Series, window: int) -> float | None:
    if len(series) < window:
        return None
    window_series = series.iloc[-window:]
    current = window_series.iloc[-1]
    if pd.isna(current):
        return None
    valid = window_series.dropna()
    if len(valid) == 0:
        return None
    return float((valid <= current).mean())


def _rolling_max_prev(series: pd.Series, window: int) -> float | None:
    if len(series) <= window:
        return None
    return _safe_float(series.iloc[-(window + 1):-1].max())


def _rolling_min_prev(series: pd.Series, window: int) -> float | None:
    if len(series) <= window:
        return None
    return _safe_float(series.iloc[-(window + 1):-1].min())


def _build_feature_context(df_slice: pd.DataFrame, computed: Dict[str, Any]) -> Dict[str, pd.Series]:
    context: Dict[str, pd.Series] = {}
    for col in df_slice.columns:
        context[col] = df_slice[col]
    for feature_name, value in computed.items():
        if feature_name not in context:
            # for formula features, prefer building from full derived series when available elsewhere;
            # first version only supports direct last-value dependencies from already-computed features.
            context[feature_name] = pd.Series([value] * len(df_slice), index=df_slice.index)
    return context


def _compute_formula_feature(rule_id: str, formula: str, df_slice: pd.DataFrame, computed: Dict[str, Any]) -> Any:
    """
    First-version formula support is explicit by rule_id.
    This avoids unsafe generic formula parsing for time-series operations.
    """
    context = _build_feature_context(df_slice, computed)

    close = context.get("close")
    amount = context.get("amount")
    adv = context.get("adv")
    decl = context.get("decl")
    high = context.get("high")
    low = context.get("low")

    if rule_id == "ret_1d":
        if len(close) < 2:
            return None
        return _safe_float(close.iloc[-1] / close.iloc[-2] - 1)

    if rule_id == "ret_5d":
        if len(close) < 6:
            return None
        return _safe_float(close.iloc[-1] / close.iloc[-6] - 1)

    if rule_id == "ret_20d":
        if len(close) < 21:
            return None
        return _safe_float(close.iloc[-1] / close.iloc[-21] - 1)

    if rule_id == "ma_slope_20":
        ma_20_series = close.rolling(20).mean()
        if len(ma_20_series.dropna()) < 6:
            return None
        return _safe_float(ma_20_series.iloc[-1] / ma_20_series.iloc[-6] - 1)

    if rule_id == "distance_to_ma20":
        ma_20 = close.rolling(20).mean().iloc[-1]
        if pd.isna(ma_20) or ma_20 == 0:
            return None
        return _safe_float(close.iloc[-1] / ma_20 - 1)

    if rule_id == "amount_ratio_1_20":
        amount_ma_20 = amount.rolling(20).mean().iloc[-1]
        if pd.isna(amount_ma_20) or amount_ma_20 == 0:
            return None
        return _safe_float(amount.iloc[-1] / amount_ma_20)

    if rule_id == "amount_ratio_5_20":
        if len(amount) < 20:
            return None
        ma5 = amount.rolling(5).mean().iloc[-1]
        ma20 = amount.rolling(20).mean().iloc[-1]
        if pd.isna(ma5) or pd.isna(ma20) or ma20 == 0:
            return None
        return _safe_float(ma5 / ma20)

    if rule_id == "breadth_ratio":
        adv_last = adv.iloc[-1]
        decl_last = decl.iloc[-1]
        denom = adv_last + decl_last + 1e-9
        return _safe_float(adv_last / denom)

    if rule_id == "breadth_diff":
        return _safe_float(adv.iloc[-1] - decl.iloc[-1])

    if rule_id == "true_range":
        if len(close) < 2:
            return None
        prev_close = close.iloc[-2]
        curr_high = high.iloc[-1]
        curr_low = low.iloc[-1]
        tr = max(
            curr_high - curr_low,
            abs(curr_high - prev_close),
            abs(curr_low - prev_close),
        )
        return _safe_float(tr)

    if rule_id == "atr_pct_14":
        if len(df_slice) < 15:
            return None
        prev_close = close.shift(1)
        tr_series = pd.concat(
            [
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        atr_14 = tr_series.rolling(14).mean().iloc[-1]
        curr_close = close.iloc[-1]
        if pd.isna(atr_14) or curr_close == 0:
            return None
        return _safe_float(atr_14 / curr_close)

    if rule_id == "breakout_20d":
        prev_max = _rolling_max_prev(high, 20)
        if prev_max is None:
            return None
        return bool(close.iloc[-1] > prev_max)

    if rule_id == "breakdown_20d":
        prev_min = _rolling_min_prev(low, 20)
        if prev_min is None:
            return None
        return bool(close.iloc[-1] < prev_min)

    raise FeatureEngineError(f"Unsupported formula feature rule_id: {rule_id}")


def compute_index_features(
    index_id: str,
    date: str,
    df: pd.DataFrame,
    features_dsl: Dict[str, Any],
) -> IndexRuntime:
    """
    Compute all configured features for a single index on a single date.
    """
    df_slice = df[df["date"] <= date].copy()
    if df_slice.empty:
        raise FeatureEngineError(f"No data available for index={index_id}, date={date}")

    last_row = df_slice.iloc[-1].to_dict()
    raw = {k: _safe_float(v) for k, v in last_row.items()}

    runtime = IndexRuntime(id=index_id, date=date, raw=raw)

    for rule in features_dsl["features"]:
        rule_id = rule["id"]
        rule_type = rule["type"]
        output = rule["output"]

        try:
            if rule_type == "rolling":
                input_name = rule["input"][0]
                window = int(rule["window"])
                method = rule["method"]

                series = df_slice[input_name]
                if method == "mean":
                    value = _safe_float(series.rolling(window).mean().iloc[-1]) if len(series) >= window else None
                elif method == "max":
                    value = _safe_float(series.rolling(window).max().iloc[-1]) if len(series) >= window else None
                elif method == "min":
                    value = _safe_float(series.rolling(window).min().iloc[-1]) if len(series) >= window else None
                else:
                    raise FeatureEngineError(f"Unsupported rolling method: {method}")

            elif rule_type == "percentile":
                input_name = rule["input"][0]
                window = int(rule["window"])
                series = df_slice[input_name]
                value = _rolling_percentile_last(series, window)

            elif rule_type in {"formula", "boolean"}:
                value = _compute_formula_feature(rule_id, rule["formula"], df_slice, runtime.features)

            else:
                raise FeatureEngineError(f"Unsupported feature type: {rule_type}")

            runtime.features[output] = value
            runtime.trace["features"][output] = {
                "rule_id": rule_id,
                "rule_type": rule_type,
                "output": value,
            }

        except Exception as e:
            raise FeatureEngineError(
                f"Failed computing feature '{output}' for index={index_id}, date={date}: {e}"
            ) from e

    return runtime
```

---

# 4. `engine/state_engine.py`

这一层读取 feature runtime，然后跑 `states.yaml`。

```python
from __future__ import annotations

from typing import Any, Dict, Optional

from engine.expression import evaluate_expression, ExpressionError
from engine.models import IndexRuntime
from engine.resolver import Resolver


class StateEngineError(Exception):
    """Raised when state derivation fails."""


def derive_index_states(
    runtime: IndexRuntime,
    states_dsl: Dict[str, Any],
    prev_runtime: IndexRuntime | None = None,
) -> IndexRuntime:
    """
    Derive all configured states for a single index runtime.
    """
    resolver = Resolver(current=runtime, prev=prev_runtime)

    for rule in states_dsl["states"]:
        rule_id = rule["id"]
        output = rule["output"]
        matched_case_index: Optional[int] = None
        matched_when: Optional[str] = None
        matched_value: Any = None

        try:
            for idx, case in enumerate(rule["cases"]):
                when_expr = case["when"]
                hit = evaluate_expression(when_expr, resolver, rule_id=rule_id)
                if bool(hit):
                    matched_case_index = idx
                    matched_when = when_expr
                    matched_value = case["value"]
                    break

            if matched_value is None:
                matched_value = rule["default"]

            runtime.states[output] = matched_value
            runtime.trace["states"][output] = {
                "rule_id": rule_id,
                "matched_case": matched_case_index,
                "when": matched_when,
                "value": matched_value,
            }

        except ExpressionError as e:
            raise StateEngineError(
                f"Failed deriving state '{output}' for index={runtime.id}, date={runtime.date}: {e}"
            ) from e

    return runtime
```

---

# 5. 现在怎么接到 `run_daily.py`

你现在可以把 `run_daily.py` 小改一下，先验证 feature/state 是否跑通。

把下面这段加进去，用来测试某一天。

---

## 替换版 `run_daily.py`

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.feature_engine import compute_index_features
from engine.loader import load_all_data, load_all_dsl, load_registry
from engine.state_engine import derive_index_states
from engine.validator import validate_all_dsl, ConfigValidationError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run market structure daily pipeline.")
    parser.add_argument("--date", type=str, default=None, help="Run single date, e.g. 2026-04-05")
    parser.add_argument("--start", type=str, default=None, help="Run start date")
    parser.add_argument("--end", type=str, default=None, help="Run end date")
    parser.add_argument("--print-summary", action="store_true", help="Print loaded config summary")
    parser.add_argument("--debug-index", type=str, default=None, help="Print feature/state result for one index id")
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
                "debug_index": args.debug_index,
            },
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.date and args.debug_index:
        if args.debug_index not in data:
            raise SystemExit(f"Unknown index id: {args.debug_index}")

        df = data[args.debug_index]

        current_runtime = compute_index_features(
            index_id=args.debug_index,
            date=args.date,
            df=df,
            features_dsl=dsl["features"],
        )

        prev_dates = df[df["date"] < args.date]["date"]
        prev_runtime = None
        if not prev_dates.empty:
            prev_date = prev_dates.iloc[-1]
            prev_runtime = compute_index_features(
                index_id=args.debug_index,
                date=prev_date,
                df=df,
                features_dsl=dsl["features"],
            )
            prev_runtime = derive_index_states(
                runtime=prev_runtime,
                states_dsl=dsl["states"],
                prev_runtime=None,
            )

        current_runtime = derive_index_states(
            runtime=current_runtime,
            states_dsl=dsl["states"],
            prev_runtime=prev_runtime,
        )

        print(json.dumps(current_runtime.to_dict(), ensure_ascii=False, indent=2))
        return

    print("Bootstrap + feature/state engine completed.")
    print("Next step: pattern / transition / salience / pair / regime.")


if __name__ == "__main__":
    main()
```

---

# 6. 你现在怎么测试

先跑：

```bash
python run_daily.py --print-summary
```

确认基础加载没问题。

然后跑：

```bash
python run_daily.py --date 2026-04-05 --debug-index hs300
```

或者：

```bash
python run_daily.py --date 2026-04-05 --debug-index cyb
python run_daily.py --date 2026-04-05 --debug-index csi1000
```

你应该能看到一个 JSON，里面至少有：

* `raw`
* `features`
* `states`
* `trace.features`
* `trace.states`

---

# 7. 这一轮完成后的验收标准

满足下面 5 条，就说明这轮搭建成功：

1. `--print-summary` 正常输出
2. `--debug-index hs300 --date ...` 能正常输出 JSON
3. `features` 中至少 20 个字段大部分有值
4. `states` 中有：

   * trend_state
   * position_state
   * volume_state
   * breadth_state
   * volatility_state
5. `trace` 中能看到每个 state 命中的 rule 与 case

---

# 8. 这版代码的已知限制

这是故意保守的，不是遗漏。

## 8.1 feature formula 不是通用公式解析

而是按 `rule_id` 显式实现。
这样第一版最稳。

## 8.2 expression 目前基于安全 `eval`

够跑 state/pattern/regime 第一版，但后面可以替换成 AST。

## 8.3 暂时没有区间回放 pipeline

目前只支持单日 debug 单指数。

这正好是我们下一轮要补的。

---

# 9. 下一轮该搭什么

跑通这一轮后，下一步直接接：

* `engine/tag_engine.py`
* `engine/salience_engine.py`
* `engine/pair_engine.py`
* `engine/regime_engine.py`

顺序建议是：

1. pattern / transition
2. salience
3. pair
4. regime

这样你就能从“单指数状态”走到“市场结构结论”。
