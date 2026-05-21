#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Split image/label dataset by source group to avoid near-duplicate leakage")
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.15)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def source_group(path: Path) -> str:
    stem = path.stem
    parts = stem.split("_")
    return "_".join(parts[:2]) if len(parts) >= 2 else parts[0]


def choose_split(group: str, val_ratio: float, test_ratio: float) -> str:
    bucket = int(hashlib.sha1(group.encode("utf-8")).hexdigest(), 16) % 10000 / 10000.0
    if bucket < test_ratio:
        return "test"
    if bucket < test_ratio + val_ratio:
        return "val"
    return "train"


def main() -> int:
    args = build_parser().parse_args()
    images = sorted(p for p in args.images.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES)
    assignments = [(image, choose_split(source_group(image), args.val_ratio, args.test_ratio)) for image in images]
    if args.dry_run:
        counts = {split: sum(1 for _, s in assignments if s == split) for split in ("train", "val", "test")}
        print(counts)
        return 0
    for image, split in assignments:
        label = args.labels / f"{image.stem}.txt"
        image_out = args.out / "images" / split / image.name
        label_out = args.out / "labels" / split / label.name
        image_out.parent.mkdir(parents=True, exist_ok=True)
        label_out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image, image_out)
        if label.exists():
            shutil.copy2(label, label_out)
        else:
            label_out.write_text("", encoding="utf-8")
    print(f"wrote split dataset to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
