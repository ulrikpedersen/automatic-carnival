.. _to9.4_logging_percent_sym:

=======================
Broken logging with "%"
=======================

Device log streams calls that included literal ``%`` symbols but no args used to raise
an exception.  For example, ``self.debug_stream("I want to log a %s symbol")``, or when
when logging an exception traceback that happened to include a format method.  This is
fixed in PyTango 9.4.x, so if you had code that was doing additional escaping for the ``%``
characters before logging, this can be removed.

If you do pass additional args to a logging function after the message string, and the number of args
doesn't match the number of ``%`` string formatting characters an exception will still be raised.

The updated methods are:

    - :meth:`tango.server.Device.debug_stream`
    - :meth:`tango.server.Device.info_stream`
    - :meth:`tango.server.Device.warn_stream`
    - :meth:`tango.server.Device.error_stream`
    - :meth:`tango.server.Device.fatal_stream`
    - :meth:`tango.server.Device.fatal_stream`
    - :meth:`tango.Logger.debug`
    - :meth:`tango.Logger.info`
    - :meth:`tango.Logger.warn`
    - :meth:`tango.Logger.error`
    - :meth:`tango.Logger.fatal`
    - :meth:`tango.Logger.log`
    - :meth:`tango.Logger.log_unconditionally`

Where ``tango.Logger`` is the type returned by :meth:`tango.server.Device.get_logger`.
