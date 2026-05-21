#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Streamlit label review UI for accept/reject review state")
    parser.add_argument("--images", type=Path, default=Path("data") / "frames")
    parser.add_argument("--labels", type=Path, default=Path("data") / "autolabels" / "labels")
    parser.add_argument("--state", type=Path, default=Path("data") / "review_state.json")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def iter_images(root: Path) -> list[Path]:
    if root.is_file() and root.suffix.lower() in IMAGE_SUFFIXES:
        return [root]
    return sorted(p for p in root.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES) if root.exists() else []


def load_state(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    args = build_parser().parse_args()
    images = iter_images(args.images)
    if args.dry_run:
        print(f"label review inputs ok: images={len(images)} labels={args.labels} state={args.state}")
        return 0
    try:
        import streamlit as st  # type: ignore
    except Exception as exc:
        raise SystemExit(f"Streamlit is required for label review UI: {exc}") from exc

    st.set_page_config(page_title="AI CCTV Label Review", layout="wide")
    st.title("AI CCTV Label Review")
    st.caption("MVP supports image-level accept/reject; edit boxes in CVAT or another annotation tool.")
    state = load_state(args.state)
    if not images:
        st.info(f"No images found under {args.images}")
        return 0
    selected = st.selectbox("Image", images, format_func=lambda p: p.name)
    st.image(str(selected), use_container_width=True)
    label_path = args.labels / f"{selected.stem}.txt"
    if label_path.exists():
        st.code(label_path.read_text(encoding="utf-8") or "<empty label file>")
    else:
        st.warning(f"Missing label file: {label_path}")
    current = state.get(str(selected), "unreviewed")
    st.write(f"Current state: `{current}`")
    col1, col2, col3 = st.columns(3)
    if col1.button("Accept"):
        state[str(selected)] = "accepted"
        save_state(args.state, state)
        st.rerun()
    if col2.button("Reject"):
        state[str(selected)] = "rejected"
        save_state(args.state, state)
        st.rerun()
    if col3.button("Mark val/test candidate"):
        state[str(selected)] = "candidate_human_review_required"
        save_state(args.state, state)
        st.rerun()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
