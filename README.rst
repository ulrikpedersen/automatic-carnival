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
It also adds a bit of abstraction by taking advantage of the Python capabilites:

- ``tango.client`` provides a client access to device servers and databases.
- ``tango.server`` provides base classes to declare and run device servers.


Requirements
------------

PyTango_ is compatible with python 2 and python 3.

General dependencies:

-  libtango_ >= 9.3, and its dependencies: omniORB4 and libzmq
-  `Boost.Python`_ >= 1.33

Python dependencies:

-  numpy_ >= 1.1
-  six_ >= 1.10

Build dependencies:

- setuptools_

Optional dependencies:

- futures_
- gevent_

.. note:: As a general rule, libtango_ and pytango_ should share the same major
      and minor version (for a version ``X.Y.Z``, ``X`` and ``Y`` should
      match).
      On some systems you may need to install ``libtango``, ``omniORB4`` and ``libzmq`` related
      development packages.


Install
-------

PyTango_ is available on PyPI_ as ``pytango``::

    $ pip install pytango

Alternatively, PyTango_ can be built and installed from the
`sources`_::

    $ python setup.py install

In both cases, the installation takes a few minutes since the ``_tango`` boost
extension has to compile.

.. note::
   For custom `Boost.Python`_ installation locations, environment variables can be used
   to modify the default paths.  See the description of the ``BOOST_ROOT`` and related
   variables in the ``setup.py`` file.

Usage
-----

To test the installation, import ``tango`` and check ``tango.utils.info()``::

    >>> import tango
    >>> print(tango.utils.info())
    PyTango 9.3.4 (9, 3, 4)
    PyTango compiled with:
        Python : 3.8.5
        Numpy  : 1.19.2
        Tango  : 9.3.4
        Boost  : 1.73.0

    PyTango runtime is:
        Python : 3.8.5
        Numpy  : 1.19.2
        Tango  : 9.3.4

    PyTango running on:
    uname_result(system='Linux', node='ed71265a2807', release='4.19.76-linuxkit', version='#1 SMP Tue May 26 11:42:35 UTC 2020', machine='x86_64', processor='')

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
.. _PyTango: http://gitlab.com/tango-cs/pytango
.. _PyPI: http://pypi.python.org/pypi/pytango

.. _libtango: http://tango-controls.org/downloads
.. _Boost.Python: https://www.boost.org/doc/libs/release/libs/python/doc/html/index.html
.. _numpy: http://pypi.python.org/pypi/numpy
.. _six: http://pypi.python.org/pypi/six
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _futures: http://pypi.python.org/pypi/futures
.. _gevent: http://pypi.python.org/pypi/gevent

.. _ITango: http://pypi.python.org/pypi/itango
.. _IPython: http://ipython.org

.. _documentation: http://pytango.readthedocs.io/en/latest
.. _Tango forums: http://tango-controls.org/community/forum
.. _PR and bug reports: PyTango_
.. _sources: PyTango_
.. _How to Contribute: http://pytango.readthedocs.io/en/latest/how-to-contribute.html#how-to-contribute
