from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from ai_cctv.camera import parse_source  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record webcam video for later AI CCTV dataset creation.")
    parser.add_argument("--out", type=Path, required=True, help="Output video path under data/raw/.")
    parser.add_argument("--source", default="0", help="Camera index or video device name. Default: 0")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--seconds", type=float, default=0.0, help="Auto-stop after seconds; 0 means press q.")
    parser.add_argument("--dry-run", action="store_true", help="Create no file; print planned capture settings.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.dry_run:
        print(f"Would record source={args.source} to {args.out} at {args.width}x{args.height}@{args.fps}")
        return 0
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise SystemExit("opencv-python is required for webcam recording.") from exc

    args.out.parent.mkdir(parents=True, exist_ok=True)
    source = parse_source(args.source)
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        raise SystemExit(f"Could not open camera source: {args.source}")
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    capture.set(cv2.CAP_PROP_FPS, args.fps)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(args.out), fourcc, float(args.fps), (args.width, args.height))
    if not writer.isOpened():
        capture.release()
        raise SystemExit(f"Could not create output video: {args.out}")
    started = cv2.getTickCount()
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                raise SystemExit("Camera read failed while recording.")
            frame = cv2.resize(frame, (args.width, args.height))
            writer.write(frame)
            cv2.imshow("record_webcam", frame)
            elapsed = (cv2.getTickCount() - started) / cv2.getTickFrequency()
            if args.seconds > 0 and elapsed >= args.seconds:
                break
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        writer.release()
        capture.release()
        cv2.destroyAllWindows()
    print(f"Recorded: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
