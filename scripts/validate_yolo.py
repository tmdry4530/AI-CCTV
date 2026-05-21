from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from ai_cctv.config import select_device  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a YOLO model against the AI CCTV dataset.")
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=Path("data") / "datasets" / "ai_cctv.yaml")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    device = select_device(args.device)
    if args.dry_run:
        print(f"YOLO val dry-run: model={args.model} data={args.data} imgsz={args.imgsz} device={device}")
        return 0
    if not args.data.exists():
        raise SystemExit(f"Dataset yaml does not exist yet: {args.data}")
    if not args.model.exists():
        raise SystemExit(
            f"Model file does not exist yet: {args.model}. Do not invent validation metrics before training."
        )
    try:
        from ultralytics import YOLO  # type: ignore
    except ImportError as exc:
        raise SystemExit("ultralytics is required for validation. Install requirements.txt.") from exc
    model = YOLO(str(args.model))
    metrics = model.val(data=str(args.data), imgsz=args.imgsz, device=device)
    print(metrics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
