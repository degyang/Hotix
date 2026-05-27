from dataclasses import asdict, dataclass, field

from hotix.engine.expression import evaluate_expression
from hotix.engine.resolver import Resolver


@dataclass
class MarketContextResult:
    label: str = ""
    score: float = 0.0
    confidence: float = 0.0
    allowed_styles: list[str] = field(default_factory=list)
    disallowed_styles: list[str] = field(default_factory=list)
    risk_budget: dict = field(default_factory=dict)
    evidence: list[str] = field(default_factory=list)
    runner_up: str = ""
    runner_up_score: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


def score_market_context(
    market, indices: dict, pairs: dict, contexts_dsl: dict
) -> dict:
    resolver = Resolver(current=market, indices=indices, pairs=pairs, market=market)
    scores = []
    trace = {}

    for context_def in contexts_dsl["contexts"]:
        total_score = 0.0
        evidence = []
        matched_rules = []
        for rule in context_def["rules"]:
            if evaluate_expression(rule["when"], resolver):
                score = float(rule["score"])
                total_score += score
                evidence.append(rule["evidence"])
                matched_rules.append(
                    {
                        "rule_id": rule["id"],
                        "score": score,
                        "evidence": rule["evidence"],
                    }
                )
        scores.append((context_def, total_score, evidence))
        trace[context_def["id"]] = {
            "label": context_def["label"],
            "score": total_score,
            "matched_rules": matched_rules,
        }

    market.trace["contexts"] = trace
    ranked = sorted(scores, key=lambda item: item[1], reverse=True)
    if not ranked:
        return MarketContextResult().to_dict()

    winner_def, winner_score, winner_evidence = ranked[0]
    runner_up_def, runner_up_score, _ = ranked[1] if len(ranked) > 1 else ({}, 0.0, [])
    total_score = sum(score for _, score, _ in ranked)
    confidence = winner_score / total_score if total_score > 0 else 0.0

    return MarketContextResult(
        label=winner_def["label"],
        score=winner_score,
        confidence=confidence,
        allowed_styles=winner_def.get("allowed_styles", []),
        disallowed_styles=winner_def.get("disallowed_styles", []),
        risk_budget=winner_def.get("risk_budget", {}),
        evidence=winner_evidence,
        runner_up=runner_up_def.get("label", ""),
        runner_up_score=runner_up_score,
    ).to_dict()
