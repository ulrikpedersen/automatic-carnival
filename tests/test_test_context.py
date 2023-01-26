import os

import pytest

import tango

from tango import AttrWriteType, GreenMode
from tango.asyncio_executor import AsyncioExecutor
from tango.device_server import get_worker
from tango.gevent_executor import GeventExecutor
from tango.green import SynchronousExecutor
from tango.server import Device
from tango.server import command, attribute, device_property
from tango.test_utils import (
    DeviceTestContext,
    MultiDeviceTestContext,
    SimpleDevice,
    ClassicAPISimpleDeviceImpl,
    ClassicAPISimpleDeviceClass
)


WINDOWS = "nt" in os.name


class Device1(Device):

    def init_device(self):
        super(Device, self).init_device()
        self.set_state(tango.DevState.ON)
        self._attr1 = 100

    @attribute
    def attr1(self):
        return self._attr1


class Device2(Device):

    def init_device(self):
        super(Device, self).init_device()
        self.set_state(tango.DevState.ON)
        self._attr2 = 200

    @attribute
    def attr2(self):
        return self._attr2


class Device1GreenModeUnspecified(Device1):
    pass


class Device1Synchronous(Device1):
    green_mode = GreenMode.Synchronous


class Device1Gevent(Device1):
    green_mode = GreenMode.Gevent


class Device1Asyncio(Device1):
    green_mode = GreenMode.Asyncio


class Device2GreenModeUnspecified(Device2):
    pass


class Device2Synchronous(Device2):
    green_mode = GreenMode.Synchronous


class Device2Gevent(Device2):
    green_mode = GreenMode.Gevent


class Device2Asyncio(Device2):
    green_mode = GreenMode.Asyncio


class Device1AsyncInit(Device1):
    green_mode = GreenMode.Asyncio

    async def init_device(self):
        await super().init_device()
        self._attr1 = 150


def test_single_device(server_green_mode):
    class TestDevice(Device1):
        green_mode = server_green_mode

    with DeviceTestContext(TestDevice) as proxy:
        assert proxy.attr1 == 100


def test_single_async_init_device():
    with DeviceTestContext(Device1AsyncInit) as proxy:
        assert proxy.attr1 == 150


def test_single_device_old_api():
    with DeviceTestContext(ClassicAPISimpleDeviceImpl, ClassicAPISimpleDeviceClass) as proxy:
        assert proxy.attr1 == 100


@pytest.mark.parametrize(
    "class_field, device",
    [
        (SimpleDevice, SimpleDevice),
        ("tango.test_utils.SimpleDevice", SimpleDevice),
        (
            ("tango.test_utils.ClassicAPISimpleDeviceClass", "tango.test_utils.ClassicAPISimpleDeviceImpl"),
            ClassicAPISimpleDeviceImpl
        ),
        (
            ("tango.test_utils.ClassicAPISimpleDeviceClass", ClassicAPISimpleDeviceImpl),
            ClassicAPISimpleDeviceImpl
        ),
        (
            (ClassicAPISimpleDeviceClass, "tango.test_utils.ClassicAPISimpleDeviceImpl"),
            ClassicAPISimpleDeviceImpl
        ),
        (
            (ClassicAPISimpleDeviceClass, ClassicAPISimpleDeviceImpl),
            ClassicAPISimpleDeviceImpl
        ),
    ]
)
def test_multi_devices_info(class_field, device):
    devices_info = ({"class": class_field, "devices": [{"name": "test/device1/1"}]},)

    dev_class = device if isinstance(device, str) else device.__name__

    with MultiDeviceTestContext(devices_info) as context:
        proxy1 = context.get_device("test/device1/1")
        assert proxy1.info().dev_class == dev_class


def test_multi_with_single_device(server_green_mode):
    class TestDevice(Device1):
        green_mode = server_green_mode

    devices_info = ({"class": TestDevice, "devices": [{"name": "test/device1/1"}]},)

    with MultiDeviceTestContext(devices_info) as context:
        proxy1 = context.get_device("test/device1/1")
        assert proxy1.attr1 == 100


def test_multi_with_single_device_old_api():
    devices_info = (
        {
            "class": (ClassicAPISimpleDeviceClass, ClassicAPISimpleDeviceImpl),
            "devices": [{"name": "test/device1/1"}],
        },
    )

    with MultiDeviceTestContext(devices_info) as context:
        proxy1 = context.get_device("test/device1/1")
        assert proxy1.attr1 == 100


def test_multi_with_two_devices(server_green_mode):
    class TestDevice1(Device1):
        green_mode = server_green_mode

    class TestDevice2(Device2):
        green_mode = server_green_mode

    devices_info = (
        {"class": TestDevice1, "devices": [{"name": "test/device1/1"}]},
        {"class": TestDevice2, "devices": [{"name": "test/device2/1"}]},
    )

    with MultiDeviceTestContext(devices_info) as context:
        proxy1 = context.get_device("test/device1/1")
        proxy2 = context.get_device("test/device2/1")
        assert proxy1.State() == tango.DevState.ON
        assert proxy2.State() == tango.DevState.ON
        assert proxy1.attr1 == 100
        assert proxy2.attr2 == 200


@pytest.mark.parametrize(
    "first_type, second_type, exception_type",
    [
        (Device1GreenModeUnspecified, Device2GreenModeUnspecified, None),
        (Device1GreenModeUnspecified, Device2Synchronous, None),
        (Device1GreenModeUnspecified, Device2Gevent, ValueError),
        (Device1GreenModeUnspecified, Device2Asyncio, ValueError),
        (Device1Synchronous, Device2GreenModeUnspecified, None),
        (Device1Synchronous, Device2Synchronous, None),
        (Device1Synchronous, Device2Gevent, ValueError),
        (Device1Synchronous, Device2Asyncio, ValueError),
        (Device1Asyncio, Device2GreenModeUnspecified, ValueError),
        (Device1Asyncio, Device2Synchronous, ValueError),
        (Device1Asyncio, Device2Gevent, ValueError),
        (Device1Asyncio, Device2Asyncio, None),
        (Device1Gevent, Device2GreenModeUnspecified, ValueError),
        (Device1Gevent, Device2Synchronous, ValueError),
        (Device1Gevent, Device2Gevent, None),
        (Device1Gevent, Device2Asyncio, ValueError),
    ]
)
def test_multi_with_mixed_device_green_modes(first_type, second_type, exception_type):

    devices_info = (
        {"class": first_type, "devices": [{"name": "test/device1/1"}]},
        {"class": second_type, "devices": [{"name": "test/device2/1"}]},
    )

    if exception_type is None:
        with MultiDeviceTestContext(devices_info):
            pass
    else:
        with pytest.raises(exception_type, match=r"mixed green mode"):
            with MultiDeviceTestContext(devices_info):
                pass


@pytest.mark.parametrize(
    "device_type, green_mode, global_mode, exception_type, executor_type",
    [
        # If a device specifies its green mode explicitly, then both
        # green_mode kwarg and global green mode are ignored. The device must use its specified mode.
        (Device1Synchronous, GreenMode.Asyncio, GreenMode.Asyncio, None, SynchronousExecutor),
        (Device1Synchronous, GreenMode.Gevent, GreenMode.Gevent, None, SynchronousExecutor),
        (Device1Asyncio, GreenMode.Synchronous, GreenMode.Synchronous, None, AsyncioExecutor),
        (Device1Asyncio, GreenMode.Gevent, GreenMode.Gevent, None, AsyncioExecutor),
        (Device1Gevent, GreenMode.Synchronous, GreenMode.Synchronous, None, GeventExecutor),
        (Device1Gevent, GreenMode.Asyncio, GreenMode.Asyncio, None, GeventExecutor),

        # If device doesn't specify its green mode, but green_mode kwarg is provided,
        # then we use green_mode kwarg
        (Device1GreenModeUnspecified, GreenMode.Synchronous, GreenMode.Asyncio, None, SynchronousExecutor),
        (Device1GreenModeUnspecified, GreenMode.Synchronous, GreenMode.Gevent, None, SynchronousExecutor),
        (Device1GreenModeUnspecified, GreenMode.Asyncio, GreenMode.Synchronous, None, AsyncioExecutor),
        (Device1GreenModeUnspecified, GreenMode.Asyncio, GreenMode.Gevent, None, AsyncioExecutor),
        (Device1GreenModeUnspecified, GreenMode.Gevent, GreenMode.Synchronous, None, GeventExecutor),
        (Device1GreenModeUnspecified, GreenMode.Gevent, GreenMode.Asyncio, None, GeventExecutor),

        # Finally, if neither device green mode nor green_mode kwarg are specified, then use global mode instead.
        # (currently only works for synchronous mode - see unsupported modes below)
        (Device1GreenModeUnspecified, None, GreenMode.Synchronous, None, SynchronousExecutor),

        # Unsupported modes - device servers with the following combinations
        # fail to start up. The cause is unknown. This could be fixed in the future.
        (Device1GreenModeUnspecified, None, GreenMode.Asyncio, RuntimeError, AsyncioExecutor),
        (Device1GreenModeUnspecified, None, GreenMode.Gevent, RuntimeError, GeventExecutor),
        (Device1Asyncio, None,  GreenMode.Asyncio, RuntimeError, AsyncioExecutor),
        (Device1Gevent, None, GreenMode.Gevent, RuntimeError, GeventExecutor),
    ]
)
def test_green_modes_in_device_kwarg_and_global(
    device_type, green_mode, global_mode, exception_type, executor_type
):
    if WINDOWS and exception_type is not None:
        pytest.skip("Skip test that hangs on Windows")
        return

    old_green_mode = tango.get_green_mode()
    try:
        tango.set_green_mode(global_mode)

        if exception_type is None:
            with DeviceTestContext(device_type, green_mode=green_mode):
                pass
            assert type(get_worker()) == executor_type
        else:
            with pytest.raises(exception_type, match=r"stuck at init"):
                with DeviceTestContext(device_type, green_mode=green_mode, timeout=0.5):
                    pass

    finally:
        tango.set_green_mode(old_green_mode)


def test_multi_with_async_devices_initialised():

    class TestDevice2Async(Device2):
        green_mode = GreenMode.Asyncio

    devices_info = (
        {"class": Device1AsyncInit, "devices": [{"name": "test/device1/1"}]},
        {"class": TestDevice2Async, "devices": [{"name": "test/device2/1"}]},
    )

    with MultiDeviceTestContext(devices_info) as context:
        proxy1 = context.get_device("test/device1/1")
        proxy2 = context.get_device("test/device2/1")
        assert proxy1.State() == tango.DevState.ON
        assert proxy2.State() == tango.DevState.ON
        assert proxy1.attr1 == 150
        assert proxy2.attr2 == 200


def test_multi_device_access():
    devices_info = (
        {"class": Device1, "devices": [{"name": "test/device1/1"}]},
        {"class": Device2, "devices": [{"name": "test/device2/2"}]},
    )

    with MultiDeviceTestContext(devices_info) as context:
        device_access1 = context.get_device_access("test/device1/1")
        device_access2 = context.get_device_access("test/device2/2")
        server_access = context.get_server_access()
        assert "test/device1/1" in device_access1
        assert "test/device2/2" in device_access2
        assert context.server_name in server_access
        proxy1 = tango.DeviceProxy(device_access1)
        proxy2 = tango.DeviceProxy(device_access2)
        proxy_server = tango.DeviceProxy(server_access)
        assert proxy1.attr1 == 100
        assert proxy2.attr2 == 200
        assert proxy_server.State() == tango.DevState.ON


def test_multi_device_proxy_cached():
    devices_info = ({"class": Device1, "devices": [{"name": "test/device1/1"}]},)

    with MultiDeviceTestContext(devices_info) as context:
        device1_first = context.get_device("test/device1/1")
        device1_second = context.get_device("test/device1/1")
        assert device1_first is device1_second


def test_multi_with_two_devices_with_properties(server_green_mode):
    class TestDevice1(Device):
        green_mode = server_green_mode

        prop1 = device_property(dtype=str)

        @command(dtype_out=str)
        def get_prop1(self):
            return self.prop1

    class TestDevice2(Device):
        green_mode = server_green_mode

        prop2 = device_property(dtype=int)

        @command(dtype_out=int)
        def get_prop2(self):
            return self.prop2

    devices_info = (
        {
            "class": TestDevice1,
            "devices": [{"name": "test/device1/1", "properties": {"prop1": "abcd"}}],
        },
        {
            "class": TestDevice2,
            "devices": [{"name": "test/device2/2", "properties": {"prop2": 5555}}],
        },
    )

    with MultiDeviceTestContext(devices_info) as context:
        proxy1 = context.get_device("test/device1/1")
        proxy2 = context.get_device("test/device2/2")
        assert proxy1.get_prop1() == "abcd"
        assert proxy2.get_prop2() == 5555


@pytest.fixture(
    # Per test we have the input config tuple, and then the expected exception type
    params=[
        # empty config
        [tuple(), IndexError],
        # missing/invalid keys
        [({"not-class": Device1, "devices": [{"name": "test/device1/1"}]},), KeyError],
        [({"class": Device1, "not-devices": [{"name": "test/device1/1"}]},), KeyError],
        [({"class": Device1, "devices": [{"not-name": "test/device1/1"}]},), KeyError],
        # duplicate class
        [
            (
                {"class": Device1, "devices": [{"name": "test/device1/1"}]},
                {"class": Device1, "devices": [{"name": "test/device1/2"}]},
            ),
            ValueError,
        ],
        # mixing old "classic" API and new high level API
        [
            (
                {"class": Device1, "devices": [{"name": "test/device1/1"}]},
                {
                    "class": (ClassicAPISimpleDeviceClass, ClassicAPISimpleDeviceImpl),
                    "devices": [{"name": "test/device1/2"}],
                },
            ),
            ValueError,
        ],
        # mixing green modes
        [
            (
                {"class": Device1Synchronous, "devices": [{"name": "test/device1/1"}]},
                {"class": Device1Gevent, "devices": [{"name": "test/device1/2"}]},
            ),
            ValueError,
        ],
    ]
)
def bad_multi_device_config(request):
    return request.param


def test_multi_bad_config_fails(bad_multi_device_config):
    bad_config, expected_error = bad_multi_device_config
    with pytest.raises(expected_error):
        with MultiDeviceTestContext(bad_config):
            pass


@pytest.fixture()
def memorized_attribute_test_device_factory():
    """
    Returns a test device factory that provides a test device with an
    attribute that is memorized or not, according to its boolean
    argument
    """
    def _factory(is_attribute_memorized):
        class _Device(Device):
            def init_device(self):
                self._attr_value = 0

            attr = attribute(
                access=AttrWriteType.READ_WRITE,
                memorized=is_attribute_memorized,
                hw_memorized=is_attribute_memorized
            )

            def read_attr(self):
                return self._attr_value

            def write_attr(self, value):
                self._attr_value = value

        return _Device
    return _factory


@pytest.mark.parametrize(
    "is_attribute_memorized, memorized_value, expected_value",
    [
        (False, None, 0),
        (False, "1", 0),
        (True, None, 0),
        (True, "1", 1),
    ]
)
def test_multi_with_memorized_attribute_values(
    memorized_attribute_test_device_factory,
    is_attribute_memorized,
    memorized_value,
    expected_value
):
    TestDevice = memorized_attribute_test_device_factory(is_attribute_memorized)

    device_info = {"name": "test/device1/1"}
    if memorized_value is not None:
        device_info["memorized"] = {"attr": memorized_value}

    devices_info = (
        {
            "class": TestDevice,
            "devices": [device_info]
        },
    )

    with MultiDeviceTestContext(devices_info) as context:
        proxy = context.get_device("test/device1/1")
        assert proxy.attr == expected_value


@pytest.mark.parametrize(
    "is_attribute_memorized, memorized_value, expected_value",
    [
        (False, None, 0),
        (False, 1, 0),
        (True, None, 0),
        (True, 1, 1),
    ]
)
def test_single_with_memorized_attribute_values(
    memorized_attribute_test_device_factory,
    is_attribute_memorized,
    memorized_value,
    expected_value
):
    TestDevice = memorized_attribute_test_device_factory(is_attribute_memorized)

    kwargs = {
        "memorized": {"attr": memorized_value}
    } if memorized_value is not None else {}

    with DeviceTestContext(TestDevice, **kwargs) as proxy:
        assert proxy.attr == expected_value
