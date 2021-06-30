#!/usr/bin/env python3

"""
Trivial power supply device with no external connection or behaviour.

Extends ps0b.py with a DevEnum attribute "output_tracking".
This would make sense in dual-output power supply, but that
hasn't been implemented here, for simplicity.
"""

import enum
import random
from time import sleep
from tango import AttrWriteType
from tango.server import Device, attribute, command


class TrackingMode(enum.IntEnum):
    INDEPENDENT = 0  # must start at zero!
    SYNCED = 1  # and increment by 1


class PowerSupply(Device):

    _tracking_mode = TrackingMode.SYNCED

    @attribute(
        dtype=float,
        polling_period=1000,  # milliseconds
        rel_change=1e-3)
    def voltage(self):
        noise = -0.05 + 0.1 * random.random()
        return 1.5 + noise

    @command
    def calibrate(self):
        sleep(0.1)

    @attribute(dtype=TrackingMode, access=AttrWriteType.READ_WRITE)
    def output_tracking(self):
        return self._tracking_mode

    @output_tracking.write
    def output_tracking(self, value):
        self._tracking_mode = value


if __name__ == '__main__':
    PowerSupply.run_server()
