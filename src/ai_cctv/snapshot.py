"""Event snapshot pathing and frame capture."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .state import Event


def snapshot_path(base_dir: Path | str, event: Event) -> Path:
    safe_type = event.event_type.replace("/", "_")
    frame = event.frame_index if event.frame_index is not None else "na"
    millis = int(event.timestamp * 1000)
    return Path(base_dir) / f"{millis}_{safe_type}_object{event.object_id}_frame{frame}.jpg"


def save_snapshot(frame: Any, base_dir: Path | str, event: Event) -> Path:
    try:
        import cv2  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("opencv-python is required to save snapshots.") from exc
    path = snapshot_path(base_dir, event)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), frame):
        raise RuntimeError(f"Failed to write snapshot: {path}")
    event.snapshot_path = path
    return path
