from pathlib import Path

from ai_cctv.snapshot import snapshot_path_for_event
from ai_cctv.state import Event, EventType


def test_snapshot_path_uses_event_type_and_object_id():
    path = snapshot_path_for_event(Path("data") / "snapshots", Event(1.234, EventType.ABANDONED_OBJECT, 10, "bag"))
    assert path.parent == Path("data") / "snapshots"
    assert "abandoned_object" in path.name
    assert "obj10" in path.name
