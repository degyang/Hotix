import pytest

from hotix.engine.models import IndexRuntime, SalienceItem
from hotix.engine.salience_engine import (
    build_cross_section_salience,
    score_index_salience,
)


def test_score_index_salience_accumulates_bucket_scores(
    index_runtime_with_tags, dsl_bundle
):
    runtime = score_index_salience(index_runtime_with_tags, dsl_bundle["salience"])
    assert runtime.salience["total_score"] == 6.3
    assert runtime.salience["positive_score"] == 4.1
    assert runtime.salience["transition_score"] == 2.2
    assert len(runtime.salience["matched_rules"]) == 3


def test_score_index_salience_emits_structured_items(
    index_runtime_with_tags, dsl_bundle
):
    runtime = score_index_salience(index_runtime_with_tags, dsl_bundle["salience"])

    items = runtime.salience["items"]
    assert len(items) == 3
    assert items[0]["rule_id"] == "s_pattern_low_repair"
    assert items[0]["asset_id"] == "000300"
    assert items[0]["scope"] == "asset"
    assert items[0]["dimension"] == "price"
    assert items[0]["category"] == "pattern"
    assert items[0]["polarity"] == "positive"
    assert items[0]["severity"] == "medium"
    assert items[0]["confidence"] == pytest.approx(0.70)
    assert items[0]["evidence"]["ret_1d"] == pytest.approx(0.02)
    assert "中继" not in items[0]["reason"]
    assert runtime.trace["salience"][0]["item_id"] == items[0]["id"]


def test_salience_item_to_dict_keeps_output_contract():
    item = SalienceItem(
        id="item-1",
        rule_id="rule-1",
        date="2026-04-05",
        scope="asset",
        asset_id="000300",
        dimension="price",
        category="pattern",
        polarity="positive",
        score=2.1,
        severity="medium",
        confidence=0.7,
        freshness="current",
        reason="低位放量修复",
        evidence={"ret_1d": 0.02},
        tags=["repair"],
    )

    assert item.to_dict() == {
        "id": "item-1",
        "rule_id": "rule-1",
        "date": "2026-04-05",
        "scope": "asset",
        "asset_id": "000300",
        "universe_id": None,
        "dimension": "price",
        "category": "pattern",
        "polarity": "positive",
        "score": 2.1,
        "severity": "medium",
        "confidence": 0.7,
        "freshness": "current",
        "reason": "低位放量修复",
        "evidence": {"ret_1d": 0.02},
        "tags": ["repair"],
        "rank": None,
        "metric": None,
        "direction": None,
    }


def test_build_cross_section_salience_ranks_positive_and_negative_topn():
    runtimes = {
        "000300": IndexRuntime(
            id="000300",
            date="2026-04-05",
            features={"ret_1d": 0.03, "amount_ratio_1_20": 1.4},
        ),
        "000852": IndexRuntime(
            id="000852",
            date="2026-04-05",
            features={"ret_1d": -0.02, "amount_ratio_1_20": 0.7},
        ),
        "399006": IndexRuntime(
            id="399006",
            date="2026-04-05",
            features={"ret_1d": 0.01, "amount_ratio_1_20": 2.1},
        ),
    }
    metric_specs = [
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
    ]

    result = build_cross_section_salience(runtimes, metric_specs, top_n=2)

    assert [item["asset_id"] for item in result["price"]["ret_1d"]["top_gain"]] == [
        "000300",
        "399006",
    ]
    assert [item["asset_id"] for item in result["price"]["ret_1d"]["top_decline"]] == [
        "000852",
        "399006",
    ]
    assert result["price"]["ret_1d"]["top_gain"][0]["rank"] == 1
    assert result["price"]["ret_1d"]["top_gain"][0]["score"] == pytest.approx(0.03)
    assert result["price"]["ret_1d"]["top_decline"][0]["polarity"] == "negative"
    assert (
        result["volume"]["amount_ratio_1_20"]["top_expansion"][0]["asset_id"]
        == "399006"
    )
