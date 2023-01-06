cmake_minimum_required(VERSION 3.14)

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

find_package (Python 3.8 COMPONENTS Development)
message(STATUS "Python version: ${Python_VERSION}")
message(STATUS " - python include dir: ${Python_INCLUDE_DIRS}")

set(BOOST_VERBOSE "ON")
find_package(Boost 1.71 REQUIRED CONFIG COMPONENTS python3)
if(NOT Boost_PYTHON3_FOUND)
    find_package(Boost 1.71 REQUIRED CONFIG COMPONENTS python38)
endif()

message(STATUS "Boost version: ${Boost_VERSION}")

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

target_link_libraries(pytango_pytango PRIVATE Python::Module Boost::python3 PkgConfig::TANGO)

# ---- Developer mode ----

if(NOT pytango_DEVELOPER_MODE)
  return()
elseif(NOT PROJECT_IS_TOP_LEVEL)
  message(
      AUTHOR_WARNING
      "Developer mode is intended for developers of pytango"
  )
endif()

