from market_system.engine.models import IndexRuntime
from market_system.engine.resolver import Resolver


def test_resolver_reads_self_prev_and_index_paths():
    prev = IndexRuntime(
        id="000300",
        date="2026-04-04",
        raw={},
        features={"ret_1d": -0.01},
        states={"trend_state": "down"},
    )
    curr = IndexRuntime(
        id="000300",
        date="2026-04-05",
        raw={},
        features={"ret_1d": 0.02},
        states={"trend_state": "up"},
    )
    resolver = Resolver(current=curr, prev=prev, indices={"000300": curr}, pairs={}, market=None)
    assert resolver.resolve("self.ret_1d") == 0.02
    assert resolver.resolve("prev.trend_state") == "down"
    assert resolver.resolve("index.000300.trend_state") == "up"
