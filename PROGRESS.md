# PROGRESS.md

## Current objective

Complete readiness-first Webcam AI CCTV implementation from `.codex/goals/ai-cctv-complete.md`.

## Completed

- Planning document pack exists.
- Python package scaffold exists under `src/ai_cctv/`.
- Pure event logic is implemented without OpenCV/YOLO/GPU/filesystem writes.
- Mock sequence tests cover owner registration, abandoned object, suspicious approach,
  `theft_suspected`, passing-by, occlusion grace, and logging/dataset checks.
- Runtime, dashboard, data collection, auto-labeling, dataset split/check, training, validation, and
  benchmark scripts exist and support `--help`.
- Data/model directories are scaffolded with tracked placeholders.
- README and runbooks document Windows RTX training and MacBook demo paths.

## Still external / not claimed

- Real dataset has not been collected.
- Final labels have not been human-reviewed.
- Final model has not been trained.
- MacBook FPS has not been measured.
- `data/samples/final_demo.mp4` has not been recorded.

These are expected future activities and are not implementation blockers under the readiness-first
plan.

## Verification

Run before final completion report:

```bash
python -m pytest
python -m compileall src scripts tools
python scripts/check_dataset.py --help
python scripts/train_yolo.py --help
python scripts/validate_yolo.py --help
python scripts/benchmark_model.py --help
```
