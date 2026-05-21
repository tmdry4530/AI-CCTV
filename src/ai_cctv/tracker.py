"""YOLO tracking wrapper that returns stable internal tracked detections."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .config import select_device
from .detector import COCO_PROJECT_ALIASES, PROJECT_CLASS_IDS, _flatten4, _to_scalar
from .state import BBox, TrackedDetection, normalize_class_name


class YoloTracker:
    def __init__(
        self,
        model_path: str | Path,
        device: str = "auto",
        imgsz: int = 640,
        conf: float = 0.35,
        iou: float = 0.5,
        tracker_type: str = "botsort",
        fallback_tracker: str = "bytetrack",
        target_classes: Iterable[str] | None = None,
    ) -> None:
        self.model_path = Path(model_path)
        self.device = select_device(device)
        self.imgsz = imgsz
        self.conf = conf
        self.iou = iou
        self.tracker_type = tracker_type
        self.fallback_tracker = fallback_tracker
        self.target_classes = set(target_classes or {"person", "bag", "laptop", "cell_phone"})
        try:
            from ultralytics import YOLO  # type: ignore
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("Ultralytics is required for YOLO tracking. Install ultralytics first.") from exc
        self.model = YOLO(str(self.model_path))

    def track(self, frame: Any) -> list[TrackedDetection]:
        try:
            results = self.model.track(
                source=frame,
                persist=True,
                tracker=f"{self.tracker_type}.yaml",
                imgsz=self.imgsz,
                conf=self.conf,
                iou=self.iou,
                device=self.device,
                verbose=False,
            )
        except Exception:  # pragma: no cover - depends on tracker availability
            results = self.model.track(
                source=frame,
                persist=True,
                tracker=f"{self.fallback_tracker}.yaml",
                imgsz=self.imgsz,
                conf=self.conf,
                iou=self.iou,
                device=self.device,
                verbose=False,
            )
        if not results:
            return []
        return tracked_detections_from_ultralytics_result(results[0], self.target_classes)


def tracked_detections_from_ultralytics_result(
    result: Any,
    target_classes: Iterable[str] | None = None,
) -> list[TrackedDetection]:
    targets = set(target_classes or {"person", "bag", "laptop", "cell_phone"})
    names = getattr(result, "names", {}) or {}
    tracked: list[TrackedDetection] = []
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return tracked
    for idx, box in enumerate(boxes):
        raw_class_id = int(_to_scalar(getattr(box, "cls", 0)))
        raw_name = names.get(raw_class_id, str(raw_class_id)) if isinstance(names, dict) else str(raw_class_id)
        class_name = normalize_class_name(COCO_PROJECT_ALIASES.get(str(raw_name), str(raw_name)))
        if class_name not in targets:
            continue
        class_id = PROJECT_CLASS_IDS.get(class_name, raw_class_id)
        xyxy = _flatten4(getattr(box, "xyxy", None))
        if xyxy is None:
            continue
        track_raw = getattr(box, "id", None)
        track_id = -(idx + 1) if track_raw is None else int(_to_scalar(track_raw))
        bbox = BBox.from_iterable(xyxy)
        tracked.append(
            TrackedDetection(
                track_id=track_id,
                class_id=class_id,
                class_name=class_name,
                confidence=float(_to_scalar(getattr(box, "conf", 0.0))),
                bbox=bbox,
                center=bbox.center,
            )
        )
    return tracked
