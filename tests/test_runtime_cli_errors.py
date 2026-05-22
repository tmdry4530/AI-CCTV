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


def write_runtime_config(tmp_path: Path) -> Path:
    model = tmp_path / "best_demo.pt"
    model.write_bytes(b"dry-run placeholder model")
    config = tmp_path / "demo.yaml"
    config.write_text(
        f"""
camera:
  source: 0
  width: 1280
  height: 720
  fps: 15
model:
  path: {model.as_posix()}
  device: cpu
  imgsz: 640
  conf_default: 0.35
  iou: 0.5
classes:
  person: 0
  bag: 1
  laptop: 2
  cell_phone: 3
thresholds:
  owner_min_seconds: 3.0
  abandoned_min_seconds: 5.0
  suspicious_min_seconds: 1.5
  missing_grace_seconds: 2.0
tracker:
  type: botsort
  fallback: bytetrack
paths:
  logs: {tmp_path.joinpath("events.csv").as_posix()}
  snapshots: {tmp_path.joinpath("snapshots").as_posix()}
""".strip(),
        encoding="utf-8",
    )
    return config


def assert_clean_success(result: subprocess.CompletedProcess[str], expected: str) -> None:
    combined = result.stdout + result.stderr
    assert result.returncode == 0
    assert "Traceback" not in combined
    assert expected in combined


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


def test_run_video_dry_run_succeeds_when_source_and_model_exist(tmp_path: Path) -> None:
    source = tmp_path / "sample.mp4"
    source.write_bytes(b"dry-run placeholder video")
    config = write_runtime_config(tmp_path)

    result = run_script([
        "scripts/run_video.py",
        "--source",
        str(source),
        "--config",
        str(config),
        "--dry-run",
    ])

    assert_clean_success(result, "Runtime dry-run OK")


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


def test_run_webcam_dry_run_succeeds_when_model_exists(tmp_path: Path) -> None:
    config = write_runtime_config(tmp_path)

    result = run_script(["scripts/run_webcam.py", "--config", str(config), "--dry-run"])

    assert_clean_success(result, "Runtime dry-run OK")


def test_run_dashboard_dry_run_prints_streamlit_command() -> None:
    result = run_script(["scripts/run_dashboard.py", "--dry-run"])

    assert_clean_success(result, "streamlit run")
