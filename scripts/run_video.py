from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from ai_cctv.cli import run_runtime  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AI CCTV on a video file.")
    parser.add_argument("--source", type=Path, required=True, help="Video file path, e.g. data/samples/final_demo.mp4")
    parser.add_argument("--config", type=Path, default=Path("configs") / "demo_mac.yaml")
    parser.add_argument("--max-frames", type=int, default=None, help="Stop after N frames for smoke tests.")
    parser.add_argument("--no-display", action="store_true", help="Disable OpenCV window.")
    parser.add_argument("--no-snapshots", action="store_true", help="Do not save event snapshots.")
    parser.add_argument("--dry-run", action="store_true", help="Validate config/model/source and exit.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return run_runtime(
        config_path=args.config,
        source=args.source,
        display=not args.no_display,
        save_snapshots=not args.no_snapshots,
        max_frames=args.max_frames,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    raise SystemExit(main())
