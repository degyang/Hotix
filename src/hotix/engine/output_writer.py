import json
from pathlib import Path

from hotix.engine.asset_registry import format_asset_label
from hotix.engine.report_templates import (
    ReportTemplate,
    select_report_template,
)

STATE_LABELS = {
    "up": "上行",
    "down": "下行",
    "range": "震荡",
    "transitional_down": "转弱",
    "transitional_up": "转强",
    "high": "高位",
    "mid": "中位",
    "low_mid": "中低位",
    "low": "低位",
    "normal": "常态",
    "expansion": "放量",
    "contraction": "缩量",
    "weak": "弱",
    "strong": "强",
    "neutral": "中性",
    "neutral_weak": "中性偏弱",
    "neutral_strong": "中性偏强",
    "medium": "中等",
    "extreme": "极端",
}


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json_output(output_dir: Path, date: str, payload: dict) -> Path:
    output_path = ensure_dir(output_dir) / f"{date}.json"
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_path


def render_markdown(payload: dict) -> str:
    market = payload["market"]
    profile = market.get("market_profile", {})
    regime = market["market_regime"]
    context = market.get("market_context", {})
    universes = payload.get("universes", {})
    indices = payload.get("indices", {})
    asset_names = payload.get("asset_names", {})
    template = select_report_template(universes)

    sections = [
        f"# {template.title} - {payload['date']}",
        "",
        "## Executive Summary",
        f"- 市场画像：{profile.get('one_liner', '当前市场画像：暂无清晰单边结构。')}",
        f"- 结构标签：{profile.get('primary_label', 'no_clear_structure')}",
        f"- 主导维度：{_join_or_none(profile.get('dominant_dimensions', []))}",
        *(_lines(_professional_key_points(profile, universes, indices, asset_names))),
        "",
        "## 一句话画像",
        f"- {profile.get('one_liner', '当前市场画像：暂无清晰单边结构。')}",
        f"- Label: {profile.get('primary_label', 'no_clear_structure')}",
        "",
        "## 今日主导维度",
        *(_lines(profile.get("dominant_dimensions", []))),
        "",
        "## 关键结论",
        *(_lines(_professional_key_points(profile, universes, indices, asset_names))),
        "",
        f"## {template.internals_title}",
        *(_render_market_internals(indices, template, asset_names)),
        "",
        "## Cross-Section Salience",
        *(_render_cross_section_salience(universes, asset_names)),
        "",
        f"## {template.universe_review_title}",
        *(_render_universe_review(universes, indices, asset_names)),
        "",
        "## Salience Details",
        "### Positive",
        *(
            _render_salience_items(
                profile.get("top_salience", {}).get("positive", []), template
            )
        ),
        "",
        "### Negative",
        *(
            _render_salience_items(
                profile.get("top_salience", {}).get("negative", []), template
            )
        ),
        "",
        "### Warning",
        *(
            _render_salience_items(
                profile.get("top_salience", {}).get("warning", []), template
            )
        ),
        "",
        "## Key Evidence",
        f"- Regime：{regime.get('label', '')}，score={regime.get('score', 0):.2f}，confidence={regime.get('confidence', 0):.2f}",
        f"- Market Context：{context.get('label', '')}，score={context.get('score', 0):.2f}，confidence={context.get('confidence', 0):.2f}",
        *(_lines(regime.get("evidence", []), prefix="Regime 证据")),
        *(_lines(context.get("evidence", []), prefix="Context 证据")),
        "",
        "## Observation Notes",
        "- 本报告只描述当前市场结构，不预测未来走势。",
        "- 本报告不提供买卖、仓位、回测或执行建议。",
        "",
        "## 市场上下文",
        f"- Label: {context.get('label', '')}",
        f"- Score: {context.get('score', 0):.2f}",
        f"- Confidence: {context.get('confidence', 0):.2f}",
        f"- Allowed: {_join_or_none(context.get('allowed_styles', []))}",
        f"- Disallowed: {_join_or_none(context.get('disallowed_styles', []))}",
        f"- Evidence: {'；'.join(context.get('evidence', [])) if context.get('evidence') else '无'}",
        "",
        "## 今日最亮信号",
        *(_render_market_bucket(market.get("top_positive", []), template, asset_names)),
        "",
        "## 今日最暗信号",
        *(_render_market_bucket(market.get("top_negative", []), template, asset_names)),
        "",
        "## 今日预警",
        *(_render_market_bucket(market.get("top_warning", []), template, asset_names)),
        "",
        "## 今日切换",
        *(
            _render_market_bucket(
                market.get("top_transition", []), template, asset_names
            )
        ),
        "",
        "## 结构关系",
        *(_lines(market.get("relation_tags", []))),
        "",
        f"## {template.overview_title}",
        *(_render_asset_overview(indices, template, asset_names)),
    ]
    return "\n".join(sections) + "\n"


def _asset_label(asset_id: str | None, asset_names: dict | None = None) -> str:
    return format_asset_label(asset_id, asset_names)


def _state_label(value) -> str:
    return STATE_LABELS.get(value, value if value is not None else "无")


def _format_percent(value) -> str:
    if value is None:
        return "无"
    return f"{float(value) * 100:.2f}%"


def _format_number(value, digits: int = 2) -> str:
    if value is None:
        return "无"
    return f"{float(value):.{digits}f}"


def _join_or_none(items: list) -> str:
    return "、".join(str(item) for item in items) if items else "无"


def _lines(items: list, prefix: str | None = None) -> list[str]:
    if not items:
        return ["- 无"] if prefix is None else []
    if prefix:
        return [f"- {prefix}：{item}" for item in items]
    return [f"- {item}" for item in items]


def _render_market_internals(
    indices: dict, template: ReportTemplate, asset_names: dict | None = None
) -> list[str]:
    if not indices:
        return ["- 无"]

    lines = [
        f"| {template.member_label} | 涨跌幅 | 广度 | 上涨/下跌家数 | 量能 | 波动 | 位置 | 趋势 |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for index_id, runtime in indices.items():
        raw = runtime.get("raw", {})
        features = runtime.get("features", {})
        states = runtime.get("states", {})
        adv_decl = f"{raw.get('adv', '无')}/{raw.get('decl', '无')}"
        lines.append(
            "| "
            + " | ".join(
                [
                    _asset_label(index_id, asset_names),
                    _format_percent(features.get("ret_1d")),
                    _format_percent(features.get("breadth_ratio")),
                    adv_decl,
                    _format_number(features.get("amount_ratio_1_20")),
                    _format_percent(features.get("volatility_percentile_250d")),
                    _format_percent(features.get("price_percentile_120d")),
                    _state_label(states.get("trend_state")),
                ]
            )
            + " |"
        )
    return lines


def _render_cross_section_salience(
    universes: dict, asset_names: dict | None = None
) -> list[str]:
    lines = []
    for universe_id, universe in universes.items():
        cross_section = universe.get("cross_section", {})
        if not cross_section:
            continue
        lines.extend([f"### {_universe_display_name(universe_id, universe)}", ""])
        lines.extend(
            _render_metric_topn(
                cross_section.get("price", {}).get("ret_1d", {}),
                "涨幅 TOPN",
                "跌幅 TOPN",
                positive_key="top_gain",
                negative_key="top_decline",
                percent=True,
                asset_names=asset_names,
            )
        )
        lines.extend(
            _render_metric_topn(
                cross_section.get("volume", {}).get("amount_ratio_1_20", {}),
                "量能放大 TOPN",
                "量能收缩 TOPN",
                positive_key="top_expansion",
                negative_key="top_contraction",
                asset_names=asset_names,
            )
        )
        lines.extend(
            _render_metric_topn(
                cross_section.get("volatility", {}).get(
                    "volatility_percentile_250d", {}
                ),
                "高波动 TOPN",
                "低波动 TOPN",
                positive_key="top_high_volatility",
                negative_key="top_low_volatility",
                percent=True,
                asset_names=asset_names,
            )
        )
        lines.extend(
            _render_metric_topn(
                cross_section.get("breadth", {}).get("breadth_ratio", {}),
                "广度强 TOPN",
                "广度弱 TOPN",
                positive_key="top_breadth",
                negative_key="bottom_breadth",
                percent=True,
                asset_names=asset_names,
            )
        )
        lines.extend(
            _render_metric_topn(
                cross_section.get("position", {}).get("price_percentile_120d", {}),
                "高位 TOPN",
                "低位 TOPN",
                positive_key="top_high_position",
                negative_key="top_low_position",
                percent=True,
                asset_names=asset_names,
            )
        )
        lines.append("")

    return lines or ["- 无"]


def _render_metric_topn(
    bucket: dict,
    positive_title: str,
    negative_title: str,
    positive_key: str,
    negative_key: str,
    percent: bool = False,
    asset_names: dict | None = None,
) -> list[str]:
    if not bucket:
        return []
    return [
        f"#### {positive_title}",
        *(
            _render_topn_items(
                bucket.get(positive_key, []),
                percent=percent,
                asset_names=asset_names,
            )
        ),
        "",
        f"#### {negative_title}",
        *(
            _render_topn_items(
                bucket.get(negative_key, []),
                percent=percent,
                asset_names=asset_names,
            )
        ),
        "",
    ]


def _render_topn_items(
    items: list[dict], percent: bool = False, asset_names: dict | None = None
) -> list[str]:
    if not items:
        return ["- 无"]
    lines = []
    for item in items:
        value = item.get("score")
        formatted_value = _format_percent(value) if percent else _format_number(value)
        lines.append(
            f"- #{item.get('rank', '?')} {_asset_label(item.get('asset_id'), asset_names)}: {formatted_value}"
        )
    return lines


def _render_universe_review(
    universes: dict, indices: dict, asset_names: dict | None = None
) -> list[str]:
    if not universes:
        return ["- 无"]
    lines = []
    for universe_id, universe in universes.items():
        member_names = [
            _asset_label(member, asset_names) for member in universe.get("members", [])
        ]
        lines.extend(
            [
                f"### {_universe_display_name(universe_id, universe)}",
                f"- 成员：{_join_or_none(member_names)}",
                *(
                    _lines(
                        [
                            _professionalize_summary(
                                summary, universe, indices, asset_names
                            )
                            for summary in universe.get("summary", [])
                        ]
                    )
                ),
                *(_render_universe_contributors(universe, indices, asset_names)),
                "",
            ]
        )
    return lines


def _render_universe_contributors(
    universe: dict, indices: dict, asset_names: dict | None = None
) -> list[str]:
    weak_members = []
    for member in universe.get("members", []):
        states = indices.get(member, {}).get("states", {})
        if states.get("breadth_state") == "weak":
            weak_members.append(_asset_label(member, asset_names))
    if not weak_members:
        return []
    return [f"- 广度弱贡献：{_join_or_none(weak_members)}"]


def _professional_key_points(
    profile: dict, universes: dict, indices: dict, asset_names: dict | None = None
) -> list[str]:
    points = []
    for point in profile.get("key_points", []):
        if "宽基指数" in point and "broad_indices" in universes:
            points.append(
                _professionalize_summary(
                    point, universes["broad_indices"], indices, asset_names
                )
            )
        else:
            points.append(point)
    return points


def _professionalize_summary(
    summary: str, universe: dict, indices: dict, asset_names: dict | None = None
) -> str:
    if "宽基指数" not in summary:
        return summary
    member_labels = [
        _asset_label(member, asset_names)
        for member in universe.get("members", [])
        if member in indices
    ]
    if not member_labels:
        return summary.replace(
            "宽基指数", _universe_display_name("broad_indices", universe)
        )
    if "广度偏弱" in summary:
        return f"{_join_or_none(member_labels)}等主要指数广度偏弱。"
    if "负向显著性多于正向显著性" in summary:
        return f"{_universe_display_name('broad_indices', universe)}负向显著性多于正向显著性，主要观察对象包括{_join_or_none(member_labels)}。"
    return summary.replace(
        "宽基指数", _universe_display_name("broad_indices", universe)
    )


def _universe_display_name(universe_id: str, universe: dict) -> str:
    if universe_id == "broad_indices":
        return "主要指数观察池"
    return universe.get("name", universe_id)


def _contextualize_text(text: str, template: ReportTemplate) -> str:
    if template.universe_type == "index":
        return text
    return text.replace("指数", template.member_label)


def _render_salience_items(items: list[dict], template: ReportTemplate) -> list[str]:
    deduped = _dedupe_salience_items(items)
    if not deduped:
        return ["- 无"]
    lines = []
    for item in deduped:
        dimension = item.get("dimension", "")
        score = item.get("score", 0.0)
        reason = _contextualize_text(item.get("reason", ""), template)
        lines.append(
            f"- {_asset_label(item.get('asset_id') or item.get('asset'))} [{dimension}] score={score:.2f}: {reason}"
        )
    return lines


def _dedupe_salience_items(items: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for item in items:
        key = (
            item.get("asset_id") or item.get("asset"),
            item.get("rule_id"),
            item.get("dimension"),
            item.get("reason"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _render_market_bucket(
    items: list[dict], template: ReportTemplate, asset_names: dict | None = None
) -> list[str]:
    if not items:
        return ["- 无"]
    return [
        f"- {_asset_label(item.get('asset'), asset_names)}（score={item['score']:.2f}）：{_contextualize_text('；'.join(item.get('reasons', [])) or '无', template)}"
        for item in items
    ]


def _render_asset_overview(
    indices: dict, template: ReportTemplate, asset_names: dict | None = None
) -> list[str]:
    if not indices:
        return ["- 无"]
    lines = []
    for index_id, runtime in indices.items():
        states = runtime.get("states", {})
        patterns = [
            _contextualize_text(pattern, template)
            for pattern in runtime.get("pattern_tags", [])
        ]
        transitions = [
            _contextualize_text(transition, template)
            for transition in runtime.get("transition_tags", [])
        ]
        lines.extend(
            [
                f"### {_asset_label(index_id, asset_names)}",
                f"- 趋势={_state_label(states.get('trend_state'))}，位置={_state_label(states.get('position_state'))}，量能={_state_label(states.get('volume_state'))}，广度={_state_label(states.get('breadth_state'))}，波动={_state_label(states.get('volatility_state'))}",
                f"- patterns: {_join_or_none(patterns)}",
                f"- transitions: {_join_or_none(transitions)}",
                "",
            ]
        )
    return lines


def write_markdown_output(output_dir: Path, date: str, markdown_text: str) -> Path:
    output_path = ensure_dir(output_dir) / f"{date}.md"
    output_path.write_text(markdown_text, encoding="utf-8")
    return output_path
