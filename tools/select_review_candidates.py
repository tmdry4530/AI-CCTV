#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank auto-labeled images for human review")
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def iter_images(root: Path) -> list[Path]:
    if root.is_file() and root.suffix.lower() in IMAGE_SUFFIXES:
        return [root]
    return sorted(p for p in root.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES)


def load_metadata(path: Path | None) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    if path is None or not path.exists():
        return grouped
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        grouped[str(row.get("image", ""))].append(row)
    return grouped


def score_image(image: Path, labels_dir: Path, metadata: dict[str, list[dict[str, object]]], class_counts: Counter[str]) -> tuple[float, str]:
    score = 0.0
    reasons: list[str] = []
    label = labels_dir / f"{image.stem}.txt"
    if not label.exists():
        score += 100.0
        reasons.append("missing_label")
    rows = metadata.get(str(image), [])
    if rows:
        low_conf = [float(r.get("confidence", 1.0)) for r in rows if float(r.get("confidence", 1.0)) < 0.45]
        if low_conf:
            score += 30.0 + (0.45 - min(low_conf)) * 100
            reasons.append("low_confidence")
        if len(rows) >= 5:
            score += 10.0
            reasons.append("high_object_count")
        for row in rows:
            cls = str(row.get("class_name", ""))
            if class_counts and class_counts[cls] <= max(1, min(class_counts.values())):
                score += 5.0
                reasons.append("class_imbalance")
    if "demo" in image.as_posix().lower() or "final" in image.as_posix().lower():
        score += 20.0
        reasons.append("demo_priority")
    return score, ",".join(sorted(set(reasons)))


def main() -> int:
    args = build_parser().parse_args()
    images = iter_images(args.images)
    metadata = load_metadata(args.metadata)
    class_counts: Counter[str] = Counter()
    for rows in metadata.values():
        for row in rows:
            class_counts[str(row.get("class_name", ""))] += 1
    ranked = []
    for image in images:
        score, reasons = score_image(image, args.labels, metadata, class_counts)
        ranked.append({"image": str(image), "score": f"{score:.3f}", "reasons": reasons})
    ranked.sort(key=lambda row: float(row["score"]), reverse=True)
    ranked = ranked[: args.limit]
    if args.dry_run or args.out is None:
        for row in ranked[:20]:
            print(row)
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "score", "reasons"])
        writer.writeheader()
        writer.writerows(ranked)
    print(f"wrote {len(ranked)} review candidates to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
