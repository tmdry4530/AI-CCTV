# Objective

Build a webcam-based AI CCTV system with auto-labeling, custom YOLO training support, abandoned object detection, theft_suspected detection, RTX 4070 SUPER training, and MacBook demo readiness.

# Source of truth

Use these files as source of truth:

- `AGENTS.md`
- `PRD.md`
- `SPEC.md`
- `TECH_SPEC.md`
- `TEST_PLAN.md`
- `DATASET_PLAN.md`
- `AUTO_LABELING_PLAN.md`
- `MODEL_PLAN.md`
- `EVAL_PLAN.md`
- `PLATFORM_MATRIX.md`
- `MODEL_EXPERIMENTS.md`

# Required system features

- webcam input
- video file input
- YOLO detector wrapper
- object tracker wrapper
- internal dataclass state model
- geometry utilities
- owner assignment logic
- abandoned object event
- suspicious approach event
- theft_suspected event
- CSV event log
- snapshot saving
- OpenCV overlay
- Streamlit dashboard
- MacBook demo config
- sample video fallback

# Required model features

- data collection script
- frame extraction script
- auto-labeling script
- label review UI
- dataset split script
- dataset checker
- YOLO training script
- YOLO validation script
- model benchmark script
- model experiment log

# Platform requirements

- Tests must pass on macOS and Windows.
- Runtime must work on MacBook without CUDA.
- Training should use RTX 4070 SUPER CUDA when available.
- Device selection must support cuda, mps, and cpu.
- Use pathlib for all filesystem paths.

# Accuracy targets

- mAP50 target >= 0.70 on custom validation set.
- person recall target >= 0.85.
- main object recall target >= 0.65.
- MacBook demo FPS target >= 10.
- demo scenario target >= 4 successes out of 5 runs.

# Required verification

```bash
python -m pytest
python -m compileall src scripts tools
python scripts/check_dataset.py --help
python scripts/train_yolo.py --help
python scripts/validate_yolo.py --help
python scripts/benchmark_model.py --help
```

# Optional verification when data/model exists

```bash
yolo detect val data=data/datasets/ai_cctv.yaml model=models/best_demo.pt
python scripts/benchmark_model.py --model models/best_demo.pt --source 0 --imgsz 640
python scripts/run_video.py --source data/samples/final_demo.mp4 --config configs/demo_mac.yaml
```

# Safety

- Do not implement face recognition.
- Do not identify real people.
- Do not upload video or snapshots to cloud by default.
- Use theft_suspected, never claim actual theft.

# Completion criteria

Do not mark complete until:

- all required features are implemented
- all required verification commands pass or failures are explicitly documented
- README has Mac and Windows setup
- event logic is testable without webcam or YOLO
- demo scenario is documented
- final report includes changed files, tests, skipped checks, model workflow, and residual risks

# Readiness-first correction

Actual video recording and final dataset collection will happen later.
Do not treat missing raw videos, missing reviewed labels, or missing final model weights as implementation blockers.
Instead, complete the project to a readiness state where the following can start immediately once data is available:

- frame extraction
- auto-labeling
- label review
- dataset split/check
- RTX 4070 SUPER training
- YOLO validation
- MacBook benchmark
- webcam/sample-video demo

Windows Desktop with RTX 4070 SUPER is the primary implementation and training environment.
MacBook is a fallback implementation environment and the final demo environment.

Before data exists, completion means:

- all scripts exist
- all scripts provide `--help`
- mock tests pass
- dry-run or clear missing-data errors exist
- docs explain next commands
- no fake mAP/FPS/demo success values are invented
