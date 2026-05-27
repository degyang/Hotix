from hotix.engine.models import MarketRuntime
from hotix.engine.regime_engine import collect_market_relation_tags, score_market_regime


def test_market_runtime_has_explicit_defaults():
    market = MarketRuntime(date="2026-04-05")

    assert market.date == "2026-04-05"
    assert market.relation_tags == []
    assert market.market_regime == {}
    assert market.market_context == {}
    assert market.policy == {}
    assert market.trace == {}


def test_score_market_regime_selects_label_with_evidence(
    market_runtime_ready, ready_indices, ready_pairs, dsl_bundle
):
    market = collect_market_relation_tags(market_runtime_ready, ready_pairs)
    market = score_market_regime(
        market, ready_indices, ready_pairs, dsl_bundle["regimes"]
    )
    assert market.market_regime["label"] == "权重防守市"
    assert "权重大盘主导" in market.market_regime["evidence"]
