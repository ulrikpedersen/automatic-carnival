# -*- coding: utf-8 -*-

import os
import sys
import textwrap
import threading
import time
import pytest
import enum

from tango import AttrData, Attr, AttrDataFormat, AttReqType, AttrWriteType, \
    DevBoolean, DevLong, DevDouble, DevFailed, \
    DevEncoded, DevEnum, DevState, DevVoid, \
    Device_4Impl, Device_5Impl, DeviceClass, \
    GreenMode, LatestDeviceImpl, READ_WRITE, SCALAR
from tango.server import Device
from tango.pyutil import parse_args
from tango.server import _get_tango_type_format, command, attribute, device_property
from tango.test_utils import DeviceTestContext, MultiDeviceTestContext, \
    GoodEnum, BadEnumNonZero, BadEnumSkipValues, BadEnumDuplicates, \
    assert_close, DEVICE_SERVER_ARGUMENTS, os_system
from tango.utils import EnumTypeError, get_enum_labels, is_pure_str

# Asyncio imports
try:
    import asyncio
except ImportError:
    import trollius as asyncio  # noqa: F401

# Constants
WINDOWS = "nt" in os.name


# Test state/status

def test_empty_device(server_green_mode):

    class TestDevice(Device):
        green_mode = server_green_mode

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.state() == DevState.UNKNOWN
        assert proxy.status() == 'The device is in UNKNOWN state.'


def test_set_state(state, server_green_mode):
    status = 'The device is in {0!s} state.'.format(state)

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

def test_identity_command(typed_values, server_green_mode):
    dtype, values, expected = typed_values

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

def test_read_write_attribute(typed_values, server_green_mode):
    dtype, values, expected = typed_values

    class TestDevice(Device):
        green_mode = server_green_mode

        @attribute(dtype=dtype, max_dim_x=10,
                   access=AttrWriteType.READ_WRITE)
        def attr(self):
            return self.attr_value

        @attr.write
        def attr(self, value):
            self.attr_value = value

    with DeviceTestContext(TestDevice) as proxy:
        for value in values:
            proxy.attr = value
            assert_close(proxy.attr, expected(value))


def test_read_write_attribute_enum(server_green_mode):
    values = (member.value for member in GoodEnum)
    enum_labels = get_enum_labels(GoodEnum)

    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super(TestDevice, self).__init__(*args, **kwargs)
            self.attr_from_enum_value = 0
            self.attr_from_labels_value = 0

        @attribute(dtype=GoodEnum, access=AttrWriteType.READ_WRITE)
        def attr_from_enum(self):
            return self.attr_from_enum_value

        @attr_from_enum.write
        def attr_from_enum(self, value):
            self.attr_from_enum_value = value

        @attribute(dtype='DevEnum', enum_labels=enum_labels,
                   access=AttrWriteType.READ_WRITE)
        def attr_from_labels(self):
            return self.attr_from_labels_value

        @attr_from_labels.write
        def attr_from_labels(self, value):
            self.attr_from_labels_value = value

    with DeviceTestContext(TestDevice) as proxy:
        for value, label in zip(values, enum_labels):
            proxy.attr_from_enum = value
            read_attr = proxy.attr_from_enum
            assert read_attr == value
            assert isinstance(read_attr, enum.IntEnum)
            assert read_attr.value == value
            assert read_attr.name == label
            proxy.attr_from_labels = value
            read_attr = proxy.attr_from_labels
            assert read_attr == value
            assert isinstance(read_attr, enum.IntEnum)
            assert read_attr.value == value
            assert read_attr.name == label
        for value, label in zip(values, enum_labels):
            proxy.attr_from_enum = label
            read_attr = proxy.attr_from_enum
            assert read_attr == value
            assert isinstance(read_attr, enum.IntEnum)
            assert read_attr.value == value
            assert read_attr.name == label
            proxy.attr_from_labels = label
            read_attr = proxy.attr_from_labels
            assert read_attr == value
            assert isinstance(read_attr, enum.IntEnum)
            assert read_attr.value == value
            assert read_attr.name == label

    with pytest.raises(TypeError) as context:
        class BadTestDevice(Device):
            green_mode = server_green_mode

            def __init__(self, *args, **kwargs):
                super(BadTestDevice, self).__init__(*args, **kwargs)
                self.attr_value = 0

            # enum_labels may not be specified if dtype is an enum.Enum
            @attribute(dtype=GoodEnum, enum_labels=enum_labels)
            def bad_attr(self):
                return self.attr_value

        BadTestDevice()  # dummy instance for Codacy
    assert 'enum_labels' in str(context.value)


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

        def read_attr_r(self):
            return "readable"

        def read_attr_rw(self):
            return self._read_write_value

        def write_attr_rw(self, value):
            self._read_write_value = value

        def is_attr_r_allowed(self, req_type):
            assert req_type == AttReqType.READ_REQ
            return self._is_allowed

        def is_attr_rw_allowed(self, req_type):
            assert req_type in (AttReqType.READ_REQ, AttReqType.WRITE_REQ)
            return self._is_allowed

        @command(dtype_in=bool)
        def make_allowed(self, yesno):
            self._is_allowed = yesno

    with DeviceTestContext(TestDevice) as proxy:
        proxy.make_allowed(True)
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



def test_read_write_dynamic_attribute(typed_values, server_green_mode):
    dtype, values, expected = typed_values

    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super(TestDevice, self).__init__(*args, **kwargs)
            self.attr_value = None

        @command
        def add_dyn_attr(self):
            attr = attribute(
                name="dyn_attr",
                dtype=dtype,
                max_dim_x=10,
                access=AttrWriteType.READ_WRITE,
                fget=self.read,
                fset=self.write)
            self.add_attribute(attr)

        @command
        def delete_dyn_attr(self):
            self.remove_attribute("dyn_attr")

        def read(self, attr):
            attr.set_value(self.attr_value)

        def write(self, attr):
            self.attr_value = attr.get_write_value()

    with DeviceTestContext(TestDevice) as proxy:
        proxy.add_dyn_attr()
        for value in values:
            proxy.dyn_attr = value
            assert_close(proxy.dyn_attr, expected(value))
        proxy.delete_dyn_attr()
        assert "dyn_attr" not in proxy.get_attribute_list()


def test_read_write_dynamic_attribute_enum(server_green_mode):
    values = (member.value for member in GoodEnum)
    enum_labels = get_enum_labels(GoodEnum)

    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super(TestDevice, self).__init__(*args, **kwargs)
            self.attr_value = 0

        @command
        def add_dyn_attr_old(self):
            attr = AttrData(
                "dyn_attr",
                None,
                attr_info=[
                    (DevEnum, SCALAR, READ_WRITE),
                    {"enum_labels": enum_labels},
                ],
            )
            self.add_attribute(attr, r_meth=self.read, w_meth=self.write)

        @command
        def add_dyn_attr_new(self):
            attr = attribute(
                name="dyn_attr",
                dtype=GoodEnum,
                access=AttrWriteType.READ_WRITE,
                fget=self.read,
                fset=self.write)
            self.add_attribute(attr)

        @command
        def delete_dyn_attr(self):
            self.remove_attribute("dyn_attr")

        def read(self, attr):
            attr.set_value(self.attr_value)

        def write(self, attr):
            self.attr_value = attr.get_write_value()

    with DeviceTestContext(TestDevice) as proxy:
        for add_attr_cmd in [proxy.add_dyn_attr_old, proxy.add_dyn_attr_new]:
            add_attr_cmd()
            for value, label in zip(values, enum_labels):
                proxy.dyn_attr = value
                read_attr = proxy.dyn_attr
                assert read_attr == value
                assert isinstance(read_attr, enum.IntEnum)
                assert read_attr.value == value
                assert read_attr.name == label
            proxy.delete_dyn_attr()
            assert "dyn_attr" not in proxy.get_attribute_list()


def test_read_write_dynamic_attribute_is_allowed_with_async(
        typed_values, server_green_mode):
    dtype, values, expected = typed_values

    class TestDevice(Device):
        green_mode = server_green_mode

        def __init__(self, *args, **kwargs):
            super(TestDevice, self).__init__(*args, **kwargs)
            self._is_test_attr_allowed = True

        def initialize_dynamic_attributes(self):
            # recommended approach: using attribute() and bound methods:
            attr = attribute(
                name="dyn_attr1",
                dtype=dtype,
                max_dim_x=10,
                access=AttrWriteType.READ_WRITE,
                fget=self.read_attr1,
                fset=self.write_attr1,
                fisallowed=self.is_attr1_allowed,
            )
            self.add_attribute(attr)

            # not recommended: using attribute() with unbound methods:
            attr = attribute(
                name="dyn_attr2",
                dtype=dtype,
                max_dim_x=10,
                access=AttrWriteType.READ_WRITE,
                fget=TestDevice.read_attr2,
                fset=TestDevice.write_attr2,
                fisallowed=TestDevice.is_attr2_allowed,
            )
            self.add_attribute(attr)

            # possible approach: using attribute() with method name strings:
            attr = attribute(
                name="dyn_attr3",
                dtype=dtype,
                max_dim_x=10,
                access=AttrWriteType.READ_WRITE,
                fget="read_attr3",
                fset="write_attr3",
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
                self.read_attr4,
                self.write_attr4,
                self.is_attr4_allowed,
            )

            # old approach: using tango.AttrData with unbound methods:
            attr_name = "dyn_attr5"
            attr_data = AttrData(attr_name, dev_class.get_name(), data_info)
            self.add_attribute(
                attr_data,
                TestDevice.read_attr5,
                TestDevice.write_attr5,
                TestDevice.is_attr5_allowed,
            )

            # old approach: using tango.AttrData with default method names
            attr_name = "dyn_attr6"
            attr_data = AttrData(attr_name, dev_class.get_name(), data_info)
            self.add_attribute(attr_data)

        def _get_attr_data_info(self):
            simple_type, fmt = _get_tango_type_format(dtype)
            data_info = [[simple_type, fmt, READ_WRITE]]
            if fmt == AttrDataFormat.SPECTRUM:
                max_dim_x = 10
                data_info[0].append(max_dim_x)
            return data_info

        @command(dtype_in=bool)
        def make_allowed(self, yesno):
            self._is_test_attr_allowed = yesno

        # the following methods are written in plain text which looks
        # weird. This is done so that it is easy to change for async
        # tests without duplicating all the code.
        synchronous_code = textwrap.dedent("""\
            def read_attr1(self, attr):
                attr.set_value(self.attr_value1)
    
            def write_attr1(self, attr):
                self.attr_value1 = attr.get_write_value()
    
            def is_attr1_allowed(self, req_type):
                return self._is_test_attr_allowed
    
            def read_attr2(self, attr):
                attr.set_value(self.attr_value2)
    
            def write_attr2(self, attr):
                self.attr_value2 = attr.get_write_value()
    
            def is_attr2_allowed(self, req_type):
                return self._is_test_attr_allowed
    
            def read_attr3(self, attr):
                attr.set_value(self.attr_value3)
    
            def write_attr3(self, attr):
                self.attr_value3 = attr.get_write_value()
    
            def is_attr3_allowed(self, req_type):
                return self._is_test_attr_allowed
    
            def read_attr4(self, attr):
                attr.set_value(self.attr_value4)
    
            def write_attr4(self, attr):
                self.attr_value4 = attr.get_write_value()
    
            def is_attr4_allowed(self, req_type):
                return self._is_test_attr_allowed
    
            def read_attr5(self, attr):
                attr.set_value(self.attr_value5)
    
            def write_attr5(self, attr):
                self.attr_value5 = attr.get_write_value()
    
            def is_attr5_allowed(self, req_type):
                return self._is_test_attr_allowed
    
            def read_dyn_attr6(self, attr):
                attr.set_value(self.attr_value6)
    
            def write_dyn_attr6(self, attr):
                self.attr_value6 = attr.get_write_value()
    
            def is_dyn_attr6_allowed(self, req_type):
                return self._is_test_attr_allowed
            """)

        asynchronous_code = synchronous_code.replace("def ", "async def ")

        if server_green_mode != GreenMode.Asyncio:
            exec(synchronous_code)
        else:
            exec(asynchronous_code)

    with DeviceTestContext(TestDevice) as proxy:
        proxy.make_allowed(True)
        for value in values:
            proxy.dyn_attr1 = value
            assert_close(proxy.dyn_attr1, expected(value))
            proxy.dyn_attr2 = value
            assert_close(proxy.dyn_attr2, expected(value))
            proxy.dyn_attr3 = value
            assert_close(proxy.dyn_attr3, expected(value))
            proxy.dyn_attr4 = value
            assert_close(proxy.dyn_attr4, expected(value))
            proxy.dyn_attr5 = value
            assert_close(proxy.dyn_attr5, expected(value))
            proxy.dyn_attr6 = value
            assert_close(proxy.dyn_attr6, expected(value))

        proxy.make_allowed(False)
        for value in values:
            with pytest.raises(DevFailed):
                proxy.dyn_attr1 = value
            with pytest.raises(DevFailed):
                _ = proxy.dyn_attr1
            with pytest.raises(DevFailed):
                proxy.dyn_attr2 = value
            with pytest.raises(DevFailed):
                _ = proxy.dyn_attr2
            with pytest.raises(DevFailed):
                proxy.dyn_attr3 = value
            with pytest.raises(DevFailed):
                _ = proxy.dyn_attr3
            with pytest.raises(DevFailed):
                proxy.dyn_attr4 = value
            with pytest.raises(DevFailed):
                _ = proxy.dyn_attr4
            with pytest.raises(DevFailed):
                proxy.dyn_attr5 = value
            with pytest.raises(DevFailed):
                _ = proxy.dyn_attr5
            with pytest.raises(DevFailed):
                proxy.dyn_attr6 = value
            with pytest.raises(DevFailed):
                _ = proxy.dyn_attr6


@pytest.mark.parametrize(
    "device_impl_class",
    [Device_4Impl, Device_5Impl, LatestDeviceImpl]
)
def test_dynamic_attribute_using_classic_api_like_sardana(device_impl_class):

    class ClassicAPIClass(DeviceClass):

        cmd_list = {
            'make_allowed': [[DevBoolean, "allow access"], [DevVoid, "none"]],
        }

        def __init__(self, name):
            super(ClassicAPIClass, self).__init__(name)
            self.set_type("TestDevice")

    class ClassicAPIDeviceImpl(device_impl_class):

        def __init__(self, cl, name):
            super(ClassicAPIDeviceImpl, self).__init__(cl, name)
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


def test_dynamic_attribute_with_non_device_method_fails(server_green_mode):

    def read_function_outside_of_any_class(attr):
        attr.set_value(123)

    class NonDeviceClass(object):
        def read_method_outside_of_device_class(self, attr):
            attr.set_value(456)

    class TestDevice(Device):
        green_mode = server_green_mode

        def initialize_dynamic_attributes(self):
            attr = attribute(
                name="dyn_attr1",
                dtype=int,
                access=AttrWriteType.READ,
                fget=read_function_outside_of_any_class,
            )
            self.add_attribute(attr)
            attr = attribute(
                name="dyn_attr2",
                dtype=int,
                access=AttrWriteType.READ,
                fget=NonDeviceClass.read_method_outside_of_device_class,
            )
            self.add_attribute(attr)

    # typically devices with non method class cannot work
    with pytest.raises(DevFailed):
        with DeviceTestContext(TestDevice):
            pass


def test_dynamic_attribute_with_non_device_method_patched(server_green_mode):

    if server_green_mode == GreenMode.Asyncio:
        async def read_function_outside_of_any_class(attr):
            attr.set_value(123)
    else:
        def read_function_outside_of_any_class(attr):
            attr.set_value(123)

    class TestDevice(Device):
        green_mode = server_green_mode

        def initialize_dynamic_attributes(self):
            # trick to run server with non device method: patch __dict__
            self.__dict__['read_dyn_attr1'] = read_function_outside_of_any_class
            attr = attribute(
                name="dyn_attr1",
                dtype=int,
                access=AttrWriteType.READ,
            )
            self.add_attribute(attr)

            setattr(self, 'read_dyn_attr2', read_function_outside_of_any_class)
            attr = attribute(
                name="dyn_attr2",
                dtype=int,
                access=AttrWriteType.READ,
            )
            self.add_attribute(attr)

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.dyn_attr1 == 123
        assert proxy.dyn_attr2 == 123


def test_read_only_dynamic_attribute_with_dummy_write_method(server_green_mode):

    def dummy_write_method():
        return None

    class TestDevice(Device):
        green_mode = server_green_mode

        def read_attribute(self, attr):
            attr.set_value(123)

        def initialize_dynamic_attributes(self):
            self.add_attribute(
                Attr('dyn_attr', DevLong, AttrWriteType.READ),
                r_meth=self.read_attribute,
                w_meth=dummy_write_method,
            )

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.dyn_attr == 123


# Test properties

def test_device_property_no_default(typed_values, server_green_mode):
    dtype, values, expected = typed_values
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


def test_device_property_with_default_value(typed_values, server_green_mode):
    dtype, values, expected = typed_values
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
            super(TestDevice, self).get_device_properties(*args, **kwargs)
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
            ac2 = self.get_attribute_config(u"attr_config_ok")
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

        def dev_status(self):
            return 3 * A.dev_status(self)

        if server_green_mode == GreenMode.Asyncio:
            async def dev_status(self):
                coro = super(type(self), self).dev_status()
                result = await coro
                return 3*result

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


def test_mandatory_device_property_with_db_value_succeeds(
        typed_values, server_green_mode):
    dtype, values, expected = typed_values
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


def test_mandatory_device_property_without_db_value_fails(
        typed_values, server_green_mode):
    dtype, _, _ = typed_values

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
        proxy_source.add_logging_target("device::{}".format(consumer_access))

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


@pytest.mark.parametrize(
    "applicable_os, test_input, expected_output",
    DEVICE_SERVER_ARGUMENTS,
    ids=_avoid_double_colon_node_ids
)
def test_arguments(applicable_os, test_input, expected_output, os_system):
    try:
        assert set(expected_output) == set(parse_args(test_input.split()))
    except SystemExit as err:
        assert sys.platform not in applicable_os
