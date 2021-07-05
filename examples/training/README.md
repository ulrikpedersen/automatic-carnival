# PyTango Training Material

This folder includes example scripts for using PyTango as a client and a server.
It is useful to refer to during training exercises.

## Acknowledgments

Portions of the source code are derived from work by multiple authors:
- https://github.com/vxgmichel
- https://github.com/tiagocoutinho
- https://github.com/ajoubertza
- https://github.com/lorenzopivetta
  
These repos were used:
- https://github.com/vxgmichel/icalepcs-workshop
- https://github.com/ajoubertza/icalepcs-workshop

## Setup of the Tango Development Environment

A simple Docker compose environment is useful for executing these scripts.

We use existing docker images for database, Tango Database server, TangoTest server and ipython/itango CLI.
They are from the [Square Kilometre Array Organisation](https://www.skatelescope.org) (SKAO) project.

Container services:
- **tangodb**: MariaDB database
- **databaseds**:  Database Device Server, `sys/database/2`
- **tangotest**:  TangoTest Device Server: `sys/tg_test/1`
- **cli**:  Python command line tools, with this folder as a volume mount in `/training`

### Docker network
The docker-compose file requires a Docker network to be created, since `host`
networking is not supported on MacOS:

```commandline
docker network create pytango-training-net  
```

The network can be removed, when no longer required:
```commandline
docker network rm pytango-training-net  
```

### Starting and stopping the services

From the folder containing `docker-compose.yml`, the services can be started by executing:

```commandline
docker-compose up
```

Push CTRL+C to stop.

## Command-line access to ipython/itango

Once the Docker compose services are running, we can use the cli container.
A few examples are shown below.

### Start an ipython session

```shell
docker-compose exec cli ipython3

Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.21.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import tango

In [2]: print(tango.utils.info())
PyTango 9.3.3 (9, 3, 3)
PyTango compiled with:
    Python : 3.7.3
    Numpy  : 1.19.2
    Tango  : 9.3.4
    Boost  : 1.67.0

PyTango runtime is:
    Python : 3.7.3
    Numpy  : 1.19.2
    Tango  : 9.3.4

PyTango running on:
uname_result(system='Linux', node='86032deafb5a', release='4.19.121-linuxkit', version='#1 SMP Thu Jan 21 15:36:34 UTC 2021', machine='x86_64', processor='')
```

### Start an itango session

```shell
docker-compose exec cli itango3

ITango 9.3.3 -- An interactive Tango client.

Running on top of Python 3.7.3, IPython 7.21 and PyTango 9.3.3

help      -> ITango's help system.
object?   -> Details about 'object'. ?object also works, ?? prints more.

IPython profile: tango

hint: Try typing: mydev = Device("<tab>

In [1]: dev = Device("sys/tg_test/1")

In [2]: dev.ping()
Out[2]: 552

In [3]: dev.double_scalar
Out[3]: -57.588745922974105
```

### Register and run a new device

Start the device:
```shell
docker-compose exec cli bash

tango@c5f6dc31dc6b:/training$ cd server/
tango@c5f6dc31dc6b:/training/server$ ./ps0a.py test
The device server PowerSupply/test is not defined in database. Exiting!
tango@c5f6dc31dc6b:/training/server$ tango_admin --add-server PowerSupply/test PowerSupply train/ps/1 
tango@c5f6dc31dc6b:/training/server$ ./ps0a.py test
Ready to accept request
```

While that is running, connect a `DeviceProxy` to it from another ipython session:
```shell
docker-compose exec cli ipython3

Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.21.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import tango

In [2]: dp = tango.DeviceProxy("train/ps/1")

In [3]: dp.ping()
Out[3]: 318

In [4]: dp.voltage
Out[4]: 1.23

```

### Run the power supply simulator, and a device that uses it


Ensure the gevent package is installed:
```shell
docker-compose exec cli pip install gevent

Defaulting to user installation because normal site-packages is not writeable
...
Successfully installed gevent-21.1.2 greenlet-1.1.0 zope.event-4.5.0 zope.interface-5.4.0
```

Start the power supply simulator:
```shell
docker-compose exec cli /training/server/ps-simulator.py

INFO:root:starting simulator...
INFO:simulator.45000:simulator listenning on ('', 45000)!
```

Start the power supply device:
```shell
docker-compose exec cli /training/server/ps1.py test

Ready to accept request
```

While that is running, connect to it from another ipython session:
```shell
docker-compose exec cli ipython3

Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
Type 'copyright', 'credits' or 'license' for more information
IPython 7.21.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import tango

In [2]: dp = tango.DeviceProxy("train/ps/1")

In [3]: dp.voltage
Out[3]: 0.1

In [4]: dp.calibrate()

In [5]:
```

## Webinars

More details of the webinars can be found online.
- 4th Tango Kernel webinar - PyTango:  
  https://www.tango-controls.org/community/news/2021/06/10/4th-tango-kernel-webinar-pytango/
