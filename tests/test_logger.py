import csv

from ai_cctv.logger import CsvEventLogger
from ai_cctv.state import Event


def test_csv_event_logger_writes_header_and_row(tmp_path) -> None:
    path = tmp_path / "events.csv"
    logger = CsvEventLogger(path)
    logger.log(Event(timestamp=1.25, event_type="theft_suspected", object_id=10, object_class="bag"))
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    assert rows[0]["event_type"] == "theft_suspected"
    assert rows[0]["object_class"] == "bag"
