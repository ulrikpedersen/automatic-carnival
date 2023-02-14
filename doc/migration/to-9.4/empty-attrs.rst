.. _to9.4_empty_attrs:

===================================
Empty spectrum and image attributes
===================================

.. warning::
     This is the most significant API change.  It could cause errors in existing
     Tango clients and devices.

Both server-side writing, and client-side reading could be affected.  There are differences
depending on an attribute's data type and its access type (read/read-write).  We go into detail
below.  The goal of the changes was to make usage more intuitive, and to provide a more
consistent API.

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: none

Writing - server side
---------------------

When an empty sequence is written to a spectrum or image attribute of type :class:`~tango.CmdArgType.DevString` the
write function used to receive a :obj:`None` value, but now it will receive an empty :obj:`list`.
For other types, the behaviour is unchanged - they were already receiving an empty :obj:`numpy.ndarray`.

Example device::

    from tango import AttrWriteType
    from tango.server import Device, attribute

    class Test(Device):
        str1d = attribute(dtype=(str,), max_dim_x=4, access=AttrWriteType.WRITE)
        int1d = attribute(dtype=(int,), max_dim_x=4, access=AttrWriteType.WRITE)
        str2d = attribute(dtype=((str,),), max_dim_x=4, max_dim_y=4, access=AttrWriteType.WRITE)
        int2d = attribute(dtype=((int,),), max_dim_x=4, max_dim_y=4, access=AttrWriteType.WRITE)

        def write_str1d(self, values):
            print(f"Writing str1d: values={values!r}, type={type(values)}")

        def write_int1d(self, values):
            print(f"Writing int1d: values={values!r}, type={type(values)}")

        def write_str2d(self, values):
            print(f"Writing str2d: values={values!r}, type={type(values)}")

        def write_int2d(self, values):
            print(f"Writing int2d: values={values!r}, type={type(values)}")

If a client writes empty data to the device::

    >>> dp = tango.DeviceProxy("tango://127.0.0.1:8888/test/nodb/test#dbase=no")
    >>> dp.str1d = []
    >>> dp.int1d = []
    >>> dp.str2d = [[]]
    >>> dp.int2d = [[]]

**Old**: The output from a v9.3.x PyTango device would be::

    Writing str1d: values=None, type=<class 'NoneType'>
    Writing int1d: values=array([], dtype=int64), type=<class 'numpy.ndarray'>
    Writing str2d: values=None, type=<class 'NoneType'>
    Writing int2d: values=array([], shape=(1, 0), dtype=int64), type=<class 'numpy.ndarray'>

**New**: The output from a v9.4.x PyTango device would be::

    Writing str1d: values=[], type=<class 'list'>
    Writing int1d: values=array([], dtype=int64), type=<class 'numpy.ndarray'>
    Writing str2d: values=[], type=<class 'list'>
    Writing int2d: values=array([], shape=(1, 0), dtype=int64), type=<class 'numpy.ndarray'>

Notice the change in values received for the ``str1d`` and ``str2d`` attributes.  If your existing devices have
special handling for :obj:`None`, then they may need to change.

Reading - client side
---------------------

When clients read from spectrum and image attributes with empty values, clients will now receive
an empty sequence instead of a :obj:`None` value.  For :class:`~tango.CmdArgType.DevString` and
:class:`~tango.CmdArgType.DevEnum` types, the *sequence* is a :obj:`tuple`, while other types
get a :obj:`numpy.ndarray` by default.

There is a subtle inconsistency in PyTango 9.3.x - empty **read-only** spectrum and image attributes always
returned :obj:`None` values, but **read-write** spectrum attributes *can* return empty sequences
instead of :obj:`None` values.  It depends on the set point (written value) stored for the attribute -
if it is non-empty, then the client gets an empty sequence.  This is shown in the examples below.
From PyTango 9.4.x, the behaviour is more consistent.

.. warning::
    Reading attributes of any type can still produce a :obj:`None` value if the
    quality is :class:`~tango.AttrQuality.ATTR_INVALID`.  Client-side code should
    always be prepared for this.  This behaviour is unchanged in PyTango 9.4.x
    (an exception being the fix for enumerated types using the high-level API, so that they
    also return :obj:`None`).

.. note::
    It is possible to get the data returned in other container types using the
    ``extract_as`` argument with :meth:`tango.DeviceProxy.read_attribute`.

This change affects values received via both the high-level API, and the low-level method it
uses, :meth:`tango.DeviceProxy.read_attribute`.  It also affects all related read methods:
:meth:`tango.DeviceProxy.read_attributes`, :meth:`tango.DeviceProxy.read_attribute_asynch`,
:meth:`tango.DeviceProxy.read_attribute_reply`, :meth:`tango.DeviceProxy.read_attributes_asynch`,
:meth:`tango.DeviceProxy.read_attributes_reply`.

The read attribute methods return data via :class:`tango.DeviceAttribute` objects.  These include
a ``value`` field for the read value, and a ``w_value`` field for the last set point (i.e., last value written).
Both of these fields are affected by this change.

Example device::

    from enum import IntEnum
    from tango import AttrWriteType
    from tango.server import Device, attribute

    class AnEnum(IntEnum):
       A = 0
       B = 1

    class Test(Device):
        @attribute(dtype=(str,), max_dim_x=4)
        def str1d(self):
            return []

        @attribute(dtype=(AnEnum,), max_dim_x=4)
        def enum1d(self):
            return []

        @attribute(dtype=(int,), max_dim_x=4, access=AttrWriteType.READ)
        def int1d(self):
            return []

        @attribute(dtype=(int,), max_dim_x=4, access=AttrWriteType.READ_WRITE)
        def int1d_rw(self):
            return []

        @int1d_rw.write
        def int1d_rw(self, values):
            print(f"Writing int1d_rw: values={values!r}, type={type(values)}")

        @attribute(dtype=((str,),), max_dim_x=4, max_dim_y=4)
        def str2d(self):
            return [[]]

        @attribute(dtype=((int,),), max_dim_x=4, max_dim_y=4)
        def int2d(self):
            return [[]]

High-level API reads
^^^^^^^^^^^^^^^^^^^^

**Old**: A PyTango 9.3.x client reads the empty data from the device using the high-level API::

    >>> dp = tango.DeviceProxy("tango://127.0.0.1:8888/test/nodb/test#dbase=no")

    >>> value = dp.str1d
    >>> value, type(value)
    (None, <class 'NoneType'>)

    >>> value = dp.enum1d  # broken in PyTango 9.3.x
    Traceback: ... ValueError: None is not a valid enum1d

    >>> value = dp.int1d  # read-only attribute
    >>> value, type(value)
    (None, <class 'NoneType'>)

    >>> value = dp.int1d_rw  # read-write attribute (default set point is [0])
    >>> value, type(value)
    (array([], dtype=int64), <class 'numpy.ndarray'>)
    >>> dp.int1d_rw = []  # write empty value (set point changed to empty)
    >>> value = dp.int1d_rw  # read again, after set point changed
    >>> value, type(value)
    (None, <class 'NoneType'>)

    >>> value = dp.str2d
    >>> value, type(value)
    (None, <class 'NoneType'>)

    >>> value = dp.int2d
    >>> value, type(value)
    (None, <class 'NoneType'>)

In the above example, notice that high-level API reads of enumerated spectrum types fail under PyTango 9.3.x.
Also see the difference in behaviour between read-only attributes like ``int1d`` and read-write attributes
like ``int1d_rw``.  Read-write spectrum attributes behave inconsistently with empty data prior to
PyTango 9.4.x.

**New**: A PyTango 9.4.x client reads the empty data from the device using the high-level API (device server
has been restarted after previous example)::

    >>> dp = tango.DeviceProxy("tango://127.0.0.1:8888/test/nodb/test#dbase=no")

    >>> value = dp.str1d
    >>> value, type(value)
    ((), <class 'tuple'>)

    >>> value = dp.enum1d
    >>> value, type(value)
    ((), <class 'tuple'>)

    >>> value = dp.int1d  # read-only attribute
    >>> value, type(value)
    (array([], dtype=int64), <class 'numpy.ndarray'>)

    >>> value = dp.int1d_rw  # read-write attribute (default set point is [0])
    >>> value, type(value)
    (array([], dtype=int64), <class 'numpy.ndarray'>)
    >>> dp.int1d_rw = []  # write empty value (set point changed to empty)
    >>> value = dp.int1d_rw  # read again, after set point changed
    >>> value, type(value)
    (array([], dtype=int64), <class 'numpy.ndarray'>)

    >>> value = dp.str2d
    >>> value, type(value)
    ((), <class 'tuple'>)

    >>> value = dp.int2d
    >>> value, type(value)
    (array([], shape=(1, 0), dtype=int64), <class 'numpy.ndarray'>)

Low-level API reads
^^^^^^^^^^^^^^^^^^^

In these examples, focus on the ``value`` field (the value read back), which changes as above, and the
``type`` field.  Using PyTango 9.3.x, the ``type`` is number 100, which indicates an unknown type, while
with PyTango 9.4.0, the type stays correct even when the value is empty.  The change in ``type`` is
something updated in `cppTango`_ 9.4.1.

 **Old**: A PyTango 9.3.x client reads the empty data from the device using the low-level API::

    >>> dp = tango.DeviceProxy("tango://127.0.0.1:8888/test/nodb/test#dbase=no")

    >>> print(dp.read_attribute("str1d"))
    DeviceAttribute[
    data_format = tango._tango.AttrDataFormat.SPECTRUM
          dim_x = 0
          dim_y = 0
     has_failed = False
       is_empty = True
           name = 'str1d'
        nb_read = 0
     nb_written = 0
        quality = tango._tango.AttrQuality.ATTR_VALID
    r_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
           time = TimeVal(tv_nsec = 0, tv_sec = 1676068470, tv_usec = 650091)
           type = tango._tango.CmdArgType(100)
          value = None
        w_dim_x = 0
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
        w_value = None]

    >>> print(dp.read_attribute("int1d"))
    DeviceAttribute[
    data_format = tango._tango.AttrDataFormat.SPECTRUM
          dim_x = 0
          dim_y = 0
     has_failed = False
       is_empty = False
           name = 'int1d'
        nb_read = 0
     nb_written = 1
        quality = tango._tango.AttrQuality.ATTR_VALID
    r_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
           time = TimeVal(tv_nsec = 0, tv_sec = 1676068478, tv_usec = 597279)
           type = tango._tango.CmdArgType.DevLong64
          value = array([], dtype=int64)
        w_dim_x = 1
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 1, dim_y = 0)
        w_value = array([0])]

    >>> print(dp.read_attribute("str2d"))
    DeviceAttribute[
    data_format = tango._tango.AttrDataFormat.IMAGE
          dim_x = 0
          dim_y = 1
     has_failed = False
       is_empty = True
           name = 'str2d'
        nb_read = 0
     nb_written = 0
        quality = tango._tango.AttrQuality.ATTR_VALID
    r_dimension = AttributeDimension(dim_x = 0, dim_y = 1)
           time = TimeVal(tv_nsec = 0, tv_sec = 1676068484, tv_usec = 896408)
           type = tango._tango.CmdArgType(100)
          value = None
        w_dim_x = 0
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
        w_value = None]

    >>> print(dp.read_attribute("int2d"))
    DeviceAttribute[
    data_format = tango._tango.AttrDataFormat.IMAGE
          dim_x = 0
          dim_y = 1
     has_failed = False
       is_empty = True
           name = 'int2d'
        nb_read = 0
     nb_written = 0
        quality = tango._tango.AttrQuality.ATTR_VALID
    r_dimension = AttributeDimension(dim_x = 0, dim_y = 1)
           time = TimeVal(tv_nsec = 0, tv_sec = 1676068489, tv_usec = 330193)
           type = tango._tango.CmdArgType(100)
          value = None
        w_dim_x = 0
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
        w_value = None]


**New**: A PyTango 9.4.x client reads the empty data from the device using the low-level API::

    >>> dp = tango.DeviceProxy("tango://127.0.0.1:8888/test/nodb/test#dbase=no")

    >>> print(dp.read_attribute("str1d"))
    DeviceAttribute[
    data_format = tango._tango.AttrDataFormat.SPECTRUM
          dim_x = 0
          dim_y = 0
     has_failed = False
       is_empty = True
           name = 'str1d'
        nb_read = 0
     nb_written = 0
        quality = tango._tango.AttrQuality.ATTR_VALID
    r_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
           time = TimeVal(tv_nsec = 0, tv_sec = 1676068550, tv_usec = 333749)
           type = tango._tango.CmdArgType.DevString
          value = ()
        w_dim_x = 0
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
        w_value = ()]

    >>> print(dp.read_attribute("int1d"))
    DeviceAttribute[
    data_format = tango._tango.AttrDataFormat.SPECTRUM
          dim_x = 0
          dim_y = 0
     has_failed = False
       is_empty = False
           name = 'int1d'
        nb_read = 0
     nb_written = 1
        quality = tango._tango.AttrQuality.ATTR_VALID
    r_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
           time = TimeVal(tv_nsec = 0, tv_sec = 1676068554, tv_usec = 243413)
           type = tango._tango.CmdArgType.DevLong64
          value = array([], dtype=int64)
        w_dim_x = 1
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 1, dim_y = 0)
        w_value = array([0])]

    >>> print(dp.read_attribute("str2d"))
    DeviceAttribute[
    data_format = tango._tango.AttrDataFormat.IMAGE
          dim_x = 0
          dim_y = 1
     has_failed = False
       is_empty = True
           name = 'str2d'
        nb_read = 0
     nb_written = 0
        quality = tango._tango.AttrQuality.ATTR_VALID
    r_dimension = AttributeDimension(dim_x = 0, dim_y = 1)
           time = TimeVal(tv_nsec = 0, tv_sec = 1676068558, tv_usec = 191433)
           type = tango._tango.CmdArgType.DevString
          value = ()
        w_dim_x = 0
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
        w_value = ()]

    >>> print(dp.read_attribute("int2d"))
    DeviceAttribute[
    data_format = tango._tango.AttrDataFormat.IMAGE
          dim_x = 0
          dim_y = 1
     has_failed = False
       is_empty = True
           name = 'int2d'
        nb_read = 0
     nb_written = 0
        quality = tango._tango.AttrQuality.ATTR_VALID
    r_dimension = AttributeDimension(dim_x = 0, dim_y = 1)
           time = TimeVal(tv_nsec = 0, tv_sec = 1676068562, tv_usec = 50107)
           type = tango._tango.CmdArgType.DevLong64
          value = array([], shape=(1, 0), dtype=int64)
        w_dim_x = 0
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
        w_value = array([], shape=(0, 0), dtype=int64)]

Low-level API reads of set point (write value)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In these examples, focus on the ``w_value`` field which is the set point, or last written value.

 **Old**: A PyTango 9.3.x client changes the set point and reads using the low-level API::

    >>> dp = tango.DeviceProxy("tango://127.0.0.1:8888/test/nodb/test#dbase=no")

    >>> dp.int1d_rw = [1, 2]
    >>> print(dp.read_attribute("int1d_rw"))
    DeviceAttribute[
        ...
           type = tango._tango.CmdArgType.DevLong64
        w_dim_x = 2
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 2, dim_y = 0)
        w_value = array([1, 2])]

    >>> dp.int1d_rw = []
    >>> print(dp.read_attribute("int1d_rw"))
    DeviceAttribute[
        ...
           type = tango._tango.CmdArgType(100)
        w_dim_x = 0
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
        w_value = None]

 **New**: A PyTango 9.4.x client changes the set point and reads using the low-level API::

    >>> dp = tango.DeviceProxy("tango://127.0.0.1:8888/test/nodb/test#dbase=no")

    >>> dp.int1d_rw = [1, 2]
    >>> print(dp.read_attribute("int1d_rw"))
    DeviceAttribute[
        ...
           type = tango._tango.CmdArgType.DevLong64
        w_dim_x = 2
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 2, dim_y = 0)
        w_value = array([1, 2])]

    >>> dp.int1d_rw = []
    >>> print(dp.read_attribute("int1d_rw"))
    DeviceAttribute[
        ...
           type = tango._tango.CmdArgType.DevLong64
        w_dim_x = 0
        w_dim_y = 0
    w_dimension = AttributeDimension(dim_x = 0, dim_y = 0)
        w_value = array([], dtype=int64)]
