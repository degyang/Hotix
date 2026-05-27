from hotix.engine.expression import evaluate_expression
from hotix.engine.resolver import Resolver


def derive_index_states(runtime, states_dsl: dict, prev_runtime=None):
    runtime.trace.setdefault("states", {})
    resolver = Resolver(current=runtime, prev=prev_runtime)

    for rule in states_dsl["states"]:
        output = rule["output"]
        value = rule["default"]
        matched_case = None
        for index, case in enumerate(rule["cases"]):
            try:
                if evaluate_expression(case["when"], resolver):
                    value = case["value"]
                    matched_case = index
                    break
            except TypeError:
                continue
            except Exception as exc:
                raise ValueError(
                    f"Failed to evaluate state rule {rule['id']}: {case['when']}"
                ) from exc
        runtime.states[output] = value
        runtime.trace["states"][output] = {
            "rule_id": rule["id"],
            "matched_case": matched_case,
            "value": value,
        }

    return runtime
