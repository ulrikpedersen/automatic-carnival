#!/usr/bin/env python3

"""
Power supply device that connects to a "hardware" simulator
provided by ps-simulator.py.  The communication is handled
by a library, instead of the Tango device directly.
Launch the ps-simulator.py script before starting this device server.
"""


from tango import InfoIt, DebugIt
from tango.server import Device, attribute, command, device_property

from libps import PowerSupplyClient


class PowerSupply(Device):
    host = device_property(str, default_value="localhost")
    port = device_property(int, default_value=45000)

    @DebugIt()
    def init_device(self):
        super().init_device()
        self.debug_stream(f"Power supply: {self.host}:{self.port}")
        self.ps_client = PowerSupplyClient(self.host, self.port)

    @DebugIt()
    def delete_device(self):
        self.ps_client.disconnect()

    @attribute(dtype=float)
    @DebugIt(show_args=False, show_kwargs=False, show_ret=True)
    def voltage(self):
        return self.ps_client.get_voltage()

    @command
    @InfoIt()
    def calibrate(self):
        self.ps_client.do_calibration()


if __name__ == "__main__":
    PowerSupply.run_server()
