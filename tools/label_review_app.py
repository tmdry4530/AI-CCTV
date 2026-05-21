from __future__ import annotations

import json
import sys
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASS_NAMES = {0: "person", 1: "bag", 2: "laptop", 3: "cell_phone"}


def list_images(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)


def label_for_image(image: Path, image_root: Path, label_root: Path) -> Path:
    return label_root / image.relative_to(image_root).with_suffix(".txt")


def read_labels(label_path: Path) -> list[str]:
    if not label_path.exists():
        return []
    return [line.strip() for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    try:
        import streamlit as st  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit("streamlit is required for label review. Install requirements.txt.") from exc

    st.set_page_config(page_title="AI CCTV Label Review", layout="wide")
    st.title("AI CCTV Label Review")
    st.caption("MVP review: accept/reject image-level labels before validation/test use.")

    image_root = Path(st.sidebar.text_input("Image root", "data/frames"))
    label_root = Path(st.sidebar.text_input("Label root", "data/autolabels/labels"))
    state_path = Path(st.sidebar.text_input("Review state", "data/reviewed/review_state.json"))
    state_path.parent.mkdir(parents=True, exist_ok=True)

    state: dict[str, str] = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))

    images = list_images(image_root)
    if not images:
        st.warning(f"No images found under {image_root}")
        st.info("Run record_webcam.py, extract_frames.py, and auto_label_yolo.py first.")
        return

    status_filter = st.sidebar.selectbox("Status", ["all", "unreviewed", "accepted", "rejected"])
    filtered = []
    for image in images:
        status = state.get(str(image), "unreviewed")
        if status_filter == "all" or status == status_filter:
            filtered.append(image)
    if not filtered:
        st.info("No images match this filter.")
        return

    index = st.sidebar.number_input("Image index", min_value=0, max_value=len(filtered) - 1, value=0)
    image = filtered[int(index)]
    label_path = label_for_image(image, image_root, label_root)
    labels = read_labels(label_path)
    current_status = state.get(str(image), "unreviewed")

    col_image, col_meta = st.columns([2, 1])
    with col_image:
        st.image(str(image), caption=f"{image.name} ({current_status})", use_container_width=True)
    with col_meta:
        st.write("Image", str(image))
        st.write("Label", str(label_path))
        if not label_path.exists():
            st.error("Missing label file")
        else:
            st.code("\n".join(labels) or "<empty label file>")
        if labels:
            st.write("Classes")
            for line in labels:
                class_id = int(line.split()[0])
                st.write(f"- {class_id}: {CLASS_NAMES.get(class_id, 'unknown')}")
        accept, reject = st.columns(2)
        if accept.button("Accept"):
            state[str(image)] = "accepted"
            state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
            st.rerun()
        if reject.button("Reject"):
            state[str(image)] = "rejected"
            state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
            st.rerun()

    st.subheader("Review progress")
    accepted = sum(1 for value in state.values() if value == "accepted")
    rejected = sum(1 for value in state.values() if value == "rejected")
    st.write({"total_images": len(images), "accepted": accepted, "rejected": rejected})


def print_help() -> None:
    print(
        "usage: streamlit run tools/label_review_app.py\n\n"
        "Image-level label review UI for AI CCTV auto-label outputs.\n"
        "Configure paths from the Streamlit sidebar:\n"
        "  Image root: data/frames\n"
        "  Label root: data/autolabels/labels\n"
        "  Review state: data/reviewed/review_state.json"
    )


if __name__ == "__main__":
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        print_help()
        raise SystemExit(0)
    main()
