.. _to9.4_hl_dynamic:

=====================================
High-level API for dynamic attributes
=====================================

The read and write methods for dynamic attributes can now be coded in a
more Pythonic way, similar to the approach used with static attributes.
This is a new feature so existing code does not have to be modified.

Prior to 9.4.x, the methods had to look something like::

    def low_level_read(self, attr):
        value = self._values[attr.get_name()]
        attr.set_value(value)

    def low_level_write(self, attr):
        value = attr.get_write_value()
        self._values[attr.get_name()] = value

From 9.4.x, the read method can simply return the result, and the write method can be passed
the new value, instead of extracting it from the ``attr`` parameter::

        def high_level_read(self, attr):
            value = self._values[attr.get_name()]
            return value

        def high_level_write(self, attr, value):
            self._values[attr.get_name()] = value

Further details, and more options are discussed in :ref:`dynamic-attributes-howto`.
