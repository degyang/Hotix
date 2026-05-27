from hotix.engine.context_engine import score_market_context


def test_score_market_context_selects_cash_with_evidence(
    dsl_bundle, market_runtime_ready, ready_indices, ready_pairs
):
    market_runtime_ready.market_regime = {
        "label": "混沌市",
        "score": 2.0,
        "confidence": 0.6,
        "evidence": ["未形成明确结构主线"],
    }
    market_runtime_ready.top_positive = []
    market_runtime_ready.top_negative = []
    market_runtime_ready.top_warning = [
        {"asset": "000300", "score": 2.8, "reasons": ["高位放量分歧"]}
    ]

    result = score_market_context(
        market_runtime_ready, ready_indices, ready_pairs, dsl_bundle["contexts"]
    )

    assert result["label"] == "Cash"
    assert result["score"] > 0
    assert "观察" in result["allowed_styles"]
    assert result["risk_budget"]["total_exposure"] == 0.10
    assert result["evidence"]
