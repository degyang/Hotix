from market_system.engine.expression import evaluate_expression
from market_system.engine.resolver import Resolver


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def detect_index_patterns(runtime, patterns_dsl: dict, prev_runtime=None):
    resolver = Resolver(current=runtime, prev=prev_runtime)
    hits = []
    traces = []
    for rule in patterns_dsl["patterns"]:
        if evaluate_expression(rule["when"], resolver):
            hits.append(rule["add_tag"])
            traces.append({"rule_id": rule["id"], "tag": rule["add_tag"]})
    runtime.pattern_tags = _dedupe_keep_order(hits)
    runtime.trace.setdefault("patterns", traces)
    return runtime


def detect_index_transitions(runtime, transitions_dsl: dict, prev_runtime=None):
    if prev_runtime is None:
        runtime.transition_tags = []
        runtime.trace.setdefault("transitions", [])
        return runtime

    resolver = Resolver(current=runtime, prev=prev_runtime)
    hits = []
    traces = []
    for rule in transitions_dsl["transitions"]:
        if evaluate_expression(rule["when"], resolver):
            hits.append(rule["add_tag"])
            traces.append({"rule_id": rule["id"], "tag": rule["add_tag"]})
    runtime.transition_tags = _dedupe_keep_order(hits)
    runtime.trace.setdefault("transitions", traces)
    return runtime
