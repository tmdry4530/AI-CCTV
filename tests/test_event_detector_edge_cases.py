from __future__ import annotations

from ai_cctv.event_detector import EventDetector
from ai_cctv.state import EventThresholds, TrackedDetection


def person(track_id: int, x: float, y: float) -> TrackedDetection:
    return TrackedDetection(track_id=track_id, class_id=0, class_name="person", confidence=1.0, bbox=(x, y, x + 10, y + 10))


def obj(track_id: int, class_name: str, x: float, y: float) -> TrackedDetection:
    return TrackedDetection(track_id=track_id, class_id=1, class_name=class_name, confidence=1.0, bbox=(x, y, x + 10, y + 10))


def detector() -> EventDetector:
    return EventDetector(
        thresholds=EventThresholds(
            owner_min_seconds=3.0,
            abandoned_min_seconds=5.0,
            suspicious_min_seconds=1.5,
            missing_grace_seconds=2.0,
            event_cooldown_seconds=3.0,
        ),
        frame_size=(100, 100),
    )


def register_and_abandon(d: EventDetector) -> None:
    d.update([person(1, 10, 10), obj(10, "bag", 15, 10)], timestamp=0.0)
    d.update([person(1, 10, 10), obj(10, "bag", 15, 10)], timestamp=3.0)
    d.update([obj(10, "bag", 15, 10)], timestamp=4.0)
    d.update([obj(10, "bag", 15, 10)], timestamp=9.0)
    assert d.objects[10].status == "abandoned"


def test_event_cooldown_prevents_duplicate_suspicious_approach() -> None:
    d = detector()
    register_and_abandon(d)
    d.update([person(2, 16, 10), obj(10, "bag", 15, 10)], timestamp=10.0)
    first = d.update([person(2, 16, 10), obj(10, "bag", 15, 10)], timestamp=11.5)
    second = d.update([person(2, 16, 10), obj(10, "bag", 15, 10)], timestamp=12.0)
    assert [event.event_type for event in first] == ["suspicious_approach"]
    assert second == []


def test_owner_returns_before_abandonment_threshold_resets_timer() -> None:
    d = detector()
    d.update([person(1, 10, 10), obj(10, "bag", 15, 10)], timestamp=0.0)
    d.update([person(1, 10, 10), obj(10, "bag", 15, 10)], timestamp=3.0)
    assert d.objects[10].owner_id == 1
    d.update([obj(10, "bag", 15, 10)], timestamp=4.0)
    d.update([person(1, 50, 50), obj(10, "bag", 15, 10)], timestamp=8.0)
    events = d.update([obj(10, "bag", 15, 10)], timestamp=9.1)
    assert events == []
    assert d.objects[10].status == "owned"


def test_multiple_people_near_one_object_emits_single_owner() -> None:
    d = detector()
    d.update([person(1, 10, 10), person(2, 12, 10), obj(10, "bag", 15, 10)], timestamp=0.0)
    events = d.update([person(1, 10, 10), person(2, 12, 10), obj(10, "bag", 15, 10)], timestamp=3.0)
    assert [event.event_type for event in events] == ["owner_registered"]
    assert d.objects[10].owner_id in {1, 2}


def test_multiple_objects_keep_independent_state() -> None:
    d = detector()
    d.update([person(1, 10, 10), obj(10, "bag", 15, 10), obj(20, "laptop", 80, 80)], timestamp=0.0)
    d.update([person(1, 10, 10), obj(10, "bag", 15, 10), obj(20, "laptop", 80, 80)], timestamp=3.0)
    d.update([obj(10, "bag", 15, 10), obj(20, "laptop", 80, 80)], timestamp=4.0)
    events = d.update([obj(10, "bag", 15, 10), obj(20, "laptop", 80, 80)], timestamp=9.0)
    assert [event.event_type for event in events] == ["abandoned_object"]
    assert events[0].object_id == 10
    assert d.objects[20].owner_id is None


def test_object_missing_without_recent_non_owner_does_not_trigger_theft_suspected() -> None:
    d = detector()
    register_and_abandon(d)
    assert d.update([], timestamp=12.0) == []
    assert d.update([], timestamp=20.0) == []
    assert d.objects[10].status == "abandoned"
