"""Webcam/video input helpers with lazy OpenCV imports."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def parse_source(source: str | int | Path) -> int | str:
    if isinstance(source, int):
        return source
    text = str(source)
    if text.isdigit():
        return int(text)
    return text


@dataclass(slots=True)
class VideoSource:
    source: int | str | Path
    width: int | None = None
    height: int | None = None
    fps: int | None = None
    _capture: Any | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._capture = None

    def open(self) -> "VideoSource":
        try:
            import cv2  # type: ignore
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("opencv-python is required for webcam/video input.") from exc
        parsed = parse_source(self.source)
        if isinstance(parsed, str) and not Path(parsed).exists():
            raise FileNotFoundError(f"Video source not found: {parsed}")
        capture = cv2.VideoCapture(parsed)
        if not capture.isOpened():
            raise RuntimeError(f"Could not open video source: {self.source}")
        if isinstance(parsed, int):
            if self.width:
                capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            if self.height:
                capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            if self.fps:
                capture.set(cv2.CAP_PROP_FPS, self.fps)
        self._capture = capture
        return self

    def read(self) -> tuple[bool, Any]:
        if self._capture is None:
            raise RuntimeError("VideoSource must be opened before read().")
        return self._capture.read()

    def release(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    @property
    def is_open(self) -> bool:
        return self._capture is not None
