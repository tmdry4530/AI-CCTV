"""Streamlit dashboard for event logs and readiness status."""

from __future__ import annotations

from pathlib import Path

DEFAULT_LOG_PATH = Path("data") / "logs" / "events.csv"
DEFAULT_SNAPSHOT_DIR = Path("data") / "snapshots"


def run_dashboard(log_path: Path = DEFAULT_LOG_PATH, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> None:
    try:
        import pandas as pd  # type: ignore
        import streamlit as st  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("streamlit and pandas are required for the dashboard.") from exc

    st.set_page_config(page_title="AI CCTV Dashboard", layout="wide")
    st.title("Webcam AI CCTV Dashboard")
    st.caption("Events are advisory only. This system reports theft_suspected, never actual theft.")

    st.sidebar.header("Paths")
    log_input = st.sidebar.text_input("CSV log", str(log_path))
    snapshot_input = st.sidebar.text_input("Snapshot directory", str(snapshot_dir))
    log_file = Path(log_input)
    snapshots = Path(snapshot_input)

    if not log_file.exists():
        st.warning(f"No event log yet: {log_file}")
        st.info("Run a webcam/video demo or keep this dashboard open for future events.")
        return

    df = pd.read_csv(log_file)
    total = len(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Events", total)
    col2.metric("theft_suspected", int((df.get("event_type") == "theft_suspected").sum()))
    col3.metric("abandoned_object", int((df.get("event_type") == "abandoned_object").sum()))

    st.subheader("Event log")
    st.dataframe(df.tail(200), use_container_width=True)

    st.subheader("Snapshots")
    if not snapshots.exists():
        st.info(f"Snapshot directory not found yet: {snapshots}")
        return
    images = sorted(snapshots.glob("*.jpg"))[-12:]
    if not images:
        st.info("No snapshots saved yet.")
        return
    columns = st.columns(3)
    for index, image in enumerate(images):
        with columns[index % 3]:
            st.image(str(image), caption=image.name, use_container_width=True)


if __name__ == "__main__":  # pragma: no cover
    run_dashboard()
