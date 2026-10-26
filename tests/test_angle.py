import math
from utils.pose_utils import calculate_angle, classify


def test_right_angle():
    assert math.isclose(calculate_angle((1, 0), (0, 0), (0, 1)), 90, abs_tol=1e-6)


def test_straight_line_is_180():
    assert math.isclose(calculate_angle((-1, 0), (0, 0), (1, 0)), 180, abs_tol=1e-6)


def test_zero_vector():
    assert calculate_angle((0, 0), (0, 0), (1, 1)) is None


def test_bands():
    assert classify(170)[0] == "Near-normal range"
    assert classify(100)[0] == "Moderately restricted"
    assert classify(None)[0] == "Unknown"
