import json

from hotix.engine.asset_registry import load_hotdx_portfolio_names


def test_load_hotdx_portfolio_names_normalizes_exchange_suffix(tmp_path):
    config_path = tmp_path / "portfolio.industry.json"
    config_path.write_text(
        json.dumps(
            {
                "queries": [
                    {"symbol": "880301.SH", "name": "煤炭"},
                    {"symbol": "399006.SZ", "name": "创业板指"},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert load_hotdx_portfolio_names(config_path) == {
        "880301": "煤炭",
        "399006": "创业板指",
    }
