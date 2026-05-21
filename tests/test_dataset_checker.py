from pathlib import Path

from scripts.check_dataset import check_dataset


def test_dataset_checker_accepts_valid_yolo_dataset(tmp_path: Path) -> None:
    root = tmp_path / "ai_cctv"
    for split in ("train", "val", "test"):
        (root / "images" / split).mkdir(parents=True)
        (root / "labels" / split).mkdir(parents=True)
        (root / "images" / split / f"{split}.jpg").write_bytes(b"fake")
        (root / "labels" / split / f"{split}.txt").write_text("0 0.5 0.5 0.2 0.2\n", encoding="utf-8")
    yaml_path = tmp_path / "ai_cctv.yaml"
    yaml_path.write_text(
        "path: ai_cctv\n"
        "train: images/train\n"
        "val: images/val\n"
        "test: images/test\n"
        "names:\n"
        "  0: person\n"
        "  1: bag\n"
        "  2: laptop\n"
        "  3: cell_phone\n",
        encoding="utf-8",
    )
    assert check_dataset(yaml_path) == []


def test_dataset_checker_reports_invalid_label(tmp_path: Path) -> None:
    root = tmp_path / "ai_cctv"
    for split in ("train", "val", "test"):
        (root / "images" / split).mkdir(parents=True)
        (root / "labels" / split).mkdir(parents=True)
        (root / "images" / split / f"{split}.jpg").write_bytes(b"fake")
        (root / "labels" / split / f"{split}.txt").write_text("9 1.2 0.5 0.2 0.2\n", encoding="utf-8")
    yaml_path = tmp_path / "ai_cctv.yaml"
    yaml_path.write_text(
        "path: ai_cctv\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n"
        "  0: person\n  1: bag\n  2: laptop\n  3: cell_phone\n",
        encoding="utf-8",
    )
    errors = check_dataset(yaml_path)
    assert any("class id 9" in error for error in errors)
    assert any("within [0, 1]" in error for error in errors)
