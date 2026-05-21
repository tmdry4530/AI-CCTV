from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.split_dataset import split_reviewed_dataset


def write_reviewed_pair(source: Path, group: str, frame: str = "frame_000001.jpg") -> None:
    image = source / "images" / group / frame
    label = source / "labels" / group / Path(frame).with_suffix(".txt")
    image.parent.mkdir(parents=True, exist_ok=True)
    label.parent.mkdir(parents=True, exist_ok=True)
    image.write_bytes(b"fake image")
    label.write_text("0 0.5 0.5 0.2 0.2\n", encoding="utf-8")


def read_split_manifest(out: Path) -> list[dict[str, str]]:
    with (out / "split_manifest.csv").open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def test_by_video_split_keeps_source_group_in_single_split(tmp_path: Path) -> None:
    source = tmp_path / "reviewed"
    for group in ("mac_bag_owner_leave_01", "mac_bag_theft_suspected_01", "mac_empty_scene_01"):
        write_reviewed_pair(source, group, "frame_000001.jpg")
        write_reviewed_pair(source, group, "frame_000002.jpg")
    out = tmp_path / "datasets" / "ai_cctv"

    split_reviewed_dataset(source=source, out=out, strategy="by-video", clean=True)

    rows = read_split_manifest(out)
    groups: dict[str, set[str]] = {}
    for row in rows:
        groups.setdefault(row["source_group"], set()).add(row["split"])
    assert groups
    assert all(len(splits) == 1 for splits in groups.values())


def test_empty_reviewed_source_fails_clearly(tmp_path: Path) -> None:
    source = tmp_path / "reviewed"
    source.mkdir()
    with pytest.raises(SystemExit, match="No reviewed image/label pairs"):
        split_reviewed_dataset(source=source, out=tmp_path / "out", strategy="by-video")


def test_by_video_split_fails_when_source_group_cannot_be_inferred(tmp_path: Path) -> None:
    source = tmp_path / "reviewed"
    image = source / "images" / "frame_000001.jpg"
    label = source / "labels" / "frame_000001.txt"
    image.parent.mkdir(parents=True)
    label.parent.mkdir(parents=True)
    image.write_bytes(b"fake image")
    label.write_text("0 0.5 0.5 0.2 0.2\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="Cannot infer source video/scenario group"):
        split_reviewed_dataset(source=source, out=tmp_path / "out", strategy="by-video")


def test_dataset_yaml_written_correctly(tmp_path: Path) -> None:
    source = tmp_path / "reviewed"
    write_reviewed_pair(source, "mac_bag_owner_leave_01")
    write_reviewed_pair(source, "mac_empty_scene_01")
    out = tmp_path / "datasets" / "ai_cctv"

    result = split_reviewed_dataset(source=source, out=out, strategy="by-video")

    yaml_text = result.yaml_path.read_text(encoding="utf-8")
    assert "path: ai_cctv" in yaml_text
    assert "train: images/train" in yaml_text
    assert "val: images/val" in yaml_text
    assert "test: images/test" in yaml_text
    assert "0: person" in yaml_text
    assert "3: cell_phone" in yaml_text
