"""Configuration loading and cross-platform device selection."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .state import EventThresholds


@dataclass(slots=True)
class CameraConfig:
    source: int | str = 0
    width: int = 1280
    height: int = 720
    fps: int = 15


@dataclass(slots=True)
class ModelConfig:
    path: Path = Path("models") / "best_demo.pt"
    device: str = "auto"
    imgsz: int = 640
    conf_default: float = 0.35
    iou: float = 0.5


@dataclass(slots=True)
class TrackerConfig:
    type: str = "botsort"
    fallback: str = "bytetrack"


@dataclass(slots=True)
class PathConfig:
    logs: Path = Path("data") / "logs" / "events.csv"
    snapshots: Path = Path("data") / "snapshots"


@dataclass(slots=True)
class AppConfig:
    camera: CameraConfig = field(default_factory=CameraConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    classes: dict[str, int] = field(
        default_factory=lambda: {"person": 0, "bag": 1, "laptop": 2, "cell_phone": 3}
    )
    thresholds: EventThresholds = field(default_factory=EventThresholds)
    tracker: TrackerConfig = field(default_factory=TrackerConfig)
    paths: PathConfig = field(default_factory=PathConfig)


def load_config(path: Path | str) -> AppConfig:
    """Load YAML config into typed dataclasses."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on user environment
        raise RuntimeError("PyYAML is required to read config files. Install requirements.txt.") from exc

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return config_from_mapping(data)


def config_from_mapping(data: dict[str, Any]) -> AppConfig:
    camera_data = data.get("camera", {}) or {}
    model_data = data.get("model", {}) or {}
    tracker_data = data.get("tracker", {}) or {}
    path_data = data.get("paths", {}) or {}
    thresholds_data = data.get("thresholds", {}) or {}

    threshold_keys = {field.name for field in EventThresholds.__dataclass_fields__.values()}
    clean_thresholds = {k: v for k, v in thresholds_data.items() if k in threshold_keys}

    return AppConfig(
        camera=CameraConfig(**camera_data),
        model=ModelConfig(
            path=Path(model_data.get("path", Path("models") / "best_demo.pt")),
            device=str(model_data.get("device", "auto")),
            imgsz=int(model_data.get("imgsz", 640)),
            conf_default=float(model_data.get("conf_default", 0.35)),
            iou=float(model_data.get("iou", 0.5)),
        ),
        classes={str(k): int(v) for k, v in (data.get("classes", {}) or {}).items()}
        or {"person": 0, "bag": 1, "laptop": 2, "cell_phone": 3},
        thresholds=EventThresholds(**clean_thresholds),
        tracker=TrackerConfig(**tracker_data),
        paths=PathConfig(
            logs=Path(path_data.get("logs", Path("data") / "logs" / "events.csv")),
            snapshots=Path(path_data.get("snapshots", Path("data") / "snapshots")),
        ),
    )


def select_device(preferred: str = "auto") -> str:
    """Return cuda, mps, or cpu without requiring CUDA for runtime/tests."""

    normalized = preferred.strip().lower()
    if normalized not in {"auto", "cuda", "0", "mps", "cpu"}:
        return preferred
    try:
        import torch  # type: ignore
    except ImportError:
        return "cpu" if normalized == "auto" else normalized

    if normalized in {"cuda", "0"}:
        return "cuda" if torch.cuda.is_available() else "cpu"
    if normalized == "mps":
        mps = getattr(torch.backends, "mps", None)
        return "mps" if mps and mps.is_available() else "cpu"
    if normalized == "cpu":
        return "cpu"
    if torch.cuda.is_available():
        return "cuda"
    mps = getattr(torch.backends, "mps", None)
    if mps and mps.is_available():
        return "mps"
    return "cpu"


def select_training_device(preferred: str = "auto") -> str:
    """Return an Ultralytics-friendly training device string."""

    normalized = preferred.strip().lower()
    if normalized in {"cuda", "0"}:
        return "0"
    selected = select_device(preferred)
    return "0" if selected == "cuda" and preferred == "auto" else selected
