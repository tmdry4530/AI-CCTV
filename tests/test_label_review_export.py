from __future__ import annotations

import json
from pathlib import Path

from tools.label_review_app import export_reviewed_pairs


def write_pair(image_root: Path, label_root: Path, relative: str) -> Path:
    image = image_root / relative
    label = label_root / Path(relative).with_suffix(".txt")
    image.parent.mkdir(parents=True, exist_ok=True)
    label.parent.mkdir(parents=True, exist_ok=True)
    image.write_bytes(b"fake image")
    label.write_text("0 0.5 0.5 0.2 0.2\n", encoding="utf-8")
    return image


def test_reviewed_export_creates_accepted_image_label_pairs(tmp_path: Path) -> None:
    image_root = tmp_path / "frames"
    label_root = tmp_path / "autolabels" / "labels"
    accepted = write_pair(image_root, label_root, "mac_bag_owner_leave_01/frame_000001.jpg")
    rejected = write_pair(image_root, label_root, "mac_bag_owner_leave_01/frame_000002.jpg")
    state_path = tmp_path / "review_state.json"
    state_path.write_text(
        json.dumps(
            {
                "mac_bag_owner_leave_01/frame_000001.jpg": "accepted",
                str(rejected): "rejected",
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "reviewed"

    result = export_reviewed_pairs(
        image_root=image_root,
        label_root=label_root,
        state_path=state_path,
        output_dir=output,
    )

    assert result.accepted == 1
    assert result.rejected == 1
    assert (output / "images" / "mac_bag_owner_leave_01" / accepted.name).exists()
    assert (output / "labels" / "mac_bag_owner_leave_01" / accepted.with_suffix(".txt").name).exists()
    assert not (output / "images" / "mac_bag_owner_leave_01" / rejected.name).exists()
    manifest = (output / "review_manifest.csv").read_text(encoding="utf-8")
    assert "source_group" in manifest
    assert "mac_bag_owner_leave_01" in manifest


def test_reviewed_export_skips_accepted_items_with_missing_labels(tmp_path: Path) -> None:
    image_root = tmp_path / "frames"
    label_root = tmp_path / "autolabels" / "labels"
    image = image_root / "mac_bag_owner_leave_01" / "frame_000001.jpg"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"fake image")
    state_path = tmp_path / "review_state.json"
    state_path.write_text(json.dumps({"mac_bag_owner_leave_01/frame_000001.jpg": "accepted"}), encoding="utf-8")

    result = export_reviewed_pairs(
        image_root=image_root,
        label_root=label_root,
        state_path=state_path,
        output_dir=tmp_path / "reviewed",
    )

    assert result.accepted == 0
    assert result.missing_labels == 1
