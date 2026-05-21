"""Runtime loop connecting camera, tracker, event detector, logging, snapshots, and overlay."""

from __future__ import annotations

import time
from pathlib import Path

from .camera import VideoSource
from .config import AppConfig, load_config
from .event_detector import EventDetector
from .logger import CSVEventLogger
from .snapshot import save_snapshot
from .state import Event, TrackedDetection
from .tracker import YoloTracker
from .visualizer import draw_overlay


def run_pipeline(
    config: str | Path | AppConfig,
    source_override: str | int | Path | None = None,
    dry_run: bool = False,
    show: bool = True,
    max_frames: int | None = None,
    fallback_video: str | Path | None = None,
) -> int:
    cfg = load_config(config) if not isinstance(config, AppConfig) else config
    source = source_override if source_override is not None else cfg.camera.source
    if dry_run:
        print(f"config ok: model={cfg.model.path} source={source} logs={cfg.paths.logs}")
        return 0

    try:
        return _run_opened_source(cfg, source, show=show, max_frames=max_frames)
    except RuntimeError as exc:
        fallback = Path(fallback_video) if fallback_video else cfg.paths.sample_video
        if fallback and Path(fallback).exists() and str(source) != str(fallback):
            print(f"Primary source failed ({exc}); trying fallback video {fallback}")
            return _run_opened_source(cfg, fallback, show=show, max_frames=max_frames)
        raise


def _run_opened_source(cfg: AppConfig, source: str | int | Path, show: bool, max_frames: int | None) -> int:
    try:
        import cv2  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("OpenCV is required for runtime. Install opencv-python first.") from exc

    tracker = YoloTracker(
        cfg.model.path,
        device=cfg.model.device,
        imgsz=cfg.model.imgsz,
        conf=cfg.model.conf_default,
        iou=cfg.model.iou,
        tracker_type=cfg.tracker.type,
        fallback_tracker=cfg.tracker.fallback,
        target_classes=cfg.classes.keys(),
    )
    event_detector = EventDetector(cfg.thresholds)
    logger = CSVEventLogger(cfg.paths.logs)
    frame_count = 0
    started = time.monotonic()
    with VideoSource(source, width=cfg.camera.width, height=cfg.camera.height, fps=cfg.camera.fps) as cap:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame_count += 1
            timestamp = time.monotonic() - started
            tracked = tracker.track(frame)
            frame_size = (int(frame.shape[1]), int(frame.shape[0]))
            events = event_detector.update(tracked, timestamp=timestamp, frame_size=frame_size, frame_index=frame_count)
            events = _attach_snapshots(frame, cfg.paths.snapshots, events)
            logger.log_many(events)
            if show:
                draw_overlay(frame, tracked, events)
                cv2.imshow("Webcam AI CCTV", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            if max_frames is not None and frame_count >= max_frames:
                break
    if show:
        cv2.destroyAllWindows()
    return 0


def _attach_snapshots(frame: object, snapshot_dir: Path, events: list[Event]) -> list[Event]:
    updated: list[Event] = []
    for event in events:
        path = save_snapshot(frame, snapshot_dir, event)
        updated.append(
            Event(
                timestamp=event.timestamp,
                event_type=event.event_type,
                object_id=event.object_id,
                object_class=event.object_class,
                owner_id=event.owner_id,
                related_person_id=event.related_person_id,
                confidence=event.confidence,
                snapshot_path=path,
                message=event.message,
            )
        )
    return updated
