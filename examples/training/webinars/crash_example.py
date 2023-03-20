"""
This crashes under PyTango 9.3.3 and cppTango 9.3.4.  Possibly other versions too.
"""
from tango.test_context import DeviceTestContext
import tango
import time


class Device1(tango.server.Device):
    pass


with DeviceTestContext(Device1, process=True) as proxy:
    cb = tango.utils.EventCallback()
    eid = proxy.subscribe_event("state", tango.EventType.ATTR_CONF_EVENT, cb)
    sleep = 12  # sleep >~11 ==> SIGSEGV ; sleep<10 ==> exit OK
    for i in range(sleep):
        time.sleep(1)
        print(i + 1, end=", ")
    print("\nbefore unsubscribe")
    proxy.unsubscribe_event(eid)  # <-- SEGFAULT here
    print("after unsubscribe")
