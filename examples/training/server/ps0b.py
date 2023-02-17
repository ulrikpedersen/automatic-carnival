#!/usr/bin/env python3

"""
Trivial power supply device with no external connection or behaviour.

Extends ps0a.py, adding noise to the voltage attribute and configuring
it to be polled in the server code.
"""

import random
from time import sleep
from tango.server import Device, attribute, command


class PowerSupply(Device):
    @attribute(dtype=float, polling_period=3000, rel_change=1e-3)  # milliseconds
    def voltage(self):
        noise = -0.05 + 0.1 * random.random()
        return 1.5 + noise

    @command
    def calibrate(self):
        sleep(0.1)


if __name__ == "__main__":
    PowerSupply.run_server()
