from hotix.engine.market_profile_engine import build_market_profile


def test_build_market_profile_uses_dominant_negative_breadth():
    universes = {
        "broad_indices": {
            "id": "broad_indices",
            "name": "宽基指数",
            "salience": {
                "top_negative": [
                    {"dimension": "breadth", "score": 3.2, "reason": "广度极弱"}
                ],
                "top_warning": [],
                "top_divergence": [],
                "top_positive": [],
            },
            "summary": ["宽基指数内部广度偏弱。"],
        }
    }

    profile = build_market_profile("2026-05-27", universes)

    assert profile["primary_label"] == "breadth_weakness"
    assert "breadth" in profile["dominant_dimensions"]
    assert profile["key_points"]
    assert profile["condition"] == "market_following"


def test_build_market_profile_detects_healthy_expansion():
    universes = {
        "broad_indices": {
            "id": "broad_indices",
            "name": "宽基指数",
            "salience": {
                "top_negative": [],
                "top_warning": [],
                "top_divergence": [],
                "top_positive": [
                    {"dimension": "breadth", "score": 2.0, "reason": "广度极强"},
                    {"dimension": "price", "score": 2.1, "reason": "低位放量修复"},
                ],
            },
            "summary": ["宽基指数内部广度偏强。"],
        }
    }

    profile = build_market_profile("2026-05-27", universes)

    assert profile["primary_label"] == "healthy_expansion"
    assert profile["top_salience"]["positive"]


def test_build_market_profile_does_not_use_prediction_or_trading_terms():
    profile = build_market_profile("2026-05-27", {})
    text = " ".join(
        [
            profile["one_liner"],
            profile["primary_label"],
            " ".join(profile["key_points"]),
        ]
    )

    forbidden_terms = ["预计", "明天", "建议买入", "建议减仓", "目标仓位"]
    assert not any(term in text for term in forbidden_terms)
