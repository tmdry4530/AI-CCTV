# TECH_SPEC.md

## 1. 기술 목표

- 이벤트 로직과 모델 추론을 분리한다.
- YOLO/OpenCV 없이 이벤트 로직을 테스트할 수 있게 한다.
- detector/tracker는 내부 dataclass로 결과를 변환한다.
- Windows와 macOS에서 동일한 코드베이스가 동작한다.
- RTX 4070 SUPER 학습과 MacBook 시연을 모두 지원한다.

## 2. 패키지 구조

```text
src/ai_cctv/
├─ __init__.py
├─ config.py
├─ camera.py
├─ detector.py
├─ tracker.py
├─ geometry.py
├─ state.py
├─ event_detector.py
├─ logger.py
├─ snapshot.py
├─ visualizer.py
├─ app.py
└─ cli.py
```

## 3. 모듈 계약

### `detector.py`

입력:

- OpenCV frame
- model path
- confidence threshold
- target classes

출력:

- `list[Detection]`

`Detection` 필드:

- `class_id`
- `class_name`
- `confidence`
- `bbox`
- `center`

금지:

- event logic import 금지
- 직접 로그 저장 금지

### `tracker.py`

입력:

- frame
- detection model 또는 YOLO track result

출력:

- `list[TrackedDetection]`

`TrackedDetection` 필드:

- `track_id`
- `class_id`
- `class_name`
- `confidence`
- `bbox`
- `center`

### `event_detector.py`

입력:

- 현재 frame index/timestamp
- tracked people
- tracked objects

출력:

- `list[Event]`

금지:

- `cv2` import 금지
- `ultralytics` import 금지
- filesystem write 금지

### `logger.py`

입력:

- Event

출력:

- CSV row
- optional SQLite row

## 4. Device 선택

```python
def select_device() -> str:
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"
```

## 5. 경로 처리

모든 경로는 `pathlib.Path`를 사용한다.

금지:

```python
"data\\logs\\events.csv"
"data/logs/events.csv"
```

권장:

```python
Path("data") / "logs" / "events.csv"
```

## 6. CLI 계약

### 웹캠 실행

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml
```

### 영상 실행

```bash
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
```

### 대시보드

```bash
python scripts/run_dashboard.py
```

### 프레임 추출

```bash
python scripts/extract_frames.py --source data/raw/demo.mp4 --out data/frames/demo --every-n 10
```

### 자동 라벨링

```bash
python scripts/auto_label_yolo.py --images data/frames --out data/autolabels --classes person bag laptop cell_phone
```

### 학습

```bash
python scripts/train_yolo.py --data data/datasets/ai_cctv.yaml --model yolo11s.pt --epochs 80 --imgsz 640 --device auto
```

### 검증

```bash
python scripts/validate_yolo.py --model runs/train/ai_cctv_s_640/weights/best.pt --data data/datasets/ai_cctv.yaml
```

### 벤치마크

```bash
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
```

## 7. 의존성 초안

```text
opencv-python
ultralytics
streamlit
pandas
pyyaml
pytest
numpy
pillow
```

선택:

```text
ruff
mypy
torch
```

`torch`는 설치 환경별 차이가 있으므로 README에서 Mac/Windows 설치 가이드를 분리한다.
