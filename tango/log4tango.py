# ------------------------------------------------------------------------------
# This file is part of PyTango (http://pytango.rtfd.io)
#
# Copyright 2006-2012 CELLS / ALBA Synchrotron, Bellaterra, Spain
# Copyright 2013-2014 European Synchrotron Radiation Facility, Grenoble, France
#
# Distributed under the terms of the GNU Lesser General Public License,
# either version 3 of the License, or (at your option) any later version.
# See LICENSE.txt for more info.
# ------------------------------------------------------------------------------

"""
This is an internal PyTango module. It provides tango log classes that can
be used as decorators in any method of :class:`tango.DeviceImpl`.

To access these members use directly :mod:`tango` module and NOT tango.log4tango.

Example::

    import tango

    class MyDev(tango.Device_4Impl):

        @tango.InfoIt()
        def read_Current(self, attr):
            attr.set_value(self._current)
"""

__all__ = ("TangoStream", "LogIt", "DebugIt", "InfoIt", "WarnIt",
           "ErrorIt", "FatalIt")

__docformat__ = "restructuredtext"

import functools


class TangoStream:
    def __init__(self, fn):
        self._fn = fn
        self._accum = ""

    def write(self, s):
        self._accum += s
        # while there is no new line, just accumulate the buffer
        try:
            if s[-1] == '\n' or s.index('\n') >= 0:
                self.flush()
        except ValueError:
            pass

    def flush(self):
        b = self._accum
        if b is None or len(self._accum) == 0:
            return
        # take the '\n' because the log adds it
        if b[-1] == '\n':
            b = b[:-1]
        self._fn(b)
        self._accum = ""


class LogIt:
    """A class designed to be a decorator of any method of a
    :class:`tango.DeviceImpl` subclass. The idea is to log the entrance and
    exit of any decorated method.

    Example::

        class MyDevice(tango.Device_4Impl):

            @tango.LogIt()
            def read_Current(self, attr):
                attr.set_value(self._current, 1)

    All log messages generated by this class have DEBUG level. If you whish
    to have different log level messages, you should implement subclasses that
    log to those levels. See, for example, :class:`tango.InfoIt`.

    The constructor receives three optional arguments:
        * show_args - shows method arguments in log message (defaults to False)
        * show_kwargs - shows keyword method arguments in log message (defaults to False)
        * show_ret - shows return value in log message (defaults to False)
    """

    def __init__(self, show_args=False, show_kwargs=False, show_ret=False):
        """Initializes de LogIt object.

            :param show_args: (bool) show arguments in log message (default is False)
            :param show_kwargs: (bool) show keyword arguments in log message (default is False)
            :param show_ret: (bool) show return in log message (default is False)
        """
        self._show_args = show_args
        self._show_kwargs = show_kwargs
        self._show_ret = show_ret

    def __compact_elem(self, v, maxlen=25):
        v = repr(v)
        if len(v) > maxlen:
            v = v[:maxlen - 6] + " [...]"
        return v

    def __compact_elems(self, elems):
        return map(self.__compact_elem, elems)

    def __compact_elems_str(self, elems):
        return ", ".join(self.__compact_elems(elems))

    def __compact_item(self, k, v, maxlen=None):
        if maxlen is None:
            return "{}={}".format(k, self.__compact(v))
        return "{}={}".format(k, self.__compact(v, maxlen=maxlen))

    def __compact_dict(self, d, maxlen=None):
        return (self.__compact_item(k, v) for k, v in d.items())

    def __compact_dict_str(self, d, maxlen=None):
        return ", ".join(self.__compact_dict(d, maxlen=maxlen))

    def is_enabled(self, obj):
        return obj.get_logger().is_debug_enabled()

    def get_log_func(self, obj):
        return obj.debug_stream

    def __call__(self, f):
        @functools.wraps(f)
        def log_stream(*args, **kwargs):
            dev = args[0]
            if not self.is_enabled(dev):
                return f(*args, **kwargs)
            log = self.get_log_func(dev)
            f_name = dev.__class__.__name__ + "." + f.__name__
            sargs = ""
            if self._show_args:
                sargs = self.__compact_elems_str(args[1:])
            if self._show_kwargs:
                sargs += self.__compact_dict_str(kwargs)
            log(f"-> {f_name}({sargs})")
            with_exc = True
            try:
                ret = f(*args, **kwargs)
                with_exc = False
                return ret
            finally:
                if with_exc:
                    log(f"<- {f_name}() raised exception!")
                else:
                    sret = ""
                    if self._show_ret:
                        sret = self.__compact_elem(ret) + " "
                    log(f"{sret}<- {f_name}()")

        log_stream._wrapped = f
        return log_stream


class DebugIt(LogIt):
    """A class designed to be a decorator of any method of a
    :class:`tango.DeviceImpl` subclass. The idea is to log the entrance and
    exit of any decorated method as DEBUG level records.

    Example::

        class MyDevice(tango.Device_4Impl):

            @tango.DebugIt()
            def read_Current(self, attr):
                attr.set_value(self._current, 1)

    All log messages generated by this class have DEBUG level.

    The constructor receives three optional arguments:
        * show_args - shows method arguments in log message (defaults to False)
        * show_kwargs - shows keyword method arguments in log message (defaults to False)
        * show_ret - shows return value in log message (defaults to False)
    """

    def is_enabled(self, d):
        return d.get_logger().is_debug_enabled()

    def get_log_func(self, d):
        return d.debug_stream


class InfoIt(LogIt):
    """A class designed to be a decorator of any method of a
    :class:`tango.DeviceImpl` subclass. The idea is to log the entrance and
    exit of any decorated method as INFO level records.

    Example::

        class MyDevice(tango.Device_4Impl):

            @tango.InfoIt()
            def read_Current(self, attr):
                attr.set_value(self._current, 1)

    All log messages generated by this class have INFO level.

    The constructor receives three optional arguments:
        * show_args - shows method arguments in log message (defaults to False)
        * show_kwargs - shows keyword method arguments in log message (defaults to False)
        * show_ret - shows return value in log message (defaults to False)
    """

    def is_enabled(self, d):
        return d.get_logger().is_info_enabled()

    def get_log_func(self, d):
        return d.info_stream


class WarnIt(LogIt):
    """A class designed to be a decorator of any method of a
    :class:`tango.DeviceImpl` subclass. The idea is to log the entrance and
    exit of any decorated method as WARN level records.

    Example::

        class MyDevice(tango.Device_4Impl):

            @tango.WarnIt()
            def read_Current(self, attr):
                attr.set_value(self._current, 1)

    All log messages generated by this class have WARN level.

    The constructor receives three optional arguments:
        * show_args - shows method arguments in log message (defaults to False)
        * show_kwargs - shows keyword method arguments in log message (defaults to False)
        * show_ret - shows return value in log message (defaults to False)
    """

    def is_enabled(self, d):
        return d.get_logger().is_warn_enabled()

    def get_log_func(self, d):
        return d.warn_stream


class ErrorIt(LogIt):
    """A class designed to be a decorator of any method of a
    :class:`tango.DeviceImpl` subclass. The idea is to log the entrance and
    exit of any decorated method as ERROR level records.

    Example::

        class MyDevice(tango.Device_4Impl):

            @tango.ErrorIt()
            def read_Current(self, attr):
                attr.set_value(self._current, 1)

    All log messages generated by this class have ERROR level.

    The constructor receives three optional arguments:
        * show_args - shows method arguments in log message (defaults to False)
        * show_kwargs - shows keyword method arguments in log message (defaults to False)
        * show_ret - shows return value in log message (defaults to False)
    """

    def is_enabled(self, d):
        return d.get_logger().is_error_enabled()

    def get_log_func(self, d):
        return d.error_stream


class FatalIt(LogIt):
    """A class designed to be a decorator of any method of a
    :class:`tango.DeviceImpl` subclass. The idea is to log the entrance and
    exit of any decorated method as FATAL level records.

    Example::

        class MyDevice(tango.Device_4Impl):

            @tango.FatalIt()
            def read_Current(self, attr):
                attr.set_value(self._current, 1)

    All log messages generated by this class have FATAL level.

    The constructor receives three optional arguments:
        * show_args - shows method arguments in log message (defaults to False)
        * show_kwargs - shows keyword method arguments in log message (defaults to False)
        * show_ret - shows return value in log message (defaults to False)
    """

    def is_enabled(self, d):
        return d.get_logger().is_fatal_enabled()

    def get_log_func(self, d):
        return d.fatal_stream
