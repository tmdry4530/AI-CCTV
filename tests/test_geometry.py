from ai_cctv.geometry import bbox_center, distance, is_near, moved_significantly, yolo_xywhn_from_bbox
from ai_cctv.state import BBox


def test_bbox_center_and_distance():
    box = BBox(10, 20, 30, 60)
    assert bbox_center(box) == (20, 40)
    assert distance((0, 0), (3, 4)) == 5


def test_near_threshold_uses_frame_diagonal():
    frame = (100, 100)
    assert is_near((0, 0), (10, 0), 0.08, frame)
    assert not is_near((0, 0), (20, 0), 0.08, frame)


def test_moved_significantly_and_yolo_conversion():
    frame = (100, 100)
    assert moved_significantly((0, 0), (30, 0), 0.2, frame)
    assert yolo_xywhn_from_bbox(BBox(10, 20, 30, 60), frame) == (0.2, 0.4, 0.2, 0.4)
