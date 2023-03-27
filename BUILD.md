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

New build system: how to build the wheel
========================================
Pytango can be built into a distribution package using the build system provided. The build sytstem is based
on a few development tools, mainly:

* cmake - for building the c++ code and pulling in dependency configurations
* python build - the (new) standard build interface in python world
* scikit-build-core - provides glue to seamlessly invoke cmake builds from a python build

Assuming the library dependencies are already installed on your host (see [above](#pytango-library-dependencies)), you should create a python virtualenv for the build. This virtualenv can be very small because scikit-build-core actually creates its own virtualenv in the background (in /tmp) where the pytango build requirements are pulled in.

The following is a quick summary of how to build and check the pytango wheel. Assuming workstation environment is appropriately configred with pre-installed dependencies.

In brief, the steps are essentially:
1. Clone the pytango repo
2. Setup a virtual environment
3. Build the wheel using build and scikit-build-core
4. Generate the wheel with batteries (i.e. pull dependency libraries into a wheel)
5. Install the wheel
6. Test the wheel

Steps 1-3:  configure your environment and build the basic wheel (using scikit-build-core and cmake under the hood)
```shell
git clone git@gitlab.com:tango-controls/pytango.git
cd pytango
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip build clang-tidy clang-format numpy scikit-build-core
# Setting the TANGO_ROOT variable is only required for a non-standard system install of cppTango
TANGO_ROOT=/path/to/installed/tango.9.4 python3 -m build
# Check what has been built:
ls dist/
# Further check what is in the wheel if you're really curious:
unzip dist/*.whl
```

Step 4: pull the dependency libraries into a (new) wheel. This step is platform-dependent.
On Linux:
```shell
# on Linux only
pip install auditwheel 
# LD_LIBRARY_PATH only required if Tango is installed in a non-standard location
LD_LIBRARY_PATH=/path/to/installed/tango.9.4/lib/ auditwheel repair dist/pytango*.whl  
ls wheelhouse/
```

On MacOS:
```shell
# on MacOS only
pip install delocate 
# DYLD_LIBRARY_PATH only required if Tango is installed in a non-standard location
$ DYLD_LIBRARY_PATH=/path/to/installed/tango.9.4/lib/ delocate-wheel -w wheelhouse/ -v dist/pytango*.whl
ls wheelhouse/
```

Step 5-6: Installing and checking the wheel package. 
```shell
# install the wheel with batteries
python -m pip install --prefer-binary wheelhouse/pytango*.whl
# Tests need to run somewhere not in the root of the pytango repo since the source code is located in a folder named `tango` and conflicts with the module name.
mkdir tmp && cd tmp/
python -c "import tango; print(tango.utils.info())"
```

Advanced Build Configuration
============================

The following information is intended for maintainers of pytango that may need to dive deeper into the depths of the build system.

cmake configuration options
---------------------------

cmake can be used with all of its standard configuration options for different types of builds, etc.

Specific to this project, the following cmake cache variables can be used to hint at where to find dependencies, these can also defined and read from the environment although the cache (i.e. cmake `-D` option) will take precedence):

* **TANGO_ROOT** - Set this to the path where cppTango is installed IF not in a system path. This is handed as a hint to pkg-config.
* **PYTHON_ROOT** - Use this if you have multiple python installations. Set to the root path where the particular version of python is installed.
* **BOOST_PYTHON_SUFFIX** - By default is 3 and works for modern platforms. Set this only if you have problems with finding boost python (i.e. if your boost version is <1.73, in this case set to '38' or whatever python version you have) A warning about mismatching python and python.boost versions will be printed by cmake.

Other environment variables can also be used to control aspects of the build:
* **CMAKE_ARGS** - use this to set flags/options that are used by scikit-build-core when invoking cmake.
* **CMAKE_GENERATOR** - for example chose between "Unix Makefiles" (default) and "Ninja".

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
pip install clang-tidy clang-format numpy
pip list
Package      Version
------------ --------
clang-format 15.0.7
clang-tidy   15.0.2.1
ninja        1.11.1
numpy        1.24.1
pip          22.3.1
setuptools   65.6.3

pip install cmake   # ONLY IF CMAKE IS NOT ALREADY AVAILABLE
```

If you **do** have the `CMakeUserPresets.json` file in the root of the project, then configure, build the `_pytango.so` library in "Debug" mode in the `cmakebuild/dev/` directory and (optionally) install it:
```shell
mkdir install  # optional: if you want to test installed lib locally

cmake --preset=dev -DCMAKE_INSTALL_PREFIX=$(pwd)/install  # configuring - the install prefix is optional
cmake --build --preset=dev   # building
cmake --build --preset=dev --target install  # optionally install the library

ls install/pytango/
_pytango.9.4.0.so _pytango.9.so     _pytango.so

```

If you do **not** have the `CMakeUserPresets.json` in the root of the project (i.e. if you're in a hurry or on a CI platform) then configure, build and install is a little more manual but you can fall back on the available `ci-<platform>` presets where `<platform>` can be one of the following:
 * ci-macOS
 * ci-Linux
 * ci-Windows

Assuming that you do have the virtualenv defined as above (or all tools _somehow_ available), you can build a CI configuration which will build `_pytango.so` in "Release" mode in the `cmakebuild/` directory:
```shell
cmake --preset=ci-macOS -DTANGO_ROOT=/path/to/installed/tango.9.4
cmake --build --preset=dev

```



### Configuration options
The above python wheel build is the most basic form of build. There are many ways to tweak and configure the build.

It is also possible to invoke a set of defined cmake presets from `CMakePresets.json` by using the `CMAKE_ARGS` environment variable. This may be convenient to store CI configurations for cmake in one place and leave the CI yaml definitions quite simple (i.e. TANGO_ROOT could be defined in `CMakePresets.json`):

```shell
CMAKE_ARGS="--preset=ci-macOS" python3 -m build
```

NOTE that you cannot reference presets from your own `CMakeUserPresets.json` as it is not packaged with the PyTango source distribution and not available in the temporary virtualenv that scikit-build-core creates.