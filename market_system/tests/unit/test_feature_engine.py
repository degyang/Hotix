import pandas as pd

from market_system.engine.feature_engine import compute_index_features
from market_system.engine.loader import load_all_dsl
from market_system.tests.conftest import PACKAGE_ROOT


def test_compute_index_features_returns_expected_ret_and_ma_values():
    dsl = load_all_dsl(PACKAGE_ROOT / "dsl")
    rows = []
    for i in range(1, 26):
        rows.append(
            {
                "date": f"2026-03-{i:02d}",
                "open": 100 + i - 1,
                "high": 101 + i - 1,
                "low": 99 + i - 1,
                "close": 100 + i,
                "volume": 1000 + i * 10,
                "amount": 10000 + i * 100,
                "adv": 180 + i,
                "decl": 120 - min(i, 20),
            }
        )
    df = pd.DataFrame(rows)
    runtime = compute_index_features("000300", "2026-03-25", df, dsl["features"])
    assert round(runtime.features["ret_1d"], 6) == round((125 / 124) - 1, 6)
    assert round(runtime.features["ma_20"], 6) == round(sum(range(106, 126)) / 20, 6)
