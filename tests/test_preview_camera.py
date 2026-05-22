from __future__ import annotations

import pytest

from scripts.preview_camera import build_parser, preview_source


def test_preview_camera_parser_defaults_to_webcam_zero() -> None:
    args = build_parser().parse_args([])

    assert args.source == "0"
    assert preview_source(args.source) == 0
    assert args.width == 1280
    assert args.height == 720
    assert args.fps == 15


def test_preview_camera_parser_accepts_capture_settings() -> None:
    args = build_parser().parse_args(
        ["--source", "1", "--width", "640", "--height", "480", "--fps", "30"]
    )

    assert preview_source(args.source) == 1
    assert args.width == 640
    assert args.height == 480
    assert args.fps == 30


def test_preview_camera_parser_rejects_non_positive_capture_settings() -> None:
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["--width", "0"])
