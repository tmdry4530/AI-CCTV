#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ai_cctv.config import _load_yaml

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate YOLO dataset structure and labels")
    parser.add_argument("--data", type=Path, default=Path("data") / "datasets" / "ai_cctv.yaml")
    parser.add_argument("--allow-empty", action="store_true", help="Allow empty image/label directories for scaffolding")
    parser.add_argument("--require-reviewed", action="store_true", help="Require reviewed metadata for val/test splits when metadata exists")
    return parser


def validate_dataset(data_yaml: Path, allow_empty: bool = False, require_reviewed: bool = False) -> list[str]:
    errors: list[str] = []
    if not data_yaml.exists():
        return [f"dataset yaml missing: {data_yaml}"]
    data = _load_yaml(data_yaml)
    names = _parse_names(data.get("names", {}))
    if not names:
        errors.append("names mapping is empty")
    root = Path(data.get("path", data_yaml.parent))
    if not root.is_absolute():
        root = (data_yaml.parent / root).resolve() if data_yaml.parent.name != "datasets" else (ROOT / root).resolve()
    for split in ("train", "val", "test"):
        rel = data.get(split)
        if rel is None:
            errors.append(f"missing split: {split}")
            continue
        images_dir = root / rel
        labels_dir = root / str(rel).replace("images", "labels", 1)
        if not images_dir.exists():
            errors.append(f"missing images dir: {images_dir}")
            continue
        if not labels_dir.exists():
            errors.append(f"missing labels dir: {labels_dir}")
            continue
        images = sorted(p for p in images_dir.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES)
        if not images and not allow_empty:
            errors.append(f"no images found in {images_dir}")
        for image in images:
            label = labels_dir / f"{image.stem}.txt"
            if not label.exists():
                errors.append(f"missing label for {image}")
                continue
            errors.extend(_validate_label_file(label, names))
        if require_reviewed and split in {"val", "test"}:
            review_file = root / f"{split}_reviewed.txt"
            if not review_file.exists():
                errors.append(f"missing human review marker for {split}: {review_file}")
    return errors


def _parse_names(raw: Any) -> dict[int, str]:
    if isinstance(raw, dict):
        return {int(k): str(v) for k, v in raw.items()}
    if isinstance(raw, list):
        return {idx: str(name) for idx, name in enumerate(raw)}
    return {}


def _validate_label_file(label: Path, names: dict[int, str]) -> list[str]:
    errors: list[str] = []
    for line_no, line in enumerate(label.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 5:
            errors.append(f"{label}:{line_no}: expected 5 YOLO fields")
            continue
        try:
            class_id = int(parts[0])
            values = [float(v) for v in parts[1:]]
        except ValueError:
            errors.append(f"{label}:{line_no}: non-numeric label field")
            continue
        if class_id not in names:
            errors.append(f"{label}:{line_no}: class id {class_id} not in names")
        if any(v < 0.0 or v > 1.0 for v in values):
            errors.append(f"{label}:{line_no}: normalized bbox values must be within [0, 1]")
    return errors


def main() -> int:
    args = build_parser().parse_args()
    errors = validate_dataset(args.data, allow_empty=args.allow_empty, require_reviewed=args.require_reviewed)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"dataset ok: {args.data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
