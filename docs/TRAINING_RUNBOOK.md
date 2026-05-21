# TRAINING_RUNBOOK.md

## Purpose

Train and validate YOLO models once the checked dataset exists. Windows Desktop + RTX 4070 SUPER is
the primary training environment. Do not record fake mAP/FPS values before these commands run.

## 1. Verify dataset

```bash
python scripts/check_dataset.py --data data/datasets/ai_cctv.yaml
```

## 2. Quick dataset sanity training

```bash
python scripts/train_yolo.py --data data/datasets/ai_cctv.yaml --model yolo11n.pt --epochs 30 --imgsz 640 --device cuda --name ai_cctv_n_quick
```

Ultralytics CLI equivalent:

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11n.pt epochs=30 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_n_quick
```

## 3. Primary final candidate

```bash
python scripts/train_yolo.py --data data/datasets/ai_cctv.yaml --model yolo11s.pt --epochs 80 --imgsz 640 --device cuda --name ai_cctv_s_640
```

## 4. Small-object candidate

```bash
python scripts/train_yolo.py --data data/datasets/ai_cctv.yaml --model yolo11s.pt --epochs 80 --imgsz 960 --device cuda --name ai_cctv_s_960
```

## 5. Accuracy upper-bound candidate

```bash
python scripts/train_yolo.py --data data/datasets/ai_cctv.yaml --model yolo11m.pt --epochs 100 --imgsz 640 --device cuda --name ai_cctv_m_640
```

## 6. Validate

```bash
python scripts/validate_yolo.py --model runs/train/ai_cctv_s_640/weights/best.pt --data data/datasets/ai_cctv.yaml --imgsz 640
```

Record results in `MODEL_EXPERIMENTS.md` only after validation actually runs.

## 7. Select final demo model

Selection order is demo-readiness first, not mAP-only:

1. MacBook FPS >= 10;
2. demo success >= 4/5;
3. person recall >= 0.85;
4. main object recall >= 0.65;
5. false `theft_suspected` is low enough for presentation.

Copy the selected model explicitly:

```bash
mkdir -p models
cp runs/train/ai_cctv_s_640/weights/best.pt models/best_demo.pt
```

## 8. MacBook benchmark handoff

```bash
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
```

Then continue with `docs/DEMO_RUNBOOK.md`.
