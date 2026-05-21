# AGENTS.md

## Project

This repository implements a webcam-based AI CCTV system for abandoned object and theft-suspected event detection.

## Stack

- Python 3.11+
- OpenCV
- Ultralytics YOLO
- pytest
- Streamlit
- Windows RTX 4070 SUPER for training
- MacBook for final demo

## Architecture rules

- Do not implement everything in one file.
- Keep detection/tracking separate from event logic.
- Event logic must be testable without webcam, OpenCV, YOLO, or GPU.
- `event_detector.py` must not import `cv2` or `ultralytics`.
- Use dataclasses or typed models for internal state.
- Use `pathlib.Path` for all filesystem paths.
- Do not hardcode Windows or macOS path separators.
- Do not require CUDA for runtime or tests.
- Training may use CUDA when available.
- MacBook demo must work without CUDA.

## Required modules

- `camera.py`: webcam/video frame input
- `detector.py`: YOLO detection wrapper
- `tracker.py`: tracking wrapper
- `geometry.py`: bbox center, distance, movement helpers
- `state.py`: tracked people, objects, and events
- `event_detector.py`: owner registration, abandoned object, suspicious approach, theft_suspected logic
- `logger.py`: CSV/SQLite event logging
- `snapshot.py`: event frame capture
- `visualizer.py`: OpenCV overlay rendering
- `app.py`: Streamlit dashboard

## Safety rules

- Do not implement face recognition.
- Do not identify real people.
- Do not claim actual theft.
- Use `theft_suspected`, never `theft_detected`.
- Do not upload videos, snapshots, or labels to cloud by default.
- Do not store private keys or API keys in the repo.

## Model rules

- Start with pretrained YOLO baseline.
- Use public datasets only for detector bootstrapping.
- Use MacBook-captured data for demo-domain adaptation.
- Use auto-labeling to reduce manual labeling.
- Validation and test labels must be human-reviewed.
- Final model is selected by MacBook demo performance, not only mAP.

## Testing

Run before completion:

```bash
python -m pytest
python -m compileall src scripts tools
python scripts/check_dataset.py --help
python scripts/train_yolo.py --help
python scripts/benchmark_model.py --help
```

## Required behavior

- Owner is registered only after a person stays near an object for the configured duration.
- Abandoned object is detected only when owner disappears and object remains visible.
- Theft suspected is detected only when a non-owner was recently near the object and the object disappears or moves significantly.
- Temporary occlusion must not immediately trigger object removal.
- Passing by must not trigger theft_suspected.

## Completion report

Every final report must include:

1. changed files
2. implemented features
3. tests run
4. failed or skipped checks
5. model training commands
6. MacBook demo instructions
7. remaining risks
