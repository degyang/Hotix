import pytest

from market_system.engine.loader import load_all_dsl
from market_system.engine.models import IndexRuntime
from market_system.engine.state_engine import derive_index_states
from market_system.tests.conftest import PACKAGE_ROOT


def test_derive_index_states_sets_trend_and_volume_states():
    dsl = load_all_dsl(PACKAGE_ROOT / "dsl")
    runtime = IndexRuntime(
        id="000300",
        date="2026-04-05",
        raw={"close": 105},
        features={
            "ma_20": 100,
            "ma_60": 95,
            "ma_slope_20": 0.02,
            "price_percentile_120d": 0.5,
            "amount_ratio_1_20": 1.2,
            "amount_percentile_120d": 0.6,
            "breadth_ratio": 0.62,
            "volatility_percentile_250d": 0.5,
        },
    )
    runtime = derive_index_states(runtime, dsl["states"])
    assert runtime.states["trend_state"] == "up"
    assert runtime.states["volume_state"] == "expansion"


def test_derive_index_states_raises_for_invalid_expression():
    runtime = IndexRuntime(id="000300", date="2026-04-05", raw={}, features={}, states={}, trace={})
    dsl = {
        "states": [
            {
                "id": "broken_rule",
                "output": "trend_state",
                "default": "range",
                "cases": [{"when": "self.missing > 0", "value": "up"}],
            }
        ]
    }

    with pytest.raises(Exception, match="broken_rule"):
        derive_index_states(runtime, dsl)
