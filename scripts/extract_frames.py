from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract image frames from a video file.")
    parser.add_argument("--source", type=Path, required=True, help="Input video path.")
    parser.add_argument("--out", type=Path, required=True, help="Output image directory.")
    parser.add_argument("--every-n", type=int, default=10, help="Save every Nth frame.")
    parser.add_argument("--limit", type=int, default=0, help="Maximum frames to save; 0 means no limit.")
    parser.add_argument("--prefix", default=None, help="Filename prefix; defaults to source stem.")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and print plan.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.every_n <= 0:
        raise SystemExit("--every-n must be > 0")
    if not args.source.exists():
        raise SystemExit(f"Input video does not exist yet: {args.source}")
    if args.dry_run:
        print(f"Would extract every {args.every_n} frames from {args.source} to {args.out}")
        return 0
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise SystemExit("opencv-python is required for frame extraction.") from exc
    args.out.mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(str(args.source))
    if not capture.isOpened():
        raise SystemExit(f"Could not open video: {args.source}")
    prefix = args.prefix or args.source.stem
    frame_index = 0
    saved = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if frame_index % args.every_n == 0:
                path = args.out / f"{prefix}_{frame_index:06d}.jpg"
                if not cv2.imwrite(str(path), frame):
                    raise SystemExit(f"Could not write frame: {path}")
                saved += 1
                if args.limit and saved >= args.limit:
                    break
            frame_index += 1
    finally:
        capture.release()
    print(f"Saved {saved} frames to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
