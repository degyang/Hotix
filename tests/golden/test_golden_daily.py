import json

from conftest import FIXTURES_DIR, PACKAGE_ROOT

from hotix.engine.pipeline import build_context, run_single_date


def test_daily_payload_matches_golden_sample():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    actual = run_single_date(ctx, "2026-04-03")
    expected_path = FIXTURES_DIR / "expected_daily_2026-04-03.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    assert actual == expected
