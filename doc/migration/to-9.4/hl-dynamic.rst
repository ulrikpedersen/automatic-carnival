.. _to9.4_hl_dynamic:

=====================================
High-level API for dynamic attributes
=====================================

The read methods for dynamic attributes can now be coded in a
more Pythonic way, similar to the approach used with static attributes.
This is a new feature so existing code does not have to be modified.

Prior to 9.4.x, the methods had to look something like::

    def low_level_read(self, attr):
        value = self._values[attr.get_name()]
        attr.set_value(value)

From 9.4.x, the read method can simply return the result::

        def high_level_read(self, attr):
            value = self._values[attr.get_name()]
            return value

Further details are discussed in :ref:`dynamic-attributes-howto`.
