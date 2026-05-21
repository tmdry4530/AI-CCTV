#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_cctv.config import select_device
from ai_cctv.geometry import yolo_xywhn_from_bbox
from ai_cctv.detector import detections_from_ultralytics_result

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local YOLO auto-labeling for AI CCTV images")
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", default="yolo11s.pt")
    parser.add_argument("--classes", nargs="+", default=["person", "bag", "laptop", "cell_phone"])
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def iter_images(root: Path) -> list[Path]:
    if root.is_file() and root.suffix.lower() in IMAGE_SUFFIXES:
        return [root]
    return sorted(p for p in root.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES)


def main() -> int:
    args = build_parser().parse_args()
    images = iter_images(args.images)
    if args.dry_run:
        print(f"would auto-label {len(images)} images -> {args.out} using {args.model}")
        return 0
    try:
        from ultralytics import YOLO  # type: ignore
    except Exception as exc:
        raise SystemExit(f"Ultralytics is required: {exc}") from exc
    model = YOLO(args.model)
    labels_dir = args.out / "labels"
    meta_path = args.out / "metadata.jsonl"
    labels_dir.mkdir(parents=True, exist_ok=True)
    class_to_id = {name: idx for idx, name in enumerate(args.classes)}
    device = select_device(args.device)
    with meta_path.open("w", encoding="utf-8") as meta_file:
        for image in images:
            results = model.predict(source=str(image), imgsz=args.imgsz, conf=args.conf, device=device, verbose=False)
            detections = detections_from_ultralytics_result(results[0], target_classes=args.classes) if results else []
            shape = getattr(results[0], "orig_shape", None) if results else None
            if shape:
                image_size = (int(shape[1]), int(shape[0]))
            else:
                from PIL import Image  # type: ignore

                with Image.open(image) as im:
                    image_size = im.size
            label_lines: list[str] = []
            for det in detections:
                if det.class_name not in class_to_id:
                    continue
                cx, cy, w, h = yolo_xywhn_from_bbox(det.bbox, image_size)
                label_lines.append(f"{class_to_id[det.class_name]} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
                meta_file.write(
                    json.dumps(
                        {
                            "image": str(image),
                            "label": str(labels_dir / f"{image.stem}.txt"),
                            "class_name": det.class_name,
                            "confidence": det.confidence,
                            "bbox_xyxy": det.bbox.as_xyxy(),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            (labels_dir / f"{image.stem}.txt").write_text("\n".join(label_lines) + ("\n" if label_lines else ""), encoding="utf-8")
    print(f"wrote labels to {labels_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
