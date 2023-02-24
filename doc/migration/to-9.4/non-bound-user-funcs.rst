.. _to9.4_non_bound_user_funcs:

==============================================================
Non-bound user functions for read/write/isallowed and commands
==============================================================

When providing the user functions that are executed on attribute
and command access, the general requirement was that they
had to be methods on the :class:`tango.server.Device` class.
This has led to some confusion when developers try a plain function
instead. There were some ways to work around this, e.g., by patching the
Python device instance ``__dict__``.  From Pytango 9.4.x this is
no longer necessary.  User functions can now be defined outside of the
device class, if desired.

This feature applies to both static and dynamic attributes/commands:

    - attribute read method (``fget``/``fread`` kwarg)
    - attribute write method (``fset``/``fwrite`` kwarg)
    - attribute is allowed method (``fisallowed`` kwarg)
    - command is allowed method (``fisallowed`` kwarg)

The first argument to these functions will be a reference to the device instance.

For example, using static attributes and commands::

    from tango import AttrWriteType, AttReqType
    from tango.server import Device, command, attribute

    global_data = {"example_attr1": 100}


    def read_example_attr1(device):
        print(f"read from device {device.get_name()}")
        return global_data["example_attr1"]


    def write_example_attr1(device, value):
        print(f"write to device {device.get_name()}")
        global_data["example_attr1"] = value


    def is_example_attr1_allowed(device, req_type):
        print(f"is_allowed attr for device {device.get_name()}")
        assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
        return True


    def is_cmd1_allowed(device):
        print(f"is_allowed cmd for device {device.get_name()}")
        return True


    class Test(Device):

        example_attr1 = attribute(
            fget=read_example_attr1,
            fset=write_example_attr1,
            fisallowed=is_example_attr1_allowed,
            dtype=int,
            access=AttrWriteType.READ_WRITE
        )

        @command(dtype_in=int, dtype_out=int, fisallowed=is_cmd1_allowed)
        def identity1(self, value):
            return value


Another example, using dynamic attributes and commands::

    from tango import AttrWriteType, AttReqType
    from tango.server import Device, command, attribute

    global_data = {"example_attr2": 200}


    def read_example_attr2(device, attr):
        print(f"read from device {device.get_name()} attr {attr.get_name()}")
        return global_data["example_attr2"]


    def write_example_attr2(device, attr):
        print(f"write to device {device.get_name()} attr {attr.get_name()}")
        value = attr.get_write_value()
        global_data["example_attr2"] = value


    def is_example_attr2_allowed(device, req_type):
        print(f"is_allowed attr for device {device.get_name()}")
        assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
        return True


    def is_cmd2_allowed(device):
        print(f"is_allowed cmd for device {device.get_name()}")
        return True


    class Test(Device):
        def initialize_dynamic_attributes(self):
            attr = attribute(
                name="example_attr2",
                dtype=int,
                access=AttrWriteType.READ_WRITE,
                fget=read_example_attr2,
                fset=write_example_attr2,
                fisallowed=is_example_attr2_allowed,
            )
            self.add_attribute(attr)
            cmd = command(
                f=self.identity2,
                dtype_in=int,
                dtype_out=int,
                fisallowed=is_cmd2_allowed,
            )
            self.add_command(cmd)

        def identity2(self, value):
            return value
