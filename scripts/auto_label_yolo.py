from __future__ import annotations

import argparse
import csv
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
PROJECT_NAMES = {0: "person", 1: "bag", 2: "laptop", 3: "cell_phone"}
NAME_TO_PROJECT_ID = {name: idx for idx, name in PROJECT_NAMES.items()}
ALIASES = {
    "person": "person",
    "backpack": "bag",
    "handbag": "bag",
    "suitcase": "bag",
    "bag": "bag",
    "luggage": "bag",
    "laptop": "laptop",
    "cell phone": "cell_phone",
    "cell_phone": "cell_phone",
    "cellphone": "cell_phone",
    "phone": "cell_phone",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Auto-label images with a local/pretrained YOLO model.")
    parser.add_argument("--images", type=Path, required=True, help="Image file or directory.")
    parser.add_argument("--out", type=Path, required=True, help="Output directory for YOLO labels and manifest.")
    parser.add_argument("--model", default="yolo11n.pt", help="YOLO model path/name for bootstrapping.")
    parser.add_argument("--classes", nargs="+", default=list(PROJECT_NAMES.values()))
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--dry-run", action="store_true", help="List images and planned classes without model inference.")
    return parser


def iter_images(root: Path) -> list[Path]:
    if root.is_file() and root.suffix.lower() in IMAGE_EXTENSIONS:
        return [root]
    if not root.exists():
        raise SystemExit(f"Image input does not exist yet: {root}")
    return sorted(path for path in root.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)


def normalize_name(name: str) -> str | None:
    key = name.strip().lower().replace("_", " ")
    return ALIASES.get(key)


def main() -> int:
    args = build_parser().parse_args()
    images = iter_images(args.images)
    wanted = set(args.classes)
    if args.dry_run:
        print(f"Would auto-label {len(images)} images from {args.images} to {args.out}")
        print(f"classes={sorted(wanted)} model={args.model}")
        return 0
    if not images:
        raise SystemExit(f"No images found under {args.images}")
    try:
        from ultralytics import YOLO  # type: ignore
    except ImportError as exc:
        raise SystemExit("ultralytics is required for auto-labeling. Install requirements.txt.") from exc

    labels_dir = args.out / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.out / "manifest.csv"
    model = YOLO(args.model)
    rows: list[dict[str, str | int | float]] = []
    for image in images:
        result = model.predict(
            source=str(image),
            conf=args.conf,
            imgsz=args.imgsz,
            device=None if args.device == "auto" else args.device,
            verbose=False,
        )[0]
        names = getattr(result, "names", getattr(model, "names", {})) or {}
        image_shape = getattr(result, "orig_shape", None)
        if image_shape is None:
            height, width = 1, 1
        else:
            height, width = image_shape[:2]
        relative = image.relative_to(args.images) if args.images.is_dir() else Path(image.name)
        label_path = labels_dir / relative.with_suffix(".txt")
        label_path.parent.mkdir(parents=True, exist_ok=True)
        label_lines: list[str] = []
        for box in result.boxes or []:
            class_id = int(box.cls[0].item()) if hasattr(box.cls[0], "item") else int(box.cls[0])
            raw_name = str(names.get(class_id, class_id))
            project_name = normalize_name(raw_name)
            if project_name is None or project_name not in wanted:
                continue
            project_id = NAME_TO_PROJECT_ID[project_name]
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            x_center = ((x1 + x2) / 2.0) / max(1, width)
            y_center = ((y1 + y2) / 2.0) / max(1, height)
            box_width = (x2 - x1) / max(1, width)
            box_height = (y2 - y1) / max(1, height)
            confidence = float(box.conf[0].item()) if hasattr(box.conf[0], "item") else float(box.conf[0])
            label_lines.append(f"{project_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}")
            rows.append(
                {
                    "image": str(image),
                    "label": str(label_path),
                    "class": project_name,
                    "confidence": confidence,
                    "source_class": raw_name,
                }
            )
        label_path.write_text("\n".join(label_lines) + ("\n" if label_lines else ""), encoding="utf-8")
    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["image", "label", "class", "confidence", "source_class"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote labels to {labels_dir}")
    print(f"Wrote manifest to {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
