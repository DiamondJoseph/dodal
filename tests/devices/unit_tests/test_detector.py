from unittest.mock import patch

from dodal.devices.det_dim_constants import EIGER2_X_16M_SIZE
from dodal.devices.detector import DetectorParams


def create_detector_params_with_directory(directory):
    return DetectorParams(
        100,
        1.0,
        directory,
        "test",
        0,
        1.0,
        0.0,
        0.0,
        1,
        1,
        False,
        "tests/devices/unit_tests/test_lookup_table.txt",
        detector_size_constants=EIGER2_X_16M_SIZE,
    )


def test_if_trailing_slash_not_provided_then_appended():
    params = create_detector_params_with_directory("test/dir")
    assert params.directory == "test/dir/"


def test_if_trailing_slash_provided_then_not_appended():
    params = create_detector_params_with_directory("test/dir/")
    assert params.directory == "test/dir/"


@patch(
    "src.dodal.devices.detector.DetectorDistanceToBeamXYConverter.parse_table",
)
def test_correct_det_dist_to_beam_converter_path_passed_in(mocked_parse_table):
    params = DetectorParams(
        100,
        1.0,
        "directory",
        "test",
        0,
        1.0,
        0.0,
        0.0,
        1,
        1,
        False,
        "a fake directory",
        detector_size_constants=EIGER2_X_16M_SIZE,
    )
    params.to_json()
    assert params.beam_xy_converter.lookup_file == "a fake directory"
