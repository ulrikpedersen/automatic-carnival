.. _to9.4_attr_decorators:

========================
New attribute decorators
========================

In order to improve with readability and better match Python's :class:`property` syntax, the
:class:`tango.server.attribute` decorator has a few new options.  No changes are required for
existing code.  These are the new options:

  - ``@<attribute>.getter``
  - ``@<attribute>.read``
  - ``@<attribute>.is_allowed``

The ``getter`` and ``read`` methods are aliases for each other and are applicable to reading
of attributes.  They provide symmetry with the decorators that handle
writing to attributes:  ``setter`` and ``write``.  The new ``is_allowed`` decorator provides
a consistent way to define the "is allowed" method for an attribute.

Unlike Python properties, the names of the decorated methods do not have to match.

A simple example::

    from tango import AttReqType, DevState
    from tango.server import Device, attribute

    class Test(Device):
        _simulated_voltage = 0.0

        voltage = attribute(dtype=float)

        @voltage.getter
        def voltage(self):
            return self._simulated_voltage

        @voltage.setter
        def voltage(self, value):
            self._simulated_voltage = value

        @voltage.is_allowed
        def voltage_can_be_changed(self, req_type):
            if req_type == AttReqType.WRITE_REQ:
                return self.get_state() == DevState.ON
            else:
                return True

There are many variations possible when using these.  See more in :ref:`howto_write_a_server`.