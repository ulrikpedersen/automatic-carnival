PyTango
=======

|Doc Status|
|Gitlab Build Status|
|Appveyor Build Status|
|Pypi Version|
|Python Versions|
|Conda|

Main website: http://pytango.readthedocs.io

Python binding for Tango_, a library dedicated to distributed control systems.


Description
-----------

PyTango_ exposes the complete `Tango C++ API`_ through the ``tango`` python module.
It also adds a bit of abstraction by taking advantage of the Python capabilities:

- ``tango.client`` provides a client access to device servers and databases.
- ``tango.server`` provides base classes to declare and run device servers.


Requirements
------------

PyTango_ is compatible with python 3.6+.

General dependencies:

-  cppTango_ >= 9.4.1, and its dependencies: omniORB4 and libzmq
-  `Boost.Python`_ >= 1.71

Python dependencies:

-  numpy_ >= 1.13.3

Build dependencies:

- pypa-build_
- scikit-build-core_

Optional dependencies (test):

- gevent_
- psutil_
- pytest_
- pytest-forked_

.. note:: As a general rule, cppTango_ and pytango_ should share the same major
      and minor version (for a version ``X.Y.Z``, ``X`` and ``Y`` should
      match).
      On some systems you may need to install ``omniORB4`` and ``libzmq`` related
      development packages.


Install
-------

PyTango_ is available on PyPI_ as ``pytango``, with pre-built binaries for some platforms
(you need pip>=19.3, so upgrade first if necessary)::

    $ python -m pip install --upgrade pip
    $ python -m pip install pytango

Alternatively, pre-built PyTango_ binaries can be installed from `Conda Forge_`::

    $ conda install -c conda-forge pytango

For the very latest code, or for development purposes, PyTango_ can be built and installed from the
`sources`_.  This is complicated by the dependencies - see the Getting Started section in the documentation_.

Usage
-----

To test the installation, import ``tango`` and check ``tango.utils.info()``::

    >>> import tango
    >>> print(tango.utils.info())
    PyTango 9.4.2.dev0 (9, 4, 2, 'dev', 0)
    PyTango compiled with:
        Python : 3.11.2
        Numpy  : PYTANGO_NUMPY_VERSION
        Tango  : 9.4.1
        Boost  : 1.81.0

    PyTango runtime is:
        Python : 3.11.2
        Numpy  : 1.24.2
        Tango  : 9.4.1

    PyTango running on:
    uname_result(system='Darwin', node='osloxf01', release='21.6.0', version='Darwin Kernel Version 21.6.0: Mon Dec 19 20:43:09 PST 2022; root:xnu-8020.240.18~2/RELEASE_ARM64_T6000', machine='arm64')

For an interactive use, consider using ITango_, a tango IPython_ profile.


Documentation
-------------

Check out the documentation_ for more information.



Support and contribution
------------------------

You can get support from the `Tango forums`_, for both Tango_ and PyTango_ questions.

All contributions,  `PR and bug reports`_ are welcome, please see: `How to Contribute`_ !


.. |Doc Status| image:: https://readthedocs.org/projects/pytango/badge/?version=latest
                :target: http://pytango.readthedocs.io/en/latest
                :alt:

.. |Gitlab Build Status| image:: https://img.shields.io/gitlab/pipeline-status/tango-controls/pytango?branch=develop&label=develop
                         :target: https://gitlab.com/tango-controls/pytango/-/pipelines?page=1&scope=branches&ref=develop
                         :alt:

.. |Appveyor Build Status| image:: https://img.shields.io/appveyor/build/ajoubertza/pytango-0h1yy/develop?label=develop%20%28Windows%29
                           :target: https://ci.appveyor.com/project/ajoubertza/pytango-0h1yy/branch/develop
                           :alt:

.. |Pypi Version| image:: https://img.shields.io/pypi/v/PyTango.svg
                  :target: https://pypi.python.org/pypi/PyTango
                  :alt:

.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/PyTango.svg
                     :target: https://pypi.python.org/pypi/PyTango/
                     :alt:

.. |Conda| image:: https://img.shields.io/conda/v/conda-forge/pytango
                    :target: https://anaconda.org/conda-forge/pytango
                    :alt:

.. _Tango: http://tango-controls.org
.. _Tango C++ API: https://tango-controls.github.io/cppTango-docs/index.html
.. _PyTango: http://gitlab.com/tango-controls/pytango
.. _PyPI: http://pypi.python.org/pypi/pytango
.. _Conda Forge: https://anaconda.org/conda-forge/pytango
.. _scikit-build-core: https://github.com/scikit-build/scikit-build-core
.. _pypa-build: https://github.com/pypa/build

.. _cppTango: https://gitlab.com/tango-controls/cppTango
.. _libtango: http://tango-controls.org/downloads
.. _Boost.Python: https://www.boost.org/doc/libs/release/libs/python/doc/html/index.html
.. _numpy: http://pypi.python.org/pypi/numpy
.. _packaging: http://pypi.python.org/pypi/packaging
.. _psutil: http://pypi.python.org/pypi/psutil
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _gevent: http://pypi.python.org/pypi/gevent
.. _pytest: https://docs.pytest.org/en/latest/
.. _pytest-forked: https://github.com/pytest-dev/pytest-forked
.. _psutil: https://github.com/giampaolo/psutil

.. _ITango: http://pypi.python.org/pypi/itango
.. _IPython: http://ipython.org

.. _documentation: http://pytango.readthedocs.io/en/latest
.. _Tango forums: http://tango-controls.org/community/forum
.. _PR and bug reports: PyTango_
.. _sources: PyTango_
.. _How to Contribute: http://pytango.readthedocs.io/en/latest/how-to-contribute.html#how-to-contribute
