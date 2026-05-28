from hotix.engine.models import IndexRuntime
from hotix.engine.universe_engine import (
    build_all_universe_profiles,
    build_universe_profile,
)


def test_build_universe_profile_counts_state_distributions():
    indices = {
        "000300": IndexRuntime(
            id="000300",
            date="2026-05-27",
            states={"breadth_state": "weak", "trend_state": "down"},
            salience={"items": []},
        ),
        "399006": IndexRuntime(
            id="399006",
            date="2026-05-27",
            states={"breadth_state": "strong", "trend_state": "up"},
            salience={"items": []},
        ),
    }
    universe = {
        "id": "broad_indices",
        "name": "宽基指数",
        "type": "index_panel",
        "role": "market_core",
        "members": ["000300", "399006"],
    }

    profile = build_universe_profile(universe, indices)

    assert profile["state"]["breadth_distribution"] == {"weak": 1, "strong": 1}
    assert profile["state"]["trend_distribution"] == {"down": 1, "up": 1}
    assert profile["participation"]["member_count"] == 2
    assert profile["summary"]


def test_build_universe_profile_includes_cross_section_topn():
    indices = {
        "000300": IndexRuntime(
            id="000300",
            date="2026-05-27",
            features={"ret_1d": 0.01},
            salience={"items": []},
        ),
        "399006": IndexRuntime(
            id="399006",
            date="2026-05-27",
            features={"ret_1d": 0.03},
            salience={"items": []},
        ),
        "000852": IndexRuntime(
            id="000852",
            date="2026-05-27",
            features={"ret_1d": -0.02},
            salience={"items": []},
        ),
    }
    universe = {
        "id": "broad_indices",
        "name": "宽基指数",
        "type": "index_panel",
        "role": "market_core",
        "members": ["000300", "399006", "000852"],
    }

    profile = build_universe_profile(universe, indices)

    ret_1d = profile["cross_section"]["price"]["ret_1d"]
    assert ret_1d["top_gain"][0]["asset_id"] == "399006"
    assert ret_1d["top_decline"][0]["asset_id"] == "000852"


def test_build_universe_profile_uses_top5_when_member_count_reaches_10():
    indices = {
        f"8803{index:02d}": IndexRuntime(
            id=f"8803{index:02d}",
            date="2026-05-27",
            features={"ret_1d": index / 100},
            salience={"items": []},
        )
        for index in range(10)
    }
    universe = {
        "id": "sector_universe",
        "name": "行业指数观察池",
        "type": "sector",
        "role": "sector_structure",
        "members": list(indices),
    }

    profile = build_universe_profile(universe, indices)

    ret_1d = profile["cross_section"]["price"]["ret_1d"]
    assert len(ret_1d["top_gain"]) == 5
    assert len(ret_1d["top_decline"]) == 5


def test_build_universe_profile_sorts_salience_by_score():
    indices = {
        "000300": IndexRuntime(
            id="000300",
            date="2026-05-27",
            salience={
                "items": [
                    {
                        "asset_id": "000300",
                        "dimension": "breadth",
                        "polarity": "negative",
                        "category": "state",
                        "score": 2.2,
                        "reason": "广度极弱",
                    }
                ]
            },
        ),
        "399006": IndexRuntime(
            id="399006",
            date="2026-05-27",
            salience={
                "items": [
                    {
                        "asset_id": "399006",
                        "dimension": "price",
                        "polarity": "positive",
                        "category": "pattern",
                        "score": 3.0,
                        "reason": "低位放量修复",
                    }
                ]
            },
        ),
    }
    universe = {
        "id": "broad_indices",
        "name": "宽基指数",
        "type": "index_panel",
        "role": "market_core",
        "members": ["000300", "399006"],
    }

    profile = build_universe_profile(universe, indices)

    assert profile["salience"]["top_positive"][0]["asset_id"] == "399006"
    assert profile["salience"]["top_negative"][0]["asset_id"] == "000300"


def test_build_all_universe_profiles_returns_profiles_by_id():
    indices = {
        "000300": IndexRuntime(
            id="000300",
            date="2026-05-27",
            states={"trend_state": "up"},
            salience={"items": []},
        )
    }
    universes_dsl = {
        "universes": [
            {
                "id": "broad_indices",
                "name": "宽基指数",
                "type": "index_panel",
                "role": "market_core",
                "members": ["000300"],
            }
        ]
    }

    profiles = build_all_universe_profiles(universes_dsl, indices)

    assert set(profiles) == {"broad_indices"}
