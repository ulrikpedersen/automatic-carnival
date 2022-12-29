if(PROJECT_IS_TOP_LEVEL)
  set(
      CMAKE_INSTALL_INCLUDEDIR "include/pytango-${PROJECT_VERSION}"
      CACHE PATH ""
  )
endif()

include(CMakePackageConfigHelpers)
include(GNUInstallDirs)

# find_package(<package>) call for consumers to find this project
set(package pytango)

install(
    DIRECTORY
    include/
    "${PROJECT_BINARY_DIR}/export/"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
    COMPONENT pytango_Development
)

install(
    TARGETS pytango_pytango
    EXPORT pytangoTargets
    RUNTIME #
    COMPONENT pytango_Runtime
    LIBRARY #
    COMPONENT pytango_Runtime
    NAMELINK_COMPONENT pytango_Development
    ARCHIVE #
    COMPONENT pytango_Development
    INCLUDES #
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)

write_basic_package_version_file(
    "${package}ConfigVersion.cmake"
    COMPATIBILITY SameMajorVersion
)

# Allow package maintainers to freely override the path for the configs
set(
    pytango_INSTALL_CMAKEDIR "${CMAKE_INSTALL_LIBDIR}/cmake/${package}"
    CACHE PATH "CMake package config location relative to the install prefix"
)
mark_as_advanced(pytango_INSTALL_CMAKEDIR)

install(
    FILES cmake/install-config.cmake
    DESTINATION "${pytango_INSTALL_CMAKEDIR}"
    RENAME "${package}Config.cmake"
    COMPONENT pytango_Development
)

install(
    FILES "${PROJECT_BINARY_DIR}/${package}ConfigVersion.cmake"
    DESTINATION "${pytango_INSTALL_CMAKEDIR}"
    COMPONENT pytango_Development
)

install(
    EXPORT pytangoTargets
    NAMESPACE pytango::
    DESTINATION "${pytango_INSTALL_CMAKEDIR}"
    COMPONENT pytango_Development
)

if(PROJECT_IS_TOP_LEVEL)
  include(CPack)
endif()
