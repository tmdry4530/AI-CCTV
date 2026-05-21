"""Streamlit dashboard for event logs and snapshots."""

from __future__ import annotations

import csv
from pathlib import Path

from .logger import CSV_FIELDS


def load_events_csv(path: str | Path) -> list[dict[str, str]]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def dashboard_main(log_path: str | Path = Path("data") / "logs" / "events.csv", snapshot_dir: str | Path = Path("data") / "snapshots") -> None:
    try:
        import pandas as pd  # type: ignore
        import streamlit as st  # type: ignore
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Streamlit dashboard requires streamlit and pandas.") from exc

    log_path = Path(log_path)
    snapshot_dir = Path(snapshot_dir)
    st.set_page_config(page_title="Webcam AI CCTV", layout="wide")
    st.title("Webcam AI CCTV Dashboard")
    st.caption("Events are rule-based alerts, not identification or proof of actual theft.")

    rows = load_events_csv(log_path)
    if not rows:
        st.info(f"No events found at {log_path}")
        st.dataframe(pd.DataFrame(columns=CSV_FIELDS), use_container_width=True)
        return

    df = pd.DataFrame(rows)
    st.metric("Total events", len(df))
    if "event_type" in df:
        st.bar_chart(df["event_type"].value_counts())
    st.dataframe(df, use_container_width=True)

    st.subheader("Snapshots")
    for row in rows[-12:]:
        snapshot = row.get("snapshot_path") or ""
        path = Path(snapshot)
        if snapshot and path.exists():
            st.image(str(path), caption=f"{row.get('event_type')} object={row.get('object_id')}")
    if snapshot_dir.exists():
        st.caption(f"Snapshot directory: {snapshot_dir}")
