"""Configuration loading and device selection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .state import EventDetectorConfig


@dataclass(frozen=True)
class CameraConfig:
    source: int | str = 0
    width: int = 1280
    height: int = 720
    fps: int = 15


@dataclass(frozen=True)
class ModelConfig:
    path: Path = Path("models") / "best_demo.pt"
    device: str = "auto"
    imgsz: int = 640
    conf_default: float = 0.35
    iou: float = 0.5


@dataclass(frozen=True)
class TrackerConfig:
    type: str = "botsort"
    fallback: str = "bytetrack"


@dataclass(frozen=True)
class PathsConfig:
    logs: Path = Path("data") / "logs" / "events.csv"
    snapshots: Path = Path("data") / "snapshots"
    sample_video: Path = Path("data") / "samples" / "final_demo.mp4"


@dataclass(frozen=True)
class AppConfig:
    camera: CameraConfig
    model: ModelConfig
    classes: dict[str, int]
    thresholds: EventDetectorConfig
    tracker: TrackerConfig
    paths: PathsConfig


DEFAULT_CLASSES = {"person": 0, "bag": 1, "laptop": 2, "cell_phone": 3}


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    data = _load_yaml(config_path)
    camera_raw = data.get("camera", {})
    model_raw = data.get("model", {})
    tracker_raw = data.get("tracker", {})
    paths_raw = data.get("paths", {})
    thresholds_raw = data.get("thresholds", {})
    return AppConfig(
        camera=CameraConfig(
            source=_parse_source(camera_raw.get("source", 0)),
            width=int(camera_raw.get("width", 1280)),
            height=int(camera_raw.get("height", 720)),
            fps=int(camera_raw.get("fps", 15)),
        ),
        model=ModelConfig(
            path=Path(model_raw.get("path", Path("models") / "best_demo.pt")),
            device=str(model_raw.get("device", "auto")),
            imgsz=int(model_raw.get("imgsz", 640)),
            conf_default=float(model_raw.get("conf_default", 0.35)),
            iou=float(model_raw.get("iou", 0.5)),
        ),
        classes={str(k): int(v) for k, v in data.get("classes", DEFAULT_CLASSES).items()},
        thresholds=EventDetectorConfig(**{k: v for k, v in thresholds_raw.items() if k in EventDetectorConfig.__dataclass_fields__}),
        tracker=TrackerConfig(
            type=str(tracker_raw.get("type", "botsort")),
            fallback=str(tracker_raw.get("fallback", "bytetrack")),
        ),
        paths=PathsConfig(
            logs=Path(paths_raw.get("logs", Path("data") / "logs" / "events.csv")),
            snapshots=Path(paths_raw.get("snapshots", Path("data") / "snapshots")),
            sample_video=Path(paths_raw.get("sample_video", Path("data") / "samples" / "final_demo.mp4")),
        ),
    )


def select_device(preferred: str = "auto") -> str:
    preferred = (preferred or "auto").lower()
    if preferred != "auto":
        return preferred
    try:
        import torch  # type: ignore
    except Exception:
        return "cpu"
    try:
        if torch.cuda.is_available():
            return "cuda"
        mps = getattr(torch.backends, "mps", None)
        if mps is not None and mps.is_available():
            return "mps"
    except Exception:
        return "cpu"
    return "cpu"


def _parse_source(value: Any) -> int | str:
    if isinstance(value, int):
        return value
    text = str(value)
    if text.isdecimal():
        return int(text)
    return text


def _load_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"Config root must be a mapping: {path}")
        return loaded
    except ModuleNotFoundError:
        return _minimal_yaml_mapping(text)


def _minimal_yaml_mapping(text: str) -> dict[str, Any]:
    """Tiny fallback parser for the simple one-level nested YAML used here."""

    root: dict[str, Any] = {}
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        is_nested = raw_line.startswith(" ")
        if not is_nested and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                root[key] = {}
                current = root[key]
            else:
                root[key] = _parse_scalar(value)
                current = None
            continue
        if is_nested and current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = _parse_scalar(value.strip())
    return root


def _parse_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"\'')
