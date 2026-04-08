from market_system.engine.resolver import Resolver
from market_system.engine.expression import evaluate_expression


def collect_market_relation_tags(market, pairs: dict):
    seen = set()
    tags = []
    traces = []
    for pair in pairs.values():
        for tag in pair.relation_tags:
            if tag not in seen:
                seen.add(tag)
                tags.append(tag)
                traces.append({"pair_id": pair.id, "tag": tag})
    market.relation_tags = tags
    market.trace["relations"] = traces
    return market


def score_market_regime(market, indices: dict, pairs: dict, regimes_dsl: dict):
    resolver = Resolver(current=market, indices=indices, pairs=pairs, market=market)
    best_label = ""
    best_score = -1.0
    best_evidence = []
    scores = []
    market.trace.setdefault("regimes", {})

    for regime in regimes_dsl["regimes"]:
        score = 0.0
        evidence = []
        matched_rules = []
        for rule in regime["rules"]:
            if evaluate_expression(rule["when"], resolver):
                score += float(rule["score"])
                evidence.append(rule["evidence"])
                matched_rules.append({"rule_id": rule["id"], "score": float(rule["score"]), "evidence": rule["evidence"]})
        scores.append(score)
        market.trace["regimes"][regime["id"]] = {"label": regime["label"], "score": score, "matched_rules": matched_rules}
        if score > best_score:
            best_score = score
            best_label = regime["label"]
            best_evidence = evidence

    total_score = sum(scores)
    confidence = (best_score / total_score) if total_score > 0 else 0.0
    market.market_regime = {
        "label": best_label,
        "score": best_score,
        "evidence": best_evidence,
        "confidence": confidence,
    }
    return market
