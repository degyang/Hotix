import json
from pathlib import Path

from market_system.engine.pipeline import build_context, run_single_date
from market_system.tests.conftest import FIXTURES_DIR, PACKAGE_ROOT


def test_daily_payload_matches_golden_sample():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    actual = run_single_date(ctx, "2026-04-03")
    expected_path = PACKAGE_ROOT / "tests/fixtures/expected_daily_2026-04-03.json"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    assert actual == expected
