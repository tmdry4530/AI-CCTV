#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_cctv.camera import record_webcam


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record webcam video for demo-domain data collection")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source", default="0")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--seconds", type=float, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source = int(args.source) if str(args.source).isdecimal() else args.source
    path = record_webcam(args.out, source=source, width=args.width, height=args.height, fps=args.fps, seconds=args.seconds)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
