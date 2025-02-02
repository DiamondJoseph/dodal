import bluesky.plan_stubs as bps
import pytest
from bluesky.run_engine import RunEngine

from dodal.devices.fast_grid_scan import (
    FastGridScan,
    GridScanParams,
    set_fast_grid_scan_params,
)


def wait_for_fgs_valid(fgs_motors: FastGridScan, timeout=0.5):
    SLEEP_PER_CHECK = 0.1
    times_to_check = int(timeout / SLEEP_PER_CHECK)
    for _ in range(times_to_check):
        scan_invalid = yield from bps.rd(fgs_motors.scan_invalid)
        pos_counter = yield from bps.rd(fgs_motors.position_counter)
        if not scan_invalid and pos_counter == 0:
            return
        yield from bps.sleep(SLEEP_PER_CHECK)
    raise Exception(f"Scan parameters invalid after {timeout} seconds")


@pytest.fixture()
def fast_grid_scan():
    fast_grid_scan = FastGridScan(name="fast_grid_scan", prefix="BL03S-MO-SGON-01:FGS:")
    yield fast_grid_scan


@pytest.mark.s03
def test_when_program_data_set_and_staged_then_expected_images_correct(
    fast_grid_scan: FastGridScan,
):
    RE = RunEngine()
    RE(set_fast_grid_scan_params(fast_grid_scan, GridScanParams(2, 2)))
    assert fast_grid_scan.expected_images.get() == 2 * 2
    fast_grid_scan.stage()
    assert fast_grid_scan.position_counter.get() == 0


@pytest.mark.s03
def test_given_valid_params_when_kickoff_then_completion_status_increases_and_finishes(
    fast_grid_scan: FastGridScan,
):
    def set_and_wait_plan(fast_grid_scan: FastGridScan):
        yield from set_fast_grid_scan_params(fast_grid_scan, GridScanParams(3, 3))
        yield from wait_for_fgs_valid(fast_grid_scan)

    prev_current, prev_fraction = None, None

    def progress_watcher(*args, **kwargs):
        nonlocal prev_current, prev_fraction
        if "current" in kwargs.keys() and "fraction" in kwargs.keys():
            current, fraction = kwargs["current"], kwargs["fraction"]
            if not prev_current:
                prev_current, prev_fraction = current, fraction
            else:
                assert current > prev_current
                assert fraction > prev_fraction
                assert 0 < fraction < 1
                assert 0 < prev_fraction < 1

    RE = RunEngine()
    RE(set_and_wait_plan(fast_grid_scan))
    assert fast_grid_scan.position_counter.get() == 0

    # S03 currently is giving 2* the number of expected images (see #13)
    fast_grid_scan.expected_images.put(3 * 3 * 2)

    fast_grid_scan.kickoff()
    complete_status = fast_grid_scan.complete()
    complete_status.watch(progress_watcher)
    complete_status.wait()
    assert prev_current is not None
    assert prev_fraction is not None
