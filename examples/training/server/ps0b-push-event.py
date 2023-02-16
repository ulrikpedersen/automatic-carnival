#!/usr/bin/env python3

"""
Trivial power supply device with no external connection or behaviour.

Extends ps0b.py, changing the voltage attribute to push events
directly, rather than using polling.
This is a poor example since changes in the voltage attribute
will only get pushed at the end of calibration, rather than
whenever they change "significantly".
"""

import random
from time import sleep
from tango.server import Device, attribute, command


class PowerSupply(Device):
    def init_device(self):
        self.set_change_event("voltage", True, False)
        self.set_archive_event("voltage", True, False)

    @attribute(dtype=float)
    def voltage(self):
        return self._get_voltage()

    def _get_voltage(self):
        noise = -0.05 + 0.1 * random.random()
        return 1.5 + noise

    @command
    def calibrate(self):
        sleep(0.1)
        value = self._get_voltage()
        self.push_change_event("voltage", value)
        self.push_archive_event("voltage", value)


if __name__ == "__main__":
    PowerSupply.run_server()
