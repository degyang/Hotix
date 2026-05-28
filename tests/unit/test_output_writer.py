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


def test_render_markdown_includes_market_profile_and_universe_sections():
    payload = {
        "date": "2026-05-27",
        "market": {
            "market_profile": {
                "one_liner": "当前市场画像：breadth_weakness。",
                "primary_label": "breadth_weakness",
                "dominant_dimensions": ["breadth"],
                "key_points": ["广度是当前主导负向维度。"],
                "top_salience": {"positive": [], "negative": [], "warning": []},
            },
            "market_regime": {"label": "", "score": 0, "confidence": 0, "evidence": []},
            "market_context": {},
            "policy": {},
            "relation_tags": [],
            "top_positive": [],
            "top_negative": [],
            "top_warning": [],
            "top_transition": [],
        },
        "universes": {
            "broad_indices": {
                "name": "宽基指数",
                "summary": ["宽基指数内部广度偏弱。"],
                "salience": {"top_positive": [], "top_negative": [], "top_warning": []},
            }
        },
        "indices": {},
    }

    text = render_markdown(payload)

    assert "## 一句话画像" in text
    assert "breadth_weakness" in text
    assert "## 今日主导维度" in text
    assert "## 关键结论" in text
    assert "## Universe 分析" in text
    assert "主要指数观察池" in text


def test_render_markdown_uses_professional_report_sections_and_index_names():
    payload = {
        "date": "2026-05-27",
        "indices": {
            "000001": {
                "raw": {"adv": 120, "decl": 380},
                "features": {
                    "ret_1d": -0.0123,
                    "amount_ratio_1_20": 1.12,
                    "volatility_percentile_250d": 0.91,
                    "breadth_ratio": 0.24,
                    "price_percentile_120d": 0.63,
                },
                "states": {
                    "trend_state": "transitional_down",
                    "position_state": "mid",
                    "volume_state": "normal",
                    "breadth_state": "weak",
                    "volatility_state": "extreme",
                },
                "pattern_tags": [],
                "transition_tags": [],
            },
            "399006": {
                "raw": {"adv": 80, "decl": 420},
                "features": {
                    "ret_1d": 0.0188,
                    "amount_ratio_1_20": 1.46,
                    "volatility_percentile_250d": 0.78,
                    "breadth_ratio": 0.16,
                    "price_percentile_120d": 0.88,
                },
                "states": {
                    "trend_state": "up",
                    "position_state": "high",
                    "volume_state": "normal",
                    "breadth_state": "weak",
                    "volatility_state": "high",
                },
                "pattern_tags": ["指数上行但跟随不足"],
                "transition_tags": [],
            },
        },
        "universes": {
            "broad_indices": {
                "name": "主要指数观察池",
                "members": ["000001", "399006"],
                "summary": ["主要指数观察池内部广度偏弱。"],
                "salience": {"top_positive": [], "top_negative": [], "top_warning": []},
                "cross_section": {
                    "price": {
                        "ret_1d": {
                            "top_gain": [
                                {
                                    "asset_id": "399006",
                                    "score": 0.0188,
                                    "rank": 1,
                                    "metric": "ret_1d",
                                }
                            ],
                            "top_decline": [
                                {
                                    "asset_id": "000001",
                                    "score": -0.0123,
                                    "rank": 1,
                                    "metric": "ret_1d",
                                }
                            ],
                        }
                    },
                    "breadth": {
                        "breadth_ratio": {
                            "top_breadth": [
                                {
                                    "asset_id": "000001",
                                    "score": 0.24,
                                    "rank": 1,
                                    "metric": "breadth_ratio",
                                }
                            ],
                            "bottom_breadth": [
                                {
                                    "asset_id": "399006",
                                    "score": 0.16,
                                    "rank": 1,
                                    "metric": "breadth_ratio",
                                }
                            ],
                        }
                    },
                },
            }
        },
        "market": {
            "market_profile": {
                "one_liner": "当前市场画像：广度偏弱是主要结构特征。",
                "primary_label": "breadth_weakness",
                "dominant_dimensions": ["breadth"],
                "key_points": ["breadth 是当前主导维度。"],
                "top_salience": {
                    "positive": [],
                    "negative": [
                        {
                            "asset_id": "399006",
                            "rule_id": "s_pattern_up_breadth_weak",
                            "dimension": "breadth",
                            "score": 2.4,
                            "reason": "指数上行但跟随不足",
                        },
                        {
                            "asset_id": "399006",
                            "rule_id": "s_pattern_up_breadth_weak",
                            "dimension": "breadth",
                            "score": 2.4,
                            "reason": "指数上行但跟随不足",
                        },
                    ],
                    "warning": [],
                },
            },
            "market_regime": {
                "label": "权重防守市",
                "score": 3,
                "confidence": 0.6,
                "evidence": [],
            },
            "market_context": {
                "label": "Defense",
                "score": 6,
                "confidence": 0.75,
                "evidence": ["市场处于权重防守市"],
            },
            "policy": {
                "setup_permissions": {
                    "breakout": {"status": "forbidden", "size": "none"}
                },
                "execution_constraints": {"max_new_positions": 1},
                "vetoes": ["negative_structure_pressure"],
            },
            "relation_tags": [],
            "top_positive": [],
            "top_negative": [],
            "top_warning": [],
            "top_transition": [],
        },
    }

    text = render_markdown(payload)

    assert "## Executive Summary" in text
    assert "## Market Internals" in text
    assert "## Cross-Section Salience" in text
    assert "上证指数(000001)" in text
    assert "创业板指(399006)" in text
    assert "涨幅 TOP" in text
    assert "广度弱 TOP" in text
    assert text.count("创业板指(399006) [breadth]") == 1
    assert "策略权限" not in text
    assert "Risk Budget" not in text
    assert "Max New Positions" not in text
    assert "status=forbidden" not in text


def test_render_markdown_uses_sector_template_without_index_specific_sections():
    payload = {
        "date": "2026-05-27",
        "indices": {
            "880301": {
                "raw": {"adv": 0, "decl": 0},
                "features": {
                    "ret_1d": 0.012,
                    "amount_ratio_1_20": 1.30,
                    "volatility_percentile_250d": 0.70,
                    "breadth_ratio": 0.0,
                    "price_percentile_120d": 0.82,
                },
                "states": {
                    "trend_state": "up",
                    "position_state": "high",
                    "volume_state": "expansion",
                    "breadth_state": "weak",
                    "volatility_state": "medium",
                },
                "pattern_tags": [],
                "transition_tags": [],
            }
        },
        "universes": {
            "sector_universe": {
                "name": "行业指数观察池",
                "type": "sector",
                "members": ["880301"],
                "summary": ["行业指数观察池内部广度偏弱。"],
                "salience": {"top_positive": [], "top_negative": [], "top_warning": []},
                "cross_section": {
                    "price": {
                        "ret_1d": {
                            "top_gain": [
                                {
                                    "asset_id": "880301",
                                    "score": 0.012,
                                    "rank": 1,
                                    "metric": "ret_1d",
                                }
                            ],
                            "top_decline": [],
                        }
                    }
                },
            }
        },
        "market": {
            "market_profile": {
                "one_liner": "当前市场画像：板块结构分化。",
                "primary_label": "defensive_split",
                "dominant_dimensions": ["price"],
                "key_points": ["price 是当前主导维度。"],
                "top_salience": {
                    "positive": [],
                    "negative": [],
                    "warning": [
                        {
                            "asset_id": "880301",
                            "dimension": "breadth",
                            "score": 2.4,
                            "reason": "指数上行但跟随不足",
                        }
                    ],
                },
            },
            "market_regime": {"label": "", "score": 0, "confidence": 0, "evidence": []},
            "market_context": {},
            "relation_tags": [],
            "top_positive": [],
            "top_negative": [],
            "top_warning": [
                {
                    "asset": "880301",
                    "score": 2.4,
                    "reasons": ["指数上行但跟随不足"],
                }
            ],
            "top_transition": [],
        },
    }

    text = render_markdown(payload)

    assert "# 板块结构日报 - 2026-05-27" in text
    assert "## 板块轮动分析" in text
    assert "## 板块状态概览" in text
    assert "行业指数观察池" in text
    assert "涨幅 TOPN" in text
    assert "指数状态概览" not in text
    assert "主要指数观察池" not in text
    assert "指数上行" not in text
