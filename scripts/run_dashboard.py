from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _bootstrap import add_src_to_path

REPO_ROOT = add_src_to_path()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch the Streamlit AI CCTV dashboard.")
    parser.add_argument("--module", type=Path, default=REPO_ROOT / "src" / "ai_cctv" / "app.py")
    parser.add_argument(
        "--no-launch",
        action="store_true",
        help="Validate command only; do not start Streamlit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Alias for --no-launch; validate the dashboard command without starting Streamlit.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.module.exists():
        print(f"ERROR: Dashboard module not found: {args.module}", file=sys.stderr)
        return 1
    if args.no_launch or args.dry_run:
        print(f"streamlit run {args.module}")
        return 0
    try:
        import streamlit  # noqa: F401  # type: ignore
    except ImportError as exc:
        message = "streamlit is required. Install requirements.txt before dashboard launch."
        raise SystemExit(message) from exc
    return subprocess.call([sys.executable, "-m", "streamlit", "run", str(args.module)])


if __name__ == "__main__":
    raise SystemExit(main())
