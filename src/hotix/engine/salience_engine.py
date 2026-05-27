import math

from hotix.engine.expression import evaluate_expression
from hotix.engine.models import SalienceItem
from hotix.engine.resolver import Resolver

DEFAULT_CROSS_SECTION_METRIC_SPECS = [
    {
        "dimension": "price",
        "metric": "ret_1d",
        "positive_label": "top_gain",
        "negative_label": "top_decline",
    },
    {
        "dimension": "volume",
        "metric": "amount_ratio_1_20",
        "positive_label": "top_expansion",
        "negative_label": "top_contraction",
    },
    {
        "dimension": "volatility",
        "metric": "volatility_percentile_250d",
        "positive_label": "top_high_volatility",
        "negative_label": "top_low_volatility",
    },
    {
        "dimension": "breadth",
        "metric": "breadth_ratio",
        "positive_label": "top_breadth",
        "negative_label": "bottom_breadth",
    },
    {
        "dimension": "position",
        "metric": "price_percentile_120d",
        "positive_label": "top_high_position",
        "negative_label": "top_low_position",
    },
]


def build_market_salience(indices: dict):
    def collect(bucket: str):
        items = []
        score_key = f"{bucket}_score"
        for index_id, runtime in indices.items():
            score = runtime.salience.get(score_key, 0.0)
            if score > 0:
                items.append(
                    {
                        "asset": index_id,
                        "score": score,
                        "reasons": [
                            rule["reason"]
                            for rule in runtime.salience["matched_rules"]
                            if rule["bucket"] == bucket
                        ],
                    }
                )
        return sorted(items, key=lambda item: item["score"], reverse=True)

    return {
        "top_positive": collect("positive"),
        "top_negative": collect("negative"),
        "top_warning": collect("warning"),
        "top_transition": collect("transition"),
    }


def score_index_salience(runtime, salience_dsl: dict, prev_runtime=None):
    resolver = Resolver(current=runtime, prev=prev_runtime)
    result = {
        "total_score": 0.0,
        "positive_score": 0.0,
        "negative_score": 0.0,
        "warning_score": 0.0,
        "transition_score": 0.0,
        "matched_rules": [],
        "items": [],
    }

    for rule in salience_dsl["salience"]["scoring_rules"]:
        if evaluate_expression(rule["when"], resolver):
            score = float(rule["score"])
            result["total_score"] += score
            bucket_key = f"{rule['bucket']}_score"
            if bucket_key in result:
                result[bucket_key] += score
            item = _build_rule_salience_item(runtime, rule, score)
            item_dict = item.to_dict()
            result["items"].append(item_dict)
            result["matched_rules"].append(
                {
                    "rule_id": rule["id"],
                    "item_id": item.id,
                    "score": score,
                    "bucket": rule["bucket"],
                    "polarity": rule["polarity"],
                    "dimension": item.dimension,
                    "category": item.category,
                    "reason": rule["reason"],
                }
            )

    runtime.salience = result
    runtime.trace.setdefault("salience", result["matched_rules"])
    return runtime


def _build_rule_salience_item(runtime, rule: dict, score: float) -> SalienceItem:
    evidence = {}
    for field_name in rule.get("evidence_fields", []):
        try:
            evidence[field_name] = runtime.get_field(field_name)
        except KeyError:
            continue

    return SalienceItem(
        id=f"{runtime.id}:{runtime.date}:{rule['id']}",
        rule_id=rule["id"],
        date=runtime.date,
        scope=rule.get("scope", "asset"),
        asset_id=runtime.id,
        dimension=rule["dimension"],
        category=rule["category"],
        polarity=rule["polarity"],
        score=score,
        severity=rule.get("severity", "medium"),
        confidence=float(rule.get("confidence", 0.7)),
        freshness=rule.get("freshness", "current"),
        reason=rule["reason"],
        evidence=evidence,
        tags=list(rule.get("tags", [])),
    )


def build_cross_section_salience(
    runtimes: dict,
    metric_specs: list[dict] | None = None,
    top_n: int = 3,
) -> dict:
    specs = metric_specs or DEFAULT_CROSS_SECTION_METRIC_SPECS
    result = {}

    for spec in specs:
        dimension = spec["dimension"]
        metric = spec["metric"]
        rows = _collect_metric_rows(runtimes, metric)
        if not rows:
            continue

        positive_label = spec.get("positive_label", "top_positive")
        negative_label = spec.get("negative_label", "top_negative")
        dimension_bucket = result.setdefault(dimension, {})
        dimension_bucket[metric] = {
            positive_label: _rank_cross_section_items(
                rows=sorted(rows, key=lambda row: row["value"], reverse=True)[:top_n],
                spec=spec,
                label=positive_label,
                polarity="positive",
                direction="positive",
            ),
            negative_label: _rank_cross_section_items(
                rows=sorted(rows, key=lambda row: row["value"])[:top_n],
                spec=spec,
                label=negative_label,
                polarity="negative",
                direction="negative",
            ),
        }

    return result


def _collect_metric_rows(runtimes: dict, metric: str) -> list[dict]:
    rows = []
    for asset_id, runtime in runtimes.items():
        try:
            value = runtime.get_field(metric)
        except KeyError:
            continue
        if value is None:
            continue
        if isinstance(value, float) and math.isnan(value):
            continue
        rows.append(
            {
                "asset_id": asset_id,
                "date": runtime.date,
                "value": float(value),
            }
        )
    return rows


def _rank_cross_section_items(
    rows: list[dict], spec: dict, label: str, polarity: str, direction: str
) -> list[dict]:
    items = []
    for rank, row in enumerate(rows, start=1):
        item = SalienceItem(
            id=f"{row['date']}:{spec['dimension']}:{spec['metric']}:{label}:{row['asset_id']}",
            rule_id=None,
            date=row["date"],
            scope=spec.get("scope", "cross_section"),
            asset_id=row["asset_id"],
            dimension=spec["dimension"],
            category=spec.get("category", "cross_section_topn"),
            polarity=polarity,
            score=row["value"],
            severity=spec.get("severity", "medium"),
            confidence=float(spec.get("confidence", 1.0)),
            freshness=spec.get("freshness", "current"),
            reason=f"{spec['metric']} {label} rank {rank}",
            evidence={spec["metric"]: row["value"]},
            tags=list(spec.get("tags", [])),
            universe_id=spec.get("universe_id"),
            rank=rank,
            metric=spec["metric"],
            direction=direction,
        )
        items.append(item.to_dict())
    return items
