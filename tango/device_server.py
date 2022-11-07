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
This is an internal PyTango module.
"""

from __future__ import print_function

import copy
import functools
import inspect
import os

from ._tango import (
    DeviceImpl, Device_3Impl, Device_4Impl, Device_5Impl,
    DevFailed, Attribute, WAttribute, AttrWriteType,
    MultiAttribute, MultiClassAttribute,
    Attr, Logger, AttrWriteType, AttrDataFormat,
    DispLevel, UserDefaultAttrProp, StdStringVector)

from .utils import document_method as __document_method
from .utils import copy_doc, get_latest_device_class
from .green import get_executor
from .attr_data import AttrData

from .log4tango import TangoStream

__docformat__ = "restructuredtext"

__all__ = ("ChangeEventProp", "PeriodicEventProp",
           "ArchiveEventProp", "AttributeAlarm", "EventProperties",
           "AttributeConfig", "AttributeConfig_2",
           "AttributeConfig_3", "AttributeConfig_5",
           "MultiAttrProp", "device_server_init")

# Worker access

_WORKER = get_executor()


def set_worker(worker):
    global _WORKER
    _WORKER = worker


def get_worker():
    return _WORKER

# patcher for dynamic attribute

def __run_in_executor(fn):
    if not hasattr(fn, 'wrapped_with_executor'):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return get_worker().execute(fn, *args, **kwargs)
        # to avoid double wrapping we add an empty field, and then use it to check, whether function is already wrapped
        wrapper.wrapped_with_executor = True
        return wrapper
    else:
        return fn

def get_source_location():
    """Helper function that provides source location for logging functions."""
    # Search the call stack until we are out of the 'tango' module. We cannot
    # have a fixed number here beause loggers/streams are used in many places
    # inside pytango with varying call stack depth.
    for frame, filename, lineno, _, _, _ in inspect.stack():
        module = frame.f_globals['__name__']
        if module != "tango" and not module.startswith("tango."):
            filename = os.path.basename(filename)
            return filename, lineno
    return "(unknown)", 0


class LatestDeviceImpl(get_latest_device_class()):
    __doc__ = """\
    Latest implementation of the TANGO device base class (alias for {0}).

    It inherits from CORBA classes where all the network layer is implemented.
    """.format(get_latest_device_class().__name__)


class AttributeAlarm(object):
    """This class represents the python interface for the Tango IDL object
    AttributeAlarm."""

    def __init__(self):
        self.min_alarm = ''
        self.max_alarm = ''
        self.min_warning = ''
        self.max_warning = ''
        self.delta_t = ''
        self.delta_val = ''
        self.extensions = []


class ChangeEventProp(object):
    """This class represents the python interface for the Tango IDL object
    ChangeEventProp."""

    def __init__(self):
        self.rel_change = ''
        self.abs_change = ''
        self.extensions = []


class PeriodicEventProp(object):
    """This class represents the python interface for the Tango IDL object
    PeriodicEventProp."""

    def __init__(self):
        self.period = ''
        self.extensions = []


class ArchiveEventProp(object):
    """This class represents the python interface for the Tango IDL object
    ArchiveEventProp."""

    def __init__(self):
        self.rel_change = ''
        self.abs_change = ''
        self.period = ''
        self.extensions = []


class EventProperties(object):
    """This class represents the python interface for the Tango IDL object
    EventProperties."""

    def __init__(self):
        self.ch_event = ChangeEventProp()
        self.per_event = PeriodicEventProp()
        self.arch_event = ArchiveEventProp()


class MultiAttrProp(object):
    """This class represents the python interface for the Tango IDL object
    MultiAttrProp."""

    def __init__(self):
        self.label = ''
        self.description = ''
        self.unit = ''
        self.standard_unit = ''
        self.display_unit = ''
        self.format = ''
        self.min_value = ''
        self.max_value = ''
        self.min_alarm = ''
        self.max_alarm = ''
        self.min_warning = ''
        self.max_warning = ''
        self.delta_t = ''
        self.delta_val = ''
        self.event_period = ''
        self.archive_period = ''
        self.rel_change = ''
        self.abs_change = ''
        self.archive_rel_change = ''
        self.archive_abs_change = ''


def _init_attr_config(attr_cfg):
    """Helper function to initialize attribute config objects"""
    attr_cfg.name = ''
    attr_cfg.writable = AttrWriteType.READ
    attr_cfg.data_format = AttrDataFormat.SCALAR
    attr_cfg.data_type = 0
    attr_cfg.max_dim_x = 0
    attr_cfg.max_dim_y = 0
    attr_cfg.description = ''
    attr_cfg.label = ''
    attr_cfg.unit = ''
    attr_cfg.standard_unit = ''
    attr_cfg.display_unit = ''
    attr_cfg.format = ''
    attr_cfg.min_value = ''
    attr_cfg.max_value = ''
    attr_cfg.writable_attr_name = ''
    attr_cfg.extensions = []


class AttributeConfig(object):
    """This class represents the python interface for the Tango IDL object
    AttributeConfig."""

    def __init__(self):
        _init_attr_config(self)
        self.min_alarm = ''
        self.max_alarm = ''


class AttributeConfig_2(object):
    """This class represents the python interface for the Tango IDL object
    AttributeConfig_2."""

    def __init__(self):
        _init_attr_config(self)
        self.level = DispLevel.OPERATOR
        self.min_alarm = ''
        self.max_alarm = ''


class AttributeConfig_3(object):
    """This class represents the python interface for the Tango IDL object
    AttributeConfig_3."""

    def __init__(self):
        _init_attr_config(self)
        self.level = -1
        self.att_alarm = AttributeAlarm()
        self.event_prop = EventProperties()
        self.sys_extensions = []


class AttributeConfig_5(object):
    """This class represents the python interface for the Tango IDL object
    AttributeConfig_5."""

    def __init__(self):
        _init_attr_config(self)
        self.memorized = False
        self.mem_init = False
        self.level = -1
        self.root_attr_name = ''
        self.enum_labels = []
        self.att_alarm = AttributeAlarm()
        self.event_prop = EventProperties()
        self.sys_extensions = []


def __Attribute__get_properties(self, attr_cfg=None):
    """
    get_properties(self, attr_cfg = None) -> AttributeConfig

        Get attribute properties.

        :param conf: the config object to be filled with
                     the attribute configuration. Default is None meaning the
                     method will create internally a new AttributeConfig_5
                     and return it.
                     Can be AttributeConfig, AttributeConfig_2,
                     AttributeConfig_3, AttributeConfig_5 or
                     MultiAttrProp

        :returns: the config object filled with attribute configuration information
        :rtype: AttributeConfig

        New in PyTango 7.1.4
    """

    if attr_cfg is None:
        attr_cfg = MultiAttrProp()
    if not isinstance(attr_cfg, MultiAttrProp):
        raise TypeError("attr_cfg must be an instance of MultiAttrProp")
    return self._get_properties_multi_attr_prop(attr_cfg)


def __Attribute__set_properties(self, attr_cfg, dev=None):
    """
    set_properties(self, attr_cfg, dev)

        Set attribute properties.

        This method sets the attribute properties value with the content
        of the fileds in the AttributeConfig/ AttributeConfig_3 object

        :param conf: the config object.
        :type conf: AttributeConfig or AttributeConfig_3
        :param dev: the device (not used, maintained
                    for backward compatibility)
        :type dev: DeviceImpl

        New in PyTango 7.1.4
    """

    if not isinstance(attr_cfg, MultiAttrProp):
        raise TypeError("attr_cfg must be an instance of MultiAttrProp")
    return self._set_properties_multi_attr_prop(attr_cfg)


def __Attribute__str(self):
    return '%s(%s)' % (self.__class__.__name__, self.get_name())


def __init_Attribute():
    Attribute.__str__ = __Attribute__str
    Attribute.__repr__ = __Attribute__str
    Attribute.get_properties = __Attribute__get_properties
    Attribute.set_properties = __Attribute__set_properties


def __DeviceImpl__get_device_class(self):
    """
    get_device_class(self)

        Get device class singleton.

        :returns: the device class singleton (device_class field)
        :rtype: DeviceClass

    """
    try:
        return self._device_class_instance
    except AttributeError:
        return None


def __DeviceImpl__get_device_properties(self, ds_class=None):
    """
    get_device_properties(self, ds_class = None)

        Utility method that fetches all the device properties from the database
        and converts them into members of this DeviceImpl.

        :param ds_class: the DeviceClass object. Optional. Default value is
                         None meaning that the corresponding DeviceClass object for this
                         DeviceImpl will be used
        :type ds_class: DeviceClass

        :raises DevFailed:
    """
    if ds_class is None:
        try:
            # Call this method in a try/except in case this is called during the DS shutdown sequence
            ds_class = self.get_device_class()
        except:
            return
    try:
        pu = self.prop_util = ds_class.prop_util
        self.device_property_list = copy.deepcopy(ds_class.device_property_list)
        class_prop = ds_class.class_property_list
        pu.get_device_properties(self, class_prop, self.device_property_list)
        for prop_name in class_prop:
            setattr(self, prop_name, pu.get_property_values(prop_name, class_prop))
        for prop_name in self.device_property_list:
            setattr(self, prop_name, self.prop_util.get_property_values(prop_name, self.device_property_list))
    except DevFailed as df:
        print(80 * "-")
        print(df)
        raise df


def __DeviceImpl__add_attribute(self, attr, r_meth=None, w_meth=None, is_allo_meth=None):
    """
    add_attribute(self, attr, r_meth=None, w_meth=None, is_allo_meth=None) -> Attr

        Add a new attribute to the device attribute list.

        Please, note that if you add
        an attribute to a device at device creation time, this attribute will be added
        to the device class attribute list. Therefore, all devices belonging to the
        same class created after this attribute addition will also have this attribute.

        :param attr: the new attribute to be added to the list.
        :type attr: server.attribute or Attr or AttrData
        :param r_meth: the read method to be called on a read request
                       (if attr is of type server.attribute, then use the
                       fget field in the attr object instead)
        :type r_meth: callable
        :param w_meth: the write method to be called on a write request
                       (if attr is writable)
                       (if attr is of type server.attribute, then use the
                       fset field in the attr object instead)
        :type w_meth: callable
        :param is_allo_meth: the method that is called to check if it
                             is possible to access the attribute or not
                             (if attr is of type server.attribute, then use the
                             fisallowed field in the attr object instead)
        :type is_allo_meth: callable

        :returns: the newly created attribute.
        :rtype: Attr

        :raises DevFailed:
    """

    attr_data = None
    if isinstance(attr, AttrData):
        attr_data = attr
        attr = attr.to_attr()

    att_name = attr.get_name()

    r_name = 'read_%s' % att_name
    if r_meth is None:
        if attr_data is not None:
            r_name = attr_data.read_method_name
        if hasattr(attr_data, 'fget'):
            r_meth = attr_data.fget
        elif hasattr(self, r_name):
            r_meth = getattr(self, r_name)
    else:
        r_name = r_meth.__name__

    if attr.get_writable() in (AttrWriteType.READ,
                               AttrWriteType.READ_WRITE,
                               AttrWriteType.READ_WITH_WRITE,
                               ):
        _ensure_user_method_can_be_called(self, r_name, r_meth)

    w_name = 'write_%s' % att_name
    if w_meth is None:
        if attr_data is not None:
            w_name = attr_data.write_method_name
        if hasattr(attr_data, 'fset'):
            w_meth = attr_data.fset
        elif hasattr(self, w_name):
            w_meth = getattr(self, w_name)
    else:
        w_name = w_meth.__name__

    if attr.get_writable() in (AttrWriteType.WRITE,
                               AttrWriteType.READ_WRITE,
                               AttrWriteType.READ_WITH_WRITE,
                               ):
        _ensure_user_method_can_be_called(self, w_name, w_meth)

    ia_name = 'is_%s_allowed' % att_name
    if is_allo_meth is None:
        if attr_data is not None:
            ia_name = attr_data.is_allowed_name
        if hasattr(attr_data, 'fisallowed'):
            is_allo_meth = attr_data.fisallowed
        elif hasattr(self, ia_name):
            is_allo_meth = getattr(self, ia_name)
    else:
            ia_name = is_allo_meth.__name__
    _ensure_user_method_can_be_called(self, ia_name, is_allo_meth)

    self._add_attribute(attr, r_name, w_name, ia_name)
    return attr


def _ensure_user_method_can_be_called(obj, name, user_method):
    if user_method is not None:

        # we have to check that user provided us with the device method,
        # otherwise method won't be found during call
        is_device_method = getattr(obj, name, None) == user_method

        if not is_device_method:
            # in case user gave us class method, we are trying to find it in device:
            bound_user_method = getattr(obj, name, None)
            if bound_user_method is None:
                raise ValueError(
                    "User-supplied method for attributes must be "
                    "available as a bound method on the Device class. "
                    "When accessing Tango attributes, the PyTango extension "
                    "code, PyAttr::read, uses the name of the method "
                    "to get a reference to it from the Device object. "
                    "{} was not found on {}.".format(name, obj)
                )
            user_method = bound_user_method

        # If server run in async mode, all calls must be wrapped with async executor:
        user_method_cannot_be_run_directly = get_worker().asynchronous
        if user_method_cannot_be_run_directly:
            setattr(obj, name, __run_in_executor(user_method))

    # else user hasn't provided a method, which may be OK (e.g., using named lookup, or
    # unnecessary method like a write for a read-only attribute).


def __DeviceImpl__remove_attribute(self, attr_name):
    """
    remove_attribute(self, attr_name)

        Remove one attribute from the device attribute list.

        :param attr_name: attribute name
        :type attr_name: str

        :raises DevFailed:
    """
    self._remove_attribute(attr_name)


def __DeviceImpl__add_command(self, cmd, device_level=True):
    """
    add_command(self, cmd, device_level=True) -> cmd

        Add a new command to the device command list.

        :param cmd: the new command to be added to the list
        :param device_level: Set this flag to true if the command must be added
                             for only this device

        :returns: The command to add
        :rtype: Command

        :raises DevFailed:
    """
    config = dict(cmd.__tango_command__[1][2])
    if config and ("Display level" in config):
        disp_level = config["Display level"]
    else:
        disp_level = DispLevel.OPERATOR
    self._add_command(cmd.__name__, cmd.__tango_command__[1], disp_level,
                      device_level)
    return cmd


def __DeviceImpl__remove_command(self, cmd_name, free_it=False, clean_db=True):
    """
    remove_command(self, attr_name)

        Remove one command from the device command list.

        :param cmd_name: command name to be removed from the list
        :type cmd_name: str
        :param free_it: set to true if the command object must be freed.
        :type free_it: bool
        :param clean_db: Clean command related information (included polling info
                         if the command is polled) from database.

        :raises DevFailed:
    """
    self._remove_command(cmd_name, free_it, clean_db)


def __DeviceImpl__debug_stream(self, msg, *args):
    """
    debug_stream(self, msg, *args)

        Sends the given message to the tango debug stream.

        Since PyTango 7.1.3, the same can be achieved with::

            print(msg, file=self.log_debug)

        :param msg: the message to be sent to the debug stream
        :type msg: str
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__debug_stream(filename, line, msg)


def __DeviceImpl__info_stream(self, msg, *args):
    """
    info_stream(self, msg, *args)

        Sends the given message to the tango info stream.

        Since PyTango 7.1.3, the same can be achieved with::

            print(msg, file=self.log_info)

        :param msg: the message to be sent to the info stream
        :type msg: str
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__info_stream(filename, line, msg)


def __DeviceImpl__warn_stream(self, msg, *args):
    """
    warn_stream(self, msg, *args)

        Sends the given message to the tango warn stream.

        Since PyTango 7.1.3, the same can be achieved with::

            print(msg, file=self.log_warn)

        :param msg: the message to be sent to the warn stream
        :type msg: str
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__warn_stream(filename, line, msg)


def __DeviceImpl__error_stream(self, msg, *args):
    """
    error_stream(self, msg, *args)

        Sends the given message to the tango error stream.

        Since PyTango 7.1.3, the same can be achieved with::

            print(msg, file=self.log_error)

        :param msg: the message to be sent to the error stream
        :type msg: str
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__error_stream(filename, line, msg)


def __DeviceImpl__fatal_stream(self, msg, *args):
    """
    fatal_stream(self, msg, *args)

        Sends the given message to the tango fatal stream.

        Since PyTango 7.1.3, the same can be achieved with::

            print(msg, file=self.log_fatal)

        :param msg: the message to be sent to the fatal stream
        :type msg: str
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__fatal_stream(filename, line, msg)


@property
def __DeviceImpl__debug(self):
    if not hasattr(self, "_debug_s"):
        self._debug_s = TangoStream(self.debug_stream)
    return self._debug_s


@property
def __DeviceImpl__info(self):
    if not hasattr(self, "_info_s"):
        self._info_s = TangoStream(self.info_stream)
    return self._info_s


@property
def __DeviceImpl__warn(self):
    if not hasattr(self, "_warn_s"):
        self._warn_s = TangoStream(self.warn_stream)
    return self._warn_s


@property
def __DeviceImpl__error(self):
    if not hasattr(self, "_error_s"):
        self._error_s = TangoStream(self.error_stream)
    return self._error_s


@property
def __DeviceImpl__fatal(self):
    if not hasattr(self, "_fatal_s"):
        self._fatal_s = TangoStream(self.fatal_stream)
    return self._fatal_s


def __DeviceImpl__str(self):
    return '%s(%s)' % (self.__class__.__name__, self.get_name())


def __init_DeviceImpl():
    DeviceImpl._device_class_instance = None
    DeviceImpl.get_device_class = __DeviceImpl__get_device_class
    DeviceImpl.get_device_properties = __DeviceImpl__get_device_properties
    DeviceImpl.add_attribute = __DeviceImpl__add_attribute
    DeviceImpl.remove_attribute = __DeviceImpl__remove_attribute
    DeviceImpl.add_command = __DeviceImpl__add_command
    DeviceImpl.remove_command = __DeviceImpl__remove_command
    DeviceImpl.__str__ = __DeviceImpl__str
    DeviceImpl.__repr__ = __DeviceImpl__str
    DeviceImpl.debug_stream = __DeviceImpl__debug_stream
    DeviceImpl.info_stream = __DeviceImpl__info_stream
    DeviceImpl.warn_stream = __DeviceImpl__warn_stream
    DeviceImpl.error_stream = __DeviceImpl__error_stream
    DeviceImpl.fatal_stream = __DeviceImpl__fatal_stream
    DeviceImpl.log_debug = __DeviceImpl__debug
    DeviceImpl.log_info = __DeviceImpl__info
    DeviceImpl.log_warn = __DeviceImpl__warn
    DeviceImpl.log_error = __DeviceImpl__error
    DeviceImpl.log_fatal = __DeviceImpl__fatal


def __Logger__log(self, level, msg, *args):
    """
    log(self, level, msg, *args)

        Sends the given message to the tango the selected stream.

        :param level: Log level
        :type level: Level.LevelLevel
        :param msg: the message to be sent to the stream
        :type msg: str
        :param args: list of optional message arguments
        :type args: Sequence[str]
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__log(filename, line, level, msg)


def __Logger__log_unconditionally(self, level, msg, *args):
    """
    log_unconditionally(self, level, msg, *args)

        Sends the given message to the tango the selected stream,
        without checking the level.

        :param level: Log level
        :type level: Level.LevelLevel
        :param msg: the message to be sent to the stream
        :type msg: str
        :param args: list of optional message arguments
        :type args: Sequence[str]
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__log_unconditionally(filename, line, level, msg)


def __Logger__debug(self, msg, *args):
    """
    debug(self, msg, *args)

        Sends the given message to the tango debug stream.

        :param msg: the message to be sent to the debug stream
        :type msg: str
        :param args: list of optional message arguments
        :type args: Sequence[str]
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__debug(filename, line, msg)


def __Logger__info(self, msg, *args):
    """
    info(self, msg, *args)

        Sends the given message to the tango info stream.

        :param msg: the message to be sent to the info stream
        :type msg: str
        :param args: list of optional message arguments
        :type args: Sequence[str]
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__info(filename, line, msg)


def __Logger__warn(self, msg, *args):
    """
    warn(self, msg, *args)

        Sends the given message to the tango warn stream.

        :param msg: the message to be sent to the warn stream
        :type msg: str
        :param args: list of optional message arguments
        :type args: Sequence[str]
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__warn(filename, line, msg)


def __Logger__error(self, msg, *args):
    """
    error(self, msg, *args)

        Sends the given message to the tango error stream.

        :param msg: the message to be sent to the error stream
        :type msg: str
        :param args: list of optional message arguments
        :type args: Sequence[str]
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__error(filename, line, msg)


def __Logger__fatal(self, msg, *args):
    """
    fatal(self, msg, *args)

        Sends the given message to the tango fatal stream.

        :param msg: the message to be sent to the fatal stream
        :type msg: str
        :param args: list of optional message arguments
        :type args: Sequence[str]
    """
    filename, line = get_source_location()
    if args:
        msg = msg % args
    self.__fatal(filename, line, msg)


def __UserDefaultAttrProp_set_enum_labels(self, enum_labels):
    """
    set_enum_labels(self, enum_labels)

        Set default enumeration labels.

        :param enum_labels: list of enumeration labels
        :type enum_labels: Sequence[str]

        New in PyTango 9.2.0
    """
    elbls = StdStringVector()
    for enu in enum_labels:
        elbls.append(enu)
    return self._set_enum_labels(elbls)


def __Attr__str(self):
    return '%s(%s)' % (self.__class__.__name__, self.get_name())


def __init_Attr():
    Attr.__str__ = __Attr__str
    Attr.__repr__ = __Attr__str


def __init_UserDefaultAttrProp():
    UserDefaultAttrProp.set_enum_labels = __UserDefaultAttrProp_set_enum_labels


def __init_Logger():
    Logger.log = __Logger__log
    Logger.log_unconditionally = __Logger__log_unconditionally
    Logger.debug = __Logger__debug
    Logger.info = __Logger__info
    Logger.warn = __Logger__warn
    Logger.error = __Logger__error
    Logger.fatal = __Logger__fatal


def __doc_DeviceImpl():
    def document_method(method_name, desc, append=True):
        return __document_method(DeviceImpl, method_name, desc, append)

    DeviceImpl.__doc__ = """
    Base class for all TANGO device.

    This class inherits from CORBA classes where all the network layer is implemented.
    """

    document_method("init_device", """
    init_device(self)

        Intialize the device.
    """)

    document_method("set_state", """
    set_state(self, new_state)

        Set device state.

        :param new_state: the new device state
        :type new_state: DevState
    """)

    document_method("get_state", """
    get_state(self) -> DevState

        Get a COPY of the device state.

        :returns: Current device state
        :rtype: DevState
    """)

    document_method("get_prev_state", """
    get_prev_state(self) -> DevState

        Get a COPY of the device's previous state.

        :returns: the device's previous state
        :rtype: DevState
    """)

    document_method("get_name", """
    get_name(self) -> (str)

        Get a COPY of the device name.

        :returns: the device name
        :rtype: str
    """)

    document_method("get_device_attr", """
    get_device_attr(self) -> MultiAttribute

        Get device multi attribute object.

        :returns: the device's MultiAttribute object
        :rtype: MultiAttribute
    """)

    document_method("register_signal", """
    register_signal(self, signo)

        Register a signal.

        Register this device as device to be informed when signal signo
        is sent to to the device server process

        :param signo: signal identifier
        :type signo: int
    """)

    document_method("unregister_signal", """
    unregister_signal(self, signo)

        Unregister a signal.

        Unregister this device as device to be informed when signal signo
        is sent to to the device server process

        :param signo: signal identifier
        :type signo: int
    """)

    document_method("get_status", """
    get_status(self, ) -> str

        Get a COPY of the device status.

        :returns: the device status
        :rtype: str
    """)

    document_method("set_status", """
    set_status(self, new_status)

        Set device status.

        :param new_status: the new device status
        :type new_status: str
    """)

    document_method("append_status", """
    append_status(self, status, new_line=False)

        Appends a string to the device status.

        :param status: the string to be appened to the device status
        :type status: str
        :param new_line: If true, appends a new line character before the string. Default is False
        :type new_line: bool
    """)

    document_method("dev_state", """
    dev_state(self) -> DevState

        Get device state.

        Default method to get device state. The behaviour of this method depends
        on the device state. If the device state is ON or ALARM, it reads the
        attribute(s) with an alarm level defined, check if the read value is
        above/below the alarm and eventually change the state to ALARM, return
        the device state. For all th other device state, this method simply
        returns the state This method can be redefined in sub-classes in case
        of the default behaviour does not fullfill the needs.

        :returns: the device state
        :rtype: DevState

        :raises DevFailed: If it is necessary to read attribute(s) and a problem occurs during the reading
    """)

    document_method("dev_status", """
    dev_status(self) -> str

        Get device status.

        Default method to get device status. It returns the contents of the device
        dev_status field. If the device state is ALARM, alarm messages are added
        to the device status. This method can be redefined in sub-classes in case
        of the default behaviour does not fullfill the needs.

        :returns: the device status
        :rtype: str

        :raises DevFailed: If it is necessary to read attribute(s) and a problem occurs during the reading
    """)

    document_method("set_change_event", """
    set_change_event(self, attr_name, implemented, detect=True)

        Set an implemented flag for the attribute to indicate that the server fires
        change events manually, without the polling to be started.

        If the detect parameter is set to true, the criteria specified for the
        change event are verified and the event is only pushed if they are fullfilled.
        If detect is set to false the event is fired without any value checking!

        :param attr_name: attribute name
        :type attr_name: str
        :param implemented: True when the server fires change events manually.
        :type implemented: bool
        :param detect: Triggers the verification of the change event properties
                       when set to true. Default value is true.
        :type detect: bool
    """)

    document_method("set_archive_event", """
    set_archive_event(self, attr_name, implemented, detect=True)

        Set an implemented flag for the attribute to indicate that the server fires
        archive events manually, without the polling to be started.

        If the detect parameter is set to true, the criteria specified for the
        archive event are verified and the event is only pushed if they are fullfilled.
        If detect is set to false the event is fired without any value checking!

        :param attr_name: attribute name
        :type attr_name: str
        :param implemented: True when the server fires change events manually.
        :type implemented: bool
        :param detect: Triggers the verification of the change event properties
                       when set to true. Default value is true.
        :type detect: bool
    """)

    document_method("push_change_event", """
    push_change_event(self, attr_name)

        .. function:: push_change_event(self, attr_name, except)
                      push_change_event(self, attr_name, data, dim_x = 1, dim_y = 0)
                      push_change_event(self, attr_name, str_data, data)
                      push_change_event(self, attr_name, data, time_stamp, quality, dim_x = 1, dim_y = 0)
                      push_change_event(self, attr_name, str_data, data, time_stamp, quality)
            :noindex:

        Push a change event for the given attribute name.

        The event is pushed to the notification daemon.

        :param attr_name: attribute name
        :type attr_name: str
        :param data: the data to be sent as attribute event data. Data must be compatible with the
                     attribute type and format.
                     for SPECTRUM and IMAGE attributes, data can be any type of sequence of elements
                     compatible with the attribute type
        :param str_data: special variation for DevEncoded data type. In this case 'data' must
                         be a str or an object with the buffer interface.
        :type str_data: str
        :param except: Instead of data, you may want to send an exception.
        :type except: DevFailed
        :param dim_x: the attribute x length. Default value is 1
        :type dim_x: int
        :param dim_y: the attribute y length. Default value is 0
        :type dim_y: int
        :param time_stamp: the time stamp
        :type time_stamp: double
        :param quality: the attribute quality factor
        :type quality: AttrQuality

        :raises DevFailed: If the attribute data type is not coherent.
    """)

    document_method("push_archive_event", """
    push_archive_event(self, attr_name)

        .. function:: push_archive_event(self, attr_name, except)
                      push_archive_event(self, attr_name, data, dim_x = 1, dim_y = 0)
                      push_archive_event(self, attr_name, str_data, data)
                      push_archive_event(self, attr_name, data, time_stamp, quality, dim_x = 1, dim_y = 0)
                      push_archive_event(self, attr_name, str_data, data, time_stamp, quality)
            :noindex:

        Push an archive event for the given attribute name.

        The event is pushed to the notification daemon.

        :param attr_name: attribute name
        :type attr_name: str
        :param data: the data to be sent as attribute event data. Data must be compatible with the
                     attribute type and format.
                     for SPECTRUM and IMAGE attributes, data can be any type of sequence of elements
                     compatible with the attribute type
        :param str_data: special variation for DevEncoded data type. In this case 'data' must
                         be a str or an object with the buffer interface.
        :type str_data: str
        :param except: Instead of data, you may want to send an exception.
        :type except: DevFailed
        :param dim_x: the attribute x length. Default value is 1
        :type dim_x: int
        :param dim_y: the attribute y length. Default value is 0
        :type dim_y: int
        :param time_stamp: the time stamp
        :type time_stamp: double
        :param quality: the attribute quality factor
        :type quality: AttrQuality

        :raises DevFailed: If the attribute data type is not coherent.
    """)

    document_method("push_event", """
    push_event(self, attr_name, filt_names, filt_vals)

        .. function:: push_event(self, attr_name, filt_names, filt_vals, data, dim_x = 1, dim_y = 0)
                      push_event(self, attr_name, filt_names, filt_vals, str_data, data)
                      push_event(self, attr_name, filt_names, filt_vals, data, time_stamp, quality, dim_x = 1, dim_y = 0)
                      push_event(self, attr_name, filt_names, filt_vals, str_data, data, time_stamp, quality)
            :noindex:

        Push a user event for the given attribute name.

        The event is pushed to the notification daemon.

        :param attr_name: attribute name
        :type attr_name: str
        :param filt_names: the filterable fields name
        :type filt_names: Sequence[str]
        :param filt_vals: the filterable fields value
        :type filt_vals: Sequence[double]
        :param data: the data to be sent as attribute event data. Data must be compatible with the
                     attribute type and format.
                     for SPECTRUM and IMAGE attributes, data can be any type of sequence of elements
                     compatible with the attribute type
        :param str_data: special variation for DevEncoded data type. In this case 'data' must
                         be a str or an object with the buffer interface.
        :type str_data: str
        :param dim_x: the attribute x length. Default value is 1
        :type dim_x: int
        :param dim_y: the attribute y length. Default value is 0
        :type dim_y: int
        :param time_stamp: the time stamp
        :type time_stamp: double
        :param quality: the attribute quality factor
        :type quality: AttrQuality

        :raises DevFailed: If the attribute data type is not coherent.
    """)

    document_method("set_data_ready_event", """
    set_data_ready_event(self, attr_name, implemented)

        Set an implemented flag for the attribute to indicate that the server fires
        data ready events manually.

        :param attr_name: attribute name
        :type attr_name: str
        :param implemented: True when the server fires change events manually.
        :type implemented: bool
    """)

    document_method("push_data_ready_event", """
    push_data_ready_event(self, attr_name, counter = 0)

        Push a data ready event for the given attribute name.

        The event is pushed to the notification daemon.

        The method needs only the attribue name and an optional
        "counter" which will be passed unchanged within the event

        :param attr_name: attribute name
        :type attr_name: str
        :param counter: the user counter
        :type counter: int

        :raises DevFailed: If the attribute name is unknown.
    """)

    document_method("push_pipe_event", """
    push_pipe_event(self, pipe_name, except)

        .. function:: push_pipe_event(self, pipe_name, blob, reuse_it)
                      push_pipe_event(self, pipe_name, blob, timeval, reuse_it)
            :noindex:

        Push a pipe event for the given blob.

        :param pipe_name: pipe name
        :type pipe_name: str
        :param blob: the blob data
        :type blob: DevicePipeBlob

        :raises DevFailed: If the pipe name is unknown.

        New in PyTango 9.2.2
    """)

    document_method("get_logger", """
    get_logger(self) -> Logger

        Returns the Logger object for this device

        :returns: the Logger object for this device
        :rtype: Logger
    """)

    document_method("init_logger", """
    init_logger(self) -> None

        Setups logger for the device.  Called automatically when device starts.
    """)

    document_method("start_logging", """
    start_logging(self) -> None

        Starts logging
    """)

    document_method("stop_logging", """
    stop_logging(self) -> None

        Stops logging
    """)

    document_method("get_exported_flag", """
    get_exported_flag(self) -> bool

        Returns the state of the exported flag

        :returns: the state of the exported flag
        :rtype: bool

        New in PyTango 7.1.2
    """)

    document_method("is_attribute_polled", """
    is_attribute_polled(self, attr_name) -> bool

        True if the attribute is polled.

        :param str attr_name: attribute name
        
        :return: True if the attribute is polled
        :rtype: bool
    """)

    document_method("is_command_polled", """
    is_command_polled(self, cmd_name) -> bool

        True if the command is polled.

        :param str cmd_name: attribute name
        
        :return: True if the command is polled
        :rtype: bool
    """)

    document_method("poll_attribute", """
    poll_attribute(self, attr_name, period) -> None

        Add an attribute to the list of polled attributes.

        :param str attr_name: attribute name
        
        :param int period: polling period in milliseconds

        :return: None
        :rtype: None
    """)

    document_method("poll_command", """
    poll_command(self, cmd_name, period) -> None

        Add a command to the list of polled commands.

        :param str cmd_name: attribute name

        :param int period: polling period in milliseconds

        :return: None
        :rtype: None
    """)

    document_method("stop_poll_attribute", """
    stop_poll_attribute(self, attr_name) -> None

        Remove an attribute from the list of polled attributes.

        :param str attr_name: attribute name

        :return: None
        :rtype: None
    """)

    document_method("stop_poll_command", """
    stop_poll_command(self, cmd_name) -> None

        Remove a command from the list of polled commands.

        :param str cmd_name: cmd_name name

        :return: None
        :rtype: None
    """)

    document_method("get_poll_ring_depth", """
    get_poll_ring_depth(self) -> int

        Returns the poll ring depth

        :returns: the poll ring depth
        :rtype: int

        New in PyTango 7.1.2
    """)

    document_method("get_poll_old_factor", """
    get_poll_old_factor(self) -> int

        Returns the poll old factor

        :returns: the poll old factor
        :rtype: int

        New in PyTango 7.1.2
    """)

    document_method("is_polled", """
    is_polled(self) -> bool

        Returns if it is polled

        :returns: True if it is polled or False otherwise
        :rtype: bool

        New in PyTango 7.1.2
    """)

    document_method("get_polled_cmd", """
    get_polled_cmd(self) -> Sequence[str]

        Returns a COPY of the list of polled commands

        :returns: a COPY of the list of polled commands
        :rtype: Sequence[str]

        New in PyTango 7.1.2
    """)

    document_method("get_polled_attr", """
    get_polled_attr(self) -> Sequence[str]

        Returns a COPY of the list of polled attributes

        :returns: a COPY of the list of polled attributes
        :rtype: Sequence[str]

        New in PyTango 7.1.2
    """)

    document_method("get_non_auto_polled_cmd", """
    get_non_auto_polled_cmd(self) -> Sequence[str]

        Returns a COPY of the list of non automatic polled commands

        :returns: a COPY of the list of non automatic polled commands
        :rtype: Sequence[str]

        New in PyTango 7.1.2
    """)

    document_method("get_non_auto_polled_attr", """
    get_non_auto_polled_attr(self) -> Sequence[str]

        Returns a COPY of the list of non automatic polled attributes

        :returns: a COPY of the list of non automatic polled attributes
        :rtype: Sequence[str]

        New in PyTango 7.1.2
    """)

    document_method("stop_polling", """
    stop_polling(self)

        .. function:: stop_polling(self, with_db_upd)
            :noindex:

        Stop all polling for a device. if the device is polled, call this
        method before deleting it.

        :param with_db_upd: Is it necessary to update db?
        :type with_db_upd: bool

        New in PyTango 7.1.2
    """)

    document_method("get_attribute_poll_period", """
    get_attribute_poll_period(self, attr_name) -> int

        Returns the attribute polling period (ms) or 0 if the attribute
        is not polled.

        :param attr_name: attribute name
        :type attr_name: str

        :returns: attribute polling period (ms) or 0 if it is not polled
        :rtype: int

        New in PyTango 8.0.0
    """)

    document_method("get_attribute_config", """
    get_attribute_config(self, attr_names) -> list[DeviceAttributeConfig]

        Returns the list of AttributeConfig for the requested names

        :param attr_names: sequence of str with attribute names
        :type attr_names: list[str]

        :returns: :class:`tango.DeviceAttributeConfig` for each requested attribute name
        :rtype: list[:class:`tango.DeviceAttributeConfig`]
    """)

    document_method("get_command_poll_period", """
    get_command_poll_period(self, cmd_name) -> int

        Returns the command polling period (ms) or 0 if the command
        is not polled.

        :param cmd_name: command name
        :type cmd_name: str

        :returns: command polling period (ms) or 0 if it is not polled
        :rtype: int

        New in PyTango 8.0.0
    """)

    document_method("check_command_exists", """
    check_command_exists(self)

        Check that a command is supported by the device and
        does not need input value.

        The method throws an exception if the
        command is not defined or needs an input value.

        :param cmd_name: the command name
        :type cmd_name: str

        :raises DevFailed:
        :raises API_IncompatibleCmdArgumentType:
        :raises API_CommandNotFound:

        New in PyTango 7.1.2
    """)

    document_method("get_dev_idl_version", """
    get_dev_idl_version(self) -> int

        Returns the IDL version.

        :returns: the IDL version
        :rtype: int

        New in PyTango 7.1.2
    """)

    document_method("get_cmd_poll_ring_depth", """
    get_cmd_poll_ring_depth(self, cmd_name) -> int

        Returns the command poll ring depth.

        :param cmd_name: the command name
        :type cmd_name: str

        :returns: the command poll ring depth
        :rtype: int

        New in PyTango 7.1.2
    """)

    document_method("get_attr_poll_ring_depth", """
    get_attr_poll_ring_depth(self, attr_name) -> int

        Returns the attribute poll ring depth.

        :param attr_name: the attribute name
        :type attr_name: str

        :returns: the attribute poll ring depth
        :rtype: int

        New in PyTango 7.1.2
    """)

    document_method("is_device_locked", """
    is_device_locked(self) -> bool

        Returns if this device is locked by a client.

        :returns: True if it is locked or False otherwise
        :rtype: bool

        New in PyTango 7.1.2
    """)

    document_method("get_min_poll_period", """
    get_min_poll_period(self) -> int

        Returns the min poll period.

        :returns: the min poll period
        :rtype: int

        New in PyTango 7.2.0
    """)

    document_method("get_cmd_min_poll_period", """
    get_cmd_min_poll_period(self) -> Sequence[str]

        Returns the min command poll period.

        :returns: the min command poll period
        :rtype: Sequence[str]

        New in PyTango 7.2.0
    """)

    document_method("get_attr_min_poll_period", """
    get_attr_min_poll_period(self) -> Sequence[str]

        Returns the min attribute poll period

        :returns: the min attribute poll period
        :rtype: Sequence[str]

        New in PyTango 7.2.0
    """)

    document_method("push_att_conf_event", """
    push_att_conf_event(self, attr)

        Push an attribute configuration event.

        :param attr: the attribute for which the configuration event
                     will be sent.
        :type attr: Attribute

        New in PyTango 7.2.1
    """)

    document_method("push_pipe_event", """
    push_pipe_event(self, blob)

        Push an pipe event.

        :param blob: the blob which pipe event will be send.

        New in PyTango 9.2.2
    """)

    document_method("is_there_subscriber", """
    is_there_subscriber(self, att_name, event_type) -> bool

        Check if there is subscriber(s) listening for the event.

        This method returns a boolean set to true if there are some
        subscriber(s) listening on the event specified by the two method
        arguments. Be aware that there is some delay (up to 600 sec)
        between this method returning false and the last subscriber
        unsubscription or crash...

        The device interface change event is not supported by this method.

        :param att_name: the attribute name
        :type att_name: str
        :param event_type: the event type
        :type event_type: EventType

        :returns: True if there is at least one listener or False otherwise
        :rtype: bool
    """)


def __doc_extra_DeviceImpl(cls):
    def document_method(method_name, desc, append=True):
        return __document_method(cls, method_name, desc, append)

    document_method("delete_device", """
    delete_device(self)

        Delete the device.
    """)

    document_method("always_executed_hook", """
    always_executed_hook(self)

        Hook method.

        Default method to implement an action necessary on a device before
        any command is executed. This method can be redefined in sub-classes
        in case of the default behaviour does not fullfill the needs

        :raises DevFailed: This method does not throw exception but a redefined method can.
    """)

    document_method("read_attr_hardware", """
    read_attr_hardware(self, attr_list)

        Read the hardware to return attribute value(s).

        Default method to implement an action necessary on a device to read
        the hardware involved in a read attribute CORBA call. This method
        must be redefined in sub-classes in order to support attribute reading

        :param attr_list: list of indices in the device object attribute vector
                          of an attribute to be read.
        :type attr_list: Sequence[int]

        :raises DevFailed: This method does not throw exception but a redefined method can.
    """)

    document_method("write_attr_hardware", """
    write_attr_hardware(self)

        Write the hardware for attributes.

        Default method to implement an action necessary on a device to write
        the hardware involved in a write attribute. This method must be
        redefined in sub-classes in order to support writable attribute

        :param attr_list: list of indices in the device object attribute vector
                          of an attribute to be written.
        :type attr_list: Sequence[int]

        :raises DevFailed: This method does not throw exception but a redefined method can.
    """)

    document_method("signal_handler", """
    signal_handler(self, signo)

        Signal handler.

        The method executed when the signal arrived in the device server process.
        This method is defined as virtual and then, can be redefined following
        device needs.

        :param signo: the signal number
        :type signo: int

        :raises DevFailed: This method does not throw exception but a redefined method can.
    """)

    document_method("get_attribute_config_2", """
    get_attribute_config_2(self, attr_names) -> list[AttributeConfig_2]

        Returns the list of AttributeConfig_2 for the requested names

        :param attr_names: sequence of str with attribute names
        :type attr_names: list[str]

        :returns: list of :class:`tango.AttributeConfig_2` for each requested attribute name
        :rtype: list[:class:`tango.AttributeConfig_2`]
    """)

    document_method("get_attribute_config_3", """
    get_attribute_config_3(self, attr_name) -> list[AttributeConfig_3]

        Returns the list of AttributeConfig_3 for the requested names

        :param attr_names: sequence of str with attribute names
        :type attr_names: list[str]

        :returns: list of :class:`tango.AttributeConfig_3` for each requested attribute name
        :rtype: list[:class:`tango.AttributeConfig_3`]
    """)

    document_method("set_attribute_config_3", """
    set_attribute_config_3(self, new_conf) -> None

        Sets attribute configuration locally and in the Tango database

        :param new_conf: The new attribute(s) configuration. One AttributeConfig structure is needed for each attribute to update
        :type new_conf: list[:class:`tango.AttributeConfig_3`]

        :returns: None
        :rtype: None
    """)

    copy_doc(cls, "dev_state")
    copy_doc(cls, "dev_status")


def __doc_Attribute():
    def document_method(method_name, desc, append=True):
        return __document_method(Attribute, method_name, desc, append)

    Attribute.__doc__ = """
    This class represents a Tango attribute.
    """

    document_method("is_write_associated", """
    is_write_associated(self) -> bool

        Check if the attribute has an associated writable attribute.

        :returns: True if there is an associated writable attribute
        :rtype: bool
    """)

    document_method("is_min_alarm", """
    is_min_alarm(self) -> bool

        Check if the attribute is in minimum alarm condition.

        :returns: true if the attribute is in alarm condition (read value below the min. alarm).
        :rtype: bool
    """)

    document_method("is_max_alarm", """
    is_max_alarm(self) -> bool

        Check if the attribute is in maximum alarm condition.

        :returns: true if the attribute is in alarm condition (read value above the max. alarm).
        :rtype: bool
    """)

    document_method("is_min_warning", """
    is_min_warning(self) -> bool

        Check if the attribute is in minimum warning condition.

        :returns: true if the attribute is in warning condition (read value below the min. warning).
        :rtype: bool
    """)

    document_method("is_max_warning", """
    is_max_warning(self) -> bool

        Check if the attribute is in maximum warning condition.

        :returns: true if the attribute is in warning condition (read value above the max. warning).
        :rtype: bool
    """)

    document_method("is_rds_alarm", """
    is_rds_alarm(self) -> bool

        Check if the attribute is in RDS alarm condition.

        :returns: true if the attribute is in RDS condition (Read Different than Set).
        :rtype: bool
    """)

    document_method("is_polled", """
    is_polled(self) -> bool

        Check if the attribute is polled.

        :returns: true if the attribute is polled.
        :rtype: bool
    """)

    document_method("check_alarm", """
    check_alarm(self) -> bool

        Check if the attribute read value is below/above the alarm level.

        :returns: true if the attribute is in alarm condition.
        :rtype: bool

        :raises DevFailed: If no alarm level is defined.
    """)

    document_method("get_writable", """
    get_writable(self) -> AttrWriteType

        Get the attribute writable type (RO/WO/RW).

        :returns: The attribute write type.
        :rtype: AttrWriteType
    """)

    document_method("get_name", """
    get_name(self) -> str

        Get attribute name.

        :returns: The attribute name
        :rtype: str
    """)

    document_method("get_data_type", """
    get_data_type(self) -> int

        Get attribute data type.

        :returns: the attribute data type
        :rtype: int
    """)

    document_method("get_data_format", """
    get_data_format(self) -> AttrDataFormat

        Get attribute data format.

        :returns: the attribute data format
        :rtype: AttrDataFormat
    """)

    document_method("get_assoc_name", """
    get_assoc_name(self) -> str

        Get name of the associated writable attribute.

        :returns: the associated writable attribute name
        :rtype: str
    """)

    document_method("get_assoc_ind", """
    get_assoc_ind(self) -> int

        Get index of the associated writable attribute.

        :returns: the index in the main attribute vector of the associated writable attribute
        :rtype: int
    """)

    document_method("set_assoc_ind", """
    set_assoc_ind(self, index)

        Set index of the associated writable attribute.

        :param index: The new index in the main attribute vector of the associated writable attribute
        :type index: int
    """)

    document_method("get_date", """
    get_date(self) -> TimeVal

        Get a COPY of the attribute date.

        :returns: the attribute date
        :rtype: TimeVal
    """)

    document_method("set_date", """
    set_date(self, new_date)

        Set attribute date.

        :param new_date: the attribute date
        :type new_date: TimeVal
    """)

    document_method("get_label", """
    get_label(self, ) -> str

        Get attribute label property.

        :returns: the attribute label
        :rtype: str
    """)

    document_method("get_quality", """
    get_quality(self) -> AttrQuality

        Get a COPY of the attribute data quality.

        :returns: the attribute data quality
        :rtype: AttrQuality
    """)

    document_method("set_quality", """
    set_quality(self, quality, send_event=False)

        Set attribute data quality.

        :param quality: the new attribute data quality
        :type quality: AttrQuality
        :param send_event: true if a change event should be sent. Default is false.
        :type send_event: bool
    """)

    document_method("get_data_size", """
    get_data_size(self)

        Get attribute data size.

        :returns: the attribute data size
        :rtype: int
    """)

    document_method("get_x", """
    get_x(self) -> int

        Get attribute data size in x dimension.

        :returns: the attribute data size in x dimension. Set to 1 for scalar attribute
        :rtype: int
    """)

    document_method("get_max_dim_x", """
    get_max_dim_x(self) -> int

        Get attribute maximum data size in x dimension.

        :returns: the attribute maximum data size in x dimension. Set to 1 for scalar attribute
        :rtype: int
    """)

    document_method("get_y", """
    get_y(self) -> int

        Get attribute data size in y dimension.

        :returns: the attribute data size in y dimension. Set to 0 for scalar attribute
        :rtype: int
    """)

    document_method("get_max_dim_y", """
    get_max_dim_y(self) -> int

        Get attribute maximum data size in y dimension.

        :returns: the attribute maximum data size in y dimension. Set to 0 for scalar attribute
        :rtype: int
    """)

    document_method("get_polling_period", """
    get_polling_period(self) -> int

        Get attribute polling period.

        :returns: The attribute polling period in mS. Set to 0 when the attribute is not polled
        :rtype: int
    """)

    document_method("set_attr_serial_model", """
    set_attr_serial_model(self, ser_model) -> void

        Set attribute serialization model.

        This method allows the user to choose the attribute serialization model.

        :param ser_model: The new serialisation model. The
                          serialization model must be one of ATTR_BY_KERNEL,
                          ATTR_BY_USER or ATTR_NO_SYNC
        :type ser_model: AttrSerialModel

        New in PyTango 7.1.0
    """)

    document_method("get_attr_serial_model", """
    get_attr_serial_model(self) -> AttrSerialModel

        Get attribute serialization model.

        :returns: The attribute serialization model
        :rtype: AttrSerialModel

        New in PyTango 7.1.0
    """)

    document_method("set_value", """
    set_value(self, data, dim_x = 1, dim_y = 0) <= DEPRECATED

        .. function:: set_value(self, data)
                      set_value(self, str_data, data)
            :noindex:

        Set internal attribute value.

        This method stores the attribute read value inside the object.
        This method also stores the date when it is called and initializes the
        attribute quality factor.

        :param data: the data to be set. Data must be compatible with the attribute type and format.
                     In the DEPRECATED form for SPECTRUM and IMAGE attributes, data
                     can be any type of FLAT sequence of elements compatible with the
                     attribute type.
                     In the new form (without dim_x or dim_y) data should be any
                     sequence for SPECTRUM and a SEQUENCE of equal-length SEQUENCES
                     for IMAGE attributes.
                     The recommended sequence is a C continuous and aligned numpy
                     array, as it can be optimized.
        :param str_data: special variation for DevEncoded data type. In this case 'data' must
                         be a str or an object with the buffer interface.
        :type str_data: str
        :param dim_x: [DEPRECATED] the attribute x length. Default value is 1
        :type dim_x: int
        :param dim_y: [DEPRECATED] the attribute y length. Default value is 0
        :type dim_y: int
    """)

    document_method("set_value_date_quality", """
    set_value_date_quality(self, data, time_stamp, quality, dim_x = 1, dim_y = 0) <= DEPRECATED

        .. function:: set_value_date_quality(self, data, time_stamp, quality)
                      set_value_date_quality(self, str_data, data, time_stamp, quality)
            :noindex:

        Set internal attribute value, date and quality factor.

        This method stores the attribute read value, the date and the attribute quality
        factor inside the object.

        :param data: the data to be set. Data must be compatible with the attribute type and format.
                     In the DEPRECATED form for SPECTRUM and IMAGE attributes, data
                     can be any type of FLAT sequence of elements compatible with the
                     attribute type.
                     In the new form (without dim_x or dim_y) data should be any
                     sequence for SPECTRUM and a SEQUENCE of equal-length SEQUENCES
                     for IMAGE attributes.
                     The recommended sequence is a C continuous and aligned numpy
                     array, as it can be optimized.
        :param str_data: special variation for DevEncoded data type. In this case 'data' must
                         be a str or an object with the buffer interface.
        :type str_data: str
        :param dim_x: [DEPRECATED] the attribute x length. Default value is 1
        :type dim_x: int
        :param dim_y: [DEPRECATED] the attribute y length. Default value is 0
        :type dim_y: int
        :param time_stamp: the time stamp
        :type time_stamp: double
        :param quality: the attribute quality factor
        :type quality: AttrQuality
    """)

    document_method("set_change_event", """
    set_change_event(self, implemented, detect = True)

        Set a flag to indicate that the server fires change events manually,
        without the polling to be started for the attribute.

        If the detect parameter is set to true, the criteria specified for
        the change event are verified and the event is only pushed if they
        are fullfilled. If detect is set to false the event is fired without
        any value checking!

        :param implemented: True when the server fires change events manually.
        :type implemented: bool
        :param detect: (optional, default is True) Triggers the verification of
                       the change event properties when set to true.
        :type detect: bool

        New in PyTango 7.1.0
    """)

    document_method("set_archive_event", """
    set_archive_event(self, implemented, detect = True)

        Set a flag to indicate that the server fires archive events manually,
        without the polling to be started for the attribute.

        If the detect parameter
        is set to true, the criteria specified for the archive event are verified
        and the event is only pushed if they are fullfilled.

        :param implemented: True when the server fires archive events manually.
        :type implemented: bool
        :param detect: (optional, default is True) Triggers the verification of
                       the archive event properties when set to true.
        :type detect: bool

        New in PyTango 7.1.0
    """)

    document_method("is_change_event", """
    is_change_event(self) -> bool

        Check if the change event is fired manually (without polling) for this attribute.

        :returns: True if a manual fire change event is implemented.
        :rtype: bool

        New in PyTango 7.1.0
    """)

    document_method("is_check_change_criteria", """
    is_check_change_criteria(self) -> bool

        Check if the change event criteria should be checked when firing the
        event manually.

        :returns: True if a change event criteria will be checked.
        :rtype: bool

        New in PyTango 7.1.0
    """)

    document_method("is_archive_event", """
    is_archive_event(self) -> bool

        Check if the archive event is fired manually (without polling) for this attribute.

        :returns: True if a manual fire archive event is implemented.
        :rtype: bool

        New in PyTango 7.1.0
    """)

    document_method("is_check_archive_criteria", """
    is_check_archive_criteria(self) -> bool

        Check if the archive event criteria should be checked when firing the
        event manually.

        :returns: True if a archive event criteria will be checked.
        :rtype: bool

        New in PyTango 7.1.0
    """)

    document_method("set_data_ready_event", """
    set_data_ready_event(self, implemented)

        Set a flag to indicate that the server fires data ready events.

        :param implemented: True when the server fires data ready events manually.
        :type implemented: bool

        New in PyTango 7.2.0
    """)

    document_method("is_data_ready_event", """
    is_data_ready_event(self) -> bool

        Check if the data ready event is fired manually (without polling)
        for this attribute.

        :returns: True if a manual fire data ready event is implemented.
        :rtype: bool

        New in PyTango 7.2.0
    """)

    document_method("remove_configuration", """
    remove_configuration(self)

        Remove the attribute configuration from the database.

        This method can be used to clean-up all the configuration of an
        attribute to come back to its default values or the remove all
        configuration of a dynamic attribute before deleting it.

        The method removes all configured attribute properties and removes
        the attribute from the list of polled attributes.

        New in PyTango 7.1.0
    """)


def __doc_WAttribute():
    def document_method(method_name, desc, append=True):
        return __document_method(WAttribute, method_name, desc, append)

    WAttribute.__doc__ = """
    This class represents a Tango writable attribute.
    """

    document_method("get_min_value", """
    get_min_value(self) -> obj

        Get attribute minimum value or throws an exception if the
        attribute does not have a minimum value.

        :returns: an object with the python minimum value
        :rtype: obj
    """)

    document_method("get_max_value", """
    get_max_value(self) -> obj

        Get attribute maximum value or throws an exception if the
        attribute does not have a maximum value.

        :returns: an object with the python maximum value
        :rtype: obj
    """)

    document_method("set_min_value", """
    set_min_value(self, data)

        Set attribute minimum value.

        :param data: the attribute minimum value. python data type must be compatible
                     with the attribute data format and type.
    """)

    document_method("set_max_value", """
    set_max_value(self, data)

        Set attribute maximum value.

        :param data: the attribute maximum value. python data type must be compatible
                     with the attribute data format and type.
    """)

    document_method("is_min_value", """
    is_min_value(self) -> bool

        Check if the attribute has a minimum value.

        :returns: true if the attribute has a minimum value defined
        :rtype: bool
    """)

    document_method("is_max_value", """
    is_max_value(self, ) -> bool

        Check if the attribute has a maximum value.

        :returns: true if the attribute has a maximum value defined
        :rtype: bool
    """)

    document_method("get_write_value_length", """
    get_write_value_length(self) -> int

        Retrieve the new value length (data number) for writable attribute.

        :returns: the new value data length
        :rtype: int
    """)

    #    document_method("set_write_value", """
    #    set_write_value(self, data, dim_x = 1, dim_y = 0)
    #
    #        Set the writable attribute value.
    #
    #        :param data: the data to be set. Data must be compatible with the attribute type and format.
    #                     for SPECTRUM and IMAGE attributes, data can be any type of sequence of elements
    #                     compatible with the attribute type
    #        :param dim_x: the attribute set value x length. Default value is 1
    #        :type dim_x: int
    #        :param dim_y: the attribute set value y length. Default value is 0
    #        :type dim_y: int
    #    """)

    document_method("get_write_value", """
    get_write_value(self, lst)  <= DEPRECATED

        .. function:: get_write_value(self, extract_as=ExtractAs.Numpy) -> obj
            :noindex:

        Retrieve the new value for writable attribute.

        :param extract_as:
        :type extract_as: ExtractAs
        :param lst: [out] a list object that will be filled with the attribute write value (DEPRECATED)
        :type lst: list

        :returns: the attribute write value.
        :rtype: obj
    """)


def __doc_MultiClassAttribute():
    def document_method(method_name, desc, append=True):
        return __document_method(MultiClassAttribute, method_name, desc, append)

    MultiClassAttribute.__doc__ = """
    There is one instance of this class for each device class.

    This class is mainly an aggregate of :class:`~tango.Attr` objects.
    It eases management of multiple attributes

    New in PyTango 7.2.1"""

    document_method("get_attr", """
    get_attr(self, attr_name) -> Attr

        Get the :class:`~tango.Attr` object for the attribute with
        name passed as parameter.

        :param attr_name: attribute name
        :type attr_name: str

        :returns: the attribute object
        :rtype: Attr

        :raises DevFailed: If the attribute is not defined.

        New in PyTango 7.2.1
    """)

    document_method("remove_attr", """
    remove_attr(self, attr_name, cl_name)

        Remove the :class:`~tango.Attr` object for the attribute with
        name passed as parameter.

        Does nothing if the attribute does not exist.

        :param attr_name: attribute name
        :type attr_name: str
        :param cl_name: the attribute class name
        :type cl_name: str

        New in PyTango 7.2.1
    """)

    document_method("get_attr_list", """
    get_attr_list(self) -> Sequence[Attr]

        Get the list of :class:`~tango.Attr` for this device class.

        :returns: the list of attribute objects
        :rtype: Sequence[Attr]

        New in PyTango 7.2.1
    """)


def __doc_MultiAttribute():
    def document_method(method_name, desc, append=True):
        return __document_method(MultiAttribute, method_name, desc, append)

    MultiAttribute.__doc__ = """
    There is one instance of this class for each device.
    This class is mainly an aggregate of :class:`~tango.Attribute` or
    :class:`~tango.WAttribute` objects. It eases management of multiple
    attributes"""

    document_method("get_attr_by_name", """
    get_attr_by_name(self, attr_name) -> Attribute

        Get :class:`~tango.Attribute` object from its name.

        This method returns an :class:`~tango.Attribute` object with a
        name passed as parameter. The equality on attribute name is case
        independant.

        :param attr_name: attribute name
        :type attr_name: str

        :returns: the attribute object
        :rtype: Attribute

        :raises DevFailed: If the attribute is not defined.
    """)

    document_method("get_attr_by_ind", """
    get_attr_by_ind(self, ind) -> Attribute

        Get :class:`~tango.Attribute` object from its index.

        This method returns an :class:`~tango.Attribute` object from the
        index in the main attribute vector.

        :param ind: the attribute index
        :type ind: int

        :returns: the attribute object
        :rtype: Attribute
    """)

    document_method("get_w_attr_by_name", """
    get_w_attr_by_name(self, attr_name) -> WAttribute

        Get a writable attribute object from its name.

        This method returns an :class:`~tango.WAttribute` object with a
        name passed as parameter. The equality on attribute name is case
        independant.

        :param attr_name: attribute name
        :type attr_name: str

        :returns: the attribute object
        :rtype: WAttribute

        :raises DevFailed: If the attribute is not defined.
    """)

    document_method("get_w_attr_by_ind", """
    get_w_attr_by_ind(self, ind) -> WAttribute

        Get a writable attribute object from its index.

        This method returns an :class:`~tango.WAttribute` object from the
        index in the main attribute vector.

        :param ind: the attribute index
        :type ind: int

        :returns: the attribute object
        :rtype: WAttribute
    """)

    document_method("get_attr_ind_by_name", """
    get_attr_ind_by_name(self, attr_name) -> int

        Get Attribute index into the main attribute vector from its name.

        This method returns the index in the Attribute vector (stored in the
        :class:`~tango.MultiAttribute` object) of an attribute with a
        given name. The name equality is case independant.

        :param attr_name: attribute name
        :type attr_name: str

        :returns: the attribute index
        :rtype: int

        :raises DevFailed: If the attribute is not found in the vector.

        New in PyTango 7.0.0
    """)

    document_method("get_attr_nb", """
    get_attr_nb(self) -> int

        Get attribute number.

        :returns: the number of attributes
        :rtype: int

        New in PyTango 7.0.0
    """)

    document_method("check_alarm", """
    check_alarm(self) -> bool

        .. function:: check_alarm(self, attr_name) -> bool
                      check_alarm(self, ind) -> bool
            :noindex:

        Checks an alarm.

        - The 1st version of the method checks alarm on all attribute(s) with an alarm defined.
        - The 2nd version of the method checks alarm for one attribute with a given name.
        - The 3rd version of the method checks alarm for one attribute from its index in the main attributes vector.

        :param attr_name: attribute name
        :type attr_name: str
        :param ind: the attribute index
        :type ind: int

        :returns: True if at least one attribute is in alarm condition
        :rtype: bool

        :raises DevFailed: If at least one attribute does not have any alarm level defined

        New in PyTango 7.0.0
    """)

    document_method("read_alarm", """
    read_alarm(self, status)

        Add alarm message to device status.

        This method add alarm mesage to the string passed as parameter.
        A message is added for each attribute which is in alarm condition

        :param status: a string (should be the device status)
        :type status: str

        New in PyTango 7.0.0
    """)

    document_method("get_attribute_list", """
    get_attribute_list(self) -> Sequence[Attribute]

        Get the list of attribute objects.

        :returns: list of attribute objects
        :rtype: Sequence[Attribute]

        New in PyTango 7.2.1
    """)


def __doc_Attr():
    def document_method(method_name, desc, append=True):
        return __document_method(Attr, method_name, desc, append)

    Attr.__doc__ = """
    This class represents a Tango writable attribute.
    """

    document_method("check_type", """
    check_type(self)

        This method checks data type and throws an exception in case of unsupported data type

        :raises: :class:`DevFailed`: If the data type is unsupported.
    """)

    document_method("is_allowed", """
    is_allowed(self, device, request_type) -> bool

        Returns whether the request_type is allowed for the specified device
        
        :param device: instance of Device
        :type device: :class:`tango.server.Device`
        
        :param request_type: AttReqType.READ_REQ for read request or AttReqType.WRITE_REQ for write request
        :type request_type: :const:`AttReqType`

        :returns: True if request_type is allowed for the specified device
        :rtype: bool
    """)

    # TODO finish description
    # document_method("read", """
    # read(self, device, attribute)
    #
    #     TODO: Check description
    #
    #     Default read empty method. For readable attribute, it is necessary to overwrite it
    #
    #     :param device: instance of Device
    #     :type device: Device
    # """)

    # TODO finish description
    # document_method("write", """
    # write(self, device, attribute)
    #
    #     TODO: Check description
    #
    #     Default write empty method. For writable attribute, it is necessary to overwrite it
    #
    #     :param device: instance of Device
    #     :type device: Device
    # """)


    document_method("set_default_properties", """
    set_default_properties(self)

        Set default attribute properties.

        :param attr_prop: the user default property class
        :type attr_prop: UserDefaultAttrProp
    """)

    document_method("set_disp_level", """
    set_disp_level(self, disp_lelel)

        Set the attribute display level.

        :param disp_level: the new display level
        :type disp_level: DispLevel
    """)

    document_method("set_polling_period", """
    set_polling_period(self, period)

        Set the attribute polling update period.

        :param period: the attribute polling period (in mS)
        :type period: int
    """)

    document_method("set_memorized", """
    set_memorized(self)

        Set the attribute as memorized in database (only for scalar
        and writable attribute).

        With no argument the setpoint will be
        written to the attribute during initialisation!
    """)

    document_method("set_memorized_init", """
    set_memorized_init(self, write_on_init)

        Set the initialisation flag for memorized attributes.

        - true = the setpoint value will be written to the attribute on initialisation
        - false = only the attribute setpoint is initialised.

        No action is taken on the attribute

        :param write_on_init: if true the setpoint value will be written
                              to the attribute on initialisation
        :type write_on_init: bool
    """)

    document_method("set_change_event", """
    set_change_event(self, implemented, detect)

        Set a flag to indicate that the server fires change events manually
        without the polling to be started for the attribute.

        If the detect parameter is set to true, the criteria specified for
        the change event are verified and the event is only pushed if they
        are fullfilled.

        If detect is set to false the event is fired without checking!

        :param implemented: True when the server fires change events manually.
        :type implemented: bool
        :param detect: Triggers the verification of the change event properties
                       when set to true.
        :type detect: bool
    """)

    document_method("is_change_event", """
    is_change_event(self) -> bool

        Check if the change event is fired manually for this attribute.

        :returns: true if a manual fire change event is implemented.
        :rtype: bool
    """)

    document_method("is_check_change_criteria", """
    is_check_change_criteria(self) -> bool

        Check if the change event criteria should be checked when firing the event manually.

        :returns: true if a change event criteria will be checked.
        :rtype: bool
    """)

    document_method("set_archive_event", """
    set_archive_event(self)

        Set a flag to indicate that the server fires archive events manually
        without the polling to be started for the attribute.

        If the detect
        parameter is set to true, the criteria specified for the archive
        event are verified and the event is only pushed if they are fullfilled.

        If detect is set to false the event is fired without checking!

        :param implemented: True when the server fires change events manually.
        :type implemented: bool
        :param detect: Triggers the verification of the archive event properties
                       when set to true.
        :type detect: bool
    """)

    document_method("is_archive_event", """
    is_archive_event(self) -> bool

        Check if the archive event is fired manually for this attribute.

        :returns: true if a manual fire archive event is implemented.
        :rtype: bool
    """)

    document_method("is_check_archive_criteria", """
    is_check_archive_criteria(self) -> bool

        Check if the archive event criteria should be checked when firing the event manually.

        :returns: true if a archive event criteria will be checked.
        :rtype: bool
    """)

    document_method("set_data_ready_event", """
    set_data_ready_event(self, implemented)

        Set a flag to indicate that the server fires data ready events.

        :param implemented: True when the server fires data ready events
        :type implemented: bool

        New in PyTango 7.2.0
    """)

    document_method("is_data_ready_event", """
    is_data_ready_event(self) -> bool

        Check if the data ready event is fired for this attribute.

        :returns: true if firing data ready event is implemented.
        :rtype: bool

        New in PyTango 7.2.0
    """)

    document_method("get_name", """
    get_name(self) -> str

        Get the attribute name.

        :returns: the attribute name
        :rtype: str
    """)

    document_method("get_format", """
    get_format(self) -> AttrDataFormat

        Get the attribute format.

        :returns: the attribute format
        :rtype: AttrDataFormat
    """)

    document_method("get_writable", """
    get_writable(self) -> AttrWriteType

        Get the attribute write type.

        :returns: the attribute write type
        :rtype: AttrWriteType
    """)

    document_method("get_type", """
    get_type(self) -> int

        Get the attribute data type.

        :returns: the attribute data type
        :rtype: int
    """)

    document_method("get_disp_level", """
    get_disp_level(self) -> DispLevel

        Get the attribute display level.

        :returns: the attribute display level
        :rtype: DispLevel
    """)

    document_method("get_polling_period", """
    get_polling_period(self) -> int

        Get the polling period (mS).

        :returns: the polling period (mS)
        :rtype: int
    """)

    document_method("get_memorized", """
    get_memorized(self) -> bool

        Determine if the attribute is memorized or not.

        :returns: True if the attribute is memorized
        :rtype: bool
    """)

    document_method("get_memorized_init", """
    get_memorized_init(self) -> bool

        Determine if the attribute is written at startup from the memorized
        value if it is memorized.

        :returns: True if initialized with memorized value or not
        :rtype: bool
    """)

    document_method("get_assoc", """
    get_assoc(self) -> str

        Get the associated name.

        :returns: the associated name
        :rtype: bool
    """)

    document_method("is_assoc", """
    is_assoc(self) -> bool

        Determine if it is assoc.

        :returns: if it is assoc
        :rtype: bool
    """)

    document_method("get_cl_name", """
    get_cl_name(self) -> str

        Returns the class name.

        :returns: the class name
        :rtype: str

        New in PyTango 7.2.0
    """)

    document_method("set_cl_name", """
    set_cl_name(self, cl)

        Sets the class name.

        :param cl: new class name
        :type cl: str

        New in PyTango 7.2.0
    """)

    document_method("get_class_properties", """
    get_class_properties(self) -> Sequence[AttrProperty]

        Get the class level attribute properties.

        :returns: the class attribute properties
        :rtype: Sequence[AttrProperty]
    """)

    document_method("get_user_default_properties", """
    get_user_default_properties(self) -> Sequence[AttrProperty]

        Get the user default attribute properties.

        :returns: the user default attribute properties
        :rtype: Sequence[AttrProperty]
    """)

    document_method("set_class_properties", """
    set_class_properties(self, props)

        Set the class level attribute properties.

        :param props: new class level attribute properties
        :type props: StdAttrPropertyVector
    """)


def __doc_UserDefaultAttrProp():
    def document_method(method_name, desc, append=True):
        return __document_method(UserDefaultAttrProp, method_name, desc, append)

    UserDefaultAttrProp.__doc__ = """
    User class to set attribute default properties.

    This class is used to set attribute default properties.
    Three levels of attributes properties setting are implemented within Tango.
    The highest property setting level is the database.
    Then the user default (set using this UserDefaultAttrProp class) and finally
    a Tango library default value.
    """

    document_method("set_label", """
    set_label(self, def_label)

        Set default label property.

        :param def_label: the user default label property
        :type def_label: str
    """)

    document_method("set_description", """
    set_description(self, def_description)

        Set default description property.

        :param def_description: the user default description property
        :type def_description: str
    """)

    document_method("set_format", """
    set_format(self, def_format)

        Set default format property.

        :param def_format: the user default format property
        :type def_format: str
    """)

    document_method("set_unit", """
    set_unit(self, def_unit)

        Set default unit property.

        :param def_unit: te user default unit property
        :type def_unit: str
    """)

    document_method("set_standard_unit", """
    set_standard_unit(self, def_standard_unit)

        Set default standard unit property.

        :param def_standard_unit: the user default standard unit property
        :type def_standard_unit: str
    """)

    document_method("set_display_unit", """
    set_display_unit(self, def_display_unit)

        Set default display unit property.

        :param def_display_unit: the user default display unit property
        :type def_display_unit: str
    """)

    document_method("set_min_value", """
    set_min_value(self, def_min_value)

        Set default min_value property.

        :param def_min_value: the user default min_value property
        :type def_min_value: str
    """)

    document_method("set_max_value", """
    set_max_value(self, def_max_value)

        Set default max_value property.

        :param def_max_value: the user default max_value property
        :type def_max_value: str
    """)

    document_method("set_min_alarm", """
    set_min_alarm(self, def_min_alarm)

        Set default min_alarm property.

        :param def_min_alarm: the user default min_alarm property
        :type def_min_alarm: str
    """)

    document_method("set_max_alarm", """
    set_max_alarm(self, def_max_alarm)

        Set default max_alarm property.

        :param def_max_alarm: the user default max_alarm property
        :type def_max_alarm: str
    """)

    document_method("set_min_warning", """
    set_min_warning(self, def_min_warning)

        Set default min_warning property.

        :param def_min_warning: the user default min_warning property
        :type def_min_warning: str
    """)

    document_method("set_max_warning", """
    set_max_warning(self, def_max_warning)

        Set default max_warning property.

        :param def_max_warning: the user default max_warning property
        :type def_max_warning: str
    """)

    document_method("set_delta_t", """
    set_delta_t(self, def_delta_t)

        Set default RDS alarm delta_t property.

        :param def_delta_t: the user default RDS alarm delta_t property
        :type def_delta_t: str
    """)

    document_method("set_delta_val", """
    set_delta_val(self, def_delta_val)

        Set default RDS alarm delta_val property.

        :param def_delta_val: the user default RDS alarm delta_val property
        :type def_delta_val: str
    """)

    document_method("set_abs_change", """
    set_abs_change(self, def_abs_change) <= DEPRECATED

        Set default change event abs_change property.

        :param def_abs_change: the user default change event abs_change property
        :type def_abs_change: str

        Deprecated since PyTango 8.0. Please use set_event_abs_change instead.
    """)

    document_method("set_event_abs_change", """
    set_event_abs_change(self, def_abs_change)

        Set default change event abs_change property.

        :param def_abs_change: the user default change event abs_change property
        :type def_abs_change: str

        New in PyTango 8.0
    """)

    document_method("set_rel_change", """
    set_rel_change(self, def_rel_change) <= DEPRECATED

        Set default change event rel_change property.

        :param def_rel_change: the user default change event rel_change property
        :type def_rel_change: str

        Deprecated since PyTango 8.0. Please use set_event_rel_change instead.
    """)

    document_method("set_event_rel_change", """
    set_event_rel_change(self, def_rel_change)

        Set default change event rel_change property.

        :param def_rel_change: the user default change event rel_change property
        :type def_rel_change: str

        New in PyTango 8.0
    """)

    document_method("set_period", """
    set_period(self, def_period) <= DEPRECATED

        Set default periodic event period property.

        :param def_period: the user default periodic event period property
        :type def_period: str

        Deprecated since PyTango 8.0. Please use set_event_period instead.
    """)

    document_method("set_event_period", """
    set_event_period(self, def_period)

        Set default periodic event period property.

        :param def_period: the user default periodic event period property
        :type def_period: str

        New in PyTango 8.0
    """)

    document_method("set_archive_abs_change", """
    set_archive_abs_change(self, def_archive_abs_change) <= DEPRECATED

        Set default archive event abs_change property.

        :param def_archive_abs_change: the user default archive event abs_change property
        :type def_archive_abs_change: str

        Deprecated since PyTango 8.0. Please use set_archive_event_abs_change instead.
    """)

    document_method("set_archive_event_abs_change", """
    set_archive_event_abs_change(self, def_archive_abs_change)

        Set default archive event abs_change property.

        :param def_archive_abs_change: the user default archive event abs_change property
        :type def_archive_abs_change: str

        New in PyTango 8.0
    """)

    document_method("set_archive_rel_change", """
    set_archive_rel_change(self, def_archive_rel_change) <= DEPRECATED

        Set default archive event rel_change property.

        :param def_archive_rel_change: the user default archive event rel_change property
        :type def_archive_rel_change: str

        Deprecated since PyTango 8.0. Please use set_archive_event_rel_change instead.
    """)

    document_method("set_archive_event_rel_change", """
    set_archive_event_rel_change(self, def_archive_rel_change)

        Set default archive event rel_change property.

        :param def_archive_rel_change: the user default archive event rel_change property
        :type def_archive_rel_change: str

        New in PyTango 8.0
    """)

    document_method("set_archive_period", """
    set_archive_period(self, def_archive_period) <= DEPRECATED

        Set default archive event period property.

        :param def_archive_period: t
        :type def_archive_period: str

        Deprecated since PyTango 8.0. Please use set_archive_event_period instead.
    """)

    document_method("set_archive_event_period", """
    set_archive_event_period(self, def_archive_period)

        Set default archive event period property.

        :param def_archive_period: t
        :type def_archive_period: str

        New in PyTango 8.0
    """)


def device_server_init(doc=True):
    __init_DeviceImpl()
    __init_Attribute()
    __init_Attr()
    __init_UserDefaultAttrProp()
    __init_Logger()
    if doc:
        __doc_DeviceImpl()
        __doc_extra_DeviceImpl(Device_3Impl)
        __doc_extra_DeviceImpl(Device_4Impl)
        __doc_extra_DeviceImpl(Device_5Impl)
        __doc_Attribute()
        __doc_WAttribute()
        __doc_MultiAttribute()
        __doc_MultiClassAttribute()
        __doc_UserDefaultAttrProp()
        __doc_Attr()

