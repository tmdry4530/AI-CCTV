"""Pure event detector for owner, abandoned object, and theft_suspected rules.

No OpenCV, Ultralytics, webcam, GPU, or filesystem dependency belongs here.
"""

from __future__ import annotations

from collections.abc import Iterable

from .geometry import is_near, moved_significantly
from .state import (
    BBox,
    Event,
    EventDetectorConfig,
    EventType,
    FrameSize,
    ObjectStatus,
    PERSON_CLASS,
    TrackedDetection,
    TrackedObject,
    TrackedPerson,
    is_object,
    normalize_class_name,
)


class EventDetector:
    """Stateful rule engine over tracked people and tracked objects."""

    def __init__(self, config: EventDetectorConfig | None = None) -> None:
        self.config = config or EventDetectorConfig()
        self.people: dict[int, TrackedPerson] = {}
        self.objects: dict[int, TrackedObject] = {}
        self._owner_near_since: dict[tuple[int, int], float] = {}
        self._suspicious_near_since: dict[tuple[int, int], float] = {}
        self._last_event_at: dict[tuple[EventType, int], float] = {}

    def update(
        self,
        detections: Iterable[TrackedDetection],
        timestamp: float,
        frame_size: FrameSize,
        frame_index: int | None = None,
    ) -> list[Event]:
        """Update detector state and return events emitted at this timestamp."""

        del frame_index  # Reserved for callers that track frame numbers.
        events: list[Event] = []
        normalized = [self._normalize_detection(d) for d in detections]
        current_people = {d.track_id: d for d in normalized if normalize_class_name(d.class_name) == PERSON_CLASS}
        current_objects = {
            d.track_id: d
            for d in normalized
            if is_object(d.class_name, self.config.object_classes)
        }

        self._mark_all_not_visible()
        self._update_people(current_people, timestamp)
        self._update_objects(current_objects, timestamp)

        visible_people = {pid: p for pid, p in self.people.items() if p.visible}
        visible_objects = {oid: o for oid, o in self.objects.items() if o.visible}

        events.extend(self._register_owners(visible_people, visible_objects, timestamp, frame_size))
        events.extend(self._detect_abandoned(visible_people, visible_objects, timestamp))
        events.extend(self._detect_suspicious_approach(visible_people, visible_objects, timestamp, frame_size))
        events.extend(self._detect_missing_theft_suspected(timestamp))
        events.extend(self._detect_moved_theft_suspected(visible_objects, timestamp, frame_size))
        return events

    def reset(self) -> None:
        self.people.clear()
        self.objects.clear()
        self._owner_near_since.clear()
        self._suspicious_near_since.clear()
        self._last_event_at.clear()

    def _normalize_detection(self, detection: TrackedDetection) -> TrackedDetection:
        class_name = normalize_class_name(detection.class_name)
        return TrackedDetection(
            track_id=int(detection.track_id),
            class_id=int(detection.class_id),
            class_name=class_name,
            confidence=float(detection.confidence),
            bbox=detection.bbox,
            center=detection.center,
        )

    def _mark_all_not_visible(self) -> None:
        for person in self.people.values():
            person.visible = False
        for obj in self.objects.values():
            obj.visible = False

    def _update_people(self, detections: dict[int, TrackedDetection], timestamp: float) -> None:
        for track_id, detection in detections.items():
            if track_id not in self.people:
                self.people[track_id] = TrackedPerson(
                    track_id=track_id,
                    bbox=detection.bbox,
                    center=detection.center or detection.bbox.center,
                    first_seen=timestamp,
                    last_seen=timestamp,
                    visible=True,
                    confidence=detection.confidence,
                )
            else:
                person = self.people[track_id]
                person.bbox = detection.bbox
                person.center = detection.center or detection.bbox.center
                person.last_seen = timestamp
                person.visible = True
                person.confidence = detection.confidence

    def _update_objects(self, detections: dict[int, TrackedDetection], timestamp: float) -> None:
        for track_id, detection in detections.items():
            center = detection.center or detection.bbox.center
            if track_id not in self.objects:
                self.objects[track_id] = TrackedObject(
                    track_id=track_id,
                    class_id=detection.class_id,
                    class_name=detection.class_name,
                    bbox=detection.bbox,
                    center=center,
                    first_seen=timestamp,
                    last_seen=timestamp,
                    confidence=detection.confidence,
                    last_known_position=center,
                    visible=True,
                )
            else:
                obj = self.objects[track_id]
                obj.class_id = detection.class_id
                obj.class_name = detection.class_name
                obj.bbox = detection.bbox
                obj.center = center
                obj.last_seen = timestamp
                obj.confidence = detection.confidence
                obj.last_known_position = center
                obj.missing_since = None
                obj.visible = True

        for track_id, obj in self.objects.items():
            if track_id not in detections and not obj.visible:
                if obj.missing_since is None:
                    obj.missing_since = timestamp

    def _register_owners(
        self,
        people: dict[int, TrackedPerson],
        objects: dict[int, TrackedObject],
        timestamp: float,
        frame_size: FrameSize,
    ) -> list[Event]:
        events: list[Event] = []
        active_pairs: set[tuple[int, int]] = set()
        for obj_id, obj in objects.items():
            if obj.owner_id is not None:
                continue
            nearest_person_id: int | None = None
            nearest_started_at: float | None = None
            for person_id, person in people.items():
                pair = (person_id, obj_id)
                if is_near(person.center, obj.center, self.config.owner_distance_ratio, frame_size):
                    active_pairs.add(pair)
                    self._owner_near_since.setdefault(pair, timestamp)
                    started_at = self._owner_near_since[pair]
                    if nearest_started_at is None or started_at < nearest_started_at:
                        nearest_started_at = started_at
                        nearest_person_id = person_id
            if nearest_person_id is None or nearest_started_at is None:
                continue
            if timestamp - nearest_started_at >= self.config.owner_min_seconds:
                obj.owner_id = nearest_person_id
                obj.status = ObjectStatus.OWNED
                events.extend(
                    self._emit(
                        EventType.OWNER_REGISTERED,
                        obj,
                        timestamp,
                        related_person_id=nearest_person_id,
                        message=f"owner_registered object={obj_id} owner={nearest_person_id}",
                    )
                )

        self._owner_near_since = {
            pair: started_at
            for pair, started_at in self._owner_near_since.items()
            if pair in active_pairs and self.objects.get(pair[1], None) is not None and self.objects[pair[1]].owner_id is None
        }
        return events

    def _detect_abandoned(
        self,
        people: dict[int, TrackedPerson],
        objects: dict[int, TrackedObject],
        timestamp: float,
    ) -> list[Event]:
        events: list[Event] = []
        for obj in objects.values():
            if obj.owner_id is None or obj.status != ObjectStatus.OWNED:
                continue
            owner_visible = obj.owner_id in people and people[obj.owner_id].visible
            if owner_visible:
                obj.abandoned_since = None
                continue
            if obj.abandoned_since is None:
                obj.abandoned_since = timestamp
            if timestamp - obj.abandoned_since >= self.config.abandoned_min_seconds:
                obj.status = ObjectStatus.ABANDONED
                obj.abandoned_reference_position = obj.center
                events.extend(
                    self._emit(
                        EventType.ABANDONED_OBJECT,
                        obj,
                        timestamp,
                        related_person_id=None,
                        message=f"abandoned_object object={obj.track_id} owner={obj.owner_id}",
                    )
                )
        return events

    def _detect_suspicious_approach(
        self,
        people: dict[int, TrackedPerson],
        objects: dict[int, TrackedObject],
        timestamp: float,
        frame_size: FrameSize,
    ) -> list[Event]:
        events: list[Event] = []
        active_pairs: set[tuple[int, int]] = set()
        for obj_id, obj in objects.items():
            if obj.status != ObjectStatus.ABANDONED:
                continue
            for person_id, person in people.items():
                if person_id == obj.owner_id:
                    continue
                pair = (person_id, obj_id)
                if not is_near(person.center, obj.center, self.config.owner_distance_ratio, frame_size):
                    continue
                active_pairs.add(pair)
                self._suspicious_near_since.setdefault(pair, timestamp)
                started_at = self._suspicious_near_since[pair]
                if timestamp - started_at >= self.config.suspicious_min_seconds:
                    obj.last_non_owner_near_id = person_id
                    obj.last_non_owner_near_time = timestamp
                    events.extend(
                        self._emit(
                            EventType.SUSPICIOUS_APPROACH,
                            obj,
                            timestamp,
                            related_person_id=person_id,
                            message=f"suspicious_approach object={obj_id} person={person_id}",
                        )
                    )
        self._suspicious_near_since = {
            pair: started_at for pair, started_at in self._suspicious_near_since.items() if pair in active_pairs
        }
        return events

    def _detect_missing_theft_suspected(self, timestamp: float) -> list[Event]:
        events: list[Event] = []
        for obj in self.objects.values():
            if obj.status != ObjectStatus.ABANDONED or obj.visible or obj.missing_since is None:
                continue
            if timestamp - obj.missing_since < self.config.missing_grace_seconds:
                continue
            if not self._has_recent_non_owner(obj, timestamp):
                continue
            obj.status = ObjectStatus.THEFT_SUSPECTED
            events.extend(
                self._emit(
                    EventType.THEFT_SUSPECTED,
                    obj,
                    timestamp,
                    related_person_id=obj.last_non_owner_near_id,
                    message=f"theft_suspected object={obj.track_id} reason=missing_after_non_owner_approach",
                )
            )
        return events

    def _detect_moved_theft_suspected(
        self,
        objects: dict[int, TrackedObject],
        timestamp: float,
        frame_size: FrameSize,
    ) -> list[Event]:
        events: list[Event] = []
        for obj in objects.values():
            if obj.status != ObjectStatus.ABANDONED or obj.abandoned_reference_position is None:
                continue
            if not self._has_recent_non_owner(obj, timestamp):
                continue
            if not moved_significantly(
                obj.abandoned_reference_position,
                obj.center,
                self.config.moved_distance_ratio,
                frame_size,
            ):
                continue
            obj.status = ObjectStatus.THEFT_SUSPECTED
            events.extend(
                self._emit(
                    EventType.THEFT_SUSPECTED,
                    obj,
                    timestamp,
                    related_person_id=obj.last_non_owner_near_id,
                    message=f"theft_suspected object={obj.track_id} reason=moved_after_non_owner_approach",
                )
            )
        return events

    def _has_recent_non_owner(self, obj: TrackedObject, timestamp: float) -> bool:
        if obj.last_non_owner_near_id is None or obj.last_non_owner_near_time is None:
            return False
        return timestamp - obj.last_non_owner_near_time <= self.config.recent_non_owner_seconds

    def _emit(
        self,
        event_type: EventType,
        obj: TrackedObject,
        timestamp: float,
        related_person_id: int | None,
        message: str,
    ) -> list[Event]:
        if not self._can_emit(event_type, obj.track_id, timestamp):
            return []
        self._last_event_at[(event_type, obj.track_id)] = timestamp
        return [
            Event(
                timestamp=timestamp,
                event_type=event_type,
                object_id=obj.track_id,
                object_class=obj.class_name,
                owner_id=obj.owner_id,
                related_person_id=related_person_id,
                confidence=1.0,
                message=message,
            )
        ]

    def _can_emit(self, event_type: EventType, object_id: int, timestamp: float) -> bool:
        key = (event_type, object_id)
        last = self._last_event_at.get(key)
        if last is None:
            return True
        return timestamp - last >= self.config.event_cooldown_seconds


def make_tracked_detection(
    track_id: int,
    class_name: str,
    bbox: BBox | tuple[float, float, float, float],
    timestamp: float | None = None,
    class_id: int = 0,
    confidence: float = 1.0,
) -> TrackedDetection:
    """Convenience factory for tests and simple adapters."""

    del timestamp
    box = bbox if isinstance(bbox, BBox) else BBox.from_iterable(bbox)
    return TrackedDetection(
        track_id=track_id,
        class_id=class_id,
        class_name=class_name,
        confidence=confidence,
        bbox=box,
        center=box.center,
    )
