"""Tracking adapter around Ultralytics YOLO track results."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .detector import PROJECT_CLASS_NAMES, ensure_model_available
from .event_detector import normalize_class_name
from .geometry import bbox_center
from .state import TrackedDetection


class YOLOTracker:
    """Convert YOLO tracking output into ``TrackedDetection`` objects."""

    def __init__(
        self,
        model_path: str | Path,
        *,
        tracker_type: str = "botsort",
        fallback_tracker: str = "bytetrack",
        conf: float = 0.35,
        iou: float = 0.5,
        imgsz: int = 640,
        device: str = "auto",
        target_classes: Iterable[str] = PROJECT_CLASS_NAMES,
        require_existing: bool = False,
    ) -> None:
        if require_existing:
            model_path = ensure_model_available(model_path, allow_builtin_name=False)
        self.model_path = str(model_path)
        self.tracker_type = tracker_type
        self.fallback_tracker = fallback_tracker
        self.conf = conf
        self.iou = iou
        self.imgsz = imgsz
        self.device = device
        self.target_classes = {normalize_class_name(name) for name in target_classes}
        try:
            from ultralytics import YOLO  # type: ignore
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("ultralytics is required for tracking. Install requirements.txt.") from exc
        self.model = YOLO(self.model_path)

    def track(self, frame: Any) -> list[TrackedDetection]:
        tracker_file = f"{self.tracker_type}.yaml" if not self.tracker_type.endswith(".yaml") else self.tracker_type
        try:
            results = self.model.track(
                source=frame,
                persist=True,
                tracker=tracker_file,
                conf=self.conf,
                iou=self.iou,
                imgsz=self.imgsz,
                device=None if self.device == "auto" else self.device,
                verbose=False,
            )
        except Exception:  # pragma: no cover - runtime fallback path
            fallback = (
                f"{self.fallback_tracker}.yaml"
                if not self.fallback_tracker.endswith(".yaml")
                else self.fallback_tracker
            )
            results = self.model.track(
                source=frame,
                persist=True,
                tracker=fallback,
                conf=self.conf,
                iou=self.iou,
                imgsz=self.imgsz,
                device=None if self.device == "auto" else self.device,
                verbose=False,
            )
        tracked: list[TrackedDetection] = []
        if not results:
            return tracked
        result = results[0]
        names = getattr(result, "names", getattr(self.model, "names", {})) or {}
        boxes = getattr(result, "boxes", None)
        if boxes is None or getattr(boxes, "id", None) is None:
            return tracked
        ids = boxes.id
        for index, box in enumerate(boxes):
            track_id_raw = ids[index]
            track_id = int(track_id_raw.item()) if hasattr(track_id_raw, "item") else int(track_id_raw)
            class_id = int(box.cls[0].item()) if hasattr(box.cls[0], "item") else int(box.cls[0])
            class_name = normalize_class_name(str(names.get(class_id, class_id)))
            if class_name not in self.target_classes:
                continue
            confidence = float(box.conf[0].item()) if hasattr(box.conf[0], "item") else float(box.conf[0])
            coords = box.xyxy[0].tolist() if hasattr(box.xyxy[0], "tolist") else list(box.xyxy[0])
            bbox = tuple(float(value) for value in coords)  # type: ignore[assignment]
            tracked.append(
                TrackedDetection(
                    track_id=track_id,
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    bbox=bbox,
                    center=bbox_center(bbox),
                )
            )
        return tracked
