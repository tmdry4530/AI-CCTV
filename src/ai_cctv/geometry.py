"""Geometry helpers shared by tracking and pure event logic.

This module intentionally has no OpenCV/YOLO imports so event rules can be unit-tested on mock
sequences without webcam, GPU, or model dependencies.
"""

from __future__ import annotations

from math import hypot
from typing import TypeAlias

BBox: TypeAlias = tuple[float, float, float, float]
Point: TypeAlias = tuple[float, float]
FrameSize: TypeAlias = tuple[int, int]


def bbox_center(bbox: BBox) -> Point:
    """Return the center point of an ``(x1, y1, x2, y2)`` bounding box."""

    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def bbox_width(bbox: BBox) -> float:
    """Return non-negative box width."""

    x1, _, x2, _ = bbox
    return max(0.0, x2 - x1)


def bbox_height(bbox: BBox) -> float:
    """Return non-negative box height."""

    _, y1, _, y2 = bbox
    return max(0.0, y2 - y1)


def bbox_area(bbox: BBox) -> float:
    """Return non-negative box area."""

    return bbox_width(bbox) * bbox_height(bbox)


def distance(a: Point, b: Point) -> float:
    """Euclidean distance between two points."""

    return hypot(a[0] - b[0], a[1] - b[1])


def frame_diagonal(frame_size: FrameSize) -> float:
    """Return the frame diagonal used for normalized distance thresholds."""

    width, height = frame_size
    return max(1.0, hypot(float(width), float(height)))


def normalized_distance(a: Point, b: Point, frame_size: FrameSize) -> float:
    """Distance as a ratio of frame diagonal."""

    return distance(a, b) / frame_diagonal(frame_size)


def is_near(a: Point, b: Point, frame_size: FrameSize, max_ratio: float) -> bool:
    """Return whether two centers are within ``max_ratio`` of the frame diagonal."""

    return normalized_distance(a, b, frame_size) <= max_ratio


def moved_significantly(
    previous: Point | None,
    current: Point,
    frame_size: FrameSize,
    min_ratio: float,
) -> bool:
    """Return whether movement exceeds the configured frame-normalized ratio."""

    if previous is None:
        return False
    return normalized_distance(previous, current, frame_size) >= min_ratio
