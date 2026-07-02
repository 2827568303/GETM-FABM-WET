#include "fabm_driver.h"
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ MODULE: RESUSPENSION AND SEDIMENTATION                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
module wet_resus_sed
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_expressions
   use fabm_particle
   use wet_utility, ONLY: uFunTmArrh,uFunTmGaus
   implicit none
   private
   
   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public :: type_wet_resus_sed
      ! state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_bottom_state_variable_id)                            :: id_sDIMS, id_sDPOMS, id_sNPOMS, id_sPPOMS, id_sPO4S, id_sPAIMS, id_sNH4S, id_sNO3S, id_sSiPaS                               
      type (type_state_variable_id)                                   :: id_SWDPOM, id_SWNPOM, id_SWPPOM, id_SWSiPa, id_SWDIM, id_SWPAIM, id_sNH4W, id_sNO3W, id_sPO4W, id_sDPOMS_PV, id_sNPOMS_PV, id_sPPOMS_PV
      ! environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_dependency_id)                                       :: id_uTm, id_BioTurb, id_DragVeg
      type (type_horizontal_dependency_id)                            :: id_depth, id_shear, id_bPorS, id_bot_pel_conv
      ! diagnostic variables-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDResusDead, id_aFunTauTmSet, id_tDAbioIMS, id_tDAbioPOMS
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDResusIM, id_tDResusPOM, id_tNResusPOM, id_tPResusPOM, id_tSiResusPa, id_tPResusPO4, id_tPResusAIM, id_tNResusNO3, id_tNResusNH4
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDSetIM, id_tDSetPOM, id_tNSetPOM, id_tPSetPOM, id_tPSetAIM, id_tSiSetPa
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      real(rk)                                                        :: kVegResus, cSuspMin, cSuspRef, cSuspMax, cSuspSlope, hDepthSusp, cFetchRef, cFetch, crt_shear, ref_shear, alpha, eta
      real(rk)                                                        :: cVSetMain, fLutum, fLutumRef, cThetaSed, cVSedIM, cVSedPOM
      integer                                                         :: qResus, nMACS
      logical                                                         :: diagnostics
      
   contains

   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure ::  initialize
   procedure ::  do_bottom
   
   end type type_wet_resus_sed

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk),parameter :: secs_pr_day= 86400.0_rk

contains

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_resus_sed), intent(inout), target :: self
   integer,                     intent(in)            :: configunit

   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer             :: i_fish, i_mac
   character(len=64)   :: index
   
   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%get_parameter(self%kVegResus,    'kVegResus',    'm2/gDW',    'relative resuspension reduction per gram macrophytes',           default=0.05_rk                                        )
   call self%get_parameter(self%qResus,       'qResus',       '-',         '1=original PCLake; 2=based on shear stress',                     default=2                                              )
   call self%get_parameter(self%cSuspRef,     'cSuspRef',     '-',         'qResus = 1; reference suspended matter function',                default=0.0_rk                                         )
   call self%get_parameter(self%cSuspMin,     'cSuspMin',     '-',         'qResus = 1; minimum value of logistic function',                 default=6.1_rk                                         )
   call self%get_parameter(self%cSuspMax,     'cSuspMax',     '-',         'qResus = 1; maximum value of logistic function',                 default=25.2_rk                                        )
   call self%get_parameter(self%cSuspSlope,   'cSuspSlope',   '-',         'qResus = 1; slope of logistic function',                         default=2.1_rk                                         )
   call self%get_parameter(self%hDepthSusp,   'hDepthSusp',   '-',         'qResus = 1; half-sat. value of depth in logistic function',      default=2.0_rk                                         )
   call self%get_parameter(self%cFetchRef,    'cFetchRef',    'm',         'qResus = 1; reference fetch',                                    default=1000.0_rk                                      )
   call self%get_parameter(self%cFetch,       'cFetch',       'm',         'qResus = 1; length of water body in prevailing wind direction',  default=1000.0_rk                                      )
   call self%get_parameter(self%crt_shear,    'crt_shear',    'N/m',       'qResus = 2; critical shear stress',                              default=0.02_rk                                        )
   call self%get_parameter(self%ref_shear,    'ref_shear',    'N/m',       'qResus = 2; reference shear stress',                             default=1.0_rk                                         )
   call self%get_parameter(self%alpha,        'alpha',        'g/m/d',     'qResus = 2; gross rate of sediment erosion',                     default=9000.0_rk, scale_factor=1.0_rk/secs_pr_day     )
   call self%get_parameter(self%eta,          'eta',          '-',         'qResus = 2; shear stress correction factor',                     default=1.0_rk                                         )
   call self%get_parameter(self%cVSetMain,    'cVSetMain',    'm/d',       'qResus = 2; depth averaged settling velocity',                   default=0.5_rk,    scale_factor=1.0_rk/secs_pr_day     )
   call self%get_parameter(self%fLutum,       'fLutum',       '-',         'lutum fraction of inorganic matter',                             default=0.1_rk                                         )
   call self%get_parameter(self%fLutumRef,    'fLutumRef',    '-',         'reference lutum fraction of inorganic matter',                   default=0.2_rk                                         )
   call self%get_parameter(self%cThetaSed,    'cThetaSed',    '1/e^*C',    'temperature coefficient of sedimentation',                       default=1.01_rk                                        )
   call self%get_parameter(self%cVSedIM,      'cVSedIM',      'm/d',       'IM sedimentation velocity constant at 20*C',                     default=1.0_rk                                         )
   call self%get_parameter(self%cVSedPOM,     'cVSedPOM',     'm/d',       'POM sedimentation velocity constant at 20*C',                    default=0.5_rk                                         )
   call self%get_parameter(self%diagnostics,  'diagnostics',  '-',         'toggle diagnostic output',                                       default=.false.                                        )

   !REGISTER MODEL VARIBLES, DEPENDENCIES & COUPLINGS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! register state variable dependencies------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_dependency(self%id_sDIMS,    'inorg_pool_in_sediment',          'g/m2',   'sediment inorganic matter'        )
   call self%register_state_dependency(self%id_sDPOMS,   'POM_DW_in_sediment',              'g/m2',   'POM DW in sediment'               )
   call self%register_state_dependency(self%id_sNPOMS,   'POM_N_in_sediment',               'g/m2',   'POM N in sediment'                )
   call self%register_state_dependency(self%id_sPPOMS,   'POM_P_in_sediment',               'g/m2',   'POM P in sediment'                )
   call self%register_state_dependency(self%id_sDPOMS_PV,'POM_DW_in_sediment_PV',           'g/m2',   'POM DW in sediment pelagic mirror')
   call self%register_state_dependency(self%id_sNPOMS_PV,'POM_N_in_sediment_PV',            'g/m2',   'POM N in sediment pelagic mirror' )
   call self%register_state_dependency(self%id_sPPOMS_PV,'POM_P_in_sediment_PV',            'g/m2',   'POM P in sediment pelagic mirror' )

   call self%register_state_dependency(self%id_sPO4S,    'PO4_in_sediment',                 'g/m2',   'sediment phosphate'               )
   call self%register_state_dependency(self%id_sPAIMS,   'adsorbed_phosphorus_in_sediment', 'g/m2',   'sediment absorbed phosphate'      )
   call self%register_state_dependency(self%id_sNH4S,    'NH4_in_sediment',                 'g/m2',   'sediment ammonium'                )
   call self%register_state_dependency(self%id_sNO3S,    'NO3_in_sediment',                 'g/m2',   'sediment nitrate'                 )
   call self%register_state_dependency(self%id_sSiPaS,   'particulate_Si_in_sediment',      'g/m2',   'sediment particulate Si'          )
                                                                                                                                          
   call self%register_state_dependency(self%id_SWSiPa,   'particulate_Si_in_water',         'g/m2',   'water particulate Si'             )
   call self%register_state_dependency(self%id_sNH4W,    'NH4_in_water',                    'g/m3',   'water NH4'                        )
   call self%register_state_dependency(self%id_sNO3W,    'NO3_in_water',                    'g/m3',   'water NO3'                        )
   call self%register_state_dependency(self%id_sPO4W,    'PO4_in_water',                    'g/m3',   'water PO4'                        )
   call self%register_state_dependency(self%id_SWDIM,    'inorg_pool_in_water',             'g/m3',   'inorganic matter pool in water'   )
   call self%register_state_dependency(self%id_SWPAIM,   'adsorbed_phosphorus_in_water',    'g/m3',   'adsorbed phosphorus in water'     )
   call self%register_state_dependency(self%id_SWDPOM,   'POM_DW_in_water',                 'g/m3',   'POM DW in water'                  )
   call self%register_state_dependency(self%id_SWNPOM,   'POM_N_in_water',                  'g/m3',   'POM N in water'                   )
   call self%register_state_dependency(self%id_SWPPOM,   'POM_P_in_water',                  'g/m3',   'POM P in water'                   )
   ! register other dependencies---------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_shear,standard_variables%bottom_stress)
   call self%register_dependency(self%id_uTm,standard_variables%temperature)
   call self%register_dependency(self%id_depth,standard_variables%bottom_depth)

   call self%register_horizontal_dependency(self%id_bPorS, 'bPorS', 'm3/m3','sediment porosity')
   call self%register_dependency(self%id_BioTurb,type_bulk_standard_variable(name='total_bioturbation',units='gDW/m3/d'))
   call self%register_dependency(self%id_DragVeg,type_bulk_standard_variable(name='total_macrophyte_biomass',units='gDW/m2'))
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')  
   ! register diagnostic variables-------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_tDResusDead,   'tDResusDead', '-',     'tDResusDead',                    output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_aFunTauTmSet,  'aFunTauTmSet','-',     'basic settling rate',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tDAbioIMS,     'tDAbioIMS',   'g/m2/s','IM abiotic update',              output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tDAbioPOMS,    'tDAbioPOMS',  'g/m2/s','POM abiotic update',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   ! Register diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%diagnostics) then
       call self%register_diagnostic_variable(self%id_tDResusIM, 'tDResusIM',   'g/m2/s','rate IM resuspended',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDResusPOM,'tDResusPOM',  'g/m2/s','rate DPOM resuspended',          output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNResusPOM,'tNResusPOM',  'g/m2/s','rate DPOM resuspended',          output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPResusPOM,'tPResusPOM',  'g/m2/s','rate DPOM resuspended',          output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tSiResusPa,'tSiResusPa',  'g/m2/s','rate Si particulate resuspended',output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPResusPO4,'tPResusPO4',  'g/m2/s','rate PO4 resuspended',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPResusAIM,'tPResusAIM',  'g/m2/s','rate PAIM resuspended',          output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNResusNO3,'tNResusNO3',  'g/m2/s','rate NO3 resuspended',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNResusNH4,'tNResusNH4',  'g/m2/s','rate NH4 resuspended',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDSetIM,   'tDSetIM',     'g/m2/s','rate IM sedimented',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDSetPOM,  'tDSetPOM',    'g/m2/s','rate DPOM sedimented',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNSetPOM,  'tNSetPOM',    'g/m2/s','rate DPOM sedimented',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPSetPOM,  'tPSetPOM',    'g/m2/s','rate DPOM sedimented',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPSetAIM,  'tPSetAIM',    'g/m2/s','rate PAIM sedimented',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tSiSetPa,  'tSiSetPa',    'g/m2/s','rate Si particulate sedimented', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
  endif
   return

end subroutine initialize

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO BOTTOM                                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_resus_sed), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)                            :: sNH4S, sNO3S, sPO4S, sPAIMS, sDIMS, sDPOMS, sNPOMS, sPPOMS, sSiPaS, tDSetIM, uCorVSedPOM
   real(rk)                            :: rPDPOMS, rNDPOMS, rSiDPOMS, aFunDimSusp, sPAIMW, uCorVSedIM, uTm, depth, sNH4W, sNO3W, sPO4W
   real(rk)                            :: oNH4S, oNO3S, oPO4S, tNAbioNO3S, tPSetAIM, sDIMW, tNAbioNH4S, tPAbioPO4S
   real(rk)                            :: tDAbioIMS, tPAbioAIMS, bot_pel_conv
   real(rk)                            :: BioTurb, sDVeg, aFunVegResus, tDAbioPOMS, tNAbioPOMS, tPAbioPOMS, tSiAbioPaS
   real(rk)                            :: tDResusTauDead, tDResusBareDead, tDResusDead ,tDResusIM, tDResusPOM, tPResusPOM, tNResusPOM, shear, tSiResusPa, tPResusPO4, tPResusAIM
   real(rk)                            :: tNResusNO3, tNResusNH4, uFunTmSed, aFunTauTmSet, sDPOMW, sNPOMW,sPPOMW,sSiPaW, tDSetPOM, tPSetPOM, tNSetPOM, tSiSetPa, bPorS
   
   _HORIZONTAL_LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
      ! 1.1 retrieve state dependencies                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.1.1 organic matter                                                                                     !
         !----------------------------------------------------------------------------------------------------------!
         _GET_(self%id_SWDPOM,sDPOMW)                                                                               !
         _GET_(self%id_SWNPOM,sNPOMW)                                                                               !
         _GET_(self%id_SWPPOM,sPPOMW)                                                                               !
         _GET_(self%id_SWSiPa,sSiPaW)                                                                               !
         _GET_HORIZONTAL_(self%id_sSiPaS,sSiPaS)                                                                    ! 
         _GET_HORIZONTAL_(self%id_sDPOMS,sDPOMS)                                                                    !
         _GET_HORIZONTAL_(self%id_sNPOMS,sNPOMS)                                                                    !
         _GET_HORIZONTAL_(self%id_sPPOMS,sPPOMS)                                                                    !
         rPDPOMS=sPPOMS/(sDPOMS+NearZero)                                                                           !
         rNDPOMS=sNPOMS/(sDPOMS+NearZero)                                                                           !
         rSiDPOMS=sSiPaS/(sDPOMS+NearZero)                                                                          !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.1.2 inorganic matter                                                                                   !
         !----------------------------------------------------------------------------------------------------------!
         _GET_HORIZONTAL_(self%id_sPO4S,sPO4S)                                                                      !
         _GET_HORIZONTAL_(self%id_sPAIMS,sPAIMS)                                                                    !
         _GET_HORIZONTAL_(self%id_sNH4S,sNH4S)                                                                      !
         _GET_HORIZONTAL_(self%id_sNO3S,sNO3S)                                                                      !
         _GET_HORIZONTAL_(self%id_sDIMS,sDIMS)                                                                      !
         _GET_(self%id_SWDIM,sDIMW)                                                                                 !
         _GET_(self%id_SWPAIM,sPAIMW)                                                                               !
      !=============================================================================================================!
      ! 1.2 retrieve environmental dependencies                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _GET_HORIZONTAL_(self%id_shear,shear)                                                                         !
      _GET_(self%id_DragVeg,sDVeg)                                                                                  !
      _GET_(self%id_uTm,uTm)                                                                                        !
      _GET_HORIZONTAL_(self%id_depth,depth)                                                                         !
      !=============================================================================================================!   
      ! 1.3 diagnostic dependencies                                                                                 !   
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!   
      _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)
      _GET_(self%id_BioTurb,BioTurb)                                                                                !
      BioTurb=BioTurb*bot_pel_conv                                                                                  ! convert bioturbation from gDW/m3/d to gDW/m2/d
      _GET_HORIZONTAL_(self%id_bPorS,bPorS)                                                                         !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  6. calculate resuspension and sedimentation rates                                                             !
   !================================================================================================================!
      ! 6.1 resuspension                                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.1.1 calculate macrophyte dependence of resuspension                                                    !
         !----------------------------------------------------------------------------------------------------------!
         aFunVegResus=max(0.0_rk,1.0_rk-self%kVegResus*sDVeg)                                                       ! macrophyte dependence of resuspension
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.1.2 calculate base resuspension rate                                                                   !
         !----------------------------------------------------------------------------------------------------------!
         select case(self%qResus)                                                                                   ! calculate resuspension rate, two methods
            case(1)                                                                                                 !   (original PCLake method)
               if (uTm >= 0.1_rk) then                                                                              !     if temperature is above threshold
                  aFunDimSusp=self%cSuspRef*((self%cSuspMin+self%cSuspMax/(1.0_rk+exp(self%cSuspSlope*&             !
                  & (depth-self%hDepthSusp))))*((((self%cFetch +NearZero)/ self%cFetchRef) )** (0.5_rk)))           !       Empirical_resuspension_function_(logistic_fit_to_data), in day-1
               else                                                                                                 !     temperature is below threshold
                  aFunDimSusp=0.0_rk                                                                                !       resuspension function is zero
               endif                                                                                                !
            case(2)                                                                                                 !   (resuspension based on shear stress from physical driver model)
               if(shear <= self%crt_shear)then                                                                      !     shear is below critical value
                  aFunDimSusp=0.0_rk                                                                                !       no reuspension
               else                                                                                                 !     shear is above critical value
                  aFunDimSusp=(self%alpha/self%cVSetMain)*((shear-self%crt_shear)/self%ref_shear)**self%eta         !       calculate reuspension based on shear
               endif                                                                                                !
         end select                                                                                                 !
         tDResusTauDead=min(aFunDimSusp, ((aFunDimSusp +NearZero )**(0.5_rk))) &                                    !
             *((self%fLutum/ self%fLutumRef )** (0.5_rk))*bPorS                                                     ! resuspension due to shear stress
         tDResusBareDead=tDResusTauDead+BioTurb                                                                     ! resuspension due to_shear stress AND fish, in day-1
         tDResusDead=tDResusBareDead*aFunVegResus                                                                   ! resuspension corrected for macrophytes effect, in day-1
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.1.3 resuspension of sediment coponents                                                                 !
         !----------------------------------------------------------------------------------------------------------!
         tDResusIM=self%fLutum*sDIMS/(self%fLutum*sDIMS+sDPOMS+NearZero)*(tDResusDead/secs_pr_day)                  !  inorganic matter resuspension
         tDResusPOM=sDPOMS/(self%fLutum*sDIMS+sDPOMS+NearZero)*(tDResusDead/secs_pr_day)                            !  POM resuspension in DW
         tPResusPOM=rPDPOMS*tDResusPOM                                                                              !  POM resuspension in P
         tNResusPOM=rNDPOMS*tDResusPOM                                                                              !  POM resuspension in N
         tSiResusPa=rSiDPOMS*tDResusPOM                                                                             !  POM resuspension in SI
         tPResusAIM=sPAIMS/(sDIMS+NearZero)*tDResusIM                                                               !  resuspension adsorbed PAIM
         tPResusPO4=sPO4S/(sDPOMS+NearZero)*tDResusPOM                                                              !  resuspension of PO4
         tNResusNO3=sNO3S/(sDPOMS+NearZero)*tDResusPOM                                                              !  resuspension of NO3
         tNResusNH4=sNH4S/(sDPOMS+NearZero)*tDResusPOM                                                              !  resuspension of NH4
      !=============================================================================================================!
      ! 6.2 sedimentation                                                                                           !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.1 net sedimentation calculation, based on resuspension                                               !
         !----------------------------------------------------------------------------------------------------------!
         uFunTmSed= uFunTmArrh(uTm,self%cThetaSed)                                                                  ! temperature correction of sedimentation
         aFunTauTmSet=min(1.0_rk,1.0_rk/((aFunDimSusp +NearZero )**(0.5_rk)))*uFunTmSed                             ! correction factor for settling rate (<= 1), net settling rate, in day
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.2 sedimentation of sediment coponents                                                                !
         !----------------------------------------------------------------------------------------------------------!
         uCorVSedIM=((self%fLutumRef/self%fLutum)**(0.5))*self%cVSedIM*aFunTauTmSet                                 ! sedimentation velocity of IM, in day
         uCorVSedIM=uCorVSedIM/secs_pr_day                                                                          ! convert to seconds
         tDSetIM=uCorVSedIM*sDIMW                                                                                   ! sedimentation IM
         tPSetAIM=sPAIMW/(sDIMW+NearZero)*tDSetIM                                                                  ! sedimentation PAIM
         uCorVSedPOM=self%cVSedPOM*aFunTauTmSet                                                                     ! sedimentation velocity of POM, in day
         uCorVSedPOM=uCorVSedPOM/secs_pr_day                                                                        ! convert to seconds
         tDSetPOM=uCorVSedPOM*sDPOMW                                                                                ! sedimentation flux of POM in DW
         tPSetPOM=uCorVSedPOM*sPPOMW                                                                                ! sedimentation of POM in P
         tNSetPOM=uCorVSedPOM*sNPOMW                                                                                ! sedimentation of POM in N
         tSiSetPa=uCorVSedPOM*sSiPaW                                                                                ! sedimentation of POM in Si
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 7. final state variable ROC calculations                                                                       !
   !================================================================================================================!
      ! 7.1 total abiotic fluxes                                                                                    !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDAbioIMS   = tDSetIM   - tDResusIM                                                                           ! total ROC of IM DW in the sediment
      tDAbioPOMS  = tDSetPOM  - tDResusPOM                                                                          ! total ROC of POM DW in the sediment
      tPAbioPOMS  = tPSetPOM  - tPResusPOM                                                                          ! total ROC of POM P in the sediment
      tPAbioPO4S  =           - tPResusPO4                                                                          ! total ROC of PO4 in the sediment
      tPAbioAIMS  = tPSetAIM  - tPResusAIM                                                                          ! total ROC of absorbed P in the sediment
      tNAbioNH4S  =           - tNResusNH4                                                                          ! total ROC of NH4 in the sediment
      tNAbioNO3S  =           - tNResusNO3                                                                          ! total ROC of NO3 in the sediment
      tNAbioPOMS  = tNSetPOM  - tNResusPOM                                                                          ! total ROC of POM N in the sediment
      tSiAbioPaS  = tSiSetPa  - tSiResusPa                                                                          ! total ROC of POM Si in the sediment
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 8. update variables                                                                                            !
   !================================================================================================================!
      ! 8.1 update sediment state variables                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_ODE_(self%id_sDIMS,tDAbioIMS)                                                                     !
      _SET_BOTTOM_ODE_(self%id_sDPOMS,tDAbioPOMS)                                                                   !
      _SET_BOTTOM_ODE_(self%id_sPPOMS,tPAbioPOMS)                                                                   !
      _SET_BOTTOM_ODE_(self%id_sNPOMS,tNAbioPOMS)                                                                   !
      _SET_BOTTOM_EXCHANGE_(self%id_sDPOMS_PV,tDAbioPOMS*bot_pel_conv)                                              !
      _SET_BOTTOM_EXCHANGE_(self%id_sPPOMS_PV,tPAbioPOMS*bot_pel_conv)                                              !
      _SET_BOTTOM_EXCHANGE_(self%id_sNPOMS_PV,tNAbioPOMS*bot_pel_conv)                                              !
      _SET_BOTTOM_ODE_(self%id_sSiPaS,tSiAbioPaS)                                                                   !
      _SET_BOTTOM_ODE_(self%id_sNH4S,tNAbioNH4S)                                                                    !
      _SET_BOTTOM_ODE_(self%id_sNO3S,tNAbioNO3S)                                                                    !
      _SET_BOTTOM_ODE_(self%id_sPO4S,tPAbioPO4S)                                                                    !
      _SET_BOTTOM_ODE_(self%id_sPAIMS,tPAbioAIMS)                                                                   !
      !=============================================================================================================!
      ! 8.2 update water column variables                                                                           !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_EXCHANGE_(self%id_SWDIM,  tDResusIM   -tDSetIM)                                                   !
      _SET_BOTTOM_EXCHANGE_(self%id_SWDPOM, tDResusPOM  -tDSetPOM)                                                  !
      _SET_BOTTOM_EXCHANGE_(self%id_SWNPOM, tNResusPOM  -tNSetPOM)                                                  !
      _SET_BOTTOM_EXCHANGE_(self%id_SWPPOM, tPResusPOM  -tPSetPOM)                                                  !
      _SET_BOTTOM_EXCHANGE_(self%id_SWSiPa, tSiResusPa  -tSiSetPa)                                                  !
      _SET_BOTTOM_EXCHANGE_(self%id_SWPAIM, tPResusAIM  -tPSetAIM)                                                  !   
      _SET_BOTTOM_EXCHANGE_(self%id_sNH4W,  tNResusNH4)                                                             !
      _SET_BOTTOM_EXCHANGE_(self%id_sNO3W,  tNResusNO3)                                                             !
      _SET_BOTTOM_EXCHANGE_(self%id_sPO4W,  tPResusPO4)                                                             !
      !=============================================================================================================!
      ! 8.3 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDResusDead, tDResusDead)                                                 !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_aFunTauTmSet,aFunTauTmSet)                                                !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDAbioPOMS,  tDAbioPOMS)                                                  !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDAbioIMS,   tDAbioIMS)                                                   !
      !=============================================================================================================!
      ! 8.4 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDResusIM,  tDResusIM)                                                !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDResusPOM, tDResusPOM)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNResusPOM, tNResusPOM)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPResusPOM, tPResusPOM)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiResusPa, tSiResusPa)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPResusPO4, tPResusPO4)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPResusAIM, tPResusAIM)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNResusNO3, tNResusNO3)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNResusNH4, tNResusNH4)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDSetIM,    tDSetIM)                                                  !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDSetPOM,   tDSetPOM)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNSetPOM,   tNSetPOM)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPSetPOM,   tPSetPOM)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPSetAIM,   tPSetAIM)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiSetPa,   tSiSetPa)                                                 !
      endif                                                                                                         !
      !=============================================================================================================!
   _HORIZONTAL_LOOP_END_ !!! END OF MODEL CODE::
end subroutine do_bottom
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
end module wet_resus_sed
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
