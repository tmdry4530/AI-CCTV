from __future__ import annotations

from ai_cctv.event_detector import EventDetector
from ai_cctv.state import EventThresholds, TrackedDetection


def person(track_id: int, x: float, y: float) -> TrackedDetection:
    return TrackedDetection(
        track_id=track_id,
        class_id=0,
        class_name="person",
        confidence=1.0,
        bbox=(x, y, x + 10, y + 10),
    )


def bag(track_id: int, x: float, y: float) -> TrackedDetection:
    return TrackedDetection(
        track_id=track_id,
        class_id=1,
        class_name="bag",
        confidence=1.0,
        bbox=(x, y, x + 10, y + 10),
    )


def demo_detector() -> EventDetector:
    return EventDetector(
        thresholds=EventThresholds(
            owner_min_seconds=3.0,
            abandoned_min_seconds=5.0,
            suspicious_min_seconds=1.5,
            missing_grace_seconds=2.0,
            event_cooldown_seconds=1.0,
        ),
        frame_size=(100, 100),
    )


def test_prd_abandoned_then_theft_suspected_sequence_uses_mock_tracks() -> None:
    detector = demo_detector()

    assert detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=0.0) == []
    events = detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=3.0)
    assert [event.event_type for event in events] == ["owner_registered"]
    assert events[0].owner_id == 1

    assert detector.update([bag(10, 15, 10)], timestamp=4.0) == []
    events = detector.update([bag(10, 15, 10)], timestamp=9.0)
    assert [event.event_type for event in events] == ["abandoned_object"]
    assert detector.objects[10].status == "abandoned"

    assert detector.update([person(2, 16, 10), bag(10, 15, 10)], timestamp=10.0) == []
    events = detector.update([person(2, 16, 10), bag(10, 15, 10)], timestamp=11.5)
    assert [event.event_type for event in events] == ["suspicious_approach"]
    assert events[0].related_person_id == 2

    assert detector.update([person(2, 16, 10)], timestamp=12.0) == []
    assert detector.objects[10].status == "missing"
    events = detector.update([person(2, 16, 10)], timestamp=14.0)
    assert [event.event_type for event in events] == ["theft_suspected"]
    assert events[0].related_person_id == 2
    assert detector.objects[10].theft_suspected


def test_no_theft_suspected_when_non_owner_only_passes_by_in_mock_tracks() -> None:
    detector = demo_detector()
    detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=0.0)
    detector.update([person(1, 10, 10), bag(10, 15, 10)], timestamp=3.0)
    detector.update([bag(10, 15, 10)], timestamp=4.0)
    detector.update([bag(10, 15, 10)], timestamp=9.0)

    assert detector.update([person(2, 16, 10), bag(10, 15, 10)], timestamp=10.0) == []
    assert detector.update([person(2, 80, 80), bag(10, 15, 10)], timestamp=10.5) == []
    events = detector.update([bag(10, 15, 10)], timestamp=14.0)

    assert all(event.event_type != "theft_suspected" for event in events)
    assert detector.objects[10].status == "abandoned"
