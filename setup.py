# ------------------------------------------------------------------------------
# This file is part of PyTango (http://pytango.rtfd.io)
#
# Copyright 2006-2012 CELLS / ALBA Synchrotron, Bellaterra, Spain
# Copyright 2013-2014 European Synchrotron Radiation Facility, Grenoble, France
#
# Distributed under the terms of the GNU Lesser General Public License,
# either version 3 of the License, or (at your option) any later version.
# See LICENSE.txt for more info.
# ------------------------------------------------------------------------------

# pylint: disable=deprecated-method

import os
import sys
import runpy
import struct
import subprocess
import json

from ctypes.util import find_library

from setuptools import setup, Extension
from setuptools import Command
from setuptools.command.build_ext import build_ext as dftbuild_ext
from setuptools.command.install import install

from distutils.command.build import build as dftbuild
from distutils.unixccompiler import UnixCCompiler
from distutils.version import LooseVersion as V

# numpy is only required when compiling, not when building the sdist for example
try:
    import numpy
except ImportError:
    numpy = None

# Platform constants
POSIX = "posix" in os.name
MACOS = "darwin" in os.sys.platform
WINDOWS = "nt" in os.name
IS64 = 8 * struct.calcsize("P") == 64
PYTHON_VERSION = sys.version_info

# Arguments
TESTING = any(x in sys.argv for x in ["test", "pytest"])


try:
    from numpy.distutils.ccompiler import CCompiler_compile
    import distutils.ccompiler
    distutils.ccompiler.CCompiler.compile = CCompiler_compile
    print("Using numpy-patched parallel compiler")
except ImportError:
    pass


def get_readme(name="README.rst"):
    """Get readme file contents without the badges."""
    with open(name) as f:
        return "\n".join(
            line
            for line in f.read().splitlines()
            if not line.startswith("|") or not line.endswith("|")
        )


def pkg_config(*packages, **config):
    config_map = {
        "-I": "include_dirs",
        "-L": "library_dirs",
        "-l": "libraries",
    }
    cmd = [
        "pkg-config",
        "--cflags-only-I",
        "--libs-only-L",
        "--libs-only-l",
        " ".join(packages),
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    result = proc.wait()
    result = str(proc.communicate()[0].decode("utf-8"))
    for elem in result.split():
        flag, value = elem[:2], elem[2:]
        config_values = config.setdefault(config_map.get(flag), [])
        if value not in config_values:
            config_values.append(value)
    return config


def abspath(*path):
    """A method to determine absolute path for a given relative path to the
    directory where this setup.py script is located"""
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(setup_dir, *path)


def get_release_info():
    namespace = runpy.run_path(abspath("tango/release.py"), run_name="tango.release")
    return namespace["Release"]


def uniquify(seq):
    no_dups = []
    for elem in seq:
        if elem not in no_dups:
            no_dups.append(elem)
    return no_dups


def add_lib(name, dirs, sys_libs, env_name=None, lib_name=None, inc_suffix=None):
    if env_name is None:
        env_name = name.upper() + "_ROOT"
    ENV = os.environ.get(env_name)
    if lib_name is None:
        lib_name = name
    if ENV is None:
        sys_libs.append(lib_name)
        return
    else:
        inc_dir = os.path.join(ENV, "include")
        dirs["include_dirs"].append(inc_dir)
        if inc_suffix is not None:
            inc_dir = os.path.join(inc_dir, inc_suffix)
            dirs["include_dirs"].append(inc_dir)

        lib_dirs = [os.path.join(ENV, "lib")]
        if IS64:
            lib64_dir = os.path.join(ENV, "lib64")
            if os.path.isdir(lib64_dir):
                lib_dirs.insert(0, lib64_dir)
        dirs["library_dirs"].extend(lib_dirs)

        if lib_name.startswith("lib"):
            lib_name = lib_name[3:]
        dirs["libraries"].append(lib_name)


def add_lib_boost(dirs):
    """Add boost-python configuration details.

    There are optional environment variables that can be used for
    non-standard boost installations.

    The BOOST_ROOT can be used for a custom boost installation in
    a separate directory, like:

        /opt/my_boost
            |- include
            |- lib

    In this case, use:

        BOOST_ROOT=/opt/my_boost

    Alternatively, the header and library folders can be specified
    individually (do not set BOOST_ROOT).  For example, if the
    python.hpp file is in /usr/local/include/boost123/boost/:

        BOOST_HEADERS=/usr/local/include/boost123

    If the libboost_python.so file is in /usr/local/lib/boost123:

        BOOST_LIBRARIES=/usr/local/lib/boost123

    Lastly, the boost-python library name can be specified, if the
    automatic detection is not working.  For example, if the
    library is libboost_python_custom.so, then use:

        BOOST_PYTHON_LIB=boost_python_custom

    """

    BOOST_ROOT = os.environ.get("BOOST_ROOT")
    BOOST_HEADERS = os.environ.get("BOOST_HEADERS")
    BOOST_LIBRARIES = os.environ.get("BOOST_LIBRARIES")
    BOOST_PYTHON_LIB = os.environ.get("BOOST_PYTHON_LIB")
    boost_library_name = BOOST_PYTHON_LIB if BOOST_PYTHON_LIB else "boost_python"
    if BOOST_ROOT is None:
        if POSIX and not BOOST_PYTHON_LIB:
            # library name differs widely across distributions, so if it
            # wasn't specified as an environment var, then try the
            # various options, being as Python version specific as possible
            suffixes = [
                "{v[0]}{v[1]}".format(v=PYTHON_VERSION),
                "-{v[0]}{v[1]}".format(v=PYTHON_VERSION),
                "-py{v[0]}{v[1]}".format(v=PYTHON_VERSION),
                "{v[0]}-py{v[0]}{v[1]}".format(v=PYTHON_VERSION),
                "{v[0]}".format(v=PYTHON_VERSION),
                "",
            ]
            for suffix in suffixes:
                candidate = boost_library_name + suffix
                if find_library(candidate):
                    boost_library_name = candidate
                    break
        if BOOST_HEADERS:
            dirs["include_dirs"].append(BOOST_HEADERS)
        if BOOST_LIBRARIES:
            dirs["library_dirs"].append(BOOST_LIBRARIES)
    else:
        inc_dir = os.path.join(BOOST_ROOT, "include")
        lib_dirs = [os.path.join(BOOST_ROOT, "lib")]
        if IS64:
            lib64_dir = os.path.join(BOOST_ROOT, "lib64")
            if os.path.isdir(lib64_dir):
                lib_dirs.insert(0, lib64_dir)

        dirs["include_dirs"].append(inc_dir)
        dirs["library_dirs"].extend(lib_dirs)

    dirs["libraries"].append(boost_library_name)


class build(dftbuild):

    user_options = list(dftbuild.user_options)

    # Strip library option
    user_options.append(
        (
            "strip-lib",
            None,
            "strips the shared library of debugging symbols"
            " (Unix like systems only)",
        )
    )

    boolean_options = dftbuild.boolean_options + ["strip-lib"]

    def initialize_options(self):
        dftbuild.initialize_options(self)
        self.strip_lib = None
        self.no_doc = None

    def finalize_options(self):
        dftbuild.finalize_options(self)

    def run(self):
        dftbuild.run(self)
        if self.strip_lib:
            self.strip_debug_symbols()

    def strip_debug_symbols(self):
        if not POSIX:
            return
        if os.system("type objcopy") != 0:
            return
        d = abspath(self.build_lib, "tango")
        orig_dir = os.path.abspath(os.curdir)
        so = "_tango.so"
        dbg = so + ".dbg"
        try:
            os.chdir(d)
            stripped_cmd = 'file %s | grep -q "not stripped" || exit 1' % so
            not_stripped = os.system(stripped_cmd) == 0
            if not_stripped:
                os.system("objcopy --only-keep-debug %s %s" % (so, dbg))
                os.system("objcopy --strip-debug --strip-unneeded %s" % (so,))
                os.system("objcopy --add-gnu-debuglink=%s %s" % (dbg, so))
                os.system("chmod -x %s" % (dbg,))
        finally:
            os.chdir(orig_dir)


class build_ext(dftbuild_ext):
    def build_extensions(self):
        self.use_cpp_0x = False
        if isinstance(self.compiler, UnixCCompiler):
            compiler_pars = self.compiler.compiler_so
            while "-Wstrict-prototypes" in compiler_pars:
                del compiler_pars[compiler_pars.index("-Wstrict-prototypes")]
            # self.compiler.compiler_so = " ".join(compiler_pars)

            # mimic tango check to activate C++0x extension
            compiler = self.compiler.compiler
            proc = subprocess.Popen(compiler + ["-dumpversion"], stdout=subprocess.PIPE)
            pipe = proc.stdout
            proc.wait()
            gcc_ver = pipe.readlines()[0].decode().strip()
            if V(gcc_ver) >= V("4.3.3"):
                self.use_cpp_0x = True
        dftbuild_ext.build_extensions(self)

    def build_extension(self, ext):
        if self.use_cpp_0x:
            ext.extra_compile_args += ["-std=c++14"]
            ext.define_macros += [("PYTANGO_HAS_UNIQUE_PTR", "1")]
        ext.extra_compile_args += [
            "-Wno-deprecated-declarations",
        ]
        dftbuild_ext.build_extension(self, ext)


class check_tests_errors(Command):
    """ Checks tests summary.json for failed tests and raises errror if found """

    description = (
        "Checks tests summary.json for failed tests and raises errror if found"
    )

    user_options = [
        ("summary-file=", None, "Path to summary.json"),
        (
            "ignore-gevent-errors",
            None,
            "Failed tests using GreenMode.Gevent will not raise error.",
        ),
    ]

    def initialize_options(self):
        self.summary_file = "summary.json"
        self.ignore_gevent_errors = False

    def finalize_options(self):
        if self.ignore_gevent_errors is not False:
            self.ignore_gevent_errors = True
        if not os.path.isfile(self.summary_file):
            raise Exception("Provided summary.json file does not exists.")

    def run(self):
        with open(self.summary_file, "r") as f:
            summary = json.load(f)
            for test in summary:
                if test["outcome"] in ["failed", "Failed", "fail", "error", "Error"]:
                    if self.ignore_gevent_errors and "Gevent" in test["testName"]:
                        pass
                    else:
                        raise Exception("Some tests in summary.json failed.")
        print("No failed tests found in the tests summary file.")


def setup_args():

    directories = {
        "include_dirs": [],
        "library_dirs": [],
        "libraries": [],
    }
    sys_libs = []
    add_lib("tango", directories, sys_libs, lib_name="tango")
    add_lib("omni", directories, sys_libs, lib_name="omniORB4")
    add_lib("zmq", directories, sys_libs, lib_name="libzmq")
    add_lib_boost(directories)

    macros = []
    # special numpy configuration (only needed at build time)
    if numpy is not None:
        directories["include_dirs"].append(numpy.get_include())

        macros.append(("PYTANGO_NUMPY_VERSION", numpy.__version__))
        macros.append(("NPY_NO_DEPRECATED_API", "0"))

    if POSIX or MACOS:
        directories = pkg_config(*sys_libs, **directories)

    Release = get_release_info()

    author = Release.authors["Coutinho"]

    please_debug = False

    packages = [
        "tango",
        "tango.databaseds",
        "tango.databaseds.db_access",
    ]

    py_modules = [
        "PyTango",  # Backward compatibilty
    ]

    provides = [
        "tango",
        "PyTango",  # Backward compatibilty
    ]

    python_requires = ">=3.6"

    requires = [
        "boost_python (>=1.33)",
        "numpy (>=1.13.3)",
        "six (>=1.10)",
    ]

    install_requires = [
        "numpy (>=1.13.3)",
        "six (>=1.10)",
    ]

    setup_requires = []

    if TESTING:
        setup_requires += ["pytest-runner"]

    tests_require = [
        "gevent != 1.5a1",
        "psutil",
    ]

    if PYTHON_VERSION < (3, 7):
        tests_require += [
            "pytest < 7.1",
            "pytest-forked",
            "tomli < 2.0",
            "typing-extensions < 4.0",
        ]
    else:
        tests_require += ["pytest", "pytest-forked"]

    package_data = {
        "tango.databaseds": ["*.xmi", "*.sql", "*.sh", "DataBaseds"],
    }

    data_files = []

    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved ::"
        " GNU Library or Lesser General Public License (LGPL)",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
    ]

    # Note for PyTango developers:
    # Compilation time can be greatly reduced by compiling the file
    # src/precompiled_header.hpp as src/precompiled_header.hpp.gch
    # and then uncommenting this line. Someday maybe this will be
    # automated...
    extra_compile_args = [
        # '-include ext/precompiled_header.hpp',
    ]

    extra_link_args = []

    if please_debug:
        extra_compile_args += ["-g", "-O0"]
        extra_link_args += ["-g", "-O0"]

    src_dir = abspath("ext")
    client_dir = src_dir
    server_dir = os.path.join(src_dir, "server")

    clientfiles = sorted(
        os.path.join(client_dir, fname)
        for fname in os.listdir(client_dir)
        if fname.endswith(".cpp")
    )

    serverfiles = sorted(
        os.path.join(server_dir, fname)
        for fname in os.listdir(server_dir)
        if fname.endswith(".cpp")
    )

    cppfiles = clientfiles + serverfiles
    directories["include_dirs"].extend([client_dir, server_dir])

    include_dirs = uniquify(directories["include_dirs"])
    library_dirs = uniquify(directories["library_dirs"])
    libraries = uniquify(directories["libraries"])

    pytango_ext = Extension(
        name="_tango",
        sources=cppfiles,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        define_macros=macros,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language="c++",
        depends=[],
    )

    cmdclass = {
        "build": build,
        "build_ext": build_ext,
        "install": install,
        "check_tests_errors": check_tests_errors,
    }

    long_description = get_readme()

    opts = dict(
        name="pytango",
        version=Release.version_long,
        description=Release.description,
        long_description=long_description,
        author=author[0],
        author_email=author[1],
        url=Release.url,
        download_url=Release.download_url,
        platforms=Release.platform,
        license=Release.license,
        packages=packages,
        py_modules=py_modules,
        classifiers=classifiers,
        package_data=package_data,
        data_files=data_files,
        provides=provides,
        keywords=Release.keywords,
        python_requires=python_requires,
        requires=requires,
        install_requires=install_requires,
        setup_requires=setup_requires,
        tests_require=tests_require,
        extras_require={
            "tests": tests_require
        },
        ext_package="tango",
        ext_modules=[pytango_ext],
        cmdclass=cmdclass,
    )

    return opts


def main():
    return setup(**setup_args())


if __name__ == "__main__":
    main()
