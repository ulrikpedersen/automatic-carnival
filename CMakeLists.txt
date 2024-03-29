cmake_minimum_required(VERSION 3.16)  # Ubuntu 20.04 ships with cmake 3.16.3
# cmake_minimum_required(VERSION 3.17)  # cmake 3.17 added support for conda environments FindPython
# cmake_minimum_required(VERSION 3.25)  # latest release. Available as pip install cmake

include(cmake/prelude.cmake)

project(
    pytango
    VERSION 9.4.0
    DESCRIPTION "Python bindings for the Tango distributed control system"
    HOMEPAGE_URL "https://pytango.readthedocs.io/"
    LANGUAGES CXX
)

include(cmake/project-is-top-level.cmake)

# ---- Dependencies -------
find_package(PkgConfig REQUIRED)

# TANGO_ROOT: this variable can be set as an environment variable or
#             as a cache variable on the commandline: "-D TANGO_ROOT=/path/to/cpptango
#             By default the variable is not set and system is searched for cpptango
#             using pkg-config.
#             The cache variable/commandline takes precedence over the environment variable.
if (DEFINED ENV{TANGO_ROOT})
    set(TANGO_ROOT "$ENV{TANGO_ROOT}" CACHE STRING "Tango root installation path")
else()
    set(TANGO_ROOT "" CACHE STRING "Tango root installation path")
endif()
message(STATUS "TANGO_ROOT cache variable is: \"TANGO_ROOT=${TANGO_ROOT}\"")
list(APPEND CMAKE_PREFIX_PATH ${TANGO_ROOT})
pkg_check_modules(TANGO REQUIRED IMPORTED_TARGET tango)

# Find Python and NumPy
# https://cmake.org/cmake/help/latest/module/FindPython.html
if (DEFINED ENV{PYTHON_ROOT})
    set(Python_ROOT_DIR "$ENV{PYTHON_ROOT}" CACHE STRING "Python root installation path")
    set(Python_FIND_STRATEGY LOCATION)
endif()
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
if (DEFINED ENV{BOOST_PYTHON_SUFFIX})
    set(BOOST_PYTHON_SUFFIX "$ENV{BOOST_PYTHON_SUFFIX}" CACHE STRING "Sets the suffix on the Boost Python component to search for (default is 3). Set this only if your Boost version is < 1.73")
else()
    set(BOOST_PYTHON_SUFFIX "3" CACHE STRING "Sets the suffix on the Boost Python component to search for (default is 3). Set this only if your Boost version is < 1.73")
endif()
set(Boost_VERBOSE "ON")
find_package(Boost 1.71 REQUIRED COMPONENTS python${BOOST_PYTHON_SUFFIX} CONFIG)
message(STATUS "Boost Python version: ${Boost_PYTHON_VERSION}")

# Just a sanity check: the python used to build pytango should match the
# version used to build libboost_python. This could be changed from WARNING to ERROR(?)
# cmake hack: using VERSION_EQUAL would be better but Python reports a full MAJOR.MINOR.PATCH
#             version number whereas boost-python only reports MAJOR.MINOR. MATCHES works but
#             we're pretending that the shorter version string is a regex.
if(NOT ${Python_VERSION} MATCHES ${Boost_PYTHON_VERSION})
    message(WARNING "The interpreter/library python version (${Python_VERSION}) does not match the version of python that libboost_python was built with (${Boost_PYTHON_VERSION})")
endif()

# ---- Declare library ----
# A python extension module library must be shared
add_library(
    pytango_tango SHARED
    ext/device_attribute.cpp
    ext/device_proxy.cpp
    ext/pytgutils.cpp
    ext/base_types.cpp
    ext/attribute_alarm_info.cpp
    ext/attribute_info_ex.cpp
    ext/device_data.cpp
    ext/callback.cpp
    ext/command_info.cpp
    ext/device_attribute_config.cpp
    ext/exception.cpp
    ext/devintr_change_event_data.cpp
    ext/db.cpp
    ext/version.cpp
    ext/dev_error.cpp
    ext/pipe_event_data.cpp
    ext/device_pipe.cpp
    ext/to_py.cpp
    ext/pipe_info.cpp
    ext/constants.cpp
    ext/api_util.cpp
    ext/dev_command_info.cpp
    ext/change_event_info.cpp
    ext/server/tango_util.cpp
    ext/server/pipe.cpp
    ext/server/device_impl.cpp
    ext/server/attr.cpp
    ext/server/command.cpp
    ext/server/multi_class_attribute.cpp
    ext/server/log4tango.cpp
    ext/server/encoded_attribute.cpp
    ext/server/auto_monitor.cpp
    ext/server/attribute.cpp
    ext/server/device_class.cpp
    ext/server/multi_attribute.cpp
    ext/server/subdev.cpp
    ext/server/user_default_pipe_prop.cpp
    ext/server/fwdAttr.cpp
    ext/server/dserver.cpp
    ext/server/wattribute.cpp
    ext/server/user_default_attr_prop.cpp
    ext/attr_conf_event_data.cpp
    ext/device_info.cpp
    ext/periodic_event_info.cpp
    ext/database.cpp
    ext/precompiled_header.cpp
    ext/enums.cpp
    ext/attribute_proxy.cpp
    ext/pyutils.cpp
    ext/attribute_event_info.cpp
    ext/attribute_dimension.cpp
    ext/archive_event_info.cpp
    ext/locking_thread.cpp
    ext/device_data_history.cpp
    ext/from_py.cpp
    ext/group_reply.cpp
    ext/device_attribute_history.cpp
    ext/locker_info.cpp
    ext/group_reply_list.cpp
    ext/time_val.cpp
    ext/connection.cpp
    ext/attribute_info.cpp
    ext/pytango.cpp
    ext/poll_device.cpp
    ext/group.cpp
    ext/event_data.cpp
    ext/data_ready_event_data.cpp
)
add_library(pytango::tango ALIAS pytango_tango)

set_target_properties(
    pytango_tango PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN YES
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}"
    EXPORT_NAME tango
    OUTPUT_NAME tango
    PREFIX "_"
)
if ( CMAKE_SYSTEM_NAME MATCHES "Darwin" )
  # .so suffix is default on linux and required for python to load
    # the extension module. On MacOS the default is .dylib so we have
    # to force the suffix here.
    # (what to do for Windows?)
    set_target_properties(pytango_tango PROPERTIES SUFFIX ".so")  
endif()

target_include_directories(
    pytango_tango
    PUBLIC
    "$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/ext>"
)

target_compile_features(pytango_tango PUBLIC cxx_std_14)

target_link_libraries(pytango_tango PRIVATE Python::Module Python::NumPy Boost::python PkgConfig::TANGO)

install(TARGETS pytango_tango LIBRARY DESTINATION tango)

# ---- Developer mode ----

if(NOT pytango_DEVELOPER_MODE)
  return()
elseif(NOT PROJECT_IS_TOP_LEVEL)
  message(
      AUTHOR_WARNING
      "Developer mode is intended for developers of pytango"
  )
endif()

