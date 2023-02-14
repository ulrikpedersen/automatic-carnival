.. _pytango-news:

###########
What's new?
###########

The sections below will give you the most relevant news from the PyTango releases.
For help moving to a new release, or for the complete list of changes, see the
following links:

.. toctree::
    :maxdepth: 1

    migration/index
    History of changes <revision>


****************************
What's new in PyTango 9.4.0?
****************************

Date: 2023-02-15

Type: major release

Changed
=======

- PyTango requires at least `cppTango`_ 9.4.1.  See the :ref:`migration guide <to9.4_deps_install>`.
- Breaking change to the API when using empty spectrum and image attributes.  Clients reading an empty
  attribute will get an empty sequence (list/tuple/numpy array) instead of a :obj:`None` value.  Similarly,
  devices that have an empty sequence written will receive that in the write method instead of a :obj:`None`
  value.  See the migration guide on :ref:`empty attributes <to9.4_empty_attrs>` and
  :ref:`extract as <to9.4_extract_as>`.
- Python dependencies:  `numpy`_ is no longer optional - it is required.
  Other new requirements are `packaging <https://pypi.org/project/packaging>`_ and
  `psutil <https://pypi.org/project/psutil>`_.
- Binary wheels for more platforms, including Linux, are available on `PyPI`_.  Fast installation without compiling and
  figuring out all the dependencies!
- The dependencies packaged with the binary PyPI wheels are as follows:
    - Linux:
        - cpptango: 9.4.1
        - omniorb: 4.2.4
        - libzmq: v4.3.4
        - cppzmq: v4.7.1
        - libjpeg-turbo: 2.0.9
        - tango-idl: 5.1.1
        - boost: 1.80.0 (with patch for Python 3.11 support)
    - Windows:
        - cpptango: 9.4.1
        - omniorb: 4.2.5
        - libzmq: v4.0.5-2
        - cppzmq: v4.7.1
        - libjpeg-turbo: 2.0.3
        - tango-idl: 5.1.2
        - boost: 1.73.0
- When using the ``--port`` commandline option without ``--host``, the ``ORBendpoint`` for ``gio::tcp`` passed
  to cppTango will use ``"0.0.0.0"`` as the host instead of an empty string.  This is to workaround a
  `regression with cppTango 9.4.1 <https://gitlab.com/tango-controls/cppTango/-/issues/1055>`_.
  Note that if the ``--ORBendPoint`` commandline option is specified directly, it will not be modified.
  This will lead to a crash if an empty host is used, e.g., ``--ORBendPoint giop:tcp::1234``.

Added
=====

- User methods for attribute access (read/write/is allowed), and for commands (execute/is allowed)
  can be plain functions.  They don't need to be methods on the device class anymore.  There was some
  inconsistency with this previously, but now it is the same for static and dynamic attributes,
  and for commands.  Static and dynamic commands can also take an ``fisallowed`` keyword argument.
  See the :ref:`migration guide <to9.4_non_bound_user_funcs>`.
- Device methods for reading and writing dynamic attributes can use the high-level API instead of getting
  and setting values inside :class:`~tango.Attr` objects.  See the :ref:`migration guide <to9.4_hl_dynamic>`.
- High-level API support for accessing and creating DevEnum spectrum and image attributes.
  See the :ref:`migration guide <to9.4_hl_dev_enum>`.
- Developers can optionally allow Python attributes to be added to a :class:`~tango.DeviceProxy` instance
  by calling :meth:`~tango.DeviceProxy.unfreeze_dynamic_interface`.  The default behaviour is still
  to raise an exception when accessing unknown attributes.
  See the :ref:`migration guide <to9.4_optional_proxy_attrs>`.
- Attribute decorators have additional methods: :meth:`~tango.server.attribute.getter`,
  :meth:`~tango.server.attribute.read` and :meth:`~tango.server.attribute.is_allowed`.
  See the :ref:`migration guide <to9.4_attr_decorators>`.
- Python 3.11 support.
- MacOS support.  This is easiest installing from `Conda-forge`_.  Compiling locally is not recommended.
  See :ref:`Getting started <getting-started>`.
- Integrated development environment (IDE) autocompletion for methods inherited from
  :class:`tango.server.Device` and :class:`tango.LatestDeviceImpl`.  Attributes from the full class
  hierarchy are now more easily accessible directly in your editor.

Fixed
=====

- Log stream calls that include literal ``%`` symbols but no args now work properly without
  raising an exception.  E.g., ``self.debug_stream("I want to log a %s symbol")``.
  See the :ref:`migration guide <to9.4_logging_percent_sym>`.
- Writing a :obj:`numpy.array` to a spectrum attribute of type :obj:`str` no longer crashes.
- Reading an enum attribute with :class:`~tango.AttrQuality.ATTR_INVALID` quality via the high-level API
  now returns :obj:`None` instead of crashing.  This behaviour is consistent with the other data types.

Removed
=======

- Support for Python 2.7 and Python 3.5.
- The option to install PyTango without `numpy`_.
