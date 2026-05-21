"""Geometry helpers for bounding boxes, distances, proximity, and movement."""

from __future__ import annotations

from math import hypot

from .state import BBox, FrameSize, Point


def bbox_center(bbox: BBox | tuple[float, float, float, float]) -> Point:
    if isinstance(bbox, BBox):
        return bbox.center
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def distance(a: Point, b: Point) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def frame_diagonal(frame_size: FrameSize) -> float:
    width, height = frame_size
    return max(1.0, hypot(width, height))


def ratio_distance(a: Point, b: Point, frame_size: FrameSize) -> float:
    return distance(a, b) / frame_diagonal(frame_size)


def is_near(a: Point, b: Point, ratio: float, frame_size: FrameSize) -> bool:
    """Return True when two centers are within ratio of the frame diagonal."""

    return ratio_distance(a, b, frame_size) <= ratio


def moved_significantly(start: Point, current: Point, ratio: float, frame_size: FrameSize) -> bool:
    return ratio_distance(start, current, frame_size) >= ratio


def yolo_xywhn_from_bbox(bbox: BBox, image_size: FrameSize) -> tuple[float, float, float, float]:
    width, height = image_size
    width = max(1, width)
    height = max(1, height)
    cx, cy = bbox.center
    return (
        cx / width,
        cy / height,
        bbox.width / width,
        bbox.height / height,
    )
