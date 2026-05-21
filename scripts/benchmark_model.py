#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_cctv.camera import VideoSource
from ai_cctv.config import select_device


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark YOLO runtime FPS on webcam or video")
    parser.add_argument("--model", required=True)
    parser.add_argument("--source", default="0")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--frames", type=int, default=120)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    device = select_device(args.device)
    source = int(args.source) if str(args.source).isdecimal() else args.source
    if args.dry_run:
        print(f"would benchmark model={args.model} source={source} imgsz={args.imgsz} device={device}")
        return 0
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception as exc:
        raise SystemExit(f"Ultralytics is required for benchmark: {exc}") from exc
    model = YOLO(args.model)
    measured = 0
    inference_seconds = 0.0
    with VideoSource(source) as cap:
        frame_idx = 0
        while measured < args.frames:
            ok, frame = cap.read()
            if not ok:
                break
            frame_idx += 1
            start = time.perf_counter()
            model.predict(source=frame, imgsz=args.imgsz, device=device, verbose=False)
            elapsed = time.perf_counter() - start
            if frame_idx > args.warmup:
                measured += 1
                inference_seconds += elapsed
    fps = measured / inference_seconds if inference_seconds > 0 else 0.0
    avg_ms = (inference_seconds / measured * 1000.0) if measured else 0.0
    print(f"device={device} frames={measured} fps={fps:.2f} avg_inference_ms={avg_ms:.2f}")
    return 0 if measured else 1


if __name__ == "__main__":
    raise SystemExit(main())
