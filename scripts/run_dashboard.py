#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_cctv.app import load_events_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Streamlit dashboard for AI CCTV events")
    parser.add_argument("--log", type=Path, default=Path("data") / "logs" / "events.csv")
    parser.add_argument("--snapshots", type=Path, default=Path("data") / "snapshots")
    parser.add_argument("--dry-run", action="store_true", help="Check event CSV readability without launching Streamlit")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.dry_run:
        rows = load_events_csv(args.log)
        print(f"dashboard inputs ok: log={args.log} rows={len(rows)} snapshots={args.snapshots}")
        return 0
    from ai_cctv.app import dashboard_main

    dashboard_main(args.log, args.snapshots)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
