# Install script for directory: /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/fabm/src

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc13_v23_fish_checkstate_fix2/fabm")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Debug")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/libfabm.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/CMakeFiles/fabm.dir/install-cxx-module-bmi-Debug.cmake" OPTIONAL)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE DIRECTORY FILES "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/modules/${BUILD_TYPE}/")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE FILE FILES
    "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/fabm/src/../include/fabm.h"
    "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/fabm/src/../include/fabm_version.h"
    "/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/fabm/src/drivers/gotm/fabm_driver.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/fabmConfig.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/fabmConfig.cmake"
         "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/fabmConfig.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/fabmConfig-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/cmake/fabmConfig.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/fabmConfig.cmake")
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/cmake" TYPE FILE FILES "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/CMakeFiles/Export/272ceadb8458515b2ae4b5630a6029cc/fabmConfig-debug.cmake")
  endif()
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/aed/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/hzg/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/iow/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/klimacampus/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/metu/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/msi/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/au/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/bb/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/examples/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/gotm/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/jrc/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/pml/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/selma/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/su/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/niva/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/akvaplan/cmake_install.cmake")
  include("/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/models/wet/cmake_install.cmake")

endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v23_fish_checkstate_fix2/fabm/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
