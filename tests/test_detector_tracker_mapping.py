from ai_cctv.detector import detections_from_ultralytics_result
from ai_cctv.tracker import tracked_detections_from_ultralytics_result


class FakeBox:
    def __init__(self, cls, name_id, conf=0.9, track_id=None):
        self.cls = cls
        self.conf = conf
        self.xyxy = [[10, 20, 30, 40]]
        self.id = track_id


class FakeResult:
    names = {0: "person", 24: "backpack", 63: "laptop", 67: "cell phone"}

    def __init__(self, boxes):
        self.boxes = boxes


def test_detector_maps_coco_bag_aliases_to_project_classes():
    result = FakeResult([FakeBox(24, "backpack")])
    detections = detections_from_ultralytics_result(result)
    assert len(detections) == 1
    assert detections[0].class_name == "bag"


def test_tracker_preserves_track_id_and_cell_phone_alias():
    result = FakeResult([FakeBox(67, "cell phone", track_id=42)])
    tracked = tracked_detections_from_ultralytics_result(result)
    assert len(tracked) == 1
    assert tracked[0].track_id == 42
    assert tracked[0].class_name == "cell_phone"
