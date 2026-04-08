from market_system.engine.expression import evaluate_expression
from market_system.engine.resolver import Resolver


def build_market_salience(indices: dict):
    def collect(bucket: str):
        items = []
        score_key = f"{bucket}_score"
        for index_id, runtime in indices.items():
            score = runtime.salience.get(score_key, 0.0)
            if score > 0:
                items.append(
                    {
                        "asset": index_id,
                        "score": score,
                        "reasons": [rule["reason"] for rule in runtime.salience["matched_rules"] if rule["bucket"] == bucket],
                    }
                )
        return sorted(items, key=lambda item: item["score"], reverse=True)

    return {
        "top_positive": collect("positive"),
        "top_negative": collect("negative"),
        "top_warning": collect("warning"),
        "top_transition": collect("transition"),
    }


def score_index_salience(runtime, salience_dsl: dict, prev_runtime=None):
    resolver = Resolver(current=runtime, prev=prev_runtime)
    result = {
        "total_score": 0.0,
        "positive_score": 0.0,
        "negative_score": 0.0,
        "warning_score": 0.0,
        "transition_score": 0.0,
        "matched_rules": [],
    }

    for rule in salience_dsl["salience"]["scoring_rules"]:
        if evaluate_expression(rule["when"], resolver):
            score = float(rule["score"])
            result["total_score"] += score
            bucket_key = f"{rule['bucket']}_score"
            if bucket_key in result:
                result[bucket_key] += score
            result["matched_rules"].append(
                {
                    "rule_id": rule["id"],
                    "score": score,
                    "bucket": rule["bucket"],
                    "polarity": rule["polarity"],
                    "reason": rule["reason"],
                }
            )

    runtime.salience = result
    runtime.trace.setdefault("salience", result["matched_rules"])
    return runtime
