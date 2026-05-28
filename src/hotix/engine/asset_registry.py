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


def asset_names_from_registry(registry: dict) -> dict[str, str]:
    return {
        asset_id: config.get("name", asset_id)
        for asset_id, config in registry.get("indices", {}).items()
    }


def format_asset_label(asset_id: str | None, asset_names: dict | None = None) -> str:
    if not asset_id:
        return "unknown"
    names = asset_names or INDEX_NAMES
    name = names.get(asset_id) or INDEX_NAMES.get(asset_id)
    if not name or name == asset_id:
        return asset_id
    return f"{name}({asset_id})"
