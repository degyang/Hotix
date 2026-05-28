import math
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from hotix.engine.context_engine import score_market_context
from hotix.engine.feature_engine import compute_index_features
from hotix.engine.loader import load_all_data, load_all_dsl, load_registry
from hotix.engine.market_profile_engine import build_market_profile
from hotix.engine.models import MarketRuntime
from hotix.engine.output_writer import (
    render_markdown,
    write_json_output,
    write_markdown_output,
)
from hotix.engine.pair_engine import (
    compute_pair_features,
    create_pair_runtime,
    derive_pair_states,
    detect_pair_relation_tags,
)
from hotix.engine.policy_engine import score_policy
from hotix.engine.regime_engine import collect_market_relation_tags, score_market_regime
from hotix.engine.report_templates import normalize_universe_type
from hotix.engine.salience_engine import build_market_salience, score_index_salience
from hotix.engine.state_engine import derive_index_states
from hotix.engine.tag_engine import detect_index_patterns, detect_index_transitions
from hotix.engine.universe_engine import build_all_universe_profiles
from hotix.engine.validator import validate_all_dsl


@dataclass
class PipelineContext:
    root: Path
    registry: dict
    dsl: dict
    data: dict


def _available_dates(ctx: PipelineContext) -> list[str]:
    return sorted(
        set.intersection(*[set(df["date"].tolist()) for df in ctx.data.values()])
    )


def latest_available_date(ctx: PipelineContext) -> str:
    common_dates = _available_dates(ctx)
    if not common_dates:
        raise ValueError("No common market dates available")
    return common_dates[-1]


def _normalize(value):
    if isinstance(value, dict):
        return {key: _normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _output_root(ctx: PipelineContext) -> Path:
    if ctx.root.name == "hotix" and ctx.root.parent.name == "src":
        return ctx.root.parent.parent
    return ctx.root


def build_context(
    root: str | Path,
    data_dir: str | Path | None = None,
    universe_type: str = "index",
) -> PipelineContext:
    root = Path(root).resolve()
    if data_dir is None:
        raise ValueError("Provide --data-dir or an explicit data_dir path.")
    resolved_data_dir = Path(data_dir).expanduser().resolve()
    universe_type = normalize_universe_type(universe_type)
    registry = _build_registry(root, resolved_data_dir, universe_type)
    dsl = _build_dsl(root, registry, universe_type)
    validate_all_dsl(dsl, registry)
    data = load_all_data(resolved_data_dir, registry)
    return PipelineContext(root=root, registry=registry, dsl=dsl, data=data)


def _build_registry(root: Path, data_dir: Path, universe_type: str) -> dict:
    if universe_type == "index":
        return load_registry(root / "config" / "index_registry.yaml")
    return {
        "indices": {
            path.stem: {"name": path.stem, "symbol": path.stem, "role": universe_type}
            for path in sorted(data_dir.glob("*.csv"))
        }
    }


def _build_dsl(root: Path, registry: dict, universe_type: str) -> dict:
    dsl = deepcopy(load_all_dsl(root / "dsl"))
    if universe_type == "index":
        return dsl

    members = sorted(registry["indices"])
    dsl["universes"] = {
        "version": "0.1",
        "dsl_type": "universes",
        "universes": [
            {
                "id": f"{universe_type}_universe",
                "name": _default_universe_name(universe_type),
                "type": universe_type,
                "role": f"{universe_type}_structure",
                "members": members,
            }
        ],
    }
    dsl["pairs"] = {"version": "0.1", "dsl_type": "pairs", "pairs": []}
    dsl["regimes"] = {"version": "0.1", "dsl_type": "regimes", "regimes": []}
    return dsl


def _default_universe_name(universe_type: str) -> str:
    names = {
        "etf": "ETF观察池",
        "stock": "个股观察池",
        "sector": "行业指数观察池",
        "mixed": "样本观察池",
    }
    return names.get(universe_type, "样本观察池")


def run_single_date(ctx: PipelineContext, date: str) -> dict:
    common_dates = _available_dates(ctx)
    if date not in common_dates:
        raise ValueError(f"No market data available for date {date}")

    indices = {}
    for index_id, df in ctx.data.items():
        current = compute_index_features(index_id, date, df, ctx.dsl["features"])
        prev_dates = df[df["date"] < date]["date"]
        prev_runtime = None
        if not prev_dates.empty:
            prev_runtime = compute_index_features(
                index_id, prev_dates.iloc[-1], df, ctx.dsl["features"]
            )
            prev_runtime = derive_index_states(prev_runtime, ctx.dsl["states"])
        current = derive_index_states(current, ctx.dsl["states"], prev_runtime)
        current = detect_index_patterns(current, ctx.dsl["patterns"], prev_runtime)
        current = detect_index_transitions(
            current, ctx.dsl["transitions"], prev_runtime
        )
        current = score_index_salience(current, ctx.dsl["salience"], prev_runtime)
        indices[index_id] = current

    universes = build_all_universe_profiles(ctx.dsl["universes"], indices)

    pairs = {}
    for pair_def in ctx.dsl["pairs"]["pairs"]:
        if pair_def["left"] not in indices or pair_def["right"] not in indices:
            continue
        pair_runtime = create_pair_runtime(pair_def, date)
        pair_runtime = compute_pair_features(
            pair_runtime, ctx.dsl["pair_features"], indices
        )
        pair_runtime = derive_pair_states(pair_runtime, ctx.dsl["pair_states"], indices)
        pair_runtime = detect_pair_relation_tags(
            pair_runtime, ctx.dsl["relation_tags"], indices
        )
        pairs[pair_runtime.id] = pair_runtime

    market = MarketRuntime(date=date)
    for key, value in build_market_salience(indices).items():
        setattr(market, key, value)
    market = collect_market_relation_tags(market, pairs)
    market = score_market_regime(market, indices, pairs, ctx.dsl["regimes"])
    market.market_context = score_market_context(
        market, indices, pairs, ctx.dsl["contexts"]
    )
    market.policy = score_policy(market, indices, pairs, ctx.dsl["policies"])
    market_profile = build_market_profile(date, universes)

    payload = {
        "date": date,
        "indices": {key: value.__dict__ for key, value in indices.items()},
        "universes": universes,
        "pairs": {key: value.__dict__ for key, value in pairs.items()},
        "market": {
            "date": market.date,
            "relation_tags": market.relation_tags,
            "top_positive": market.top_positive,
            "top_negative": market.top_negative,
            "top_warning": market.top_warning,
            "top_transition": market.top_transition,
            "market_regime": market.market_regime,
            "market_context": market.market_context,
            "market_profile": market_profile,
            "policy": market.policy,
            "trace": market.trace,
        },
    }
    return _normalize(payload)


def run_date_range(
    ctx: PipelineContext,
    start: str | None = None,
    end: str | None = None,
    write_files: bool = False,
) -> list[dict]:
    common_dates = _available_dates(ctx)
    selected_dates = [
        date
        for date in common_dates
        if (start is None or date >= start) and (end is None or date <= end)
    ]
    results = []
    for date in selected_dates:
        payload = run_single_date(ctx, date)
        results.append(payload)
        if write_files:
            output_root = _output_root(ctx)
            write_json_output(output_root / "outputs" / "json", date, payload)
            write_markdown_output(
                output_root / "outputs" / "markdown", date, render_markdown(payload)
            )
    return results
