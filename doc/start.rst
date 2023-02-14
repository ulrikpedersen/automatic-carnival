.. highlight:: python
   :linenothreshold: 10

.. _getting-started:

Getting started
===============

The first section show the easy way, with pre-compiled packages.  If that doesn't work, or you
need to compile from source, see the second section.

.. contents:: Contents
   :depth: 1
   :local:
   :backlinks: none

Installing pre-compiled packages (easy)
---------------------------------------

PyPI (Linux, Windows)
~~~~~~~~~~~~~~~~~~~~~~~~

You can install the latest version from `PyPI`_.

Install PyTango with pip (common platforms have binary wheels, so no compilation or dependencies required):

.. sourcecode:: console

    $ python -m pip install pytango

If this step downloads a ``.tar.gz`` file instead of a ``.whl`` file, then we don't have a binary package
for your platform.  Try Conda.

If you are going to utilize the gevent green mode of PyTango it is recommended to have a recent version of gevent.
You can force gevent installation with the "gevent" keyword:

.. sourcecode:: console

    $ python -m pip install pytango[gevent]

Conda (Linux, Windows, MacOS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install the latest version from `Conda-forge`_.

Conda-forge provides binary wheels for different platforms, compared to `PyPI`_.
MacOS binaries are available since version 9.4.0.

If you don't already have conda, try the `Mambaforge`_ installer (an alternative installer to `Miniconda`_).

To install PyTango in a new conda environment (you can choose a different version of Python):

.. sourcecode:: console

    $ conda create --channel conda-forge --name pytango-env python=3.11 pytango
    $ conda activate pytango-env

Other useful packages on conda-forge include:  ``tango-test``, ``jive`` and ``tango-database``.

Linux
~~~~~

PyTango is available on linux as an official debian/ubuntu package (however, this may not be the latest release):

For Python 3:

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

First, make sure `Python`_  is installed.  Then follow the same instructions as for `PyPI`_ above.
There are binary wheels for some Windows platforms available.

Building and installing from source (hard)
------------------------------------------

This is the more complicated option, as you need to have all the correct dependencies and build tools
installed.

Conda
~~~~~

The basic steps are shown below (specify your Python version).

.. sourcecode:: console

   $ conda create -n pytangodev -c conda-forge boost cpptango cppzmq cxx-compiler numpy pkg-config psutil python=3.11
   $ conda activate pytangodev
   $ git clone https://gitlab.com/tango-controls/pytango.git
   $ cd pytango
   $ export BOOST_ROOT=$CONDA_PREFIX TANGO_ROOT=$CONDA_PREFIX ZMQ_ROOT=$CONDA_PREFIX OMNI_ROOT=$CONDA_PREFIX
   $ python setup.py build
   $ python setup.py install

For more variations, see the folder ``.devcontainer`` in the root of the source repository
with an example of the compilation in a Docker container.  The ``.gitlab-ci.yml``
file in the source repo is another good reference for Conda-based compilation.

Linux
~~~~~

Since PyTango 9 the build system used to compile PyTango is the standard python
setuptools.

First, make sure you have the following packages already installed (all of them
are available from the major official distribution repositories):

* libtango9 from `cppTango`_.
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
If you wish to install in a different directory, replace the last line with:

.. sourcecode:: console

    $ # private installation to your user (usually ~/.local/lib/python<X>.<Y>/site-packages)
    $ python setup.py install --user

    $ # or specific installation directory
    $ python setup.py install --prefix=/home/homer/local

.. note::
   For custom `boost-python`_ installation locations, environment variables can be used
   to modify the default paths.  See the description of the ``BOOST_ROOT`` and related
   variables in the ``setup.py`` file.

Windows
~~~~~~~

On windows, PyTango must be built using MS VC++.
Since it is rarely needed and the instructions are so complicated, I have
choosen to place the how-to in a separate text file. You can find it in the
source package under :file:`doc/windows_notes.txt`.

MacOS
~~~~~

Compilation of cppTango and PyTango directly on MacOS is non-trivial.  Rather use a Conda environment
to compile PyTango.  If you really want to try it, see https://gitlab.com/tjuerges/build_tango for
some guidelines.  Also take note of the `patch required <https://gitlab.com/tango-controls/tango-doc/-/issues/387>`_
for omniorb <= 4.2.5 on Apple Silicon.

Basic installation check
------------------------

To test the installation, import ``tango`` and check ``tango.Release.version``:

.. sourcecode:: console

    $ cd  # move to a folder that doesn't contain the source code, if you built it
    $ python -c "import tango; print(tango.Release.version)"
    9.4.0

Next steps: Check out the :ref:`pytango-quick-tour`.
