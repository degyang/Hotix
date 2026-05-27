from collections import Counter


def build_market_profile(date: str, universe_profiles: dict) -> dict:
    salience_items = _collect_salience_items(universe_profiles)
    dimension_scores = _score_dimensions(salience_items)
    top_salience = _build_top_salience(salience_items)
    primary_label = _select_primary_label(top_salience, dimension_scores)
    dominant_dimensions = [
        dimension
        for dimension, _score in sorted(
            dimension_scores.items(), key=lambda item: item[1], reverse=True
        )[:3]
    ]
    key_points = _build_key_points(
        primary_label, dominant_dimensions, top_salience, universe_profiles
    )

    return {
        "date": date,
        "primary_label": primary_label,
        "one_liner": _build_one_liner(primary_label),
        "dominant_dimensions": dominant_dimensions,
        "condition": "market_following",
        "key_points": key_points,
        "top_salience": top_salience,
        "universe_summaries": _collect_universe_summaries(universe_profiles),
    }


def _collect_salience_items(universe_profiles: dict) -> list[dict]:
    items = []
    for universe_id, profile in universe_profiles.items():
        salience = profile.get("salience", {})
        raw_items = list(salience.get("items", []))
        if not raw_items:
            raw_items.extend(
                _with_default_polarity(salience.get("top_positive", []), "positive")
            )
            raw_items.extend(
                _with_default_polarity(salience.get("top_negative", []), "negative")
            )
            raw_items.extend(_with_default_category(salience.get("top_warning", [])))
        for item in raw_items:
            enriched = dict(item)
            enriched.setdefault("universe_id", universe_id)
            enriched.setdefault("universe_name", profile.get("name", universe_id))
            items.append(enriched)
    return items


def _with_default_polarity(items: list[dict], polarity: str) -> list[dict]:
    return [dict(item, polarity=item.get("polarity", polarity)) for item in items]


def _with_default_category(items: list[dict]) -> list[dict]:
    return [dict(item, category=item.get("category", "warning")) for item in items]


def _score_dimensions(items: list[dict]) -> dict:
    counter = Counter()
    for item in items:
        dimension = item.get("dimension")
        if dimension:
            counter[dimension] += float(item.get("score", 0.0))
    return dict(counter)


def _build_top_salience(items: list[dict]) -> dict:
    sorted_items = sorted(items, key=lambda item: item.get("score", 0.0), reverse=True)
    return {
        "positive": [
            item for item in sorted_items if item.get("polarity") == "positive"
        ][:5],
        "negative": [
            item for item in sorted_items if item.get("polarity") == "negative"
        ][:5],
        "warning": [
            item
            for item in sorted_items
            if item.get("category") in {"warning", "divergence"}
        ][:5],
    }


def _select_primary_label(top_salience: dict, dimension_scores: dict) -> str:
    negative = top_salience["negative"]
    positive = top_salience["positive"]
    warning = top_salience["warning"]
    strongest_dimension = max(dimension_scores, key=dimension_scores.get, default=None)

    if strongest_dimension == "breadth" and negative:
        return "breadth_weakness"
    if warning and len(positive) <= len(warning):
        return "repair_unconfirmed"
    if negative and positive:
        return "defensive_split"
    if len(positive) >= 2 and not negative:
        return "healthy_expansion"
    return "no_clear_structure"


def _build_one_liner(primary_label: str) -> str:
    labels = {
        "breadth_weakness": "当前市场画像：广度偏弱是主要结构特征。",
        "repair_unconfirmed": "当前市场画像：修复线索存在，但确认度不足。",
        "defensive_split": "当前市场画像：正负显著性并存，结构分化。",
        "healthy_expansion": "当前市场画像：正向扩散较清晰。",
        "no_clear_structure": "当前市场画像：暂无清晰单边结构。",
    }
    return labels.get(primary_label, labels["no_clear_structure"])


def _build_key_points(
    primary_label: str,
    dominant_dimensions: list[str],
    top_salience: dict,
    universe_profiles: dict,
) -> list[str]:
    points = []
    if dominant_dimensions:
        points.append(f"{dominant_dimensions[0]} 是当前主导维度。")

    if primary_label == "breadth_weakness":
        points.append("负向显著性集中在广度或参与度维度。")
    elif primary_label == "repair_unconfirmed":
        points.append("预警或背离项仍然压制结构确认。")
    elif primary_label == "defensive_split":
        points.append("正向和负向显著性同时存在，市场内部结构分化。")
    elif primary_label == "healthy_expansion":
        points.append("正向显著性多于负向显著性。")
    else:
        points.append("各维度尚未形成稳定主线。")

    negative_count = len(top_salience["negative"])
    positive_count = len(top_salience["positive"])
    points.append(
        f"当前正向显著性 {positive_count} 项，负向显著性 {negative_count} 项。"
    )

    for summary in _collect_universe_summaries(universe_profiles)[:2]:
        points.append(summary)

    return points


def _collect_universe_summaries(universe_profiles: dict) -> list[str]:
    return [
        summary
        for profile in universe_profiles.values()
        for summary in profile.get("summary", [])
    ]
