from market_system.engine.debug_report import build_index_debug_report, build_market_debug_report, build_pair_debug_report
from market_system.engine.pipeline import build_context, run_single_date
from market_system.tests.conftest import FIXTURES_DIR, PACKAGE_ROOT


def test_build_index_debug_report_contains_core_sections():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    payload = run_single_date(ctx, "2026-04-03")
    report = build_index_debug_report(payload, "000300")
    assert "features" in report
    assert "states" in report
    assert "pattern_tags" in report
    assert "salience" in report


def test_build_market_debug_report_contains_regime_and_relations():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    payload = run_single_date(ctx, "2026-04-03")
    report = build_market_debug_report(payload)
    assert "relation_tags" in report
    assert "market_regime" in report
    assert "market_context" in report
    assert "top_positive" in report


def test_build_pair_debug_report_contains_pair_sections():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    payload = run_single_date(ctx, "2026-04-03")
    report = build_pair_debug_report(payload, "000300_vs_399006")
    assert report["id"] == "000300_vs_399006"
    assert "features" in report
    assert "states" in report
