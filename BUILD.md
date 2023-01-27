Building pytango
================

This document is intended for maintainers, developers and distribution/package builders.

A number of practical use-cases for building pytango or parts of it are described here.

Developers platforms
--------------------

We all have our favorite brand of laptop, desktop, server and distro... Embrace the diversity - it forces us to think outside of our own particular box!

In random order:

### MacOS

I recommend switching from the default 'zsh' Terminal to using 'bash' by default. It is perhaps not strictly necessary as zsh is mostly backwards compatible - but it does occasionally cause some hard-to understand issues.

These instructions should work for both Intel (x86_64) and Apple (arm64) Silicon. Tested primarily on Monterey (M1).

Install [Homebrew](https://brew.sh/) if you do not already have it! You practically can't develop software on a Mac without it (and if you can then you're amazing and don't need these instructions)

The order here doesn't really matter. But first some tooling:
```shell
brew install coreutils cppcheck git lcov pkg-config python@3.11
```

Then some Tango/PyTango library dependencies:
```shell
brew install boost boost-python3 cppzmq jpeg-turbo omniorb zeromq
```

### Docker container in vscode

See the `.devcontainer/README.md`

### Ubuntu

See the `.devcontainer/Dockerfile` for how to install the dependencies - or just build and use the Docker image directly.

### Windows

Uhm. Todo. Help?

cmake configuration options
---------------------------

cmake can be used with all of its standard configuration options for different types of builds, etc.

Specific to this project, the following cmake cache variables can be used to hint at where to find dependencies:

 * **TANGO_ROOT** - set this to the path where cppTango is installed IF not in a system path. This is handed as a hint to pkg-config.
 * **BOOST_PYTHON_SUFFIX** - by default is 3 and works for modern platforms. Set this only if you have problems with finding boost python (i.e. if your boost version is <1.73, in this case set to '38' or whatever python version you have)

### Use a [CMakeUserPresets.json](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html) file

This is a file that a developer can use to setup their local development environment and configuration options. This will inevitably be workstation-dependent and should **not** be committed to source control.

A recommended example to get started with (replace with TANGO_ROOT entry):
```json
{
  "version": 2,
  "cmakeMinimumRequired": {
    "major": 3,
    "minor": 16,
    "patch": 0
  },
  "configurePresets": [
    {
      "name": "dev-common",
      "hidden": true,
      "inherits": ["dev-mode", "clang-tidy", "cppcheck"]
    },
    {
      "name": "dev-unix",
      "binaryDir": "${sourceDir}/cmakebuild/dev-unix",
      "inherits": ["dev-common", "ci-unix"],
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
      }
    },
    {
      "name": "dev",
      "binaryDir": "${sourceDir}/cmakebuild/dev",
      "inherits": "dev-unix",
      "cacheVariables": {
        "TANGO_ROOT": "/path/to/installed/tango.9.4"
      }
    }
  ],
  "buildPresets": [
    {
      "name": "dev",
      "configurePreset": "dev",
      "configuration": "Debug",
      "jobs": 8
    }
  ]
}
```

Building the CPP source code
----------------------------
Please note that the instructions in this section are for developers/maintainers of the C++
extension code. Python developers/users/packagers do **not** need to invoke cmake directly
in order to build pytango. See the next section for python build instructions.

The `ext/` dir contains the source code for the pytango bindings to the cppTango C++ library.
These python bindings are generated using Boost Python and built using cmake.

### PyTango library dependencies
The C++ code has dependencies on:
 * Tango (cppTango) & its dependencies...
 * Python
 * Boost Python
 * NumPy

### PyTango Build System Dependencies
In addition the build system requires a development environment with the following tools:
 * cmake (>=3.16 - the newer the better)
 * python (>= 3.8 - the newer the better)
 * clang-format
 * clang-tidy
 * ninja
 * pkg-config

(the latter 3 are not *strictly* required but the build system is configured by default to expect these)

### Example build 
The following example shows how to build _just_ the C++ code into a shared object called `_pytango.so`.
The example uses a python virtualenv in order to pull together an up-to-date build environment which developers are encouraged to use.

Pre-amble: setup the environment.
First check that you have a recent cmake (>= 3.16) installed:
```shell
user@computer home $ cd pytango
user@computer pytango $ cmake --version
cmake version 3.25.1

CMake suite maintained and supported by Kitware (kitware.com/cmake).
```

If you don't have cmake already then you can install it in a python virtualenv (see below). NOTE: only `pip install cmake`
IF you don't have cmake in your environment. Otherwise they can conflict and cause difficult-to-track errors.

We create a python virtualenv in order to conveniently pull in some recent versions of useful developer tools:
```shell
cd pytango/   # if you're not already here...
user@computer pytango $ python3.11 -m venv venv
user@computer pytango $ source venv/bin/activate
(venv) user@computer pytango $ pip install clang-tidy clang-format numpy
(venv) user@computer pytango $ pip list
Package      Version
------------ --------
clang-format 15.0.7
clang-tidy   15.0.2.1
ninja        1.11.1
numpy        1.24.1
pip          22.3.1
setuptools   65.6.3

(venv) user@computer pytango $ pip install cmake   # ONLY IF CMAKE IS NOT ALREADY AVAILABLE
```

If you **do** have the `CMakeUserPresets.json` file in the root of the project, then configure, build the `_pytango.so` library in "Debug" mode in the `cmakebuild/dev/` directory and (optionally) install it:
```shell
(venv) user@computer pytango $ mkdir install  # optional: if you want to test installed lib locally

(venv) user@computer pytango $ cmake --preset=dev -DCMAKE_INSTALL_PREFIX=$(pwd)/install  # configuring - the install prefix is optional
(venv) user@computer pytango $ cmake --build --preset=dev   # building
(venv) user@computer pytango $ cmake --build --preset=dev --target install  # optionally install the library

(venv) user@computer pytango $ ls install/pytango/
_pytango.9.4.0.so _pytango.9.so     _pytango.so

```

If you do **not** have the `CMakeUserPresets.json` in the root of the project (i.e. if you're in a hurry or on a CI platform) then configure, build and install is a little more manual but you can fall back on the available `ci-<platform>` presets where `<platform>` can be one of the following:
 * ci-macOS
 * ci-Linux
 * ci-Windows

Assuming that you do have the virtualenv defined as above (or all tools _somehow_ available), you can build a CI configuration which will build `_pytango.so` in "Release" mode in the `cmakebuild/` directory:
```shell
(venv) user@computer pytango $ cmake --preset=ci-macOS -DTANGO_ROOT=/path/to/installed/tango.9.4
(venv) user@computer pytango $ cmake --build --preset=dev

```

Building the python package
---------------------------

Pytango can be built into a distribution package using the build system provided. The build sytstem is based
on a few development tools, mainly:

* cmake - for building the c++ code and pulling in dependency configurations
* python build - the (new) standard build interface in python world
* scikit-build-core - provides glue to seamlessly invoke cmake builds from a python build

Assuming the library dependencies are already installed on your host (see [above](#pytango-library-dependencies)), you should create a python virtualenv for the build. This virtualenv can be very small because scikit-build-core actually creates its own virtualenv in the background (in /tmp) where the pytango build requirements are pulled in.

```shell
user@computer pytango $ python3.11 -m venv buildvenv
user@computer pytango $ source buildvenv/bin/activate
(buildvenv) user@computer pytango $ pip install pip install build scikit-build-core
...
(buildvenv) user@computer pytango $ pip list
Package           Version
----------------- -------
build             0.10.0
install           1.3.5
packaging         23.0
pip               22.3.1
pyproject_hooks   1.0.0
scikit_build_core 0.1.5
setuptools        65.6.3

# Setting the TANGO_ROOT variable is only required for a non-standard system install of cppTango
(buildvenv) user@computer pytango $ TANGO_ROOT=/path/to/installed/tango.9.4 python3 -m build
...
[100%] Built target pytango_tango
*** Installing project into wheel...
-- Install configuration: "Release"
-- Installing: /var/folders/gp/7q57_wf53bs1_v04jvt52rm40000gn/T/tmparowuq1s/wheel/platlib/tango/_tango.9.4.0.so
-- Installing: /var/folders/gp/7q57_wf53bs1_v04jvt52rm40000gn/T/tmparowuq1s/wheel/platlib/tango/_tango.9.so
-- Installing: /var/folders/gp/7q57_wf53bs1_v04jvt52rm40000gn/T/tmparowuq1s/wheel/platlib/tango/_tango.so
*** Making wheel...
Successfully built pytango-9.4.0.tar.gz and pytango-9.4.0-cp311-cp311-macosx_12_0_arm64.whl
(buildvenv) user@computer pytango $ ls dist
pytango-9.4.0-cp311-cp311-macosx_12_0_arm64.whl pytango-9.4.0.tar.gz

```

### Configuration options
The above build is the most basic form of build. There are many ways to tweak and configure the build.

Environment variables can be used to point to non-standard/non-system installed versions of boost, python and tango:
* TANGO_ROOT
* BOOST_ROOT
* PYTHON_ROOT

Other environment variables can also be used to control aspects of the build:
* CMAKE_ARGS - use this to set flags/options that are used by scikit-build-core when invoking cmake.
* CMAKE_GENERATOR - for example chose between "Unix Makefiles" (default) and "Ninja".
* BOOST_PYTHON_SUFFIX - Sets the suffix on the Boost Python component to search for (default is 3). Set this if your Boost version is < 1.73 OR if you have multiple installations of python.

It is also possible to invoke a set of defined cmake presets from `CMakePresets.json` by using the `CMAKE_ARGS` environment variable. This may be convenient to store CI configurations for cmake in one place and leave the CI yaml definitions quite simple (i.e. TANGO_ROOT could be defined in `CMakePresets.json`):

```shell
(buildvenv) user@computer pytango $ CMAKE_ARGS="--preset=ci-macOS" python3 -m build
```

NOTE that you cannot reference presets from your own `CMakeUserPresets.json` as it is not packaged with the PyTango source distribution and not available in the temporary virtualenv that scikit-build-core creates.