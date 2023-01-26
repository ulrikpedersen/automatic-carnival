.. highlight:: python
   :linenothreshold: 5

.. _getting-started:

Getting started
===============

Installing
----------

PyPi
~~~~

You can also install the latest version from `PyPi`_.

Install PyTango with pip (common platforms have binary wheels, so no compilation or dependencies required):

.. sourcecode:: console

    $ python -m pip install PyTango

Installation options:

If you are going to utilize gevent green mode of PyTango it is recommended to have a recent version of gevent.
You can force gevent installation with "gevent" keyword:

.. sourcecode:: console

    $ python -m pip install PyTango[gevent]

Linux
~~~~~

PyTango is available on linux as an official debian/ubuntu package (however, this may not be the latest release):

- for Python 3.X:
.. sourcecode:: console

    $ sudo apt-get install python3-tango

RPM packages are also available for RHEL & CentOS:

.. hlist::
   :columns: 2

   * `CentOS 6 32bits <http://pubrepo.maxiv.lu.se/rpm/el6/x86_64/>`_
   * `CentOS 6 64bits <http://pubrepo.maxiv.lu.se/rpm/el6/x86_64/>`_
   * `CentOS 7 64bits <http://pubrepo.maxiv.lu.se/rpm/el7/x86_64/>`_
   * `Fedora 23 32bits <http://pubrepo.maxiv.lu.se/rpm/fc23/i/386/>`_
   * `Fedora 23 64bits <http://pubrepo.maxiv.lu.se/rpm/fc23/x86_64/>`_

Windows
~~~~~~~

First, make sure `Python`_ and `numpy`_ are installed.

PyTango team provides a limited set of binary PyTango distributables for
Windows XP/Vista/7/8. The complete list of binaries can be downloaded from
`PyPI`_.

Select the proper windows package, download it and finally execute the
installion wizard.

Compiling
---------

Linux
~~~~~

Since PyTango 9 the build system used to compile PyTango is the standard python
setuptools.

First, make sure you have the following packages already installed (all of them
are available from the major official distribution repositories):

* ``libtango9``
* `boost-python`_ (including boost-python-dev)
* `numpy`_

Besides the binaries for the three dependencies mentioned above, you also need
the development files for the respective libraries.

You can get the latest ``.tar.gz`` from `PyPI`_ or directly
the latest source checkout:

.. sourcecode:: console

    $ git clone https://gitlab.com/tango-controls/pytango.git
    $ cd pytango
    $ python setup.py build
    $ sudo python setup.py install

This will install PyTango in the system python installation directory.
(Since PyTango9, :ref:`itango` has been removed to a separate project and it will not be installed with PyTango.)
If you whish to install in a different directory, replace the last line with:

.. sourcecode:: console

    $ # private installation to your user (usually ~/.local/lib/python<X>.<Y>/site-packages)
    $ python setup.py install --user

    $ # or specific installation directory
    $ python setup.py install --prefix=/home/homer/local

Windows
~~~~~~~

On windows, PyTango must be built using MS VC++.
Since it is rarely needed and the instructions are so complicated, I have
choosen to place the how-to in a separate text file. You can find it in the
source package under :file:`doc/windows_notes.txt`.

Testing
-------

To test the installation, import ``tango`` and check ``tango.Release.version``:

.. sourcecode:: console

    $ python -c "import tango; print(tango.Release.version)"
    9.4.0

Next steps: Check out the :ref:`pytango-quick-tour`.
