from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASS_NAMES = {0: "person", 1: "bag", 2: "laptop", 3: "cell_phone"}
DEFAULT_IMAGE_ROOT = Path("data") / "frames"
DEFAULT_LABEL_ROOT = Path("data") / "autolabels" / "labels"
DEFAULT_STATE_PATH = Path("data") / "reviewed" / "review_state.json"
DEFAULT_EXPORT_DIR = Path("data") / "reviewed"


@dataclass(slots=True)
class ExportResult:
    accepted: int = 0
    rejected: int = 0
    skipped_unreviewed: int = 0
    missing_labels: int = 0
    missing_groups: int = 0
    output_dir: Path = DEFAULT_EXPORT_DIR
    manifest_path: Path = DEFAULT_EXPORT_DIR / "review_manifest.csv"


@dataclass(slots=True)
class ExportRecord:
    image: Path
    label: Path
    source_group: str
    status: str


def list_images(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*") if path.suffix.lower() in IMAGE_EXTENSIONS)


def relative_to_root(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return Path(path.name)


def label_for_image(image: Path, image_root: Path, label_root: Path) -> Path:
    return label_root / relative_to_root(image, image_root).with_suffix(".txt")


def read_labels(label_path: Path) -> list[str]:
    if not label_path.exists():
        return []
    return [line.strip() for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_review_state(state_path: Path) -> dict[str, str]:
    if not state_path.exists():
        return {}
    data = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Review state must be a JSON object: {state_path}")
    return {str(key): str(value) for key, value in data.items()}


def save_review_state(state_path: Path, state: dict[str, str]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def review_status_for_image(state: dict[str, str], image: Path, image_root: Path) -> str:
    relative = relative_to_root(image, image_root)
    candidates = [str(image), str(relative), image.name]
    try:
        candidates.append(str(image.resolve()))
    except OSError:
        pass
    for key in candidates:
        if key in state:
            return state[key]
    return "unreviewed"


def infer_source_group(relative_image: Path) -> str | None:
    """Infer source video/scenario group from folder or extract_frames-style filename."""

    if len(relative_image.parts) > 1:
        return relative_image.parts[0]
    stem = relative_image.stem
    # extract_frames.py produces <source_stem>_<frame_index:06d>.jpg.
    for separator in ("_", "-"):
        if separator in stem:
            prefix, suffix = stem.rsplit(separator, 1)
            if suffix.isdigit() and len(suffix) >= 4 and prefix:
                if prefix.lower() in {"frame", "image", "img"}:
                    return None
                return prefix
    return stem


def export_reviewed_pairs(
    *,
    image_root: Path,
    label_root: Path,
    state_path: Path,
    output_dir: Path,
    clean: bool = False,
) -> ExportResult:
    """Copy accepted image/label pairs into a split_dataset.py-consumable reviewed tree.

    Output layout:

    ```text
    output_dir/
      images/<source_group>/<image>
      labels/<source_group>/<image>.txt
      review_manifest.csv
    ```
    """

    state = load_review_state(state_path)
    images = list_images(image_root)
    image_out = output_dir / "images"
    label_out = output_dir / "labels"
    manifest_path = output_dir / "review_manifest.csv"
    if clean:
        for path in (image_out, label_out, manifest_path):
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
    image_out.mkdir(parents=True, exist_ok=True)
    label_out.mkdir(parents=True, exist_ok=True)

    result = ExportResult(output_dir=output_dir, manifest_path=manifest_path)
    records: list[ExportRecord] = []
    for image in images:
        status = review_status_for_image(state, image, image_root)
        if status == "rejected":
            result.rejected += 1
            continue
        if status != "accepted":
            result.skipped_unreviewed += 1
            continue
        label = label_for_image(image, image_root, label_root)
        if not label.exists():
            result.missing_labels += 1
            continue
        relative = relative_to_root(image, image_root)
        group = infer_source_group(relative)
        if group is None:
            result.missing_groups += 1
            continue
        export_relative = Path(group) / relative.name
        destination_image = image_out / export_relative
        destination_label = label_out / export_relative.with_suffix(".txt")
        destination_image.parent.mkdir(parents=True, exist_ok=True)
        destination_label.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image, destination_image)
        shutil.copy2(label, destination_label)
        result.accepted += 1
        records.append(
            ExportRecord(
                image=destination_image.relative_to(output_dir),
                label=destination_label.relative_to(output_dir),
                source_group=group,
                status=status,
            )
        )

    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["image", "label", "source_group", "status"])
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "image": record.image.as_posix(),
                    "label": record.label.as_posix(),
                    "source_group": record.source_group,
                    "status": record.status,
                }
            )
    return result


def build_export_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export accepted AI CCTV label-review pairs.")
    parser.add_argument("--export", action="store_true", help="Run export mode instead of Streamlit UI.")
    parser.add_argument("--image-root", type=Path, default=DEFAULT_IMAGE_ROOT)
    parser.add_argument("--label-root", type=Path, default=DEFAULT_LABEL_ROOT)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_EXPORT_DIR)
    parser.add_argument("--clean", action="store_true", help="Remove previous exported images/labels first.")
    return parser


def run_export_cli(argv: list[str] | None = None) -> int:
    args = build_export_parser().parse_args(argv)
    if not args.export:
        print_help()
        return 0
    result = export_reviewed_pairs(
        image_root=args.image_root,
        label_root=args.label_root,
        state_path=args.state,
        output_dir=args.out,
        clean=args.clean,
    )
    print(f"Exported accepted pairs: {result.accepted}")
    print(f"Rejected excluded: {result.rejected}")
    print(f"Unreviewed skipped: {result.skipped_unreviewed}")
    print(f"Accepted with missing labels skipped: {result.missing_labels}")
    print(f"Accepted with unknown source groups skipped: {result.missing_groups}")
    print(f"Reviewed output: {result.output_dir}")
    print(f"Manifest: {result.manifest_path}")
    if result.accepted == 0:
        raise SystemExit("No accepted image/label pairs were exported. Review labels first.")
    return 0


def main() -> None:
    try:
        import streamlit as st  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit("streamlit is required for label review. Install requirements.txt.") from exc

    st.set_page_config(page_title="AI CCTV Label Review", layout="wide")
    st.title("AI CCTV Label Review")
    st.caption("MVP review: accept/reject image-level labels before validation/test use.")

    image_root = Path(st.sidebar.text_input("Image root", str(DEFAULT_IMAGE_ROOT)))
    label_root = Path(st.sidebar.text_input("Label root", str(DEFAULT_LABEL_ROOT)))
    state_path = Path(st.sidebar.text_input("Review state", str(DEFAULT_STATE_PATH)))
    export_dir = Path(st.sidebar.text_input("Reviewed export dir", str(DEFAULT_EXPORT_DIR)))
    state_path.parent.mkdir(parents=True, exist_ok=True)

    state = load_review_state(state_path)

    images = list_images(image_root)
    if not images:
        st.warning(f"No images found under {image_root}")
        st.info("Run record_webcam.py, extract_frames.py, and auto_label_yolo.py first.")
        return

    status_filter = st.sidebar.selectbox("Status", ["all", "unreviewed", "accepted", "rejected"])
    filtered = []
    for image in images:
        status = review_status_for_image(state, image, image_root)
        if status_filter == "all" or status == status_filter:
            filtered.append(image)
    if not filtered:
        st.info("No images match this filter.")
        return

    index = st.sidebar.number_input("Image index", min_value=0, max_value=len(filtered) - 1, value=0)
    image = filtered[int(index)]
    label_path = label_for_image(image, image_root, label_root)
    labels = read_labels(label_path)
    current_status = review_status_for_image(state, image, image_root)

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
            state[str(relative_to_root(image, image_root))] = "accepted"
            save_review_state(state_path, state)
            st.rerun()
        if reject.button("Reject"):
            state[str(relative_to_root(image, image_root))] = "rejected"
            save_review_state(state_path, state)
            st.rerun()

        if st.button("Export accepted reviewed pairs"):
            result = export_reviewed_pairs(
                image_root=image_root,
                label_root=label_root,
                state_path=state_path,
                output_dir=export_dir,
                clean=False,
            )
            st.success(f"Exported {result.accepted} accepted pairs to {result.output_dir}")
            if result.missing_labels:
                st.warning(f"Skipped {result.missing_labels} accepted images with missing labels")

    st.subheader("Review progress")
    statuses = [review_status_for_image(state, image_path, image_root) for image_path in images]
    accepted = sum(1 for value in statuses if value == "accepted")
    rejected = sum(1 for value in statuses if value == "rejected")
    st.write({"total_images": len(images), "accepted": accepted, "rejected": rejected})


def print_help() -> None:
    print(
        "usage:\n"
        "  streamlit run tools/label_review_app.py\n"
        "  python tools/label_review_app.py --export [--image-root DIR] [--label-root DIR] "
        "[--state FILE] [--out DIR] [--clean]\n\n"
        "Image-level label review UI and accepted-pair export for AI CCTV auto-label outputs.\n"
        f"Defaults:\n"
        f"  Image root: {DEFAULT_IMAGE_ROOT}\n"
        f"  Label root: {DEFAULT_LABEL_ROOT}\n"
        f"  Review state: {DEFAULT_STATE_PATH}\n"
        f"  Reviewed export dir: {DEFAULT_EXPORT_DIR}"
    )


if __name__ == "__main__":
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        print_help()
        raise SystemExit(0)
    if "--export" in sys.argv[1:]:
        raise SystemExit(run_export_cli(sys.argv[1:]))
    main()
