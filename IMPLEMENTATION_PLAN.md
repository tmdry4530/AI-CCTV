# IMPLEMENTATION_PLAN.md

## Phase 0: Repository scaffold

### 목표

프로젝트 기본 구조, 설정 파일, 문서, 테스트 골격을 만든다.

### 산출물

- `src/ai_cctv/`
- `tests/`
- `scripts/`
- `tools/`
- `configs/`
- `data/`
- `models/`
- `docs/`
- `requirements.txt`
- `pyproject.toml`

### 완료 기준

```bash
python -m compileall src scripts tools
```

## Phase 1: Pure event logic

### 목표

YOLO/OpenCV 없이 테스트 가능한 이벤트 로직을 만든다.

### 구현 파일

- `src/ai_cctv/geometry.py`
- `src/ai_cctv/state.py`
- `src/ai_cctv/event_detector.py`

### 테스트

- `tests/test_geometry.py`
- `tests/test_owner_assignment.py`
- `tests/test_abandoned_detection.py`
- `tests/test_theft_suspected.py`

### 완료 기준

```bash
python -m pytest tests/test_geometry.py tests/test_owner_assignment.py tests/test_abandoned_detection.py tests/test_theft_suspected.py
```

## Phase 2: Detector/tracker adapters

### 목표

YOLO 결과를 내부 dataclass로 변환한다.

### 구현 파일

- `src/ai_cctv/detector.py`
- `src/ai_cctv/tracker.py`
- `src/ai_cctv/config.py`

### 완료 기준

```bash
python -m pytest
python -m compileall src
```

## Phase 3: Runtime

### 목표

웹캠/영상 파일을 처리하고 화면에 결과를 표시한다.

### 구현 파일

- `src/ai_cctv/camera.py`
- `src/ai_cctv/visualizer.py`
- `scripts/run_webcam.py`
- `scripts/run_video.py`

### 완료 기준

```bash
python scripts/run_webcam.py --help
python scripts/run_video.py --help
```

## Phase 4: Auto-labeling

### 목표

라벨링 수작업을 최소화하는 파이프라인을 만든다.

### 구현 파일

- `scripts/record_webcam.py`
- `scripts/extract_frames.py`
- `scripts/auto_label_yolo.py`
- `tools/label_review_app.py`
- `scripts/split_dataset.py`
- `scripts/check_dataset.py`

### 완료 기준

```bash
python scripts/record_webcam.py --help
python scripts/extract_frames.py --help
python scripts/auto_label_yolo.py --help
python scripts/check_dataset.py --help
```

## Phase 5: Training/evaluation

### 목표

RTX 4070 SUPER에서 학습하고 MacBook에서 벤치마크할 수 있게 한다.

### 구현 파일

- `scripts/train_yolo.py`
- `scripts/validate_yolo.py`
- `scripts/benchmark_model.py`

### 완료 기준

```bash
python scripts/train_yolo.py --help
python scripts/validate_yolo.py --help
python scripts/benchmark_model.py --help
```

## Phase 6: Logging/dashboard

### 목표

이벤트를 저장하고 발표용으로 표시한다.

### 구현 파일

- `src/ai_cctv/logger.py`
- `src/ai_cctv/snapshot.py`
- `src/ai_cctv/app.py`
- `scripts/run_dashboard.py`

### 완료 기준

```bash
python -m pytest
python -m compileall src scripts tools
```

## Phase 7: Demo hardening

### 목표

MacBook 발표 실패 가능성을 낮춘다.

### 구현 파일

- `README.md`
- `DEMO_SCENARIO.md`
- `TROUBLESHOOTING.md`
- `configs/demo_mac.yaml`

### 완료 기준

```bash
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
python scripts/run_webcam.py --config configs/demo_mac.yaml
```
