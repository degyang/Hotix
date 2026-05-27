from hotix.engine.expression import normalize_expression


class ConfigValidationError(Exception):
    pass


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ConfigValidationError(message)


def _collect_unique_ids(items: list[dict], label: str) -> None:
    seen = set()
    for item in items:
        _ensure("id" in item and item["id"], f"{label} missing id")
        _ensure(item["id"] not in seen, f"{label} duplicated id: {item['id']}")
        seen.add(item["id"])


def _validate_expression(expr: str, label: str) -> None:
    try:
        compile(normalize_expression(expr), f"<{label}>", "eval")
    except SyntaxError as exc:
        raise ConfigValidationError(f"{label} invalid expression: {expr}") from exc


def validate_all_dsl(dsl: dict, registry: dict) -> None:
    _ensure("indices" in registry, "registry missing indices")
    index_ids = set(registry["indices"])

    _ensure(
        "features" in dsl and "features" in dsl["features"],
        "features.yaml missing features",
    )
    _collect_unique_ids(dsl["features"]["features"], "features")

    _ensure("states" in dsl and "states" in dsl["states"], "states.yaml missing states")
    _collect_unique_ids(dsl["states"]["states"], "states")
    for state in dsl["states"]["states"]:
        _ensure("output" in state, f"state missing output: {state.get('id')}")
        _ensure("cases" in state, f"state missing cases: {state.get('id')}")
        _ensure("default" in state, f"state missing default: {state.get('id')}")
        for case in state["cases"]:
            _ensure("when" in case, f"state case missing when: {state.get('id')}")
            _validate_expression(case["when"], f"state {state['id']}")

    _ensure("pairs" in dsl, "dsl missing pairs")
    _ensure(
        "salience" in dsl and "salience" in dsl["salience"],
        "salience.yaml missing salience",
    )
    _ensure(
        "scoring_rules" in dsl["salience"]["salience"],
        "salience.yaml missing scoring_rules",
    )
    _collect_unique_ids(dsl["salience"]["salience"]["scoring_rules"], "salience")
    for rule in dsl["salience"]["salience"]["scoring_rules"]:
        for required in [
            "group",
            "when",
            "score",
            "bucket",
            "polarity",
            "reason",
            "dimension",
            "category",
        ]:
            _ensure(
                required in rule,
                f"salience rule missing {required}: {rule.get('id')}",
            )
        _ensure(
            rule["bucket"] in {"positive", "negative", "warning", "transition"},
            f"salience rule invalid bucket: {rule.get('id')}",
        )
        _ensure(
            rule["polarity"] in {"positive", "negative", "neutral"},
            f"salience rule invalid polarity: {rule.get('id')}",
        )
        _validate_expression(rule["when"], f"salience {rule['id']}")

    _ensure("pairs" in dsl["pairs"], "pairs.yaml missing pairs")
    _collect_unique_ids(dsl["pairs"]["pairs"], "pairs")

    for pair in dsl["pairs"]["pairs"]:
        _ensure(pair["left"] in index_ids, f"unknown index: {pair['left']}")
        _ensure(pair["right"] in index_ids, f"unknown index: {pair['right']}")

    _ensure(
        "regimes" in dsl and "regimes" in dsl["regimes"], "regimes.yaml missing regimes"
    )
    _collect_unique_ids(dsl["regimes"]["regimes"], "regimes")
    for regime in dsl["regimes"]["regimes"]:
        _ensure("label" in regime, f"regime missing label: {regime.get('id')}")
        _ensure("rules" in regime, f"regime missing rules: {regime.get('id')}")
        for rule in regime["rules"]:
            _ensure(
                "id" in rule and rule["id"],
                f"regime rule missing id: {regime.get('id')}",
            )
            _ensure("when" in rule, f"regime rule missing when: {regime.get('id')}")
            _ensure("score" in rule, f"regime rule missing score: {regime.get('id')}")
            _ensure(
                "evidence" in rule, f"regime rule missing evidence: {regime.get('id')}"
            )
            _validate_expression(rule["when"], f"regime {regime['id']}")

    _ensure(
        "contexts" in dsl and "contexts" in dsl["contexts"],
        "contexts.yaml missing contexts",
    )
    _collect_unique_ids(dsl["contexts"]["contexts"], "contexts")
    for context in dsl["contexts"]["contexts"]:
        _ensure("label" in context, f"context missing label: {context.get('id')}")
        _ensure("rules" in context, f"context missing rules: {context.get('id')}")
        _ensure(
            "allowed_styles" in context,
            f"context missing allowed_styles: {context.get('id')}",
        )
        _ensure(
            "disallowed_styles" in context,
            f"context missing disallowed_styles: {context.get('id')}",
        )
        _ensure(
            "risk_budget" in context,
            f"context missing risk_budget: {context.get('id')}",
        )
        for rule in context["rules"]:
            _ensure(
                "id" in rule and rule["id"],
                f"context rule missing id: {context.get('id')}",
            )
            _ensure("when" in rule, f"context rule missing when: {context.get('id')}")
            _ensure("score" in rule, f"context rule missing score: {context.get('id')}")
            _ensure(
                "evidence" in rule,
                f"context rule missing evidence: {context.get('id')}",
            )
            _validate_expression(rule["when"], f"context {context['id']}")

    _ensure(
        "policies" in dsl and "policies" in dsl["policies"],
        "policies.yaml missing policies",
    )
    _ensure("defaults" in dsl["policies"], "policies.yaml missing defaults")
    _ensure(
        "setup_permissions" in dsl["policies"]["defaults"],
        "policies defaults missing setup_permissions",
    )
    _ensure(
        "execution_constraints" in dsl["policies"]["defaults"],
        "policies defaults missing execution_constraints",
    )
    _ensure("vetoes" in dsl["policies"]["defaults"], "policies defaults missing vetoes")
    _collect_unique_ids(dsl["policies"]["policies"], "policies")
    for policy in dsl["policies"]["policies"]:
        _ensure("priority" in policy, f"policy missing priority: {policy.get('id')}")
        _ensure("when" in policy, f"policy missing when: {policy.get('id')}")
        _ensure("set" in policy, f"policy rule missing set: {policy.get('id')}")
        _validate_expression(policy["when"], f"policy {policy['id']}")
