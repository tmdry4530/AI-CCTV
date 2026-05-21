#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_cctv.config import select_device


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train a YOLO detector for AI CCTV classes")
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--model", default="yolo11s.pt")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", default="-1")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--project", default="runs/train")
    parser.add_argument("--name", default="ai_cctv_s_640")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    device = select_device(args.device)
    if args.dry_run:
        print(f"would train model={args.model} data={args.data} epochs={args.epochs} imgsz={args.imgsz} device={device}")
        return 0
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception as exc:
        raise SystemExit(f"Ultralytics is required for training: {exc}") from exc
    model = YOLO(args.model)
    batch = int(args.batch) if str(args.batch).lstrip("-").isdigit() else args.batch
    model.train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=batch,
        device=device,
        project=args.project,
        name=args.name,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
