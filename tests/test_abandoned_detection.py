from ai_cctv.event_detector import EventDetector
from ai_cctv.state import EventThresholds, TrackedDetection


def person(track_id: int, x: float, y: float) -> TrackedDetection:
    return TrackedDetection(track_id=track_id, class_id=0, class_name="person", confidence=1.0, bbox=(x, y, x + 10, y + 10))


def bag(track_id: int, x: float, y: float) -> TrackedDetection:
    return TrackedDetection(track_id=track_id, class_id=1, class_name="bag", confidence=1.0, bbox=(x, y, x + 10, y + 10))


def register_owner(detector: EventDetector) -> None:
    detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=0.0)
    detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=3.0)
    assert detector.objects[10].owner_id == 1


def test_abandoned_requires_owner_absent_and_object_visible() -> None:
    detector = EventDetector(
        thresholds=EventThresholds(owner_min_seconds=3.0, abandoned_min_seconds=5.0),
        frame_size=(100, 100),
    )
    register_owner(detector)
    assert detector.update([bag(10, 15, 10)], timestamp=4.0) == []
    assert detector.update([bag(10, 15, 10)], timestamp=8.9) == []
    events = detector.update([bag(10, 15, 10)], timestamp=9.0)
    assert [event.event_type for event in events] == ["abandoned_object"]
    assert detector.objects[10].status == "abandoned"


def test_no_abandoned_when_owner_remains_visible() -> None:
    detector = EventDetector(
        thresholds=EventThresholds(owner_min_seconds=3.0, abandoned_min_seconds=5.0),
        frame_size=(100, 100),
    )
    register_owner(detector)
    events = detector.update([person(1, 40, 40), bag(10, 15, 10)], timestamp=12.0)
    assert events == []
    assert detector.objects[10].status == "owned"
