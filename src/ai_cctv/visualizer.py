"""OpenCV overlay rendering for detections and events."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .state import Event, TrackedDetection


COLORS = {
    "person": (80, 220, 80),
    "bag": (60, 160, 255),
    "laptop": (255, 180, 80),
    "cell_phone": (255, 80, 180),
}


def draw_overlay(frame: Any, detections: Iterable[TrackedDetection], events: Iterable[Event] = ()) -> Any:
    try:
        import cv2  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("OpenCV is required for visualization. Install opencv-python first.") from exc
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det.bbox.as_xyxy()]
        color = COLORS.get(det.class_name, (230, 230, 230))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"{det.class_name}#{det.track_id} {det.confidence:.2f}"
        cv2.putText(frame, label, (x1, max(20, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    y = 28
    for event in events:
        text = f"{event.event_type.value} obj={event.object_id} person={event.related_person_id or '-'}"
        cv2.putText(frame, text, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        y += 28
    return frame
