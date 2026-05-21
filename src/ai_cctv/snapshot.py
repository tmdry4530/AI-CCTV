"""Event snapshot path generation and frame capture."""

from __future__ import annotations

from pathlib import Path

from .state import Event


def snapshot_path_for_event(snapshot_dir: str | Path, event: Event, suffix: str = ".jpg") -> Path:
    timestamp_ms = int(event.timestamp * 1000)
    name = f"{timestamp_ms}_{event.event_type.value}_obj{event.object_id}{suffix}"
    return Path(snapshot_dir) / name


def save_snapshot(frame: object, snapshot_dir: str | Path, event: Event) -> Path:
    try:
        import cv2  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("OpenCV is required for snapshot saving. Install opencv-python first.") from exc
    path = snapshot_path_for_event(snapshot_dir, event)
    path.parent.mkdir(parents=True, exist_ok=True)
    ok = cv2.imwrite(str(path), frame)
    if not ok:
        raise RuntimeError(f"Failed to write snapshot: {path}")
    return path
