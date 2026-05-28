import json
from functools import lru_cache
from pathlib import Path

INDEX_NAMES = {
    "000001": "上证指数",
    "399001": "深证成指",
    "000016": "上证50",
    "000300": "沪深300",
    "000905": "中证500",
    "000852": "中证1000",
    "399006": "创业板指",
    "000680": "科创综指",
}

HOTDX_CONFIG_DIR = Path("~/Projects/hotdx/config").expanduser()
HOTDX_PORTFOLIO_FILES = [
    "portfolio_index.json",
    "portfolio.industry.json",
]


def _normalize_symbol(symbol: str) -> str:
    return symbol.split(".", maxsplit=1)[0]


def load_hotdx_portfolio_names(path: Path | str) -> dict[str, str]:
    path = Path(path)
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        _normalize_symbol(item["symbol"]): item["name"]
        for item in payload.get("queries", [])
        if item.get("symbol") and item.get("name")
    }


@lru_cache(maxsize=8)
def load_hotdx_asset_names(config_dir: Path | str = HOTDX_CONFIG_DIR) -> dict[str, str]:
    config_dir = Path(config_dir)
    names = {}
    for filename in HOTDX_PORTFOLIO_FILES:
        names.update(load_hotdx_portfolio_names(config_dir / filename))
    return names


def asset_names_from_registry(registry: dict) -> dict[str, str]:
    return {
        asset_id: config.get("name", asset_id)
        for asset_id, config in registry.get("indices", {}).items()
    }


def format_asset_label(asset_id: str | None, asset_names: dict | None = None) -> str:
    if not asset_id:
        return "unknown"
    names = {**INDEX_NAMES, **load_hotdx_asset_names(), **(asset_names or {})}
    name = names.get(asset_id)
    if not name or name == asset_id:
        return asset_id
    return f"{name}({asset_id})"
