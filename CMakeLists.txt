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
include(cmake/variables.cmake)

# ---- Dependencies -------
find_package (Python 3.11 COMPONENTS Development)
message(STATUS "Python version: ${Python_VERSION}")
message(STATUS " - python include dir: ${Python_INCLUDE_DIRS}")

set(BOOST_VERBOSE "ON")
find_package(Boost 1.73 REQUIRED CONFIG COMPONENTS python3)
message(STATUS "Boost version: ${Boost_VERSION}")

# ---- Declare library ----
add_library(pytango_tango
    source/pytango.cpp)
add_library(pytango::tango ALIAS pytango_tango)

include(GenerateExportHeader)
generate_export_header(
    pytango_tango
    BASE_NAME pytango
    EXPORT_FILE_NAME export/pytango/pytango_export.hpp
    CUSTOM_CONTENT_FROM_VARIABLE pragma_suppress_c4251
)

if(NOT BUILD_SHARED_LIBS)
  target_compile_definitions(pytango_tango PUBLIC PYTANGO_STATIC_DEFINE)
endif()

set_target_properties(
    pytango_tango PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN YES
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}"
    EXPORT_NAME tango
    OUTPUT_NAME tango
)

target_include_directories(
    pytango_tango ${warning_guard}
    PUBLIC
    "$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>"
)

target_include_directories(
    pytango_tango SYSTEM
    PUBLIC
    "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/export>"
)

target_compile_features(pytango_tango PUBLIC cxx_std_14)

# A python extension module library must be shared
add_library(
    pytango_pytango SHARED
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
    pytango_pytango ${warning_guard}
    PUBLIC
    "$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/include>"
)

target_include_directories(
    pytango_pytango SYSTEM
    PUBLIC
    "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/export>"
)

target_compile_features(pytango_pytango PUBLIC cxx_std_14)

target_link_libraries(pytango_pytango PRIVATE pytango_tango Python::Module Boost::python3)

# ---- Install rules ----

if(NOT CMAKE_SKIP_INSTALL_RULES)
  include(cmake/install-rules.cmake)
endif()

# ---- Developer mode ----

if(NOT pytango_DEVELOPER_MODE)
  return()
elseif(NOT PROJECT_IS_TOP_LEVEL)
  message(
      AUTHOR_WARNING
      "Developer mode is intended for developers of pytango"
  )
endif()

include(cmake/dev-mode.cmake)
