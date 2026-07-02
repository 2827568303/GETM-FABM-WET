#include "fabm_driver.h"
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ MODULE: SEDIMENT EXCHANGE (RESUSPENSION, SEDIMENTATION AND DIFFUSION)                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
module wet_sediment_exchange
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_expressions
   use fabm_particle
   use wet_utility, ONLY: uFunTmArrh,uFunTmGaus
   implicit none
   private
   
   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public :: type_wet_sediment_exchange
      ! state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_bottom_state_variable_id)                            :: id_sDIMS, id_sPAIMS, id_sNH4S, id_sNO3S, id_sPO4S, id_sSiPaS, id_sSiO2S                               
      type (type_state_variable_id)                                   :: id_sDIMW, id_sPAIMW, id_sNH4W, id_sNO3W, id_sPO4W, id_sSiPaW, id_sSiO2W
      type (type_model_id),                 allocatable, dimension(:) :: id_pom, id_dom
      type (type_bottom_state_variable_id), allocatable, dimension(:) :: id_sDPOMS, id_sNPOMS, id_sPPOMS, id_sCPOMS, id_sDDOMS, id_sNDOMS, id_sPDOMS, id_sCDOMS
      type (type_state_variable_id),        allocatable, dimension(:) :: id_sDPOMW, id_sNPOMW, id_sPPOMW, id_sCPOMW, id_sDDOMW, id_sNDOMW, id_sPDOMW, id_sCDOMW
      type (type_state_variable_id),        allocatable, dimension(:) :: id_sDPOMS_PV, id_sNPOMS_PV, id_sPPOMS_PV, id_sCPOMS_PV, id_sDDOMS_PV, id_sNDOMS_PV, id_sPDOMS_PV, id_sCDOMS_PV
      ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                                   :: id_O2ConsSed
      ! environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_dependency_id)                                       :: id_uTm, id_BioTurb, id_DragVeg
      type (type_horizontal_dependency_id)                            :: id_depth, id_shear, id_bPorS, id_bPorCorS, id_cDepthS, id_fDepthDifS, id_bot_pel_conv
      ! diagnostic variables-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDResusDead, id_aFunTauTmSet, id_tDAbioIMS, id_tDAbioTotPOMS
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDResusIM, id_tSiResusPa, id_tPResusPO4, id_tPResusAIM, id_tNResusNO3, id_tNResusNH4, id_tDSedIM, id_tPSedAIM, id_tSiSedPa
      type (type_horizontal_diagnostic_variable_id)                   :: id_tNDifNH4,id_tNDifNO3,id_tPDifPO4, id_tSiResusSiO2, id_tSiDifSiO2
      type (type_horizontal_diagnostic_variable_id), allocatable, dimension(:)   :: id_tDResusPOM, id_tNResusPOM, id_tPResusPOM, id_tCResusPOM, id_tDSedPOM, id_tNSedPOM, id_tPSedPOM, id_tCSedPOM, id_tDExchPOMS
      type (type_horizontal_diagnostic_variable_id), allocatable, dimension(:)   :: id_tDResusDOM, id_tNResusDOM, id_tPResusDOM, id_tCResusDOM, id_tDDifDOM, id_tPDifDOM, id_tNDifDOM, id_tCDifDOM
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      real(rk)                                                        :: kVegResus, cSuspMin, cSuspRef, cSuspMax, cSuspSlope, hDepthSusp, cFetchRef, cFetch, crt_shear, ref_shear, alpha, eta
      real(rk)                                                        :: cVSetMain, fLutum, fLutumRef, cThetaSed, cVSedIM, cVSedSiPa, cThetaDif, cTurbDifNut, kNDifNH4, kNDifNO3, kPDifPO4, kSiO2Dif
      !real(rk)                                                        :: cTurbDifO2, kO2Dif
      real(rk),          allocatable, dimension(:)                    :: cVSedPOM, kDDifDOM, kNDifDOM, kPDifDOM
      integer                                                         :: qResus, nMACS, nPOM, nDOM, i_pom, i_dom
      logical                                                         :: diagnostics
      
   contains

   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure ::  initialize
   procedure ::  do_bottom
   
   end type type_wet_sediment_exchange

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk),parameter :: secs_pr_day= 86400.0_rk

contains

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_sediment_exchange), intent(inout), target :: self
   integer,                            intent(in)            :: configunit

   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   character(len=64)   :: index
   integer             :: i_pom, i_dom
   
   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! Resuspension and sedimention
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
   call self%get_parameter(self%cVSedSiPa,    'cVSedSiPa',    'm/d',       'Si particulate sedimentation velocity constant at 20*C',         default=0.5_rk                                         )
   ! Diffusion
   call self%get_parameter(self%cThetaDif,    'cThetaDif',    '1/e^*C',    'temperature coefficient for diffusion',                          default=1.016_rk                                       )
   call self%get_parameter(self%cTurbDifNut,  'cTurbDifNut',  '-',         'bioturbation correction of nutrient diffusion',                  default=12.0_rk                                        )
   call self%get_parameter(self%kNDifNH4,     'kNDifNH4',     'm2/d',      'molecular NH4 diffusion constant at 20*C',                       default=0.000112_rk, scale_factor=1.0_rk/secs_pr_day   )   
   call self%get_parameter(self%kNDifNO3,     'kNDifNO3',     'm2/d',      'NO3 diffusion constant at 20*C',                                 default=0.000086_rk, scale_factor=1.0_rk/secs_pr_day   )
   call self%get_parameter(self%kPDifPO4,     'kPDifPO4',     'm2/d',      'PO4 diffusion constant at 20*C',                                 default=0.000072_rk, scale_factor=1.0_rk/secs_pr_day   )
   call self%get_parameter(self%kSiO2Dif,     'kSiO2Dif',     'm2/d',      'SiO2 diffusion constant at 20*C',                                default=0.0000864_rk,scale_factor=1.0_rk/secs_pr_day   )
   !call self%get_parameter(self%kO2Dif,       'kO2Dif',       'm2/d',      'O2 diffusion constant at 20*C',                                  default=0.00017_rk,  scale_factor=1.0_rk/secs_pr_day   )
   !call self%get_parameter(self%cTurbDifO2,   'cTurbDifO2',   '-',         'bioturbation factor for oxygen diffusion',                       default=5.0_rk                                         )
   ! diagnostics
   call self%get_parameter(self%diagnostics,  'diagnostics',  '-',         'toggle diagnostic output',                                       default=.false.                                        )
   ! POM parameters---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   ! tka 15/4: implement POM resus/sed
   call self%get_parameter(self%nPOM,                   'nPOM',                     '-',    'number of POM groups',                                           default=1                             )
   allocate (self%cVSedPOM(self%nPOM))
   !allocate (self%pom_suffix(self%nPOM))
   do i_pom=1,self%nPOM                                                                                                                                                      
       write(index,'(i0)') i_pom                                                                                                                                          
       call self%get_parameter(self%cVSedPOM(i_pom),    'cVSedPOM'//trim(index),    'm/d',  'POM sedimentation velocity constant at 20*C '//trim(index),      default=0.5_rk                        )
   end do
   ! DOM parameters---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   ! tka 16/4: implement DOM diffusion
   call self%get_parameter(self%nDOM,                   'nDOM',                     '-',    'number of DOM groups',                                           default=1                             )
   allocate (self%kDDifDOM(self%nDOM))
   allocate (self%kNDifDOM(self%nDOM))
   allocate (self%kPDifDOM(self%nDOM))
   !allocate (self%dom_suffix(self%nDOM))
   do i_dom=1,self%nDOM                                                                                                                                                      
       write(index,'(i0)') i_dom                                                                                                                                          
       call self%get_parameter(self%kDDifDOM(i_dom),    'kDDifDOM'//trim(index),    'm2/d', 'DOM diffusion constant DW at 20*C '//trim(index), default=0.002_rk,    scale_factor=1.0_rk/secs_pr_day )
       call self%get_parameter(self%kNDifDOM(i_dom),    'kNDifDOM'//trim(index),    'm2/d', 'DOM diffusion constant N at  20*C '//trim(index), default=0.000085_rk, scale_factor=1.0_rk/secs_pr_day )
       call self%get_parameter(self%kPDifDOM(i_dom),    'kPDifDOM'//trim(index),    'm2/d', 'DOM diffusion constant P at  20*C '//trim(index), default=0.00016_rk,  scale_factor=1.0_rk/secs_pr_day )
       !call self%get_parameter(self%kCDifDOM(i_dom),    'kCDifDOM'//trim(index),    'm2/d', 'DOM diffusion constant C at  20*C '//trim(index), default=0.002_rk,    scale_factor=1.0_rk/secs_pr_day )
   end do
   !REGISTER MODEL VARIABLES, DEPENDENCIES & COUPLINGS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! register state variable dependencies------------------------------------------------------------------------------------------------------------------------------------------------------------
   allocate(self%id_pom(self%nPOM))
   allocate(self%id_sDPOMW(self%nPOM))
   allocate(self%id_sNPOMW(self%nPOM))
   allocate(self%id_sPPOMW(self%nPOM))
   allocate(self%id_sCPOMW(self%nPOM))
   allocate(self%id_sDPOMS(self%nPOM))
   allocate(self%id_sNPOMS(self%nPOM))
   allocate(self%id_sPPOMS(self%nPOM))
   allocate(self%id_sCPOMS(self%nPOM))
   allocate(self%id_sDPOMS_PV(self%nPOM))
   allocate(self%id_sNPOMS_PV(self%nPOM))
   allocate(self%id_sPPOMS_PV(self%nPOM))
   allocate(self%id_sCPOMS_PV(self%nPOM))
   allocate(self%id_tDExchPOMS(self%nPOM))
   allocate(self%id_tDResusPOM(self%nPOM))
   allocate(self%id_tPResusPOM(self%nPOM))
   allocate(self%id_tNResusPOM(self%nPOM))
   allocate(self%id_tCResusPOM(self%nPOM))
   allocate(self%id_tDSedPOM(self%nPOM))
   allocate(self%id_tPSedPOM(self%nPOM))
   allocate(self%id_tNSedPOM(self%nPOM))
   allocate(self%id_tCSedPOM(self%nPOM))
   do i_pom=1,self%nPOM
       write(index,'(i0)') i_pom
       call self%register_model_dependency(self%id_pom(i_pom),                          'pom_model'//trim(index))
       ! water                                                                          
       call self%register_state_dependency(self%id_sDPOMW(i_pom),                       'POM_D_in_water_'//trim(index),           'g/m3', 'POM D'//trim(index))
       call self%register_state_dependency(self%id_sNPOMW(i_pom),                       'POM_N_in_water_'//trim(index),           'g/m3', 'POM N'//trim(index))
       call self%register_state_dependency(self%id_sPPOMW(i_pom),                       'POM_P_in_water_'//trim(index),           'g/m3', 'POM P'//trim(index))
       call self%register_state_dependency(self%id_sCPOMW(i_pom),                       'POM_C_in_water_'//trim(index),           'g/m3', 'POM C'//trim(index))
       call self%request_coupling_to_model(self%id_sDPOMW(i_pom),self%id_pom(i_pom),    'sDW')                        
       call self%request_coupling_to_model(self%id_sNPOMW(i_pom),self%id_pom(i_pom),    'sNW')
       call self%request_coupling_to_model(self%id_sPPOMW(i_pom),self%id_pom(i_pom),    'sPW')
       call self%request_coupling_to_model(self%id_sCPOMW(i_pom),self%id_pom(i_pom),    'sCW')
       ! sediment                                                                                                                 
       call self%register_state_dependency(self%id_sDPOMS(i_pom),                       'POM_D_in_sediment_'//trim(index),        'g/m2', 'POM D'//trim(index))
       call self%register_state_dependency(self%id_sNPOMS(i_pom),                       'POM_N_in_sediment_'//trim(index),        'g/m2', 'POM N'//trim(index))
       call self%register_state_dependency(self%id_sPPOMS(i_pom),                       'POM_P_in_sediment_'//trim(index),        'g/m2', 'POM P'//trim(index))
       call self%register_state_dependency(self%id_sCPOMS(i_pom),                       'POM_C_in_sediment_'//trim(index),        'g/m2', 'POM C'//trim(index))
       call self%request_coupling_to_model(self%id_sDPOMS(i_pom),self%id_pom(i_pom),    'sDS')
       call self%request_coupling_to_model(self%id_sNPOMS(i_pom),self%id_pom(i_pom),    'sNS')
       call self%request_coupling_to_model(self%id_sPPOMS(i_pom),self%id_pom(i_pom),    'sPS')
       call self%request_coupling_to_model(self%id_sCPOMS(i_pom),self%id_pom(i_pom),    'sCS')
       ! PV
       call self%register_state_dependency(self%id_sDPOMS_PV(i_pom),                    'POM_D_in_sediment_'//trim(index)//'_PV', 'g/m2', 'POM D PV pelagic mirror'//trim(index))
       call self%register_state_dependency(self%id_sNPOMS_PV(i_pom),                    'POM_N_in_sediment_'//trim(index)//'_PV', 'g/m2', 'POM N PV pelagic mirror'//trim(index))
       call self%register_state_dependency(self%id_sPPOMS_PV(i_pom),                    'POM_P_in_sediment_'//trim(index)//'_PV', 'g/m2', 'POM P PV pelagic mirror'//trim(index))
       call self%register_state_dependency(self%id_sCPOMS_PV(i_pom),                    'POM_C_in_sediment_'//trim(index)//'_PV', 'g/m2', 'POM C PV pelagic mirror'//trim(index))
       call self%request_coupling_to_model(self%id_sDPOMS_PV(i_pom),self%id_pom(i_pom), 'sDS_PV')
       call self%request_coupling_to_model(self%id_sNPOMS_PV(i_pom),self%id_pom(i_pom), 'sNS_PV')
       call self%request_coupling_to_model(self%id_sPPOMS_PV(i_pom),self%id_pom(i_pom), 'sPS_PV')
       call self%request_coupling_to_model(self%id_sCPOMS_PV(i_pom),self%id_pom(i_pom), 'sCS_PV')
       ! diagnostics
       call self%register_diagnostic_variable(self%id_tDExchPOMS(i_pom), 'tDExchPOMS_'//trim(index),	'g/m2/s','ROC DPOM exchange '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom) ! tka 17/4 for burial ROC
       if (self%diagnostics) then
	       call self%register_diagnostic_variable(self%id_tDResusPOM(i_pom), 'tDResusPOM_'//trim(index),	'g/m2/s','rate DPOM resuspended '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tPResusPOM(i_pom), 'tPResusPOM_'//trim(index),	'g/m2/s','rate PPOM resuspended '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tNResusPOM(i_pom), 'tNResusPOM_'//trim(index),	'g/m2/s','rate NPOM resuspended '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tCResusPOM(i_pom), 'tCResusPOM_'//trim(index),	'g/m2/s','rate CPOM resuspended '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tDSedPOM(i_pom),   'tDSedPOM_'//trim(index),	    'g/m2/s','rate DPOM sedimented '//trim(index), output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tPSedPOM(i_pom),   'tPSedPOM_'//trim(index),	    'g/m2/s','rate PPOM sedimented '//trim(index), output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tNSedPOM(i_pom),   'tNSedPOM_'//trim(index),	    'g/m2/s','rate NPOM sedimented '//trim(index), output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tCSedPOM(i_pom),   'tCSedPOM_'//trim(index),	    'g/m2/s','rate CPOM sedimented '//trim(index), output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       endif 
   end do
   ! DOM coupling
   allocate(self%id_dom(self%nDOM))
   allocate(self%id_sDDOMW(self%nDOM))
   allocate(self%id_sNDOMW(self%nDOM))
   allocate(self%id_sPDOMW(self%nDOM))
   allocate(self%id_sCDOMW(self%nDOM))
   allocate(self%id_sDDOMS(self%nDOM))
   allocate(self%id_sNDOMS(self%nDOM))
   allocate(self%id_sPDOMS(self%nDOM))
   allocate(self%id_sCDOMS(self%nDOM))
   allocate(self%id_sDDOMS_PV(self%nDOM))
   allocate(self%id_sNDOMS_PV(self%nDOM))
   allocate(self%id_sPDOMS_PV(self%nDOM))
   allocate(self%id_sCDOMS_PV(self%nDOM))
   allocate(self%id_tDResusDOM(self%nDOM))
   allocate(self%id_tPResusDOM(self%nDOM))
   allocate(self%id_tNResusDOM(self%nDOM))
   allocate(self%id_tCResusDOM(self%nDOM))
   allocate(self%id_tDDifDOM(self%nDOM))
   allocate(self%id_tNDifDOM(self%nDOM))
   allocate(self%id_tPDifDOM(self%nDOM))
   allocate(self%id_tCDifDOM(self%nDOM))
   do i_dom=1,self%nDOM
       write(index,'(i0)') i_dom
       call self%register_model_dependency(self%id_dom(i_dom),  'dom_model'//trim(index))
       ! water
       call self%register_state_dependency(self%id_sDDOMW(i_dom), 'DOM_D_in_water_'//trim(index), 'g/m3', 'DOM D'//trim(index))
       call self%register_state_dependency(self%id_sNDOMW(i_dom), 'DOM_N_in_water_'//trim(index), 'g/m3', 'DOM N'//trim(index))
       call self%register_state_dependency(self%id_sPDOMW(i_dom), 'DOM_P_in_water_'//trim(index), 'g/m3', 'DOM P'//trim(index))
       call self%register_state_dependency(self%id_sCDOMW(i_dom), 'DOM_C_in_water_'//trim(index), 'g/m3', 'DOM C'//trim(index))
       call self%request_coupling_to_model(self%id_sDDOMW(i_dom),self%id_dom(i_dom), 'sDW')
       call self%request_coupling_to_model(self%id_sNDOMW(i_dom),self%id_dom(i_dom), 'sNW')
       call self%request_coupling_to_model(self%id_sPDOMW(i_dom),self%id_dom(i_dom), 'sPW')
       call self%request_coupling_to_model(self%id_sCDOMW(i_dom),self%id_dom(i_dom), 'sCW')
       ! sediment
       call self%register_state_dependency(self%id_sDDOMS(i_dom), 'DOM_D_in_sediment_'//trim(index), 'g/m2', 'DOM D'//trim(index))
       call self%register_state_dependency(self%id_sNDOMS(i_dom), 'DOM_N_in_sediment_'//trim(index), 'g/m2', 'DOM N'//trim(index))
       call self%register_state_dependency(self%id_sPDOMS(i_dom), 'DOM_P_in_sediment_'//trim(index), 'g/m2', 'DOM P'//trim(index))
       call self%register_state_dependency(self%id_sCDOMS(i_dom), 'DOM_C_in_sediment_'//trim(index), 'g/m2', 'DOM C'//trim(index))
       call self%request_coupling_to_model(self%id_sDDOMS(i_dom),self%id_dom(i_dom), 'sDS')
       call self%request_coupling_to_model(self%id_sNDOMS(i_dom),self%id_dom(i_dom), 'sNS')
       call self%request_coupling_to_model(self%id_sPDOMS(i_dom),self%id_dom(i_dom), 'sPS')
       call self%request_coupling_to_model(self%id_sCDOMS(i_dom),self%id_dom(i_dom), 'sCS')
       ! PV
       call self%register_state_dependency(self%id_sDDOMS_PV(i_dom),                    'DOM_D_in_sediment_'//trim(index)//'_PV', 'g/m2', 'DOM D PV pelagic mirror'//trim(index))
       call self%register_state_dependency(self%id_sNDOMS_PV(i_dom),                    'DOM_N_in_sediment_'//trim(index)//'_PV', 'g/m2', 'DOM N PV pelagic mirror'//trim(index))
       call self%register_state_dependency(self%id_sPDOMS_PV(i_dom),                    'DOM_P_in_sediment_'//trim(index)//'_PV', 'g/m2', 'DOM P PV pelagic mirror'//trim(index))
       call self%register_state_dependency(self%id_sCDOMS_PV(i_dom),                    'DOM_C_in_sediment_'//trim(index)//'_PV', 'g/m2', 'DOM C PV pelagic mirror'//trim(index))
       call self%request_coupling_to_model(self%id_sDDOMS_PV(i_dom),self%id_dom(i_dom), 'sDS_PV')
       call self%request_coupling_to_model(self%id_sNDOMS_PV(i_dom),self%id_dom(i_dom), 'sNS_PV')
       call self%request_coupling_to_model(self%id_sPDOMS_PV(i_dom),self%id_dom(i_dom), 'sPS_PV')
       call self%request_coupling_to_model(self%id_sCDOMS_PV(i_dom),self%id_dom(i_dom), 'sCS_PV')
       ! diagnostics
       if (self%diagnostics) then
	       call self%register_diagnostic_variable(self%id_tDResusDOM(i_dom), 'tDResusDOM_'//trim(index),	'g/m2/s','rate DDOM resuspended '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tPResusDOM(i_dom), 'tPResusDOM_'//trim(index),	'g/m2/s','rate PDOM resuspended '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tNResusDOM(i_dom), 'tNResusDOM_'//trim(index),	'g/m2/s','rate NDOM resuspended '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tCResusDOM(i_dom), 'tCResusDOM_'//trim(index),	'g/m2/s','rate CDOM resuspended '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tDDifDOM(i_dom),   'tDDifDOM_'//trim(index),	    'g/m2/s','rate DDOM diffussion '//trim(index), output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tPDifDOM(i_dom),   'tPDifDOM_'//trim(index),	    'g/m2/s','rate PDOM diffussion '//trim(index), output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tNDifDOM(i_dom),   'tNDifDOM_'//trim(index),	    'g/m2/s','rate NDOM diffussion '//trim(index), output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tCDifDOM(i_dom),   'tCDifDOM_'//trim(index),	    'g/m2/s','rate CDOM diffussion '//trim(index), output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       endif 
   end do
   ! INORGANICS
   ! SEDIMENT
   call self%register_state_dependency(self%id_sDIMS,    'inorg_pool_in_sediment',          'g/m2',   'sediment inorganic matter'                                                                   )
   call self%register_state_dependency(self%id_sPO4S,    'PO4_in_sediment',                 'g/m2',   'sediment phosphate'                                                                          )
   call self%register_state_dependency(self%id_sPAIMS,   'PAIM_in_sediment',                'g/m2',   'sediment absorbed phosphate'                                                                 )
   call self%register_state_dependency(self%id_sNH4S,    'NH4_in_sediment',                 'g/m2',   'sediment ammonium'                                                                           )
   call self%register_state_dependency(self%id_sNO3S,    'NO3_in_sediment',                 'g/m2',   'sediment nitrate'                                                                            )
   call self%register_state_dependency(self%id_sSiPaS,   'particulate_Si_in_sediment',      'g/m2',   'sediment particulate Si'                                                                     )
   call self%register_state_dependency(self%id_sSiO2S,   'dissolved_Si_in_sediment',        'g/m2',   'sediment dissolved Si'                                                                       )
   ! WATER                                                                                                                                                                                                  
   call self%register_state_dependency(self%id_sSiPaW,   'particulate_Si_in_water',         'g/m2',   'water particulate Si'                                                                        )
   call self%register_state_dependency(self%id_sSiO2W,   'SiO2_in_water',                   'g/m3',   'water SiO2'                                                                                  )
   call self%register_state_dependency(self%id_sNH4W,    'NH4_in_water',                    'g/m3',   'water NH4'                                                                                   )
   call self%register_state_dependency(self%id_sNO3W,    'NO3_in_water',                    'g/m3',   'water NO3'                                                                                   )
   call self%register_state_dependency(self%id_sPO4W,    'PO4_in_water',                    'g/m3',   'water PO4'                                                                                   )
   call self%register_state_dependency(self%id_sDIMW,    'inorg_pool_in_water',             'g/m3',   'inorganic matter pool in water'                                                              )
   call self%register_state_dependency(self%id_sPAIMW,   'PAIM_in_water',                   'g/m3',   'adsorbed phosphorus in water'                                                                )
   ! call self%register_state_dependency(self%id_O2ConsSed,'oxygen_pool_water',               'g/m3',   'Oxygen pool water'                                                                           )
   ! register other dependencies---------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_shear,standard_variables%bottom_stress)
   call self%register_dependency(self%id_uTm,standard_variables%temperature)
   call self%register_dependency(self%id_depth,standard_variables%bottom_depth)

   call self%register_horizontal_dependency(self%id_bPorS,      'bPorS',      'm3/m3','sediment porosity') 
   call self%register_horizontal_dependency(self%id_bPorCorS,   'bPorCorS',   'm3/m3','sediment porosity corrected for tortuosity') 
   call self%register_horizontal_dependency(self%id_cDepthS,    'cDepthS',    'm',    'sediment depth') 
   call self%register_horizontal_dependency(self%id_fDepthDifS, 'fDepthDifS', '-',    'nutrient diffusion distance as fraction of sediment depth') 
   call self%register_dependency(self%id_BioTurb,type_bulk_standard_variable(name='total_bioturbation',units='gDW/m3/d'))
   call self%register_dependency(self%id_DragVeg,type_bulk_standard_variable(name='total_macrophyte_biomass',units='gDW/m2'))
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')  
   ! register diagnostic variables-------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_tDResusDead,   'tDResusDead', '-',     'tDResusDead',                    output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_aFunTauTmSet,  'aFunTauTmSet','-',     'basic settling rate',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tDAbioIMS,     'tDAbioIMS',   'g/m2/s','IM abiotic update',              output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tDAbioTotPOMS, 'tDAbioTotPOMS',  'g/m2/s','Total POM abiotic update',    output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   ! Register diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%diagnostics) then
       call self%register_diagnostic_variable(self%id_tDResusIM, 'tDResusIM',   'g/m2/s','rate IM resuspended',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tSiResusPa,'tSiResusPa',  'g/m2/s','rate Si particulate resuspended',output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPResusPO4,'tPResusPO4',  'g/m2/s','rate PO4 resuspended',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPResusAIM,'tPResusAIM',  'g/m2/s','rate PAIM resuspended',          output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNResusNO3,'tNResusNO3',  'g/m2/s','rate NO3 resuspended',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNResusNH4,'tNResusNH4',  'g/m2/s','rate NH4 resuspended',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDSedIM,   'tDSedIM',     'g/m2/s','rate IM sedimented',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPSedAIM,  'tPSedAIM',    'g/m2/s','rate PAIM sedimented',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tSiSedPa,  'tSiSedPa',    'g/m2/s','rate Si particulate sedimented', output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPDifPO4,  'tPDifPO4',    'g/m2/s','rate PO4 diffusion',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNDifNO3,  'tNDifNO3',    'g/m2/s','rate NO3 diffusion',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNDifNH4,  'tNDifNH4',    'g/m2/s','rate NH4 diffusion',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tSiDifSiO2,'tSiDifSiO2',  'g/m2/s','rate SiO2 diffusion',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
  endif
   return

end subroutine initialize

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO BOTTOM                                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_sediment_exchange), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)                            :: sNH4S, sNO3S, sPO4S, sPAIMS, sDIMS, sSiPaS, tDSedIM, tDResusPOMTot
   real(rk)                            :: rSiDPOMS, aFunDimSusp, sPAIMW, uCorVSedIM, uTm, depth, sNH4W, sNO3W, sPO4W
   real(rk)                            :: oNH4S, oNO3S, oPO4S, oSiO2S, tNAbioNO3S, tPSedAIM, sDIMW, tNAbioNH4S, tPAbioPO4S, akO2DifCor
   real(rk)                            :: tDAbioIMS, tPAbioAIMS, bot_pel_conv, tPDifPO4, tNDifNO3, tNDifNH4, tSiDifSiO2, sSiO2W, sSiO2S, uCorVSedSiPa, tSiSedPa
   real(rk)                            :: BioTurb, sDVeg, aFunVegResus, tDAbioTotPOMS, tSiAbioPaS, tSiAbioSiO2S, bIntVol, uFunTmDif, uCorDif, aDepthDif, cTurbDifO2
   real(rk)                            :: tDResusTauDead, tDResusBareDead, tDResusDead ,tDResusIM,  shear, tSiResusPa, tPResusPO4, tPResusAIM
   real(rk)                            :: tNResusNO3, tNResusNH4, tSiResusSiO2, uFunTmSed, aFunTauTmSet, sSiPaW, tSiSetPa, bPorS, bPorCorS, cDepthS, fDepthDifS
   real(rk), dimension(self%nPOM)      :: sDPOMW, sNPOMW, sPPOMW, sDPOMS, sNPOMS, sPPOMS, rNDPOMS, rPDPOMS, tDResusPOM, tPResusPOM, tNResusPOM, sCPOMW, sCPOMS, rCDPOMS, tCResusPOM
   real(rk), dimension(self%nPOM)      :: tDSedPOM, tPSedPOM, tNSedPOM, tDAbioPOMS, tNAbioPOMS, tPAbioPOMS, uCorVSedPOM, tCAbioPOMS, tCSedPOM
   real(rk), dimension(self%nDOM)      :: sDDOMW, sNDOMW, sPDOMW, sDDOMS, sNDOMS, sPDOMS, rNDDOMS, rPDDOMS, tDResusDOM, tPResusDOM, tNResusDOM, sCDOMW, rCDDOMS, sCDOMS, tCResusDOM
   real(rk), dimension(self%nDOM)      :: tDDifDOM, tPDifDOM, tNDifDOM, tDAbioDOMS, tNAbioDOMS, tPAbioDOMS, oDDOMS, oNDOMS, oPDOMS, oCDOMS, tCAbioDOMS, tCDifDOM
   integer                             :: i_pom, i_dom                                                                                                                                
   character(len=64)                   :: index                                                                                         
   
   _HORIZONTAL_LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
      ! 1.1 retrieve state dependencies                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.1.1 particulate organic matter                                                                         !
         !----------------------------------------------------------------------------------------------------------!
         do i_pom=1,self%nPOM                                                                                       ! for each pom
            _GET_(self%id_sDPOMW(i_pom),sDPOMW(i_pom))                                                              !   get POMW dry weight (dimensions: nPOM)
            _GET_(self%id_sNPOMW(i_pom),sNPOMW(i_pom))                                                              !   get POMW phosphorous (dimensions: nPOM)
            _GET_(self%id_sPPOMW(i_pom),sPPOMW(i_pom))                                                              !   get POMW nitrogen (dimensions: nPOM)
            _GET_(self%id_sCPOMW(i_pom),sCPOMW(i_pom))                                                              !   get POMW carbon (dimensions: nPOM)
         end do                                                                                                     !
         do i_pom=1,self%nPOM                                                                                       ! for each pom
            _GET_HORIZONTAL_(self%id_sDPOMS(i_pom),sDPOMS(i_pom))                                                   ! get POMs dry weight (dimensions: nPOM)
            _GET_HORIZONTAL_(self%id_sNPOMS(i_pom),sNPOMS(i_pom))                                                   ! get POMS phosphorous (dimensions: nPOM)
            _GET_HORIZONTAL_(self%id_sPPOMS(i_pom),sPPOMS(i_pom))                                                   ! get POMS nitrogen (dimensions: nPOM)
            _GET_HORIZONTAL_(self%id_sCPOMS(i_pom),sCPOMS(i_pom))                                                   ! get POMS carbon (dimensions: nPOM)
         end do                                                                                                     !
         rNDPOMS = sNPOMS/(sDPOMS+NearZero)                                                                         ! calculate POMS N:DW ratios (dimensions: nPOM)
         rPDPOMS = sPPOMS/(sDPOMS+NearZero)                                                                         ! calculate POMS P:DW ratios (dimensions: nPOM)
         rCDPOMS = sCPOMS/(sDPOMS+NearZero)                                                                         ! calculate POMS C:DW ratios (dimensions: nPOM)
         ! Silicone cycle                                                                                           !
         _GET_(self%id_sSiPaW,sSiPaW)                                                                               !
         _GET_HORIZONTAL_(self%id_sSiPaS,sSiPaS)                                                                    ! 
         _GET_HORIZONTAL_(self%id_sSiO2S,sSiO2S)                                                                    ! 
         rSiDPOMS=sSiPaS/(sum(sDPOMS)+NearZero)                                                                     !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.1.2 dissolved organic matter                                                                           !
         !----------------------------------------------------------------------------------------------------------!
         do i_dom=1,self%nDOM                                                                                       ! for each pom
            _GET_(self%id_sDDOMW(i_dom),sDDOMW(i_dom))                                                              !   get DOMW dry weight (dimensions: nDOM)
            _GET_(self%id_sNDOMW(i_dom),sNDOMW(i_dom))                                                              !   get DOMW nitrogen (dimensions: nDOM)
            _GET_(self%id_sPDOMW(i_dom),sPDOMW(i_dom))                                                              !   get DOMW phosphorous (dimensions: nDOM)
            _GET_(self%id_sCDOMW(i_dom),sCDOMW(i_dom))                                                              !   get DOMW carbon (dimensions: nDOM)
         end do                                                                                                     !
         do i_dom=1,self%nDOM                                                                                       ! for each pom
            _GET_HORIZONTAL_(self%id_sDDOMS(i_dom),sDDOMS(i_dom))                                                   ! get DOMs dry weight (dimensions: nDOM)
            _GET_HORIZONTAL_(self%id_sNDOMS(i_dom),sNDOMS(i_dom))                                                   ! get DOMS nitrogen (dimensions: nDOM)
            _GET_HORIZONTAL_(self%id_sPDOMS(i_dom),sPDOMS(i_dom))                                                   ! get DOMS phosphorous (dimensions: nDOM)
            _GET_HORIZONTAL_(self%id_sCDOMS(i_dom),sCDOMS(i_dom))                                                   ! get DOMS carbon (dimensions: nDOM)
         end do                                                                                                     !
         rNDDOMS = sNDOMS/(sDDOMS+NearZero)                                                                         ! calculate DOMS N:DW ratios (dimensions: nDOM)
         rPDDOMS = sPDOMS/(sDDOMS+NearZero)                                                                         ! calculate DOMS P:DW ratios (dimensions: nDOM)
         rCDDOMS = sCDOMS/(sDDOMS+NearZero)                                                                         ! calculate DOMS C:DW ratios (dimensions: nDOM)
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.1.3 inorganic matter                                                                                   !
         !----------------------------------------------------------------------------------------------------------!
         _GET_HORIZONTAL_(self%id_sPO4S,sPO4S)                                                                      !
         _GET_HORIZONTAL_(self%id_sPAIMS,sPAIMS)                                                                    !
         _GET_HORIZONTAL_(self%id_sNH4S,sNH4S)                                                                      !
         _GET_HORIZONTAL_(self%id_sNO3S,sNO3S)                                                                      !
         _GET_HORIZONTAL_(self%id_sDIMS,sDIMS)                                                                      !
         _GET_(self%id_sNH4W,sNH4W)                                                                                 !
         _GET_(self%id_sNO3W,sNO3W)                                                                                 !
         _GET_(self%id_sPO4W,sPO4W)                                                                                 !
         _GET_(self%id_sSiO2W,sSiO2W)                                                                               !
         _GET_(self%id_sDIMW,sDIMW)                                                                                 !
         _GET_(self%id_sPAIMW,sPAIMW)                                                                               !
         !_GET_(self%id_O2ConsSed,sO2W)                                                                              ! tka 23/4: was used in abiotic_sediment
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
      _GET_HORIZONTAL_(self%id_bPorCorS,bPorCorS)                                                                   !
      _GET_HORIZONTAL_(self%id_cDepthS,cDepthS)                                                                     !
      _GET_HORIZONTAL_(self%id_fDepthDifS,fDepthDifS)                                                               ! 
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. calculate resuspension and sedimentation rates                                                             !
   !================================================================================================================!
      ! 2.1 resuspension                                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.1.1 calculate macrophyte dependence of resuspension                                                    !
         !----------------------------------------------------------------------------------------------------------!
         aFunVegResus=max(0.0_rk,1.0_rk-self%kVegResus*sDVeg)                                                       ! macrophyte dependence of resuspension
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.1.2 calculate base resuspension rate                                                                   !
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
         ! 2.1.3 resuspension of sediment coponents                                                                 !
         !----------------------------------------------------------------------------------------------------------!
         tDResusIM=self%fLutum*sDIMS/(self%fLutum*sDIMS+sum(sDPOMS)+NearZero)*(tDResusDead/secs_pr_day)             !  inorganic matter resuspension
         ! tka 15/4 tDResusPOM for each POM group         
         tDResusPOMTot=sum(sDPOMS)/(self%fLutum*sDIMS+sum(sDPOMS)+NearZero)*(tDResusDead/secs_pr_day)               !  Total POM resuspension in DW
         tDResusPOM=sDPOMS/(self%fLutum*sDIMS+sum(sDPOMS)+NearZero)*(tDResusDead/secs_pr_day)                       !  POM resuspension in DW (dimensions: nPOM)
         tPResusPOM=rPDPOMS*tDResusPOM                                                                              !  POM resuspension in P (dimensions: nPOM)
         tNResusPOM=rNDPOMS*tDResusPOM                                                                              !  POM resuspension in N (dimensions: nPOM)
         tCResusPOM=rCDPOMS*tDResusPOM                                                                              !  POM resuspension in C (dimensions: nPOM)
         ! DOM resuspension
         tDResusDOM=sDDOMS/(sum(sDPOMS)+NearZero)*tDResusPOMTot                                                     !  resuspension of DW DOMW
         tPResusDOM=rPDDOMS*tDResusDOM                                                                              !  resuspension of P DOMS
         tNResusDOM=rNDDOMS*tDResusDOM                                                                              !  resuspension of N DOMS
         tCResusDOM=rCDDOMS*tDResusDOM                                                                              !  resuspension of C DOMS
         ! DIN
         tSiResusPa=rSiDPOMS*tDResusPOMTot                                                                          !  POM resuspension in SI, tka 15/4 how to handle? weight?
         tPResusAIM=sPAIMS/(sDIMS+NearZero)*tDResusIM                                                               !  resuspension adsorbed PAIM
         tPResusPO4=sPO4S/(sum(sDPOMS)+NearZero)*tDResusPOMTot                                                      !  resuspension of PO4, tka 15/4 incl ..POMTot
         tNResusNO3=sNO3S/(sum(sDPOMS)+NearZero)*tDResusPOMTot                                                      !  resuspension of NO3, tka 15/4 incl ..POMTot
         tNResusNH4=sNH4S/(sum(sDPOMS)+NearZero)*tDResusPOMTot                                                      !  resuspension of NH4, tka 15/4 incl ..POMTot
         tSiResusSiO2=sSiO2S/(sum(sDPOMS)+NearZero)*tDResusPOMTot                                                   !  resuspension of SiO2, tka 16/4 incl ..POMTot
      !=============================================================================================================!
      ! 2.2 sedimentation                                                                                           !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.2.1 net sedimentation calculation, based on resuspension                                               !
         !----------------------------------------------------------------------------------------------------------!
         uFunTmSed= uFunTmArrh(uTm,self%cThetaSed)                                                                  ! temperature correction of sedimentation
         aFunTauTmSet=min(1.0_rk,1.0_rk/((aFunDimSusp +NearZero )**(0.5_rk)))*uFunTmSed                             ! correction factor for settling rate (<= 1), net settling rate, in day
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.2.2 sedimentation of sediment coponents                                                                !
         !----------------------------------------------------------------------------------------------------------!
         uCorVSedIM=((self%fLutumRef/self%fLutum)**(0.5))*self%cVSedIM*aFunTauTmSet                                 ! sedimentation velocity of IM, in day
         uCorVSedIM=uCorVSedIM/secs_pr_day                                                                          ! convert to seconds
         ! tka 15/4 should change Set to Sed for consistency in naming!
         tDSedIM=uCorVSedIM*sDIMW                                                                                   ! sedimentation IM
         tPSedAIM=sPAIMW/(sDIMW+NearZero)*tDSedIM                                                                   ! sedimentation PAIM
         ! tka 15/4 change
         uCorVSedPOM=self%cVSedPOM*aFunTauTmSet                                                                     ! sedimentation velocity of POM, in day (dim: nPOM)
         uCorVSedPOM=uCorVSedPOM/secs_pr_day                                                                        ! convert to seconds (dim: nPOM)
         tDSedPOM=uCorVSedPOM*sDPOMW                                                                                ! sedimentation flux of POM in DW (dim: nPOM)
         tPSedPOM=uCorVSedPOM*sPPOMW                                                                                ! sedimentation of POM in P (dim: nPOM)
         tNSedPOM=uCorVSedPOM*sNPOMW                                                                                ! sedimentation of POM in N (dim: nPOM)
         tCSedPOM=uCorVSedPOM*sCPOMW                                                                                ! sedimentation of POM in C (dim: nPOM)
         ! tka 15/4 how to handle?
         uCorVSedSiPa=self%cVSedSiPa*aFunTauTmSet
         uCorVSedSiPa=uCorVSedSiPa/secs_pr_day
         tSiSedPa=uCorVSedSiPa*sSiPaW                                                                               ! sedimentation of POM in Si
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  3. calculate diffusion rates                                                                                  !
   !================================================================================================================!
      ! tka 16/4 incl in sediment_exchange                                                                          !
      bIntVol = max(NearZero, cDepthS / bPorS)                                                                      ! interstitial water volume in sediment (unit: meter)
	  !=============================================================================================================!
      ! 3.1 inorganic matter                                                                                        !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      oNO3S = max(0.0_rk, sNO3S / bIntVol)                                                                          ! conc. of dissolved NO3 in interstitial water
      oNH4S=max(0.0_rk, sNH4S / bIntVol)                                                                            ! conc. of dissolved NH4 in interstitial water
      oPO4S = max(0.0_rk, sPO4S / bIntVol)                                                                          ! conc. of dissolved PO4 in interstitial water
      oSiO2S  = sSiO2S  / bIntVol                                                                                   ! conc. of dissolved SiO2 in interstitial water
      !=============================================================================================================!
      ! 3.2 organic matter                                                                                          !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      oDDOMS  = sDDOMS  / bIntVol                                                                                   ! conc. of dissolved organic D in interstitial water
      oNDOMS  = sNDOMS  / bIntVol                                                                                   ! conc. of dissolved organic N in interstitial water
      oPDOMS  = sPDOMS  / bIntVol                                                                                   ! conc. of dissolved organic P in interstitial water
      oCDOMS  = sCDOMS  / bIntVol                                                                                   ! conc. of dissolved organic P in interstitial water
      !=============================================================================================================!
      ! 3.4 temperature function for diffusion                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      uFunTmDif= uFunTmArrh(uTm,self%cThetaDif)                                                                     ! temperature function of diffusion
      !=============================================================================================================!
      ! 3.5 diffusion of inorganic matter                                                                           !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      aDepthDif= max(NearZero, fDepthDifS*cDepthS)                                                                  ! average diffusion distance
	  uCorDif = uFunTmDif*self%cTurbDifNut*bPorCorS/aDepthDif                                                       ! corrected water to sediment diffusion constant
      tNDifNH4=self%kNDifNH4*(oNH4S-sNH4W)*uCorDif                                                                  ! diffusion flux of NH4
      tNDifNO3=self%kNDifNO3*(oNO3S-sNO3W)*uCorDif                                                                  ! diffusion flux of NO3
      tPDifPO4=self%kPDifPO4*(oPO4S-sPO4W)*uCorDif                                                                  ! diffusion flux of PO4
      tSiDifSiO2=self%kSiO2Dif*(oSiO2S-sSiO2W)*uCorDif                                                              ! diffusion flux of SiO2
      !akO2DifCor=self%kO2Dif*uFunTmDif*self%cTurbDifO2*bPorCorS                                                    ! corrected O2 diffusion coefficient, tka 23/4: used in abiotic_sediment
      !tO2Dif= akO2DifCor*sO2W/aDepthDif                                                                            ! O2_diffusion (water to sediment), tka 23/4: used in abiotic_sediment 
      !=============================================================================================================!
      ! 3.6 diffusion of organic matter                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDDifDOM =self%kDDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oDDOMS-sDDOMW)/aDepthDif                        ! diffusion flux of dissolved organic DW (dim: nDOM)
      tNDifDOM =self%kNDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oNDOMS-sNDOMW)/aDepthDif                        ! diffusion flux of dissolved organic N (dim: nDOM)
      tPDifDOM =self%kPDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oPDOMS-sPDOMW)/aDepthDif                        ! diffusion flux of dissolved organic P (dim: nDOM)
      tCDifDOM =self%kDDifDOM *uFunTmDif*self%cTurbDifNut*bPorCorS*(oCDOMS-sCDOMW)/aDepthDif                        ! diffusion flux of dissolved organic P (dim: nDOM)
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. final state variable ROC calculations                                                                       !
   !================================================================================================================!
      ! 4.1 total abiotic fluxes                                                                                    !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      ! POM
      tDAbioPOMS  = tDSedPOM  - tDResusPOM                                                                          ! total ROC of POM DW in the sediment (dim:nPOM)
      tPAbioPOMS  = tPSedPOM  - tPResusPOM                                                                          ! total ROC of POM P in the sediment (dim:nPOM)
      tNAbioPOMS  = tNSedPOM  - tNResusPOM                                                                          ! total ROC of POM N in the sediment (dim:nPOM)
      tCAbioPOMS  = tCSedPOM  - tCResusPOM                                                                          ! total ROC of POM C in the sediment (dim:nPOM)
      ! DOM
      tDAbioDOMS  = -tDDifDOM  - tDResusDOM                                                                         ! total ROC of POM DW in the sediment (dim:nDOM)
      tPAbioDOMS  = -tPDifDOM  - tPResusDOM                                                                         ! total ROC of DOM P in the sediment (dim:nDOM)
      tNAbioDOMS  = -tNDifDOM  - tNResusDOM                                                                         ! total ROC of DOM N in the sediment (dim:nDOM)
      tCAbioDOMS  = -tCDifDOM  - tCResusDOM                                                                         ! total ROC of DOM N in the sediment (dim:nDOM)
      ! DIN
      tPAbioPO4S  = -tPDifPO4 - tPResusPO4                                                                          ! total ROC of DO4 in the sediment
      tPAbioAIMS  = tPSedAIM  - tPResusAIM                                                                          ! total ROC of absorbed P in the sediment
      tNAbioNH4S  = -tNDifNH4 - tNResusNH4                                                                          ! total ROC of NH4 in the sediment
      tNAbioNO3S  = -tNDifNO3 - tNResusNO3                                                                          ! total ROC of NO3 in the sediment
      tSiAbioSiO2S = -tSiDifSiO2 - tSiResusSiO2                                                                     ! total ROC of NO3 in the sediment
      tSiAbioPaS  = tSiSedPa  - tSiResusPa                                                                          ! total ROC of POM Si in the sediment
      tDAbioIMS   = tDSedIM   - tDResusIM                                                                           ! total ROC of IM DW in the sediment
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 5. update variables                                                                                            !
   !================================================================================================================!
      ! 5.1 update sediment state variables                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_ODE_(self%id_sDIMS,tDAbioIMS)                                                                     !
      _SET_BOTTOM_ODE_(self%id_sSiPaS,tSiAbioPaS)                                                                   !
      _SET_BOTTOM_ODE_(self%id_sSiO2S,tSiAbioSiO2S)                                                                 !
      _SET_BOTTOM_ODE_(self%id_sNH4S,tNAbioNH4S)                                                                    !
      _SET_BOTTOM_ODE_(self%id_sNO3S,tNAbioNO3S)                                                                    !
      _SET_BOTTOM_ODE_(self%id_sPO4S,tPAbioPO4S)                                                                    !
      _SET_BOTTOM_ODE_(self%id_sPAIMS,tPAbioAIMS)                                                                   !
      !=============================================================================================================!
      ! 5.2 update sediment POM state variables                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      do i_pom = 1,self%nPOM                                                                                        ! for each pom, tka 15/4
         _SET_BOTTOM_ODE_(self%id_sDPOMS(i_pom),tDAbioPOMS(i_pom))                                                  !   update POMS DW ODEs (dim: nPOM)
         _SET_BOTTOM_ODE_(self%id_sNPOMS(i_pom),tNAbioPOMS(i_pom))                                                  !   update POMS N ODEs (dim: nPOM)
         _SET_BOTTOM_ODE_(self%id_sPPOMS(i_pom),tPAbioPOMS(i_pom))                                                  !   update POMS P ODEs (dim: nPOM)
         _SET_BOTTOM_ODE_(self%id_sCPOMS(i_pom),tCAbioPOMS(i_pom))                                                  !   update POMS C ODEs (dim: nPOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sDPOMS_PV(i_pom),tDAbioPOMS(i_pom)*bot_pel_conv)                             !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables) (dim: nPOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sNPOMS_PV(i_pom),tNAbioPOMS(i_pom)*bot_pel_conv)                             !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables) (dim: nPOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sPPOMS_PV(i_pom),tPAbioPOMS(i_pom)*bot_pel_conv)                             !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables) (dim: nPOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sCPOMS_PV(i_pom),tCAbioPOMS(i_pom)*bot_pel_conv)                             !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables) (dim: nPOM)
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDExchPOMS(i_pom),  tDAbioPOMS(i_pom))                                 ! tka 17/4 for ROC in burial
      end do                                                                                                        !
      !=============================================================================================================!
      ! 5.3 update sediment DOM state variables                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      do i_dom = 1,self%nDOM                                                                                        ! for each dom, tka 15/4
         _SET_BOTTOM_ODE_(self%id_sDDOMS(i_dom),tDAbioDOMS(i_dom))                                                  !   update DOMS DW ODEs (dim: nDOM)
         _SET_BOTTOM_ODE_(self%id_sNDOMS(i_dom),tNAbioDOMS(i_dom))                                                  !   update DOMS N ODEs (dim: nDOM)
         _SET_BOTTOM_ODE_(self%id_sPDOMS(i_dom),tPAbioDOMS(i_dom))                                                  !   update DOMS P ODEs (dim: nDOM)
         _SET_BOTTOM_ODE_(self%id_sCDOMS(i_dom),tCAbioDOMS(i_dom))                                                  !   update DOMS C ODEs (dim: nDOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sDDOMS_PV(i_dom),tDAbioDOMS(i_dom)*bot_pel_conv)                             !   update ROC of projected bottom variables
         _SET_BOTTOM_EXCHANGE_(self%id_sNDOMS_PV(i_dom),tNAbioDOMS(i_dom)*bot_pel_conv)                             !   update ROC of projected bottom variables
         _SET_BOTTOM_EXCHANGE_(self%id_sPDOMS_PV(i_dom),tPAbioDOMS(i_dom)*bot_pel_conv)                             !   update ROC of projected bottom variables
         _SET_BOTTOM_EXCHANGE_(self%id_sCDOMS_PV(i_dom),tCAbioDOMS(i_dom)*bot_pel_conv)                             !   update ROC of projected bottom variables
      end do                                                                                                        !
      !=============================================================================================================!
      ! 5.4 update water column variables                                                                           !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      do i_pom = 1,self%nPOM                                                                                        ! for each pom, tka 16/4
         _SET_BOTTOM_EXCHANGE_(self%id_sDPOMW(i_pom),-tDAbioPOMS(i_pom))                                            !   update POMS DW ODEs (dim: nPOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sNPOMW(i_pom),-tNAbioPOMS(i_pom))                                            !   update POMS N ODEs (dim: nPOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sPPOMW(i_pom),-tPAbioPOMS(i_pom))                                            !   update POMS P ODEs (dim: nPOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sCPOMW(i_pom),-tCAbioPOMS(i_pom))                                            !   update POMS C ODEs (dim: nPOM)
      end do                                                                                                        !
      do i_dom = 1,self%nDOM                                                                                        ! for each dom, tka 16/4
         _SET_BOTTOM_EXCHANGE_(self%id_sDDOMW(i_dom),-tDAbioDOMS(i_dom))                                            !   update POMS DW ODEs (dim: nDOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sNDOMW(i_dom),-tNAbioDOMS(i_dom))                                            !   update POMS N ODEs (dim: nDOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sPDOMW(i_dom),-tPAbioDOMS(i_dom))                                            !   update POMS P ODEs (dim: nDOM)
         _SET_BOTTOM_EXCHANGE_(self%id_sCDOMW(i_dom),-tCAbioDOMS(i_dom))                                            !   update POMS C ODEs (dim: nDOM)
      end do                                                                                                        !
      _SET_BOTTOM_EXCHANGE_(self%id_sDIMW,  tDResusIM   -tDSedIM)                                                   !
      _SET_BOTTOM_EXCHANGE_(self%id_sSiPaW, tSiResusPa  -tSiSedPa)                                                  !
      _SET_BOTTOM_EXCHANGE_(self%id_sSiO2W, tSiResusSiO2+tSiDifSiO2)                                                !
      _SET_BOTTOM_EXCHANGE_(self%id_sPAIMW, tPResusAIM  -tPSedAIM)                                                  !   
      _SET_BOTTOM_EXCHANGE_(self%id_sNH4W,  tNResusNH4  +tNDifNH4)                                                  !
      _SET_BOTTOM_EXCHANGE_(self%id_sNO3W,  tNResusNO3  +tNDifNO3)                                                  !
      _SET_BOTTOM_EXCHANGE_(self%id_sPO4W,  tPResusPO4  +tPDifPO4)                                                  !
      !=============================================================================================================!
      ! 5.5 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDResusDead, tDResusDead)                                                 !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_aFunTauTmSet,aFunTauTmSet)                                                !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDAbioTotPOMS,  sum(tDAbioPOMS))                                          ! tka 16/4
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDAbioIMS,   tDAbioIMS)                                                   !
      !=============================================================================================================!
      ! 5.6 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDResusIM,  tDResusIM)                                                !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiResusPa, tSiResusPa)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPResusPO4, tPResusPO4)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPResusAIM, tPResusAIM)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNResusNO3, tNResusNO3)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNResusNH4, tNResusNH4)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDSedIM,    tDSedIM)                                                  !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPSedAIM,   tPSedAIM)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiSedPa,   tSiSedPa)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPDifPO4,   tPDifPO4)                                                 ! 
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNDifNH4,   tNDifNH4)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNDifNO3,   tNDifNO3)                                                 ! 
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiDifSiO2, tSiDifSiO2)                                               !
          do i_pom = 1,self%nPOM                                                                                    !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDResusPOM(i_pom), tDResusPOM(i_pom))                              ! (dim:nPOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNResusPOM(i_pom), tNResusPOM(i_pom))                              ! (dim:nPOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPResusPOM(i_pom), tPResusPOM(i_pom))                              ! (dim:nPOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCResusPOM(i_pom), tCResusPOM(i_pom))                              ! (dim:nPOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDSedPOM(i_pom),   tDSedPOM(i_pom))                                ! (dim:nPOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNSedPOM(i_pom),   tNSedPOM(i_pom))                                ! (dim:nPOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPSedPOM(i_pom),   tPSedPOM(i_pom))                                ! (dim:nPOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCSedPOM(i_pom),   tCSedPOM(i_pom))                                ! (dim:nPOM)
		  end do                                                                                                    !
          do i_dom = 1,self%nDOM                                                                                    !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDResusDOM(i_dom), tDResusDOM(i_dom))                              ! (dim:nDOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNResusDOM(i_dom), tNResusDOM(i_dom))                              ! (dim:nDOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPResusDOM(i_dom), tPResusDOM(i_dom))                              ! (dim:nDOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCResusDOM(i_dom), tCResusDOM(i_dom))                              ! (dim:nDOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDDifDOM(i_dom),   tDDifDOM(i_dom))                                ! (dim:nDOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNDifDOM(i_dom),   tNDifDOM(i_dom))                                ! (dim:nDOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPDifDOM(i_dom),   tPDifDOM(i_dom))                                ! (dim:nDOM)
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCDifDOM(i_dom),   tCDifDOM(i_dom))                                ! (dim:nDOM)
		  end do                                                                                                    !          
      endif                                                                                                         !
      !=============================================================================================================!
   _HORIZONTAL_LOOP_END_ !!! END OF MODEL CODE::
end subroutine do_bottom
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
end module wet_sediment_exchange
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
