# MODEL_PLAN.md

## 1. 목표

- COCO pretrained 모델로 baseline 확보
- 공개 luggage/bag 데이터셋과 MacBook 수집 데이터로 custom YOLO fine-tuning
- RTX 4070 SUPER에서 학습
- MacBook에서 최종 FPS/정확도 검증

## 2. 장비

### 학습

- Windows desktop
- RTX 4070 SUPER
- CUDA 사용
- VRAM 12GB 기준

### 시연

- MacBook
- MPS 또는 CPU
- 최종 모델은 `models/best_demo.pt`

## 3. 모델 후보

| 모델 | 용도 |
|---|---|
| YOLO nano | 빠른 데이터셋 검증 |
| YOLO small | 최종 1순위 후보 |
| YOLO small imgsz=960 | 작은 물체 개선 후보 |
| YOLO medium | 정확도 상한 확인 |

## 4. 학습 명령

### 1차: 빠른 데이터셋 검증

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11n.pt epochs=30 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_n_quick
```

### 2차: 기본 최종 후보

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11s.pt epochs=80 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_s_640
```

### 3차: 작은 물체 개선 후보

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11s.pt epochs=80 imgsz=960 batch=-1 device=0 project=runs/train name=ai_cctv_s_960
```

### 4차: 정확도 상한 확인

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11m.pt epochs=100 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_m_640
```

## 5. 최종 모델 선택 기준

최종 발표 모델은 mAP만으로 고르지 않는다.

```text
1. MacBook FPS >= 10
2. demo success >= 4/5
3. person recall >= 0.85
4. main object recall >= 0.65
5. false theft_suspected가 과도하지 않을 것
```

## 6. 모델 파일 관리

```text
models/
├─ best_demo.pt
├─ best_s_640.pt
├─ best_s_960.pt
└─ README.md
```

`best_demo.pt`는 발표 전 최종 고정 모델이다.

## 7. MacBook benchmark

```bash
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
```

## 8. 모델 개선 루프

```text
evaluate
→ identify weak class
→ collect more MacBook data
→ auto-label
→ review selected labels
→ retrain
→ validate
→ benchmark on MacBook
```

## 9. 현재 단계 정책: 학습 실행은 데이터 준비 후 진행

지금 Codex가 해야 하는 것은 최종 학습을 실제로 완료하는 것이 아니라, 데이터가 준비되는 즉시 학습 가능한 상태를 만드는 것이다.

### 지금 구현할 것

- 학습 스크립트
- 검증 스크립트
- 벤치마크 스크립트
- 모델 실험 로그 템플릿
- `models/README.md`
- Windows RTX 4070 SUPER 학습 명령
- MacBook benchmark 명령
- 데이터가 없을 때의 명확한 안내 메시지

### 데이터 준비 후 실행할 것

```bash
python scripts/check_dataset.py --data data/datasets/ai_cctv.yaml
python scripts/train_yolo.py --data data/datasets/ai_cctv.yaml --model yolo11s.pt --epochs 80 --imgsz 640 --device cuda
python scripts/validate_yolo.py --model runs/train/ai_cctv_s_640/weights/best.pt --data data/datasets/ai_cctv.yaml
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
```

### 금지

- 데이터가 없는데 임의 mAP 수치를 작성하지 않는다.
- 최종 모델이 없는데 `best_demo.pt`가 검증됐다고 주장하지 않는다.
- MacBook FPS를 실제 측정 없이 추정값으로 쓰지 않는다.
