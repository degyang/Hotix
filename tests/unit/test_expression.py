from hotix.engine.expression import evaluate_expression
from hotix.engine.models import IndexRuntime
from hotix.engine.resolver import Resolver


def test_expression_evaluates_boolean_rule_against_runtime():
    curr = IndexRuntime(
        id="000300",
        date="2026-04-05",
        raw={},
        features={"ret_1d": 0.02},
        states={"trend_state": "up"},
    )
    resolver = Resolver(current=curr)
    assert (
        evaluate_expression("self.ret_1d > 0 and self.trend_state == 'up'", resolver)
        is True
    )


def test_expression_accepts_code_based_index_reference():
    curr = IndexRuntime(
        id="000300",
        date="2026-04-05",
        raw={},
        features={"ret_1d": 0.02},
        states={"trend_state": "up"},
    )
    resolver = Resolver(current=curr, indices={"000300": curr})
    assert evaluate_expression("index.000300.trend_state == 'up'", resolver) is True
