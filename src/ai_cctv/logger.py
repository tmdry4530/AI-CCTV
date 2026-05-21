"""CSV/SQLite event logging."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from .state import Event

EVENT_FIELDS = [
    "timestamp",
    "event_type",
    "object_id",
    "object_class",
    "owner_id",
    "related_person_id",
    "confidence",
    "snapshot_path",
    "frame_index",
    "message",
]


class CsvEventLogger:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=EVENT_FIELDS)
                writer.writeheader()

    def log(self, event: Event) -> None:
        with self.path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=EVENT_FIELDS)
            writer.writerow(event.to_row())

    def log_many(self, events: list[Event]) -> None:
        for event in events:
            self.log(event)


class SqliteEventLogger:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    object_id INTEGER NOT NULL,
                    object_class TEXT NOT NULL,
                    owner_id INTEGER,
                    related_person_id INTEGER,
                    confidence REAL,
                    snapshot_path TEXT,
                    frame_index INTEGER,
                    message TEXT
                )
                """
            )

    def log(self, event: Event) -> None:
        row = event.to_row()
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT INTO events (
                    timestamp, event_type, object_id, object_class, owner_id,
                    related_person_id, confidence, snapshot_path, frame_index, message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(row[field] for field in EVENT_FIELDS),
            )
