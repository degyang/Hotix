import pytest
from conftest import PACKAGE_ROOT

from hotix.engine.loader import load_all_dsl, load_registry
from hotix.engine.validator import ConfigValidationError, validate_all_dsl


def test_phase1_config_files_exist():
    required = [
        "config/index_registry.yaml",
        "dsl/features.yaml",
        "dsl/states.yaml",
        "dsl/patterns.yaml",
        "dsl/transitions.yaml",
        "dsl/salience.yaml",
        "dsl/pairs.yaml",
        "dsl/pair_features.yaml",
        "dsl/pair_states.yaml",
        "dsl/relation_tags.yaml",
        "dsl/regimes.yaml",
        "dsl/contexts.yaml",
        "dsl/policies.yaml",
    ]
    for rel in required:
        assert (PACKAGE_ROOT / rel).exists(), rel


def test_validate_all_dsl_accepts_phase1_files():
    registry = load_registry(PACKAGE_ROOT / "config/index_registry.yaml")
    dsl = load_all_dsl(PACKAGE_ROOT / "dsl")
    validate_all_dsl(dsl, registry)


def test_validate_all_dsl_accepts_code_based_regime_expression():
    registry = {"indices": {"000300": {"name": "沪深300"}}}
    dsl = {
        "features": {"features": []},
        "states": {"states": []},
        "patterns": {"patterns": []},
        "transitions": {"transitions": []},
        "salience": {"salience": {"scoring_rules": []}},
        "pairs": {"pairs": []},
        "pair_features": {"pair_features": []},
        "pair_states": {"pair_states": []},
        "relation_tags": {"relation_tags": []},
        "regimes": {
            "regimes": [
                {
                    "id": "test",
                    "label": "Test",
                    "rules": [
                        {
                            "id": "r1",
                            "when": "index.000300.trend_state == 'up'",
                            "score": 1,
                            "evidence": "ok",
                        }
                    ],
                }
            ]
        },
        "contexts": {"contexts": []},
        "policies": {
            "defaults": {
                "setup_permissions": {},
                "execution_constraints": {},
                "vetoes": [],
            },
            "policies": [],
        },
    }
    validate_all_dsl(dsl, registry)


def test_validate_all_dsl_rejects_invalid_regime_expression():
    registry = {"indices": {"000300": {"name": "沪深300"}}}
    dsl = {
        "features": {"features": []},
        "states": {"states": []},
        "patterns": {"patterns": []},
        "transitions": {"transitions": []},
        "salience": {"salience": {"scoring_rules": []}},
        "pairs": {"pairs": []},
        "pair_features": {"pair_features": []},
        "pair_states": {"pair_states": []},
        "relation_tags": {"relation_tags": []},
        "regimes": {
            "regimes": [
                {
                    "id": "test",
                    "label": "Test",
                    "rules": [
                        {
                            "id": "r1",
                            "when": "index.000300.trend_state ==",
                            "score": 1,
                            "evidence": "bad",
                        }
                    ],
                }
            ]
        },
        "contexts": {"contexts": []},
        "policies": {
            "defaults": {
                "setup_permissions": {},
                "execution_constraints": {},
                "vetoes": [],
            },
            "policies": [],
        },
    }
    with pytest.raises(ConfigValidationError, match="regime test invalid expression"):
        validate_all_dsl(dsl, registry)


def test_validate_all_dsl_rejects_unknown_pair_reference():
    registry = {"indices": {"000300": {"name": "沪深300"}}}
    dsl = {
        "features": {"features": []},
        "states": {"states": []},
        "patterns": {"patterns": []},
        "transitions": {"transitions": []},
        "salience": {"salience": {"scoring_rules": []}},
        "pairs": {"pairs": [{"id": "bad", "left": "000300", "right": "missing"}]},
        "pair_features": {"pair_features": []},
        "pair_states": {"pair_states": []},
        "relation_tags": {"relation_tags": []},
        "regimes": {"regimes": []},
        "contexts": {"contexts": []},
        "policies": {
            "defaults": {
                "setup_permissions": {},
                "execution_constraints": {},
                "vetoes": [],
            },
            "policies": [],
        },
    }
    with pytest.raises(ConfigValidationError):
        validate_all_dsl(dsl, registry)


def test_validate_all_dsl_rejects_duplicate_feature_ids():
    registry = {"indices": {"000300": {"name": "沪深300"}}}
    dsl = {
        "features": {
            "features": [
                {
                    "id": "dup",
                    "type": "formula",
                    "input": ["close"],
                    "formula": "1",
                    "output": "a",
                },
                {
                    "id": "dup",
                    "type": "formula",
                    "input": ["close"],
                    "formula": "1",
                    "output": "b",
                },
            ]
        },
        "states": {"states": []},
        "patterns": {"patterns": []},
        "transitions": {"transitions": []},
        "salience": {"salience": {"scoring_rules": []}},
        "pairs": {"pairs": []},
        "pair_features": {"pair_features": []},
        "pair_states": {"pair_states": []},
        "relation_tags": {"relation_tags": []},
        "regimes": {"regimes": []},
        "contexts": {"contexts": []},
        "policies": {
            "defaults": {
                "setup_permissions": {},
                "execution_constraints": {},
                "vetoes": [],
            },
            "policies": [],
        },
    }
    with pytest.raises(ConfigValidationError):
        validate_all_dsl(dsl, registry)


def test_validate_all_dsl_rejects_state_rule_missing_default():
    registry = {"indices": {"000300": {"name": "沪深300"}}}
    dsl = {
        "features": {"features": []},
        "states": {
            "states": [{"id": "trend_state", "output": "trend_state", "cases": []}]
        },
        "patterns": {"patterns": []},
        "transitions": {"transitions": []},
        "salience": {"salience": {"scoring_rules": []}},
        "pairs": {"pairs": []},
        "pair_features": {"pair_features": []},
        "pair_states": {"pair_states": []},
        "relation_tags": {"relation_tags": []},
        "regimes": {"regimes": []},
        "contexts": {"contexts": []},
        "policies": {
            "defaults": {
                "setup_permissions": {},
                "execution_constraints": {},
                "vetoes": [],
            },
            "policies": [],
        },
    }
    with pytest.raises(ConfigValidationError):
        validate_all_dsl(dsl, registry)


def test_validate_all_dsl_rejects_invalid_state_expression():
    registry = {"indices": {"000300": {"name": "沪深300"}}}
    dsl = {
        "features": {"features": []},
        "states": {
            "states": [
                {
                    "id": "trend_state",
                    "output": "trend_state",
                    "default": "range",
                    "cases": [{"when": "self.missing >", "value": "up"}],
                }
            ]
        },
        "patterns": {"patterns": []},
        "transitions": {"transitions": []},
        "salience": {"salience": {"scoring_rules": []}},
        "pairs": {"pairs": []},
        "pair_features": {"pair_features": []},
        "pair_states": {"pair_states": []},
        "relation_tags": {"relation_tags": []},
        "regimes": {"regimes": []},
        "contexts": {"contexts": []},
        "policies": {
            "defaults": {
                "setup_permissions": {},
                "execution_constraints": {},
                "vetoes": [],
            },
            "policies": [],
        },
    }
    with pytest.raises(ConfigValidationError, match="invalid expression"):
        validate_all_dsl(dsl, registry)


def test_validate_all_dsl_rejects_context_rule_missing_risk_budget():
    registry = {"indices": {"000300": {"name": "沪深300"}}}
    dsl = {
        "features": {"features": []},
        "states": {"states": []},
        "patterns": {"patterns": []},
        "transitions": {"transitions": []},
        "salience": {"salience": {"scoring_rules": []}},
        "pairs": {"pairs": []},
        "pair_features": {"pair_features": []},
        "pair_states": {"pair_states": []},
        "relation_tags": {"relation_tags": []},
        "regimes": {"regimes": []},
        "contexts": {
            "contexts": [
                {
                    "id": "cash",
                    "label": "Cash",
                    "rules": [
                        {
                            "id": "ctx_cash_01",
                            "when": "len(market.relation_tags) == 0",
                            "score": 2,
                            "evidence": "缺乏明确结构主线",
                        }
                    ],
                    "allowed_styles": ["观察"],
                    "disallowed_styles": ["主动进攻"],
                }
            ]
        },
    }
    with pytest.raises(ConfigValidationError, match="context missing risk_budget"):
        validate_all_dsl(dsl, registry)


def test_validate_all_dsl_rejects_invalid_context_expression():
    registry = {"indices": {"000300": {"name": "沪深300"}}}
    dsl = {
        "features": {"features": []},
        "states": {"states": []},
        "patterns": {"patterns": []},
        "transitions": {"transitions": []},
        "salience": {"salience": {"scoring_rules": []}},
        "pairs": {"pairs": []},
        "pair_features": {"pair_features": []},
        "pair_states": {"pair_states": []},
        "relation_tags": {"relation_tags": []},
        "regimes": {"regimes": []},
        "contexts": {
            "contexts": [
                {
                    "id": "cash",
                    "label": "Cash",
                    "rules": [
                        {
                            "id": "ctx_cash_01",
                            "when": "market.market_regime.label ==",
                            "score": 2,
                            "evidence": "坏表达式",
                        }
                    ],
                    "allowed_styles": ["观察"],
                    "disallowed_styles": ["主动进攻"],
                    "risk_budget": {
                        "total_exposure": 0.1,
                        "max_positions": 1,
                        "max_single_name_weight": 0.05,
                    },
                }
            ]
        },
    }
    with pytest.raises(ConfigValidationError, match="context cash invalid expression"):
        validate_all_dsl(dsl, registry)


def test_validate_all_dsl_rejects_policy_rule_missing_set():
    registry = {"indices": {"000300": {"name": "沪深300"}}}
    dsl = {
        "features": {"features": []},
        "states": {"states": []},
        "patterns": {"patterns": []},
        "transitions": {"transitions": []},
        "salience": {"salience": {"scoring_rules": []}},
        "pairs": {"pairs": []},
        "pair_features": {"pair_features": []},
        "pair_states": {"pair_states": []},
        "relation_tags": {"relation_tags": []},
        "regimes": {"regimes": []},
        "contexts": {"contexts": []},
        "policies": {
            "defaults": {
                "setup_permissions": {},
                "execution_constraints": {},
                "vetoes": [],
            },
            "policies": [
                {
                    "id": "pol_bad",
                    "priority": 100,
                    "when": "market.market_context.label == 'Cash'",
                }
            ],
        },
    }
    with pytest.raises(ConfigValidationError, match="policy rule missing set"):
        validate_all_dsl(dsl, registry)
