"""Runtime orchestration shared by webcam and video scripts."""

from __future__ import annotations

from pathlib import Path
from time import monotonic

from .camera import VideoSource
from .config import load_config, select_device
from .detector import ensure_model_available
from .event_detector import EventDetector
from .logger import CsvEventLogger
from .snapshot import save_snapshot
from .tracker import YOLOTracker
from .visualizer import draw_overlays


def validate_runtime_inputs(
    *,
    config_path: Path,
    source: int | str | Path | None = None,
    require_source_file: bool = False,
) -> None:
    cfg = load_config(config_path)
    ensure_model_available(cfg.model.path, allow_builtin_name=False)
    if require_source_file and source is not None:
        text = str(source)
        if not text.isdigit() and not Path(text).exists():
            raise FileNotFoundError(f"Video source not found: {source}")


def run_runtime(
    *,
    config_path: Path,
    source: int | str | Path | None = None,
    display: bool = True,
    save_snapshots: bool = True,
    max_frames: int | None = None,
    dry_run: bool = False,
) -> int:
    cfg = load_config(config_path)
    runtime_source = cfg.camera.source if source is None else source
    if dry_run:
        validate_runtime_inputs(
            config_path=config_path,
            source=runtime_source,
            require_source_file=not str(runtime_source).isdigit(),
        )
        print("Runtime dry-run OK")
        print(f"source={runtime_source}")
        print(f"model={cfg.model.path}")
        print(f"device={select_device(cfg.model.device)}")
        print(f"logs={cfg.paths.logs}")
        print(f"snapshots={cfg.paths.snapshots}")
        return 0

    try:
        import cv2  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("opencv-python is required for runtime display.") from exc

    ensure_model_available(cfg.model.path, allow_builtin_name=False)
    device = select_device(cfg.model.device)
    tracker = YOLOTracker(
        cfg.model.path,
        tracker_type=cfg.tracker.type,
        fallback_tracker=cfg.tracker.fallback,
        conf=cfg.model.conf_default,
        iou=cfg.model.iou,
        imgsz=cfg.model.imgsz,
        device=device,
        target_classes=cfg.classes.keys(),
        require_existing=True,
    )
    detector = EventDetector(thresholds=cfg.thresholds, frame_size=(cfg.camera.width, cfg.camera.height))
    logger = CsvEventLogger(cfg.paths.logs)
    capture = VideoSource(runtime_source, width=cfg.camera.width, height=cfg.camera.height, fps=cfg.camera.fps).open()
    start = monotonic()
    frame_index = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            timestamp = monotonic() - start
            tracks = tracker.track(frame)
            events = detector.update(tracks, timestamp=timestamp, frame_index=frame_index)
            if save_snapshots:
                for event in events:
                    save_snapshot(frame, cfg.paths.snapshots, event)
            logger.log_many(events)
            if display:
                output = draw_overlays(frame, tracks, events)
                cv2.imshow("AI CCTV", output)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            frame_index += 1
            if max_frames is not None and frame_index >= max_frames:
                break
    finally:
        capture.release()
        if display:
            cv2.destroyAllWindows()
    return 0
