"""Pure event-state machine for abandoned object and theft_suspected scenarios.

No OpenCV, Ultralytics, GPU, webcam, or filesystem dependency belongs in this module. Tests feed
mock ``TrackedDetection`` sequences directly.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from .geometry import FrameSize, is_near, moved_significantly
from .state import Event, EventThresholds, EventType, TrackedDetection, TrackedObject, TrackedPerson

DEFAULT_OBJECT_CLASSES = frozenset({"bag", "backpack", "handbag", "suitcase", "laptop", "cell_phone", "cell phone"})


def normalize_class_name(name: str) -> str:
    """Normalize detector class names into project-level class names."""

    compact = name.strip().lower().replace(" ", "_").replace("-", "_")
    if compact in {"backpack", "handbag", "suitcase", "luggage"}:
        return "bag"
    if compact in {"cellphone", "mobile_phone", "phone"}:
        return "cell_phone"
    return compact


@dataclass(slots=True)
class EventDetector:
    thresholds: EventThresholds = field(default_factory=EventThresholds)
    frame_size: FrameSize = (1280, 720)
    object_classes: frozenset[str] = frozenset({"bag", "laptop", "cell_phone"})
    people: dict[int, TrackedPerson] = field(default_factory=dict, init=False)
    objects: dict[int, TrackedObject] = field(default_factory=dict, init=False)
    _proximity_start: dict[tuple[int, int], float] = field(default_factory=dict, init=False)
    _owner_absent_start: dict[int, float] = field(default_factory=dict, init=False)
    _non_owner_near_start: dict[tuple[int, int], float] = field(default_factory=dict, init=False)
    _object_missing_start: dict[int, float] = field(default_factory=dict, init=False)
    _last_event_time: dict[tuple[EventType, int, int | None], float] = field(
        default_factory=dict, init=False
    )

    def __post_init__(self) -> None:
        self.object_classes = frozenset(normalize_class_name(name) for name in self.object_classes)

    def update(
        self,
        detections: Iterable[TrackedDetection],
        timestamp: float,
        frame_index: int | None = None,
    ) -> list[Event]:
        """Update state with current tracked detections and return newly emitted events."""

        current_people: dict[int, TrackedDetection] = {}
        current_objects: dict[int, TrackedDetection] = {}
        for detection in detections:
            class_name = normalize_class_name(detection.class_name)
            normalized = TrackedDetection(
                class_id=detection.class_id,
                class_name=class_name,
                confidence=detection.confidence,
                bbox=detection.bbox,
                center=detection.center,
                track_id=detection.track_id,
            )
            if class_name == "person":
                current_people[normalized.track_id] = normalized
            elif class_name in self.object_classes:
                current_objects[normalized.track_id] = normalized

        self._mark_all_invisible()
        self._update_people(current_people, timestamp)
        # Movement checks need the previous object positions, so run event rules before committing
        # the new last_known_position for visible objects.
        visible_object_ids = set(current_objects)
        for track_id, detection in current_objects.items():
            self._upsert_object(track_id, detection, timestamp, update_position=False)

        events: list[Event] = []
        events.extend(self._detect_owner_registration(timestamp, frame_index))
        events.extend(self._detect_abandoned(timestamp, frame_index))
        events.extend(self._detect_suspicious_approach(timestamp, frame_index))
        events.extend(self._detect_theft_from_movement(timestamp, frame_index))
        events.extend(self._detect_theft_from_missing(visible_object_ids, timestamp, frame_index))

        for track_id in visible_object_ids:
            obj = self.objects[track_id]
            obj.last_known_position = obj.center
            obj.visible = True
            if not obj.theft_suspected and obj.status == "missing":
                obj.status = "abandoned" if obj.owner_id is not None else "visible"
            self._object_missing_start.pop(track_id, None)

        self._cleanup_stale_timers(current_people, current_objects)
        return events

    def _mark_all_invisible(self) -> None:
        for person in self.people.values():
            person.visible = False
        for obj in self.objects.values():
            obj.visible = False

    def _update_people(self, detections: dict[int, TrackedDetection], timestamp: float) -> None:
        for track_id, detection in detections.items():
            existing = self.people.get(track_id)
            if existing is None:
                self.people[track_id] = TrackedPerson(
                    track_id=track_id,
                    bbox=detection.bbox,
                    center=detection.center or (0.0, 0.0),
                    first_seen=timestamp,
                    last_seen=timestamp,
                    visible=True,
                )
            else:
                existing.bbox = detection.bbox
                existing.center = detection.center or existing.center
                existing.last_seen = timestamp
                existing.visible = True

    def _upsert_object(
        self,
        track_id: int,
        detection: TrackedDetection,
        timestamp: float,
        *,
        update_position: bool,
    ) -> None:
        existing = self.objects.get(track_id)
        if existing is None:
            center = detection.center or (0.0, 0.0)
            self.objects[track_id] = TrackedObject(
                track_id=track_id,
                class_name=detection.class_name,
                bbox=detection.bbox,
                center=center,
                first_seen=timestamp,
                last_seen=timestamp,
                visible=True,
                last_known_position=center if update_position else None,
            )
            return
        existing.class_name = detection.class_name
        existing.bbox = detection.bbox
        existing.center = detection.center or existing.center
        existing.last_seen = timestamp
        existing.visible = True
        if update_position:
            existing.last_known_position = existing.center

    def _visible_people(self) -> list[TrackedPerson]:
        return [person for person in self.people.values() if person.visible]

    def _visible_objects(self) -> list[TrackedObject]:
        return [obj for obj in self.objects.values() if obj.visible]

    def _detect_owner_registration(self, timestamp: float, frame_index: int | None) -> list[Event]:
        events: list[Event] = []
        for obj in self._visible_objects():
            if obj.owner_id is not None:
                continue
            near_person_ids: set[int] = set()
            for person in self._visible_people():
                key = (person.track_id, obj.track_id)
                if is_near(person.center, obj.center, self.frame_size, self.thresholds.owner_distance_ratio):
                    near_person_ids.add(person.track_id)
                    self._proximity_start.setdefault(key, timestamp)
                    if timestamp - self._proximity_start[key] >= self.thresholds.owner_min_seconds:
                        obj.owner_id = person.track_id
                        obj.status = "owned"
                        events.extend(
                            self._emit(
                                "owner_registered",
                                obj,
                                timestamp,
                                frame_index,
                                related_person_id=person.track_id,
                                message=f"person {person.track_id} registered as owner",
                            )
                        )
                        break
                else:
                    self._proximity_start.pop(key, None)
            for key in list(self._proximity_start):
                person_id, object_id = key
                if object_id == obj.track_id and person_id not in near_person_ids:
                    self._proximity_start.pop(key, None)
        return events

    def _detect_abandoned(self, timestamp: float, frame_index: int | None) -> list[Event]:
        events: list[Event] = []
        for obj in self._visible_objects():
            if obj.owner_id is None or obj.status in {"abandoned", "theft_suspected"}:
                self._owner_absent_start.pop(obj.track_id, None)
                continue
            owner = self.people.get(obj.owner_id)
            owner_visible = owner.visible if owner else False
            if owner_visible:
                self._owner_absent_start.pop(obj.track_id, None)
                continue
            self._owner_absent_start.setdefault(obj.track_id, timestamp)
            if timestamp - self._owner_absent_start[obj.track_id] >= self.thresholds.abandoned_min_seconds:
                obj.status = "abandoned"
                obj.abandoned_position = obj.center
                obj.last_known_position = obj.center
                events.extend(
                    self._emit(
                        "abandoned_object",
                        obj,
                        timestamp,
                        frame_index,
                        message="owner absent while object remains visible",
                    )
                )
        return events

    def _detect_suspicious_approach(self, timestamp: float, frame_index: int | None) -> list[Event]:
        events: list[Event] = []
        for obj in self._visible_objects():
            if obj.status != "abandoned" or obj.owner_id is None:
                continue
            near_ids: set[int] = set()
            for person in self._visible_people():
                if person.track_id == obj.owner_id:
                    continue
                key = (person.track_id, obj.track_id)
                if is_near(person.center, obj.center, self.frame_size, self.thresholds.owner_distance_ratio):
                    near_ids.add(person.track_id)
                    self._non_owner_near_start.setdefault(key, timestamp)
                    if timestamp - self._non_owner_near_start[key] >= self.thresholds.suspicious_min_seconds:
                        obj.last_non_owner_near_id = person.track_id
                        obj.last_non_owner_near_time = timestamp
                        events.extend(
                            self._emit(
                                "suspicious_approach",
                                obj,
                                timestamp,
                                frame_index,
                                related_person_id=person.track_id,
                                confidence=0.8,
                                message="non-owner remained near abandoned object",
                            )
                        )
                else:
                    self._non_owner_near_start.pop(key, None)
            for key in list(self._non_owner_near_start):
                person_id, object_id = key
                if object_id == obj.track_id and person_id not in near_ids:
                    self._non_owner_near_start.pop(key, None)
        return events

    def _detect_theft_from_movement(self, timestamp: float, frame_index: int | None) -> list[Event]:
        events: list[Event] = []
        for obj in self._visible_objects():
            if obj.status != "abandoned" or obj.theft_suspected:
                continue
            related_person = self._current_near_non_owner(obj)
            if related_person is None:
                continue
            anchor = obj.abandoned_position or obj.last_known_position
            if moved_significantly(anchor, obj.center, self.frame_size, self.thresholds.moved_distance_ratio):
                obj.status = "theft_suspected"
                obj.theft_suspected = True
                obj.last_non_owner_near_id = related_person.track_id
                obj.last_non_owner_near_time = timestamp
                events.extend(
                    self._emit(
                        "theft_suspected",
                        obj,
                        timestamp,
                        frame_index,
                        related_person_id=related_person.track_id,
                        confidence=0.75,
                        message="abandoned object moved significantly while non-owner was near",
                    )
                )
        return events

    def _detect_theft_from_missing(
        self,
        visible_object_ids: set[int],
        timestamp: float,
        frame_index: int | None,
    ) -> list[Event]:
        events: list[Event] = []
        for obj in self.objects.values():
            if obj.track_id in visible_object_ids:
                continue
            if obj.status not in {"abandoned", "missing"} or obj.theft_suspected:
                continue
            if not self._had_recent_non_owner(obj, timestamp):
                continue
            self._object_missing_start.setdefault(obj.track_id, timestamp)
            obj.status = "missing"
            if timestamp - self._object_missing_start[obj.track_id] >= self.thresholds.missing_grace_seconds:
                obj.status = "theft_suspected"
                obj.theft_suspected = True
                events.extend(
                    self._emit(
                        "theft_suspected",
                        obj,
                        timestamp,
                        frame_index,
                        related_person_id=obj.last_non_owner_near_id,
                        confidence=0.75,
                        message="abandoned object missing after recent non-owner approach",
                    )
                )
        return events

    def _current_near_non_owner(self, obj: TrackedObject) -> TrackedPerson | None:
        for person in self._visible_people():
            if person.track_id == obj.owner_id:
                continue
            if is_near(person.center, obj.center, self.frame_size, self.thresholds.owner_distance_ratio):
                return person
        return None

    def _had_recent_non_owner(self, obj: TrackedObject, timestamp: float) -> bool:
        if obj.last_non_owner_near_id is None or obj.last_non_owner_near_time is None:
            return False
        return timestamp - obj.last_non_owner_near_time <= self.thresholds.recent_non_owner_seconds

    def _emit(
        self,
        event_type: EventType,
        obj: TrackedObject,
        timestamp: float,
        frame_index: int | None,
        *,
        related_person_id: int | None = None,
        confidence: float = 1.0,
        message: str = "",
    ) -> list[Event]:
        key = (event_type, obj.track_id, related_person_id)
        previous = self._last_event_time.get(key)
        if previous is not None and timestamp - previous < self.thresholds.event_cooldown_seconds:
            return []
        self._last_event_time[key] = timestamp
        return [
            Event(
                timestamp=timestamp,
                event_type=event_type,
                object_id=obj.track_id,
                object_class=obj.class_name,
                owner_id=obj.owner_id,
                related_person_id=related_person_id,
                confidence=confidence,
                frame_index=frame_index,
                message=message,
            )
        ]

    def _cleanup_stale_timers(
        self,
        current_people: dict[int, TrackedDetection],
        current_objects: dict[int, TrackedDetection],
    ) -> None:
        current_person_ids = set(current_people)
        current_object_ids = set(current_objects)
        for key in list(self._proximity_start):
            person_id, object_id = key
            if person_id not in current_person_ids or object_id not in current_object_ids:
                self._proximity_start.pop(key, None)
        for key in list(self._non_owner_near_start):
            person_id, object_id = key
            if person_id not in current_person_ids or object_id not in current_object_ids:
                self._non_owner_near_start.pop(key, None)
