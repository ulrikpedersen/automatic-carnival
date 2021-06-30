#!/usr/bin/env python3
#
# client example: reading an attribute, also with simplified syntax

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
    da = dev.read_attribute(attr_name)
    print(f"attribute.name: {da.name}")
    print(f"attribute.timestamp: {da.get_date()}")
    print(f"attribute.quality: {da.quality}")
    print(f"attribute.dim_x: {da.dim_x}")
    print(f"attribute.type: {da.type}")
    print(f"attribute.value: {da.value}")
except DevFailed as ex:
    Except.print_exception(ex)
    print("failed to read attribute")
    sys.exit(1)  # simplistic error handling

# set a value with Jive and check the result here
try:
    # read the attribute again
    da = dev.read_attribute(attr_name)
    print(f"attribute.value    (reading): {da.value}")
    print(f"attribute.w_value  (setting): {da.w_value}")
except DevFailed as ex:
    Except.print_exception(ex)
    print("failed to read attribute")
    sys.exit(1)

"""
Typical output:

➜  training git:(develop) ✗ docker-compose exec cli /training/client/reading02.py
proxy for sys/tg_test/1 created
attribute.name: double_scalar
attribute.timestamp: 2021-06-30 20:07:50.801692
attribute.quality: ATTR_VALID
attribute.dim_x: 1
attribute.type: DevDouble
attribute.value: -226.03415499895206
attribute.value    (reading): -226.03415499895206
attribute.w_value  (setting): 0.0
"""
