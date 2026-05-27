from hotix.engine.tag_engine import detect_index_patterns, detect_index_transitions


def test_detect_index_patterns_returns_expected_tags(index_runtime_ready, dsl_bundle):
    runtime = detect_index_patterns(index_runtime_ready, dsl_bundle["patterns"])
    assert runtime.pattern_tags == ["低位放量修复"]


def test_detect_index_transitions_returns_expected_tags(
    index_runtime_ready, prev_index_runtime, dsl_bundle
):
    runtime = detect_index_transitions(
        index_runtime_ready, dsl_bundle["transitions"], prev_index_runtime
    )
    assert runtime.transition_tags == ["趋势转上"]
