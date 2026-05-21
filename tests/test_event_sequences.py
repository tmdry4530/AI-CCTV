from ai_cctv.event_detector import EventDetector, make_tracked_detection
from ai_cctv.state import BBox, EventDetectorConfig, EventType

FRAME = (1000, 1000)


def d(track_id: int, class_name: str, center: tuple[float, float]):
    x, y = center
    return make_tracked_detection(track_id, class_name, BBox(x - 8, y - 8, x + 8, y + 8))


def config() -> EventDetectorConfig:
    return EventDetectorConfig()


def make_abandoned_detector() -> EventDetector:
    detector = EventDetector(config())
    detector.update([d(1, "person", (100, 100)), d(10, "bag", (125, 100))], 0, FRAME)
    detector.update([d(1, "person", (100, 100)), d(10, "bag", (125, 100))], 3, FRAME)
    detector.update([d(10, "bag", (125, 100))], 4, FRAME)
    detector.update([d(10, "bag", (125, 100))], 9, FRAME)
    return detector


def test_sequence_a_normal_owner_present_no_abandoned():
    detector = EventDetector(config())
    emitted = []
    for t in [0, 1, 2, 3, 4, 5]:
        emitted.extend(detector.update([d(1, "person", (100, 100)), d(10, "bag", (125, 100))], t, FRAME))
    assert [e.event_type for e in emitted] == [EventType.OWNER_REGISTERED]


def test_sequence_b_abandoned_object():
    detector = EventDetector(config())
    emitted = []
    for t, detections in [
        (0, [d(1, "person", (100, 100)), d(10, "bag", (125, 100))]),
        (3, [d(1, "person", (100, 100)), d(10, "bag", (125, 100))]),
        (5, [d(10, "bag", (125, 100))]),
        (10, [d(10, "bag", (125, 100))]),
    ]:
        emitted.extend(detector.update(detections, t, FRAME))
    assert EventType.ABANDONED_OBJECT in [e.event_type for e in emitted]


def test_sequence_c_theft_suspected():
    detector = make_abandoned_detector()
    emitted = []
    emitted.extend(detector.update([d(2, "person", (120, 100)), d(10, "bag", (125, 100))], 11, FRAME))
    emitted.extend(detector.update([d(2, "person", (120, 100)), d(10, "bag", (125, 100))], 12.5, FRAME))
    emitted.extend(detector.update([d(2, "person", (120, 100))], 14, FRAME))
    emitted.extend(detector.update([d(2, "person", (120, 100))], 16.1, FRAME))
    assert EventType.SUSPICIOUS_APPROACH in [e.event_type for e in emitted]
    assert EventType.THEFT_SUSPECTED in [e.event_type for e in emitted]


def test_sequence_d_passing_by_no_theft_suspected():
    detector = make_abandoned_detector()
    emitted = []
    emitted.extend(detector.update([d(2, "person", (120, 100)), d(10, "bag", (125, 100))], 11, FRAME))
    emitted.extend(detector.update([d(2, "person", (800, 800)), d(10, "bag", (125, 100))], 12, FRAME))
    emitted.extend(detector.update([d(10, "bag", (125, 100))], 17, FRAME))
    assert EventType.THEFT_SUSPECTED not in [e.event_type for e in emitted]


def test_sequence_e_temporary_occlusion_no_theft_suspected():
    detector = make_abandoned_detector()
    emitted = []
    emitted.extend(detector.update([], 11, FRAME))
    emitted.extend(detector.update([d(10, "bag", (125, 100))], 12, FRAME))
    emitted.extend(detector.update([d(10, "bag", (125, 100))], 14, FRAME))
    assert EventType.THEFT_SUSPECTED not in [e.event_type for e in emitted]
