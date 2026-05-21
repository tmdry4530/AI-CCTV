#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_cctv.runtime import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AI CCTV runtime on a video file")
    parser.add_argument("--source", type=Path, required=True, help="Video file path")
    parser.add_argument("--config", type=Path, default=Path("configs") / "demo_mac.yaml")
    parser.add_argument("--no-window", action="store_true", help="Disable OpenCV display window")
    parser.add_argument("--dry-run", action="store_true", help="Validate config/source arguments without opening model")
    parser.add_argument("--max-frames", type=int, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return run_pipeline(
        args.config,
        source_override=args.source,
        dry_run=args.dry_run,
        show=not args.no_window,
        max_frames=args.max_frames,
    )


if __name__ == "__main__":
    raise SystemExit(main())
