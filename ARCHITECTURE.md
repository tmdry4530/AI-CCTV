# ARCHITECTURE.md

## 1. 전체 구조

```text
Webcam / Video
   ↓
CameraReader
   ↓
YOLO Detector / Tracker
   ↓
Internal Tracked Detections
   ↓
State Store
   ↓
Geometry Engine
   ↓
Event Detector
   ↓
Logger / Snapshot Writer
   ↓
Visualizer / Dashboard
```

## 2. 설계 원칙

- detector와 event detector를 분리한다.
- 모델 결과는 내부 dataclass로 변환한다.
- 이벤트 로직은 pure Python으로 테스트 가능해야 한다.
- 플랫폼 종속 코드는 config/device layer에 숨긴다.
- 시연 runtime과 학습 pipeline을 분리한다.

## 3. 주요 데이터 흐름

### Runtime Flow

```text
frame = camera.read()
tracked = tracker.track(frame)
people, objects = normalize(tracked)
events = event_detector.update(timestamp, people, objects)
logger.write(events)
snapshot.save(frame, events)
visualizer.draw(frame, people, objects, events)
```

### Training Flow

```text
record webcam video
→ extract frames
→ auto-label images
→ review selected labels
→ split train/val/test by source video
→ check dataset
→ train YOLO
→ validate YOLO
→ benchmark on MacBook
→ choose best_demo.pt
```

## 4. 경계

### Runtime Boundary

- 입력: webcam/video frame
- 출력: screen overlay, event log, snapshot

### Model Boundary

- 입력: labeled YOLO dataset
- 출력: trained model weights, metrics

### Evaluation Boundary

- 입력: detection metrics, runtime metrics, event test results
- 출력: model selection decision

## 5. 상태 머신

### Object status

```text
normal
→ owned
→ abandoned
→ suspicious
→ theft_suspected
→ returned
```

### 상태 전이

```text
normal + nearby person for 3s
  → owned

owned + owner missing + object visible for 5s
  → abandoned

abandoned + non-owner nearby for 1.5s
  → suspicious

suspicious + object missing or moved significantly
  → theft_suspected

abandoned + owner returns
  → returned or owned
```

## 6. 발표용 구조 설명

발표에서는 다음 식으로 설명한다.

```text
이 시스템은 단순히 객체를 찾는 것이 아니라,
객체 ID를 추적하고,
사람과 물건의 관계를 시간 기준으로 누적해,
상황 이벤트를 판정한다.
```
