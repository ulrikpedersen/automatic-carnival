#!/usr/bin/env python3
#
# client example: reading an attribute, also with simplified (high-level) syntax

import sys
from tango import DeviceProxy, DevFailed, Except

dev_name = "sys/tg_test/1"
attr_name = "double_scalar"

# step 1 - create the device proxy
try:
    dev = DeviceProxy(dev_name)
    print(f"proxy for {dev_name} created")
except DevFailed as ex:
    Except.print_exception(ex)
    sys.exit(1)

# step 2 - read the attribute
try:
    da = dev.read_attribute(attr_name)  # read the attribute
    value = da.value
except DevFailed as ex:
    Except.print_exception(ex)
    print("failed to read attribute")
    sys.exit(1)

print(f"{dev_name}/{attr_name} value: {value}")

# step 3 - use simplified interface
try:
    value2 = dev.double_scalar
except DevFailed as ex:
    Except.print_exception(ex)
    print("failed to read double_scalar")
    sys.exit(1)

print(f"{dev_name}/{attr_name} value2: {value2}")

"""
Typical output:

➜  training git:(develop) ✗ docker-compose exec cli python /training/client/reading01.py
proxy for sys/tg_test/1 created
sys/tg_test/1/double_scalar value: -184.15039639576005
sys/tg_test/1/double_scalar value2: -187.22596334769938
"""
