#!/usr/bin/env python3
#
# client example: writing an attribute, also with simplified syntax

import sys
from tango import DeviceProxy, DevFailed, Except

dev_name = "sys/tg_test/1"
attr_name = "double_scalar"

# step 1 create the device proxy
try:
    dev = DeviceProxy(dev_name)
    print(f"proxy for {dev_name} created")
except DevFailed as ex:
    Except.print_exception(ex)
    sys.exit(1)

# step 2 write the attribute
try:
    dev.write_attribute(attr_name, 5.678)  # write the attribute directly
    print(f"write_attribute {attr_name!r} OK")
except DevFailed as ex:
    Except.print_exception(ex)
    print("failed to write attribute")
    sys.exit(1)

# use simplified syntax
try:
    dev.attr_name = 0.618  # WRONG! you are defining new attribute attr_name
    # in object dev with value 0.618
    dev.double_scalar = 0.619
    print(f"write_attribute SIMPLIFIED {attr_name!r} OK")
except DevFailed as ex:
    Except.print_exception(ex)
    print("failed to write attribute with simplified syntax")
    sys.exit(1)

"""
Typical output:

➜  training git:(develop) ✗ docker-compose exec cli /training/client/writing01.py
proxy for sys/tg_test/1 created
write_attribute 'double_scalar' OK
write_attribute SIMPLIFIED 'double_scalar' OK
"""
