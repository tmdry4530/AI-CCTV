"""Typed state models for detector output, tracking state, and events."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .geometry import BBox, Point, bbox_center

ObjectStatus = Literal["visible", "owned", "abandoned", "missing", "theft_suspected"]
EventType = Literal[
    "owner_registered",
    "abandoned_object",
    "suspicious_approach",
    "object_removed",
    "theft_suspected",
    "object_returned",
]


@dataclass(slots=True)
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox: BBox
    center: Point | None = None

    def __post_init__(self) -> None:
        if self.center is None:
            self.center = bbox_center(self.bbox)


@dataclass(slots=True)
class TrackedDetection(Detection):
    track_id: int = -1


@dataclass(slots=True)
class TrackedPerson:
    track_id: int
    bbox: BBox
    center: Point
    first_seen: float
    last_seen: float
    visible: bool = True


@dataclass(slots=True)
class TrackedObject:
    track_id: int
    class_name: str
    bbox: BBox
    center: Point
    first_seen: float
    last_seen: float
    owner_id: int | None = None
    status: ObjectStatus = "visible"
    last_non_owner_near_id: int | None = None
    last_non_owner_near_time: float | None = None
    last_known_position: Point | None = None
    abandoned_position: Point | None = None
    visible: bool = True
    theft_suspected: bool = False


@dataclass(slots=True)
class Event:
    timestamp: float
    event_type: EventType
    object_id: int
    object_class: str
    owner_id: int | None = None
    related_person_id: int | None = None
    confidence: float = 1.0
    snapshot_path: Path | None = None
    frame_index: int | None = None
    message: str = ""

    def to_row(self) -> dict[str, str | int | float | None]:
        return {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "object_id": self.object_id,
            "object_class": self.object_class,
            "owner_id": self.owner_id,
            "related_person_id": self.related_person_id,
            "confidence": self.confidence,
            "snapshot_path": str(self.snapshot_path) if self.snapshot_path else "",
            "frame_index": self.frame_index if self.frame_index is not None else "",
            "message": self.message,
        }


@dataclass(slots=True)
class EventThresholds:
    owner_distance_ratio: float = 0.15
    owner_min_seconds: float = 3.0
    abandoned_min_seconds: float = 5.0
    suspicious_min_seconds: float = 1.5
    missing_grace_seconds: float = 2.0
    moved_distance_ratio: float = 0.20
    event_cooldown_seconds: float = 3.0
    recent_non_owner_seconds: float = 10.0


@dataclass(slots=True)
class RuntimeStats:
    frames: int = 0
    events: int = 0
    fps_samples: list[float] = field(default_factory=list)
