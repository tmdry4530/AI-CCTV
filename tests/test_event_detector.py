from ai_cctv.event_detector import EventDetector, make_tracked_detection
from ai_cctv.state import BBox, EventDetectorConfig, EventType, ObjectStatus

FRAME = (1000, 1000)


def det(track_id: int, class_name: str, center: tuple[float, float]):
    x, y = center
    return make_tracked_detection(track_id, class_name, BBox(x - 10, y - 10, x + 10, y + 10))


def cfg() -> EventDetectorConfig:
    return EventDetectorConfig(
        owner_distance_ratio=0.15,
        owner_min_seconds=3.0,
        abandoned_min_seconds=5.0,
        suspicious_min_seconds=1.5,
        missing_grace_seconds=2.0,
        moved_distance_ratio=0.20,
        event_cooldown_seconds=3.0,
        recent_non_owner_seconds=8.0,
    )


def test_owner_registered_only_after_min_duration():
    detector = EventDetector(cfg())
    assert detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 0.0, FRAME) == []
    assert detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 2.9, FRAME) == []
    events = detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 3.0, FRAME)
    assert [e.event_type for e in events] == [EventType.OWNER_REGISTERED]
    assert detector.objects[10].owner_id == 1
    assert detector.objects[10].status == ObjectStatus.OWNED


def test_abandoned_requires_owner_gone_and_object_visible():
    detector = EventDetector(cfg())
    detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 0.0, FRAME)
    detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 3.0, FRAME)
    assert detector.update([det(10, "bag", (130, 100))], 5.0, FRAME) == []
    events = detector.update([det(10, "bag", (130, 100))], 10.0, FRAME)
    assert [e.event_type for e in events] == [EventType.ABANDONED_OBJECT]
    assert detector.objects[10].status == ObjectStatus.ABANDONED


def test_suspicious_and_theft_suspected_after_non_owner_and_missing():
    detector = EventDetector(cfg())
    detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 0.0, FRAME)
    detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 3.0, FRAME)
    detector.update([det(10, "bag", (130, 100))], 5.0, FRAME)
    detector.update([det(10, "bag", (130, 100))], 10.0, FRAME)
    assert detector.update([det(2, "person", (120, 100)), det(10, "bag", (130, 100))], 11.0, FRAME) == []
    events = detector.update([det(2, "person", (120, 100)), det(10, "bag", (130, 100))], 12.5, FRAME)
    assert [e.event_type for e in events] == [EventType.SUSPICIOUS_APPROACH]
    assert detector.update([det(2, "person", (120, 100))], 13.0, FRAME) == []
    events = detector.update([det(2, "person", (120, 100))], 15.1, FRAME)
    assert [e.event_type for e in events] == [EventType.THEFT_SUSPECTED]


def test_moved_object_after_suspicious_approach_triggers_theft_suspected():
    detector = EventDetector(cfg())
    detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 0.0, FRAME)
    detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 3.0, FRAME)
    detector.update([det(10, "bag", (130, 100))], 5.0, FRAME)
    detector.update([det(10, "bag", (130, 100))], 10.0, FRAME)
    detector.update([det(2, "person", (120, 100)), det(10, "bag", (130, 100))], 11.0, FRAME)
    detector.update([det(2, "person", (120, 100)), det(10, "bag", (130, 100))], 12.5, FRAME)
    events = detector.update([det(2, "person", (430, 100)), det(10, "bag", (430, 100))], 13.0, FRAME)
    assert [e.event_type for e in events] == [EventType.THEFT_SUSPECTED]


def test_cooldown_prevents_duplicate_suspicious_events():
    detector = EventDetector(cfg())
    detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 0.0, FRAME)
    detector.update([det(1, "person", (100, 100)), det(10, "bag", (130, 100))], 3.0, FRAME)
    detector.update([det(10, "bag", (130, 100))], 5.0, FRAME)
    detector.update([det(10, "bag", (130, 100))], 10.0, FRAME)
    detector.update([det(2, "person", (120, 100)), det(10, "bag", (130, 100))], 11.0, FRAME)
    assert detector.update([det(2, "person", (120, 100)), det(10, "bag", (130, 100))], 12.5, FRAME)
    assert detector.update([det(2, "person", (120, 100)), det(10, "bag", (130, 100))], 13.0, FRAME) == []
