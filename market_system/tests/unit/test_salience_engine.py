from market_system.engine.salience_engine import score_index_salience


def test_score_index_salience_accumulates_bucket_scores(index_runtime_with_tags, dsl_bundle):
    runtime = score_index_salience(index_runtime_with_tags, dsl_bundle["salience"])
    assert runtime.salience["total_score"] == 6.3
    assert runtime.salience["positive_score"] == 4.1
    assert runtime.salience["transition_score"] == 2.2
    assert len(runtime.salience["matched_rules"]) == 3
