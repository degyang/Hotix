from market_system.engine.expression import evaluate_expression
from market_system.engine.models import PairRuntime
from market_system.engine.resolver import Resolver


def create_pair_runtime(pair_def: dict, date: str) -> PairRuntime:
    return PairRuntime(id=pair_def["id"], date=date, left=pair_def["left"], right=pair_def["right"], trace={})


def compute_pair_features(runtime, pair_features_dsl: dict, indices: dict):
    resolver = Resolver(current=runtime, indices=indices)
    runtime.trace.setdefault("features", {})
    for rule in pair_features_dsl["pair_features"]:
        value = evaluate_expression(rule["formula"], resolver)
        runtime.features[rule["output"]] = value
        runtime.trace["features"][rule["output"]] = {"rule_id": rule["id"], "output": value}
    return runtime


def derive_pair_states(runtime, pair_states_dsl: dict, indices: dict):
    resolver = Resolver(current=runtime, indices=indices)
    runtime.trace.setdefault("states", {})
    for rule in pair_states_dsl["pair_states"]:
        value = rule["default"]
        matched_case = None
        for idx, case in enumerate(rule["cases"]):
            if evaluate_expression(case["when"], resolver):
                value = case["value"]
                matched_case = idx
                break
        runtime.states[rule["output"]] = value
        runtime.trace["states"][rule["output"]] = {"rule_id": rule["id"], "matched_case": matched_case, "value": value}
    return runtime


def detect_pair_relation_tags(runtime, relation_tags_dsl: dict, indices: dict):
    resolver = Resolver(current=runtime, indices=indices)
    hits = []
    traces = []
    for rule in relation_tags_dsl["relation_tags"]:
        if rule["pair"] != runtime.id:
            continue
        if evaluate_expression(rule["when"], resolver):
            hits.append(rule["add_tag"])
            traces.append({"rule_id": rule["id"], "tag": rule["add_tag"]})
    runtime.relation_tags = hits
    runtime.trace.setdefault("relation_tags", traces)
    return runtime
