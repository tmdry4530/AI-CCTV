"""Ultralytics YOLO detector adapter.

The adapter converts external model outputs to internal dataclasses. Imports of Ultralytics are lazy
so tests and ``--help`` commands work without model dependencies installed.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .event_detector import normalize_class_name
from .geometry import bbox_center
from .state import Detection

PROJECT_CLASS_NAMES = ("person", "bag", "laptop", "cell_phone")


def _looks_like_local_path(model_path: str | Path) -> bool:
    path = Path(model_path)
    return path.parent != Path(".") or str(model_path).startswith(("/", "~"))


def ensure_model_available(model_path: str | Path, *, allow_builtin_name: bool = True) -> Path | str:
    """Return model path/name or raise a clear missing-model error for local paths."""

    raw = str(model_path)
    path = Path(raw).expanduser()
    if path.exists():
        return path
    if allow_builtin_name and not _looks_like_local_path(raw):
        return raw
    raise FileNotFoundError(
        f"Model file not found: {path}. Provide a trained local model or use a built-in YOLO name "
        "such as yolo11n.pt for bootstrapping. Do not claim final demo readiness until a real "
        "models/best_demo.pt has been measured."
    )


class YOLODetector:
    """Thin wrapper around ``ultralytics.YOLO.predict``."""

    def __init__(
        self,
        model_path: str | Path,
        *,
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
        self.conf = conf
        self.iou = iou
        self.imgsz = imgsz
        self.device = device
        self.target_classes = {normalize_class_name(name) for name in target_classes}
        try:
            from ultralytics import YOLO  # type: ignore
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("ultralytics is required for detection. Install requirements.txt.") from exc
        self.model = YOLO(self.model_path)

    def detect(self, frame: Any) -> list[Detection]:
        results = self.model.predict(
            source=frame,
            conf=self.conf,
            iou=self.iou,
            imgsz=self.imgsz,
            device=None if self.device == "auto" else self.device,
            verbose=False,
        )
        detections: list[Detection] = []
        if not results:
            return detections
        result = results[0]
        names = getattr(result, "names", getattr(self.model, "names", {})) or {}
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return detections
        for box in boxes:
            class_id = int(box.cls[0].item()) if hasattr(box.cls[0], "item") else int(box.cls[0])
            raw_name = str(names.get(class_id, class_id))
            class_name = normalize_class_name(raw_name)
            if class_name not in self.target_classes:
                continue
            confidence = float(box.conf[0].item()) if hasattr(box.conf[0], "item") else float(box.conf[0])
            coords = box.xyxy[0].tolist() if hasattr(box.xyxy[0], "tolist") else list(box.xyxy[0])
            bbox = tuple(float(value) for value in coords)  # type: ignore[assignment]
            detections.append(
                Detection(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    bbox=bbox,
                    center=bbox_center(bbox),
                )
            )
        return detections
