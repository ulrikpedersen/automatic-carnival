.. _to9.4_optional_proxy_attrs:

=========================================================
Optionally add Python attributes to DeviceProxy instances
=========================================================

Prior to PyTango 9.3.4, developers could add arbitrary Python attributes to a
:class:`~tango.DeviceProxy` instance.  From version 9.3.4 PyTango raises an
exception if this is attempted.  To aid backwards compatibility, where the
old use case was beneficial, some new methods have been added to the :class:`~tango.DeviceProxy`.
We use the term *dynamic interface* to refer this.  When the *dynamic interface* is frozen
(the default) it cannot be changed, and you get an exception if you try.  Unfreeze it
by calling :meth:`~tango.DeviceProxy.unfreeze_dynamic_interface` if you want to make these
kinds of changes.  Here is an example::

    >>> import tango
    >>> dp = tango.DeviceProxy("sys/tg_test/1")
    >>> dp.is_dynamic_interface_frozen()
    True
    >>> dp.non_tango_attr = 123
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/lib/python3.11/site-packages/tango/device_proxy.py", line 484, in __DeviceProxy__setattr
        raise e from cause
      File "/lib/python3.11/site-packages/tango/device_proxy.py", line 478, in __DeviceProxy__setattr
        raise AttributeError(
    AttributeError: Tried to set non-existent attr 'non_tango_attr' to 123.
    The DeviceProxy object interface is frozen and cannot be modified - see tango.DeviceProxy.freeze_dynamic_interface for details.
    >>> dp.unfreeze_dynamic_interface()
    /lib/python3.11/site-packages/tango/device_proxy.py:302: UserWarning: Dynamic interface unfrozen on DeviceProxy instance TangoTest(sys/tg_test/1) id=0x102a4ea20 - arbitrary Python attributes can be set without raising an exception.
      warnings.warn(
    >>> dp.non_tango_attr = 123
    >>> dp.non_tango_attr
    123
    >>> dp.freeze_dynamic_interface()
    >>> dp.is_dynamic_interface_frozen()
    True

