from dataclasses import dataclass

UNIVERSE_TYPE_ALIASES = {
    "index_panel": "index",
    "indices": "index",
    "sector_panel": "sector",
}

SUPPORTED_UNIVERSE_TYPES = {"index", "etf", "stock", "sector", "mixed"}


@dataclass(frozen=True)
class ReportTemplate:
    universe_type: str
    title: str
    internals_title: str
    universe_review_title: str
    overview_title: str
    universe_label: str
    member_label: str


REPORT_TEMPLATES = {
    "index": ReportTemplate(
        universe_type="index",
        title="市场结构日报",
        internals_title="Market Internals",
        universe_review_title="Universe 分析",
        overview_title="指数状态概览",
        universe_label="指数观察池",
        member_label="指数",
    ),
    "etf": ReportTemplate(
        universe_type="etf",
        title="ETF 组合结构日报",
        internals_title="ETF Internals",
        universe_review_title="ETF 轮动分析",
        overview_title="ETF 状态概览",
        universe_label="ETF 观察池",
        member_label="ETF",
    ),
    "stock": ReportTemplate(
        universe_type="stock",
        title="个股组合结构日报",
        internals_title="Stock Internals",
        universe_review_title="个股组合分析",
        overview_title="个股状态概览",
        universe_label="个股观察池",
        member_label="个股",
    ),
    "sector": ReportTemplate(
        universe_type="sector",
        title="板块结构日报",
        internals_title="Sector Internals",
        universe_review_title="板块轮动分析",
        overview_title="板块状态概览",
        universe_label="板块观察池",
        member_label="板块",
    ),
    "mixed": ReportTemplate(
        universe_type="mixed",
        title="组合结构日报",
        internals_title="Sample Internals",
        universe_review_title="样本组合分析",
        overview_title="样本状态概览",
        universe_label="样本观察池",
        member_label="样本",
    ),
}


def normalize_universe_type(value: str | None) -> str:
    normalized = (value or "mixed").strip().lower()
    normalized = UNIVERSE_TYPE_ALIASES.get(normalized, normalized)
    if normalized not in SUPPORTED_UNIVERSE_TYPES:
        return "mixed"
    return normalized


def get_report_template(universe_type: str | None) -> ReportTemplate:
    return REPORT_TEMPLATES[normalize_universe_type(universe_type)]


def select_report_template(universes: dict) -> ReportTemplate:
    if not universes:
        return get_report_template("index")
    if "broad_indices" in universes and not universes["broad_indices"].get("type"):
        return get_report_template("index")
    universe_types = {
        normalize_universe_type(universe.get("type")) for universe in universes.values()
    }
    if len(universe_types) == 1:
        return get_report_template(next(iter(universe_types)))
    return get_report_template("mixed")
