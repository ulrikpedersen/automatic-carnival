.. _to9.4_deps_install:

=============================
Dependencies and installation
=============================

Dependencies
============

PyTango v9.4.0 is the first release which **only** supports Python 3.6 or
higher.  If you haven't moved all your clients and devices to Python 3, now
is the time!

PyTango v9.4.0 moved from `cppTango`_ 9.3.x to at least cppTango 9.4.1.  It
will not run with cppTango 9.4.0 or earlier.

In most cases, your existing PyTango devices and clients will continue to
work as before, however there are important changes.  In the other sections of
the migration guide, you can find the incompatibilities and the necessary migration steps.

Installation
============

Environments created with Python 2 need to be ported to Python 3.
You will need at least Python 3.6 and cppTango 9.4.1.  Python dependencies will be
installed automatically, including `numpy`_ - this is no longer optional, and doesn't
have to be installed before installing PyTango.

The binary wheels on `PyPI`_ and `Conda-forge`_ makes installation very simple on many
platforms.  No need for compilation.  See :ref:`Getting started <getting-started>`.
