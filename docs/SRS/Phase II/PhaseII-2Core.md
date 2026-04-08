下面直接落地第二阶段最核心的部分：

1. `dsl/contexts.yaml`
2. `engine/context_engine.py`
3. 修改 `engine/output_writer.py`
4. 修改 `engine/pipeline.py`
5. 修改 `run_daily.py`
6. 第二阶段这一轮的验收方法

这一轮完成后，你就会在第一阶段结果之上，多出一个**可执行的市场上下文层**：

* `Offense`
* `Caution`
* `Defense`
* `Cash`

并且会输出：

* `allowed_styles`
* `disallowed_styles`
* `risk_budget`
* `evidence`

---

# 1. 新增 `dsl/contexts.yaml`

先做第一版，规则不要太多，先稳。

```yaml
version: "0.1"
dsl_type: contexts

contexts:
  - id: offense
    label: Offense
    rules:
      - id: ctx_off_01
        when: "market.market_regime.label == '成长进攻市'"
        score: 3
        evidence: 市场处于成长进攻市

      - id: ctx_off_02
        when: "len(market.top_positive) > 0"
        score: 1
        evidence: 存在显著正向信号

      - id: ctx_off_03
        when: "'成长风格占优' in market.relation_tags"
        score: 2
        evidence: 成长风格占优

      - id: ctx_off_04
        when: "len(market.top_negative) == 0"
        score: 1
        evidence: 负向显著信号较弱

    allowed_styles:
      - 趋势跟随
      - 高弹性进攻
      - 强势主线试错

    disallowed_styles:
      - 逆势抄底
      - 弱势股博弈

    risk_budget:
      total_exposure: 0.80
      max_positions: 6
      max_single_name_weight: 0.20

  - id: caution
    label: Caution
    rules:
      - id: ctx_cau_01
        when: "market.market_regime.label == '结构分裂市'"
        score: 2
        evidence: 市场处于结构分裂市

      - id: ctx_cau_02
        when: "len(market.top_positive) > 0 and len(market.top_warning) > 0"
        score: 2
        evidence: 正向信号与预警信号并存

      - id: ctx_cau_03
        when: "'成长风格占优' in market.relation_tags or '权重大盘主导' in market.relation_tags"
        score: 1
        evidence: 存在单边结构主导，但不够全面

    allowed_styles:
      - 低频趋势跟随
      - 只做最强方向
      - 轻仓试错

    disallowed_styles:
      - 高频乱试
      - 全面铺仓

    risk_budget:
      total_exposure: 0.50
      max_positions: 4
      max_single_name_weight: 0.15

  - id: defense
    label: Defense
    rules:
      - id: ctx_def_01
        when: "market.market_regime.label == '权重防守市'"
        score: 3
        evidence: 市场处于权重防守市

      - id: ctx_def_02
        when: "len(market.top_negative) > 0"
        score: 2
        evidence: 存在显著负向信号

      - id: ctx_def_03
        when: "'权重大盘主导' in market.relation_tags"
        score: 1
        evidence: 权重大盘主导，小票弹性不足

      - id: ctx_def_04
        when: "len(market.top_warning) > 0"
        score: 1
        evidence: 存在结构预警

    allowed_styles:
      - 防守
      - 低频
      - 核心资产轻仓参与

    disallowed_styles:
      - 高弹性追涨
      - 高频试错
      - 弱转强博弈

    risk_budget:
      total_exposure: 0.30
      max_positions: 3
      max_single_name_weight: 0.10

  - id: cash
    label: Cash
    rules:
      - id: ctx_cash_01
        when: "market.market_regime.label == '混沌市'"
        score: 3
        evidence: 市场处于混沌市

      - id: ctx_cash_02
        when: "len(market.top_warning) > 0 and len(market.top_positive) == 0"
        score: 2
        evidence: 预警存在且缺乏明确正向信号

      - id: ctx_cash_03
        when: "len(market.relation_tags) == 0"
        score: 2
        evidence: 缺乏明确结构主线

    allowed_styles:
      - 观察
      - 复盘
      - 等待

    disallowed_styles:
      - 主动进攻
      - 高频试错
      - 重仓出击

    risk_budget:
      total_exposure: 0.10
      max_positions: 1
      max_single_name_weight: 0.05
```

---

# 2. 新增 `engine/context_engine.py`

```python
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from engine.expression import evaluate_expression, ExpressionError
from engine.models import IndexRuntime, PairRuntime, MarketRuntime
from engine.resolver import Resolver


class ContextEngineError(Exception):
    """Raised when context scoring fails."""


@dataclass
class MarketContextResult:
    label: str = ""
    score: float = 0.0
    confidence: float = 0.0
    allowed_styles: List[str] = None
    disallowed_styles: List[str] = None
    risk_budget: Dict[str, Any] = None
    evidence: List[str] = None
    runner_up: str = ""
    runner_up_score: float = 0.0

    def __post_init__(self) -> None:
        if self.allowed_styles is None:
            self.allowed_styles = []
        if self.disallowed_styles is None:
            self.disallowed_styles = []
        if self.risk_budget is None:
            self.risk_budget = {}
        if self.evidence is None:
            self.evidence = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def score_market_context(
    market: MarketRuntime,
    indices: Dict[str, IndexRuntime],
    pairs: Dict[str, PairRuntime],
    contexts_dsl: Dict[str, Any],
) -> Dict[str, Any]:
    context_scores: Dict[str, float] = {}
    context_evidence: Dict[str, List[str]] = {}
    context_meta: Dict[str, Dict[str, Any]] = {}
    context_trace: Dict[str, Any] = {}

    resolver = Resolver(
        current=market,
        indices=indices,
        pairs=pairs,
        market=market,
    )

    for context_def in contexts_dsl["contexts"]:
        context_id = context_def["id"]
        label = context_def["label"]
        total_score = 0.0
        evidence: List[str] = []
        matched_rules: List[Dict[str, Any]] = []

        for rule in context_def["rules"]:
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
                raise ContextEngineError(
                    f"Failed scoring context '{context_id}' on date={market.date}: {e}"
                ) from e

        context_scores[context_id] = total_score
        context_evidence[context_id] = evidence
        context_meta[context_id] = {
            "label": label,
            "allowed_styles": context_def.get("allowed_styles", []),
            "disallowed_styles": context_def.get("disallowed_styles", []),
            "risk_budget": context_def.get("risk_budget", {}),
        }
        context_trace[context_id] = {
            "label": label,
            "score": total_score,
            "matched_rules": matched_rules,
        }

    if "contexts" not in market.trace:
        market.trace["contexts"] = {}
    market.trace["contexts"] = context_trace

    if not context_scores:
        result = MarketContextResult()
        return result.to_dict()

    sorted_contexts = sorted(context_scores.items(), key=lambda x: x[1], reverse=True)
    top_id, top_score = sorted_contexts[0]
    runner_up_id, runner_up_score = (sorted_contexts[1] if len(sorted_contexts) > 1 else ("", 0.0))

    total_all_scores = sum(context_scores.values())
    confidence = (top_score / total_all_scores) if total_all_scores > 0 else 0.0

    runner_up_label = context_meta[runner_up_id]["label"] if runner_up_id else ""

    result = MarketContextResult(
        label=context_meta[top_id]["label"],
        score=top_score,
        confidence=confidence,
        allowed_styles=context_meta[top_id]["allowed_styles"],
        disallowed_styles=context_meta[top_id]["disallowed_styles"],
        risk_budget=context_meta[top_id]["risk_budget"],
        evidence=context_evidence[top_id],
        runner_up=runner_up_label,
        runner_up_score=runner_up_score,
    )
    return result.to_dict()
```

---

# 3. 修改 `engine/output_writer.py`

在 `render_markdown()` 里加入 context 段落。
你直接替换成下面这个版本。

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class OutputWriterError(Exception):
    """Raised when writing outputs fails."""


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json_output(output_dir: str | Path, date: str, payload: Dict[str, Any]) -> Path:
    output_path = ensure_dir(output_dir) / f"{date}.json"
    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise OutputWriterError(f"Failed writing json output: {output_path}\nError: {e}") from e
    return output_path


def _render_bullets(items: List[Dict[str, Any]], fallback: str = "无") -> List[str]:
    if not items:
        return [fallback]

    lines: List[str] = []
    for item in items[:5]:
        asset = item.get("asset", "")
        score = item.get("score", 0)
        reasons = item.get("reasons", [])
        reason_text = "；".join(reasons) if reasons else "无"
        lines.append(f"- {asset}（score={score:.2f}）：{reason_text}")
    return lines


def render_markdown(payload: Dict[str, Any]) -> str:
    date = payload["date"]
    market = payload["market"]
    regime = market["market_regime"]
    context = market.get("market_context", {})

    lines: List[str] = []
    lines.append(f"# 市场结构日报 - {date}")
    lines.append("")

    lines.append("## 市场状态")
    lines.append(f"- Regime: {regime.get('label', '') or '未分类'}")
    lines.append(f"- Regime Score: {regime.get('score', 0):.2f}")
    lines.append(f"- Regime Confidence: {regime.get('confidence', 0):.2f}")
    if regime.get("runner_up"):
        lines.append(f"- Regime Runner-up: {regime['runner_up']} ({regime.get('runner_up_score', 0):.2f})")
    lines.append("")

    lines.append("## 市场上下文")
    lines.append(f"- Context: {context.get('label', '') or '未分类'}")
    lines.append(f"- Context Score: {context.get('score', 0):.2f}")
    lines.append(f"- Context Confidence: {context.get('confidence', 0):.2f}")
    if context.get("runner_up"):
        lines.append(f"- Context Runner-up: {context['runner_up']} ({context.get('runner_up_score', 0):.2f})")
    lines.append("")

    lines.append("## 交易约束")
    allowed = context.get("allowed_styles", [])
    disallowed = context.get("disallowed_styles", [])
    risk_budget = context.get("risk_budget", {})

    lines.append(f"- Allowed Styles: {', '.join(allowed) if allowed else '无'}")
    lines.append(f"- Disallowed Styles: {', '.join(disallowed) if disallowed else '无'}")
    if risk_budget:
        lines.append(
            "- Risk Budget: "
            f"total_exposure={risk_budget.get('total_exposure')}, "
            f"max_positions={risk_budget.get('max_positions')}, "
            f"max_single_name_weight={risk_budget.get('max_single_name_weight')}"
        )
    else:
        lines.append("- Risk Budget: 无")
    lines.append("")

    lines.append("## 今日最亮信号")
    lines.extend(_render_bullets(market.get("top_positive", [])))
    lines.append("")

    lines.append("## 今日最暗信号")
    lines.extend(_render_bullets(market.get("top_negative", [])))
    lines.append("")

    lines.append("## 今日预警")
    lines.extend(_render_bullets(market.get("top_warning", [])))
    lines.append("")

    lines.append("## 今日切换")
    lines.extend(_render_bullets(market.get("top_transition", [])))
    lines.append("")

    lines.append("## 结构关系")
    relation_tags = market.get("relation_tags", [])
    if relation_tags:
        for tag in relation_tags:
            lines.append(f"- {tag}")
    else:
        lines.append("- 无明确结构关系标签")
    lines.append("")

    lines.append("## Regime 证据")
    evidence = regime.get("evidence", [])
    if evidence:
        for item in evidence:
            lines.append(f"- {item}")
    else:
        lines.append("- 无")
    lines.append("")

    lines.append("## Context 证据")
    context_evidence = context.get("evidence", [])
    if context_evidence:
        for item in context_evidence:
            lines.append(f"- {item}")
    else:
        lines.append("- 无")
    lines.append("")

    lines.append("## 指数状态概览")
    for index_id, runtime in payload.get("indices", {}).items():
        states = runtime.get("states", {})
        pattern_tags = runtime.get("pattern_tags", [])
        transition_tags = runtime.get("transition_tags", [])
        lines.append(f"### {index_id}")
        lines.append(
            f"- trend={states.get('trend_state')}, "
            f"position={states.get('position_state')}, "
            f"volume={states.get('volume_state')}, "
            f"breadth={states.get('breadth_state')}, "
            f"volatility={states.get('volatility_state')}"
        )
        lines.append(f"- patterns: {', '.join(pattern_tags) if pattern_tags else '无'}")
        lines.append(f"- transitions: {', '.join(transition_tags) if transition_tags else '无'}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_markdown_output(output_dir: str | Path, date: str, markdown_text: str) -> Path:
    output_path = ensure_dir(output_dir) / f"{date}.md"
    try:
        with output_path.open("w", encoding="utf-8") as f:
            f.write(markdown_text)
    except Exception as e:
        raise OutputWriterError(f"Failed writing markdown output: {output_path}\nError: {e}") from e
    return output_path
```

---

# 4. 修改 `engine/pipeline.py`

把 context 接到 market 上。
你直接替换成下面版本。

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from engine.context_engine import score_market_context
from engine.feature_engine import compute_index_features
from engine.loader import load_all_data, load_all_dsl, load_registry
from engine.output_writer import render_markdown, write_json_output, write_markdown_output
from engine.pair_engine import create_pair_runtime, compute_pair_features, derive_pair_states
from engine.regime_engine import collect_market_relation_tags, score_market_regime
from engine.salience_engine import build_market_salience, score_index_salience
from engine.state_engine import derive_index_states
from engine.tag_engine import (
    detect_index_patterns,
    detect_index_transitions,
    detect_pair_relation_tags,
)
from engine.validator import validate_all_dsl


@dataclass
class PipelineContext:
    project_root: Path
    registry: Dict[str, Any]
    dsl: Dict[str, Any]
    data: Dict[str, pd.DataFrame]


class PipelineError(Exception):
    """Raised when pipeline execution fails."""


def build_context(project_root: str | Path) -> PipelineContext:
    root = Path(project_root)
    registry = load_registry(root / "config" / "index_registry.yaml")
    dsl = load_all_dsl(root / "dsl")
    validate_all_dsl(dsl, registry)
    data = load_all_data(root / "data" / "raw", registry)

    return PipelineContext(
        project_root=root,
        registry=registry,
        dsl=dsl,
        data=data,
    )


def _get_prev_date(df: pd.DataFrame, date: str) -> Optional[str]:
    prev_dates = df[df["date"] < date]["date"]
    if prev_dates.empty:
        return None
    return str(prev_dates.iloc[-1])


def _build_index_runtime_for_date(
    index_id: str,
    date: str,
    df: pd.DataFrame,
    dsl: Dict[str, Any],
):
    current_runtime = compute_index_features(
        index_id=index_id,
        date=date,
        df=df,
        features_dsl=dsl["features"],
    )

    prev_date = _get_prev_date(df, date)
    prev_runtime = None

    if prev_date is not None:
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

    return current_runtime


def run_single_date(ctx: PipelineContext, date: str) -> Dict[str, Any]:
    indices = {}

    for index_id, df in ctx.data.items():
        if date not in set(df["date"].tolist()):
            raise PipelineError(f"Date {date} not found in data for index {index_id}")

        indices[index_id] = _build_index_runtime_for_date(
            index_id=index_id,
            date=date,
            df=df,
            dsl=ctx.dsl,
        )

    market = build_market_salience(date=date, indices=indices)

    pairs = {}
    for pair_def in ctx.dsl["pairs"]["pairs"]:
        pair_runtime = create_pair_runtime(pair_def, date)
        pair_runtime = compute_pair_features(
            runtime=pair_runtime,
            pair_features_dsl=ctx.dsl["pair_features"],
            indices=indices,
        )
        pair_runtime = derive_pair_states(
            runtime=pair_runtime,
            pair_states_dsl=ctx.dsl["pair_states"],
            indices=indices,
        )
        pair_runtime = detect_pair_relation_tags(
            runtime=pair_runtime,
            relation_tags_dsl=ctx.dsl["relation_tags"],
            indices=indices,
        )
        pairs[pair_runtime.id] = pair_runtime

    market = collect_market_relation_tags(market=market, pairs=pairs)
    market = score_market_regime(
        market=market,
        indices=indices,
        pairs=pairs,
        regimes_dsl=ctx.dsl["regimes"],
    )

    market_context = score_market_context(
        market=market,
        indices=indices,
        pairs=pairs,
        contexts_dsl=ctx.dsl["contexts"],
    )

    market_payload = market.to_dict()
    market_payload["market_context"] = market_context

    payload = {
        "date": date,
        "indices": {k: v.to_dict() for k, v in indices.items()},
        "pairs": {k: v.to_dict() for k, v in pairs.items()},
        "market": market_payload,
    }
    return payload


def get_common_dates(ctx: PipelineContext) -> List[str]:
    date_sets = []
    for _, df in ctx.data.items():
        date_sets.append(set(df["date"].tolist()))

    if not date_sets:
        return []

    common = set.intersection(*date_sets)
    return sorted(common)


def filter_dates(all_dates: List[str], start: str | None, end: str | None) -> List[str]:
    result = all_dates
    if start:
        result = [d for d in result if d >= start]
    if end:
        result = [d for d in result if d <= end]
    return result


def run_date_range(
    ctx: PipelineContext,
    start: str | None = None,
    end: str | None = None,
    json_output_dir: str | Path | None = None,
    markdown_output_dir: str | Path | None = None,
) -> List[Dict[str, Any]]:
    all_dates = get_common_dates(ctx)
    selected_dates = filter_dates(all_dates, start, end)

    if not selected_dates:
        raise PipelineError("No common dates available in selected range.")

    results: List[Dict[str, Any]] = []

    for date in selected_dates:
        payload = run_single_date(ctx, date)
        results.append(payload)

        if json_output_dir:
            write_json_output(json_output_dir, date, payload)
        if markdown_output_dir:
            markdown_text = render_markdown(payload)
            write_markdown_output(markdown_output_dir, date, markdown_text)

    return results
```

---

# 5. 修改 `run_daily.py`

只是把摘要输出里加上 context。

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.pipeline import build_context, run_date_range, run_single_date, PipelineError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run market structure pipeline.")
    parser.add_argument("--date", type=str, default=None, help="Single date, e.g. 2026-04-05")
    parser.add_argument("--start", type=str, default=None, help="Start date")
    parser.add_argument("--end", type=str, default=None, help="End date")
    parser.add_argument("--print-summary", action="store_true", help="Print context summary")
    parser.add_argument("--debug-index", type=str, default=None, help="Print full single-index result for a date")
    parser.add_argument("--dump-json", action="store_true", help="Print full payload json")
    parser.add_argument("--write-files", action="store_true", help="Write json/markdown outputs")
    return parser.parse_args()


def print_context_summary(ctx) -> None:
    summary = {
        "indices": list(ctx.registry["indices"].keys()),
        "dsl_rule_counts": {
            "features": len(ctx.dsl["features"]["features"]),
            "states": len(ctx.dsl["states"]["states"]),
            "patterns": len(ctx.dsl["patterns"]["patterns"]),
            "transitions": len(ctx.dsl["transitions"]["transitions"]),
            "salience": len(ctx.dsl["salience"]["salience"]["scoring_rules"]),
            "pairs": len(ctx.dsl["pairs"]["pairs"]),
            "pair_features": len(ctx.dsl["pair_features"]["pair_features"]),
            "pair_states": len(ctx.dsl["pair_states"]["pair_states"]),
            "relation_tags": len(ctx.dsl["relation_tags"]["relation_tags"]),
            "regimes": len(ctx.dsl["regimes"]["regimes"]),
            "contexts": len(ctx.dsl["contexts"]["contexts"]),
        },
        "data_rows": {k: len(v) for k, v in ctx.data.items()},
        "date_range": {
            k: {"start": v["date"].min(), "end": v["date"].max()}
            for k, v in ctx.data.items()
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parent

    try:
        ctx = build_context(project_root)
    except Exception as e:
        raise SystemExit(f"Failed building pipeline context: {e}") from e

    if args.print_summary:
        print_context_summary(ctx)

    json_output_dir = project_root / "outputs" / "json"
    markdown_output_dir = project_root / "outputs" / "markdown"

    try:
        if args.date:
            payload = run_single_date(ctx, args.date)

            if args.write_files:
                from engine.output_writer import render_markdown, write_json_output, write_markdown_output
                write_json_output(json_output_dir, args.date, payload)
                write_markdown_output(markdown_output_dir, args.date, render_markdown(payload))

            if args.debug_index:
                indices = payload["indices"]
                if args.debug_index not in indices:
                    raise SystemExit(f"Unknown index id: {args.debug_index}")
                print(json.dumps(indices[args.debug_index], ensure_ascii=False, indent=2))
                return

            if args.dump_json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return

            print(json.dumps({
                "date": payload["date"],
                "market_regime": payload["market"]["market_regime"],
                "market_context": payload["market"]["market_context"],
                "top_positive": payload["market"]["top_positive"][:3],
                "top_negative": payload["market"]["top_negative"][:3],
                "top_warning": payload["market"]["top_warning"][:3],
                "top_transition": payload["market"]["top_transition"][:3],
                "relation_tags": payload["market"]["relation_tags"],
            }, ensure_ascii=False, indent=2))
            return

        if args.start or args.end:
            results = run_date_range(
                ctx,
                start=args.start,
                end=args.end,
                json_output_dir=json_output_dir if args.write_files else None,
                markdown_output_dir=markdown_output_dir if args.write_files else None,
            )
            print(json.dumps({
                "dates_processed": len(results),
                "start": results[0]["date"] if results else None,
                "end": results[-1]["date"] if results else None,
                "write_files": args.write_files,
            }, ensure_ascii=False, indent=2))
            return

        raise SystemExit("Provide either --date or --start/--end.")

    except PipelineError as e:
        raise SystemExit(f"Pipeline execution failed: {e}") from e


if __name__ == "__main__":
    main()
```

---

# 6. 现在怎么测试

先检查 summary：

```bash
python run_daily.py --print-summary --date 2026-04-05
```

你要看到：

* `contexts` 规则数量已经被识别

然后跑单日全量：

```bash
python run_daily.py --date 2026-04-05 --dump-json
```

检查 `payload["market"]` 下是否有：

```json
"market_context": {
  "label": "...",
  "score": ...,
  "confidence": ...,
  "allowed_styles": [...],
  "disallowed_styles": [...],
  "risk_budget": {...},
  "evidence": [...]
}
```

再跑写文件：

```bash
python run_daily.py --date 2026-04-05 --write-files
```

检查：

* `outputs/json/2026-04-05.json`
* `outputs/markdown/2026-04-05.md`

markdown 里应新增：

* 市场上下文
* 交易约束
* Context 证据

---

# 7. 这一轮的验收标准

这一轮完成后，至少满足这几条：

## JSON

`market` 下同时有：

* `market_regime`
* `market_context`

## context 内容

包含：

* label
* score
* confidence
* allowed_styles
* disallowed_styles
* risk_budget
* evidence

## markdown

新增三个段落：

* 市场上下文
* 交易约束
* Context 证据

## 命令行摘要

`python run_daily.py --date ...` 输出里包含 `market_context`

---

# 8. 下一轮该做什么

第二阶段下一步最应该做的不是再加更多 context 规则，而是：

1. **扩到 8 指数面板**
2. **加 validation engine**
3. **输出 regime/context 分布统计**
4. **准备 weekly reporting**

按落地顺序，最合适的下一轮是直接做：

* 扩 `index_registry.yaml`
* 扩 `pairs.yaml`
* 补齐 raw 数据
* 新增 `engine/validation_engine.py`

这样第二阶段就从“有 context”进入“可验证、可校准”。
