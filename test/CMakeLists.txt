cmake_minimum_required(VERSION 3.14)

project(pytangoTests LANGUAGES CXX)

include(../cmake/project-is-top-level.cmake)
include(../cmake/folders.cmake)
include(../cmake/windows-set-path.cmake)

# ---- Dependencies ----

if(PROJECT_IS_TOP_LEVEL)
  find_package(pytango REQUIRED)
  enable_testing()
endif()

# ---- Tests ----

add_executable(pytango_test source/pytango_test.cpp)
target_link_libraries(pytango_test PRIVATE pytango::tango)
target_compile_features(pytango_test PRIVATE cxx_std_14)

add_test(NAME pytango_test COMMAND pytango_test)
windows_set_path(pytango_test pytango::tango)

# ---- End-of-file commands ----

add_folders(Test)
