# Generate placeholder "wet" module (versions all set to "unknown" - updated at build time if FABM_EMBED_VERSION is set)
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/version.F90.in ${CMAKE_CURRENT_BINARY_DIR}/version.F90)

add_library(fabm_models_wet OBJECT
            wet_model_library.F90
            ${CMAKE_CURRENT_BINARY_DIR}/version.F90
            abiotic_sediment.F90
            abiotic_water.F90
            burial.F90
            sediment_exchange.F90
            fish.F90
            fish_pclake.F90
            macrophytes.F90
            phytoplankton.F90
            om_pool.F90
            utility.F90
            zoobenthos.F90
            zooplankton.F90
            bot_pel_interface.F90
            bivalves.F90
           )

add_dependencies(fabm_models_wet fabm_base)

if(FABM_EMBED_VERSION)
  # Dynamically generate "wet_version" module with git commit/branch information at every build.
  add_custom_target(fabm_models_wet_version
     ${CMAKE_COMMAND} -DINFILE=${CMAKE_CURRENT_SOURCE_DIR}/version.F90.in -DOUTFILE=${CMAKE_CURRENT_BINARY_DIR}/version.F90 -P ${GET_GIT_INFO_SCRIPT}
     WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
     COMMENT "Retrieving description of last WET commit..." 
     SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/version.F90.in ${GET_GIT_INFO_SCRIPT}
     VERBATIM
  )
  add_dependencies(fabm_models_wet fabm_models_wet_version)
endif()

#-----------------------------------------------------------------------
# Copyright (C) 2017 - WET developers
#-----------------------------------------------------------------------
