"""Shared CLI helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def ensure_parent(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def add_common_config_arg(parser: Any) -> None:
    parser.add_argument("--config", type=Path, default=Path("configs") / "demo_mac.yaml", help="Path to YAML config")
