from __future__ import annotations

import argparse
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

try:
    from _bootstrap import add_src_to_path
except ImportError:  # pragma: no cover - supports pytest importing as scripts.preview_camera
    from scripts._bootstrap import add_src_to_path

add_src_to_path()

from ai_cctv.camera import VideoSource  # noqa: E402


WINDOW_NAME = "AI CCTV Camera Preview"


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def preview_source(raw_source: str) -> int | Path:
    if raw_source.isdigit():
        return int(raw_source)
    return Path(raw_source)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Preview a webcam/video source without YOLO, model weights, tracker, "
            "dataset, or CUDA."
        )
    )
    parser.add_argument("--source", default="0", help="Camera index or video file path. Default: 0")
    parser.add_argument("--width", type=positive_int, default=1280)
    parser.add_argument("--height", type=positive_int, default=720)
    parser.add_argument("--fps", type=positive_int, default=15)
    return parser


def draw_status(cv2: Any, frame: Any, *, fps: float) -> Any:
    height, width = frame.shape[:2]
    lines = [
        f"FPS: {fps:.1f}",
        f"Frame: {width}x{height}",
        "Press q to exit",
    ]
    for index, text in enumerate(lines):
        y = 32 + index * 28
        cv2.putText(frame, text, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(
            frame,
            text,
            (12, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
    return frame


def run_preview(*, source: int | Path, width: int, height: int, fps: int) -> int:
    try:
        import cv2  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        message = "opencv-python is required for camera preview. Install requirements.txt."
        raise RuntimeError(message) from exc

    try:
        capture = VideoSource(source, width=width, height=height, fps=fps).open()
    except RuntimeError as exc:
        if "Could not open video source" in str(exc):
            message = (
                f"Could not open camera/video source: {source}. "
                "Check the source index, camera connection, and OS camera permissions."
            )
            raise RuntimeError(message) from exc
        raise
    print(f"Previewing source={source} at requested {width}x{height}@{fps}. Press q to exit.")

    last_tick = perf_counter()
    display_fps = 0.0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError(f"Camera read failed for source: {source}")

            now = perf_counter()
            elapsed = now - last_tick
            last_tick = now
            if elapsed > 0:
                instant_fps = 1.0 / elapsed
                display_fps = (
                    instant_fps
                    if display_fps == 0.0
                    else (display_fps * 0.85) + (instant_fps * 0.15)
                )

            cv2.imshow(WINDOW_NAME, draw_status(cv2, frame, fps=display_fps))
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        capture.release()
        cv2.destroyAllWindows()
    return 0


def main() -> int:
    args = build_parser().parse_args()
    try:
        return run_preview(
            source=preview_source(args.source),
            width=args.width,
            height=args.height,
            fps=args.fps,
        )
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
