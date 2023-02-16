#!/usr/bin/env python3

"""Trivial example of a low-level API device server."""

import sys
import tango


class Motor(tango.Device_5Impl):
    def __init__(self, cl, name):
        tango.Device_5Impl.__init__(self, cl, name)
        Motor.init_device(self)

    def delete_device(self):
        pass

    def init_device(self):
        self.get_device_properties(self.get_device_class())
        self.attr_position_read = 1.0

    def always_executed_hook(self):
        pass

    def read_position(self, attr):
        attr.set_value(self.attr_position_read)

    def read_attr_hardware(self, data):
        pass


class MotorClass(tango.DeviceClass):
    class_property_list = {}
    device_property_list = {}
    cmd_list = {}
    attr_list = {"position": [[tango.DevDouble, tango.SCALAR, tango.READ]]}

    def __init__(self, name):
        tango.DeviceClass.__init__(self, name)
        self.set_type(name)


def main():
    try:
        util = tango.Util(sys.argv)
        util.add_class(MotorClass, Motor, "Motor")
        U = tango.Util.instance()
        U.server_init()
        U.server_run()
    except tango.DevFailed as exc:
        print(f"-------> Received a DevFailed exception: {exc}")
    except Exception as exc:
        print(f"-------> An unforeseen exception occurred: {exc}")


if __name__ == "__main__":
    main()
