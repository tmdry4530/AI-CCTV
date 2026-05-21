from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_script(args: list[str]) -> subprocess.CompletedProcess[str]:
    repo = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def assert_clean_failure(result: subprocess.CompletedProcess[str], expected: str) -> None:
    combined = result.stdout + result.stderr
    assert result.returncode == 1
    assert "Traceback" not in combined
    assert expected in combined
    assert "ERROR:" in combined


def test_run_video_dry_run_missing_model_exits_without_traceback(tmp_path: Path) -> None:
    source = tmp_path / "sample.mp4"
    source.write_bytes(b"not a real video; dry-run only")
    result = run_script([
        "scripts/run_video.py",
        "--source",
        str(source),
        "--config",
        "configs/demo_mac.yaml",
        "--dry-run",
    ])
    assert_clean_failure(result, "Model file not found")


def test_run_video_dry_run_missing_sample_video_exits_clearly() -> None:
    result = run_script([
        "scripts/run_video.py",
        "--source",
        "data/samples/final_demo.mp4",
        "--config",
        "configs/demo_mac.yaml",
        "--dry-run",
    ])
    assert_clean_failure(result, "Video source not found")


def test_run_video_dry_run_missing_config_exits_clearly(tmp_path: Path) -> None:
    source = tmp_path / "sample.mp4"
    source.write_bytes(b"not a real video; dry-run only")
    result = run_script([
        "scripts/run_video.py",
        "--source",
        str(source),
        "--config",
        str(tmp_path / "missing.yaml"),
        "--dry-run",
    ])
    assert_clean_failure(result, "Config file not found")


def test_run_webcam_dry_run_missing_model_exits_without_traceback() -> None:
    result = run_script(["scripts/run_webcam.py", "--config", "configs/demo_mac.yaml", "--dry-run"])
    assert_clean_failure(result, "Model file not found")
