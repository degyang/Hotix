from pathlib import Path

from market_system.engine.loader import load_all_dsl, load_csv_data, load_registry
from market_system.tests.conftest import PACKAGE_ROOT


def test_project_root_contains_expected_entrypoints():
    assert (PACKAGE_ROOT / "requirements.txt").exists()
    assert (PACKAGE_ROOT / "engine" / "__init__.py").exists()
    assert (PACKAGE_ROOT / "run_daily.py").exists()


def test_load_registry_returns_indices_dict():
    data = load_registry(PACKAGE_ROOT / "config/index_registry.yaml")
    assert set(data["indices"]) == {"000001", "399001", "000016", "000300", "000905", "000852", "399006", "000680"}
    assert data["indices"]["000300"]["symbol"] == "000300"


def test_load_all_dsl_returns_expected_roots():
    dsl = load_all_dsl(PACKAGE_ROOT / "dsl")
    assert "features" in dsl
    assert "regimes" in dsl
    assert "contexts" in dsl


def test_load_csv_data_normalizes_dates_and_order():
    df = load_csv_data(PACKAGE_ROOT / "tests/fixtures/000300.csv")
    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume", "amount", "adv", "decl"]
    assert df["date"].tolist() == sorted(df["date"].tolist())


def test_load_csv_data_accepts_external_index_schema(tmp_path):
    path = tmp_path / "000300.csv"
    path.write_text(
        "\n".join(
            [
                "datetime,open,close,high,low,vol,amount,up_count,down_count",
                "2005-01-05 15:00,981.57,992.56,997.32,979.87,71191.0,4529206784.0,80,5",
                "2005-01-04 15:00:00,994.76,982.79,994.76,980.65,74128.0,4431975936.0,0,0",
            ]
        ),
        encoding="utf-8",
    )

    df = load_csv_data(path)

    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume", "amount", "adv", "decl"]
    assert df["date"].tolist() == ["2005-01-04", "2005-01-05"]
    assert df["volume"].iloc[-1] == 71191.0
    assert df["adv"].iloc[-1] == 80
    assert df["decl"].iloc[-1] == 5


def test_load_all_data_prefers_symbol_named_csv_files(tmp_path):
    from market_system.engine.loader import load_all_data

    source = PACKAGE_ROOT / "tests/fixtures/000300.csv"
    target = tmp_path / "000300.csv"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    registry = {"indices": {"000300": {"name": "沪深300", "symbol": "000300"}}}
    data = load_all_data(tmp_path, registry)

    assert "000300" in data
    assert data["000300"]["close"].iloc[-1] == 4440.79
