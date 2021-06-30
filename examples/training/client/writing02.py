#!/usr/bin/env python3
#
# client example: writing an array
import sys
from tango import DeviceProxy, DevFailed, Except

dev_name = "sys/tg_test/1"
attr_name = "double_spectrum"

# step 1 create the device proxy
try:
    dev = DeviceProxy(dev_name)
    print(f"proxy for {dev_name} created")
except DevFailed as ex:
    Except.print_exception(ex)
    sys.exit(1)

# prepare value list
values = []
for i in range(0, 255, 1):
    values.append(i / 10.0)
try:
    dev.write_attribute(attr_name, values)
    print(f"write_attribute {attr_name!r} OK")
except DevFailed as ex:
    Except.print_exception(ex)
    sys.exit(1)

# use numpy.ndarray - must import numpy
import numpy

arr_values = numpy.empty(255)
for i in range(0, 255, 1):
    arr_values[i] = i / 20.0
try:
    dev.write_attribute(attr_name, arr_values)
    dev.float_spectrum = arr_values  # simpler syntax on another attribute
    print(f"write_attribute {attr_name!r} with numpy.ndarray OK")
except DevFailed as ex:
    Except.print_exception(ex)
    sys.exit(1)

"""
Typical output:

➜  training git:(develop) ✗ docker-compose exec cli /training/client/writing02.py
proxy for sys/tg_test/1 created
write_attribute 'double_spectrum' OK
write_attribute 'double_spectrum' with numpy.ndarray OK
"""
