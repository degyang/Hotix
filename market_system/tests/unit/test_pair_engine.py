from market_system.engine.pair_engine import (
    create_pair_runtime,
    compute_pair_features,
    derive_pair_states,
    detect_pair_relation_tags,
)


def test_compute_pair_features_returns_relative_strength(dsl_bundle, ready_indices):
    pair_definition = next(pair for pair in dsl_bundle["pairs"]["pairs"] if pair["id"] == "000300_vs_399006")
    runtime = create_pair_runtime(pair_definition, "2026-04-05")
    runtime = compute_pair_features(runtime, dsl_bundle["pair_features"], ready_indices)
    assert runtime.features["rs_ret_20d"] == 0.03


def test_derive_pair_states_returns_leader_state(dsl_bundle, ready_indices):
    pair_definition = next(pair for pair in dsl_bundle["pairs"]["pairs"] if pair["id"] == "000300_vs_399006")
    runtime = create_pair_runtime(pair_definition, "2026-04-05")
    runtime = compute_pair_features(runtime, dsl_bundle["pair_features"], ready_indices)
    runtime = derive_pair_states(runtime, dsl_bundle["pair_states"], ready_indices)
    assert runtime.states["leader_state"] == "left_strong"


def test_detect_pair_relation_tags_returns_expected_tag(dsl_bundle, ready_indices):
    pair_definition = next(pair for pair in dsl_bundle["pairs"]["pairs"] if pair["id"] == "000300_vs_000852")
    runtime = create_pair_runtime(pair_definition, "2026-04-05")
    runtime = compute_pair_features(runtime, dsl_bundle["pair_features"], ready_indices)
    runtime = derive_pair_states(runtime, dsl_bundle["pair_states"], ready_indices)
    runtime = detect_pair_relation_tags(runtime, dsl_bundle["relation_tags"], ready_indices)
    assert runtime.relation_tags == ["权重大盘主导"]
