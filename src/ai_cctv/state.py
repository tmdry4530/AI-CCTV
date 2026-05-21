"""Typed state models shared by detection, tracking, events, and logging.

This module deliberately has no OpenCV/Ultralytics dependency so event logic can be
unit-tested without a webcam, model weights, or GPU.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional

Point = tuple[float, float]
FrameSize = tuple[int, int]  # width, height

PERSON_CLASS = "person"
OBJECT_CLASSES = frozenset({"bag", "laptop", "cell_phone", "wallet"})
PROJECT_CLASSES = ("person", "bag", "laptop", "cell_phone")


class EventType(str, Enum):
    OWNER_REGISTERED = "owner_registered"
    ABANDONED_OBJECT = "abandoned_object"
    SUSPICIOUS_APPROACH = "suspicious_approach"
    THEFT_SUSPECTED = "theft_suspected"


class ObjectStatus(str, Enum):
    UNOWNED = "unowned"
    OWNED = "owned"
    ABANDONED = "abandoned"
    THEFT_SUSPECTED = "theft_suspected"


@dataclass(frozen=True)
class BBox:
    """Axis-aligned bounding box in pixel coordinates."""

    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def center(self) -> Point:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    def as_xyxy(self) -> tuple[float, float, float, float]:
        return (self.x1, self.y1, self.x2, self.y2)

    @classmethod
    def from_iterable(cls, values: Iterable[float]) -> "BBox":
        x1, y1, x2, y2 = values
        return cls(float(x1), float(y1), float(x2), float(y2))


@dataclass(frozen=True)
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox: BBox
    center: Point | None = None

    def __post_init__(self) -> None:
        if self.center is None:
            object.__setattr__(self, "center", self.bbox.center)


@dataclass(frozen=True)
class TrackedDetection(Detection):
    track_id: int = -1


@dataclass
class TrackedPerson:
    track_id: int
    bbox: BBox
    center: Point
    first_seen: float
    last_seen: float
    visible: bool = True
    confidence: float = 0.0


@dataclass
class TrackedObject:
    track_id: int
    class_id: int
    class_name: str
    bbox: BBox
    center: Point
    first_seen: float
    last_seen: float
    confidence: float = 0.0
    owner_id: int | None = None
    status: ObjectStatus = ObjectStatus.UNOWNED
    last_non_owner_near_id: int | None = None
    last_non_owner_near_time: float | None = None
    last_known_position: Point | None = None
    abandoned_reference_position: Point | None = None
    abandoned_since: float | None = None
    missing_since: float | None = None
    visible: bool = True


@dataclass(frozen=True)
class Event:
    timestamp: float
    event_type: EventType
    object_id: int
    object_class: str
    owner_id: int | None = None
    related_person_id: int | None = None
    confidence: float = 1.0
    snapshot_path: Path | None = None
    message: str = ""


@dataclass(frozen=True)
class EventDetectorConfig:
    owner_distance_ratio: float = 0.15
    owner_min_seconds: float = 3.0
    abandoned_min_seconds: float = 5.0
    suspicious_min_seconds: float = 1.5
    missing_grace_seconds: float = 2.0
    moved_distance_ratio: float = 0.20
    event_cooldown_seconds: float = 3.0
    recent_non_owner_seconds: float = 8.0
    object_classes: tuple[str, ...] = field(default_factory=lambda: PROJECT_CLASSES[1:])


def is_person(class_name: str) -> bool:
    return normalize_class_name(class_name) == PERSON_CLASS


def is_object(class_name: str, object_classes: Iterable[str] | None = None) -> bool:
    allowed = set(object_classes or OBJECT_CLASSES)
    return normalize_class_name(class_name) in allowed


def normalize_class_name(class_name: str) -> str:
    """Normalize common detector names into project class names."""

    name = class_name.strip().lower().replace("-", "_")
    aliases = {
        "cell phone": "cell_phone",
        "mobile_phone": "cell_phone",
        "mobile phone": "cell_phone",
        "phone": "cell_phone",
        "backpack": "bag",
        "handbag": "bag",
        "suitcase": "bag",
        "luggage": "bag",
        "briefcase": "bag",
    }
    return aliases.get(name, name)
