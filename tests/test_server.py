import os
import sys
import textwrap
import threading
import time
import pytest
import enum
import numpy as np

from tango import (
    AttrData, Attr, AttrDataFormat, AttrQuality, AttReqType, AttrWriteType,
    DevBoolean, DevLong, DevDouble, DevFailed,
    DevEncoded, DevEnum, DevState, DevVoid,
    Device_4Impl, Device_5Impl, DeviceClass,
    GreenMode, LatestDeviceImpl, ExtractAs,
    READ_WRITE, SCALAR, SPECTRUM, CmdArgType
)
from tango.server import BaseDevice, Device
from tango.pyutil import parse_args
from tango.server import _get_tango_type_format, command, attribute, device_property
from tango.test_utils import DeviceTestContext, MultiDeviceTestContext
from tango.test_utils import GoodEnum, BadEnumNonZero, BadEnumSkipValues, BadEnumDuplicates
from tango.test_utils import assert_close, DEVICE_SERVER_ARGUMENTS
from tango.utils import (
    EnumTypeError,
    FROM_TANGO_TO_NUMPY_TYPE,
    TO_TANGO_TYPE,
    get_enum_labels,
    get_latest_device_class,
    is_pure_str,
)

# Asyncio imports
try:
    import asyncio
except ImportError:
    import trollius as asyncio  # noqa: F401

# Constants
WINDOWS = "nt" in os.name

# Test implementation classes

def test_device_classes_use_latest_implementation():
    assert issubclass(LatestDeviceImpl, get_latest_device_class())
    assert issubclass(BaseDevice, LatestDeviceImpl)
    assert issubclass(Device, BaseDevice)


# Test state/status

def test_empty_device(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.state() == DevState.UNKNOWN
        assert proxy.status() == 'The device is in UNKNOWN state.'


def test_set_state(state, server_green_mode):
    status = f'The device is in {state!s} state.'

    class TestDevice(Device):
        green_mode = server_green_mode

        def init_device(self):
            self.set_state(state)

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.state() == state
        assert proxy.status() == status


def test_set_status(server_green_mode):

    status = '\n'.join((
        "This is a multiline status",
        "with special characters such as",
        "Café à la crème"))

    class TestDevice(Device):
        green_mode = server_green_mode

        def init_device(self):
            self.set_state(DevState.ON)
            self.set_status(status)

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.state() == DevState.ON
        assert proxy.status() == status


# Test commands

def test_identity_command(command_typed_values, server_green_mode):
    dtype, values, expected = command_typed_values

    if dtype == (bool,):
        pytest.xfail('Not supported for some reasons')

    class TestDevice(Device):
        green_mode = server_green_mode

        @command(dtype_in=dtype, dtype_out=dtype)
        def identity(self, arg):
            return arg

    with DeviceTestContext(TestDevice) as proxy:
        for value in values:
            assert_close(proxy.identity(value), expected(value))


def test_command_isallowed(server_green_mode):

    is_allowed = None

    def sync_allowed():
        return is_allowed

    async def async_allowed():
        return is_allowed

    class IsAllowedCallableClass:

        def __init__(self):
            self._is_allowed = None

        def __call__(self, device):
            return self._is_allowed

        def make_allowed(self, yesno):
            self._is_allowed = yesno

    is_allowed_callable_class = IsAllowedCallableClass()

    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super(TestDevice, self).__init__(*args, **kwargs)
            self._is_allowed = True

        @command(dtype_in=int, dtype_out=int)
        def identity(self, arg):
            return arg

        @command(dtype_in=int, dtype_out=int, fisallowed="is_identity_allowed")
        def identity_kwarg_string(self, arg):
            return arg

        @command(dtype_in=int, dtype_out=int,
                 fisallowed=sync_allowed if server_green_mode != GreenMode.Asyncio else async_allowed)
        def identity_kwarg_callable(self, arg):
            return arg

        @command(dtype_in=int, dtype_out=int,
                 fisallowed=is_allowed_callable_class)
        def identity_kwarg_callable_class(self, arg):
            return arg

        @command(dtype_in=int, dtype_out=int)
        def identity_always_allowed(self, arg):
            return arg

        @command(dtype_in=bool)
        def make_allowed(self, yesno):
            self._is_allowed = yesno

        synchronous_code = textwrap.dedent("""\
            def is_identity_allowed(self):
                return self._is_allowed
            """)

        asynchronous_code = synchronous_code.replace("def ", "async def ")

        if server_green_mode != GreenMode.Asyncio:
            exec(synchronous_code)
        else:
            exec(asynchronous_code)

    with DeviceTestContext(TestDevice) as proxy:

        proxy.make_allowed(True)
        is_allowed_callable_class.make_allowed(True)
        is_allowed = True

        assert_close(proxy.identity(1), 1)
        assert_close(proxy.identity_kwarg_string(1), 1)
        assert_close(proxy.identity_kwarg_callable(1), 1)
        assert_close(proxy.identity_kwarg_callable_class(1), 1)
        assert_close(proxy.identity_always_allowed(1), 1)

        proxy.make_allowed(False)
        is_allowed_callable_class.make_allowed(False)
        is_allowed = False

        with pytest.raises(DevFailed):
            proxy.identity(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_string(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_callable(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_callable_class(1)

        assert_close(proxy.identity_always_allowed(1), 1)


@pytest.fixture(params=[True, False])
def device_command_level(request):
    return request.param


def test_dynamic_command(server_green_mode, device_command_level):

    is_allowed = None

    def sync_allowed():
        return is_allowed

    async def async_allowed():
        return is_allowed

    class IsAllowedCallable:

        def __init__(self):
            self._is_allowed = None

        def __call__(self, device):
            return self._is_allowed

        def make_allowed(self, yesno):
            self._is_allowed = yesno

    is_allowed_callable_class = IsAllowedCallable()

    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super(TestDevice, self).__init__(*args, **kwargs)
            self._is_allowed = True

        def identity(self, arg):
            return arg

        def identity_kwarg_string(self, arg):
            return arg

        def identity_kwarg_callable(self, arg):
            return arg

        def identity_kwarg_callable_outside_class(self, arg):
            return arg

        def identity_kwarg_callable_class(self, arg):
            return arg

        def identity_always_allowed(self, arg):
            return arg

        @command()
        def add_dyn_cmd(self):
            cmd = command(f=self.identity, dtype_in=int, dtype_out=int)
            self.add_command(cmd, device_command_level)

            cmd = command(f=self.identity_kwarg_string, dtype_in=int, dtype_out=int,
                          fisallowed="is_identity_allowed")
            self.add_command(cmd, device_command_level)

            cmd = command(f=self.identity_kwarg_callable, dtype_in=int, dtype_out=int,
                          fisallowed=self.is_identity_allowed)
            self.add_command(cmd, device_command_level)

            cmd = command(f=self.identity_kwarg_callable_outside_class, dtype_in=int, dtype_out=int,
                          fisallowed=sync_allowed if server_green_mode != GreenMode.Asyncio else async_allowed)
            self.add_command(cmd, device_command_level)

            cmd = command(f=self.identity_kwarg_callable_class, dtype_in=int, dtype_out=int,
                          fisallowed=is_allowed_callable_class)
            self.add_command(cmd, device_command_level)

            cmd = command(f=self.identity_always_allowed, dtype_in=int, dtype_out=int)
            self.add_command(cmd, device_command_level)

        @command(dtype_in=bool)
        def make_allowed(self, yesno):
            self._is_allowed = yesno

        synchronous_code = textwrap.dedent("""\
                def is_identity_allowed(self):
                    return self._is_allowed
                """)

        asynchronous_code = synchronous_code.replace("def ", "async def ")

        if server_green_mode != GreenMode.Asyncio:
            exec(synchronous_code)
        else:
            exec(asynchronous_code)

    with DeviceTestContext(TestDevice) as proxy:
        proxy.add_dyn_cmd()

        proxy.make_allowed(True)
        is_allowed_callable_class.make_allowed(True)
        is_allowed = True

        assert_close(proxy.identity(1), 1)
        assert_close(proxy.identity_kwarg_string(1), 1)
        assert_close(proxy.identity_kwarg_callable(1), 1)
        assert_close(proxy.identity_kwarg_callable_outside_class(1), 1)
        assert_close(proxy.identity_kwarg_callable_class(1), 1)
        assert_close(proxy.identity_always_allowed(1), 1)

        proxy.make_allowed(False)
        is_allowed_callable_class.make_allowed(False)
        is_allowed = False

        with pytest.raises(DevFailed):
            proxy.identity(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_string(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_callable(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_callable_outside_class(1)

        with pytest.raises(DevFailed):
            proxy.identity_kwarg_callable_class(1)

        assert_close(proxy.identity_always_allowed(1), 1)


def test_polled_command(server_green_mode):

    dct = {'Polling1': 100,
           'Polling2': 100000,
           'Polling3': 500}

    class TestDevice(Device):
        green_mode = server_green_mode

        @command(polling_period=dct["Polling1"])
        def Polling1(self):
            pass

        @command(polling_period=dct["Polling2"])
        def Polling2(self):
            pass

        @command(polling_period=dct["Polling3"])
        def Polling3(self):
            pass

    with DeviceTestContext(TestDevice) as proxy:
        ans = proxy.polling_status()

    for info in ans:
        lines = info.split('\n')
        comm = lines[0].split('= ')[1]
        period = int(lines[1].split('= ')[1])
        assert dct[comm] == period


def test_wrong_command_result(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode

        @command(dtype_out=str)
        def cmd_str_err(self):
            return 1.2345

        @command(dtype_out=int)
        def cmd_int_err(self):
            return "bla"

        @command(dtype_out=[str])
        def cmd_str_list_err(self):
            return ['hello', 55]

    with DeviceTestContext(TestDevice) as proxy:
        with pytest.raises(DevFailed):
            proxy.cmd_str_err()
        with pytest.raises(DevFailed):
            proxy.cmd_int_err()
        with pytest.raises(DevFailed):
            proxy.cmd_str_list_err()


# Test attributes
def test_read_write_attribute(attribute_typed_values, server_green_mode):
    dtype, values, expected = attribute_typed_values

    class TestDevice(Device):
        green_mode = server_green_mode
        _is_allowed = None

        @attribute(dtype=dtype, max_dim_x=10, max_dim_y=10,
                   access=AttrWriteType.READ_WRITE)
        def attr(self):
            return self.attr_value

        @attr.write
        def attr(self, value):
            self.attr_value = value

        def is_attr_allowed(self, req_type):
            assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
            return self._is_allowed

        @command(dtype_in=bool)
        def make_allowed(self, yesno):
            self._is_allowed = yesno

    with DeviceTestContext(TestDevice, timeout=60000) as proxy:
        proxy.make_allowed(True)
        for value in values:
            proxy.attr = value
            assert_close(proxy.attr, expected(value))

        proxy.make_allowed(False)
        with pytest.raises(DevFailed):
            proxy.attr = value
        with pytest.raises(DevFailed):
            _ = proxy.attr


def test_read_write_attribute_unbound_methods(server_green_mode):

    class Value():
        _value = None

        def set(self, val):
            self._value = val

        def get(self):
            return self._value

    v = Value()
    is_allowed = None

    if server_green_mode == GreenMode.Asyncio:
        async def read_attr():
            return v.get()

        async def write_attr(val):
            v.set(val)

        async def is_attr_allowed(req_type):
            assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
            return is_allowed
    else:
        def read_attr():
            return v.get()

        def write_attr(val):
            v.set(val)

        def is_attr_allowed(req_type):
            assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
            return is_allowed

    class TestDevice(Device):
        green_mode = server_green_mode

        attr = attribute(fget=read_attr,
                         fset=write_attr,
                         fisallowed=is_attr_allowed,
                         dtype=int,
                         access=AttrWriteType.READ_WRITE)

    with DeviceTestContext(TestDevice) as proxy:
        is_allowed = True
        proxy.attr = 123
        assert proxy.attr == 123

        is_allowed = False
        with pytest.raises(DevFailed):
            proxy.attr = 123
        with pytest.raises(DevFailed):
            _ = proxy.attr


def test_read_write_wvalue_attribute(attribute_typed_values, server_green_mode):
    dtype, values, expected = attribute_typed_values

    if dtype in [((int,),), ((float,),), ((str,),), ((bool,),)]:
        pytest.xfail("At the moment IMAGEs are not supported for set_write_value")

    class TestDevice(Device):
        green_mode = server_green_mode

        @attribute(dtype=dtype, max_dim_x=10, max_dim_y=10, access=AttrWriteType.READ_WRITE)
        def attr(self):
            return self.value

        @attr.write
        def attr(self, value):
            self.value = value
            w_attr = self.get_device_attr().get_w_attr_by_name('attr')
            fmt = w_attr.get_data_format()
            if fmt == AttrDataFormat.SPECTRUM:
                w_attr.set_write_value(value, len(value))
            elif fmt == AttrDataFormat.IMAGE:
                w_attr.set_write_value(value, len(value[0]), len(value))
            else:
                w_attr.set_write_value(value)

    with DeviceTestContext(TestDevice) as proxy:
        for value in values:
            proxy.attr = value
            assert_close(proxy.attr, expected(proxy.read_attribute('attr').w_value))


def test_write_read_empty_spectrum_attribute(extract_as, base_type):
    requested_type, expected_type = extract_as

    if requested_type == ExtractAs.Numpy and base_type == str:
        expected_type = tuple

    if requested_type in [ExtractAs.ByteArray, ExtractAs.Bytes, ExtractAs.String] and base_type == str:
        pytest.xfail('Conversion from (str,) to ByteArray, Bytes and String not supported. May be fixed in future')

    class TestDevice(Device):

        attr_value = []

        @attribute(dtype=(base_type,), max_dim_x=10, access=AttrWriteType.READ_WRITE)
        def attr(self):
            return self.attr_value

        @attr.write
        def attr(self, value):
            self.attr_value = value

        @command(dtype_out=bool)
        def is_attr_empty_list(self):
            if base_type in [int, float, bool]:
                expected_numpy_type = FROM_TANGO_TO_NUMPY_TYPE[TO_TANGO_TYPE[base_type]]
                assert self.attr_value.dtype == np.dtype(expected_numpy_type)
            else:
                assert isinstance(self.attr_value, list)
            assert len(self.attr_value) == 0

    with DeviceTestContext(TestDevice) as proxy:
        # first we read init value
        attr_read = proxy.read_attribute('attr', extract_as=requested_type)
        assert isinstance(attr_read.value, expected_type)
        assert len(attr_read.value) == 0
        # then we write empty list and check if it was really written
        proxy.attr = []
        proxy.is_attr_empty_list()
        # and finally, we read it again and check the value and wvalue
        attr_read = proxy.read_attribute('attr', extract_as=requested_type)
        assert isinstance(attr_read.value, expected_type)
        assert len(attr_read.value) == 0
        assert isinstance(attr_read.w_value, expected_type)
        assert len(attr_read.w_value) == 0


@pytest.mark.parametrize("device_impl_class", [Device_4Impl, Device_5Impl, LatestDeviceImpl])
def test_write_read_empty_spectrum_attribute_classic_api(device_impl_class, extract_as, base_type):
    requested_type, expected_type = extract_as

    if requested_type == ExtractAs.Numpy and base_type == str:
        expected_type = tuple

    if requested_type in [ExtractAs.ByteArray, ExtractAs.Bytes, ExtractAs.String] and base_type == str:
        pytest.xfail('Conversion from (str,) to ByteArray, Bytes and String not supported. May be fixed in future')

    class ClassicAPIClass(DeviceClass):

        cmd_list = {"is_attr_empty_list": [[DevVoid, "none"], [DevBoolean, "none"]]}
        attr_list = {"attr": [[TO_TANGO_TYPE[base_type], SPECTRUM, AttrWriteType.READ_WRITE, 10]]}

        def __init__(self, name):
            super().__init__(name)
            self.set_type("TestDevice")

    class ClassicAPIDeviceImpl(device_impl_class):

        attr_value = []

        def read_attr(self, attr):
            attr.set_value(self.attr_value)

        def write_attr(self, attr):
            w_value = attr.get_write_value()
            self.attr_value = w_value

        def is_attr_empty_list(self):
            if base_type in [int, float, bool]:
                expected_numpy_type = FROM_TANGO_TO_NUMPY_TYPE[TO_TANGO_TYPE[base_type]]
                assert self.attr_value.dtype == np.dtype(expected_numpy_type)
            else:
                assert isinstance(self.attr_value, list)
            assert len(self.attr_value) == 0

    with DeviceTestContext(ClassicAPIDeviceImpl, ClassicAPIClass) as proxy:
        # first we read init value
        attr_read = proxy.read_attribute('attr', extract_as=requested_type)
        assert isinstance(attr_read.value, expected_type)
        assert len(attr_read.value) == 0
        # then we write empty list and check if it was really written
        proxy.attr = []
        proxy.is_attr_empty_list()
        # and finally, we read it again and check the value and wvalue
        attr_read = proxy.read_attribute('attr', extract_as=requested_type)
        assert isinstance(attr_read.value, expected_type)
        assert len(attr_read.value) == 0
        assert isinstance(attr_read.w_value, expected_type)
        assert len(attr_read.w_value) == 0


@pytest.mark.parametrize("dtype", ["state", DevState, CmdArgType.DevState])
def test_ensure_devstate_is_pytango_enum(attr_data_format, dtype):

    if attr_data_format == AttrDataFormat.SCALAR:
        value = DevState.ON
    elif attr_data_format == AttrDataFormat.SPECTRUM:
        dtype = (dtype,)
        value = (DevState.ON, DevState.RUNNING)
    else:
        dtype = ((dtype,),)
        value = ((DevState.ON, DevState.RUNNING), (DevState.UNKNOWN, DevState.MOVING))

    class TestDevice(Device):
        @attribute(dtype=dtype, access=AttrWriteType.READ, max_dim_x=2, max_dim_y=2)
        def any_name_for_state_attribute(self):
            return value

    def check_attr_type(states):
        if attr_data_format == AttrDataFormat.SCALAR:
            assert isinstance(states, DevState)
        elif attr_data_format == AttrDataFormat.SPECTRUM:
            for state in states:
                assert isinstance(state, DevState)
        else:
            for state in states:
                for stat in state:
                    assert isinstance(stat, DevState)

    with DeviceTestContext(TestDevice) as proxy:
        states = proxy.any_name_for_state_attribute
        assert states == value
        check_attr_type(states)


def test_read_write_attribute_enum(server_green_mode, attr_data_format):
    values = (member.value for member in GoodEnum)
    enum_labels = get_enum_labels(GoodEnum)

    if attr_data_format == AttrDataFormat.SCALAR:
        good_type = GoodEnum
        good_type_str = 'DevEnum'
    elif attr_data_format == AttrDataFormat.SPECTRUM:
        good_type = (GoodEnum,)
        good_type_str = ('DevEnum',)
    else:
        good_type = ((GoodEnum,),)
        good_type_str = (('DevEnum',),)

    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if attr_data_format == AttrDataFormat.SCALAR:
                self.attr_from_enum_value = 0
                self.attr_from_labels_value = 0
            elif attr_data_format == AttrDataFormat.SPECTRUM:
                self.attr_from_enum_value = (0,)
                self.attr_from_labels_value = (0,)
            else:
                self.attr_from_enum_value = ((0,),)
                self.attr_from_labels_value = ((0,),)

        @attribute(dtype=good_type, max_dim_x=10, max_dim_y=10, access=AttrWriteType.READ_WRITE)
        def attr_from_enum(self):
            return self.attr_from_enum_value

        @attr_from_enum.write
        def attr_from_enum(self, value):
            self.attr_from_enum_value = value

        @attribute(dtype=good_type_str, max_dim_x=10, max_dim_y=10,
                   enum_labels=enum_labels, access=AttrWriteType.READ_WRITE)
        def attr_from_labels(self):
            return self.attr_from_labels_value

        @attr_from_labels.write
        def attr_from_labels(self, value):
            self.attr_from_labels_value = value

    def make_nd_value(value):
        if attr_data_format == AttrDataFormat.SCALAR:
           return value
        elif attr_data_format == AttrDataFormat.SPECTRUM:
            return (value,)
        else:
            return ((value,),)

    def check_attr_type(read_attr):
        if attr_data_format == AttrDataFormat.SCALAR:
            assert isinstance(read_attr, enum.IntEnum)
        elif attr_data_format == AttrDataFormat.SPECTRUM:
            for val in read_attr:
                assert isinstance(val, enum.IntEnum)
        else:
            for val in read_attr:
                for v in val:
                    assert isinstance(v, enum.IntEnum)

    def check_read_attr(read_attr, value, label):
        if attr_data_format == AttrDataFormat.SCALAR:
            assert_value_label(read_attr, value, label)
        elif attr_data_format == AttrDataFormat.SPECTRUM:
            for val in read_attr:
                assert_value_label(val, value, label)
        else:
            for val in read_attr:
                for v in val:
                    assert_value_label(v, value, label)

    def assert_value_label(read_attr, value, label):
        assert read_attr.value == value
        assert read_attr.name == label

    with DeviceTestContext(TestDevice) as proxy:
        for value, label in zip(values, enum_labels):
            nd_value = make_nd_value(value)
            proxy.attr_from_enum = nd_value
            read_attr = proxy.attr_from_enum
            assert read_attr == nd_value
            check_attr_type(read_attr)
            check_read_attr(read_attr, value, label)

            proxy.attr_from_labels = nd_value
            read_attr = proxy.attr_from_labels
            assert read_attr == nd_value
            check_attr_type(read_attr)
            check_read_attr(read_attr, value, label)

        for value, label in zip(values, enum_labels):
            nd_label = make_nd_value(label)
            proxy.attr_from_enum = nd_label
            read_attr = proxy.attr_from_enum
            assert read_attr == nd_label
            check_attr_type(read_attr)
            check_read_attr(read_attr, value, label)

            proxy.attr_from_labels = nd_label
            read_attr = proxy.attr_from_labels
            assert read_attr == nd_label
            check_attr_type(read_attr)
            check_read_attr(read_attr, value, label)

    with pytest.raises(TypeError) as context:
        class BadTestDevice(Device):
            green_mode = server_green_mode

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if attr_data_format == AttrDataFormat.SCALAR:
                    self.attr_value = 0
                elif attr_data_format == AttrDataFormat.SPECTRUM:
                    self.attr_value = (0,)
                else:
                    self.attr_value = ((0,),)

            # enum_labels may not be specified if dtype is an enum.Enum
            @attribute(dtype=good_type, max_dim_x=10, max_dim_y=10, enum_labels=enum_labels)
            def bad_attr(self):
                return self.attr_value

        BadTestDevice()  # dummy instance for Codacy
    assert 'enum_labels' in str(context.value)


def test_read_attribute_with_invalid_quality_is_none(attribute_typed_values):
    dtype, values, expected = attribute_typed_values

    class TestDevice(Device):
        @attribute(dtype=dtype, max_dim_x=10, max_dim_y=10)
        def attr(self):
            dummy_time = 123.4
            return values[0], dummy_time, AttrQuality.ATTR_INVALID

    with DeviceTestContext(TestDevice) as proxy:
        reading = proxy.read_attribute("attr")
        assert reading.value is None
        assert reading.quality is AttrQuality.ATTR_INVALID
        high_level_value = proxy.attr
        assert high_level_value is None


def test_read_enum_attribute_with_invalid_quality_is_none():

    class TestDevice(Device):
        @attribute(dtype=GoodEnum)
        def attr(self):
            dummy_time = 123.4
            return GoodEnum.START, dummy_time, AttrQuality.ATTR_INVALID

    with DeviceTestContext(TestDevice) as proxy:
        reading = proxy.read_attribute("attr")
        assert reading.value is None
        assert reading.quality is AttrQuality.ATTR_INVALID
        high_level_value = proxy.attr
        assert high_level_value is None


def test_wrong_attribute_read(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode

        @attribute(dtype=str)
        def attr_str_err(self):
            return 1.2345

        @attribute(dtype=int)
        def attr_int_err(self):
            return "bla"

        @attribute(dtype=[str])
        def attr_str_list_err(self):
            return ['hello', 55]

    with DeviceTestContext(TestDevice) as proxy:
        with pytest.raises(DevFailed):
            proxy.attr_str_err
        with pytest.raises(DevFailed):
            proxy.attr_int_err
        with pytest.raises(DevFailed):
            proxy.attr_str_list_err


def test_attribute_access_with_default_method_names(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode
        _read_write_value = ""
        _is_allowed = True

        attr_r = attribute(dtype=str)
        attr_rw = attribute(dtype=str, access=AttrWriteType.READ_WRITE)

        # the following methods are written in plain text which looks
        # weird. This is done so that it is easy to change for async
        # tests without duplicating all the code.
        synchronous_code = textwrap.dedent("""\
            def read_attr_r(self):
                return "readable"

            def read_attr_rw(self):
                print(f'Return value {self._read_write_value}')
                return self._read_write_value
    
            def write_attr_rw(self, value):
                print(f'Get value {value}')
                self._read_write_value = value
    
            def is_attr_r_allowed(self, req_type):
                assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
                return self._is_allowed
    
            def is_attr_rw_allowed(self, req_type):
                assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
                return self._is_allowed
    
            """)

        @command(dtype_in=bool)
        def make_allowed(self, yesno):
            self._is_allowed = yesno

        asynchronous_code = synchronous_code.replace("def ", "async def ")

        if server_green_mode != GreenMode.Asyncio:
            exec(synchronous_code)
        else:
            exec(asynchronous_code)

    with DeviceTestContext(TestDevice) as proxy:
        proxy.make_allowed(True)
        with pytest.raises(DevFailed):
            proxy.attr_r = "writable"
        assert proxy.attr_r == "readable"
        proxy.attr_rw = "writable"
        assert proxy.attr_rw == "writable"

        proxy.make_allowed(False)
        with pytest.raises(DevFailed):
            _ = proxy.attr_r
        with pytest.raises(DevFailed):
            proxy.attr_rw = "writing_not_allowed"
        with pytest.raises(DevFailed):
            _ = proxy.attr_rw


@pytest.fixture(ids=["low_level_read",
                     "high_level_read_with_attr",
                     "high_level_read_no_attr"],
                params=[textwrap.dedent("""\
                        def read_dyn_attr(self, attr):
                            attr.set_value(self.attr_value)
                            """),
                        textwrap.dedent("""\
                        def read_dyn_attr(self, attr):
                            return self.attr_value
                            """),
                        textwrap.dedent("""\
                        def read_dyn_attr(self):
                            return self.attr_value
                            """),
                        ])
def dynamic_attribute_read_function(request):
    return request.param


@pytest.fixture(ids=["low_level_write",
                     "high_level_write"],
                params=[textwrap.dedent("""\
                        def write_dyn_attr(self, attr):
                            self.attr_value = attr.get_write_value()
                            """),
                        textwrap.dedent("""\
                        def write_dyn_attr(self, attr, value):
                            self.attr_value = value
                            """)
                        ])
def dynamic_attribute_write_function(request):
    return request.param

def test_read_write_dynamic_attribute(dynamic_attribute_read_function, dynamic_attribute_write_function,
                                      server_green_mode):
    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attr_value = None

        @command
        def add_dyn_attr(self):
            attr = attribute(
                name="dyn_attr",
                dtype=int,
                access=AttrWriteType.READ_WRITE,
                fget=self.read_dyn_attr,
                fset=self.write_dyn_attr)
            self.add_attribute(attr)

        @command
        def delete_dyn_attr(self):
            self.remove_attribute("dyn_attr")

        if server_green_mode != GreenMode.Asyncio:
            exec(dynamic_attribute_read_function)
            exec(dynamic_attribute_write_function)
        else:
            exec(dynamic_attribute_read_function.replace("def ", "async def "))
            exec(dynamic_attribute_write_function.replace("def ", "async def "))

    with DeviceTestContext(TestDevice) as proxy:
        proxy.add_dyn_attr()
        proxy.dyn_attr = 123
        assert proxy.dyn_attr == 123
        proxy.delete_dyn_attr()
        assert "dyn_attr" not in proxy.get_attribute_list()


def test_read_write_dynamic_attribute_enum(server_green_mode, attr_data_format):
    values = (member.value for member in GoodEnum)
    enum_labels = get_enum_labels(GoodEnum)

    if attr_data_format == AttrDataFormat.SCALAR:
        attr_type = DevEnum
        attr_info = (DevEnum, attr_data_format, READ_WRITE)
    elif attr_data_format == AttrDataFormat.SPECTRUM:
        attr_type = (DevEnum,)
        attr_info = (DevEnum, attr_data_format, READ_WRITE, 10)
    else:
        attr_type = ((DevEnum,),)
        attr_info = (DevEnum, attr_data_format, READ_WRITE, 10, 10)

    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if attr_data_format == AttrDataFormat.SCALAR:
                self.attr_value = 0
            elif attr_data_format == AttrDataFormat.SPECTRUM:
                self.attr_value = (0,)
            else:
                self.attr_value = ((0,),)

        @command
        def add_dyn_attr_old(self):
            attr = AttrData(
                            "dyn_attr",
                            None,
                            attr_info=[attr_info, {"enum_labels": enum_labels},],
                            )
            self.add_attribute(attr,
                               r_meth=self.read_dyn_attr,
                               w_meth=self.write_dyn_attr)

        @command
        def add_dyn_attr_new(self):
            attr = attribute(
                name="dyn_attr",
                dtype=attr_type,
                max_dim_x=10,
                max_dim_y=10,
                access=AttrWriteType.READ_WRITE,
                fget=self.read_dyn_attr,
                fset=self.write_dyn_attr)
            self.add_attribute(attr)

        @command
        def delete_dyn_attr(self):
            self.remove_attribute("dyn_attr")

        sync_code = textwrap.dedent("""\
            def read_dyn_attr(self):
                return self.attr_value

            def write_dyn_attr(self, attr, value):
                self.attr_value = value
                """)

        if server_green_mode != GreenMode.Asyncio:
            exec(sync_code)
        else:
            exec(sync_code.replace("def ", "async def "))

    def make_nd_value(value):
        if attr_data_format == AttrDataFormat.SCALAR:
            return value
        elif attr_data_format == AttrDataFormat.SPECTRUM:
            return (value,)
        else:
            return ((value,),)

    def check_attr_type(read_attr):
        if attr_data_format == AttrDataFormat.SCALAR:
            assert isinstance(read_attr, enum.IntEnum)
        elif attr_data_format == AttrDataFormat.SPECTRUM:
            for val in read_attr:
                assert isinstance(val, enum.IntEnum)
        else:
            for val in read_attr:
                for v in val:
                    assert isinstance(v, enum.IntEnum)

    def check_read_attr(read_attr, value, label):
        if attr_data_format == AttrDataFormat.SCALAR:
            assert_value_label(read_attr, value, label)
        elif attr_data_format == AttrDataFormat.SPECTRUM:
            for val in read_attr:
                assert_value_label(val, value, label)
        else:
            for val in read_attr:
                for v in val:
                    assert_value_label(v, value, label)

    def assert_value_label(read_attr, value, label):
        assert read_attr.value == value
        assert read_attr.name == label

    with DeviceTestContext(TestDevice) as proxy:
        for add_attr_cmd in [proxy.add_dyn_attr_old, proxy.add_dyn_attr_new]:
            add_attr_cmd()
            for value, label in zip(values, enum_labels):
                nd_value = make_nd_value(value)
                proxy.dyn_attr = nd_value
                read_attr = proxy.dyn_attr
                assert read_attr == nd_value
                check_attr_type(read_attr)
                check_read_attr(read_attr, value, label)
            proxy.delete_dyn_attr()
            assert "dyn_attr" not in proxy.get_attribute_list()


def test_read_write_dynamic_attribute_is_allowed_with_async(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for att_num in range(1, 7):
                setattr(self, f"attr{att_num}_allowed", True)
            for att_num in range(1, 7):
                setattr(self, f"attr{att_num}_value", None)

        def initialize_dynamic_attributes(self):
            # recommended approach: using attribute() and bound methods:
            attr = attribute(
                name="dyn_attr1",
                dtype=int,
                access=AttrWriteType.READ_WRITE,
                fget=self.read_dyn_attr1,
                fset=self.write_dyn_attr1,
                fisallowed=self.is_attr1_allowed,
            )
            self.add_attribute(attr)

            # not recommended: using attribute() with unbound methods:
            attr = attribute(
                name="dyn_attr2",
                dtype=int,
                access=AttrWriteType.READ_WRITE,
                fget=TestDevice.read_dyn_attr2,
                fset=TestDevice.write_dyn_attr2,
                fisallowed=TestDevice.is_attr2_allowed,
            )
            self.add_attribute(attr)

            # possible approach: using attribute() with method name strings:
            attr = attribute(
                name="dyn_attr3",
                dtype=int,
                access=AttrWriteType.READ_WRITE,
                fget="read_dyn_attr3",
                fset="write_dyn_attr3",
                fisallowed="is_attr3_allowed",
            )
            self.add_attribute(attr)

            # old approach: using tango.AttrData with bound methods:
            attr_name = "dyn_attr4"
            data_info = self._get_attr_data_info()
            dev_class = self.get_device_class()
            attr_data = AttrData(attr_name, dev_class.get_name(), data_info)
            self.add_attribute(
                attr_data,
                self.read_dyn_attr4,
                self.write_dyn_attr4,
                self.is_attr4_allowed,
            )

            # old approach: using tango.AttrData with unbound methods:
            attr_name = "dyn_attr5"
            attr_data = AttrData(attr_name, dev_class.get_name(), data_info)
            self.add_attribute(
                attr_data,
                TestDevice.read_dyn_attr5,
                TestDevice.write_dyn_attr5,
                TestDevice.is_attr5_allowed,
            )

            # old approach: using tango.AttrData with default method names
            attr_name = "dyn_attr6"
            attr_data = AttrData(attr_name, dev_class.get_name(), data_info)
            self.add_attribute(attr_data)

        def _get_attr_data_info(self):
            simple_type, fmt = _get_tango_type_format(int)
            data_info = [[simple_type, fmt, READ_WRITE]]
            return data_info

        @command(dtype_in=bool)
        def make_allowed(self, yesno):
            for att_num in range(1, 7):
                setattr(self, f"attr{att_num}_allowed", yesno)

        # the following methods are written in plain text which looks
        # weird. This is done so that it is easy to change for async
        # tests without duplicating all the code.
        read_code = textwrap.dedent("""\
            def read_dyn_attr(self):
                return self.attr_value
                """)

        write_code = textwrap.dedent("""\
            def write_dyn_attr(self, attr, value):
                self.attr_value = value
                """)

        is_allowed_code = textwrap.dedent("""\
            def is_attr_allowed(self, req_type):
                assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
                return self.attr_allowed
            """)

        for attr_num in range(1, 7):
            read_method = read_code.replace("read_dyn_attr", f"read_dyn_attr{attr_num}")
            read_method = read_method.replace("attr_value", f"attr{attr_num}_value")
            write_method = write_code.replace("write_dyn_attr", f"write_dyn_attr{attr_num}")
            write_method = write_method.replace("attr_value", f"attr{attr_num}_value")
            if attr_num < 6:
                is_allowed_method = is_allowed_code.replace("is_attr_allowed", f"is_attr{attr_num}_allowed")
            else:
                # default name differs
                is_allowed_method = is_allowed_code.replace("is_attr_allowed", f"is_dyn_attr{attr_num}_allowed")
            is_allowed_method = is_allowed_method.replace("self.attr_allowed", f"self.attr{attr_num}_allowed")

            if server_green_mode != GreenMode.Asyncio:
                exec(read_method)
                exec(write_method)
                exec(is_allowed_method)
            else:
                exec(read_method.replace("def ", "async def "))
                exec(write_method.replace("def ", "async def "))
                exec(is_allowed_method.replace("def ", "async def "))

    with DeviceTestContext(TestDevice) as proxy:
        proxy.make_allowed(True)
        proxy.dyn_attr1 = 1
        assert proxy.dyn_attr1 == 1

        proxy.dyn_attr2 = 2
        assert proxy.dyn_attr2 == 2

        proxy.dyn_attr3 = 3
        assert proxy.dyn_attr3 == 3

        proxy.dyn_attr4 = 4
        assert proxy.dyn_attr4 == 4

        proxy.dyn_attr5 = 5
        assert proxy.dyn_attr5 == 5

        proxy.dyn_attr6 = 6
        assert proxy.dyn_attr6 == 6

        proxy.make_allowed(False)
        with pytest.raises(DevFailed):
            proxy.dyn_attr1 = 1
        with pytest.raises(DevFailed):
            _ = proxy.dyn_attr1
        with pytest.raises(DevFailed):
            proxy.dyn_attr2 = 2
        with pytest.raises(DevFailed):
            _ = proxy.dyn_attr2
        with pytest.raises(DevFailed):
            proxy.dyn_attr3 = 3
        with pytest.raises(DevFailed):
            _ = proxy.dyn_attr3
        with pytest.raises(DevFailed):
            proxy.dyn_attr4 = 4
        with pytest.raises(DevFailed):
            _ = proxy.dyn_attr4
        with pytest.raises(DevFailed):
            proxy.dyn_attr5 = 5
        with pytest.raises(DevFailed):
            _ = proxy.dyn_attr5
        with pytest.raises(DevFailed):
            proxy.dyn_attr6 = 6
        with pytest.raises(DevFailed):
            _ = proxy.dyn_attr6


@pytest.mark.parametrize("device_impl_class", [Device_4Impl, Device_5Impl, LatestDeviceImpl])
def test_dynamic_attribute_using_classic_api_like_sardana(device_impl_class):

    class ClassicAPIClass(DeviceClass):

        cmd_list = {
            'make_allowed': [[DevBoolean, "allow access"], [DevVoid, "none"]],
        }

        def __init__(self, name):
            super().__init__(name)
            self.set_type("TestDevice")

    class ClassicAPIDeviceImpl(device_impl_class):

        def __init__(self, cl, name):
            super().__init__(cl, name)
            ClassicAPIDeviceImpl.init_device(self)

        def init_device(self):
            self._attr1 = 3.14
            self._is_test_attr_allowed = True
            read = self.__class__._read_attr
            write = self.__class__._write_attr
            is_allowed = self.__class__._is_attr_allowed
            attr_name = "attr1"
            data_info = [[DevDouble, SCALAR, READ_WRITE]]
            dev_class = self.get_device_class()
            attr_data = AttrData(attr_name, dev_class.get_name(), data_info)
            self.add_attribute(attr_data, read, write, is_allowed)

        def _is_attr_allowed(self, req_type):
            assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
            return self._is_test_attr_allowed

        def _read_attr(self, attr):
            attr.set_value(self._attr1)

        def _write_attr(self, attr):
            w_value = attr.get_write_value()
            self._attr1 = w_value

        def make_allowed(self, yesno):
            self._is_test_attr_allowed = yesno

    with DeviceTestContext(ClassicAPIDeviceImpl, ClassicAPIClass) as proxy:
        proxy.make_allowed(True)
        assert proxy.attr1 == 3.14
        proxy.attr1 = 42.0
        assert proxy.attr1 == 42.0

        proxy.make_allowed(False)
        with pytest.raises(DevFailed):
            _ = proxy.attr1
        with pytest.raises(DevFailed):
            proxy.attr1 = 12.0


@pytest.mark.parametrize("read_function_signature", ['low_level', 'high_level_mixed', 'high_level'])
@pytest.mark.parametrize("patched", [True, False])
def test_dynamic_attribute_with_non_device_method(read_function_signature, patched, server_green_mode):

    class Value:
        _value = None

        def set(self, val):
            self._value = val

        def read(self):
            return self._value

    value = Value()
    is_allowed = None

    if server_green_mode == GreenMode.Asyncio:
        async def low_level_read_function(attr):
            attr.set_value(value.read())

        async def high_level_mixed_read_function(attr):
            return value.read()

        async def high_level_read_function():
            return value.read()

        async def low_level_write_function(attr):
            value.set(attr.get_write_value())

        async def high_level_write_function(attr, in_value):
            value.set(in_value)

        async def is_allowed_function(req_type):
            assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
            return is_allowed

    else:
        def low_level_read_function(attr):
            attr.set_value(value.read())

        def high_level_mixed_read_function(attr):
            return value.read()

        def high_level_read_function():
            return value.read()

        def low_level_write_function(attr):
            value.set(attr.get_write_value())

        def high_level_write_function(attr, in_value):
            value.set(in_value)

        def is_allowed_function(req_type):
            assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
            return is_allowed

    class TestDevice(Device):
        green_mode = server_green_mode

        def initialize_dynamic_attributes(self):
            if read_function_signature == "low_level":
                read_function = low_level_read_function
                write_function = low_level_write_function
            elif read_function_signature == "high_level_mixed":
                read_function = high_level_mixed_read_function
                write_function = high_level_write_function
            else:
                read_function = high_level_read_function
                write_function = high_level_write_function

            # trick to run server with non device method: patch __dict__
            if patched:
                self.__dict__['read_dyn_attr1'] = read_function
                self.__dict__['write_dyn_attr1'] = write_function
                self.__dict__['is_dyn_attr1_allowed'] = is_allowed_function
                attr = attribute(name="dyn_attr1", dtype=int, access=AttrWriteType.READ_WRITE)
                self.add_attribute(attr)

                setattr(self, 'read_dyn_attr2', read_function)
                setattr(self, 'write_dyn_attr2', write_function)
                setattr(self, 'is_dyn_attr2_allowed', is_allowed_function)
                attr = attribute(name="dyn_attr2", dtype=int, access=AttrWriteType.READ_WRITE)
                self.add_attribute(attr)

            else:
                attr = attribute(name="dyn_attr",
                                 fget=read_function,
                                 fset=write_function,
                                 fisallowed=is_allowed_function,
                                 dtype=int,
                                 access=AttrWriteType.READ_WRITE)
                self.add_attribute(attr)

    with DeviceTestContext(TestDevice) as proxy:
        is_allowed = True
        if patched:
            proxy.dyn_attr1 = 123
            assert proxy.dyn_attr1 == 123

            proxy.dyn_attr2 = 456
            assert proxy.dyn_attr2 == 456
        else:
            proxy.dyn_attr = 789
            assert proxy.dyn_attr == 789

        is_allowed = False
        if patched:
            with pytest.raises(DevFailed):
                proxy.dyn_attr1 = 123

            with pytest.raises(DevFailed):
                _ = proxy.dyn_attr1

            with pytest.raises(DevFailed):
                proxy.dyn_attr2 = 456

            with pytest.raises(DevFailed):
                _ = proxy.dyn_attr2
        else:
            with pytest.raises(DevFailed):
                proxy.dyn_attr = 123

            with pytest.raises(DevFailed):
                _ = proxy.dyn_attr


def test_attribute_decorators(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode
        current_value = None
        voltage_value = None
        is_allowed = None

        current = attribute(label="Current", unit="mA", dtype=float)
        voltage = attribute(label="Voltage", unit="V", dtype=float)

        sync_code = textwrap.dedent("""
        @current.getter
        def cur_read(self):
            return self.current_value

        @current.setter
        def cur_write(self, current):
            self.current_value = current

        @current.is_allowed
        def cur_allo(self, req_type):
            return self.is_allowed

        @voltage.read
        def vol_read(self):
            return self.voltage_value

        @voltage.write
        def vol_write(self, voltage):
            self.voltage_value = voltage

        @voltage.is_allowed
        def vol_allo(self, req_type):
            return self.is_allowed
        """)

        @command(dtype_in=bool)
        def make_allowed(self, yesno):
            self.is_allowed = yesno

        if server_green_mode == GreenMode.Asyncio:
            exec(sync_code.replace("def ", "async def "))
        else:
            exec(sync_code)

    with DeviceTestContext(TestDevice) as proxy:
        proxy.make_allowed(True)
        proxy.current = 2.
        assert_close(proxy.current, 2.)
        proxy.voltage = 3.
        assert_close(proxy.voltage, 3.)

        proxy.make_allowed(False)
        with pytest.raises(DevFailed):
            proxy.current = 4.
        with pytest.raises(DevFailed):
            _ = proxy.current
        with pytest.raises(DevFailed):
            proxy.voltage = 4.
        with pytest.raises(DevFailed):
            _ = proxy.voltage


def test_read_only_dynamic_attribute_with_dummy_write_method(dynamic_attribute_read_function, server_green_mode):

    def dummy_write_method():
        return None

    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attr_value = 123

        def initialize_dynamic_attributes(self):
            self.add_attribute(
                Attr('dyn_attr', DevLong, AttrWriteType.READ),
                r_meth=self.read_dyn_attr,
                w_meth=dummy_write_method,
            )

        sync_code = textwrap.dedent("""\
            def read_dyn_attr(self):
                return self.attr_value
                """)

        if server_green_mode != GreenMode.Asyncio:
            exec(sync_code)
        else:
            exec(sync_code.replace("def ", "async def "))

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.dyn_attr == 123


# Test properties

def test_device_property_no_default(command_typed_values, server_green_mode):
    dtype, values, expected = command_typed_values
    patched_dtype = dtype if dtype != (bool,) else (int,)
    value = values[1]

    class TestDevice(Device):
        green_mode = server_green_mode

        prop_without_db_value = device_property(dtype=dtype)
        prop_with_db_value = device_property(dtype=dtype)

        @command(dtype_out=bool)
        def is_prop_without_db_value_set_to_none(self):
            return self.prop_without_db_value is None

        @command(dtype_out=patched_dtype)
        def get_prop_with_db_value(self):
            return self.prop_with_db_value

    with DeviceTestContext(TestDevice,
                           properties={'prop_with_db_value': value}) as proxy:
        assert proxy.is_prop_without_db_value_set_to_none()
        assert_close(proxy.get_prop_with_db_value(), expected(value))


def test_device_property_with_default_value(command_typed_values, server_green_mode):
    dtype, values, expected = command_typed_values
    patched_dtype = dtype if dtype != (bool,) else (int,)

    default = values[0]
    value = values[1]

    class TestDevice(Device):
        green_mode = server_green_mode

        prop_without_db_value = device_property(
            dtype=dtype, default_value=default
        )
        prop_with_db_value = device_property(
            dtype=dtype, default_value=default
        )

        @command(dtype_out=patched_dtype)
        def get_prop_without_db_value(self):
            return self.prop_without_db_value

        @command(dtype_out=patched_dtype)
        def get_prop_with_db_value(self):
            return self.prop_with_db_value

    with DeviceTestContext(TestDevice,
                           properties={'prop_with_db_value': value}) as proxy:
        assert_close(proxy.get_prop_without_db_value(), expected(default))
        assert_close(proxy.get_prop_with_db_value(), expected(value))


def test_device_get_device_properties_when_init_device(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode
        _got_properties = False

        def get_device_properties(self, *args, **kwargs):
            super().get_device_properties(*args, **kwargs)
            self._got_properties = True

        @attribute(dtype=bool)
        def got_properties(self):
            return self._got_properties

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.got_properties


def test_device_get_attr_config(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode

        @attribute(dtype=bool)
        def attr_config_ok(self):
            # testing that call to get_attribute_config for all types of
            # input arguments gives same result and doesn't raise an exception
            ac1 = self.get_attribute_config(b"attr_config_ok")
            ac2 = self.get_attribute_config("attr_config_ok")
            ac3 = self.get_attribute_config(["attr_config_ok"])
            return repr(ac1) == repr(ac2) == repr(ac3)

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.attr_config_ok


# Test inheritance

def test_inheritance(server_green_mode):

    class A(Device):
        green_mode = server_green_mode

        prop1 = device_property(dtype=str, default_value="hello1")
        prop2 = device_property(dtype=str, default_value="hello2")

        @command(dtype_out=str)
        def get_prop1(self):
            return self.prop1

        @command(dtype_out=str)
        def get_prop2(self):
            return self.prop2

        @attribute(access=AttrWriteType.READ_WRITE)
        def attr(self):
            return self.attr_value

        @attr.write
        def attr(self, value):
            self.attr_value = value

        def dev_status(self):
            return ")`'-.,_"

    class B(A):

        prop2 = device_property(dtype=str, default_value="goodbye2")

        @attribute
        def attr2(self):
            return 3.14

        if server_green_mode == GreenMode.Asyncio:
            async def dev_status(self):
                coro = super(type(self), self).dev_status()
                result = await coro
                return 3*result
        else:
            def dev_status(self):
                return 3 * A.dev_status(self)


    with DeviceTestContext(B) as proxy:
        assert proxy.get_prop1() == "hello1"
        assert proxy.get_prop2() == "goodbye2"
        proxy.attr = 1.23
        assert proxy.attr == 1.23
        assert proxy.attr2 == 3.14
        assert proxy.status() == ")`'-.,_)`'-.,_)`'-.,_"


def test_polled_attribute(server_green_mode):

    dct = {'PolledAttribute1': 100,
           'PolledAttribute2': 100000,
           'PolledAttribute3': 500}

    class TestDevice(Device):
        green_mode = server_green_mode

        @attribute(polling_period=dct["PolledAttribute1"])
        def PolledAttribute1(self):
            return 42.0

        @attribute(polling_period=dct["PolledAttribute2"])
        def PolledAttribute2(self):
            return 43.0

        @attribute(polling_period=dct["PolledAttribute3"])
        def PolledAttribute3(self):
            return 44.0

    with DeviceTestContext(TestDevice) as proxy:
        ans = proxy.polling_status()
        for x in ans:
            lines = x.split('\n')
            attr = lines[0].split('= ')[1]
            poll_period = int(lines[1].split('= ')[1])
            assert dct[attr] == poll_period


def test_mandatory_device_property_with_db_value_succeeds(command_typed_values, server_green_mode):
    dtype, values, expected = command_typed_values
    patched_dtype = dtype if dtype != (bool,) else (int,)
    default, value = values[:2]

    class TestDevice(Device):
        green_mode = server_green_mode

        prop = device_property(dtype=dtype, mandatory=True)

        @command(dtype_out=patched_dtype)
        def get_prop(self):
            return self.prop

    with DeviceTestContext(TestDevice,
                           properties={'prop': value}) as proxy:
        assert_close(proxy.get_prop(), expected(value))


def test_mandatory_device_property_without_db_value_fails(command_typed_values, server_green_mode):
    dtype, _, _ = command_typed_values

    class TestDevice(Device):
        green_mode = server_green_mode
        prop = device_property(dtype=dtype, mandatory=True)

    with pytest.raises(DevFailed) as context:
        with DeviceTestContext(TestDevice):
            pass
    assert 'Device property prop is mandatory' in str(context.value)


def test_logging(server_green_mode):
    log_received = threading.Event()

    class LogSourceDevice(Device):
        green_mode = server_green_mode
        _last_log_time = 0.0

        @command(dtype_in=('str',))
        def log_fatal_message(self, msg):
            self._last_log_time = time.time()
            if len(msg) > 1:
                self.fatal_stream(msg[0], msg[1])
            else:
                self.fatal_stream(msg[0])

        @command(dtype_in=('str',))
        def log_error_message(self, msg):
            self._last_log_time = time.time()
            if len(msg) > 1:
                self.error_stream(msg[0], msg[1])
            else:
                self.error_stream(msg[0])

        @command(dtype_in=('str',))
        def log_warn_message(self, msg):
            self._last_log_time = time.time()
            if len(msg) > 1:
                self.warn_stream(msg[0], msg[1])
            else:
                self.warn_stream(msg[0])

        @command(dtype_in=('str',))
        def log_info_message(self, msg):
            self._last_log_time = time.time()
            if len(msg) > 1:
                self.info_stream(msg[0], msg[1])
            else:
                self.info_stream(msg[0])

        @command(dtype_in=('str',))
        def log_debug_message(self, msg):
            self._last_log_time = time.time()
            if len(msg) > 1:
                self.debug_stream(msg[0], msg[1])
            else:
                self.debug_stream(msg[0])

        @attribute(dtype=float)
        def last_log_time(self):
            return self._last_log_time

    class LogConsumerDevice(Device):
        green_mode = server_green_mode
        _last_log_data = []

        @command(dtype_in=('str',))
        def Log(self, argin):
            self._last_log_data = argin
            log_received.set()

        @attribute(dtype=int)
        def last_log_timestamp_ms(self):
            return int(self._last_log_data[0])

        @attribute(dtype=str)
        def last_log_level(self):
            return self._last_log_data[1]

        @attribute(dtype=str)
        def last_log_source(self):
            return self._last_log_data[2]

        @attribute(dtype=str)
        def last_log_message(self):
            return self._last_log_data[3]

        @attribute(dtype=str)
        def last_log_context_unused(self):
            return self._last_log_data[4]

        @attribute(dtype=str)
        def last_log_thread_id(self):
            return self._last_log_data[5]

    def assert_log_details_correct(level, msg):
        assert log_received.wait(0.5)
        _assert_log_time_close_enough()
        _assert_log_fields_correct_for_level(level, msg)
        log_received.clear()

    def _assert_log_time_close_enough():
        log_emit_time = proxy_source.last_log_time
        log_receive_time = proxy_consumer.last_log_timestamp_ms / 1000.0
        now = time.time()
        # cppTango logger time function may use a different
        # implementation to CPython's time.time().  This is
        # especially noticeable on Windows platforms.
        timer_implementation_tolerance = 0.020 if WINDOWS else 0.001
        min_time = log_emit_time - timer_implementation_tolerance
        max_time = now + timer_implementation_tolerance
        assert min_time <= log_receive_time <= max_time

    def _assert_log_fields_correct_for_level(level, msg):
        assert proxy_consumer.last_log_level == level.upper()
        assert proxy_consumer.last_log_source == "test/log/source"
        assert proxy_consumer.last_log_message == msg
        assert proxy_consumer.last_log_context_unused == ""
        assert len(proxy_consumer.last_log_thread_id) > 0

    devices_info = (
        {"class": LogSourceDevice, "devices": [{"name": "test/log/source"}]},
        {"class": LogConsumerDevice,
         "devices": [{"name": "test/log/consumer"}]},
    )

    with MultiDeviceTestContext(devices_info) as context:
        proxy_source = context.get_device("test/log/source")
        proxy_consumer = context.get_device("test/log/consumer")
        consumer_access = context.get_device_access("test/log/consumer")
        proxy_source.add_logging_target(f"device::{consumer_access}")

        for msg in ([""],
                    [" with literal %s"],
                    [" with string %s as arg", "foo"]):

            level = "fatal"
            log_msg = msg[:]
            log_msg[0] = "test " + level + msg[0]
            proxy_source.log_fatal_message(log_msg)
            if len(msg) > 1:
                 check_log_msg = log_msg[0] % log_msg[1]
            else:
                check_log_msg = log_msg[0]
            assert_log_details_correct(level, check_log_msg)

            level = 'error'
            log_msg = msg[:]
            log_msg[0] = "test " + level + msg[0]
            proxy_source.log_error_message(log_msg)
            if len(msg) > 1:
                 check_log_msg = log_msg[0] % log_msg[1]
            else:
                check_log_msg = log_msg[0]
            assert_log_details_correct(level, check_log_msg)

            level = 'warn'
            log_msg = msg[:]
            log_msg[0] = "test " + level + msg[0]
            proxy_source.log_warn_message(log_msg)
            if len(msg) > 1:
                 check_log_msg = log_msg[0] % log_msg[1]
            else:
                check_log_msg = log_msg[0]
            assert_log_details_correct(level, check_log_msg)

            level = 'info'
            log_msg = msg[:]
            log_msg[0] = "test " + level + msg[0]
            proxy_source.log_info_message(log_msg)
            if len(msg) > 1:
                 check_log_msg = log_msg[0] % log_msg[1]
            else:
                check_log_msg = log_msg[0]
            assert_log_details_correct(level, check_log_msg)

            level = 'debug'
            log_msg = msg[:]
            log_msg[0] = "test " + level + msg[0]
            proxy_source.log_debug_message(log_msg)
            if len(msg) > 1:
                 check_log_msg = log_msg[0] % log_msg[1]
            else:
                check_log_msg = log_msg[0]
            assert_log_details_correct(level, check_log_msg)


# fixtures

@pytest.fixture(params=[GoodEnum])
def good_enum(request):
    return request.param


@pytest.fixture(params=[BadEnumNonZero, BadEnumSkipValues, BadEnumDuplicates])
def bad_enum(request):
    return request.param


# test utilities for servers

def test_get_enum_labels_success(good_enum):
    expected_labels = ['START', 'MIDDLE', 'END']
    assert get_enum_labels(good_enum) == expected_labels


def test_get_enum_labels_fail(bad_enum):
    with pytest.raises(EnumTypeError):
        get_enum_labels(bad_enum)


# DevEncoded

def test_read_write_dev_encoded(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode
        attr_value = ("uint8", b"\xd2\xd3")

        @attribute(dtype=DevEncoded,
                   access=AttrWriteType.READ_WRITE)
        def attr(self):
            return self.attr_value

        @attr.write
        def attr(self, value):
            self.attr_value = value

        @command(dtype_in=DevEncoded)
        def cmd_in(self, value):
            self.attr_value = value

        @command(dtype_out=DevEncoded)
        def cmd_out(self):
            return self.attr_value

        @command(dtype_in=DevEncoded, dtype_out=DevEncoded)
        def cmd_in_out(self, value):
            self.attr_value = value
            return self.attr_value

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.attr == ("uint8", b"\xd2\xd3")

        proxy.attr = ("uint8", b"\xde")
        assert proxy.attr == ("uint8", b"\xde")

        proxy.cmd_in(("uint8", b"\xd4\xd5"))
        assert proxy.cmd_out() == ("uint8", b"\xd4\xd5")

        proxy.cmd_in_out(('uint8', b"\xd6\xd7"))
        assert proxy.attr == ("uint8", b"\xd6\xd7")


# Test Exception propagation

def test_exception_propagation(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode

        @attribute
        def attr(self):
            1 / 0  # pylint: disable=pointless-statement

        @command
        def cmd(self):
            1 / 0  # pylint: disable=pointless-statement

    with DeviceTestContext(TestDevice) as proxy:
        with pytest.raises(DevFailed) as record:
            proxy.attr  # pylint: disable=pointless-statement
        assert "ZeroDivisionError" in record.value.args[0].desc

        with pytest.raises(DevFailed) as record:
            proxy.cmd()
        assert "ZeroDivisionError" in record.value.args[0].desc


def _avoid_double_colon_node_ids(val):
    """Return node IDs without a double colon.

    IDs with "::" can't be used to launch a test from the command line, as pytest
    considers this sequence as a module/test name separator.  Add something extra
    to keep them usable for single test command line execution (e.g., under Windows CI).
    """
    if is_pure_str(val) and "::" in val:
        return str(val).replace("::", ":_:")


@pytest.fixture(params=['linux', 'win'])
def os_system(request):
    original_platform = sys.platform
    sys.platform = request.param
    yield
    sys.platform = original_platform


@pytest.mark.parametrize(
    "applicable_os, test_input, expected_output",
    DEVICE_SERVER_ARGUMENTS,
    ids=_avoid_double_colon_node_ids
)
def test_arguments(applicable_os, test_input, expected_output, os_system):
    try:
        assert set(parse_args(test_input.split())) == set(expected_output)
    except SystemExit:
        assert sys.platform not in applicable_os
