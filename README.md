# Webcam AI CCTV

Readiness-first webcam AI CCTV system for abandoned object and `theft_suspected` event demos.
The system detects/tracks people and objects, reasons about owner/object relationships over time,
logs events, saves snapshots, and provides data/model tooling so training can begin as soon as real
videos and reviewed labels are collected.

> Safety boundary: this project does **not** identify people, does **not** use face recognition, and
> does **not** claim actual theft. The only supported advisory event wording is
> `theft_suspected` / 도난 의심.

## Current readiness-first policy

Real videos, final reviewed labels, and final `models/best_demo.pt` are expected later. Missing data
is not an implementation blocker. Before data exists, completion means:

- source package, scripts, configs, and tests exist;
- every core script supports `--help`;
- event logic passes mock sequence tests without webcam, YOLO, CUDA, or real videos;
- scripts provide dry-run behavior or clear missing-data/model errors;
- runbooks document the exact next commands for data collection, auto-labeling, training,
  validation, benchmarking, and demo.

Do not invent mAP, FPS, or demo success values before measurement.

## Architecture

```text
src/ai_cctv/
├─ config.py          # YAML config and cuda/mps/cpu selection
├─ camera.py          # webcam/video input
├─ detector.py        # YOLO detection adapter
├─ tracker.py         # YOLO tracking adapter
├─ geometry.py        # pure bbox/center/distance helpers
├─ state.py           # dataclasses for tracks/events/state
├─ event_detector.py  # pure owner/abandoned/suspicious/theft_suspected logic
├─ logger.py          # CSV/SQLite event logging
├─ snapshot.py        # event snapshot capture
├─ visualizer.py      # OpenCV overlays
├─ app.py             # Streamlit dashboard
└─ cli.py             # shared runtime loop
```

`event_detector.py` intentionally does not import OpenCV, Ultralytics, webcam, GPU, or filesystem
write APIs. Runtime inference, training, auto-labeling, dashboard, and dataset tooling are separated
into modules/scripts.

## Supported classes

```yaml
0: person
1: bag
2: laptop
3: cell_phone
```

COCO bootstrap aliases such as `backpack`, `handbag`, `suitcase`, and `cell phone` are normalized
into the project classes during auto-labeling/runtime adaptation.

## Canonical event names

Logs, tests, dashboard rows, and code use lowercase snake_case event names:

```text
owner_registered
abandoned_object
suspicious_approach
object_removed
theft_suspected
object_returned
```

Uppercase names, if shown in slides or overlays, are display aliases only.

## Setup: Windows development

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If CUDA PyTorch is needed, install the PyTorch build matching the local CUDA driver from the official
PyTorch selector before training. Runtime and tests must still work without CUDA.

## Setup: Windows RTX 4070 SUPER training

Windows Desktop + RTX 4070 SUPER is the primary implementation/training environment.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python scripts/check_dataset.py --data data/datasets/ai_cctv.yaml
python scripts/train_yolo.py --data data/datasets/ai_cctv.yaml --model yolo11s.pt --epochs 80 --imgsz 640 --device cuda
```

Reference Ultralytics CLI equivalent:

```bash
yolo detect train data=data/datasets/ai_cctv.yaml model=yolo11s.pt epochs=80 imgsz=640 batch=-1 device=0 project=runs/train name=ai_cctv_s_640
```

## Setup: MacBook fallback development and final demo

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest
```

MacBook demo uses `mps` when available and falls back to `cpu`. CUDA is not required for runtime or
tests.

## Required verification before claiming completion

```bash
python -m pytest
python -m compileall src scripts tools
python scripts/check_dataset.py --help
python scripts/train_yolo.py --help
python scripts/validate_yolo.py --help
python scripts/benchmark_model.py --help
```

Broader readiness help smoke checks:

```bash
python scripts/record_webcam.py --help
python scripts/extract_frames.py --help
python scripts/auto_label_yolo.py --help
python scripts/split_dataset.py --help
python scripts/run_webcam.py --help
python scripts/run_video.py --help
python scripts/run_dashboard.py --help
```

## Data collection and auto-labeling workflow

Run after real videos can be recorded:

```bash
python scripts/record_webcam.py --out data/raw/mac_bag_owner_leave_01.mp4 --width 1280 --height 720 --fps 15
python scripts/extract_frames.py --source data/raw/mac_bag_owner_leave_01.mp4 --out data/frames/mac_bag_owner_leave_01 --every-n 10
python scripts/auto_label_yolo.py --images data/frames --out data/autolabels --classes person bag laptop cell_phone
streamlit run tools/label_review_app.py
python tools/label_review_app.py --export --image-root data/frames --label-root data/autolabels/labels --state data/reviewed/review_state.json --out data/reviewed --clean
python scripts/split_dataset.py --source data/reviewed --out data/datasets/ai_cctv --strategy by-video --clean
python scripts/check_dataset.py --data data/datasets/ai_cctv.yaml
```

Validation/test labels must be human-reviewed. Do not random-split near-duplicate frames from the
same video across train/val/test.

## Training, validation, benchmark

```bash
python scripts/train_yolo.py --data data/datasets/ai_cctv.yaml --model yolo11s.pt --epochs 80 --imgsz 640 --device cuda
python scripts/validate_yolo.py --model runs/train/ai_cctv_s_640/weights/best.pt --data data/datasets/ai_cctv.yaml
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
```

Optional quick/dry-run checks before data/model files exist:

```bash
python scripts/train_yolo.py --dry-run --device cuda
python scripts/validate_yolo.py --model models/best_demo.pt --dry-run
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --dry-run
```

## Runtime demo commands

Webcam:

```bash
python scripts/run_webcam.py --config configs/demo_mac.yaml
```

Sample/fallback video after `data/samples/final_demo.mp4` exists:

```bash
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
```

Dashboard:

```bash
python scripts/run_dashboard.py
# or
streamlit run src/ai_cctv/app.py
```

## Useful dry-run commands

```bash
python scripts/record_webcam.py --out data/raw/test.mp4 --dry-run
python scripts/auto_label_yolo.py --images data/frames --out data/autolabels --dry-run
python scripts/run_dashboard.py --no-launch
```

Runtime `--dry-run` validates config/model/source and therefore requires the referenced local model
and source files to exist; it should fail clearly until final assets are prepared.

## Missing-data behavior

- Missing dataset yaml: `check_dataset.py`, `train_yolo.py`, and `validate_yolo.py` print clear errors.
- Missing `models/best_demo.pt`: runtime/benchmark scripts refuse to claim demo readiness.
- Missing sample video: `run_video.py` reports the missing path.
- Missing optional packages: scripts explain which dependency from `requirements.txt` is needed.

## Documentation

- `docs/DATA_COLLECTION_RUNBOOK.md`
- `docs/TRAINING_RUNBOOK.md`
- `docs/DEMO_RUNBOOK.md`
- `DEMO_SCENARIO.md`
- `TROUBLESHOOTING.md`
- `MODEL_EXPERIMENTS.md`
