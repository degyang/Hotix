from collections import Counter

from hotix.engine.salience_engine import build_cross_section_salience

STATE_FIELDS = [
    "trend_state",
    "position_state",
    "volume_state",
    "breadth_state",
    "volatility_state",
]


def build_all_universe_profiles(universes_dsl: dict, indices: dict) -> dict:
    return {
        universe["id"]: build_universe_profile(universe, indices)
        for universe in universes_dsl["universes"]
    }


def build_universe_profile(universe_def: dict, indices: dict) -> dict:
    members = [member for member in universe_def["members"] if member in indices]
    member_runtimes = {member: indices[member] for member in members}
    state = _build_state_distributions(member_runtimes)
    salience = _build_universe_salience(member_runtimes)
    participation = _build_participation(member_runtimes)

    return {
        "id": universe_def["id"],
        "name": universe_def["name"],
        "type": universe_def["type"],
        "role": universe_def["role"],
        "members": members,
        "participation": participation,
        "state": state,
        "salience": salience,
        "cross_section": build_cross_section_salience(member_runtimes, top_n=3),
        "summary": _build_summary(universe_def, state, salience, participation),
    }


def _build_state_distributions(member_runtimes: dict) -> dict:
    distributions = {}
    for state_field in STATE_FIELDS:
        counter = Counter(
            runtime.states[state_field]
            for runtime in member_runtimes.values()
            if state_field in runtime.states
        )
        distributions[f"{state_field.removesuffix('_state')}_distribution"] = dict(
            counter
        )
    return distributions


def _build_universe_salience(member_runtimes: dict) -> dict:
    items = [
        item
        for runtime in member_runtimes.values()
        for item in runtime.salience.get("items", [])
    ]
    sorted_items = sorted(items, key=lambda item: item.get("score", 0.0), reverse=True)

    def top_by_polarity(polarity: str) -> list[dict]:
        return [item for item in sorted_items if item.get("polarity") == polarity][:5]

    def top_by_category(category: str) -> list[dict]:
        return [item for item in sorted_items if item.get("category") == category][:5]

    return {
        "items": sorted_items,
        "top_positive": top_by_polarity("positive"),
        "top_negative": top_by_polarity("negative"),
        "top_warning": [
            item
            for item in sorted_items
            if item.get("category") in {"warning", "divergence"}
        ][:5],
        "top_divergence": top_by_category("divergence"),
    }


def _build_participation(member_runtimes: dict) -> dict:
    member_count = len(member_runtimes)
    weak_count = sum(
        1
        for runtime in member_runtimes.values()
        if runtime.states.get("breadth_state") == "weak"
    )
    strong_count = sum(
        1
        for runtime in member_runtimes.values()
        if runtime.states.get("breadth_state") == "strong"
    )
    return {
        "member_count": member_count,
        "weak_breadth_count": weak_count,
        "strong_breadth_count": strong_count,
        "weak_breadth_ratio": weak_count / member_count if member_count else 0.0,
        "strong_breadth_ratio": strong_count / member_count if member_count else 0.0,
    }


def _build_summary(
    universe_def: dict, state: dict, salience: dict, participation: dict
) -> list[str]:
    summary = []
    name = universe_def["name"]

    if participation["member_count"] == 0:
        return [f"{name}暂无可分析成员。"]

    if participation["weak_breadth_ratio"] >= 0.5:
        summary.append(f"{name}内部广度偏弱。")
    elif participation["strong_breadth_ratio"] >= 0.5:
        summary.append(f"{name}内部广度偏强。")

    if len(salience["top_positive"]) > len(salience["top_negative"]):
        summary.append(f"{name}正向显著性多于负向显著性。")
    elif len(salience["top_negative"]) > len(salience["top_positive"]):
        summary.append(f"{name}负向显著性多于正向显著性。")

    if not summary:
        summary.append(f"{name}结构混合，未形成单边显著性。")

    trend_distribution = state.get("trend_distribution", {})
    if trend_distribution:
        dominant_trend = max(trend_distribution, key=trend_distribution.get)
        summary.append(f"{name}主导趋势状态为{dominant_trend}。")

    return summary
