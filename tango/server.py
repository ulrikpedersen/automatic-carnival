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

"""Server helper classes for writing Tango device servers."""


import sys
import copy
from inspect import getfullargspec
import inspect
import logging
import functools
import traceback

from ._tango import AttrDataFormat, AttrWriteType, CmdArgType, PipeWriteType
from ._tango import DevFailed, GreenMode, SerialModel

from .attr_data import AttrData
from .pipe_data import PipeData
from .device_class import DeviceClass
from .device_server import LatestDeviceImpl, get_worker, set_worker, run_in_executor
from .utils import get_enum_labels
from .utils import (
    is_seq,
    is_non_str_seq,
    is_pure_str,
    is_enum_seq,
    is_enum,
    set_complex_value,
)
from .utils import is_devstate, is_devstate_seq, scalar_to_array_type, TO_TANGO_TYPE
from .green import get_green_mode, get_executor
from .pyutil import Util

__all__ = (
    "DeviceMeta",
    "Device",
    "LatestDeviceImpl",
    "attribute",
    "command",
    "pipe",
    "device_property",
    "class_property",
    "run",
    "server_run",
    "Server",
)

API_VERSION = 2

# Helpers


def _get_tango_type_format(dtype=None, dformat=None, caller=None):
    if dformat is None:
        dformat = AttrDataFormat.SCALAR
        if is_non_str_seq(dtype):
            if len(dtype):
                dtype = dtype[0]
                dformat = AttrDataFormat.SPECTRUM
                if is_non_str_seq(dtype):
                    if len(dtype):
                        dtype = dtype[0]
                        dformat = AttrDataFormat.IMAGE
                    elif caller == "attribute":
                        raise TypeError(
                            "Image attribute type must be specified as ((<dtype>,),)"
                        )
            elif caller == "attribute":
                raise TypeError(
                    "Spectrum attribute type must be specified as (<dtype>,)"
                )
    return TO_TANGO_TYPE[dtype], dformat


def from_typeformat_to_type(dtype, dformat):
    if dformat == AttrDataFormat.SCALAR:
        return dtype
    elif dformat == AttrDataFormat.IMAGE:
        raise TypeError("Cannot translate IMAGE to tango type")
    return scalar_to_array_type(dtype)


def __get_wrapped_read_method(attribute, read_method):
    """
    Make sure attr is updated on read, and wrap it with executor, if needed.

    :param attribute: the attribute data information
    :type attribute: AttrData
    :param read_method: read method
    :type read_method: callable
    """

    already_wrapped = hasattr(read_method, "__access_wrapped__")
    if already_wrapped:
        return read_method

    if attribute.read_green_mode:

        @functools.wraps(read_method)
        def read_attr(self, attr):
            worker = get_worker()
            ret = worker.execute(read_method, self)
            if not attr.get_value_flag() and ret is not None:
                set_complex_value(attr, ret)
            return ret

    else:

        @functools.wraps(read_method)
        def read_attr(self, attr):
            ret = read_method(self)
            if not attr.get_value_flag() and ret is not None:
                set_complex_value(attr, ret)
            return ret

    read_attr.__access_wrapped__ = True
    return read_attr


def __patch_read_method(tango_device_klass, attribute):
    """
    Finds read method for attribute, wraps it with executor and adds
    wrapped method to device dict.

    :param tango_device_klass: a DeviceImpl class
    :type tango_device_klass: class
    :param attribute: the attribute data information
    :type attribute: AttrData
    """
    read_method = getattr(attribute, "fget", None)
    if not read_method:
        method_name = attribute.read_method_name
        read_method = getattr(tango_device_klass, method_name)

    read_attr = __get_wrapped_read_method(attribute, read_method)
    method_name = f"__read_{attribute.attr_name}_wrapper__"
    attribute.read_method_name = method_name

    setattr(tango_device_klass, method_name, read_attr)


def __get_wrapped_write_method(attribute, write_method):
    """
    Wraps write method with executor, if needed.
    """
    already_wrapped = hasattr(write_method, "__access_wrapped__")
    if already_wrapped:
        return write_method

    if attribute.write_green_mode:

        @functools.wraps(write_method)
        def write_attr(self, attr):
            value = attr.get_write_value()
            return get_worker().execute(write_method, self, value)

    else:

        @functools.wraps(write_method)
        def write_attr(self, attr):
            value = attr.get_write_value()
            return write_method(self, value)

    write_attr.__access_wrapped__ = True
    return write_attr


def __patch_write_method(tango_device_klass, attribute):
    """
    Finds write method for attribute, wraps it with executor and adds
    wrapped method to device dict.

    :param tango_device_klass: a DeviceImpl class
    :type tango_device_klass: class
    :param attribute: the attribute data information
    :type attribute: AttrData
    """
    write_method = getattr(attribute, "fset", None)
    if not write_method:
        method_name = attribute.write_method_name
        write_method = getattr(tango_device_klass, method_name)

    write_attr = __get_wrapped_write_method(attribute, write_method)
    method_name = f"__write_{attribute.attr_name}_wrapper__"
    attribute.write_method_name = method_name

    setattr(tango_device_klass, method_name, write_attr)


def __get_wrapped_isallowed_method(attribute, isallowed_method):
    """
    Wraps is allowed method with executor, if needed.

    :param attribute: the attribute data information
    :type attribute: AttrData
    :param isallowed_method: is allowed method
    :type isallowed_method: callable
    """
    already_wrapped = hasattr(isallowed_method, "__access_wrapped__")
    if already_wrapped:
        return isallowed_method

    if attribute.isallowed_green_mode:

        @functools.wraps(isallowed_method)
        def isallowed_attr(self, request_type):
            worker = get_worker()
            return worker.execute(isallowed_method, self, request_type)

    else:
        isallowed_attr = isallowed_method

    if isallowed_attr is not isallowed_method:
        isallowed_attr.__access_wrapped__ = True
    return isallowed_attr


def __patch_isallowed_method(tango_device_klass, attribute):
    """
    Finds isallowed method for attribute, wraps it with executor and adds
    wrapped method to device dict.

    :param tango_device_klass: a DeviceImpl class
    :type tango_device_klass: class
    :param attribute: the attribute data information
    :type attribute: AttrData
    """
    isallowed_method = getattr(attribute, "fisallowed", None)
    if not isallowed_method:
        method_name = attribute.is_allowed_name
        isallowed_method = getattr(tango_device_klass, method_name, None)

    if isallowed_method:
        isallowed_attr = __get_wrapped_isallowed_method(attribute, isallowed_method)
        method_name = f"__is_{attribute.attr_name}_allowed_wrapper__"
        attribute.is_allowed_name = method_name

        setattr(tango_device_klass, method_name, isallowed_attr)


def __patch_attr_methods(tango_device_klass, attribute):
    """
    Finds read, write and isallowed methods for attribute, and
    wraps into another method to make them work.

    Also patch methods with green executor, if requested.

    Finally, adds pathed methods to the device dict.

    :param tango_device_klass: a DeviceImpl class
    :type tango_device_klass: class
    :param attribute: the attribute data information
    :type attribute: AttrData
    """
    if attribute.attr_write in (AttrWriteType.READ, AttrWriteType.READ_WRITE):
        __patch_read_method(tango_device_klass, attribute)
    if attribute.attr_write in (AttrWriteType.WRITE, AttrWriteType.READ_WRITE):
        __patch_write_method(tango_device_klass, attribute)

    __patch_isallowed_method(tango_device_klass, attribute)


def __get_wrapped_pipe_read_method(pipe, read_method):
    already_wrapped = hasattr(read_method, "__access_wrapped__")
    if already_wrapped:
        return read_method

    if pipe.read_green_mode:

        @functools.wraps(read_method)
        def read_pipe(self, pipe):
            worker = get_worker()
            ret = worker.execute(read_method, self)
            if ret is not None:
                pipe.set_value(ret)
            return ret

    else:

        @functools.wraps(read_method)
        def read_pipe(self, pipe):
            ret = read_method(self)
            if ret is not None:
                pipe.set_value(ret)
            return ret

    if read_pipe is not read_method:
        read_pipe.__access_wrapped__ = True
    return read_pipe


def __patch_pipe_read_method(tango_device_klass, pipe):
    """
    Finds read method for pipe, wraps it with executor and adds wrapped
    method to device dict.

    :param tango_device_klass: a DeviceImpl class
    :type tango_device_klass: class
    :param pipe: the pipe data information
    :type pipe: PipeData
    """
    read_method = getattr(pipe, "fget", None)
    if not read_method:
        method_name = pipe.read_method_name
        read_method = getattr(tango_device_klass, method_name)

    read_pipe = __get_wrapped_pipe_read_method(pipe, read_method)
    method_name = f"__read_{pipe.pipe_name}_wrapper__"
    pipe.read_method_name = method_name

    setattr(tango_device_klass, method_name, read_pipe)


def __get_wrapped_pipe_write_method(pipe, write_method):
    already_wrapped = hasattr(write_method, "__access_wrapped__")
    if already_wrapped:
        return write_method

    if pipe.write_green_mode:

        @functools.wraps(write_method)
        def write_pipe(self, pipe):
            value = pipe.get_value()
            return get_worker().execute(write_method, self, value)

    else:

        @functools.wraps(write_method)
        def write_pipe(self, pipe):
            value = pipe.get_value()
            return write_method(self, value)

    write_pipe.__access_wrapped__ = True
    return write_pipe


def __patch_pipe_write_method(tango_device_klass, pipe):
    """
    Finds write method for pipe, wraps it with executor and adds wrapped
    method to device dict.

    :param tango_device_klass: a DeviceImpl class
    :type tango_device_klass: class
    :param pipe: the pipe data information
    :type pipe: PipeData
    """
    write_method = getattr(pipe, "fset", None)
    if not write_method:
        method_name = pipe.write_method_name
        write_method = getattr(tango_device_klass, method_name)

    write_pipe = __get_wrapped_pipe_write_method(pipe, write_method)
    method_name = f"__write_{pipe.pipe_name}_wrapper__"
    pipe.write_method_name = method_name

    setattr(tango_device_klass, method_name, write_pipe)


def __get_wrapped_pipe_isallowed_method(pipe, isallowed_method):
    """
    Wraps is allowed method with executor, if needed.

    :param pipe: the pipe data information
    :type pipe: PipeData
    :param isallowed_method: is allowed method
    :type isallowed_method: callable
    """
    already_wrapped = hasattr(isallowed_method, "__access_wrapped__")
    if already_wrapped:
        return isallowed_method

    if pipe.isallowed_green_mode:

        @functools.wraps(isallowed_method)
        def isallowed_pipe(self, request_type):
            worker = get_worker()
            return worker.execute(isallowed_method, self, request_type)

    else:
        isallowed_pipe = isallowed_method

    if isallowed_pipe is not isallowed_method:
        isallowed_pipe.__access_wrapped__ = True
    return isallowed_pipe


def __patch_pipe_isallowed_method(tango_device_klass, pipe):
    """
    Finds isallowed method for pipe, wraps it with executor and adds
    wrapped method to device dict.

    :param tango_device_klass: a DeviceImpl class
    :type tango_device_klass: class
    :param pipe: the pipe data information
    :type pipe: PipeData
    """
    isallowed_method = getattr(pipe, "fisallowed", None)
    if not isallowed_method:
        method_name = pipe.is_allowed_name
        isallowed_method = getattr(tango_device_klass, method_name, None)

    if isallowed_method:
        isallowed_attr = __get_wrapped_pipe_isallowed_method(pipe, isallowed_method)
        method_name = f"__is_{pipe.pipe_name}_allowed_wrapper__"
        pipe.is_allowed_name = method_name

        setattr(tango_device_klass, method_name, isallowed_attr)


def __patch_pipe_methods(tango_device_klass, pipe):
    """
    Finds read, write and isallowed methods for pipe, and
    wraps into another method to make them work.

    Also patch methods with green executor, if requested.

    Finally, adds pathed methods to the device dict.

    :param tango_device_klass: a DeviceImpl class
    :type tango_device_klass: class
    :param pipe: the pipe data information
    :type pipe: PipeData
    """
    __patch_pipe_read_method(tango_device_klass, pipe)
    if pipe.pipe_write == PipeWriteType.PIPE_READ_WRITE:
        __patch_pipe_write_method(tango_device_klass, pipe)
    __patch_pipe_isallowed_method(tango_device_klass, pipe)


def __patch_is_command_allowed_method(tango_device_klass, is_allowed_method, cmd_name):
    """
    :param tango_device_klass: a DeviceImpl class
    :type tango_device_klass: class
    :param is_allowed_method: a callable to check if command is allowed
    :type is_allowed_method: callable
    :param cmd_name: command name
    :type cmd_name: str
    """
    already_wrapped = hasattr(is_allowed_method, "__access_wrapped__")
    if already_wrapped:
        return is_allowed_method.__wrapped_method_name__

    method_name = getattr(is_allowed_method, "__name__", f"is_{cmd_name}_allowed")
    method_name = f"__wrapped_{method_name}__"

    wrapped_method = run_in_executor(is_allowed_method)
    wrapped_method.__access_wrapped__ = True
    wrapped_method.__wrapped_method_name__ = method_name
    setattr(tango_device_klass, method_name, wrapped_method)

    return method_name


def __patch_standard_device_methods(klass):
    # TODO allow to force non green mode

    init_device_orig = klass.init_device
    already_wrapped = hasattr(init_device_orig, "__access_wrapped__")
    if not already_wrapped:

        @functools.wraps(init_device_orig)
        def init_device(self):
            return get_worker().execute(init_device_orig, self)

        init_device.__access_wrapped__ = True
        setattr(klass, "init_device", init_device)

    delete_device_orig = klass.delete_device
    already_wrapped = hasattr(delete_device_orig, "__access_wrapped__")
    if not already_wrapped:

        @functools.wraps(delete_device_orig)
        def delete_device(self):
            return get_worker().execute(delete_device_orig, self)

        delete_device.__access_wrapped__ = True
        setattr(klass, "delete_device", delete_device)

    dev_state_orig = klass.dev_state
    already_wrapped = hasattr(dev_state_orig, "__access_wrapped__")
    if not already_wrapped:

        @functools.wraps(dev_state_orig)
        def dev_state(self):
            return get_worker().execute(dev_state_orig, self)

        dev_state.__access_wrapped__ = True
        setattr(klass, "dev_state", dev_state)

    dev_status_orig = klass.dev_status
    already_wrapped = hasattr(dev_status_orig, "__access_wrapped__")
    if not already_wrapped:

        @functools.wraps(dev_status_orig)
        def dev_status(self):
            return get_worker().execute(dev_status_orig, self)

        dev_status.__access_wrapped__ = True
        setattr(klass, "dev_status", dev_status)

    read_attr_hardware_orig = klass.read_attr_hardware
    already_wrapped = hasattr(read_attr_hardware_orig, "__access_wrapped__")
    if not already_wrapped:

        @functools.wraps(read_attr_hardware_orig)
        def read_attr_hardware(self, attr_list):
            return get_worker().execute(read_attr_hardware_orig, self, attr_list)

        read_attr_hardware.__access_wrapped__ = True
        setattr(klass, "read_attr_hardware", read_attr_hardware)

    always_executed_hook_orig = klass.always_executed_hook
    already_wrapped = hasattr(always_executed_hook_orig, "__access_wrapped__")
    if not already_wrapped:

        @functools.wraps(always_executed_hook_orig)
        def always_executed_hook(self):
            return get_worker().execute(always_executed_hook_orig, self)

        always_executed_hook.__access_wrapped__ = True
        setattr(klass, "always_executed_hook", always_executed_hook)


class _DeviceClass(DeviceClass):
    def __init__(self, name):
        DeviceClass.__init__(self, name)
        self.set_type(name)

    def dyn_attr(self, dev_list):
        """Invoked to create dynamic attributes for the given devices.
        Default implementation calls
        :meth:`TT.initialize_dynamic_attributes` for each device

        :param dev_list: list of devices
        :type dev_list: :class:`tango.DeviceImpl`"""

        for dev in dev_list:
            init_dyn_attrs = getattr(dev, "initialize_dynamic_attributes", None)
            if init_dyn_attrs and callable(init_dyn_attrs):
                try:
                    init_dyn_attrs()
                except Exception as ex:
                    dev.warn_stream("Failed to initialize dynamic attributes")
                    dev.debug_stream("Details: " + traceback.format_exc())
                    raise Exception(repr(ex))


def __create_tango_deviceclass_klass(tango_device_klass, attrs=None):
    klass_name = tango_device_klass.__name__
    if not issubclass(tango_device_klass, (BaseDevice)):
        msg = f"{klass_name} device must inherit from tango.server.Device"
        raise Exception(msg)

    if attrs is None:
        attrs = tango_device_klass.__dict__

    attr_list = {}
    pipe_list = {}
    class_property_list = {}
    device_property_list = {}
    cmd_list = {}

    for attr_name, attr_obj in attrs.items():
        if isinstance(attr_obj, attribute):
            if attr_obj.attr_name is None:
                attr_obj._set_name(attr_name)
            else:
                attr_name = attr_obj.attr_name
            attr_list[attr_name] = attr_obj
            if not attr_obj.forward:
                __patch_attr_methods(tango_device_klass, attr_obj)
        elif isinstance(attr_obj, pipe):
            if attr_obj.pipe_name is None:
                attr_obj._set_name(attr_name)
            else:
                attr_name = attr_obj.pipe_name
            pipe_list[attr_name] = attr_obj
            __patch_pipe_methods(tango_device_klass, attr_obj)
        elif isinstance(attr_obj, device_property):
            attr_obj.name = attr_name
            # if you modify the attr_obj order then you should
            # take care of the code in get_device_properties()
            device_property_list[attr_name] = [
                attr_obj.dtype,
                attr_obj.doc,
                attr_obj.default_value,
                attr_obj.mandatory,
            ]
        elif isinstance(attr_obj, class_property):
            attr_obj.name = attr_name
            class_property_list[attr_name] = [
                attr_obj.dtype,
                attr_obj.doc,
                attr_obj.default_value,
            ]
        elif inspect.isroutine(attr_obj):
            if hasattr(attr_obj, "__tango_command__"):
                cmd_name, cmd_info = attr_obj.__tango_command__
                cmd_list[cmd_name] = cmd_info
                if "Is allowed" in cmd_info[2]:
                    is_allowed_method = cmd_info[2]["Is allowed"]
                else:
                    is_allowed_method = f"is_{cmd_name}_allowed"

                if is_pure_str(is_allowed_method):
                    is_allowed_method = getattr(
                        tango_device_klass, is_allowed_method, None
                    )

                if is_allowed_method is not None:
                    cmd_info[2]["Is allowed"] = __patch_is_command_allowed_method(
                        tango_device_klass, is_allowed_method, cmd_name
                    )

    __patch_standard_device_methods(tango_device_klass)

    devclass_name = klass_name + "Class"

    devclass_attrs = dict(
        class_property_list=class_property_list,
        device_property_list=device_property_list,
        cmd_list=cmd_list,
        attr_list=attr_list,
        pipe_list=pipe_list,
    )
    return type(_DeviceClass)(devclass_name, (_DeviceClass,), devclass_attrs)


def _init_tango_device_klass(tango_device_klass, attrs=None, tango_class_name=None):
    klass_name = tango_device_klass.__name__
    tango_deviceclass_klass = __create_tango_deviceclass_klass(
        tango_device_klass, attrs=attrs
    )
    if tango_class_name is None:
        if hasattr(tango_device_klass, "TangoClassName"):
            tango_class_name = tango_device_klass.TangoClassName
        else:
            tango_class_name = klass_name
    tango_device_klass.TangoClassClass = tango_deviceclass_klass
    tango_device_klass.TangoClassName = tango_class_name
    tango_device_klass._api = API_VERSION
    return tango_device_klass


def is_tango_object(arg):
    """Return tango data if the argument is a tango object,
    False otherwise.
    """
    classes = attribute, device_property, pipe
    if isinstance(arg, classes):
        return arg
    try:
        return arg.__tango_command__
    except AttributeError:
        return False


def inheritance_patch(attrs):
    """Patch tango objects before they are processed by the metaclass."""
    for key, obj in attrs.items():
        if isinstance(obj, attribute):
            if getattr(obj, "attr_write", None) == AttrWriteType.READ_WRITE:
                if not getattr(obj, "fset", None):
                    method_name = obj.write_method_name or "write_" + key
                    obj.fset = attrs.get(method_name)


class DeviceMeta(type(LatestDeviceImpl)):
    """
    The :py:data:`metaclass` callable for :class:`Device`.

    This implementation of DeviceMeta makes device inheritance possible.
    """

    def __new__(metacls, name, bases, attrs):
        # Attribute dictionary
        dct = {}
        # Filter object from bases
        bases = tuple(base for base in bases if base != object)
        # Set tango objects as attributes
        for base in reversed(bases):
            for key, value in base.__dict__.items():
                if is_tango_object(value):
                    dct[key] = value
        # Inheritance patch
        inheritance_patch(attrs)
        # Update attribute dictionary
        dct.update(attrs)
        # Create device class
        cls = type(LatestDeviceImpl).__new__(metacls, name, bases, dct)
        # Initialize device class
        _init_tango_device_klass(cls, dct)
        cls.TangoClassName = name
        # Return device class
        return cls


class BaseDevice(LatestDeviceImpl):
    """
    Base device class for the High level API.

    It should not be used directly, since this class is not an
    instance of MetaDevice. Use tango.server.Device instead.
    """

    def __init__(self, cl, name):
        self._tango_properties = {}
        LatestDeviceImpl.__init__(self, cl, name)
        self.init_device()

    def init_device(self):
        """
        Tango init_device method. Default implementation calls
        :meth:`get_device_properties`"""
        self.get_device_properties()

    def delete_device(self):
        pass

    delete_device.__doc__ = LatestDeviceImpl.delete_device.__doc__

    def read_attr_hardware(self, attr_list):
        return LatestDeviceImpl.read_attr_hardware(self, attr_list)

    def dev_state(self):
        return LatestDeviceImpl.dev_state(self)

    def dev_status(self):
        return LatestDeviceImpl.dev_status(self)

    def get_device_properties(self, ds_class=None):
        if ds_class is None:
            try:
                # Call this method in a try/except in case this is called
                # during the DS shutdown sequence
                ds_class = self.get_device_class()
            except Exception:
                return
        try:
            pu = self.prop_util = ds_class.prop_util
            self.device_property_list = copy.deepcopy(ds_class.device_property_list)
            class_prop = ds_class.class_property_list
            pu.get_device_properties(self, class_prop, self.device_property_list)
            for prop_name in class_prop:
                value = pu.get_property_values(prop_name, class_prop)
                self._tango_properties[prop_name] = value
            for prop_name in self.device_property_list:
                value = self.prop_util.get_property_values(
                    prop_name, self.device_property_list
                )
                self._tango_properties[prop_name] = value
                properties = self.device_property_list[prop_name]
                mandatory = properties[3]
                if mandatory and value is None:
                    msg = f"Device property {prop_name} is mandatory "
                    raise Exception(msg)
        except DevFailed as df:
            print(80 * "-")
            print(df)
            raise df

    def always_executed_hook(self):
        """
        Tango always_executed_hook. Default implementation does
        nothing
        """
        pass

    def initialize_dynamic_attributes(self):
        """
        Method executed at initializion phase to create dynamic
        attributes. Default implementation does nothing. Overwrite
        when necessary.
        """
        pass

    @classmethod
    def run_server(cls, args=None, **kwargs):
        """Run the class as a device server.
        It is based on the tango.server.run method.

        The difference is that the device class
        and server name are automatically given.

        Args:
            args (iterable): args as given in the tango.server.run method
                             without the server name. If None, the sys.argv
                             list is used
            kwargs: the other keywords argument are as given
                    in the tango.server.run method.
        """
        if args is None:
            args = sys.argv[1:]
        args = [cls.__name__] + list(args)
        green_mode = getattr(cls, "green_mode", None)
        kwargs.setdefault("green_mode", green_mode)
        return run((cls,), args, **kwargs)


class attribute(AttrData):
    '''
    Declares a new tango attribute in a :class:`Device`. To be used
    like the python native :obj:`property` function. For example, to
    declare a scalar, `tango.DevDouble`, read-only attribute called
    *voltage* in a *PowerSupply* :class:`Device` do::

        class PowerSupply(Device):

            voltage = attribute()

            def read_voltage(self):
                return 999.999

    The same can be achieved with::

        class PowerSupply(Device):

            @attribute
            def voltage(self):
                return 999.999


    It receives multiple keyword arguments.

    ===================== ================================ ======================================= =======================================================================================
    parameter              type                                       default value                                 description
    ===================== ================================ ======================================= =======================================================================================
    name                   :obj:`str`                       class member name                       alternative attribute name
    dtype                  :obj:`object`                    :obj:`~tango.CmdArgType.DevDouble`      data type (see :ref:`Data type equivalence <pytango-hlapi-datatypes>`)
    dformat                :obj:`~tango.AttrDataFormat`     :obj:`~tango.AttrDataFormat.SCALAR`     data format
    max_dim_x              :obj:`int`                       1                                       maximum size for x dimension (ignored for SCALAR format)
    max_dim_y              :obj:`int`                       0                                       maximum size for y dimension (ignored for SCALAR and SPECTRUM formats)
    display_level          :obj:`~tango.DispLevel`          :obj:`~tango.DisLevel.OPERATOR`         display level
    polling_period         :obj:`int`                       -1                                      polling period
    memorized              :obj:`bool`                      False                                   attribute should or not be memorized
    hw_memorized           :obj:`bool`                      False                                   write method should be called at startup when restoring memorize value (dangerous!)
    access                 :obj:`~tango.AttrWriteType`      :obj:`~tango.AttrWriteType.READ`        read only/ read write / write only access
    fget (or fread)        :obj:`str` or :obj:`callable`    'read_<attr_name>'                      read method name or method object
    fset (or fwrite)       :obj:`str` or :obj:`callable`    'write_<attr_name>'                     write method name or method object
    fisallowed             :obj:`str` or :obj:`callable`    'is_<attr_name>_allowed'                is allowed method name or method object
    label                  :obj:`str`                       '<attr_name>'                           attribute label
    enum_labels            sequence                         None                                    the list of enumeration labels (enum data type)
    doc (or description)   :obj:`str`                       ''                                      attribute description
    unit                   :obj:`str`                       ''                                      physical units the attribute value is in
    standard_unit          :obj:`str`                       ''                                      physical standard unit
    display_unit           :obj:`str`                       ''                                      physical display unit (hint for clients)
    format                 :obj:`str`                       '6.2f'                                  attribute representation format
    min_value              :obj:`str`                       None                                    minimum allowed value
    max_value              :obj:`str`                       None                                    maximum allowed value
    min_alarm              :obj:`str`                       None                                    minimum value to trigger attribute alarm
    max_alarm              :obj:`str`                       None                                    maximum value to trigger attribute alarm
    min_warning            :obj:`str`                       None                                    minimum value to trigger attribute warning
    max_warning            :obj:`str`                       None                                    maximum value to trigger attribute warning
    delta_val              :obj:`str`                       None
    delta_t                :obj:`str`                       None
    abs_change             :obj:`str`                       None                                    minimum value change between events that causes event filter to send the event
    rel_change             :obj:`str`                       None                                    minimum relative change between events that causes event filter to send the event (%)
    period                 :obj:`str`                       None
    archive_abs_change     :obj:`str`                       None
    archive_rel_change     :obj:`str`                       None
    archive_period         :obj:`str`                       None
    green_mode             :obj:`bool`                      True                                    Default green mode for read/write/isallowed functions. If True: run with green mode executor, if False: run directly
    read_green_mode        :obj:`bool`                      'green_mode' value                      green mode for read function. If True: run with green mode executor, if False: run directly
    write_green_mode       :obj:`bool`                      'green_mode' value                      green mode for write function. If True: run with green mode executor, if False: run directly
    isallowed_green_mode   :obj:`bool`                      'green_mode' value                      green mode for is allowed function. If True: run with green mode executor, if False: run directly
    forwarded              :obj:`bool`                      False                                   the attribute should be forwarded if True
    ===================== ================================ ======================================= =======================================================================================

    .. note::
        avoid using *dformat* parameter. If you need a SPECTRUM
        attribute of say, boolean type, use instead ``dtype=(bool,)``.

    Example of a integer writable attribute with a customized label,
    unit and description::

        class PowerSupply(Device):

            current = attribute(label="Current", unit="mA", dtype=int,
                                access=AttrWriteType.READ_WRITE,
                                doc="the power supply current")

            def init_device(self):
                Device.init_device(self)
                self._current = -1

            def read_current(self):
                return self._current

            def write_current(self, current):
                self._current = current

    The same, but using attribute as a decorator::

        class PowerSupply(Device):

            def init_device(self):
                Device.init_device(self)
                self._current = -1

            @attribute(label="Current", unit="mA", dtype=int)
            def current(self):
                """the power supply current"""
                return 999.999

            @current.write
            def current(self, current):
                self._current = current

    In this second format, defining the `write` implicitly sets the attribute
    access to READ_WRITE.

    .. versionadded:: 8.1.7
        added green_mode, read_green_mode and write_green_mode options
    '''

    def __init__(self, fget=None, **kwargs):
        self._kwargs = dict(kwargs)
        self.name = kwargs.pop("name", None)
        class_name = kwargs.pop("class_name", None)
        forward = kwargs.get("forwarded", False)
        if forward:
            expected = 2 if "label" in kwargs else 1
            if len(kwargs) > expected:
                raise TypeError("Forwarded attributes only support label argument")
        else:
            green_mode = kwargs.pop("green_mode", True)
            self.read_green_mode = kwargs.pop("read_green_mode", green_mode)
            self.write_green_mode = kwargs.pop("write_green_mode", green_mode)
            self.isallowed_green_mode = kwargs.pop("isallowed_green_mode", green_mode)

            if not fget:
                fget = kwargs.pop("fread", None)

            if fget:
                if inspect.isroutine(fget):
                    self.fget = fget
                    if "doc" not in kwargs and "description" not in kwargs:
                        if fget.__doc__ is not None:
                            kwargs["doc"] = fget.__doc__
                kwargs["fget"] = fget

            fset = kwargs.pop("fwrite", kwargs.pop("fset", None))
            if fset:
                if inspect.isroutine(fset):
                    self.fset = fset
                kwargs["fset"] = fset

            fisallowed = kwargs.pop("fisallowed", None)
            if fisallowed:
                if inspect.isroutine(fisallowed):
                    self.fisallowed = fisallowed
                kwargs["fisallowed"] = fisallowed

        super().__init__(self.name, class_name)
        self.__doc__ = kwargs.get("doc", kwargs.get("description", "TANGO attribute"))
        if "dtype" in kwargs:
            dtype = kwargs["dtype"]
            dformat = kwargs.get("dformat")
            if is_enum(dtype) or is_enum_seq(dtype):
                enum_labels = kwargs.get("enum_labels")
                if enum_labels:
                    raise TypeError(
                        "For dtype of enum.Enum, (enum.Enum,) or ((enum.Enum,),) the enum_labels must not "
                        f"be specified - dtype: {dtype}, enum_labels: {enum_labels}."
                    )
                _dtype = dtype
                dtype = CmdArgType.DevEnum

                while is_enum_seq(_dtype):
                    _dtype = _dtype[0]
                    dtype = (dtype,)

                kwargs["enum_labels"] = get_enum_labels(_dtype)

            elif is_devstate(dtype) or is_devstate_seq(dtype):
                _dtype = dtype
                dtype = CmdArgType.DevState

                while is_devstate_seq(_dtype):
                    _dtype = _dtype[0]
                    dtype = (dtype,)

            kwargs["dtype"], kwargs["dformat"] = _get_tango_type_format(
                dtype, dformat, caller="attribute"
            )
        self.build_from_dict(kwargs)

    def get_attribute(self, obj):
        return obj.get_device_attr().get_attr_by_name(self.attr_name)

    # --------------------
    # descriptor interface
    # --------------------

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return self.get_attribute(obj)

    def __set__(self, obj, value):
        attr = self.get_attribute(obj)
        set_complex_value(attr, value)

    def __delete__(self, obj):
        obj.remove_attribute(self.attr_name)

    def setter(self, fset):
        """
        To be used as a decorator, ``@attribute.setter``. Defines the decorated method
        as the write attribute method to be called when a client writes
        the attribute. Equivalent to ``@attribute.write``.
        """
        self.fset = fset
        if self.attr_write == AttrWriteType.READ:
            if getattr(self, "fget", None):
                self.attr_write = AttrWriteType.READ_WRITE
            else:
                self.attr_write = AttrWriteType.WRITE
        return self

    def write(self, fset):
        """
        To be used as a decorator, ``@attribute.write``. Defines the decorated method
        as the write attribute method to be called when a client writes
        the attribute. Equivalent to ``@attribute.setter``.
        """
        return self.setter(fset)

    def getter(self, fget):
        """
        To be used as a decorator, ``@attribute.getter``. Defines the decorated method
        as the read attribute method to be called when a client reads
        the attribute. Equivalent to ``@attribute.read``.
        """
        self.fget = fget
        if self.attr_write == AttrWriteType.WRITE:
            if getattr(self, "fset", None):
                self.attr_write = AttrWriteType.READ_WRITE
            else:
                self.attr_write = AttrWriteType.READ
        return self

    def read(self, fget):
        """
        To be used as a decorator, ``@attribute.read``. Defines the decorated method
        as the read attribute method to be called when a client reads
        the attribute. Equivalent to ``@attribute.getter``.
        """
        return self.getter(fget)

    def is_allowed(self, fisallowed):
        """
        To be used as a decorator, ``@attribute.is_allowed``. Defines the decorated
        method as the is allowed attribute method
        """
        self.fisallowed = fisallowed
        return self

    def __call__(self, fget):
        return type(self)(fget=fget, **self._kwargs)


class pipe(PipeData):
    '''
    Declares a new tango pipe in a :class:`Device`. To be used
    like the python native :obj:`property` function.

    Checkout the :ref:`pipe data types <pytango-pipe-data-types>`
    to see what you should return on a pipe read request and what
    to expect as argument on a pipe write request.

    For example, to declare a read-only pipe called *ROI*
    (for Region Of Interest), in a *Detector* :class:`Device` do::

        class Detector(Device):

            ROI = pipe()

            def read_ROI(self):
                return ('ROI', ({'name': 'x', 'value': 0},
                                {'name': 'y', 'value': 10},
                                {'name': 'width', 'value': 100},
                                {'name': 'height', 'value': 200}))

    The same can be achieved with (also showing that a dict can be used
    to pass blob data)::

        class Detector(Device):

            @pipe
            def ROI(self):
                return 'ROI', dict(x=0, y=10, width=100, height=200)


    It receives multiple keyword arguments.

    ===================== ================================ ======================================= =======================================================================================
    parameter              type                                       default value                                 description
    ===================== ================================ ======================================= =======================================================================================
    name                   :obj:`str`                       class member name                       alternative pipe name
    display_level          :obj:`~tango.DispLevel`          :obj:`~tango.DisLevel.OPERATOR`         display level
    access                 :obj:`~tango.PipeWriteType`      :obj:`~tango.PipeWriteType.READ`        read only/ read write access
    fget (or fread)        :obj:`str` or :obj:`callable`    'read_<pipe_name>'                      read method name or method object
    fset (or fwrite)       :obj:`str` or :obj:`callable`    'write_<pipe_name>'                     write method name or method object
    fisallowed             :obj:`str` or :obj:`callable`    'is_<pipe_name>_allowed'                is allowed method name or method object
    label                  :obj:`str`                       '<pipe_name>'                           pipe label
    doc (or description)   :obj:`str`                       ''                                      pipe description
    green_mode             :obj:`bool`                      True                                    Default green mode for read/write/isallowed functions. If True: run with green mode executor, if False: run directly
    read_green_mode        :obj:`bool`                      'green_mode' value                      green mode for read function. If True: run with green mode executor, if False: run directly
    write_green_mode       :obj:`bool`                      'green_mode' value                      green mode for write function. If True: run with green mode executor, if False: run directly
    isallowed_green_mode   :obj:`bool`                      'green_mode' value                      green mode for is allowed function. If True: run with green mode executor, if False: run directly
    ===================== ================================ ======================================= =======================================================================================

    The same example with a read-write ROI, a customized label and description::

        class Detector(Device):

            ROI = pipe(label='Region Of Interest', doc='The active region of interest',
                       access=PipeWriteType.PIPE_READ_WRITE)

            def init_device(self):
                Device.init_device(self)
                self.__roi = 'ROI', dict(x=0, y=10, width=100, height=200)

            def read_ROI(self):
                return self.__roi

            def write_ROI(self, roi):
                self.__roi = roi


    The same, but using pipe as a decorator::

        class Detector(Device):

            def init_device(self):
                Device.init_device(self)
                self.__roi = 'ROI', dict(x=0, y=10, width=100, height=200)

            @pipe(label="Region Of Interest")
            def ROI(self):
                """The active region of interest"""
                return self.__roi

            @ROI.write
            def ROI(self, roi):
                self.__roi = roi

    In this second format, defining the `write` / `setter` implicitly sets
    the pipe access to READ_WRITE.

    .. versionadded:: 9.2.0

    .. versionadded:: 9.4.0
        added isallowed_green_mode option
    '''

    def __init__(self, fget=None, **kwargs):
        self._kwargs = dict(kwargs)
        name = kwargs.pop("name", None)
        class_name = kwargs.pop("class_name", None)
        green_mode = kwargs.pop("green_mode", True)
        self.read_green_mode = kwargs.pop("read_green_mode", green_mode)
        self.write_green_mode = kwargs.pop("write_green_mode", green_mode)
        self.isallowed_green_mode = kwargs.pop("isallowed_green_mode", green_mode)

        if not fget:
            fget = kwargs.pop("fread", None)

        if fget:
            if inspect.isroutine(fget):
                self.fget = fget
                if "doc" not in kwargs and "description" not in kwargs:
                    if fget.__doc__ is not None:
                        kwargs["doc"] = fget.__doc__
            kwargs["fget"] = fget

        fset = kwargs.pop("fwrite", kwargs.pop("fset", None))
        if fset:
            if inspect.isroutine(fset):
                self.fset = fset
            kwargs["fset"] = fset

        fisallowed = kwargs.pop("fisallowed", None)
        if fisallowed:
            if inspect.isroutine(fisallowed):
                self.fisallowed = fisallowed
            kwargs["fisallowed"] = fisallowed

        super().__init__(name, class_name)
        self.__doc__ = kwargs.get("doc", kwargs.get("description", "TANGO pipe"))
        self.build_from_dict(kwargs)

    def get_pipe(self, obj):
        dclass = obj.get_device_class()
        return dclass.get_pipe_by_name(self.pipe_name)

    # --------------------
    # descriptor interface
    # --------------------

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return self.get_attribute(obj)

    def __set__(self, obj, value):
        attr = self.get_attribute(obj)
        set_complex_value(attr, value)

    def setter(self, fset):
        """
        To be used as a decorator. Will define the decorated method
        as a write pipe method to be called when client writes to the pipe
        """
        self.fset = fset
        self.pipe_write = PipeWriteType.PIPE_READ_WRITE
        return self

    def write(self, fset):
        """
        To be used as a decorator. Will define the decorated method
        as a write pipe method to be called when client writes to the pipe
        """
        return self.setter(fset)

    def __call__(self, fget):
        return type(self)(fget=fget, **self._kwargs)


def __build_command_doc(f, name, dtype_in, doc_in, dtype_out, doc_out):
    doc = f"'{name}' TANGO command"
    if dtype_in is not None:
        arg_spec = getfullargspec(f)
        if len(arg_spec.args) > 1:
            # arg[0] should be self and arg[1] the command argument
            param_name = arg_spec.args[1]
        else:
            param_name = "arg"
        dtype_in_str = str(dtype_in)
        if not isinstance(dtype_in, str):
            try:
                dtype_in_str = dtype_in.__name__
            except Exception:
                pass
        msg = doc_in or "(not documented)"
        doc += f"\n\n:param {param_name}: {msg}\n:type {param_name}: {dtype_in_str}"
    if dtype_out is not None:
        dtype_out_str = str(dtype_out)
        if not isinstance(dtype_out, str):
            try:
                dtype_out_str = dtype_out.__name__
            except Exception:
                pass
        msg = doc_out or "(not documented)"
        doc += f"\n\n:return: {msg}\n:rtype: {dtype_out_str}"
    return doc


def command(
    f=None,
    dtype_in=None,
    dformat_in=None,
    doc_in="",
    dtype_out=None,
    dformat_out=None,
    doc_out="",
    display_level=None,
    polling_period=None,
    green_mode=None,
    fisallowed=None,
):
    """
    Declares a new tango command in a :class:`Device`.
    To be used like a decorator in the methods you want to declare as
    tango commands. The following example declares commands:

        * `void TurnOn(void)`
        * `void Ramp(DevDouble current)`
        * `DevBool Pressurize(DevDouble pressure)`

    ::

        class PowerSupply(Device):

            @command
            def TurnOn(self):
                self.info_stream('Turning on the power supply')

            @command(dtype_in=float)
            def Ramp(self, current):
                self.info_stream('Ramping on %f...' % current)

            @command(dtype_in=float, doc_in='the pressure to be set',
                     dtype_out=bool, doc_out='True if it worked, False otherwise')
            def Pressurize(self, pressure):
                self.info_stream('Pressurizing to %f...' % pressure)
                return True

    .. note::
        avoid using *dformat* parameter. If you need a SPECTRUM
        attribute of say, boolean type, use instead ``dtype=(bool,)``.

    :param dtype_in:
        a :ref:`data type <pytango-hlapi-datatypes>` describing the
        type of parameter. Default is None meaning no parameter.
    :param dformat_in: parameter data format. Default is None.
    :type dformat_in: AttrDataFormat
    :param doc_in: parameter documentation
    :type doc_in: str

    :param dtype_out:
        a :ref:`data type <pytango-hlapi-datatypes>` describing the
        type of return value. Default is None meaning no return value.
    :param dformat_out: return value data format. Default is None.
    :type dformat_out: AttrDataFormat
    :param doc_out: return value documentation
    :type doc_out: str
    :param display_level: display level for the command (optional)
    :type display_level: DispLevel
    :param polling_period: polling period in milliseconds (optional)
    :type polling_period: int
    :param green_mode:
        set green mode on this specific command. Default value is None meaning
        use the server green mode. Set it to GreenMode.Synchronous to force
        a non green command in a green server.
    :param fisallowed: is allowed method for command
    :type fisallowed: str or callable

    .. versionadded:: 8.1.7
        added green_mode option

    .. versionadded:: 9.2.0
        added display_level and polling_period optional argument

    .. versionadded:: 9.4.0
        added fisallowed option
    """
    if f is None:
        return functools.partial(
            command,
            dtype_in=dtype_in,
            dformat_in=dformat_in,
            doc_in=doc_in,
            dtype_out=dtype_out,
            dformat_out=dformat_out,
            doc_out=doc_out,
            display_level=display_level,
            polling_period=polling_period,
            green_mode=green_mode,
            fisallowed=fisallowed,
        )
    name = f.__name__

    dtype_format_in = _get_tango_type_format(dtype_in, dformat_in)
    dtype_format_out = _get_tango_type_format(dtype_out, dformat_out)

    din = [from_typeformat_to_type(*dtype_format_in), doc_in]
    dout = [from_typeformat_to_type(*dtype_format_out), doc_out]

    config_dict = {}
    if display_level is not None:
        config_dict["Display level"] = display_level
    if polling_period is not None:
        config_dict["Polling period"] = polling_period
    if fisallowed is not None:
        config_dict["Is allowed"] = fisallowed

    if green_mode == GreenMode.Synchronous:
        cmd = f
    else:

        @functools.wraps(f)
        def cmd(self, *args, **kwargs):
            return get_worker().execute(f, self, *args, **kwargs)

    cmd.__tango_command__ = name, [din, dout, config_dict]

    # try to create a minimalistic __doc__
    if cmd.__doc__ is None:
        try:
            cmd.__doc__ = __build_command_doc(
                f, name, dtype_in, doc_in, dtype_out, doc_out
            )
        except Exception:
            cmd.__doc__ = "TANGO command"

    return cmd


class _BaseProperty:
    def __init__(self, dtype, doc="", default_value=None, update_db=False):
        self.name = None
        dtype = from_typeformat_to_type(*_get_tango_type_format(dtype))
        self.dtype = dtype
        self.doc = doc
        self.default_value = default_value
        self.update_db = update_db
        self.__doc__ = doc or "TANGO property"

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return obj._tango_properties.get(self.name)

    def __set__(self, obj, value):
        obj._tango_properties[self.name] = value
        if self.update_db:
            import tango

            db = tango.Util.instance().get_database()
            db.put_device_property(obj.get_name(), {self.name: value})

    def __delete__(self, obj):
        del obj._tango_properties[self.name]


class device_property(_BaseProperty):
    """
    Declares a new tango device property in a :class:`Device`. To be
    used like the python native :obj:`property` function. For example,
    to declare a scalar, `tango.DevString`, device property called
    *host* in a *PowerSupply* :class:`Device` do::

        from tango.server import Device, DeviceMeta
        from tango.server import device_property

        class PowerSupply(Device):

            host = device_property(dtype=str)
            port = device_property(dtype=int, mandatory=True)

    :param dtype: Data type (see :ref:`pytango-data-types`)
    :param doc: property documentation (optional)
    :param mandatory (optional: default is False)
    :param default_value: default value for the property (optional)
    :param update_db: tells if set value should write the value to database.
                     [default: False]
    :type update_db: bool

    .. versionadded:: 8.1.7
        added update_db option
    """

    def __init__(
        self, dtype, doc="", mandatory=False, default_value=None, update_db=False
    ):
        super().__init__(dtype, doc, default_value, update_db)
        self.mandatory = mandatory
        if mandatory and default_value is not None:
            msg = (
                "Invalid arguments: 'mandatory' is True, so 'default_value' must be None. "
                "A mandatory device property value must be defined in the Tango Database "
                "so it cannot have a default."
            )
            raise ValueError(msg)


class class_property(_BaseProperty):
    """
    Declares a new tango class property in a :class:`Device`. To be
    used like the python native :obj:`property` function. For example,
    to declare a scalar, `tango.DevString`, class property called
    *port* in a *PowerSupply* :class:`Device` do::

        from tango.server import Device, DeviceMeta
        from tango.server import class_property

        class PowerSupply(Device):

            port = class_property(dtype=int, default_value=9788)

    :param dtype: Data type (see :ref:`pytango-data-types`)
    :param doc: property documentation (optional)
    :param default_value: default value for the property (optional)
    :param update_db: tells if set value should write the value to database.
                     [default: False]
    :type update_db: bool

    .. versionadded:: 8.1.7
        added update_db option
    """

    pass


def __to_cb(post_init_callback):
    if post_init_callback is None:
        return lambda: None

    err_msg = (
        "post_init_callback must be a callable or "
        "sequence <callable [, args, [, kwargs]]>"
    )
    if callable(post_init_callback):
        f = post_init_callback
    elif is_non_str_seq(post_init_callback):
        length = len(post_init_callback)
        if length < 1 or length > 3:
            raise TypeError(err_msg)
        cb = post_init_callback[0]
        if not callable(cb):
            raise TypeError(err_msg)
        args, kwargs = [], {}
        if length > 1:
            args = post_init_callback[1]
        if length > 2:
            kwargs = post_init_callback[2]
        f = functools.partial(cb, *args, **kwargs)
    else:
        raise TypeError(err_msg)

    return f


def _to_classes(classes):
    uclasses = []
    if is_seq(classes):
        for klass_info in classes:
            if is_seq(klass_info):
                if len(klass_info) == 2:
                    klass_klass, klass = klass_info
                    klass_name = klass.__name__
                else:
                    klass_klass, klass, klass_name = klass_info
            else:
                if not hasattr(klass_info, "_api") or klass_info._api < 2:
                    raise Exception(
                        "When giving a single class, it must "
                        "implement HLAPI (see tango.server)"
                    )
                klass_klass = klass_info.TangoClassClass
                klass_name = klass_info.TangoClassName
                klass = klass_info
            uclasses.append((klass_klass, klass, klass_name))
    else:
        for klass_name, klass_info in classes.items():
            if is_seq(klass_info):
                if len(klass_info) == 2:
                    klass_klass, klass = klass_info
                else:
                    klass_klass, klass, klass_name = klass_info
            else:
                if not hasattr(klass_info, "_api") or klass_info._api < 2:
                    raise Exception(
                        "When giving a single class, it must "
                        "implement HLAPI (see tango.server)"
                    )
                klass_klass = klass_info.TangoClassClass
                klass_name = klass_info.TangoClassName
                klass = klass_info
            uclasses.append((klass_klass, klass, klass_name))
    return uclasses


def _add_classes(util, classes):
    for class_info in _to_classes(classes):
        util.add_class(*class_info)


def _get_class_green_mode(classes, green_mode):
    if green_mode is not None:
        default_green_mode = green_mode
    else:
        default_green_mode = get_green_mode()

    green_modes = set()
    for _, klass, _ in _to_classes(classes):
        device_green_mode = getattr(klass, "green_mode", None)
        if device_green_mode is None:
            device_green_mode = default_green_mode
        green_modes.add(device_green_mode)
    if len(green_modes) > 1:
        raise ValueError(
            f"Devices with mixed green modes cannot be run in the same device "
            f"server process. Modes: {green_modes}. Classes: {classes}."
        )
    elif len(green_modes) == 0:
        raise ValueError(
            "No device classes specified - cannot run device server "
            "process with no classes."
        )
    unanimous_green_mode = green_modes.pop()
    return unanimous_green_mode


def __server_run(
    classes,
    args=None,
    msg_stream=sys.stdout,
    util=None,
    event_loop=None,
    post_init_callback=None,
    green_mode=None,
):
    green_mode = _get_class_green_mode(classes, green_mode)

    write = msg_stream.write if msg_stream else lambda msg: None

    if args is None:
        args = sys.argv

    post_init_callback = __to_cb(post_init_callback)

    if util is None:
        util = Util.init(args)

    if green_mode in (GreenMode.Gevent, GreenMode.Asyncio):
        util.set_serial_model(SerialModel.NO_SYNC)

    worker = get_executor(green_mode)
    set_worker(worker)

    if event_loop is not None:
        event_loop = functools.partial(worker.execute, event_loop)
        util.server_set_event_loop(event_loop)

    log = logging.getLogger("tango")

    def tango_loop():
        log.debug("server loop started")
        _add_classes(util, classes)
        util.server_init()
        worker.execute(post_init_callback)
        write("Ready to accept request\n")
        util.server_run()
        log.debug("server loop exit")

    worker.run(tango_loop, wait=True)
    return util


def run(
    classes,
    args=None,
    msg_stream=sys.stdout,
    verbose=False,
    util=None,
    event_loop=None,
    post_init_callback=None,
    green_mode=None,
    raises=False,
):
    """
    Provides a simple way to run a tango server. It handles exceptions
    by writting a message to the msg_stream.

    :Examples:

        Example 1: registering and running a PowerSupply inheriting from
        :class:`~tango.server.Device`::

            from tango.server import Device, run

            class PowerSupply(Device):
                pass

            run((PowerSupply,))

        Example 2: registering and running a MyServer defined by tango
        classes `MyServerClass` and `MyServer`::

            from tango import Device_4Impl, DeviceClass
            from tango.server import run

            class MyServer(Device_4Impl):
                pass

            class MyServerClass(DeviceClass):
                pass

            run({'MyServer': (MyServerClass, MyServer)})

        Example 3: registering and running a MyServer defined by tango
        classes `MyServerClass` and `MyServer`::

            from tango import Device_4Impl, DeviceClass
            from tango.server import Device, run

            class PowerSupply(Device):
                pass

            class MyServer(Device_4Impl):
                pass

            class MyServerClass(DeviceClass):
                pass

            run([PowerSupply, [MyServerClass, MyServer]])
            # or: run({'MyServer': (MyServerClass, MyServer)})

    .. note::
       the order of registration of tango classes defines the order
       tango uses to initialize the corresponding devices.
       if using a dictionary as argument for classes be aware that the
       order of registration becomes arbitrary. If you need a
       predefined order use a sequence or an OrderedDict.

    :param classes:
        Defines for which Tango Device Classes the server will run.
        If :class:`~dict` is provided, it's key is the tango class name
        and value is either:

            | :class:`~tango.server.Device`
            | two element sequence: :class:`~tango.DeviceClass`, :class:`~tango.DeviceImpl`
            | three element sequence: :class:`~tango.DeviceClass`, :class:`~tango.DeviceImpl`, tango class name :class:`~str`
    :type classes: Sequence[tango.server.Device] | dict

    :param args:
        list of command line arguments [default: None, meaning use
        sys.argv]
    :type args: list

    :param msg_stream:
        stream where to put messages [default: sys.stdout]

    :param util:
        PyTango Util object [default: None meaning create a Util
        instance]
    :type util: :class:`~tango.Util`

    :param event_loop: event_loop callable
    :type event_loop: callable

    :param post_init_callback:
        an optional callback that is executed between the calls
        Util.server_init and Util.server_run
        The optional `post_init_callback` can be a callable (without
        arguments) or a tuple where the first element is the callable,
        the second is a list of arguments (optional) and the third is a
        dictionary of keyword arguments (also optional).
    :type post_init_callback:
        callable or tuple

    :param raises:
        Disable error handling and propagate exceptions from the server
    :type raises: bool

    :return: The Util singleton object
    :rtype: :class:`~tango.Util`

    .. versionadded:: 8.1.2

    .. versionchanged:: 8.1.4
        when classes argument is a sequence, the items can also be
        a sequence <TangoClass, TangoClassClass>[, tango class name]

    .. versionchanged:: 9.2.2
        `raises` argument has been added
    """
    server_run = functools.partial(
        __server_run,
        classes,
        args=args,
        msg_stream=msg_stream,
        util=util,
        event_loop=event_loop,
        post_init_callback=post_init_callback,
        green_mode=green_mode,
    )
    # Run the server without error handling
    if raises:
        return server_run()
    # Run the server with error handling
    write = msg_stream.write if msg_stream else lambda msg: None
    try:
        return server_run()
    except KeyboardInterrupt:
        write("Exiting: Keyboard interrupt\n")
    except DevFailed as df:
        write("Exiting: Server exited with tango.DevFailed:\n" + str(df) + "\n")
        if verbose:
            write(traceback.format_exc())
    except Exception as e:
        write("Exiting: Server exited with unforseen exception:\n" + str(e) + "\n")
        if verbose:
            write(traceback.format_exc())
    write("\nExited\n")


def server_run(
    classes,
    args=None,
    msg_stream=sys.stdout,
    verbose=False,
    util=None,
    event_loop=None,
    post_init_callback=None,
    green_mode=None,
):
    """
    Since PyTango 8.1.2 it is just an alias to
    :func:`~tango.server.run`. Use :func:`~tango.server.run`
    instead.

    .. versionadded:: 8.0.0

    .. versionchanged:: 8.0.3
        Added `util` keyword parameter.
        Returns util object

    .. versionchanged:: 8.1.1
        Changed default msg_stream from *stderr* to *stdout*
        Added `event_loop` keyword parameter.
        Returns util object

    .. versionchanged:: 8.1.2
        Added `post_init_callback` keyword parameter

    .. deprecated:: 8.1.2
        Use :func:`~tango.server.run` instead.

    """
    return run(
        classes,
        args=args,
        msg_stream=msg_stream,
        verbose=verbose,
        util=util,
        event_loop=event_loop,
        post_init_callback=post_init_callback,
        green_mode=green_mode,
    )


class Device(BaseDevice, metaclass=DeviceMeta):
    """
    Device class for the high-level API.

    All device-specific classes should inherit from this class.
    """


# Avoid circular imports
from .tango_object import Server  # noqa: E402
