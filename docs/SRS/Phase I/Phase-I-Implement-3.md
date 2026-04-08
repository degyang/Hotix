下面继续，把后半段骨架接上：
* `engine/tag_engine.py`
* `engine/salience_engine.py`
* `engine/pair_engine.py`
* `engine/regime_engine.py`

这一轮完成后，你就能从：
* 单指数 raw
* 单指数 feature/state

走到：
* pattern / transition
* salience
* pair relation
* regime

也就是第一版闭环。

---

## 1. `engine/tag_engine.py`

这个文件统一处理三类标签：
* 单指数 `patterns`
* 单指数 `transitions`
* pair `relation_tags`

```python
from __future__ import annotations

from typing import Any, Dict, List

from engine.expression import evaluate_expression, ExpressionError
from engine.models import IndexRuntime, PairRuntime
from engine.resolver import Resolver


class TagEngineError(Exception):
    """Raised when tag detection fails."""


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def detect_index_patterns(
    runtime: IndexRuntime,
    patterns_dsl: Dict[str, Any],
    prev_runtime: IndexRuntime | None = None,
) -> IndexRuntime:
    resolver = Resolver(current=runtime, prev=prev_runtime)

    hits: List[str] = []
    traces: List[Dict[str, Any]] = []

    for rule in patterns_dsl["patterns"]:
        rule_id = rule["id"]
        try:
            hit = evaluate_expression(rule["when"], resolver, rule_id=rule_id)
            if bool(hit):
                tag = rule["add_tag"]
                hits.append(tag)
                traces.append({
                    "rule_id": rule_id,
                    "tag": tag,
                    "group": rule.get("group"),
                    "priority": rule.get("priority"),
                })
        except ExpressionError as e:
            raise TagEngineError(
                f"Failed detecting pattern tags for index={runtime.id}, date={runtime.date}: {e}"
            ) from e

    runtime.pattern_tags = _dedupe_keep_order(hits)
    runtime.trace["patterns"] = traces
    return runtime


def detect_index_transitions(
    runtime: IndexRuntime,
    transitions_dsl: Dict[str, Any],
    prev_runtime: IndexRuntime | None = None,
) -> IndexRuntime:
    resolver = Resolver(current=runtime, prev=prev_runtime)

    hits: List[str] = []
    traces: List[Dict[str, Any]] = []

    if prev_runtime is None:
        runtime.transition_tags = []
        runtime.trace["transitions"] = []
        return runtime

    for rule in transitions_dsl["transitions"]:
        rule_id = rule["id"]
        try:
            hit = evaluate_expression(rule["when"], resolver, rule_id=rule_id)
            if bool(hit):
                tag = rule["add_tag"]
                hits.append(tag)
                traces.append({
                    "rule_id": rule_id,
                    "tag": tag,
                })
        except ExpressionError as e:
            raise TagEngineError(
                f"Failed detecting transition tags for index={runtime.id}, date={runtime.date}: {e}"
            ) from e

    runtime.transition_tags = _dedupe_keep_order(hits)
    runtime.trace["transitions"] = traces
    return runtime


def detect_pair_relation_tags(
    runtime: PairRuntime,
    relation_tags_dsl: Dict[str, Any],
    indices: Dict[str, IndexRuntime],
) -> PairRuntime:
    resolver = Resolver(current=runtime, indices=indices)

    hits: List[str] = []
    traces: List[Dict[str, Any]] = []

    for rule in relation_tags_dsl["relation_tags"]:
        if rule["pair"] != runtime.id:
            continue

        rule_id = rule["id"]
        try:
            hit = evaluate_expression(rule["when"], resolver, rule_id=rule_id)
            if bool(hit):
                tag = rule["add_tag"]
                hits.append(tag)
                traces.append({
                    "rule_id": rule_id,
                    "tag": tag,
                    "group": rule.get("group"),
                    "priority": rule.get("priority"),
                })
        except ExpressionError as e:
            raise TagEngineError(
                f"Failed detecting relation tags for pair={runtime.id}, date={runtime.date}: {e}"
            ) from e

    runtime.relation_tags = _dedupe_keep_order(hits)
    runtime.trace["relation_tags"] = traces
    return runtime
```

---

## 2. `engine/salience_engine.py`

这一层做三件事：

1. 给单指数打分
2. 写入 `runtime.salience`
3. 在 market 层汇总 top positive / negative / warning / transition

```python
from __future__ import annotations

from typing import Any, Dict, List

from engine.expression import evaluate_expression, ExpressionError
from engine.models import IndexRuntime, MarketRuntime
from engine.resolver import Resolver


class SalienceEngineError(Exception):
    """Raised when salience scoring fails."""


def score_index_salience(
    runtime: IndexRuntime,
    salience_dsl: Dict[str, Any],
    prev_runtime: IndexRuntime | None = None,
) -> IndexRuntime:
    resolver = Resolver(current=runtime, prev=prev_runtime)

    total_score = 0.0
    positive_score = 0.0
    negative_score = 0.0
    warning_score = 0.0
    transition_score = 0.0
    matched_rules: List[Dict[str, Any]] = []

    for rule in salience_dsl["salience"]["scoring_rules"]:
        rule_id = rule["id"]
        try:
            hit = evaluate_expression(rule["when"], resolver, rule_id=rule_id)
            if not bool(hit):
                continue

            score = float(rule["score"])
            bucket = rule["bucket"]
            polarity = rule["polarity"]
            reason = rule["reason"]

            total_score += score

            if bucket == "positive":
                positive_score += score
            elif bucket == "negative":
                negative_score += score
            elif bucket == "warning":
                warning_score += score
            elif bucket == "transition":
                transition_score += score
            elif bucket == "positive_or_negative":
                if polarity == "positive":
                    positive_score += score
                elif polarity == "negative":
                    negative_score += score
            elif bucket == "warning_or_transition":
                warning_score += score

            matched_rules.append({
                "rule_id": rule_id,
                "group": rule.get("group"),
                "score": score,
                "bucket": bucket,
                "polarity": polarity,
                "reason": reason,
            })

        except ExpressionError as e:
            raise SalienceEngineError(
                f"Failed scoring salience for index={runtime.id}, date={runtime.date}: {e}"
            ) from e

    runtime.salience.total_score = total_score
    runtime.salience.positive_score = positive_score
    runtime.salience.negative_score = negative_score
    runtime.salience.warning_score = warning_score
    runtime.salience.transition_score = transition_score
    runtime.salience.matched_rules = matched_rules
    runtime.trace["salience"] = matched_rules
    return runtime


def build_market_salience(
    date: str,
    indices: Dict[str, IndexRuntime],
) -> MarketRuntime:
    market = MarketRuntime(date=date)

    positive_items: List[Dict[str, Any]] = []
    negative_items: List[Dict[str, Any]] = []
    warning_items: List[Dict[str, Any]] = []
    transition_items: List[Dict[str, Any]] = []

    for index_id, runtime in indices.items():
        if runtime.salience.positive_score > 0:
            positive_items.append({
                "asset": index_id,
                "score": runtime.salience.positive_score,
                "reasons": [r["reason"] for r in runtime.salience.matched_rules if r["bucket"] == "positive"],
            })

        if runtime.salience.negative_score > 0:
            negative_items.append({
                "asset": index_id,
                "score": runtime.salience.negative_score,
                "reasons": [r["reason"] for r in runtime.salience.matched_rules if r["bucket"] == "negative"],
            })

        if runtime.salience.warning_score > 0:
            warning_items.append({
                "asset": index_id,
                "score": runtime.salience.warning_score,
                "reasons": [r["reason"] for r in runtime.salience.matched_rules if r["bucket"] == "warning"],
            })

        if runtime.salience.transition_score > 0:
            transition_items.append({
                "asset": index_id,
                "score": runtime.salience.transition_score,
                "reasons": [r["reason"] for r in runtime.salience.matched_rules if r["bucket"] == "transition"],
            })

    market.top_positive = sorted(positive_items, key=lambda x: x["score"], reverse=True)
    market.top_negative = sorted(negative_items, key=lambda x: x["score"], reverse=True)
    market.top_warning = sorted(warning_items, key=lambda x: x["score"], reverse=True)
    market.top_transition = sorted(transition_items, key=lambda x: x["score"], reverse=True)

    return market
```

---

## 3. `engine/pair_engine.py`

这里完成：

1. 创建 pair runtime
2. 计算 pair features
3. 推导 pair states
4. relation tags 交给 `tag_engine.py`

```python
from __future__ import annotations

from typing import Any, Dict

from engine.expression import evaluate_expression, ExpressionError
from engine.models import IndexRuntime, PairRuntime
from engine.resolver import Resolver


class PairEngineError(Exception):
    """Raised when pair computation fails."""


def create_pair_runtime(pair_def: Dict[str, Any], date: str) -> PairRuntime:
    return PairRuntime(
        id=pair_def["id"],
        date=date,
        left=pair_def["left"],
        right=pair_def["right"],
    )


def compute_pair_features(
    runtime: PairRuntime,
    pair_features_dsl: Dict[str, Any],
    indices: Dict[str, IndexRuntime],
) -> PairRuntime:
    resolver = Resolver(current=runtime, indices=indices)

    for rule in pair_features_dsl["pair_features"]:
        rule_id = rule["id"]
        output = rule["output"]

        try:
            value = evaluate_expression(rule["formula"], resolver, rule_id=rule_id)
            runtime.features[output] = value
            runtime.trace["features"][output] = {
                "rule_id": rule_id,
                "output": value,
            }
        except ExpressionError as e:
            raise PairEngineError(
                f"Failed computing pair feature '{output}' for pair={runtime.id}, date={runtime.date}: {e}"
            ) from e

    return runtime


def derive_pair_states(
    runtime: PairRuntime,
    pair_states_dsl: Dict[str, Any],
    indices: Dict[str, IndexRuntime],
) -> PairRuntime:
    resolver = Resolver(current=runtime, indices=indices)

    for rule in pair_states_dsl["pair_states"]:
        rule_id = rule["id"]
        output = rule["output"]
        matched_case_index = None
        matched_when = None
        matched_value = None

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
            raise PairEngineError(
                f"Failed deriving pair state '{output}' for pair={runtime.id}, date={runtime.date}: {e}"
            ) from e

    return runtime
```

---

## 4. `engine/regime_engine.py`

这层做：

1. 汇总 pair relation tags 到 market
2. 遍历每个 regime 累分
3. 输出最高分和证据

```python
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from engine.expression import evaluate_expression, ExpressionError
from engine.models import IndexRuntime, PairRuntime, MarketRuntime, MarketRegimeResult
from engine.resolver import Resolver


class RegimeEngineError(Exception):
    """Raised when regime scoring fails."""


def collect_market_relation_tags(
    market: MarketRuntime,
    pairs: Dict[str, PairRuntime],
) -> MarketRuntime:
    tags: List[str] = []
    traces: List[Dict[str, Any]] = []

    seen = set()
    for pair_id, pair_runtime in pairs.items():
        for tag in pair_runtime.relation_tags:
            if tag not in seen:
                seen.add(tag)
                tags.append(tag)
                traces.append({
                    "pair_id": pair_id,
                    "tag": tag,
                })

    market.relation_tags = tags
    market.trace["relations"] = traces
    return market


def score_market_regime(
    market: MarketRuntime,
    indices: Dict[str, IndexRuntime],
    pairs: Dict[str, PairRuntime],
    regimes_dsl: Dict[str, Any],
) -> MarketRuntime:
    regime_scores: Dict[str, float] = {}
    regime_evidence: Dict[str, List[str]] = {}
    regime_trace: Dict[str, Any] = {}

    resolver = Resolver(
        current=market,
        indices=indices,
        pairs=pairs,
        market=market,
    )

    for regime in regimes_dsl["regimes"]:
        regime_id = regime["id"]
        label = regime["label"]
        total_score = 0.0
        evidence: List[str] = []
        matched_rules: List[Dict[str, Any]] = []

        for rule in regime["rules"]:
            rule_id = rule["id"]
            try:
                hit = evaluate_expression(rule["when"], resolver, rule_id=rule_id)
                if bool(hit):
                    score = float(rule["score"])
                    total_score += score
                    evidence.append(rule["evidence"])
                    matched_rules.append({
                        "rule_id": rule_id,
                        "score": score,
                        "evidence": rule["evidence"],
                    })
            except ExpressionError as e:
                raise RegimeEngineError(
                    f"Failed scoring regime '{regime_id}' on date={market.date}: {e}"
                ) from e

        regime_scores[regime_id] = total_score
        regime_evidence[regime_id] = evidence
        regime_trace[regime_id] = {
            "label": label,
            "score": total_score,
            "matched_rules": matched_rules,
        }

    market.trace["regimes"] = regime_trace

    if not regime_scores:
        market.market_regime = MarketRegimeResult(
            label="",
            score=0.0,
            confidence=0.0,
            evidence=[],
        )
        return market

    sorted_regimes = sorted(regime_scores.items(), key=lambda x: x[1], reverse=True)
    top_regime_id, top_score = sorted_regimes[0]
    runner_up_id, runner_up_score = (sorted_regimes[1] if len(sorted_regimes) > 1 else ("", 0.0))

    top_regime_label = next(r["label"] for r in regimes_dsl["regimes"] if r["id"] == top_regime_id)
    runner_up_label = ""
    if runner_up_id:
        runner_up_label = next(r["label"] for r in regimes_dsl["regimes"] if r["id"] == runner_up_id)

    total_all_scores = sum(regime_scores.values())
    confidence = (top_score / total_all_scores) if total_all_scores > 0 else 0.0

    market.market_regime = MarketRegimeResult(
        label=top_regime_label,
        score=top_score,
        confidence=confidence,
        evidence=regime_evidence[top_regime_id],
        runner_up=runner_up_label,
        runner_up_score=runner_up_score,
    )
    return market
```

---

# 5. 现在把它们接进 `run_daily.py`

下面给你一个升级版 `run_daily.py`。
这版已经能跑完整的：

* feature
* state
* pattern
* transition
* salience
* pair
* relation
* regime

先不做区间回放，只做**单日完整闭环**。

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.feature_engine import compute_index_features
from engine.loader import load_all_data, load_all_dsl, load_registry
from engine.pair_engine import create_pair_runtime, compute_pair_features, derive_pair_states
from engine.regime_engine import collect_market_relation_tags, score_market_regime
from engine.salience_engine import score_index_salience, build_market_salience
from engine.state_engine import derive_index_states
from engine.tag_engine import (
    detect_index_patterns,
    detect_index_transitions,
    detect_pair_relation_tags,
)
from engine.validator import validate_all_dsl, ConfigValidationError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run market structure daily pipeline.")
    parser.add_argument("--date", type=str, required=True, help="Run single date, e.g. 2026-04-05")
    parser.add_argument("--print-summary", action="store_true", help="Print loaded config summary")
    parser.add_argument("--debug-index", type=str, default=None, help="Print final result for one index id")
    parser.add_argument("--dump-json", action="store_true", help="Print full daily runtime json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    project_root = Path(__file__).resolve().parent
    dsl_dir = project_root / "dsl"
    raw_dir = project_root / "data" / "raw"
    registry_path = project_root / "config" / "index_registry.yaml"

    registry = load_registry(registry_path)
    dsl = load_all_dsl(dsl_dir)

    try:
        validate_all_dsl(dsl, registry)
    except ConfigValidationError as e:
        raise SystemExit(f"Configuration validation failed: {e}") from e

    data = load_all_data(raw_dir, registry)

    if args.print_summary:
        summary = {
            "indices": list(registry["indices"].keys()),
            "date": args.date,
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
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    # 1. build index runtimes
    indices = {}
    for index_id, df in data.items():
        current_runtime = compute_index_features(
            index_id=index_id,
            date=args.date,
            df=df,
            features_dsl=dsl["features"],
        )

        prev_dates = df[df["date"] < args.date]["date"]
        prev_runtime = None
        if not prev_dates.empty:
            prev_date = prev_dates.iloc[-1]
            prev_runtime = compute_index_features(
                index_id=index_id,
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
        current_runtime = detect_index_patterns(
            runtime=current_runtime,
            patterns_dsl=dsl["patterns"],
            prev_runtime=prev_runtime,
        )
        current_runtime = detect_index_transitions(
            runtime=current_runtime,
            transitions_dsl=dsl["transitions"],
            prev_runtime=prev_runtime,
        )
        current_runtime = score_index_salience(
            runtime=current_runtime,
            salience_dsl=dsl["salience"],
            prev_runtime=prev_runtime,
        )

        indices[index_id] = current_runtime

    # 2. build market salience
    market = build_market_salience(
        date=args.date,
        indices=indices,
    )

    # 3. build pair runtimes
    pairs = {}
    for pair_def in dsl["pairs"]["pairs"]:
        pair_runtime = create_pair_runtime(pair_def, args.date)
        pair_runtime = compute_pair_features(
            runtime=pair_runtime,
            pair_features_dsl=dsl["pair_features"],
            indices=indices,
        )
        pair_runtime = derive_pair_states(
            runtime=pair_runtime,
            pair_states_dsl=dsl["pair_states"],
            indices=indices,
        )
        pair_runtime = detect_pair_relation_tags(
            runtime=pair_runtime,
            relation_tags_dsl=dsl["relation_tags"],
            indices=indices,
        )
        pairs[pair_runtime.id] = pair_runtime

    # 4. market relation tags + regime
    market = collect_market_relation_tags(market=market, pairs=pairs)
    market = score_market_regime(
        market=market,
        indices=indices,
        pairs=pairs,
        regimes_dsl=dsl["regimes"],
    )

    # 5. outputs
    result = {
        "date": args.date,
        "indices": {k: v.to_dict() for k, v in indices.items()},
        "pairs": {k: v.to_dict() for k, v in pairs.items()},
        "market": market.to_dict(),
    }

    if args.debug_index:
        if args.debug_index not in indices:
            raise SystemExit(f"Unknown index id: {args.debug_index}")
        print(json.dumps(indices[args.debug_index].to_dict(), ensure_ascii=False, indent=2))
        return

    if args.dump_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(json.dumps({
        "date": args.date,
        "market_regime": market.market_regime.to_dict(),
        "top_positive": market.top_positive[:3],
        "top_negative": market.top_negative[:3],
        "top_warning": market.top_warning[:3],
        "relation_tags": market.relation_tags,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

---

# 6. 现在怎么测试

先跑整条链：

```bash
python run_daily.py --date 2026-04-05 --dump-json
```

看完整 JSON。

再看单指数：

```bash
python run_daily.py --date 2026-04-05 --debug-index hs300
python run_daily.py --date 2026-04-05 --debug-index cyb
python run_daily.py --date 2026-04-05 --debug-index csi1000
```

再看摘要：

```bash
python run_daily.py --date 2026-04-05
```

---

# 7. 这轮完成后的验收标准

满足下面这些，就说明第一版闭环已经成立：

## 单指数层

每个指数都有：

* `features`
* `states`
* `pattern_tags`
* `transition_tags`
* `salience`

## pair 层

每个 pair 都有：

* `features`
* `states`
* `relation_tags`

## market 层

有：

* `top_positive`
* `top_negative`
* `top_warning`
* `relation_tags`
* `market_regime`

## trace

每层都有规则命中痕迹：

* `trace.states`
* `trace.patterns`
* `trace.transitions`
* `trace.salience`
* `trace.regimes`

---

# 8. 这版之后最该补的东西

接下来最值钱的不是继续扩规则，而是补这 4 项：

## 8.1 输出落盘

新增：

* `outputs/json/YYYY-MM-DD.json`
* `outputs/markdown/YYYY-MM-DD.md`

## 8.2 区间回放

支持：

```bash
python run_daily.py --start 2026-01-01 --end 2026-04-05
```

## 8.3 explain 模式

不仅看单指数，还能看：

* pair
* regime rule 命中详情

## 8.4 Markdown 模板渲染

先不用 LLM，固定模板生成日报

---

# 9. 下一轮最合理的继续方向

我建议下一轮直接做：

* `engine/pipeline.py`
* `engine/output_writer.py` 或直接写在 `pipeline.py`
* 区间回放
* JSON/Markdown 文件输出

这样你这个系统就从“命令行调试器”变成“能稳定每日产出结果的工具”。
