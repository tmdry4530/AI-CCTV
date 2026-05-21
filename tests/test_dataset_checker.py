from pathlib import Path

from scripts.check_dataset import validate_dataset


def test_dataset_checker_accepts_valid_yolo_dataset(tmp_path: Path):
    root = tmp_path / "dataset"
    for split in ["train", "val", "test"]:
        (root / "images" / split).mkdir(parents=True)
        (root / "labels" / split).mkdir(parents=True)
        (root / "images" / split / f"sample_{split}.jpg").write_bytes(b"fake")
        (root / "labels" / split / f"sample_{split}.txt").write_text("0 0.5 0.5 0.2 0.2\n", encoding="utf-8")
    data = tmp_path / "ai_cctv.yaml"
    data.write_text(
        f"path: {root}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n  0: person\n  1: bag\n",
        encoding="utf-8",
    )
    assert validate_dataset(data) == []


def test_dataset_checker_rejects_bad_bbox(tmp_path: Path):
    root = tmp_path / "dataset"
    for split in ["train", "val", "test"]:
        (root / "images" / split).mkdir(parents=True)
        (root / "labels" / split).mkdir(parents=True)
    (root / "images" / "train" / "bad.jpg").write_bytes(b"fake")
    (root / "labels" / "train" / "bad.txt").write_text("0 1.5 0.5 0.2 0.2\n", encoding="utf-8")
    data = tmp_path / "ai_cctv.yaml"
    data.write_text(
        f"path: {root}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n  0: person\n",
        encoding="utf-8",
    )
    errors = validate_dataset(data, allow_empty=True)
    assert any("within [0, 1]" in error for error in errors)
