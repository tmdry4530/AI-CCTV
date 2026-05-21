# MODEL_EXPERIMENTS.md

## 1. 실험표

| ID | 모델 | imgsz | epochs | 장비 | 목적 | 상태 | 결과 |
|---|---|---:|---:|---|---|---|---|
| E1 | YOLO nano | 640 | 30 | RTX 4070 SUPER | 데이터셋/라벨 오류 확인 | todo | - |
| E2 | YOLO small | 640 | 80 | RTX 4070 SUPER | 정확도/속도 균형 | todo | - |
| E3 | YOLO small | 960 | 80 | RTX 4070 SUPER | 작은 물체 개선 | todo | - |
| E4 | YOLO medium | 640 | 100 | RTX 4070 SUPER | 정확도 상한 확인 | todo | - |
| E5 | best_s_640.pt | 640 | - | MacBook | 시연 FPS 검증 | todo | - |
| E6 | best_s_960.pt | 960 | - | MacBook | 작은 물체 모델 시연 검증 | todo | - |
| E7 | CoreML export | 640 | - | MacBook | 선택 최적화 | optional | - |

## 2. 실험 기록 템플릿

```md
## E-YYYYMMDD-001

- Date:
- Dataset version:
- Model:
- imgsz:
- epochs:
- batch:
- device:
- train command:
- val command:

### Detection metrics
- mAP50:
- mAP50-95:
- precision:
- recall:
- person recall:
- bag recall:
- laptop recall:
- cell_phone recall:

### Runtime metrics
- Windows FPS:
- MacBook FPS:
- inference ms:

### Event demo metrics
- abandoned success:
- theft_suspected success:
- false abandoned:
- false theft_suspected:

### Decision
- keep / reject / retrain

### Notes
-
```

## 3. 최종 모델 결정 기록

```md
## Final model decision

- Selected model:
- Reason:
- Rejected models:
- MacBook FPS:
- Demo success:
- Known weaknesses:
- Presentation fallback:
```
