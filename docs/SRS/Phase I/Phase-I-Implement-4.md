下面直接继续，把系统从“命令行调试器”推进到“可每日产出结果的工具”。

这一轮补 3 个文件：
* `engine/pipeline.py`
* `engine/output_writer.py`
* 更新 `run_daily.py`

目标：
1. 支持**单日执行**
2. 支持**区间回放**
3. 自动输出：

   * `outputs/json/YYYY-MM-DD.json`
   * `outputs/markdown/YYYY-MM-DD.md`

这一轮完成后，你就已经有一个可实际跑批的第一版。

---

## 1. `engine/output_writer.py`

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

    lines: List[str] = []
    lines.append(f"# 市场结构日报 - {date}")
    lines.append("")
    lines.append("## 市场状态")
    lines.append(f"- Regime: {regime.get('label', '') or '未分类'}")
    lines.append(f"- Score: {regime.get('score', 0):.2f}")
    lines.append(f"- Confidence: {regime.get('confidence', 0):.2f}")
    if regime.get("runner_up"):
        lines.append(f"- Runner-up: {regime['runner_up']} ({regime.get('runner_up_score', 0):.2f})")
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

## 2. `engine/pipeline.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

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

    payload = {
        "date": date,
        "indices": {k: v.to_dict() for k, v in indices.items()},
        "pairs": {k: v.to_dict() for k, v in pairs.items()},
        "market": market.to_dict(),
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

## 3. 更新 `run_daily.py`

这版支持：

* 单日执行
* 区间执行
* 自动落盘
* 可选打印摘要 / 全量 JSON / 单日 debug

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

# 4. 现在怎么跑

## 单日摘要

```bash
python run_daily.py --date 2026-04-05
```

## 单日全量 JSON

```bash
python run_daily.py --date 2026-04-05 --dump-json
```

## 单日单指数调试

```bash
python run_daily.py --date 2026-04-05 --debug-index hs300
```

## 单日并写文件

```bash
python run_daily.py --date 2026-04-05 --write-files
```

会生成：

* `outputs/json/2026-04-05.json`
* `outputs/markdown/2026-04-05.md`

## 区间回放并写文件

```bash
python run_daily.py --start 2026-03-01 --end 2026-04-05 --write-files
```

---

# 5. 这一轮完成后的验收标准

你现在要检查这几件事：

### 输出文件

* `outputs/json/` 下按日期生成 json
* `outputs/markdown/` 下按日期生成 md

### 单日 payload

* 有 `indices`
* 有 `pairs`
* 有 `market`

### markdown

至少包含：

* 市场状态
* 今日最亮信号
* 今日最暗信号
* 今日预警
* 结构关系
* Regime 证据
* 指数状态概览

### 区间回放

* 能在一段时间内连续生成文件
* 没有中途因为某天缺一个 state 就整体崩掉

---

# 6. 下一步最值得补的，不是继续加规则，而是这 4 件事

## 6.1 explain 模式增强

现在 `--debug-index` 只能看单指数。
下一步要补：

* `--debug-pair hs300_vs_cyb`
* `--debug-market`

## 6.2 feature 依赖从“手写顺序”升级成“显式依赖检查”

现在默认你在 yaml 中写对顺序。
下一步可补：

* feature output 名重复校验
* feature input 是否已经存在校验

## 6.3 markdown 增强

加：

* pair 概览
* salience 分值摘要
* regime runner-up 对比

## 6.4 输出快照

每日把最小摘要再写一份：

* `outputs/json/summary_YYYY-MM-DD.json`

这样后面做 dashboard 更方便。

---

# 7. 我建议你下一轮直接继续补什么

最合适的是继续补：

* `engine/debug_report.py`
* `--debug-pair`
* `--debug-market`
* feature 输入依赖校验
* 更稳的输出落盘摘要

这样你就从“能跑”进入“能调、能查、能维护”。
