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

The `ext/` dir contains the source code for the pytango bindings to the cppTango C++ library.
These python bindings are generated using Boost Python and built using cmake.

The C++ code has dependencies on:
 * Tango (cppTango) & its dependencies...
 * Python
 * Boost Python
 * NumPy

In addition the build system requires a development environment with the following tools:
 * cmake (>=3.16 - the newer the better)
 * python (>= 3.8 - the newer the better)
 * clang-format
 * clang-tidy
 * ninja
 * pkg-config

(the latter 3 are not *strictly* required but the build system is configured by default to expect these)

The following example shows how to build _just_ the C++ code into a shared object called `_pytango.so`.
The example uses a python virtualenv in order to pull together an up-to-date build environment which developers are encouraged to use.

Pre-amble: setup the environment.
First check that you have a recent cmake (>= 3.16) installed:
```shell
ulrik@osloxf01 home $ cd pytango
ulrik@osloxf01 pytango $ cmake --version
cmake version 3.25.1

CMake suite maintained and supported by Kitware (kitware.com/cmake).
```

If you don't have cmake already then you can install it in a python virtualenv (see below). NOTE: only `pip install cmake`
IF you don't have cmake in your environment. Otherwise they can conflict and cause difficult-to-track errors.

We create a python virtualenv in order to conveniently pull in some recent versions of useful developer tools:
```shell
cd pytango/   # if you're not already here...
ulrik@osloxf01 pytango $ python3.11 -m venv venv
ulrik@osloxf01 pytango $ source venv/bin/activate
(venv) ulrik@osloxf01 pytango $ pip install clang-tidy clang-format numpy
(venv) ulrik@osloxf01 pytango $ pip list
Package      Version
------------ --------
clang-format 15.0.7
clang-tidy   15.0.2.1
ninja        1.11.1
numpy        1.24.1
pip          22.3.1
setuptools   65.6.3

(venv) ulrik@osloxf01 pytango $ pip install cmake   # ONLY IF CMAKE IS NOT ALREADY AVAILABLE
```

If you **do** have the `CMakeUserPresets.json` file in the root of the project, then configure, build the `_pytango.so` library in "Debug" mode in the `cmakebuild/dev/` directory and (optionally) install it:
```shell
(venv) ulrik@osloxf01 pytango $ mkdir install  # optional: if you want to test installed lib locally

(venv) ulrik@osloxf01 pytango $ cmake --preset=dev -DCMAKE_INSTALL_PREFIX=$(pwd)/install  # configuring - the install prefix is optional
(venv) ulrik@osloxf01 pytango $ cmake --build --preset=dev   # building
(venv) ulrik@osloxf01 pytango $ cmake --build --preset=dev --target install  # optionally install the library

(venv) ulrik@osloxf01 pytango $ ls install/pytango/
_pytango.9.4.0.so _pytango.9.so     _pytango.so

```

If you do **not** have the `CMakeUserPresets.json` in the root of the project (i.e. if you're in a hurry or on a CI platform) then configure, build and install is a little more manual but you can fall back on the available `ci-<platform>` presets where `<platform>` can be one of the following:
 * ci-macOS
 * ci-Linux
 * ci-Windows

Assuming that you do have the virtualenv defined as above (or all tools _somehow_ available), you can build a CI configuration which will build `_pytango.so` in "Release" mode in the `cmakebuild/` directory:
```shell
(venv) ulrik@osloxf01 pytango $ cmake --preset=ci-macOS -DTANGO_ROOT=/path/to/installed/tango.9.4
(venv) ulrik@osloxf01 pytango $ cmake --build --preset=dev

```
