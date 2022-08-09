"""
A module defining pytest fixtures for testing with MultiDeviceTestContext
Requires pytest and pytest-mock
"""

from collections import defaultdict
import pytest
import socket
import tango
from tango.test_context import MultiDeviceTestContext, get_host_ip


@pytest.fixture(scope="module")
def devices_info(request):
    yield getattr(request.module, "devices_info")

    
@pytest.fixture(scope="function")
def tango_context(mocker, devices_info):
    """
    Creates and returns a TANGO MultiDeviceTestContext object, with
    tango.DeviceProxy patched to work around a name-resolving issue.
    """
    context_manager = MultiDeviceTestContext(devices_info, process=True)
    _DeviceProxy = tango.DeviceProxy
    mocker.patch(
        'tango.DeviceProxy',
        wraps=lambda fqdn, *args, **kwargs: _DeviceProxy(
            context_manager.get_device_access(fqdn), *args, **kwargs
        )
    )
    with context_manager as context:
        yield context
