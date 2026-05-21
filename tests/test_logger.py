import csv
from pathlib import Path

from ai_cctv.logger import CSVEventLogger, SQLiteEventLogger
from ai_cctv.state import Event, EventType


def test_csv_event_logger_writes_expected_fields(tmp_path: Path):
    path = tmp_path / "events.csv"
    event = Event(1.5, EventType.THEFT_SUSPECTED, object_id=10, object_class="bag", owner_id=1, related_person_id=2, snapshot_path=tmp_path / "snap.jpg")
    CSVEventLogger(path).log(event)
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    assert rows[0]["event_type"] == "theft_suspected"
    assert rows[0]["object_class"] == "bag"
    assert rows[0]["snapshot_path"].endswith("snap.jpg")


def test_sqlite_event_logger_smoke(tmp_path: Path):
    db = tmp_path / "events.sqlite"
    logger = SQLiteEventLogger(db)
    logger.log(Event(0.0, EventType.OWNER_REGISTERED, object_id=10, object_class="bag", owner_id=1))
    logger.close()
    assert db.exists()
