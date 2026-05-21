# data directory

This directory is intentionally scaffolded before real videos exist.

```text
raw/        private raw recordings; do not commit real videos
frames/     extracted images from raw videos
autolabels/ YOLO auto-generated labels and manifests
reviewed/   human review outputs for labels/images
datasets/   YOLO dataset yaml/root created by split_dataset.py
logs/       CSV event logs from runtime demos
snapshots/  event snapshot images
samples/    fallback demo videos
```

Tracked `.gitkeep` files preserve the directory shape. Real private videos, frames, labels, logs,
snapshots, and sample videos are ignored by default.

Readiness commands:

```bash
python scripts/record_webcam.py --help
python scripts/extract_frames.py --help
python scripts/auto_label_yolo.py --help
python scripts/split_dataset.py --help
python scripts/check_dataset.py --help
```
