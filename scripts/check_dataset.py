from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
EXPECTED_NAMES = {0: "person", 1: "bag", 2: "laptop", 3: "cell_phone"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check YOLO dataset structure and label sanity.")
    parser.add_argument("--data", type=Path, default=Path("data") / "datasets" / "ai_cctv.yaml")
    parser.add_argument("--allow-empty", action="store_true", help="Allow empty splits for scaffold checks.")
    return parser


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(
            f"Dataset yaml does not exist yet: {path}. Create it after split_dataset.py or use --help."
        )
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit("PyYAML is required for dataset checking. Install requirements.txt.") from exc
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"Dataset yaml must be a mapping: {path}")
    return data


def dataset_root(data_path: Path, data: dict[str, Any]) -> Path:
    raw_root = Path(str(data.get("path", data_path.parent)))
    if not raw_root.is_absolute():
        candidate = data_path.parent / raw_root
        if candidate.exists():
            return candidate
        return raw_root
    return raw_root


def names_mapping(data: dict[str, Any]) -> dict[int, str]:
    names = data.get("names")
    if isinstance(names, list):
        return {index: str(name) for index, name in enumerate(names)}
    if isinstance(names, dict):
        return {int(index): str(name) for index, name in names.items()}
    raise SystemExit("Dataset yaml must define names as list or mapping.")


def check_label_file(path: Path, class_count: int) -> list[str]:
    errors: list[str] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 5:
            errors.append(f"{path}:{line_number}: expected 5 YOLO columns, got {len(parts)}")
            continue
        try:
            class_id = int(parts[0])
            coords = [float(value) for value in parts[1:]]
        except ValueError:
            errors.append(f"{path}:{line_number}: non-numeric label value")
            continue
        if class_id < 0 or class_id >= class_count:
            errors.append(f"{path}:{line_number}: class id {class_id} outside 0..{class_count - 1}")
        if any(value < 0.0 or value > 1.0 for value in coords):
            errors.append(f"{path}:{line_number}: normalized coordinates must be within [0, 1]")
        if coords[2] <= 0.0 or coords[3] <= 0.0:
            errors.append(f"{path}:{line_number}: width/height must be positive")
    return errors


def check_dataset(data_path: Path, *, allow_empty: bool = False) -> list[str]:
    data = load_yaml(data_path)
    root = dataset_root(data_path, data)
    names = names_mapping(data)
    errors: list[str] = []
    for class_id, name in EXPECTED_NAMES.items():
        if names.get(class_id) != name:
            errors.append(f"names[{class_id}] should be {name!r}, got {names.get(class_id)!r}")
    for split in ("train", "val", "test"):
        image_rel = Path(str(data.get(split, f"images/{split}")))
        image_dir = root / image_rel
        label_dir = root / "labels" / split
        if not image_dir.exists():
            errors.append(f"missing image directory: {image_dir}")
            continue
        if not label_dir.exists():
            errors.append(f"missing label directory: {label_dir}")
            continue
        images = sorted(path for path in image_dir.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)
        if not images and not allow_empty:
            errors.append(f"no images found in {image_dir}")
        for image in images:
            label = label_dir / image.relative_to(image_dir).with_suffix(".txt")
            if not label.exists():
                errors.append(f"missing label for image {image}: {label}")
                continue
            errors.extend(check_label_file(label, len(names)))
    return errors


def main() -> int:
    args = build_parser().parse_args()
    errors = check_dataset(args.data, allow_empty=args.allow_empty)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"Dataset check passed: {args.data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
