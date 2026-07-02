#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "fabm" for configuration "Debug"
set_property(TARGET fabm APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(fabm PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_DEBUG "Fortran"
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib/libfabm.a"
  )

list(APPEND _cmake_import_check_targets fabm )
list(APPEND _cmake_import_check_files_for_fabm "${_IMPORT_PREFIX}/lib/libfabm.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
