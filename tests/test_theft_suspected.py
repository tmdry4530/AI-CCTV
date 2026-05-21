from ai_cctv.event_detector import EventDetector
from ai_cctv.state import EventThresholds, TrackedDetection


def person(track_id: int, x: float, y: float) -> TrackedDetection:
    return TrackedDetection(track_id=track_id, class_id=0, class_name="person", confidence=1.0, bbox=(x, y, x + 10, y + 10))


def bag(track_id: int, x: float, y: float) -> TrackedDetection:
    return TrackedDetection(track_id=track_id, class_id=1, class_name="bag", confidence=1.0, bbox=(x, y, x + 10, y + 10))


def abandoned_detector() -> EventDetector:
    detector = EventDetector(
        thresholds=EventThresholds(
            owner_min_seconds=3.0,
            abandoned_min_seconds=5.0,
            suspicious_min_seconds=1.5,
            missing_grace_seconds=2.0,
            moved_distance_ratio=0.2,
            event_cooldown_seconds=1.0,
        ),
        frame_size=(100, 100),
    )
    detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=0.0)
    detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=3.0)
    detector.update([bag(10, 15, 10)], timestamp=4.0)
    detector.update([bag(10, 15, 10)], timestamp=9.0)
    assert detector.objects[10].status == "abandoned"
    return detector


def test_theft_suspected_after_suspicious_approach_then_missing_beyond_grace() -> None:
    detector = abandoned_detector()
    assert detector.update([person(2, 16, 10), bag(10, 15, 10)], timestamp=10.0) == []
    events = detector.update([person(2, 16, 10), bag(10, 15, 10)], timestamp=11.5)
    assert [event.event_type for event in events] == ["suspicious_approach"]
    assert detector.update([person(2, 16, 10)], timestamp=12.0) == []
    assert detector.update([person(2, 16, 10)], timestamp=13.9) == []
    events = detector.update([person(2, 16, 10)], timestamp=14.0)
    assert [event.event_type for event in events] == ["theft_suspected"]
    assert events[0].related_person_id == 2


def test_temporary_occlusion_does_not_trigger_theft_suspected() -> None:
    detector = abandoned_detector()
    detector.update([person(2, 16, 10), bag(10, 15, 10)], timestamp=10.0)
    detector.update([person(2, 16, 10), bag(10, 15, 10)], timestamp=11.5)
    assert detector.update([person(2, 16, 10)], timestamp=12.0) == []
    events = detector.update([person(2, 16, 10), bag(10, 15, 10)], timestamp=13.0)
    assert all(event.event_type != "theft_suspected" for event in events)
    assert detector.objects[10].status == "abandoned"


def test_passing_by_does_not_trigger_theft_suspected() -> None:
    detector = abandoned_detector()
    events = detector.update([person(2, 16, 10), bag(10, 15, 10)], timestamp=10.0)
    assert events == []
    events = detector.update([person(2, 80, 80), bag(10, 15, 10)], timestamp=10.5)
    assert events == []
    events = detector.update([bag(10, 15, 10)], timestamp=13.0)
    assert all(event.event_type != "theft_suspected" for event in events)


def test_theft_suspected_when_non_owner_moves_abandoned_object() -> None:
    detector = abandoned_detector()
    events = detector.update([person(2, 55, 10), bag(10, 50, 10)], timestamp=10.0)
    assert [event.event_type for event in events] == ["theft_suspected"]
