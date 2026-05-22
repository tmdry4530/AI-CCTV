# DEMO_RUNBOOK.md

## Purpose

Final MacBook demo checklist and execution path. MacBook is the final demo environment and fallback
implementation environment when Windows-specific issues block progress.

## 1. Camera preview smoke test before model training

Run this before a trained model exists to verify the MacBook demo camera, framing, and basic OpenCV
display path:

```bash
python scripts/preview_camera.py --source 0 --width 1280 --height 720 --fps 15
```

Expected behavior:

- an OpenCV window opens with the live camera feed;
- FPS is drawn on screen;
- frame size is drawn on screen;
- pressing `q` while the preview window is focused exits cleanly.

This command must not require YOLO, model weights, tracker state, dataset files, or CUDA.

Known Mac camera permission issue: if the command reports that camera source `0` cannot be opened,
grant camera access to the terminal app you are using (`Terminal`, `iTerm`, VS Code, or the Python
launcher) in **System Settings → Privacy & Security → Camera**, restart the terminal, and try again.

## 2. Required assets before claiming demo readiness

```text
models/best_demo.pt
data/samples/final_demo.mp4
configs/demo_mac.yaml
data/logs/ directory
data/snapshots/ directory
```

If any required asset is missing, report it as a readiness gap instead of claiming demo success.

## 3. MacBook environment

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

## 4. Benchmark final model

```bash
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
```

Target: MacBook FPS >= 10. Use measured output only.

## 5. Webcam demo

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml
```

## 6. Fallback sample-video demo

```bash
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
```

## 7. Dashboard

```bash
python scripts/run_dashboard.py
# or
streamlit run src/ai_cctv/app.py
```

## 8. Presentation flow

1. Show that the system tracks person/object IDs.
2. Owner stays near object long enough to register.
3. Owner leaves while object remains.
4. System emits `abandoned_object`.
5. Non-owner approaches long enough to emit `suspicious_approach`.
6. Object disappears or moves significantly.
7. System emits `theft_suspected`.
8. Show CSV log, snapshot, and dashboard.

## 9. Presentation-day freeze

Do not train a new model, install new packages, change camera angle, change thresholds, or introduce
new object types during the live presentation.
