from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from ai_cctv.config import select_training_device  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train YOLO for AI CCTV on Windows RTX/CUDA or fallback devices.")
    parser.add_argument("--data", type=Path, default=Path("data") / "datasets" / "ai_cctv.yaml")
    parser.add_argument("--model", default="yolo11s.pt")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", default="-1")
    parser.add_argument("--device", default="auto", help="auto, cuda, 0, mps, or cpu")
    parser.add_argument("--project", default="runs/train")
    parser.add_argument("--name", default="ai_cctv_s_640")
    parser.add_argument("--dry-run", action="store_true", help="Print resolved command without training.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    resolved_device = select_training_device(args.device)
    if args.dry_run:
        print(
            "YOLO train dry-run: "
            f"data={args.data} model={args.model} epochs={args.epochs} imgsz={args.imgsz} "
            f"batch={args.batch} device={resolved_device} project={args.project} name={args.name}"
        )
        return 0
    if not args.data.exists():
        raise SystemExit(
            f"Dataset yaml does not exist yet: {args.data}. Run split_dataset.py/check_dataset.py after data collection."
        )
    try:
        from ultralytics import YOLO  # type: ignore
    except ImportError as exc:
        raise SystemExit("ultralytics is required for training. Install requirements.txt.") from exc
    model = YOLO(args.model)
    model.train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=int(args.batch) if str(args.batch).lstrip("-").isdigit() else args.batch,
        device=resolved_device,
        project=args.project,
        name=args.name,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
