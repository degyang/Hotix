import json
from pathlib import Path


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
    regime = market["market_regime"]
    context = market.get("market_context", {})
    policy = market.get("policy", {})
    profile = market.get("market_profile", {})
    relation_lines = [f"- {tag}" for tag in market.get("relation_tags", [])]
    if not relation_lines:
        relation_lines = ["- 无"]
    policy_lines = []
    for setup, permission in policy.get("setup_permissions", {}).items():
        policy_lines.append(
            f"- {setup}: status={permission.get('status')}, size={permission.get('size')}"
        )
    if not policy_lines:
        policy_lines = ["- 无"]

    def render_bucket(items):
        if not items:
            return ["- 无"]
        return [
            f"- {item['asset']}（score={item['score']:.2f}）：{'；'.join(item.get('reasons', [])) or '无'}"
            for item in items
        ]

    def render_lines(items):
        return [f"- {item}" for item in items] if items else ["- 无"]

    def render_salience_items(items):
        if not items:
            return ["- 无"]
        lines = []
        for item in items:
            asset = item.get("asset_id") or item.get("asset") or "unknown"
            dimension = item.get("dimension", "")
            score = item.get("score", 0.0)
            reason = item.get("reason", "")
            lines.append(f"- {asset} [{dimension}] score={score:.2f}: {reason}")
        return lines

    universe_sections = []
    for universe_id, universe in payload.get("universes", {}).items():
        universe_sections.extend(
            [
                f"### {universe.get('name', universe_id)}",
                *render_lines(universe.get("summary", [])),
                "",
            ]
        )
    if not universe_sections:
        universe_sections = ["- 无"]

    index_sections = []
    for index_id, runtime in payload.get("indices", {}).items():
        states = runtime.get("states", {})
        index_sections.extend(
            [
                f"### {index_id}",
                f"- trend={states.get('trend_state')}, position={states.get('position_state')}, volume={states.get('volume_state')}, breadth={states.get('breadth_state')}, volatility={states.get('volatility_state')}",
                f"- patterns: {', '.join(runtime.get('pattern_tags', [])) if runtime.get('pattern_tags') else '无'}",
                f"- transitions: {', '.join(runtime.get('transition_tags', [])) if runtime.get('transition_tags') else '无'}",
                "",
            ]
        )
    return (
        "\n".join(
            [
                f"# 市场结构日报 - {payload['date']}",
                "",
                "## 一句话画像",
                f"- {profile.get('one_liner', '当前市场画像：暂无清晰单边结构。')}",
                f"- Label: {profile.get('primary_label', 'no_clear_structure')}",
                "",
                "## 今日主导维度",
                *render_lines(profile.get("dominant_dimensions", [])),
                "",
                "## 关键结论",
                *render_lines(profile.get("key_points", [])),
                "",
                "## Universe 分析",
                *universe_sections,
                "",
                "## Salience 明细",
                "### Positive",
                *render_salience_items(
                    profile.get("top_salience", {}).get("positive", [])
                ),
                "",
                "### Negative",
                *render_salience_items(
                    profile.get("top_salience", {}).get("negative", [])
                ),
                "",
                "### Warning",
                *render_salience_items(
                    profile.get("top_salience", {}).get("warning", [])
                ),
                "",
                "## 市场状态",
                f"- Regime: {regime.get('label', '')}",
                f"- Score: {regime.get('score', 0):.2f}",
                f"- Confidence: {regime.get('confidence', 0):.2f}",
                "",
                "## 市场上下文",
                f"- Label: {context.get('label', '')}",
                f"- Score: {context.get('score', 0):.2f}",
                f"- Confidence: {context.get('confidence', 0):.2f}",
                f"- Allowed: {', '.join(context.get('allowed_styles', [])) if context.get('allowed_styles') else '无'}",
                f"- Disallowed: {', '.join(context.get('disallowed_styles', [])) if context.get('disallowed_styles') else '无'}",
                f"- Risk Budget: total_exposure={context.get('risk_budget', {}).get('total_exposure', 0)}, max_positions={context.get('risk_budget', {}).get('max_positions', 0)}, max_single_name_weight={context.get('risk_budget', {}).get('max_single_name_weight', 0)}",
                f"- Evidence: {'；'.join(context.get('evidence', [])) if context.get('evidence') else '无'}",
                "",
                "## 策略权限",
                *policy_lines,
                f"- Max New Positions: {policy.get('execution_constraints', {}).get('max_new_positions', 0)}",
                f"- Intraday Addons: {policy.get('execution_constraints', {}).get('intraday_addons', False)}",
                f"- Require Confirmation: {policy.get('execution_constraints', {}).get('require_confirmation', True)}",
                f"- Vetoes: {', '.join(policy.get('vetoes', [])) if policy.get('vetoes') else '无'}",
                "",
                "## 今日最亮信号",
                *render_bucket(market.get("top_positive", [])),
                "",
                "## 今日最暗信号",
                *render_bucket(market.get("top_negative", [])),
                "",
                "## 今日预警",
                *render_bucket(market.get("top_warning", [])),
                "",
                "## 今日切换",
                *render_bucket(market.get("top_transition", [])),
                "",
                "## 结构关系",
                *relation_lines,
                "",
                "## Regime 证据",
                *([f"- {item}" for item in regime.get("evidence", [])] or ["- 无"]),
                "",
                "## 指数状态概览",
                *index_sections,
            ]
        )
        + "\n"
    )


def write_markdown_output(output_dir: Path, date: str, markdown_text: str) -> Path:
    output_path = ensure_dir(output_dir) / f"{date}.md"
    output_path.write_text(markdown_text, encoding="utf-8")
    return output_path
