import pytest

from dodal.devices.synchrotron import Synchrotron

SIM_BEAMLINE = "BL03S"


@pytest.fixture
def synchrotron():
    synchrotron = Synchrotron(f"{SIM_BEAMLINE}-", name="synchrotron")
    return synchrotron


@pytest.mark.s03
def test_synchrotron_connects(synchrotron: Synchrotron):
    synchrotron.wait_for_connection()