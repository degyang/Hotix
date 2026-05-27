from pathlib import Path

import pytest

from hotix.engine.loader import load_all_dsl
from hotix.engine.models import IndexRuntime, MarketRuntime

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "src"
PACKAGE_ROOT = SRC_ROOT / "hotix"
FIXTURES_DIR = ROOT / "tests" / "fixtures"


@pytest.fixture
def dsl_bundle():
    return load_all_dsl(PACKAGE_ROOT / "dsl")


@pytest.fixture
def prev_index_runtime():
    return IndexRuntime(
        id="000300",
        date="2026-04-04",
        raw={"close": 100},
        features={
            "ret_1d": -0.01,
            "ma_20": 99,
            "ma_60": 100,
            "ma_slope_20": -0.01,
            "price_percentile_120d": 0.30,
            "amount_ratio_1_20": 1.0,
            "amount_percentile_120d": 0.50,
            "breadth_ratio": 0.52,
            "volatility_percentile_250d": 0.45,
        },
        states={
            "trend_state": "range",
            "position_state": "low_mid",
            "volume_state": "normal",
            "breadth_state": "neutral",
            "volatility_state": "medium",
        },
        trace={},
    )


@pytest.fixture
def index_runtime_ready():
    return IndexRuntime(
        id="000300",
        date="2026-04-05",
        raw={"close": 105},
        features={
            "ret_1d": 0.02,
            "ma_20": 100,
            "ma_60": 95,
            "ma_slope_20": 0.02,
            "price_percentile_120d": 0.15,
            "amount_ratio_1_20": 1.20,
            "amount_percentile_120d": 0.65,
            "breadth_ratio": 0.66,
            "volatility_percentile_250d": 0.50,
            "breakout_20d": False,
        },
        states={
            "trend_state": "up",
            "position_state": "low",
            "volume_state": "expansion",
            "breadth_state": "strong",
            "volatility_state": "medium",
        },
        trace={},
    )


@pytest.fixture
def index_runtime_with_tags(index_runtime_ready):
    index_runtime_ready.pattern_tags = ["低位放量修复"]
    index_runtime_ready.transition_tags = ["趋势转上"]
    return index_runtime_ready


@pytest.fixture
def ready_indices():
    return {
        "000300": IndexRuntime(
            id="000300",
            date="2026-04-05",
            raw={"close": 105},
            features={
                "ret_5d": 0.04,
                "ret_20d": 0.08,
                "amount_ratio_5_20": 1.10,
                "breadth_ratio_ma_5": 0.60,
            },
            states={
                "trend_state": "up",
                "breadth_state": "neutral_weak",
            },
            trace={},
        ),
        "399006": IndexRuntime(
            id="399006",
            date="2026-04-05",
            raw={"close": 102},
            features={
                "ret_5d": 0.02,
                "ret_20d": 0.05,
                "amount_ratio_5_20": 0.95,
                "breadth_ratio_ma_5": 0.52,
            },
            states={
                "trend_state": "down",
                "breadth_state": "neutral",
            },
            trace={},
        ),
        "000852": IndexRuntime(
            id="000852",
            date="2026-04-05",
            raw={"close": 99},
            features={
                "ret_5d": 0.01,
                "ret_20d": 0.02,
                "amount_ratio_5_20": 0.90,
                "breadth_ratio_ma_5": 0.40,
            },
            states={
                "trend_state": "range",
                "breadth_state": "weak",
            },
            trace={},
        ),
    }


@pytest.fixture
def ready_pairs():
    return {
        "000300_vs_399006": type(
            "PairStub",
            (),
            {"relation_tags": [], "id": "000300_vs_399006"},
        )(),
        "000300_vs_000852": type(
            "PairStub",
            (),
            {"relation_tags": ["权重大盘主导"], "id": "000300_vs_000852"},
        )(),
    }


@pytest.fixture
def market_runtime_ready():
    return MarketRuntime(date="2026-04-05")
