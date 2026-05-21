from __future__ import annotations

import argparse
import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLITS = ("train", "val", "test")


@dataclass(frozen=True, slots=True)
class ReviewedPair:
    image: Path
    label: Path
    source_group: str | None = None


@dataclass(slots=True)
class SplitResult:
    total_pairs: int
    groups: dict[str, str]
    yaml_path: Path
    manifest_path: Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Split reviewed images/labels into a YOLO dataset scaffold.")
    parser.add_argument("--source", type=Path, required=True, help="Reviewed dataset source directory.")
    parser.add_argument("--out", type=Path, required=True, help="Output dataset root, e.g. data/datasets/ai_cctv")
    parser.add_argument("--strategy", choices=["by-video", "simple"], default="by-video")
    parser.add_argument("--manifest", type=Path, default=None, help="Optional reviewed manifest with image,label,source_group columns.")
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--clean", action="store_true", help="Remove previous output images/labels before copying.")
    return parser


def _relative(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return Path(path.name)


def _manifest_key(path: Path) -> str:
    return Path(path).as_posix()


def load_manifest(source: Path, manifest: Path | None = None) -> dict[str, tuple[Path | None, str]]:
    manifest_path = manifest or source / "review_manifest.csv"
    if not manifest_path.exists():
        return {}
    rows: dict[str, tuple[Path | None, str]] = {}
    with manifest_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            image_raw = (row.get("image") or "").strip()
            if not image_raw:
                continue
            group = (row.get("source_group") or "").strip()
            label_raw = (row.get("label") or "").strip()
            label = Path(label_raw) if label_raw else None
            image_path = Path(image_raw)
            candidates = {
                _manifest_key(image_path),
                _manifest_key(source / image_path),
                image_path.name,
            }
            for key in candidates:
                rows[key] = (label, group)
    return rows


def infer_source_group(image: Path, source: Path, manifest_groups: dict[str, tuple[Path | None, str]]) -> str | None:
    candidates = [image, _relative(image, source), image.name]
    images_root = source / "images"
    if images_root.exists():
        candidates.append(_relative(image, images_root))
    for candidate in candidates:
        manifest_entry = manifest_groups.get(_manifest_key(Path(candidate)))
        if manifest_entry and manifest_entry[1]:
            return manifest_entry[1]
    relative_to_images = _relative(image, images_root) if images_root.exists() else _relative(image, source)
    if len(relative_to_images.parts) > 1:
        return relative_to_images.parts[0]
    stem = relative_to_images.stem
    match = re.match(r"(?P<group>.+?)(?:[_-](?:frame)?\d{4,})$", stem)
    if match:
        group = match.group("group")
        if group.lower() in {"frame", "image", "img"}:
            return None
        return group
    if image.parent != source and image.parent != images_root:
        return image.parent.name
    return None


def label_candidates(image: Path, source: Path, manifest_groups: dict[str, tuple[Path | None, str]]) -> list[Path]:
    candidates: list[Path] = []
    for key in (_manifest_key(image), _manifest_key(_relative(image, source)), image.name):
        entry = manifest_groups.get(key)
        if entry and entry[0] is not None:
            label = entry[0]
            candidates.append(label if label.is_absolute() else source / label)
    images_root = source / "images"
    if images_root.exists():
        relative = _relative(image, images_root)
        candidates.append(source / "labels" / relative.with_suffix(".txt"))
    candidates.extend(
        [
            image.with_suffix(".txt"),
            source / "labels" / _relative(image, source).with_suffix(".txt"),
            source / "labels" / f"{image.stem}.txt",
        ]
    )
    # Preserve order while de-duplicating.
    seen: set[Path] = set()
    unique: list[Path] = []
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            unique.append(candidate)
    return unique


def find_pairs(source: Path, manifest: Path | None = None) -> list[ReviewedPair]:
    if not source.exists():
        raise SystemExit(f"Reviewed source does not exist yet: {source}")
    manifest_groups = load_manifest(source, manifest)
    image_root = source / "images" if (source / "images").exists() else source
    images = sorted(path for path in image_root.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)
    pairs: list[ReviewedPair] = []
    for image in images:
        label = next((candidate for candidate in label_candidates(image, source, manifest_groups) if candidate.exists()), None)
        if label is None:
            continue
        pairs.append(ReviewedPair(image=image, label=label, source_group=infer_source_group(image, source, manifest_groups)))
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


def assign_group_splits(groups: list[str], val_ratio: float, test_ratio: float) -> dict[str, str]:
    if not groups:
        return {}
    unique = sorted(set(groups))
    total = len(unique)
    test_count = int(round(total * test_ratio))
    val_count = int(round(total * val_ratio))
    if test_ratio > 0 and total >= 3:
        test_count = max(1, test_count)
    if val_ratio > 0 and total >= 2:
        val_count = max(1, val_count)
    if total > 1:
        while test_count + val_count >= total:
            if val_count > 0:
                val_count -= 1
            elif test_count > 0:
                test_count -= 1
            else:
                break
    assignments: dict[str, str] = {}
    for index, group in enumerate(unique):
        if index < test_count:
            split = "test"
        elif index < test_count + val_count:
            split = "val"
        else:
            split = "train"
        assignments[group] = split
    return assignments


def write_yaml(out: Path) -> Path:
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
    return yaml_path


def prepare_output(out: Path, *, clean: bool) -> None:
    if clean:
        for child in (out / "images", out / "labels"):
            if child.exists():
                shutil.rmtree(child)
    for split in SPLITS:
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)


def output_relative(pair: ReviewedPair, source: Path) -> Path:
    images_root = source / "images"
    if images_root.exists():
        relative = _relative(pair.image, images_root)
    else:
        relative = _relative(pair.image, source)
    if len(relative.parts) > 1:
        return relative
    if pair.source_group:
        return Path(pair.source_group) / pair.image.name
    return Path(pair.image.name)


def split_reviewed_dataset(
    *,
    source: Path,
    out: Path,
    strategy: str = "by-video",
    manifest: Path | None = None,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1,
    dry_run: bool = False,
    clean: bool = False,
) -> SplitResult:
    pairs = find_pairs(source, manifest)
    if not pairs:
        raise SystemExit(f"No reviewed image/label pairs found in {source}. Export accepted reviews first.")
    group_assignments: dict[str, str] = {}
    if strategy == "by-video":
        missing_group = [pair.image for pair in pairs if not pair.source_group]
        if missing_group:
            examples = ", ".join(str(path) for path in missing_group[:3])
            raise SystemExit(
                "Cannot infer source video/scenario group for reviewed images. "
                f"Examples: {examples}. Organize images under group folders or provide review_manifest.csv."
            )
        group_assignments = assign_group_splits(
            [pair.source_group or "" for pair in pairs], val_ratio=val_ratio, test_ratio=test_ratio
        )
    if dry_run:
        yaml_path = out.parent / "ai_cctv.yaml"
        manifest_path = out / "split_manifest.csv"
        return SplitResult(total_pairs=len(pairs), groups=group_assignments, yaml_path=yaml_path, manifest_path=manifest_path)

    prepare_output(out, clean=clean)
    split_manifest = out / "split_manifest.csv"
    with split_manifest.open("w", newline="", encoding="utf-8") as manifest_file:
        writer = csv.DictWriter(
            manifest_file, fieldnames=["image", "label", "source_group", "split", "source_image", "source_label"]
        )
        writer.writeheader()
        for index, pair in enumerate(pairs):
            if strategy == "by-video":
                split = group_assignments[pair.source_group or ""]
            else:
                split = choose_split(index, len(pairs), val_ratio, test_ratio)
            relative = output_relative(pair, source)
            destination_image = out / "images" / split / relative
            destination_label = out / "labels" / split / relative.with_suffix(".txt")
            destination_image.parent.mkdir(parents=True, exist_ok=True)
            destination_label.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pair.image, destination_image)
            shutil.copy2(pair.label, destination_label)
            writer.writerow(
                {
                    "image": destination_image.relative_to(out).as_posix(),
                    "label": destination_label.relative_to(out).as_posix(),
                    "source_group": pair.source_group or "",
                    "split": split,
                    "source_image": str(pair.image),
                    "source_label": str(pair.label),
                }
            )
    yaml_path = write_yaml(out)
    return SplitResult(total_pairs=len(pairs), groups=group_assignments, yaml_path=yaml_path, manifest_path=split_manifest)


def main() -> int:
    args = build_parser().parse_args()
    result = split_reviewed_dataset(
        source=args.source,
        out=args.out,
        strategy=args.strategy,
        manifest=args.manifest,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        dry_run=args.dry_run,
        clean=args.clean,
    )
    if args.dry_run:
        print(f"Would split {result.total_pairs} reviewed image/label pairs from {args.source} to {args.out}")
        if args.strategy == "by-video":
            print(f"source groups: {result.groups}")
        return 0
    print(f"Split {result.total_pairs} pairs into {args.out}")
    print(f"Dataset yaml: {result.yaml_path}")
    print(f"Split manifest: {result.manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
