"""
Example used for debugging during 4th Tango Kernel Webinar.

https://www.tango-controls.org/community/news/2021/06/10/4th-tango-kernel-webinar-pytango/
"""

from tango import AttrQuality, AttrWriteType, GreenMode
from tango.server import Device, attribute
from tango.test_utils import DeviceTestContext, assert_close


def test_read_attribute():
    class TestDevice(Device):
        _voltage = 0.0

        @attribute(dtype=float, access=AttrWriteType.READ_WRITE)
        def voltage(self):
            return self._voltage

        @voltage.write
        def voltage(self, value):
            self._voltage = value

    with DeviceTestContext(TestDevice) as proxy:
        # low-level API read
        low_level_api_reading = proxy.read_attribute("voltage")
        assert_close(low_level_api_reading.value, 0.0)
        assert low_level_api_reading.quality is AttrQuality.ATTR_VALID

        # high-level API read
        high_level_api_read_value = proxy.voltage
        assert_close(high_level_api_read_value, 0.0)

        # low-level API write
        value = 24.0
        proxy.write_attribute("voltage", value)
        high_level_api_read_value = proxy.voltage
        assert_close(high_level_api_read_value, value)

        # high-level API write
        value = 48.0
        proxy.voltage = value
        high_level_api_read_value = proxy.voltage
        assert_close(high_level_api_read_value, value)


def test_read_attribute_full():
    class TestDevice(Device):
        green_mode = GreenMode.Synchronous

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._voltage = 0.0

        def init_device(self):
            super().init_device()
            print("init_device!")

        def read_attr_hardware(self, attr_list):
            print(f"read_attr_hardware for {str(attr_list)}")

        def write_attr_hardware(self, attr_list):
            print(f"write_attr_hardware for {str(attr_list)}")

        def always_executed_hook(self):
            print("always_executed_hook")

        @attribute(dtype=float, access=AttrWriteType.READ_WRITE)
        def voltage(self):
            return self._voltage

        @voltage.write
        def voltage(self, value):
            self._voltage = value

        def is_voltage_allowed(self, req_type):
            return True

        @attribute(dtype=float, access=AttrWriteType.READ)
        def current(self):
            return self._voltage / 2.0

    with DeviceTestContext(TestDevice, timeout=600, process=False) as proxy:
        # low-level API read single
        low_level_api_reading = proxy.read_attribute("voltage")
        assert_close(low_level_api_reading.value, 0.0)
        assert low_level_api_reading.quality is AttrQuality.ATTR_VALID

        # low-level API read multiple
        low_level_api_readings = proxy.read_attributes(["voltage", "current"])
        assert_close(low_level_api_readings[0].value, 0.0)
        assert low_level_api_readings[0].quality is AttrQuality.ATTR_VALID

        # high-level API read
        high_level_api_read_value = proxy.voltage
        assert_close(high_level_api_read_value, 0.0)

        # low-level API write
        value = 24.0
        proxy.write_attribute("voltage", value)
        high_level_api_read_value = proxy.voltage
        assert_close(high_level_api_read_value, value)

        # high-level API write
        value = 48.0
        proxy.voltage = value
        high_level_api_read_value = proxy.voltage
        assert_close(high_level_api_read_value, value)
