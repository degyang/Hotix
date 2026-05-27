import sys
from pathlib import Path

import pytest
from conftest import FIXTURES_DIR, PACKAGE_ROOT

from hotix.engine.output_writer import render_markdown
from hotix.engine.pipeline import (
    build_context,
    latest_available_date,
    run_date_range,
    run_single_date,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_run_single_date_returns_complete_payload():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    payload = run_single_date(ctx, "2026-04-03")
    assert set(payload) == {"date", "indices", "pairs", "market", "universes"}
    assert set(payload["indices"]) == {
        "000001",
        "399001",
        "000016",
        "000300",
        "000905",
        "000852",
        "399006",
        "000680",
    }
    assert set(payload["pairs"]) == {
        "000300_vs_399006",
        "000300_vs_000680",
        "000300_vs_000905",
        "000300_vs_000852",
        "000016_vs_000852",
        "399006_vs_000680",
        "000905_vs_000852",
    }


def test_run_single_date_includes_universe_profiles():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    payload = run_single_date(ctx, "2026-04-03")

    broad = payload["universes"]["broad_indices"]
    assert broad["name"] == "宽基指数"
    assert "state" in broad
    assert "cross_section" in broad
    assert "salience" in broad
    assert "summary" in broad


def test_run_single_date_includes_market_profile():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    payload = run_single_date(ctx, "2026-04-03")

    profile = payload["market"]["market_profile"]
    assert "primary_label" in profile
    assert "dominant_dimensions" in profile
    assert "key_points" in profile


def test_run_single_date_market_payload_contains_regime_and_relations():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    payload = run_single_date(ctx, "2026-04-03")
    assert "market_regime" in payload["market"]
    assert "market_context" in payload["market"]
    assert "relation_tags" in payload["market"]
    assert "top_positive" in payload["market"]
    assert "top_negative" in payload["market"]
    assert "top_warning" in payload["market"]
    assert "top_transition" in payload["market"]
    assert "policy" in payload["market"]


def test_run_date_range_returns_all_common_dates():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    results = run_date_range(ctx, start="2026-04-02", end="2026-04-03")
    assert [item["date"] for item in results] == ["2026-04-02", "2026-04-03"]


def test_run_date_range_write_files_creates_json_and_markdown():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    results = run_date_range(
        ctx, start="2026-04-03", end="2026-04-03", write_files=True
    )
    assert len(results) == 1
    assert (PACKAGE_ROOT / "outputs/json/2026-04-03.json").exists()
    assert (PACKAGE_ROOT / "outputs/markdown/2026-04-03.md").exists()


def test_run_single_date_includes_trace_and_regime_confidence():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    payload = run_single_date(ctx, "2026-04-03")
    core = payload["indices"]["000300"]
    assert "trace" in core
    assert "features" in core["trace"]
    assert "states" in core["trace"]
    assert "patterns" in core["trace"]
    assert "transitions" in core["trace"]
    assert "salience" in core["trace"]
    assert "confidence" in payload["market"]["market_regime"]
    assert "label" in payload["market"]["market_context"]
    assert "setup_permissions" in payload["market"]["policy"]
    assert "trace" in payload["market"]


def test_run_daily_debug_index_command_outputs_index_payload():
    import json
    import subprocess

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hotix.run_daily",
            "--date",
            "2026-04-03",
            "--data-dir",
            str(FIXTURES_DIR),
            "--debug-index",
            "000300",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    payload = json.loads(completed.stdout)
    assert payload["id"] == "000300"
    assert "features" in payload


def test_run_daily_debug_pair_command_outputs_pair_payload():
    import json
    import subprocess

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hotix.run_daily",
            "--date",
            "2026-04-03",
            "--data-dir",
            str(FIXTURES_DIR),
            "--debug-pair",
            "000300_vs_399006",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    payload = json.loads(completed.stdout)
    assert payload["id"] == "000300_vs_399006"
    assert "features" in payload


def test_run_daily_debug_market_command_outputs_market_context():
    import json
    import subprocess

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hotix.run_daily",
            "--date",
            "2026-04-03",
            "--data-dir",
            str(FIXTURES_DIR),
            "--debug-market",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    payload = json.loads(completed.stdout)
    assert "market_regime" in payload
    assert "market_context" in payload


def test_run_single_date_rejects_missing_trade_date():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    with pytest.raises(
        ValueError, match="No market data available for date 2026-04-04"
    ):
        run_single_date(ctx, "2026-04-04")


def test_run_single_date_rejects_date_before_available_data():
    ctx = build_context(PACKAGE_ROOT, data_dir=FIXTURES_DIR)
    with pytest.raises(
        ValueError, match="No market data available for date 2025-03-10"
    ):
        run_single_date(ctx, "2025-03-10")


def test_run_daily_module_can_run_from_source_package_directory():
    import json
    import subprocess

    completed = subprocess.run(
        [
            sys.executable,
            "run_daily.py",
            "--date",
            "2026-04-03",
            "--data-dir",
            str(FIXTURES_DIR),
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=PACKAGE_ROOT,
    )
    payload = json.loads(completed.stdout)
    assert payload["date"] == "2026-04-03"
    assert "market" in payload


def test_run_daily_accepts_external_data_dir_with_symbol_files(tmp_path):
    import json
    import shutil
    import subprocess

    mapping = {
        "000001": "000001.csv",
        "399001": "399001.csv",
        "000016": "000016.csv",
        "000300": "000300.csv",
        "000905": "000905.csv",
        "000852": "000852.csv",
        "399006": "399006.csv",
        "000680": "000680.csv",
    }
    for symbol, fixture_name in mapping.items():
        shutil.copyfile(FIXTURES_DIR / fixture_name, tmp_path / f"{symbol}.csv")

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hotix.run_daily",
            "--date",
            "2026-04-03",
            "--data-dir",
            str(tmp_path),
            "--dump-json",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    payload = json.loads(completed.stdout)
    assert payload["date"] == "2026-04-03"
    assert payload["indices"]["000300"]["raw"]["close"] == 4440.79


def test_run_daily_latest_uses_latest_common_fixture_date():
    import json
    import subprocess

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hotix.run_daily",
            "--latest",
            "--data-dir",
            str(FIXTURES_DIR),
            "--dump-json",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    payload = json.loads(completed.stdout)
    assert payload["date"] == "2026-04-03"


@pytest.mark.external
def test_run_daily_latest_uses_latest_common_date_from_external_data_dir():
    import json
    import subprocess

    external_data_dir = Path("~/data/index/daily").expanduser()
    expected_date = latest_available_date(
        build_context(PACKAGE_ROOT, data_dir=external_data_dir)
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "hotix.run_daily",
            "--latest",
            "--data-dir",
            str(external_data_dir),
            "--dump-json",
        ],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO_ROOT,
    )
    payload = json.loads(completed.stdout)
    assert payload["date"] == expected_date
    assert "broad_indices" in payload["universes"]
    broad = payload["universes"]["broad_indices"]
    assert len(broad["members"]) == 8
    assert "breadth_distribution" in broad["state"]
    assert "cross_section" in broad
    assert "price" in broad["cross_section"]
    assert broad["summary"]
    profile = payload["market"]["market_profile"]
    assert profile["primary_label"]
    items = [
        item
        for index_payload in payload["indices"].values()
        for item in index_payload["salience"].get("items", [])
    ]
    assert items
    assert {
        "id",
        "rule_id",
        "asset_id",
        "dimension",
        "category",
        "polarity",
        "score",
        "evidence",
    } <= set(items[0])


@pytest.mark.external
def test_real_data_latest_markdown_report_contains_market_profile():
    ctx = build_context(PACKAGE_ROOT, data_dir=Path("~/data/index/daily").expanduser())
    payload = run_single_date(ctx, latest_available_date(ctx))

    text = render_markdown(payload)

    assert "## 一句话画像" in text
    assert "## Universe 分析" in text
    assert payload["market"]["market_profile"]["primary_label"] in text


def test_run_daily_requires_data_dir():
    import subprocess

    completed = subprocess.run(
        [sys.executable, "-m", "hotix.run_daily", "--latest"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    assert completed.returncode != 0
    assert (
        "Provide --data-dir" in completed.stderr
        or "Provide --data-dir" in completed.stdout
    )
