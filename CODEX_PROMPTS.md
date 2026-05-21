# CODEX_PROMPTS.md

## 1. 초기 문서 검토 프롬프트

```text
Read the document pack in this repository:
- AGENTS.md
- PRD.md
- SPEC.md
- TECH_SPEC.md
- TEST_PLAN.md
- DATASET_PLAN.md
- AUTO_LABELING_PLAN.md
- MODEL_PLAN.md
- EVAL_PLAN.md
- PLATFORM_MATRIX.md
- MODEL_EXPERIMENTS.md

Summarize the implementation scope and identify any contradictions or missing requirements.
Do not edit files yet.
```

## 2. Phase 1: 순수 이벤트 로직

```text
/prompts:executor
Implement Phase 1 only.

Goal:
Create pure Python event logic that does not depend on OpenCV, YOLO, webcam, or GPU.

Implement:
- src/ai_cctv/geometry.py
- src/ai_cctv/state.py
- src/ai_cctv/event_detector.py
- tests/test_geometry.py
- tests/test_owner_assignment.py
- tests/test_abandoned_detection.py
- tests/test_theft_suspected.py

Rules:
- Use dataclasses.
- Use deterministic timestamps or frame indexes in tests.
- No real time sleep in tests.
- event_detector.py must not import cv2 or ultralytics.

Verification:
- python -m pytest
- python -m compileall src

Return:
1. changed files
2. event state model summary
3. tests run
4. remaining risks
```

## 3. Phase 2: Detector/Tracker Wrapper

```text
/prompts:executor
Implement Phase 2 only.

Goal:
Add detector and tracker wrappers while keeping them replaceable and mockable.

Implement:
- src/ai_cctv/detector.py
- src/ai_cctv/tracker.py
- src/ai_cctv/config.py

Rules:
- Use Ultralytics YOLO if installed.
- Provide clear error message if dependency or model is missing.
- Do not make event_detector depend directly on YOLO result objects.
- Convert detection outputs into internal dataclasses.
- Support cuda, mps, cpu device selection.

Verification:
- python -m pytest
- python -m compileall src
```

## 4. Phase 3: Webcam/Video Runtime

```text
/prompts:executor
Implement Phase 3 only.

Goal:
Add runtime scripts for webcam and video files.

Implement:
- src/ai_cctv/camera.py
- src/ai_cctv/visualizer.py
- scripts/run_webcam.py
- scripts/run_video.py

Rules:
- webcam index default: 0
- support --source for video file
- support --config
- support --model path
- pressing q exits cleanly
- no cloud upload

Verification:
- python -m compileall src scripts
- python scripts/run_webcam.py --help
- python scripts/run_video.py --help
```

## 5. Phase 4: Auto-labeling Pipeline

```text
/prompts:executor
Implement Phase 4 only.

Goal:
Add an auto-labeling workflow to minimize manual labeling.

Create:
- scripts/record_webcam.py
- scripts/extract_frames.py
- scripts/auto_label_yolo.py
- tools/label_review_app.py
- scripts/split_dataset.py
- scripts/check_dataset.py

Requirements:
- Must work on macOS and Windows.
- Use pathlib.
- Do not require CUDA.
- The review UI should let me mark labels/images as accepted/rejected.
- Validation and test sets must be human-reviewed only.
- Split dataset by source video to avoid near-duplicate leakage.

Verification:
- python -m compileall scripts tools
- python scripts/extract_frames.py --help
- python scripts/check_dataset.py --help
```

## 6. Phase 5: Training/Evaluation Pipeline

```text
/prompts:executor
Implement Phase 5 only.

Goal:
Add YOLO training, validation, and model benchmark scripts.

Create:
- scripts/train_yolo.py
- scripts/validate_yolo.py
- scripts/benchmark_model.py

Requirements:
- Windows RTX 4070 SUPER training path documented.
- MacBook benchmark path documented.
- Support device auto/cuda/mps/cpu.
- Store experiment results in MODEL_EXPERIMENTS.md or data/logs.

Verification:
- python scripts/train_yolo.py --help
- python scripts/validate_yolo.py --help
- python scripts/benchmark_model.py --help
```

## 7. Phase 6: Logging/Dashboard

```text
/prompts:executor
Implement Phase 6 only.

Goal:
Add event logging, snapshots, and a Streamlit dashboard.

Implement:
- src/ai_cctv/logger.py
- src/ai_cctv/snapshot.py
- src/ai_cctv/app.py
- scripts/run_dashboard.py

Requirements:
- CSV log at data/logs/events.csv
- snapshots saved to data/snapshots
- dashboard shows recent events and snapshot paths
- dashboard must not require webcam

Verification:
- python -m pytest
- python -m compileall src scripts
```

## 8. Phase 7: Demo Hardening

```text
/prompts:executor
Implement Phase 7 only.

Goal:
Prepare the project for MacBook presentation demo.

Update:
- README.md
- DEMO_SCENARIO.md
- TROUBLESHOOTING.md
- configs/demo_mac.yaml

README must include:
1. macOS setup
2. Windows training setup
3. webcam run
4. video fallback run
5. dashboard run
6. dataset workflow
7. training workflow
8. known limitations

Verification:
- python -m pytest
- python -m compileall src scripts tools
```

## 추가 프롬프트: 데이터 준비 전 파이프라인 완성

```text
/prompts:executor
Revise the project for readiness-first development.

Context:
- Actual video recording and final dataset collection will happen later.
- Windows Desktop with RTX 4070 SUPER is the primary implementation and training environment.
- MacBook is a fallback implementation environment and the final demo environment.

Goal:
Implement all scripts, configs, tests, and docs needed so that once videos/data are available, the project can immediately run:
1. frame extraction
2. auto-labeling
3. label review
4. dataset split/check
5. YOLO training on RTX 4070 SUPER
6. validation
7. MacBook benchmark
8. webcam or sample-video demo

Do not require real dataset files for tests.
Provide dry-run behavior or clear errors when data is missing.
```
