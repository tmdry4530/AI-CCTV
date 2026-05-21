# TRAINING_RUNBOOK.md

## 목적

데이터셋이 준비된 뒤 RTX 4070 SUPER에서 모델을 학습하기 위한 절차다.

## 1. 데이터셋 점검

```bash
python scripts/check_dataset.py --data data/datasets/ai_cctv.yaml
```

## 2. 빠른 검증 학습

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11n.pt epochs=30 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_n_quick
```

## 3. 기본 후보 학습

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11s.pt epochs=80 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_s_640
```

## 4. 작은 물체 개선 실험

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11s.pt epochs=80 imgsz=960 batch=-1 device=0 project=runs/train name=ai_cctv_s_960
```

## 5. 검증

```bash
yolo detect val data=data/datasets/ai_cctv.yaml model=runs/train/ai_cctv_s_640/weights/best.pt
```

## 6. 최종 모델 복사

```bash
mkdir -p models
cp runs/train/ai_cctv_s_640/weights/best.pt models/best_demo.pt
```
