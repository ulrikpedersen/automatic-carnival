.. _to9.4_extract_as:

================================================================
Changes to extract_as when reading spectrum and image attributes
================================================================

When a client reads a spectrum or image attribute, the default behaviour is to return
the data in a :obj:`tuple` for strings and enumerated types, or a :obj:`numpy.ndarray`
for other types.  This can be changed using the ``extract_as`` argument passed to
:meth:`tango.DeviceProxy.read_attribute` (and similar methods).

Changes in 9.4.x affect the results when using :obj:`tango.ExtractAs.Bytes`,
:obj:`tango.ExtractAs.ByteArray`, and :obj:`tango.ExtractAs.String`.  The
methods are a little unusual as they try to provide the raw data values as bytes
or strings, rather than the original data type.

Keep value and w_value separate
===============================

Prior to 9.4.x, the data in the :class:`tango.DeviceAttribute` ``value`` and ``w_value``
fields would be concatenated (respectively) and returned in the ``value`` field.  For
a read-only attributes this was reasonable, but not for read-write attributes.

In 9.4.x, the data in the two fields remains independent.

Disabled types
==============

Extracting data to bytes and strings has been disabled for attributes of type
:class:`~tango.CmdArgType.DevString` because concatenating the data from all the strings
is not clearly defined.  E.g., should null termination characters be included for each
item?  This may be re-enabled in future, once the solution becomes clear.

Problems with UTF-8 encoding
============================

For arbitrary binary data, it is not always possible to convert it into a Python :obj:`str`.
The conversion from bytes will attempt to decode the data assuming UTF-8 encoding,
so many byte sequences are invalid.  This is not a new problem in version 9.4.x, but will
be noticeable if moving from Python 2 to Python 3.  For arbitrary data, including numeric types,
rather extract to :obj:`bytes` or :obj:`bytearray`.
