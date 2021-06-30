"""
Basic unit test for a PowerSupply device with events.  Requires pytest.
"""

import time
from tango import EventType
from tango.test_utils import DeviceTestContext

from ps0b import PowerSupply


def test_calibrate():
    """Test device calibration and voltage reading."""
    with DeviceTestContext(PowerSupply, process=True) as proxy:
        proxy.calibrate()
        assert proxy.voltage == 1.23


def test_events():
    """Test change events occur."""
    results = []

    def callback(evt):
        if not evt.err:
            results.append(evt)

    with DeviceTestContext(PowerSupply, process=True) as proxy:
        eid = proxy.subscribe_event(
            "random", EventType.CHANGE_EVENT, callback, wait=True)
        # wait for events to happen
        time.sleep(2)
        assert len(results) > 1
        proxy.unsubscribe_event(eid)
