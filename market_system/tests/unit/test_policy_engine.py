from market_system.engine.policy_engine import score_policy


def test_score_policy_uses_cash_defaults_and_base_rule(dsl_bundle, market_runtime_ready, ready_indices, ready_pairs):
    market_runtime_ready.market_context = {
        "label": "Cash",
        "score": 5.0,
        "confidence": 0.71,
        "risk_budget": {"total_exposure": 0.10, "max_positions": 1, "max_single_name_weight": 0.05},
    }

    result = score_policy(market_runtime_ready, ready_indices, ready_pairs, dsl_bundle["policies"])

    assert result["setup_permissions"]["breakout"] == {"status": "forbidden", "size": "none"}
    assert result["setup_permissions"]["low_level_repair"] == {"status": "probe_only", "size": "tiny"}
    assert result["execution_constraints"]["max_new_positions"] == 1
    assert result["execution_constraints"]["require_confirmation"] is True
    assert "chaotic_market_override" in result["vetoes"]
    assert result["trace"]["matched_rules"][0]["rule_id"] == "pol_cash_base"


def test_score_policy_applies_later_higher_priority_overrides(dsl_bundle, market_runtime_ready, ready_indices, ready_pairs):
    market_runtime_ready.market_context = {"label": "Offense", "score": 4.0, "confidence": 0.8}
    market_runtime_ready.relation_tags = ["成长风格占优"]
    market_runtime_ready.top_warning = [{"asset": "000300", "score": 2.8, "reasons": ["高位放量分歧"]}]

    result = score_policy(market_runtime_ready, ready_indices, ready_pairs, dsl_bundle["policies"])

    assert result["setup_permissions"]["breakout"] == {"status": "restricted", "size": "small"}
    assert result["setup_permissions"]["continuation_pullback"] == {"status": "allowed", "size": "normal"}
    assert result["setup_permissions"]["high_beta_chase"]["status"] == "forbidden"
    assert result["execution_constraints"]["require_confirmation"] is True
    assert "warning_overhang" in result["vetoes"]
    assert [item["rule_id"] for item in result["trace"]["matched_rules"]] == [
        "pol_growth_confirmed_bonus",
        "pol_offense_base",
        "pol_warning_cap",
    ]
