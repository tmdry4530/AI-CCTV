from ai_cctv.event_detector import EventDetector
from ai_cctv.state import EventThresholds, TrackedDetection


def person(track_id: int, x: float, y: float) -> TrackedDetection:
    return TrackedDetection(track_id=track_id, class_id=0, class_name="person", confidence=1.0, bbox=(x, y, x + 10, y + 10))


def bag(track_id: int, x: float, y: float) -> TrackedDetection:
    return TrackedDetection(track_id=track_id, class_id=1, class_name="bag", confidence=1.0, bbox=(x, y, x + 10, y + 10))


def test_owner_registered_only_after_sustained_nearby_time() -> None:
    detector = EventDetector(
        thresholds=EventThresholds(owner_min_seconds=3.0, event_cooldown_seconds=1.0),
        frame_size=(100, 100),
    )
    assert detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=0.0) == []
    assert detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=2.9) == []
    events = detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=3.0)
    assert [event.event_type for event in events] == ["owner_registered"]
    assert detector.objects[10].owner_id == 1


def test_owner_not_registered_when_person_only_passes_by() -> None:
    detector = EventDetector(
        thresholds=EventThresholds(owner_min_seconds=3.0),
        frame_size=(100, 100),
    )
    detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=0.0)
    detector.update([person(1, 80, 80), bag(10, 15, 10)], timestamp=1.0)
    events = detector.update([person(1, 80, 80), bag(10, 15, 10)], timestamp=4.0)
    assert events == []
    assert detector.objects[10].owner_id is None
