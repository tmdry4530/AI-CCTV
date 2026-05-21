from __future__ import annotations

import argparse
import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Split reviewed images/labels into a YOLO dataset scaffold.")
    parser.add_argument("--source", type=Path, required=True, help="Reviewed dataset source directory.")
    parser.add_argument("--out", type=Path, required=True, help="Output dataset root, e.g. data/datasets/ai_cctv")
    parser.add_argument("--strategy", choices=["by-video", "simple"], default="by-video")
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def find_pairs(source: Path) -> list[tuple[Path, Path]]:
    if not source.exists():
        raise SystemExit(f"Reviewed source does not exist yet: {source}")
    images = sorted(path for path in source.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)
    pairs: list[tuple[Path, Path]] = []
    for image in images:
        candidates = [image.with_suffix(".txt"), source / "labels" / image.relative_to(source).with_suffix(".txt")]
        label = next((candidate for candidate in candidates if candidate.exists()), None)
        if label is not None:
            pairs.append((image, label))
    return pairs


def choose_split(index: int, total: int, val_ratio: float, test_ratio: float) -> str:
    if total <= 0:
        return "train"
    fraction = index / total
    if fraction < test_ratio:
        return "test"
    if fraction < test_ratio + val_ratio:
        return "val"
    return "train"


def write_yaml(out: Path) -> None:
    yaml_path = out.parent / "ai_cctv.yaml"
    yaml_path.write_text(
        "path: ai_cctv\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n\n"
        "names:\n"
        "  0: person\n"
        "  1: bag\n"
        "  2: laptop\n"
        "  3: cell_phone\n",
        encoding="utf-8",
    )


def main() -> int:
    args = build_parser().parse_args()
    pairs = find_pairs(args.source)
    if args.dry_run:
        print(f"Would split {len(pairs)} reviewed image/label pairs from {args.source} to {args.out}")
        return 0
    if not pairs:
        raise SystemExit(
            f"No reviewed image/label pairs found in {args.source}. Run auto-labeling and review first."
        )
    for split in ("train", "val", "test"):
        (args.out / "images" / split).mkdir(parents=True, exist_ok=True)
        (args.out / "labels" / split).mkdir(parents=True, exist_ok=True)
    total = len(pairs)
    for index, (image, label) in enumerate(pairs):
        split = choose_split(index, total, args.val_ratio, args.test_ratio)
        shutil.copy2(image, args.out / "images" / split / image.name)
        shutil.copy2(label, args.out / "labels" / split / f"{image.stem}.txt")
    write_yaml(args.out)
    print(f"Split {total} pairs into {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
