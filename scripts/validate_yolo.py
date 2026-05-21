#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_cctv.config import select_device


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a YOLO detector for AI CCTV classes")
    parser.add_argument("--model", required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    device = select_device(args.device)
    if args.dry_run:
        print(f"would validate model={args.model} data={args.data} imgsz={args.imgsz} device={device}")
        return 0
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception as exc:
        raise SystemExit(f"Ultralytics is required for validation: {exc}") from exc
    model = YOLO(args.model)
    metrics = model.val(data=str(args.data), imgsz=args.imgsz, device=device)
    print(metrics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
