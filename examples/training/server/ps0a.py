#!/usr/bin/env python3

"""
Trivial power supply device with no external connection or behaviour.
"""

from time import sleep

from tango.server import Device, attribute, command


class PowerSupply(Device):
    @attribute(dtype=float)
    def voltage(self):
        return 1.5

    @command
    def calibrate(self):
        sleep(0.1)


if __name__ == "__main__":
    PowerSupply.run_server()
