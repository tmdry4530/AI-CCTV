from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "run_webcam.py",
    "preview_camera.py",
    "run_video.py",
    "run_dashboard.py",
    "record_webcam.py",
    "extract_frames.py",
    "auto_label_yolo.py",
    "split_dataset.py",
    "check_dataset.py",
    "train_yolo.py",
    "validate_yolo.py",
    "benchmark_model.py",
]
TOOLS = ["label_review_app.py"]


def test_core_scripts_support_help() -> None:
    repo = Path(__file__).resolve().parents[1]
    for script in SCRIPTS:
        result = subprocess.run(
            [sys.executable, str(repo / "scripts" / script), "--help"],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        assert result.returncode == 0, f"{script} --help failed: {result.stderr}"
        assert "usage:" in result.stdout.lower()


def test_tools_support_help_without_streamlit_import() -> None:
    repo = Path(__file__).resolve().parents[1]
    for tool in TOOLS:
        result = subprocess.run(
            [sys.executable, str(repo / "tools" / tool), "--help"],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        assert result.returncode == 0, f"{tool} --help failed: {result.stderr}"
        assert "usage:" in result.stdout.lower()
