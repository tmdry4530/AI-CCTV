from __future__ import annotations

import sys

from ai_cctv.config import load_config, select_device


def test_demo_mac_config_loads() -> None:
    config = load_config("configs/demo_mac.yaml")
    assert config.model.path.as_posix() == "models/best_demo.pt"
    assert config.classes["person"] == 0
    assert config.paths.logs.as_posix() == "data/logs/events.csv"


def test_dev_windows_config_loads() -> None:
    config = load_config("configs/dev_windows.yaml")
    assert config.model.device == "cuda"
    assert config.camera.width == 1280


def test_select_device_auto_falls_back_to_cpu_when_torch_missing(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "torch", None)
    assert select_device("auto") == "cpu"
