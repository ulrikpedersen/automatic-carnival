#!/usr/bin/env python3

"""Trivial example of a high-level API device server."""

from tango.server import Device, attribute


class Motor(Device):
    def init_device(self):
        super().init_device()
        self.attr_position_read = 1.0

    @attribute(dtype=float)
    def position(self):
        return self.attr_position_read


def main():
    Motor.run_server()


if __name__ == "__main__":
    main()
