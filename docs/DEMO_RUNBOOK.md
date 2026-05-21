# DEMO_RUNBOOK.md

## Purpose

Final MacBook demo checklist and execution path. MacBook is the final demo environment and fallback
implementation environment when Windows-specific issues block progress.

## 1. Required assets before claiming demo readiness

```text
models/best_demo.pt
data/samples/final_demo.mp4
configs/demo_mac.yaml
data/logs/ directory
data/snapshots/ directory
```

If any required asset is missing, report it as a readiness gap instead of claiming demo success.

## 2. MacBook environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest
python -m compileall src scripts tools
```

Device policy:

```text
cuda unavailable on MacBook
mps if available
cpu fallback
```

## 3. Benchmark final model

```bash
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
```

Target: MacBook FPS >= 10. Use measured output only.

## 4. Webcam demo

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml
```

## 5. Fallback sample-video demo

```bash
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
```

## 6. Dashboard

```bash
python scripts/run_dashboard.py
# or
streamlit run src/ai_cctv/app.py
```

## 7. Presentation flow

1. Show that the system tracks person/object IDs.
2. Owner stays near object long enough to register.
3. Owner leaves while object remains.
4. System emits `abandoned_object`.
5. Non-owner approaches long enough to emit `suspicious_approach`.
6. Object disappears or moves significantly.
7. System emits `theft_suspected`.
8. Show CSV log, snapshot, and dashboard.

## 8. Presentation-day freeze

Do not train a new model, install new packages, change camera angle, change thresholds, or introduce
new object types during the live presentation.
