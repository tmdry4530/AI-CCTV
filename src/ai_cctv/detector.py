"""YOLO detector wrapper that converts model output into internal dataclasses."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from .config import select_device
from .state import BBox, Detection, normalize_class_name

PROJECT_CLASS_IDS = {"person": 0, "bag": 1, "laptop": 2, "cell_phone": 3}

COCO_PROJECT_ALIASES = {
    "person": "person",
    "backpack": "bag",
    "handbag": "bag",
    "suitcase": "bag",
    "luggage": "bag",
    "briefcase": "bag",
    "bag": "bag",
    "laptop": "laptop",
    "cell phone": "cell_phone",
    "cell_phone": "cell_phone",
    "phone": "cell_phone",
}


class YoloDetector:
    def __init__(
        self,
        model_path: str | Path,
        device: str = "auto",
        imgsz: int = 640,
        conf: float = 0.35,
        iou: float = 0.5,
        target_classes: Iterable[str] | None = None,
    ) -> None:
        self.model_path = Path(model_path)
        self.device = select_device(device)
        self.imgsz = imgsz
        self.conf = conf
        self.iou = iou
        self.target_classes = set(target_classes or {"person", "bag", "laptop", "cell_phone"})
        try:
            from ultralytics import YOLO  # type: ignore
        except Exception as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("Ultralytics is required for YOLO detection. Install ultralytics first.") from exc
        self.model = YOLO(str(self.model_path))

    def predict(self, frame: Any) -> list[Detection]:
        results = self.model.predict(
            source=frame,
            imgsz=self.imgsz,
            conf=self.conf,
            iou=self.iou,
            device=self.device,
            verbose=False,
        )
        if not results:
            return []
        return detections_from_ultralytics_result(results[0], self.target_classes)


def detections_from_ultralytics_result(
    result: Any,
    target_classes: Iterable[str] | None = None,
) -> list[Detection]:
    targets = set(target_classes or {"person", "bag", "laptop", "cell_phone"})
    names = getattr(result, "names", {}) or {}
    detections: list[Detection] = []
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return detections
    for box in boxes:
        raw_class_id = int(_to_scalar(getattr(box, "cls", 0)))
        raw_name = names.get(raw_class_id, str(raw_class_id)) if isinstance(names, dict) else str(raw_class_id)
        class_name = normalize_class_name(COCO_PROJECT_ALIASES.get(str(raw_name), str(raw_name)))
        if class_name not in targets:
            continue
        class_id = PROJECT_CLASS_IDS.get(class_name, raw_class_id)
        xyxy = _flatten4(getattr(box, "xyxy", None))
        if xyxy is None:
            continue
        bbox = BBox.from_iterable(xyxy)
        detections.append(
            Detection(
                class_id=class_id,
                class_name=class_name,
                confidence=float(_to_scalar(getattr(box, "conf", 0.0))),
                bbox=bbox,
                center=bbox.center,
            )
        )
    return detections


def _to_scalar(value: Any) -> float:
    if hasattr(value, "detach"):
        value = value.detach().cpu()
    if hasattr(value, "item"):
        return float(value.item())
    if isinstance(value, (list, tuple)):
        return _to_scalar(value[0]) if value else 0.0
    return float(value)


def _flatten4(value: Any) -> tuple[float, float, float, float] | None:
    if value is None:
        return None
    if hasattr(value, "detach"):
        value = value.detach().cpu()
    if hasattr(value, "tolist"):
        value = value.tolist()
    while isinstance(value, (list, tuple)) and len(value) == 1 and isinstance(value[0], (list, tuple)):
        value = value[0]
    if not isinstance(value, (list, tuple)) or len(value) < 4:
        return None
    return (float(value[0]), float(value[1]), float(value[2]), float(value[3]))
