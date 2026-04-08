import argparse
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market_system.engine.debug_report import build_index_debug_report, build_market_debug_report
from market_system.engine.debug_report import build_pair_debug_report
from market_system.engine.pipeline import build_context, latest_available_date, run_date_range, run_single_date
from market_system.paths import PACKAGE_ROOT


def parse_args():
    parser = argparse.ArgumentParser(description="Run Hotix market structure pipeline.")
    parser.add_argument("--date", type=str, default=None)
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    parser.add_argument("--data-dir", type=str, default=None)
    parser.add_argument("--dump-json", action="store_true")
    parser.add_argument("--write-files", action="store_true")
    parser.add_argument("--debug-index", type=str, default=None)
    parser.add_argument("--debug-pair", type=str, default=None)
    parser.add_argument("--debug-market", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.data_dir:
        raise SystemExit("Provide --data-dir.")
    ctx = build_context(PACKAGE_ROOT, data_dir=args.data_dir)
    target_date = latest_available_date(ctx) if args.latest else args.date
    if target_date:
        payload = run_single_date(ctx, target_date)
        if args.write_files:
            run_date_range(ctx, start=target_date, end=target_date, write_files=True)
        if args.debug_index:
            print(json.dumps(build_index_debug_report(payload, args.debug_index), ensure_ascii=False, indent=2))
            return
        if args.debug_pair:
            print(json.dumps(build_pair_debug_report(payload, args.debug_pair), ensure_ascii=False, indent=2))
            return
        if args.debug_market:
            print(json.dumps(build_market_debug_report(payload), ensure_ascii=False, indent=2))
            return
        print(json.dumps(payload if args.dump_json else {"date": payload["date"], "market": payload["market"]}, ensure_ascii=False, indent=2))
        return
    if args.start or args.end:
        results = run_date_range(ctx, start=args.start, end=args.end, write_files=args.write_files)
        print(json.dumps({"dates_processed": len(results)}, ensure_ascii=False, indent=2))
        return
    raise SystemExit("Provide --date, --latest, or --start/--end.")


if __name__ == "__main__":
    main()
