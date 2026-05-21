# DATA_COLLECTION_RUNBOOK.md

## Purpose

Use this when real recording becomes available. The implementation is ready before data exists; this
runbook gives the commands to move from raw video to a checked YOLO dataset.

## 1. Pre-recording checklist

- Fix camera angle and lighting for each scenario.
- Use the actual MacBook demo environment when possible.
- Include empty room, person-only, object-only, owner-registration, abandonment, occlusion, and
  non-owner approach scenarios.
- Use filenames that include device, object, scenario, and index.
- Do not upload private video or snapshots to cloud services by default.

## 2. Recommended filenames

```text
data/raw/mac_bag_owner_leave_01.mp4
data/raw/mac_bag_theft_suspected_01.mp4
data/raw/mac_laptop_owner_leave_01.mp4
data/raw/mac_cell_phone_close_01.mp4
data/raw/mac_empty_scene_01.mp4
```

## 3. Record video

```bash
python scripts/record_webcam.py --out data/raw/mac_bag_owner_leave_01.mp4 --width 1280 --height 720 --fps 15
```

Dry-run without camera access:

```bash
python scripts/record_webcam.py --out data/raw/mac_bag_owner_leave_01.mp4 --width 1280 --height 720 --fps 15 --dry-run
```

## 4. Extract frames

```bash
python scripts/extract_frames.py --source data/raw/mac_bag_owner_leave_01.mp4 --out data/frames/mac_bag_owner_leave_01 --every-n 10
```

## 5. Auto-label locally

```bash
python scripts/auto_label_yolo.py --images data/frames --out data/autolabels --classes person bag laptop cell_phone --model yolo11n.pt
```

This uses local YOLO inference. It does not upload images.

## 6. Review labels and export accepted pairs

Review labels in the UI:

```bash
streamlit run tools/label_review_app.py
```

Export only accepted reviewed image/label pairs into a `split_dataset.py`-consumable tree:

```bash
python tools/label_review_app.py --export --image-root data/frames --label-root data/autolabels/labels --state data/reviewed/review_state.json --out data/reviewed --clean
```

Rejected and unreviewed items are excluded from export. The export writes `data/reviewed/images/`,
`data/reviewed/labels/`, and `data/reviewed/review_manifest.csv`.

Minimum review priority:

1. validation/test candidates;
2. low-confidence labels;
3. cell_phone examples;
4. final demo-like scenes;
5. unusually small/large boxes or crowded images.

Validation/test labels must be human-reviewed.

## 7. Split by video/scenario and check

```bash
python scripts/split_dataset.py --source data/reviewed --out data/datasets/ai_cctv --strategy by-video --clean
python scripts/check_dataset.py --data data/datasets/ai_cctv.yaml
```

Never random-split near-duplicate frames from the same source video across train/val/test.

## 8. Handoff to training

After the dataset check passes, continue with `docs/TRAINING_RUNBOOK.md`.
