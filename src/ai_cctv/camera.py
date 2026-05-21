"""Webcam/video frame input utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def parse_video_source(source: int | str | Path) -> int | str:
    if isinstance(source, int):
        return source
    text = str(source)
    if text.isdecimal():
        return int(text)
    return str(Path(text))


class VideoSource:
    def __init__(self, source: int | str | Path, width: int | None = None, height: int | None = None, fps: int | None = None) -> None:
        self.source = parse_video_source(source)
        self.width = width
        self.height = height
        self.fps = fps
        self.capture: Any | None = None

    def open(self) -> None:
        try:
            import cv2  # type: ignore
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("OpenCV is required for webcam/video input. Install opencv-python first.") from exc
        self.capture = cv2.VideoCapture(self.source)
        if self.width:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if self.fps:
            self.capture.set(cv2.CAP_PROP_FPS, self.fps)
        if not self.capture.isOpened():
            raise RuntimeError(f"Unable to open video source: {self.source}")

    def read(self) -> tuple[bool, Any]:
        if self.capture is None:
            self.open()
        return self.capture.read()

    def release(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def __enter__(self) -> "VideoSource":
        self.open()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.release()


def record_webcam(
    out_path: Path,
    source: int | str = 0,
    width: int = 1280,
    height: int = 720,
    fps: int = 15,
    seconds: float | None = None,
) -> Path:
    try:
        import cv2  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("OpenCV is required for webcam recording. Install opencv-python first.") from exc

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    source_obj = VideoSource(source, width=width, height=height, fps=fps)
    frame_limit = int(seconds * fps) if seconds else None
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))
    count = 0
    try:
        source_obj.open()
        while True:
            ok, frame = source_obj.read()
            if not ok:
                break
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height))
            writer.write(frame)
            count += 1
            if frame_limit and count >= frame_limit:
                break
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        writer.release()
        source_obj.release()
        cv2.destroyAllWindows()
    return out_path
