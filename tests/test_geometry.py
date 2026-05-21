from ai_cctv.geometry import bbox_area, bbox_center, distance, is_near, moved_significantly


def test_bbox_center_and_area() -> None:
    assert bbox_center((0, 10, 20, 30)) == (10, 20)
    assert bbox_area((0, 10, 20, 30)) == 400


def test_distance_and_near_ratio() -> None:
    assert distance((0, 0), (3, 4)) == 5
    assert is_near((10, 10), (20, 10), (100, 100), 0.1)
    assert not is_near((10, 10), (90, 90), (100, 100), 0.1)


def test_moved_significantly() -> None:
    assert not moved_significantly(None, (20, 20), (100, 100), 0.1)
    assert moved_significantly((0, 0), (50, 0), (100, 100), 0.2)
