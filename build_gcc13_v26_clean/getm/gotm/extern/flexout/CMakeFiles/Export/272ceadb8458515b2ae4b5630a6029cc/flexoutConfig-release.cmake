#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "field_manager" for configuration "Release"
set_property(TARGET field_manager APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(field_manager PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "Fortran"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libfield_manager.a"
  )

list(APPEND _cmake_import_check_targets field_manager )
list(APPEND _cmake_import_check_files_for_field_manager "${_IMPORT_PREFIX}/lib/libfield_manager.a" )

# Import target "output_manager" for configuration "Release"
set_property(TARGET output_manager APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(output_manager PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "Fortran"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/liboutput_manager.a"
  )

list(APPEND _cmake_import_check_targets output_manager )
list(APPEND _cmake_import_check_files_for_output_manager "${_IMPORT_PREFIX}/lib/liboutput_manager.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
