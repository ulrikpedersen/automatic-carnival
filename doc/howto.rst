.. currentmodule:: tango

.. highlight:: python
   :linenothreshold: 10

.. _pytango-howto:

======
How to
======

This is a small list of how-tos specific to PyTango. A more general Tango how-to
list can be found `here <http://www.tango-controls.org/resources/howto>`_.

How to contribute
-----------------

Everyone is welcome to contribute to PyTango project.
If you don't feel comfortable with writing core PyTango we are looking for contributors to documentation or/and tests.

It refers to the next section, see :ref:`how-to-contribute`.


Check the default TANGO host
----------------------------

The default TANGO host can be defined using the environment variable
:envvar:`TANGO_HOST` or in a `tangorc` file
(see `Tango environment variables <https://tango-controls.readthedocs.io/en/latest/development/advanced/reference.html#environment-variables>`_
for complete information)

To check what is the current value that TANGO uses for the default configuration
simple do::

    >>> import tango
    >>> tango.ApiUtil.get_env_var("TANGO_HOST")
    'homer.simpson.com:10000'

Check TANGO version
-------------------

There are two library versions you might be interested in checking:
The PyTango version::

    >>> import tango
    >>> tango.__version__
    '9.4.0'
    >>> tango.__version_info__
    (9, 4, 0)

and the Tango C++ library version that PyTango was compiled with::

    >>> import tango
    >>> tango.constants.TgLibVers
    '9.4.1'


Start server from command line
------------------------------

To start server from the command line execute the following command:

.. sourcecode:: console

    $ python <server_file>.py <instance_name>
    Ready to accept request

To run server without database use option -nodb.

.. sourcecode:: console

    $ python <server_file>.py <instance_name> -nodb -port 10000
    Ready to accept request

Note, that to start server in this mode you should provide a port with either \-\-post, or \-\-ORBendPoint option

Additionally, you can use the following options:

    -h, -?, \-\-help : show usage help

    -v, \-\-verbose: set the trace level. Can be user in count way: -vvvv set level to 4 or --verbose --verbose set to 2

    -vN: directly set the trace level to N, e.g. -v3 - set level to 3

    \-\-file <file_name>: start a device server using an ASCII file instead of the Tango database

    \-\-host <host_name>: force the host from which server accept requests

    \-\-port <port>: force the port on which the device server listens

    \-\-nodb: run server without DB

    \-\-dlist <dev1,dev2,etc>: the device name list. This option is supported only with the -nodb option

    \-\-ORBendPoint giop:tcp:<host>:<port>: Specifying the host from which server accept requests and port on which the device server listens.

Note: any ORB option can be provided if it starts with -ORB<option>

Additionally in Windows the following option can be used:

    -i: install the service

    -s: install the service and choose the automatic startup mode

    -u: uninstall the service

    \-\-dbg: run in console mode to debug service. The service must have been installed prior to use it.

Note: all long-options can be provided in non-POSIX format: -port or \-\-port etc...

Report a bug
------------

Bugs can be reported as issues in `PyTango GitLab <https://gitlab.com/tango-controls/pytango/issues>`_.

It is also helpful if you can put in the issue description the PyTango information.
It can be a dump of:

.. sourcecode:: console

   $ python -c "from tango.utils import info; print(info())"

Test the connection to the Device and get it's current state
------------------------------------------------------------

One of the most basic examples is to get a reference to a device and
determine if it is running or not::

    from tango import DeviceProxy

    # Get proxy on the tango_test1 device
    print("Creating proxy to TangoTest device...")
    tango_test = DeviceProxy("sys/tg_test/1")

    # ping it
    print(tango_test.ping())

    # get the state
    print(tango_test.state())

Read and write attributes
-------------------------

Basic read/write attribute operations::

    from tango import DeviceProxy

    # Get proxy on the tango_test1 device
    print("Creating proxy to TangoTest device...")
    tango_test = DeviceProxy("sys/tg_test/1")

    # Read a scalar attribute. This will return a tango.DeviceAttribute
    # Member 'value' contains the attribute value
    scalar = tango_test.read_attribute("long_scalar")
    print(f"Long_scalar value = {scalar.value}")

    # PyTango provides a shorter way:
    scalar = tango_test.long_scalar
    print(f"Long_scalar value = {scalar}")

    # Read a spectrum attribute
    spectrum = tango_test.read_attribute("double_spectrum")
    # ... or, the shorter version:
    spectrum = tango_test.double_spectrum

    # Write a scalar attribute
    scalar_value = 18
    tango_test.write_attribute("long_scalar", scalar_value)

    #  PyTango provides a shorter way:
    tango_test.long_scalar = scalar_value

    # Write a spectrum attribute
    spectrum_value = [1.2, 3.2, 12.3]
    tango_test.write_attribute("double_spectrum", spectrum_value)
    # ... or, the shorter version:
    tango_test.double_spectrum = spectrum_value

    # Write an image attribute
    image_value = [ [1, 2], [3, 4] ]
    tango_test.write_attribute("long_image", image_value)
    # ... or, the shorter version:
    tango_test.long_image = image_value

Note that the values got when reading a spectrum or an image are numpy arrays.
This results in a faster and more memory efficient PyTango.
You can also use numpy to specify the values when
writing attributes, especially if you know the exact attribute type::

    import numpy
    from tango import DeviceProxy

    # Get proxy on the tango_test1 device
    print("Creating proxy to TangoTest device...")
    tango_test = DeviceProxy("sys/tg_test/1")

    data_1d_long = numpy.arange(0, 100, dtype=numpy.int32)

    tango_test.long_spectrum = data_1d_long

    data_2d_float = numpy.zeros((10,20), dtype=numpy.float64)

    tango_test.double_image = data_2d_float


Execute commands
----------------

As you can see in the following example, when scalar types are used, the Tango
binding automagically manages the data types, and writing scripts is quite easy::

    from tango import DeviceProxy

    # Get proxy on the tango_test1 device
    print("Creating proxy to TangoTest device...")
    tango_test = DeviceProxy("sys/tg_test/1")

    # First use the classical command_inout way to execute the DevString command
    # (DevString in this case is a command of the Tango_Test device)

    result = tango_test.command_inout("DevString", "First hello to device")
    print(f"Result of execution of DevString command = {result}")

    # the same can be achieved with a helper method
    result = tango_test.DevString("Second Hello to device")
    print(f"Result of execution of DevString command = {result}")

    # Please note that argin argument type is automatically managed by python
    result = tango_test.DevULong(12456)
    print(f"Result of execution of DevULong command = {result}")


Execute commands with more complex types
----------------------------------------

In this case you have to use put your arguments data in the correct python
structures::

    from tango import DeviceProxy

    # Get proxy on the tango_test1 device
    print("Creating proxy to TangoTest device...")
    tango_test = DeviceProxy("sys/tg_test/1")

    # The input argument is a DevVarLongStringArray so create the argin
    # variable containing an array of longs and an array of strings
    argin = ([1,2,3], ["Hello", "TangoTest device"])

    result = tango_test.DevVarLongStringArray(argin)
    print(f"Result of execution of DevVarLongArray command = {result}")

Work with Groups
----------------

.. todo::
   write this how to

Handle errors
-------------

.. todo::
   write this how to

.. _pytango-howto-server:

For now check :ref:`pytango-exception-api`.

Registering devices
-------------------

Here is how to define devices in the Tango DataBase::

    from tango import Database, DbDevInfo

    #  A reference on the DataBase
    db = Database()

    # The 3 devices name we want to create
    # Note: these 3 devices will be served by the same DServer
    new_device_name1 = "px1/tdl/mouse1"
    new_device_name2 = "px1/tdl/mouse2"
    new_device_name3 = "px1/tdl/mouse3"

    # Define the Tango Class served by this  DServer
    new_device_info_mouse = DbDevInfo()
    new_device_info_mouse._class = "Mouse"
    new_device_info_mouse.server = "ds_Mouse/server_mouse"

    # add the first device
    print("Creating device: %s" % new_device_name1)
    new_device_info_mouse.name = new_device_name1
    db.add_device(new_device_info_mouse)

    # add the next device
    print("Creating device: %s" % new_device_name2)
    new_device_info_mouse.name = new_device_name2
    db.add_device(new_device_info_mouse)

    # add the third device
    print("Creating device: %s" % new_device_name3)
    new_device_info_mouse.name = new_device_name3
    db.add_device(new_device_info_mouse)


Setting up device properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A more complex example using python subtilities.
The following python script example (containing some functions and instructions
manipulating a Galil motor axis device server) gives an idea of how the Tango
API should be accessed from Python::

    from tango import DeviceProxy

    # connecting to the motor axis device
    axis1 = DeviceProxy("microxas/motorisation/galilbox")

    # Getting Device Properties
    property_names = ["AxisBoxAttachement",
                      "AxisEncoderType",
                      "AxisNumber",
                      "CurrentAcceleration",
                      "CurrentAccuracy",
                      "CurrentBacklash",
                      "CurrentDeceleration",
                      "CurrentDirection",
                      "CurrentMotionAccuracy",
                      "CurrentOvershoot",
                      "CurrentRetry",
                      "CurrentScale",
                      "CurrentSpeed",
                      "CurrentVelocity",
                      "EncoderMotorRatio",
                      "logging_level",
                      "logging_target",
                      "UserEncoderRatio",
                      "UserOffset"]

    axis_properties = axis1.get_property(property_names)
    for prop in axis_properties.keys():
        print("%s: %s" % (prop, axis_properties[prop][0]))

    # Changing Properties
    axis_properties["AxisBoxAttachement"] = ["microxas/motorisation/galilbox"]
    axis_properties["AxisEncoderType"] = ["1"]
    axis_properties["AxisNumber"] = ["6"]
    axis1.put_property(axis_properties)

Using clients with multiprocessing
----------------------------------

Since version 9.3.0 PyTango provides :meth:`~tango.ApiUtil.cleanup()`
which resets CORBA connection.
This static function is needed when you want to use :mod:`tango` with
:mod:`multiprocessing` in your client code.

In the case when both your parent process and your child process create
:class:`~tango.DeviceProxy`, :class:`~tango.Database`
or/and :class:`~tango.AttributeProxy`
your child process inherits the context from your parent process,
i.e. open file descriptors, the TANGO and the CORBA state.
Sharing the above objects between the processes may cause unpredictable
errors, e.g. *TRANSIENT_CallTimedout*, *unidentifiable C++ exception*.
Therefore, when you start a new process you must reset CORBA connection::

    import time
    import tango

    from multiprocessing import Process


    class Worker(Process):

	def __init__(self):
	    Process.__init__(self)

	def run(self):
            # reset CORBA connection
            tango.ApiUtil.cleanup()

	    proxy = tango.DeviceProxy('test/tserver/1')

	    stime = time.time()
	    etime = stime
	    while etime - stime < 1.:
		try:
		    proxy.read_attribute("Value")
		except Exception as e:
		    print(str(e))
		etime = time.time()


    def runworkers():
	workers = [Worker() for _ in range(6)]
	for wk in workers:
	    wk.start()
	for wk in workers:
	    wk.join()


    db = tango.Database()
    dp = tango.DeviceProxy('test/tserver/1')

    for i in range(4):
	runworkers()

After `cleanup()` all references to :class:`~tango.DeviceProxy`,
:class:`~tango.AttributeProxy` or :class:`~tango.Database` objects
in the current process become invalid
and these objects need to be reconstructed.

Using clients with multithreading
---------------------------------

When performing Tango I/O from user-created threads, there can be problems.
This is often more noticeable with event subscription and unsubscription,
but it could affect any Tango I/O.  As PyTango wraps the cppTango library,
we needs to consider how cppTango's threads work.

cppTango was originally developed at a time where C++ didn't have standard
threads. All the threads currently created in cppTango are omni threads,
since this is what the omniORB library is using to create threads and since
this implementation is available for free with omniORB.

In C++, users used to create omni threads in the past so there was no issue.
Since C++11, C++ comes with an implementation of standard threads.
cppTango is currently (version 9.3.3) not directly thread safe when
a user is using C++11 standard threads or threads different than omni threads.
This lack of thread safety includes threads created from Python's
:mod:`threading` module.

In an ideal future cppTango should should protect itself, regardless
of what type of threads are used.  In the meantime, we need a work-around.

The work-around when using threads which are not omni threads is to create an
object of the C++ class ``omni_thread::ensure_self`` in the user thread, just
after the thread creation, and to delete this object only when the thread
has finished its job. This ``omni_thread::ensure_self`` object provides a
dummy omniORB ID for the thread. This ID is used when accessing thread
locks within cppTango, so the ID must remain the same for the lifetime
of the thread.  Also note that this object MUST be released before the
thread has exited, otherwise omniORB will throw an exception.

A Pythonic way to implement this work-around for multithreaded
applications is available via the :class:`~tango.EnsureOmniThread` class.
It was added in PyTango version 9.3.2.  This class is best used as a
context handler to wrap the target method of the user thread.  An example
is shown below::

    import tango
    from threading import Thread
    from time import sleep


    def thread_task():
        with tango.EnsureOmniThread():
            eid = dp.subscribe_event(
                "double_scalar", tango.EventType.PERIODIC_EVENT, cb)
            while running:
                print(f"num events stored {len(cb.get_events())}")
                sleep(1)
            dp.unsubscribe_event(eid)


    cb = tango.utils.EventCallback()  # print events to stdout
    dp = tango.DeviceProxy("sys/tg_test/1")
    dp.poll_attribute("double_scalar", 1000)
    thread = Thread(target=thread_task)
    running = True
    thread.start()
    sleep(5)
    running = False
    thread.join()

Another way to create threads in Python is the
:class:`concurrent.futures.ThreadPoolExecutor`.  The problem with this is that
the API does not provide an easy way for the context handler to cover the
lifetime of the threads, which are created as daemons.  One option is to
at least use the context handler for the functions that are submitted to the
executor. I.e., ``executor.submit(thread_task)``.  This is not guaranteed to work.
A second option to investigate (if using at least Python 3.7) is the
``initializer`` argument which could be used to ensure a call to the
:meth:`~tango.EnsureOmniThread.__enter__()` method for a thread-specific
instance of :class:`~tango.EnsureOmniThread`.  However, calling the
:meth:`~tango.EnsureOmniThread.__exit__()` method on the corresponding
object at shutdown is a problem.  Maybe it could be submitted as work.

.. _howto_write_a_server:

Write a server
--------------

Before reading this chapter you should be aware of the TANGO basic concepts.
This chapter does not explain what a Tango device or a device server is.
This is explained in detail in the
`Tango control system manual <http://www.tango-controls.org/documentation/kernel/>`_

Since version 8.1, PyTango provides a helper module which simplifies the
development of a Tango device server. This helper is provided through the
:mod:`tango.server` module.

Here is a simple example on how to write a *Clock* device server using the
high level API

.. code-block:: python
   :linenos:

    import time
    from tango.server import Device, attribute, command, pipe


    class Clock(Device):

        @attribute
        def time(self):
            return time.time()

        @command(dtype_in=str, dtype_out=str)
        def strftime(self, format):
            return time.strftime(format)

        @pipe
        def info(self):
            return ('Information',
                    dict(manufacturer='Tango',
                         model='PS2000',
                         version_number=123))


    if __name__ == "__main__":
        Clock.run_server()


**line 2**
    import the necessary symbols

**line 5**
    tango device class definition. A Tango device must inherit from
    :class:`tango.server.Device`

**line 7-9**
    definition of the *time* attribute. By default, attributes are double, scalar,
    read-only. Check the :class:`~tango.server.attribute` for the complete
    list of attribute options.

**line 11-13**
    the method *strftime* is exported as a Tango command. In receives a string
    as argument and it returns a string. If a method is to be exported as a
    Tango command, it must be decorated as such with the
    :func:`~tango.server.command` decorator

**line 15-20**
    definition of the *info* pipe. Check the :class:`~tango.server.pipe`
    for the complete list of pipe options.

**line 24**
    start the Tango run loop.  This method automatically determines the Python
    class name and exports it as a Tango class.  For more complicated cases,
    check :func:`~tango.server.run` for the complete list of options

There is a more detailed clock device server in the examples/Clock folder.

Here is a more complete example on how to write a *PowerSupply* device server
using the high level API. The example contains:

#. a read-only double scalar attribute called *voltage*
#. a read/write double scalar expert attribute *current*
#. a read/write float scalar attribute *range*, defined with pythonic-style decorators, which can be always read, but conditionally written
#. a read/write float scalar attribute *compliance*, defined with alternative decorators
#. a read-only double image attribute called *noise*
#. a *ramp* command
#. a *host* device property
#. a *port* class property

.. code-block:: python
    :linenos:

    from time import time
    from numpy.random import random_sample

    from tango import AttrQuality, AttrWriteType, DispLevel, AttReqType
    from tango.server import Device, attribute, command
    from tango.server import class_property, device_property


    class PowerSupply(Device):

        _my_range = 0
        _my_compliance = 0.
        _output_on = False

        current = attribute(label="Current", dtype=float,
                            display_level=DispLevel.EXPERT,
                            access=AttrWriteType.READ_WRITE,
                            unit="A", format="8.4f",
                            min_value=0.0, max_value=8.5,
                            min_alarm=0.1, max_alarm=8.4,
                            min_warning=0.5, max_warning=8.0,
                            fget="get_current", fset="set_current",
                            doc="the power supply current")

        noise = attribute(label="Noise", dtype=((float,),),
                          max_dim_x=1024, max_dim_y=1024,
                          fget="get_noise")

        host = device_property(dtype=str)
        port = class_property(dtype=int, default_value=9788)

        @attribute
        def voltage(self):
            self.info_stream("get voltage(%s, %d)" % (self.host, self.port))
            return 10.0

        def get_current(self):
            return 2.3456, time(), AttrQuality.ATTR_WARNING

        def set_current(self, current):
            print("Current set to %f" % current)

        def get_noise(self):
            return random_sample((1024, 1024))

        range = attribute(label="Range", dtype=float)

        @range.setter
        def range(self, new_range):
            self._my_range = new_range

        @range.getter
        def current_range(self):
            return self._my_range

        @range.is_allowed
        def can_range_be_changed(self, req_type):
            if req_type == AttReqType.WRITE_REQ:
                return not self._output_on
            return True

        compliance = attribute(label="Compliance", dtype=float)

        @compliance.read
        def compliance(self):
            return self._my_compliance

        @compliance.write
        def new_compliance(self, new_compliance):
            self._my_compliance = new_compliance

        @command(dtype_in=bool)
        def output_on_off(self, on_off):
            self._output_on = on_off

    if __name__ == "__main__":
        PowerSupply.run_server()

.. _logging:

Server logging
--------------

This chapter instructs you on how to use the tango logging API (log4tango) to
create tango log messages on your device server.

The logging system explained here is the Tango Logging Service (TLS). For
detailed information on how this logging system works please check:

    * `Usage <https://tango-controls.readthedocs.io/en/latest/development/device-api/device-server-model.html#the-tango-logging-service>`_
    * `Property reference <https://tango-controls.readthedocs.io/en/latest/development/advanced/reference.html#the-device-logging>`_

The easiest way to start seeing log messages on your device server console is
by starting it with the verbose option. Example::

    python PyDsExp.py PyDs1 -v4

This activates the console tango logging target and filters messages with
importance level DEBUG or more.
The links above provided detailed information on how to configure log levels
and log targets. In this document we will focus on how to write log messages on
your device server.

Basic logging
~~~~~~~~~~~~~

The most basic way to write a log message on your device is to use the
:class:`~tango.server.Device` logging related methods:

    * :meth:`~tango.server.Device.debug_stream`
    * :meth:`~tango.server.Device.info_stream`
    * :meth:`~tango.server.Device.warn_stream`
    * :meth:`~tango.server.Device.error_stream`
    * :meth:`~tango.server.Device.fatal_stream`

Example::

    def read_voltage(self):
        self.info_stream("read voltage attribute")
        # ...
        return voltage_value

This will print a message like::

    1282206864 [-1215867200] INFO test/power_supply/1 read voltage attribute

every time a client asks to read the *voltage* attribute value.

The logging methods support argument list feature (since PyTango 8.1). Example::

    def read_voltage(self):
        self.info_stream("read_voltage(%s, %d)", self.host, self.port)
        # ...
        return voltage_value


Logging with print statement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*This feature is only possible since PyTango 7.1.3*

It is possible to use the print statement to log messages into the tango logging
system. This is achieved by using the python's print extend form sometimes
refered to as *print chevron*.

Same example as above, but now using *print chevron*::

    def read_voltage(self, the_att):
        print >>self.log_info, "read voltage attribute"
        # ...
        return voltage_value

Or using the python 3k print function::

    def read_Long_attr(self, the_att):
        print("read voltage attribute", file=self.log_info)
        # ...
        return voltage_value


Logging with decorators
~~~~~~~~~~~~~~~~~~~~~~~

*This feature is only possible since PyTango 7.1.3*

PyTango provides a set of decorators that place automatic log messages when
you enter and when you leave a python method. For example::

    @tango.DebugIt()
    def read_Long_attr(self, the_att):
        the_att.set_value(self.attr_long)

will generate a pair of log messages each time a client asks for the 'Long_attr'
value. Your output would look something like::

    1282208997 [-1215965504] DEBUG test/pydsexp/1 -> read_Long_attr()
    1282208997 [-1215965504] DEBUG test/pydsexp/1 <- read_Long_attr()

Decorators exist for all tango log levels:
    * :class:`tango.DebugIt`
    * :class:`tango.InfoIt`
    * :class:`tango.WarnIt`
    * :class:`tango.ErrorIt`
    * :class:`tango.FatalIt`

The decorators receive three optional arguments:
    * show_args - shows method arguments in log message (defaults to False)
    * show_kwargs shows keyword method arguments in log message (defaults to False)
    * show_ret - shows return value in log message (defaults to False)

Example::

    @tango.DebugIt(show_args=True, show_ret=True)
    def IOLong(self, in_data):
        return in_data * 2

will output something like::

    1282221947 [-1261438096] DEBUG test/pydsexp/1 -> IOLong(23)
    1282221947 [-1261438096] DEBUG test/pydsexp/1 46 <- IOLong()


Multiple device classes (Python and C++) in a server
----------------------------------------------------

Within the same python interpreter, it is possible to mix several Tango classes.
Let's say two of your colleagues programmed two separate Tango classes in two
separated python files: A :class:`PLC` class in a :file:`PLC.py`::

    # PLC.py

    from tango.server import Device

    class PLC(Device):

        # bla, bla my PLC code

    if __name__ == "__main__":
        PLC.run_server()

... and a :class:`IRMirror` in a :file:`IRMirror.py`::

    # IRMirror.py

    from tango.server import Device

    class IRMirror(Device):

        # bla, bla my IRMirror code

    if __name__ == "__main__":
        IRMirror.run_server()

You want to create a Tango server called `PLCMirror` that is able to contain
devices from both PLC and IRMirror classes. All you have to do is write
a :file:`PLCMirror.py` containing the code::

    # PLCMirror.py

    from tango.server import run
    from PLC import PLC
    from IRMirror import IRMirror

    run([PLC, IRMirror])

It is also possible to add C++ Tango class in a Python device server as soon as:
    1. The Tango class is in a shared library
    2. It exist a C function to create the Tango class

For a Tango class called MyTgClass, the shared library has to be called
MyTgClass.so and has to be in a directory listed in the LD_LIBRARY_PATH
environment variable. The C function creating the Tango class has to be called
_create_MyTgClass_class() and has to take one parameter of type "char \*" which
is the Tango class name. Here is an example of the main function of the same
device server than before but with one C++ Tango class called SerialLine::

    import tango
    import sys

    if __name__ == '__main__':
        util = tango.Util(sys.argv)
        util.add_class('SerialLine', 'SerialLine', language="c++")
        util.add_class(PLCClass, PLC, 'PLC')
        util.add_class(IRMirrorClass, IRMirror, 'IRMirror')

        U = tango.Util.instance()
        U.server_init()
        U.server_run()

:Line 6: The C++ class is registered in the device server
:Line 7 and 8: The two Python classes are registered in the device server

.. _dynamic-attributes-howto:

Create attributes dynamically
-----------------------------

It is also possible to create dynamic attributes within a Python device server.
There are several ways to create dynamic attributes. One of the ways, is to
create all the devices within a loop, then to create the dynamic attributes and
finally to make all the devices available for the external world. In a C++ device
server, this is typically done within the <Device>Class::device_factory() method.
In Python device server, this method is generic and the user does not have one.
Nevertheless, this generic device_factory provides the user with a way to create
dynamic attributes.

Using the high-level API, you can re-define a method called
:meth:`~tango.server.Device.initialize_dynamic_attributes`
on each <Device>. This method will be called automatically by the device_factory for
each device. Within this method you create all the dynamic attributes.

If you are still using the low-level API with a <Device>Class instead of just a <Device>,
then you can use the generic device_factory's call to the
:meth:`~tango.DeviceClass.dyn_attr` method.
It is simply necessary to re-define this method within your <Device>Class and to create
the dynamic attributes within this method.

Internally, the high-level API re-defines :meth:`~tango.DeviceClass.dyn_attr` to call
:meth:`~tango.server.Device.initialize_dynamic_attributes` for each device.

.. note:: The ``dyn_attr()`` (and ``initialize_dynamic_attributes()`` for high-level API) methods
          are only called **once** when the device server starts, since the Python device_factory
          method is only called once. Within the device_factory method, ``init_device()`` is
          called for all devices and only after that is ``dyn_attr()`` called for all devices.
          If the ``Init`` command is executed on a device it will not call the ``dyn_attr()`` method
          again (and will not call ``initialize_dynamic_attributes()`` either).

There is another point to be noted regarding dynamic attributes within a Python
device server. The Tango Python device server core checks that for each
static attribute there exists methods named <attribute_name>_read and/or
<attribute_name>_write and/or is_<attribute_name>_allowed. Using dynamic
attributes, it is not possible to define these methods because attribute names
and number are known only at run-time.
To address this issue, you need to provide references to these methods when
calling :meth:`~tango.server.Device.add_attribute`.

The recommended approach with the high-level API is to reference these methods when
instantiating a :class:`tango.server.attribute` object using the fget, fset and/or
fisallowed kwargs (see example below).  Where fget is the method which has to be
executed when the attribute is read, fset is the method to be executed
when the attribute is written and fisallowed is the method to be executed
to implement the attribute state machine.  This :class:`tango.server.attribute` object
is then passed to the :meth:`~tango.server.Device.add_attribute` method.

.. note:: If the fget (fread), fset (fwrite) and fisallowed are given as str(name) they must be methods
          that exist on your Device class. If you want to use plain functions, or functions belonging to a
          different class, you should pass a callable.

Which arguments you have to provide depends on the type of the attribute.  For example,
a WRITE attribute does not need a read method.

.. note:: Starting from PyTango 9.4.0 the read methods for dynamic attributes
          can also be implemented with the high-level API.  Prior to that, only the low-level
          API was available.

For the read function it is possible to use one of the following signatures::

    def low_level_read(self, attr):
        attr.set_value(self.attr_value)

    def high_level_read(self, attr):
        return self.attr_value

For the write function there is only one signature::

    def low_level_write(self, attr):
        self.attr_value = attr.get_write_value()

Here is an example of a device which creates a dynamic attribute on startup::

    from tango import AttrWriteType
    from tango.server import Device, attribute

    class MyDevice(Device):

        def initialize_dynamic_attributes(self):
            self._values = {"dyn_attr": 0}
            attr = attribute(
                name="dyn_attr",
                dtype=int,
                access=AttrWriteType.READ_WRITE,
                fget=self.generic_read,
                fset=self.generic_write,
                fisallowed=self.generic_is_allowed,
            )
            self.add_attribute(attr)

        def generic_read(self, attr):
            attr_name = attr.get_name()
            value = self._values[attr_name]
            return value

        def generic_write(self, attr):
            attr_name = attr.get_name()
            value = attr.get_write_value()
            self._values[attr_name] = value

        def generic_is_allowed(self, request_type):
            # note: we don't know which attribute is being read!
            # request_type will be either AttReqType.READ_REQ or AttReqType.WRITE_REQ
            return True


Another way to create dynamic attributes is to do it some time after the device has
started.  For example, using a command.  In this case, we just call the
:meth:`~tango.server.Device.add_attribute` method when necessary.

Here is an example of a device which has a TANGO command called
*CreateFloatAttribute*. When called, this command creates a new scalar floating
point attribute with the specified name::

    from tango import AttrWriteType
    from tango.server import Device, attribute, command

    class MyDevice(Device):

        def init_device(self):
            super(MyDevice, self).init_device()
            self._values = {}

        @command(dtype_in=str)
        def CreateFloatAttribute(self, attr_name):
            if attr_name not in self._values:
                self._values[attr_name] = 0.0
                attr = attribute(
                    name=attr_name,
                    dtype=float,
                    access=AttrWriteType.READ_WRITE,
                    fget=self.generic_read,
                    fset=self.generic_write,
                )
                self.add_attribute(attr)
                self.info_stream("Added dynamic attribute %r", attr_name)
            else:
                raise ValueError(f"Already have an attribute called {repr(attr_name)}")

        def generic_read(self, attr):
            attr_name = attr.get_name()
            self.info_stream("Reading attribute %s", attr_name)
            value = self._values[attr.get_name()]
            attr.set_value(value)

        def generic_write(self, attr):
            attr_name = attr.get_name()
            value = attr.get_write_value()
            self.info_stream("Writing attribute %s - value %s", attr_name, value)
            self._values[attr.get_name()] = value

An approach more in line with the low-level API is also possible, but not recommended for
new devices. The Device_3Impl::add_attribute() method has the following
signature:

    ``add_attribute(self, attr, r_meth=None, w_meth=None, is_allo_meth=None)``

attr is an instance of the :class:`tango.Attr` class, r_meth is the method which has to be
executed when the attribute is read, w_meth is the method to be executed
when the attribute is written and is_allo_meth is the method to be executed
to implement the attribute state machine.

Old example::

    from tango import Attr, AttrWriteType
    from tango.server import Device, command

    class MyOldDevice(Device):

        @command(dtype_in=str)
        def CreateFloatAttribute(self, attr_name):
            attr = Attr(attr_name, tango.DevDouble, AttrWriteType.READ_WRITE)
            self.add_attribute(attr, self.read_General, self.write_General)

        def read_General(self, attr):
            self.info_stream("Reading attribute %s", attr.get_name())
            attr.set_value(99.99)

        def write_General(self, attr):
            self.info_stream("Writing attribute %s - value %s", attr.get_name(), attr.get_write_value())


Create/Delete devices dynamically
---------------------------------

*This feature is only possible since PyTango 7.1.2*

Starting from PyTango 7.1.2 it is possible to create devices in a device server
"en caliente". This means that you can create a command in your "management device"
of a device server that creates devices of (possibly) several other tango classes.
There are two ways to create a new device which are described below.

Tango imposes a limitation: the tango class(es) of the device(s) that is(are)
to be created must have been registered before the server starts.
If you use the high level API, the tango class(es) must be listed in the call
to :func:`~tango.server.run`. If you use the lower level server API, it must
be done using individual calls to :meth:`~tango.Util.add_class`.


Dynamic device from a known tango class name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you know the tango class name but you don't have access to the :class:`tango.DeviceClass`
(or you are too lazy to search how to get it ;-) the way to do it is call
:meth:`~tango.Util.create_device` / :meth:`~tango.Util.delete_device`.
Here is an example of implementing a tango command on one of your devices that
creates a device of some arbitrary class (the example assumes the tango commands
'CreateDevice' and 'DeleteDevice' receive a parameter of type DevVarStringArray
with two strings. No error processing was done on the code for simplicity sake)::

    from tango import Util
    from tango.server import Device, command

    class MyDevice(Device):

        @command(dtype_in=[str])
        def CreateDevice(self, pars):
            klass_name, dev_name = pars
            util = Util.instance()
            util.create_device(klass_name, dev_name, alias=None, cb=None)

        @command(dtype_in=[str])
        def DeleteDevice(self, pars):
            klass_name, dev_name = pars
            util = Util.instance()
            util.delete_device(klass_name, dev_name)

An optional callback can be registered that will be executed after the device is
registed in the tango database but before the actual device object is created
and its init_device method is called. It can be used, for example, to initialize
some device properties.

Dynamic device from a known tango class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you already have access to the :class:`~tango.DeviceClass` object that
corresponds to the tango class of the device to be created you can call directly
the :meth:`~tango.DeviceClass.create_device` / :meth:`~tango.DeviceClass.delete_device`.
For example, if you wish to create a clone of your device, you can create a
tango command called *Clone*::

    class MyDevice(tango.Device):

        def fill_new_device_properties(self, dev_name):
            prop_names = db.get_device_property_list(self.get_name(), "*")
            prop_values = db.get_device_property(self.get_name(), prop_names.value_string)
            db.put_device_property(dev_name, prop_values)

            # do the same for attributes...
            ...

        def Clone(self, dev_name):
            klass = self.get_device_class()
            klass.create_device(dev_name, alias=None, cb=self.fill_new_device_properties)

        def DeleteSibling(self, dev_name):
            klass = self.get_device_class()
            klass.delete_device(dev_name)

Note that the cb parameter is optional. In the example it is given for
demonstration purposes only.

.. _server:

Write a server (original API)
-----------------------------

This chapter describes how to develop a PyTango device server using the
original PyTango server API. This API mimics the C++ API and is considered
low level.
You should write a server using this API if you are using code generated by
`Pogo tool <https://tango-controls.readthedocs.io/en/latest/tools-and-extensions/built-in/pogo/index.html>`_
or if for some reason the high level API helper doesn't provide a feature
you need (in that case think of writing a mail to tango mailing list explaining
what you cannot do).

The main part of a Python device server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The rule of this part of a Tango device server is to:

    - Create the :class:`Util` object passing it the Python interpreter command
      line arguments
    - Add to this object the list of Tango class(es) which have to be hosted by
      this interpreter
    - Initialize the device server
    - Run the device server loop

The following is a typical code for this main function::

    if __name__ == '__main__':
        util = tango.Util(sys.argv)
        util.add_class(PyDsExpClass, PyDsExp)

        U = tango.Util.instance()
        U.server_init()
        U.server_run()

**Line 2**
    Create the Util object passing it the interpreter command line arguments
**Line 3**
    Add the Tango class *PyDsExp* to the device server. The :meth:`Util.add_class`
    method of the Util class has two arguments which are the Tango class
    PyDsExpClass instance and the Tango PyDsExp instance.
    This :meth:`Util.add_class` method is only available since version
    7.1.2. If you are using an older version please use
    :meth:`Util.add_TgClass` instead.
**Line 7**
    Initialize the Tango device server
**Line 8**
    Run the device server loop

The PyDsExpClass class in Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The rule of this class is to :

    - Host and manage data you have only once for the Tango class whatever
      devices of this class will be created
    - Define Tango class command(s)
    - Define Tango class attribute(s)

In our example, the code of this Python class looks like::

    class PyDsExpClass(tango.DeviceClass):

        cmd_list = { 'IOLong' : [ [ tango.ArgType.DevLong, "Number" ],
                                  [ tango.ArgType.DevLong, "Number * 2" ] ],
                     'IOStringArray' : [ [ tango.ArgType.DevVarStringArray, "Array of string" ],
                                         [ tango.ArgType.DevVarStringArray, "This reversed array"] ],
        }

        attr_list = { 'Long_attr' : [ [ tango.ArgType.DevLong ,
                                        tango.AttrDataFormat.SCALAR ,
                                        tango.AttrWriteType.READ],
                                      { 'min alarm' : 1000, 'max alarm' : 1500 } ],

                     'Short_attr_rw' : [ [ tango.ArgType.DevShort,
                                           tango.AttrDataFormat.SCALAR,
                                           tango.AttrWriteType.READ_WRITE ] ]
        }



**Line 1**
    The PyDsExpClass class has to inherit from the :class:`DeviceClass` class

**Line 3 to 7**
    Definition of the cmd_list :class:`dict` defining commands. The *IOLong* command
    is defined at lines 3 and 4. The *IOStringArray* command is defined in
    lines 5 and 6
**Line 9 to 17**
    Definition of the attr_list :class:`dict` defining attributes. The *Long_attr*
    attribute is defined at lines 9 to 12 and the *Short_attr_rw* attribute is
    defined at lines 14 to 16

If you have something specific to do in the class constructor like
initializing some specific data member, you will have to code a class
constructor. An example of such a contructor is ::

    def __init__(self, name):
        tango.DeviceClass.__init__(self, name)
        self.set_type("TestDevice")

The device type is set at line 3.

Defining commands
~~~~~~~~~~~~~~~~~

As shown in the previous example, commands have to be defined in a :class:`dict`
called *cmd_list* as a data member of the xxxClass class of the Tango class.
This :class:`dict` has one element per command. The element key is the command
name. The element value is a python list which defines the command. The generic
form of a command definition is:

    ``'cmd_name' : [ [in_type, <"In desc">], [out_type, <"Out desc">], <{opt parameters}>]``

The first element of the value list is itself a list with the command input
data type (one of the :class:`tango.ArgType` pseudo enumeration value) and
optionally a string describing this input argument. The second element of the
value list is also a list with the command output data type (one of the
:class:`tango.ArgType` pseudo enumeration value) and optionaly a string
describing it. These two elements are mandatory. The third list element is
optional and allows additional command definition. The authorized element for
this :class:`dict` are summarized in the following array:

    +-------------------+----------------------+------------------------------------------+
    |      key          |        Value         |             Definition                   |
    +===================+======================+==========================================+
    | "display level"   | DispLevel enum value |       The command display level          |
    +-------------------+----------------------+------------------------------------------+
    | "polling period"  | Any number           |     The command polling period (mS)      |
    +-------------------+----------------------+------------------------------------------+
    | "default command" | True or False        | To define that it is the default command |
    +-------------------+----------------------+------------------------------------------+

Defining attributes
~~~~~~~~~~~~~~~~~~~

As shown in the previous example, attributes have to be defined in a :class:`dict`
called **attr_list** as a data
member of the xxxClass class of the Tango class. This :class:`dict` has one element
per attribute. The element key is the attribute name. The element value is a
python :class:`list` which defines the attribute. The generic form of an
attribute definition is:

    ``'attr_name' : [ [mandatory parameters], <{opt parameters}>]``

For any kind of attributes, the mandatory parameters are:

    ``[attr data type, attr data format, attr data R/W type]``

The attribute data type is one of the possible value for attributes of the
:class:`tango.ArgType` pseudo enunmeration. The attribute data format is one
of the possible value of the :class:`tango.AttrDataFormat` pseudo enumeration
and the attribute R/W type is one of the possible value of the
:class:`tango.AttrWriteType` pseudo enumeration. For spectrum attribute,
you have to add the maximum X size (a number). For image attribute, you have
to add the maximun X and Y dimension (two numbers). The authorized elements for
the :class:`dict` defining optional parameters are summarized in the following
array:

    +-------------------+-----------------------------------+------------------------------------------+
    |       key         |              value                |            definition                    |
    +===================+===================================+==========================================+
    | "display level"   | tango.DispLevel enum value        |   The attribute display level            |
    +-------------------+-----------------------------------+------------------------------------------+
    |"polling period"   |          Any number               | The attribute polling period (mS)        |
    +-------------------+-----------------------------------+------------------------------------------+
    |  "memorized"      | "true" or                         | Define if and how the att. is memorized  |
    |                   | "true_without_hard_applied"       |                                          |
    +-------------------+-----------------------------------+------------------------------------------+
    |     "label"       |            A string               |       The attribute label                |
    +-------------------+-----------------------------------+------------------------------------------+
    |  "description"    |            A string               |   The attribute description              |
    +-------------------+-----------------------------------+------------------------------------------+
    |     "unit"        |            A string               |       The attribute unit                 |
    +-------------------+-----------------------------------+------------------------------------------+
    |"standard unit"    |           A number                |  The attribute standard unit             |
    +-------------------+-----------------------------------+------------------------------------------+
    | "display unit"    |            A string               |   The attribute display unit             |
    +-------------------+-----------------------------------+------------------------------------------+
    |    "format"       |            A string               | The attribute display format             |
    +-------------------+-----------------------------------+------------------------------------------+
    |  "max value"      |          A number                 |   The attribute max value                |
    +-------------------+-----------------------------------+------------------------------------------+
    |   "min value"     |           A number                |    The attribute min value               |
    +-------------------+-----------------------------------+------------------------------------------+
    |  "max alarm"      |           A number                |    The attribute max alarm               |
    +-------------------+-----------------------------------+------------------------------------------+
    |  "min alarm"      |           A number                |    The attribute min alarm               |
    +-------------------+-----------------------------------+------------------------------------------+
    | "min warning"     |           A number                |  The attribute min warning               |
    +-------------------+-----------------------------------+------------------------------------------+
    |"max warning"      |           A number                |  The attribute max warning               |
    +-------------------+-----------------------------------+------------------------------------------+
    |  "delta time"     |           A number                | The attribute RDS alarm delta time       |
    +-------------------+-----------------------------------+------------------------------------------+
    |   "delta val"     |           A number                | The attribute RDS alarm delta val        |
    +-------------------+-----------------------------------+------------------------------------------+

The PyDsExp class in Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The rule of this class is to implement methods executed by commands and attributes.
In our example, the code of this class looks like::

    class PyDsExp(tango.Device):

        def __init__(self,cl,name):
            tango.Device.__init__(self, cl, name)
            self.info_stream('In PyDsExp.__init__')
            PyDsExp.init_device(self)

        def init_device(self):
            self.info_stream('In Python init_device method')
            self.set_state(tango.DevState.ON)
            self.attr_short_rw = 66
            self.attr_long = 1246

        #------------------------------------------------------------------

        def delete_device(self):
            self.info_stream('PyDsExp.delete_device')

        #------------------------------------------------------------------
        # COMMANDS
        #------------------------------------------------------------------

        def is_IOLong_allowed(self):
            return self.get_state() == tango.DevState.ON

        def IOLong(self, in_data):
            self.info_stream('IOLong', in_data)
            in_data = in_data * 2
            self.info_stream('IOLong returns', in_data)
            return in_data

        #------------------------------------------------------------------

        def is_IOStringArray_allowed(self):
            return self.get_state() == tango.DevState.ON

        def IOStringArray(self, in_data):
            l = range(len(in_data)-1, -1, -1)
            out_index=0
            out_data=[]
            for i in l:
                self.info_stream('IOStringArray <-', in_data[out_index])
                out_data.append(in_data[i])
                self.info_stream('IOStringArray ->',out_data[out_index])
                out_index += 1
            self.y = out_data
            return out_data

        #------------------------------------------------------------------
        # ATTRIBUTES
        #------------------------------------------------------------------

        def read_attr_hardware(self, data):
            self.info_stream('In read_attr_hardware')

        def read_Long_attr(self, the_att):
            self.info_stream("read_Long_attr")

            the_att.set_value(self.attr_long)

        def is_Long_attr_allowed(self, req_type):
            return self.get_state() in (tango.DevState.ON,)

        def read_Short_attr_rw(self, the_att):
            self.info_stream("read_Short_attr_rw")

            the_att.set_value(self.attr_short_rw)

        def write_Short_attr_rw(self, the_att):
            self.info_stream("write_Short_attr_rw")

            self.attr_short_rw = the_att.get_write_value()

        def is_Short_attr_rw_allowed(self, req_type):
            return self.get_state() in (tango.DevState.ON,)

**Line 1**
    The PyDsExp class has to inherit from the tango.Device (this will used the latest
    device implementation class available, e.g. Device_5Impl)
**Line 3 to 6**
    PyDsExp class constructor. Note that at line 6, it calls the *init_device()*
    method
**Line 8 to 12**
    The init_device() method. It sets the device state (line 9) and initialises
    some data members
**Line 16 to 17**
    The delete_device() method. This method is not mandatory. You define it
    only if you have to do something specific before the device is destroyed
**Line 23 to 30**
    The two methods for the *IOLong* command. The first method is called
    *is_IOLong_allowed()* and it is the command is_allowed method (line 23 to 24).
    The second method has the same name than the command name. It is the method
    which executes the command. The command input data type is a Tango long
    and therefore, this method receives a python integer.
**Line 34 to 47**
    The two methods for the *IOStringArray* command. The first method is its
    is_allowed method (Line 34 to 35). The second one is the command
    execution method (Line 37 to 47). The command input data type is a string
    array. Therefore, the method receives the array in a python list of python
    strings.
**Line 53 to 54**
    The *read_attr_hardware()* method. Its argument is a Python sequence of
    Python integer.
**Line 56 to 59**
    The method executed when the *Long_attr* attribute is read. Note that before
    PyTango 7 it sets the attribute value with the tango.set_attribute_value
    function. Now the same can be done using the set_value of the attribute
    object
**Line 61 to 62**
    The is_allowed method for the *Long_attr* attribute. This is an optional
    method that is called when the attribute is read or written. Not defining it
    has the same effect as always returning True. The parameter req_type is of
    type :class:`AttReqtype` which tells if the method is called due to a read
    or write request. Since this is a read-only attribute, the method will only
    be called for read requests, obviously.
**Line 64 to 67**
    The method executed when the *Short_attr_rw* attribute is read.
**Line 69 to 72**
    The method executed when the Short_attr_rw attribute is written.
    Note that before PyTango 7 it gets the attribute value with a call to the
    Attribute method *get_write_value* with a list as argument. Now the write
    value can be obtained as the return value of the *get_write_value* call. And
    in case it is a scalar there is no more the need to extract it from the list.
**Line 74 to 75**
    The is_allowed method for the *Short_attr_rw* attribute. This is an optional
    method that is called when the attribute is read or written. Not defining it
    has the same effect as always returning True. The parameter req_type is of
    type :class:`AttReqtype` which tells if the method is called due to a read
    or write request.

General methods
###############

The following array summarizes how the general methods we have in a Tango
device server are implemented in Python.

+----------------------+-------------------------+-------------+-----------+
|         Name         | Input par (with "self") |return value | mandatory |
+======================+=========================+=============+===========+
|      init_device     |        None             |   None      |  Yes      |
+----------------------+-------------------------+-------------+-----------+
|     delete_device    |        None             |   None      |  No       |
+----------------------+-------------------------+-------------+-----------+
| always_executed_hook |        None             |   None      |  No       |
+----------------------+-------------------------+-------------+-----------+
|    signal_handler    |   :py:obj:`int`         |   None      |  No       |
+----------------------+-------------------------+-------------+-----------+
| read_attr_hardware   | sequence<:py:obj:`int`> |   None      |  No       |
+----------------------+-------------------------+-------------+-----------+

Implementing a command
######################

Commands are defined as described above. Nevertheless, some methods implementing
them have to be written. These methods names are fixed and depend on command
name. They have to be called:

    - ``is_<Cmd_name>_allowed(self)``
    - ``<Cmd_name>(self, arg)``

For instance, with a command called *MyCmd*, its is_allowed method has to be
called `is_MyCmd_allowed` and its execution method has to be called simply *MyCmd*.
The following array gives some more info on these methods.

+-----------------------+-------------------------+--------------------+-----------+
|        Name           | Input par (with "self") | return value       | mandatory |
+=======================+=========================+====================+===========+
| is_<Cmd_name>_allowed |        None             | Python boolean     |  No       |
+-----------------------+-------------------------+--------------------+-----------+
|      Cmd_name         | Depends on cmd type     |Depends on cmd type |  Yes      |
+-----------------------+-------------------------+--------------------+-----------+

Please check :ref:`pytango-data-types` chapter to understand the data types
that can be used in command parameters and return values.

The following code is an example of how you write code executed when a client
calls a command named IOLong::

    def is_IOLong_allowed(self):
        self.debug_stream("in is_IOLong_allowed")
        return self.get_state() == tango.DevState.ON

    def IOLong(self, in_data):
        self.info_stream('IOLong', in_data)
        in_data = in_data * 2
        self.info_stream('IOLong returns', in_data)
        return in_data

**Line 1-3**
    the is_IOLong_allowed method determines in which conditions the command
    'IOLong' can be executed. In this case, the command can only be executed if
    the device is in 'ON' state.
**Line 6**
    write a log message to the tango INFO stream (click :ref:`here <logging>` for
    more information about PyTango log system).
**Line 7**
    does something with the input parameter
**Line 8**
    write another log message to the tango INFO stream (click :ref:`here <logging>` for
    more information about PyTango log system).
**Line 9**
    return the output of executing the tango command

Implementing an attribute
#########################

Attributes are defined as described in chapter 5.3.2. Nevertheless, some methods
implementing them have to be written. These methods names are fixed and depend
on attribute name. They have to be called:

    - ``is_<Attr_name>_allowed(self, req_type)``
    - ``read_<Attr_name>(self, attr)``
    - ``write_<Attr_name>(self, attr)``

For instance, with an attribute called *MyAttr*, its is_allowed method has to be
called *is_MyAttr_allowed*, its read method has to be called *read_MyAttr* and
its write method has to be called *write_MyAttr*.
The *attr* parameter is an instance of :class:`Attr`.
Unlike the commands, the is_allowed method for attributes receives a parameter
of type :class:`AttReqtype`.

Please check :ref:`pytango-data-types` chapter to understand the data types
that can be used in attribute.

The following code is an example of how you write code executed when a client
read an attribute which is called *Long_attr*::

    def read_Long_attr(self, the_att):
        self.info_stream("read attribute name Long_attr")
        the_att.set_value(self.attr_long)

**Line 1**
    Method declaration with "the_att" being an instance of the Attribute
    class representing the Long_attr attribute
**Line 2**
    write a log message to the tango INFO stream (click :ref:`here <logging>`
    for more information about PyTango log system).
**Line 3**
    Set the attribute value using the method set_value() with the attribute
    value as parameter.

The following code is an example of how you write code executed when a client
write the Short_attr_rw attribute::

    def write_Short_attr_rw(self,the_att):
        self.info_stream("In write_Short_attr_rw for attribute ",the_att.get_name())
        self.attr_short_rw = the_att.get_write_value(data)

**Line 1**
       Method declaration with "the_att" being an instance of the Attribute
       class representing the Short_attr_rw attribute
**Line 2**
    write a log message to the tango INFO stream (click :ref:`here <logging>` for
    more information about PyTango log system).
**Line 3**
    Get the value sent by the client using the method get_write_value() and
    store the value written in the device object. Our attribute is a scalar
    short attribute so the return value is an int
