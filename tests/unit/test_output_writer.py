from hotix.engine.output_writer import render_markdown


def test_render_markdown_includes_market_sections():
    payload = {
        "date": "2026-04-05",
        "indices": {
            "000300": {
                "states": {
                    "trend_state": "up",
                    "position_state": "mid",
                    "volume_state": "expansion",
                    "breadth_state": "neutral_strong",
                    "volatility_state": "medium",
                },
                "pattern_tags": ["中继放量突破"],
                "transition_tags": ["趋势转上"],
            }
        },
        "market": {
            "market_regime": {
                "label": "成长进攻市",
                "score": 3.0,
                "confidence": 0.6,
                "evidence": ["成长风格占优"],
            },
            "market_context": {
                "label": "Offense",
                "score": 5.0,
                "confidence": 0.7,
                "allowed_styles": ["趋势跟随"],
                "disallowed_styles": ["逆势抄底"],
                "risk_budget": {
                    "total_exposure": 0.8,
                    "max_positions": 6,
                    "max_single_name_weight": 0.2,
                },
                "evidence": ["市场处于成长进攻市"],
            },
            "relation_tags": ["成长风格占优"],
            "top_positive": [
                {"asset": "399006", "score": 2.6, "reasons": ["中继放量突破"]}
            ],
            "top_negative": [],
            "top_warning": [],
            "top_transition": [
                {"asset": "399006", "score": 2.2, "reasons": ["趋势转上"]}
            ],
        },
    }
    markdown = render_markdown(payload)
    assert "## 市场上下文" in markdown
    assert "Offense" in markdown
    assert "## 今日最亮信号" in markdown
    assert "## 今日切换" in markdown
    assert "## 指数状态概览" in markdown
