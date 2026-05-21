#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract frames from a video file")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--every-n", type=int, default=10)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.every_n < 1:
        raise SystemExit("--every-n must be >= 1")
    if args.dry_run:
        print(f"would extract {args.source} -> {args.out} every {args.every_n} frames")
        return 0
    try:
        import cv2  # type: ignore
    except Exception as exc:
        raise SystemExit(f"OpenCV is required: {exc}") from exc
    cap = cv2.VideoCapture(str(args.source))
    if not cap.isOpened():
        raise SystemExit(f"Unable to open video: {args.source}")
    args.out.mkdir(parents=True, exist_ok=True)
    frame_idx = 0
    saved = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_idx % args.every_n == 0:
                out_path = args.out / f"{args.source.stem}_{frame_idx:06d}.jpg"
                cv2.imwrite(str(out_path), frame)
                saved += 1
                if args.limit is not None and saved >= args.limit:
                    break
            frame_idx += 1
    finally:
        cap.release()
    print(f"saved {saved} frames to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
