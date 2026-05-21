"""OpenCV overlay rendering for tracked objects and events."""

from __future__ import annotations

from typing import Any

from .state import Event, TrackedDetection

COLORS = {
    "person": (80, 220, 80),
    "bag": (255, 180, 60),
    "laptop": (120, 180, 255),
    "cell_phone": (200, 120, 255),
}
EVENT_COLORS = {
    "owner_registered": (255, 255, 0),
    "abandoned_object": (0, 165, 255),
    "suspicious_approach": (0, 255, 255),
    "object_removed": (80, 80, 255),
    "theft_suspected": (0, 0, 255),
    "object_returned": (80, 255, 80),
}


def draw_overlays(frame: Any, tracks: list[TrackedDetection], events: list[Event]) -> Any:
    try:
        import cv2  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("opencv-python is required for visualization.") from exc
    output = frame.copy()
    for track in tracks:
        x1, y1, x2, y2 = [int(v) for v in track.bbox]
        color = COLORS.get(track.class_name, (220, 220, 220))
        cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
        label = f"{track.class_name} #{track.track_id} {track.confidence:.2f}"
        cv2.putText(output, label, (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
    y = 28
    for event in events[-4:]:
        color = EVENT_COLORS.get(event.event_type, (255, 255, 255))
        text = f"{event.event_type} object={event.object_id} related={event.related_person_id}"
        cv2.putText(output, text, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        y += 28
    return output
