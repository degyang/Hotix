import pandas as pd

from market_system.engine.feature_engine import compute_index_features
from market_system.engine.loader import load_all_dsl
from market_system.tests.conftest import PACKAGE_ROOT


def test_compute_index_features_includes_distance_percentile_and_breakout_fields():
    dsl = load_all_dsl(PACKAGE_ROOT / "dsl")
    rows = []
    for i in range(1, 131):
        rows.append(
            {
                "date": f"2026-01-{((i - 1) % 28) + 1:02d}" if i <= 28 else f"2026-02-{((i - 29) % 28) + 1:02d}" if i <= 56 else f"2026-03-{((i - 57) % 31) + 1:02d}" if i <= 87 else f"2026-04-{((i - 88) % 30) + 1:02d}" if i <= 117 else f"2026-05-{i-117:02d}",
                "open": 100 + i - 1,
                "high": 101 + i - 1,
                "low": 99 + i - 1,
                "close": 100 + i,
                "volume": 1000 + i * 10,
                "amount": 10000 + i * 100,
                "adv": 180 + i,
                "decl": 120,
            }
        )
    df = pd.DataFrame(rows)
    runtime = compute_index_features("000300", df.iloc[-1]["date"], df, dsl["features"])
    assert runtime.features["distance_to_ma20"] is not None
    assert runtime.features["price_percentile_120d"] is not None
    assert runtime.features["amount_percentile_120d"] is not None
    assert runtime.features["breakout_20d"] in {True, False}
