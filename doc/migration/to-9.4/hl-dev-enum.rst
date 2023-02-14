.. _to9.4_hl_dev_enum:

================================================================
High-level API support for DevEnum spectrum and image attributes
================================================================

Prior to 9.4.x there were problems with both the client-side and server-side
implementation of spectrum and image attribute of type :class:`~tango.CmdArgType.DevEnum`.

On the client side, the high-level API would raise an exception when such attributes were read.
The low-level API worked correctly.

On the server side, a Python enumerated type couldn't be used to defined spectrum or image
attributes in a PyTango device.

Both of these issues have been fixed.

Example of server::

    from enum import IntEnum
    from tango import AttrWriteType
    from tango.server import Device, attribute

    class DisplayType(IntEnum):
        ANALOG = 0
        DIGITAL = 1

    class Clock(Device):

        _display_types = [DisplayType(0)]

        displays = attribute(dtype=(DisplayType,), max_dim_x=4, access=AttrWriteType.READ_WRITE)

        def read_displays(self):
            return self._display_types

        def write_displays(self, values):
            display_types = [DisplayType(value) for value in values]  # optional conversion from int values
            self._display_types = display_types

Example of client-side usage::

    >>> dp = tango.DeviceProxy("tango://127.0.0.1:8888/test/nodb/clock#dbase=no")

    >>> dp.displays
    (<displays.ANALOG: 0>,)

    >>> display = dp.displays[0]  # useful as client-side copy of the IntEnum class
    >>> display.__class__.__members__
    mappingproxy({'ANALOG': <displays.ANALOG: 0>, 'DIGITAL': <displays.DIGITAL: 1>})

    >>> dp.displays = ["ANALOG", "DIGITAL", "ANALOG"]  # string assignment
    >>> dp.displays
    (<displays.ANALOG: 0>, <displays.DIGITAL: 1>, <displays.ANALOG: 0>)

    >>> dp.displays = [display.ANALOG, "DIGITAL", display.ANALOG, 1]  # mixed assignment
    >>> dp.displays
    (<displays.ANALOG: 0>, <displays.DIGITAL: 1>, <displays.ANALOG: 0>, <displays.DIGITAL: 1>)

