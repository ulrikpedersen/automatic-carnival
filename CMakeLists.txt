cmake_minimum_required(VERSION 3.16)  # Ubuntu 20.04 ships with cmake 3.16.3
# cmake_minimum_required(VERSION 3.17)  # cmake 3.17 added support for conda environments FindPython
# cmake_minimum_required(VERSION 3.25)  # latest release. Available as pip install cmake

include(cmake/prelude.cmake)

project(
    pytango
    VERSION 9.4.1
    DESCRIPTION "Python bindings for the Tango distributed control system"
    HOMEPAGE_URL "https://pytango.readthedocs.io/"
    LANGUAGES CXX
)

include(cmake/project-is-top-level.cmake)

# ---- Dependencies -------
find_package(PkgConfig REQUIRED)
set(TANGO_ROOT "" CACHE STRING "Tango root installation path")
list(APPEND CMAKE_PREFIX_PATH ${TANGO_ROOT})
pkg_check_modules(TANGO REQUIRED IMPORTED_TARGET tango)

# Find Python and NumPy
# https://cmake.org/cmake/help/latest/module/FindPython.html
find_package (Python 3.8 COMPONENTS Interpreter Development NumPy)
message(STATUS "    Python version:  ${Python_VERSION}")
message(STATUS "      - intepreter:  ${Python_EXECUTABLE}")
message(STATUS "       - libraries:  ${Python_LIBRARIES}")
message(STATUS "       - libraries:  ${Python_LIBRARY_DIRS}")
message(STATUS "     NumPy version:  ${Python_NumPy_VERSION}")
message(STATUS "     - include dir:  ${Python_NumPy_INCLUDE_DIRS}")

# Find boost.python library.
# Work around the boost python suffix issue for Boost versions < 1.73.
# (See https://github.com/boostorg/boost_install/issues/31)
# By default we search for the component "python3" which works for Boost >= 1.73
# However, for example Ubuntu 20.04 ships with Boost 1.71 and here the developer/CI
# can set and override the cache variable BOOST_PYTHON_SUFFIX to "38" (default "3")
set(BOOST_PYTHON_SUFFIX "3" CACHE STRING "Sets the suffix on the Boost Python component to search for (default is 3). Set this only if your Boost version is < 1.73")
set(Boost_VERBOSE "ON")
find_package(Boost 1.71 REQUIRED COMPONENTS python${BOOST_PYTHON_SUFFIX} CONFIG)
message(STATUS "Boost Python version: ${Boost_PYTHON_VERSION}")

# Just a sanity check: the python used to build pytango should match the
# version used to build libboost_python.
# cmake hack: using VERSION_EQUAL would be better but Python reports a full MAJOR.MINOR.PATCH
#             version number whereas boost-python only reports MAJOR.MINOR. MATCHES works but
#             we're pretending that the shorter version string is a regex.
if(NOT ${Python_VERSION} MATCHES ${Boost_PYTHON_VERSION})
    message(WARNING "The interpreter/library python version (${Python_VERSION}) does not match the version of python that libboost_python was built with (${Boost_PYTHON_VERSION})")
endif()

# ---- Declare library ----
# A python extension module library must be shared
add_library(
    pytango_pytango SHARED
    source/pytango.cpp
    source/bpwrap.cpp
)
add_library(pytango::pytango ALIAS pytango_pytango)

set_target_properties(
    pytango_pytango PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN YES
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}"
    EXPORT_NAME pytango
    OUTPUT_NAME pytango
    PREFIX ""
)
if ( CMAKE_SYSTEM_NAME MATCHES "Darwin" )
  # .so suffix is default on linux and required for python to load
    # the extension module. On MacOS the default is .dylib so we have
    # to force the suffix here.
    # (what to do for Windows?)
    set_target_properties(pytango_pytango PROPERTIES SUFFIX ".so")  
endif()

target_include_directories(
    pytango_pytango
    PUBLIC
    "$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>"
)

target_compile_features(pytango_pytango PUBLIC cxx_std_14)

target_link_libraries(pytango_pytango PRIVATE Python::Module Python::NumPy Boost::python PkgConfig::TANGO)

install(TARGETS pytango_pytango LIBRARY DESTINATION pytango)

# ---- Developer mode ----

if(NOT pytango_DEVELOPER_MODE)
  return()
elseif(NOT PROJECT_IS_TOP_LEVEL)
  message(
      AUTHOR_WARNING
      "Developer mode is intended for developers of pytango"
  )
endif()

