# Imports

import time
from functools import partial
from threading import Thread

import pytest
from io import StringIO

from tango import (
    EventType,
    GreenMode,
    DeviceProxy,
    AttrQuality,
    EnsureOmniThread,
    is_omni_thread,
)
from tango.server import Device
from tango.server import command, attribute
from tango.test_utils import DeviceTestContext
from tango.utils import EventCallback

from tango.gevent import DeviceProxy as gevent_DeviceProxy
from tango.futures import DeviceProxy as futures_DeviceProxy
from tango.asyncio import DeviceProxy as asyncio_DeviceProxy

MAX_RETRIES = 200
DELAY_PER_RETRY = 0.05

# Helpers

device_proxy_map = {
    GreenMode.Synchronous: DeviceProxy,
    GreenMode.Futures: futures_DeviceProxy,
    GreenMode.Asyncio: partial(asyncio_DeviceProxy, wait=True),
    GreenMode.Gevent: gevent_DeviceProxy,
}


# Test device


class EventDevice(Device):
    def init_device(self):
        self.set_change_event("attr", True, False)
        self.set_data_ready_event("attr", True)

    @attribute
    def attr(self):
        return 0.0

    @command
    def send_change_event(self):
        self.push_change_event("attr", 1.0)

    @command
    def send_data_ready_event(self):
        self.push_data_ready_event("attr", 2)

    @command
    def send_change_event_with_timestamp(self):
        self.push_change_event("attr", 2.0, 3.0, AttrQuality.ATTR_WARNING)

    @command(dtype_in=str)
    def add_dyn_attr(self, name):
        attr = attribute(name=name, dtype="float", fget=self.read)
        self.add_attribute(attr)

    @command(dtype_in=str)
    def delete_dyn_attr(self, name):
        self._remove_attribute(name)

    def read(self, attr):
        attr.set_value(1.23)


# Device fixture


@pytest.fixture(
    params=[
        GreenMode.Synchronous,
        GreenMode.Futures,
        GreenMode.Asyncio,
        GreenMode.Gevent,
    ],
    scope="module",
)
def event_device(request):
    green_mode = request.param
    context = DeviceTestContext(EventDevice, host="127.0.0.1", process=True)
    with context:
        yield device_proxy_map[green_mode](context.get_device_access())


# Tests


def test_subscribe_change_event(event_device):
    results_change_event = []

    def callback_change(evt):
        results_change_event.append(evt.attr_value.value)

    # Subscribe to change event
    eid_change = event_device.subscribe_event(
        "attr", EventType.CHANGE_EVENT, callback_change, wait=True
    )
    assert eid_change == 1

    # Trigger an event
    event_device.command_inout("send_change_event", wait=True)
    # Wait for tango event
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(results_change_event) > 1:
            break
        time.sleep(DELAY_PER_RETRY)
    if retry_count + 1 >= MAX_RETRIES:
        timeout_seconds = retry_count * DELAY_PER_RETRY
        pytest.fail(
            f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. Occasionally happens, probably due to CI test runtime environment"
        )
    # Test the event values
    assert results_change_event == [0.0, 1.0]
    # Unsubscribe
    event_device.unsubscribe_event(eid_change)


def test_subscribe_data_ready_event(event_device):
    results_data_ready_event = []

    def callback_data_ready(evt):
        results_data_ready_event.append(evt.ctr)

    # Subscribe to data ready event
    eid_data_ready = event_device.subscribe_event(
        "attr", EventType.DATA_READY_EVENT, callback_data_ready, wait=True
    )
    assert eid_data_ready == 1
    # Trigger an event
    event_device.command_inout("send_data_ready_event", wait=True)
    # Wait for tango event
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(results_data_ready_event):
            break
        time.sleep(DELAY_PER_RETRY)
    if retry_count + 1 >= MAX_RETRIES:
        timeout_seconds = retry_count * DELAY_PER_RETRY
        pytest.fail(
            f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. Occasionally happens, probably due to CI test runtime environment"
        )
    # Test the event values
    assert results_data_ready_event == [2]
    # Unsubscribe
    event_device.unsubscribe_event(eid_data_ready)


def test_subscribe_interface_event(event_device):
    results = []

    def callback(evt):
        results.append(evt)

    # Subscribe
    eid = event_device.subscribe_event(
        "attr", EventType.INTERFACE_CHANGE_EVENT, callback, wait=True
    )
    assert eid == 1
    # Trigger an event
    event_device.command_inout("add_dyn_attr", "bla", wait=True)
    event_device.read_attribute("bla", wait=True) == 1.23
    # Wait for tango event
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(results) > 1:
            break
        time.sleep(DELAY_PER_RETRY)
    if retry_count + 1 >= MAX_RETRIES:
        timeout_seconds = retry_count * DELAY_PER_RETRY
        pytest.fail(
            f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. Occasionally happens, probably due to CI test runtime environment"
        )
    event_device.command_inout("delete_dyn_attr", "bla", wait=True)
    # Wait for tango event
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(results) > 2:
            break
        time.sleep(DELAY_PER_RETRY)
    if retry_count + 1 >= MAX_RETRIES:
        timeout_seconds = retry_count * DELAY_PER_RETRY
        pytest.fail(
            f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. Occasionally happens, probably due to CI test runtime environment"
        )
    # Test the first event value
    assert {cmd.cmd_name for cmd in results[0].cmd_list} == {
        "Init",
        "State",
        "Status",
        "add_dyn_attr",
        "delete_dyn_attr",
        "send_change_event",
        "send_data_ready_event",
        "send_change_event_with_timestamp",
    }
    assert {att.name for att in results[0].att_list} == {"attr", "State", "Status"}
    # Test the second event value
    assert {cmd.cmd_name for cmd in results[1].cmd_list} == {
        "Init",
        "State",
        "Status",
        "add_dyn_attr",
        "delete_dyn_attr",
        "send_change_event",
        "send_data_ready_event",
        "send_change_event_with_timestamp",
    }
    assert {att.name for att in results[1].att_list} == {
        "attr",
        "State",
        "Status",
        "bla",
    }
    # Test the third event value
    assert {cmd.cmd_name for cmd in results[2].cmd_list} == {
        "Init",
        "State",
        "Status",
        "add_dyn_attr",
        "delete_dyn_attr",
        "send_change_event",
        "send_data_ready_event",
        "send_change_event_with_timestamp",
    }
    assert {att.name for att in results[2].att_list} == {"attr", "State", "Status"}
    # Unsubscribe
    event_device.unsubscribe_event(eid)


def test_push_event_with_timestamp(event_device):
    string = StringIO()
    ec = EventCallback(fd=string)
    # Subscribe
    eid = event_device.subscribe_event("attr", EventType.CHANGE_EVENT, ec, wait=True)
    assert eid == 1
    # Trigger an event
    event_device.command_inout("send_change_event_with_timestamp", wait=True)
    # Wait for tango event
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(ec.get_events()) > 1:
            break
        time.sleep(DELAY_PER_RETRY)
    if retry_count + 1 >= MAX_RETRIES:
        timeout_seconds = retry_count * DELAY_PER_RETRY
        pytest.fail(
            f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. Occasionally happens, probably due to CI test runtime environment"
        )
    # Test the event values and timestamp
    results = [evt.attr_value.value for evt in ec.get_events()]
    assert results == [0.0, 2.0]
    assert ec.get_events()[-1].attr_value.time.totime() == 3.0
    # Check string
    line1 = "TEST/NODB/EVENTDEVICE ATTR#DBASE=NO CHANGE [ATTR_VALID] 0.0"
    line2 = "TEST/NODB/EVENTDEVICE ATTR#DBASE=NO CHANGE [ATTR_WARNING] 2.0"
    assert line1 in string.getvalue()
    assert line2 in string.getvalue()
    # Unsubscribe
    event_device.unsubscribe_event(eid)


def test_main_thread_is_omni_thread():
    assert is_omni_thread()


def test_ensure_omni_thread_main_thread_is_omni_thread():
    with EnsureOmniThread():
        assert is_omni_thread()


def test_user_thread_is_not_omni_thread():
    thread_is_omni = dict(result=None)  # use a dict so thread can modify it

    def thread_func():
        thread_is_omni["result"] = is_omni_thread()

    thread = Thread(target=thread_func)
    thread.start()
    thread.join()
    assert thread_is_omni["result"] is False


def test_ensure_omni_thread_user_thread_is_omni_thread():
    thread_is_omni = dict(result=None)  # use a dict so thread can modify it

    def thread_func():
        with EnsureOmniThread():
            thread_is_omni["result"] = is_omni_thread()

    thread = Thread(target=thread_func)
    thread.start()
    thread.join()
    assert thread_is_omni["result"] is True


def test_subscribe_change_event_from_user_thread(event_device):
    results = []

    def callback(evt):
        results.append(evt.attr_value.value)

    def thread_func():
        with EnsureOmniThread():
            eid = event_device.subscribe_event(
                "attr", EventType.CHANGE_EVENT, callback, wait=True
            )
            while running:
                time.sleep(DELAY_PER_RETRY)
            event_device.unsubscribe_event(eid)

    # Start the thread
    thread = Thread(target=thread_func)
    running = True
    thread.start()
    # Wait for tango events
    for retry_count in range(MAX_RETRIES):
        event_device.read_attribute("state", wait=True)
        if len(results) == 1:
            # Trigger an event (1 result means thread has completed subscription,
            # as that results in an initial callback)
            event_device.command_inout("send_change_event", wait=True)
        elif len(results) > 1:
            # At least 2 events means an event was received after subscription
            break
        time.sleep(DELAY_PER_RETRY)
    # Stop the thread
    running = False
    thread.join()
    if retry_count + 1 >= MAX_RETRIES:
        timeout_seconds = retry_count * DELAY_PER_RETRY
        pytest.fail(
            f"Timeout, waiting for event, after {timeout_seconds}sec over {MAX_RETRIES} retries. Occasionally happens, probably due to CI test runtime environment"
        )
    # Test the event values
    assert results == [0.0, 1.0]
