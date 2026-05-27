from copy import deepcopy

from hotix.engine.expression import evaluate_expression
from hotix.engine.models import PolicyOutput
from hotix.engine.resolver import Resolver


def _merge_list(target: list, values) -> list:
    incoming = values if isinstance(values, list) else [values]
    result = list(target)
    for value in incoming:
        if value not in result:
            result.append(value)
    return result


def _set_path(target: dict, path: str, value) -> None:
    if path == "vetoes":
        target["vetoes"] = _merge_list(target.get("vetoes", []), value)
        return

    current = target
    parts = path.split(".")
    for part in parts[:-1]:
        current = current.setdefault(part, {})
    current[parts[-1]] = value


def _apply_set(target: dict, values: dict) -> None:
    for path, value in values.items():
        if (
            isinstance(value, dict)
            and path in target
            and isinstance(target[path], dict)
        ):
            _apply_set(target[path], value)
            continue
        _set_path(target, path, value)


def score_policy(market, indices: dict, pairs: dict, policies_dsl: dict) -> dict:
    resolver = Resolver(current=market, indices=indices, pairs=pairs, market=market)
    result = deepcopy(policies_dsl.get("defaults", {}))
    result.setdefault("setup_permissions", {})
    result.setdefault("execution_constraints", {})
    result.setdefault("vetoes", [])

    matched_rules = []
    policies = sorted(
        enumerate(policies_dsl.get("policies", [])),
        key=lambda item: (int(item[1].get("priority", 0)), item[0]),
    )
    for _, rule in policies:
        if evaluate_expression(rule["when"], resolver):
            _apply_set(result, rule.get("set", {}))
            matched_rules.append(
                {"rule_id": rule["id"], "priority": int(rule.get("priority", 0))}
            )

    trace = {"matched_rules": matched_rules}
    market.trace["policy"] = trace
    return PolicyOutput(
        setup_permissions=result["setup_permissions"],
        execution_constraints=result["execution_constraints"],
        vetoes=result["vetoes"],
        trace=trace,
    ).to_dict()
