"""CSV and optional SQLite event logging."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Iterable

from .state import Event, EventType

CSV_FIELDS = [
    "timestamp",
    "event_type",
    "object_id",
    "object_class",
    "owner_id",
    "related_person_id",
    "confidence",
    "snapshot_path",
    "message",
]


class CSVEventLogger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
                writer.writeheader()

    def log(self, event: Event) -> None:
        with self.path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writerow(event_to_row(event))

    def log_many(self, events: Iterable[Event]) -> None:
        for event in events:
            self.log(event)


class SQLiteEventLogger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                timestamp REAL,
                event_type TEXT,
                object_id INTEGER,
                object_class TEXT,
                owner_id INTEGER,
                related_person_id INTEGER,
                confidence REAL,
                snapshot_path TEXT,
                message TEXT
            )
            """
        )
        self.connection.commit()

    def log(self, event: Event) -> None:
        row = event_to_row(event)
        self.connection.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            tuple(row[field] for field in CSV_FIELDS),
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()


def event_to_row(event: Event) -> dict[str, object]:
    event_type = event.event_type.value if isinstance(event.event_type, EventType) else str(event.event_type)
    return {
        "timestamp": event.timestamp,
        "event_type": event_type,
        "object_id": event.object_id,
        "object_class": event.object_class,
        "owner_id": "" if event.owner_id is None else event.owner_id,
        "related_person_id": "" if event.related_person_id is None else event.related_person_id,
        "confidence": event.confidence,
        "snapshot_path": "" if event.snapshot_path is None else str(event.snapshot_path),
        "message": event.message,
    }
