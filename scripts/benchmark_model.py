from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

from _bootstrap import add_src_to_path

add_src_to_path()

from ai_cctv.camera import parse_source  # noqa: E402
from ai_cctv.config import select_device  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark YOLO inference FPS on webcam/video sources.")
    parser.add_argument("--model", type=Path, default=Path("models") / "best_demo.pt")
    parser.add_argument("--source", default="0", help="Camera index or video file path.")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--frames", type=int, default=120)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    device = select_device(args.device)
    if args.dry_run:
        print(
            f"Benchmark dry-run: model={args.model} source={args.source} imgsz={args.imgsz} "
            f"device={device} frames={args.frames}"
        )
        return 0
    if not args.model.exists():
        raise SystemExit(
            f"Model file does not exist yet: {args.model}. Train/copy models/best_demo.pt before benchmarking."
        )
    parsed_source = parse_source(args.source)
    if isinstance(parsed_source, str) and not Path(parsed_source).exists():
        raise SystemExit(f"Benchmark source does not exist yet: {parsed_source}")
    try:
        import cv2  # type: ignore
        from ultralytics import YOLO  # type: ignore
    except ImportError as exc:
        raise SystemExit("opencv-python and ultralytics are required for benchmarking.") from exc
    capture = cv2.VideoCapture(parsed_source)
    if not capture.isOpened():
        raise SystemExit(f"Could not open benchmark source: {args.source}")
    model = YOLO(str(args.model))
    count = 0
    start = perf_counter()
    try:
        while count < args.frames:
            ok, frame = capture.read()
            if not ok:
                break
            model.predict(frame, imgsz=args.imgsz, device=device, verbose=False)
            count += 1
    finally:
        capture.release()
    elapsed = perf_counter() - start
    fps = count / elapsed if elapsed > 0 else 0.0
    print(f"frames={count}")
    print(f"elapsed_seconds={elapsed:.3f}")
    print(f"fps={fps:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
