#include "fabm_driver.h"
!
! MODULE: PHYTOPLANKTON                                                                                                                                                                          
!
module wet_phytoplankton
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_expressions
   use fabm_standard_variables
   use fabm_particle
   use wet_utility, ONLY:uFunTmGaus, DayLength
   implicit none
   private
   
   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public  :: type_wet_phytoplankton
   !PHYTOPLANKTON IN WATER COLUMN::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      ! local state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                                         :: id_sDW,id_sPW,id_sNW, id_sCW
      ! diagnostic variable identifiers--------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)                                    :: id_oSiW, id_oChla, id_rPDW, id_rNDW, id_rCDW
      ! diagnostic variables relating to limitation functions----------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)                                    :: id_ext, id_phytoextinction, id_aLLim, id_aNutLim, id_aPLim, id_aNLim
      type (type_dependency_id)                                             :: id_aLLim_in, id_aNutLim_in
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)                                    :: id_wDAss, id_wDRespW, id_wDPOMW, id_wDDOMW, id_wPUpt, id_wPPOMW, id_wPDOMW, id_wPExcrW, id_wPMortPO4W
      type (type_diagnostic_variable_id)                                    :: id_wNUptNH4, id_wNUptNO3, id_wNFix, id_wNExcrW, id_wNMortNH4W, id_wNPOMW, id_wNDOMW
      type (type_diagnostic_variable_id)                                    :: id_wSiPaW, id_wSiO2MortW, id_wSiUpt, id_wSiExcrW
      type (type_diagnostic_variable_id)                                    :: id_wCO2UptW, id_wCO2RespW, id_wCDOMW, id_wCPOMW
      type (type_diagnostic_variable_id)                                    :: id_wO2Prod, id_wO2RespW, id_Swim, id_meanparout
      ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                                         :: id_SiO2poolW, id_PO4poolW, id_NO3poolW, id_NH4poolW, id_O2poolW, id_DPOMpoolW, id_NPOMpoolW, id_PPOMpoolW
      type (type_state_variable_id)                                         :: id_SiPapoolW, id_DDOMpoolW, id_NDOMpoolW, id_PDOMpoolW, id_CO2poolW, id_CPOMpoolW, id_CDOMpoolW
      ! environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_global_dependency_id)                                      :: id_Day
      type (type_dependency_id)                                             :: id_uTm, id_dz, id_par, id_meanpar, id_extc
      type (type_horizontal_dependency_id)                                  :: id_lat, id_tDResusDead, id_aFunTauTmSet
      type (type_dependency_id)                                             :: id_afCovSurfVeg
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      real(rk)                                                              :: cSigTm, cTmOpt, cPDMin, cPDMax, cNDMin, cNDMax, hSiAss, hLRef, cLOptRef, cMuMax, kDResp, kMortW, cVPUptMax, cNFixMax
      real(rk)                                                              :: cAffPUpt, cVNUptMax, cAffNUpt, fDissMort, cCPerDW, hO2BOD, fMuNFix, cSiD, cChDMin, cChDMax, cVSet, cExtSp, cDMinW
      real(rk)                                                              :: fDOMW, cVSwim, fLVMmin, fNutLimVMdown, fNutLimVMup
      logical                                                               :: lSi, lNfix, diagnostics
      integer                                                               :: qLightMethod, qTrans
   !PHYTOPLANKTON IN SEDIMENT::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      ! local state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_bottom_state_variable_id)                                  :: id_sDS,id_sPS,id_sNS, id_sCS
      type (type_state_variable_id)                                         :: id_sDS_PV,id_sPS_PV,id_sNS_PV, id_sCS_PV
      ! diagnostic variable identifiers--------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                         :: id_oSiS, id_rPDS, id_rNDS, id_rCDS
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                         :: id_tDSed, id_tPSed, id_tNSed, id_tDResus, id_tPResus, id_tNResus, id_tDPOMS, id_tDDOMS, id_tNMortNH4S, id_tNExcrS, id_tNPOMS, id_tNDOMS
      type (type_horizontal_diagnostic_variable_id)                         :: id_tPMortPO4S, id_tPExcrS, id_tPPOMS, id_tPDOMS, id_tSiPaS, id_tSiO2S, id_tSiExcrS
      type (type_horizontal_diagnostic_variable_id)                         :: id_tCSed, id_tCResus, id_tCPOMS, id_tCDOMS, id_tCRespS
      ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_bottom_state_variable_id)                                  :: id_PO4poolS, id_NH4poolS, id_DPOMpoolS, id_NPOMpoolS, id_PPOMpoolS, id_SiPapoolS, id_DDOMpoolS, id_CPOMpoolS, id_CDOMpoolS !id_NO3poolS tka 27/3 2025
      type (type_bottom_state_variable_id)                                  :: id_NDOMpoolS,id_PDOMpoolS,id_SiO2poolS
      type (type_state_variable_id)                                         :: id_DPOMpoolS_PV,id_PPOMpoolS_PV,id_NPOMpoolS_PV, id_CPOMpoolS_PV, id_DDOMpoolS_PV,id_PDOMpoolS_PV,id_NDOMpoolS_PV, id_CDOMpoolS_PV
      type (type_horizontal_dependency_id)                                  :: id_bot_pel_conv
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      real(rk)                                                              :: kMortS, cDMinS, fDOMS, cResusExp, kResusMax, cVSed
                                                                                     
   contains                                                                          

   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure :: initialize
   procedure :: do
   procedure :: do_bottom
   procedure :: get_vertical_movement
   procedure :: get_light_extinction
   
   end type type_wet_phytoplankton

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: Pi=3.14159265358979_rk
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk),parameter :: molO2molC = 2.6667_rk
   real(rk),parameter ::O2PerNO3 = 1.5_rk
   real(rk),parameter :: molO2molN = 2.2857_rk
   real(rk),parameter :: mgPerg = 1000_rk

contains

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_phytoplankton), intent(inout), target :: self
   integer,                     intent(in)            :: configunit
   
   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer  :: i_mac
   character(len=64)   :: index

   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! photosynthesis parameters-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%qLightMethod,  'qLightMethod',  '-',             'lightmethod 1=no photoinhibition; 2=photoinhibition',            default=2                                          )
   call self%get_parameter(self%hLRef,         'hLRef',         'W/m2',          'qLightMethod=1; half-sat. PAR at 20*C; Lehmann function',        default=17.0_rk                                    )
   call self%get_parameter(self%cLOptRef,      'cLOptRef',      'W/m2',          'qLightMethod=2; optimum PAR at 20*C; Steele function',           default=25.0_rk                                    )
   ! nutrient uptake parameters------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%lSi,           'lSi',           '-',             'toggle Si usage',                                                default=.false.                                    )
   call self%get_parameter(self%hSiAss,        'hSiAss',        'mgSi/l',        'half-saturation constant for Si; only for lSi=.true.',           default=0.09_rk                                    )
   call self%get_parameter(self%cSiD,          'cSiD',          'mgSi/mgDW',     'lSi=.true.; Si/DW ratio',                                        default=0.15_rk                                    )
   call self%get_parameter(self%lNfix,         'lNfix',         '-',             'toggle nitrogen fixation',                                       default=.false.                                    )
   call self%get_parameter(self%cNFixMax,      'cNFixMax',      'mgN/mgDW/d',    'lNfix=.true.; maximum N fixation rate',                          default=0.01_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%fMuNFix,       'fMuNFix',       '-',             'lNfix=.true.; fraction of MuMax at max N fix.',                  default=0.9_rk                                     )
   call self%get_parameter(self%cVPUptMax,     'cVPUptMax',     'mgP/mgDW/d',    'P uptake capacity at 20*C',                                      default=0.04_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%cAffPUpt,      'cAffPUpt',      'l/mgDW/d',      'P uptake affinity',                                              default=0.8_rk,     scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%cVNUptMax,     'cVNUptMax',     'mgN/mgDW/d',    'N uptake capacity at 20*C',                                      default=0.08_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%cAffNUpt,      'cAffNUpt',      'l/mgDW/d',      'N uptake affinity',                                              default=0.2_rk,     scale_factor=1.0_rk/secs_pr_day)
   ! population-level parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cDMinW,        'cDMinW',        'gDW/m3',        'minimum DW concentration in water',                              default=0.00001_rk                                 )
   call self%get_parameter(self%cExtSp,        'cExtSp',        'm2/gDW',        'specific extinction coefficient',                                default=0.35_rk                                    )
   call self%get_parameter(self%qTrans,        'qTrans',        '-',             'vert. trans. method: 0=no trans.; 1=constant; 2=Nut. taxis; 3=Light taxis; 4=N&L)',  default=1                      )
   call self%get_parameter(self%cVSwim,        'cVSwim',        'm/d',           'qTrans > 1; vertical swimming speed',                            default=10.0_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%fLVMmin,       'fLVMmin',       'W/m2',          'qTrans > 2; minimum detectable PAR level',                       default=0.025_rk                                   )
   call self%get_parameter(self%fNutLimVMdown, 'fNutLimVMdown', '-',             'qTrans = 2 or 4; threshold nut. limitation for downwards taxis', default=0.675_rk                                   )
   call self%get_parameter(self%fNutLimVMup,   'fNutLimVMup',   '-',             'qTrans > 2 or 4; threshold nut. limitation for upwards taxis',   default=0.75_rk                                    )
   call self%get_parameter(self%cVSet,         'cVSet',         'm/d',           'qTrans = 1; settling rate; NOTE: negative in case of sinking',   default=0.05_rk,    scale_factor=1.0_rk/secs_pr_day)
   ! vital rate parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cMuMax,        'cMuMax',        '1/d',           'maximum growth rate at 20*C',                                    default=1.4_rk,     scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%kDResp,        'kDResp',        '1/d',           'maintenance respiration constant at 20*C',                       default=0.03_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%kMortW,        'kMortW',        '1/d',           'mortality constant in water',                                    default=0.01_rk,    scale_factor=1.0_rk/secs_pr_day)
   ! temperature parameters----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cSigTm,        'cSigTm',        '*C',            'growth rate temperature constant; sigma in Gaussian curve',      default=11.6_rk                                    )
   call self%get_parameter(self%cTmOpt,        'cTmOpt',        '*C',            'optimum temperature of growth rate',                             default=25.0_rk                                    )
   ! stochiometric parameters--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cPDMin,        'cPDMin',        'mgP/mgDW',      'minimum P/DW ratio',                                             default=0.003_rk                                   )
   call self%get_parameter(self%cPDMax,        'cPDMax',        'mgP/mgDW',      'maximum P/DW ratio',                                             default=0.025_rk                                   )
   call self%get_parameter(self%cNDMin,        'cNDMin',        'mgN/mgDW',      'minimum N/DW ratio',                                             default=0.018_rk                                   )
   call self%get_parameter(self%cNDMax,        'cNDMax',        'mgN/mgDW',      'maximum N/DW ratio',                                             default=0.15_rk                                    )
   call self%get_parameter(self%fDissMort,     'fDissMort',     '-',             'soluble inorganic nutrient fraction of dead cells',              default=0.2_rk                                     )
   call self%get_parameter(self%cCPerDW,       'cCPerDW',       'gC/gDW',        'C content of organic matter DW',                                 default=0.4_rk                                     )
   call self%get_parameter(self%hO2BOD,        'hO2BOD',        'mgO2/l',        'half-saturation constant for oxygen conc. on BOD',               default=1.0_rk                                     )
   call self%get_parameter(self%cChDMin,       'cChDMin',       'mgChl/mgDW',    'minimum chlorophyll/C ratio',                                    default=0.005_rk                                   )
   call self%get_parameter(self%cChDMax,       'cChDMax',       'mgChl/mgDW',    'maximum chlorophyll/C ratio',                                    default=0.015_rk                                   )
   call self%get_parameter(self%fDOMW,         'fDOMW',         '-',             'DOM fraction of dead cells',                                     default=0.0_rk                                     )
   ! sediment phytoplankton parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%kMortS,        'kMortS',        '1/d',           'mortality rate of settled phytoplankton',                        default=0.2_rk,     scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%fDOMS,         'fDOMS',         '-',             'DOM fraction of settled dead cells',                             default=0.0_rk                                     )
   call self%get_parameter(self%cDMinS,        'cDMinS',        'gDW/m3',        'minimum DW concentration in sediment',                           default=0.00001_rk                                 )
   ! settlement and resuspension parameters------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cResusExp,     'cResusExp',     '1/(gDW/m2/d)',  'exponent parameter for phytoplankton resuspension',              default=-0.379_rk                                  )
   call self%get_parameter(self%kResusMax,     'kResusMax',     '1/d',           'maximum phytoplankton resuspension rate',                        default=0.25_rk                                    )
   call self%get_parameter(self%cVSed,         'cVSed',         'm/d',           'sedimentation velocity',                                         default=0.2_rk                                     )
   ! diagnostic  parameter-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,   'diagnostics',    '-',            'toggle diagnostic output',                                       default=.false.                                    )
      
   !REGISTER MODEL VARIABLES, DEPENDENCIES & COUPLINGS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! state variables-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sDW,'sDW','gDW/m3','water column DW',initial_value=0.5_rk,    minimum=self%cDMinW,               vertical_movement= self%cVSet, no_river_dilution=.TRUE.)
   call self%register_state_variable(self%id_sPW,'sPW','gP/m3', 'water column P', initial_value=0.005_rk,  minimum=self%cDMinW * self%cPDMin, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)
   call self%register_state_variable(self%id_sNW,'sNW','gN/m3', 'water column N', initial_value=0.05_rk,   minimum=self%cDMinW * self%cNDMin, vertical_movement= self%cVSet, no_river_dilution=.TRUE.)
   call self%register_state_variable(self%id_sCW,'sCW','gC/m3', 'water column C', initial_value=0.20_rk,   minimum=self%cDMinW * self%cCPerDW,vertical_movement= self%cVSet, no_river_dilution=.TRUE.)
   if (self%qTrans == 0) then
       call self%set_variable_property(self%id_sDW,   'disable_transport',   .true.)   
       call self%set_variable_property(self%id_sNW,   'disable_transport',   .true.)
       call self%set_variable_property(self%id_sPW,   'disable_transport',   .true.)
       call self%set_variable_property(self%id_sCW,   'disable_transport',   .true.)
   endif
   call self%register_state_variable(self%id_sDS,'sDS','gDW/m2','sediment DW',    initial_value=0.001_rk,  minimum=self%cDMinS                                                                       )
   call self%register_state_variable(self%id_sPS,'sPS','gP/m2', 'sediment P',     initial_value=0.00001_rk,minimum=self%cDMinS * self%cPDMin                                                         )
   call self%register_state_variable(self%id_sNS,'sNS','gN/m2', 'sediment N',     initial_value=0.0001_rk, minimum=self%cDMinS * self%cNDMin                                                         )
   call self%register_state_variable(self%id_sCS,'sCS','gC/m2', 'sediment C',     initial_value=0.0004_rk, minimum=self%cDMinS * self%cCPerDW                                                        )
   call self%register_state_variable(self%id_sDS_PV,'sDS_PV','gDW/m2','sediment DW PV',initial_value=0.001_rk,  minimum=self%cDMinS,               no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)
   call self%register_state_variable(self%id_sPS_PV,'sPS_PV','gP/m2', 'sediment P  PV',initial_value=0.00001_rk,minimum=self%cDMinS * self%cPDMin, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)
   call self%register_state_variable(self%id_sNS_PV,'sNS_PV','gN/m2', 'sediment N  PV',initial_value=0.0001_rk, minimum=self%cDMinS * self%cNDMin, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)
   call self%register_state_variable(self%id_sCS_PV,'sCS_PV','gC/m2', 'sediment C  PV',initial_value=0.0004_rk, minimum=self%cDMinS * self%cCPerDW,no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)
   call self%set_variable_property(self%id_sDS_PV,   'disable_transport',   .true.)   
   call self%set_variable_property(self%id_sNS_PV,   'disable_transport',   .true.)
   call self%set_variable_property(self%id_sPS_PV,   'disable_transport',   .true.)
   call self%set_variable_property(self%id_sCS_PV,   'disable_transport',   .true.)
   ! register diagnostic variables---------------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%lSi) then
      call self%register_diagnostic_variable(self%id_oSiW,         'oSiW',           'g/m3 ', 'Si',                                   output=output_instantaneous,source=source_do                   )
      call self%register_diagnostic_variable(self%id_oSiS,         'oSiS',           'g/m2/s','oSiS',                                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom            )
   endif                                                                                                                                                                                             
   call self%register_diagnostic_variable(self%id_oChla,           'oChla',          'mg/m3', 'chlorophyll a',                        output=output_instantaneous,source=source_do                   )
   call self%register_diagnostic_variable(self%id_rPDW,            'rPDW',           '-',     'P/D ratio',                            output=output_instantaneous,source=source_do                   )
   call self%register_diagnostic_variable(self%id_rNDW,            'rNDW',           '-',     'N/D ratio',                            output=output_instantaneous,source=source_do                   )
   call self%register_diagnostic_variable(self%id_rCDW,            'rCDW',           '-',     'C/D ratio',                            output=output_instantaneous,source=source_do                   )
   call self%register_diagnostic_variable(self%id_ext,             'ext',            '-',     'phytoextinction factor',               output=output_instantaneous,source=source_do ) ! tka 16/5: no output
   call self%register_diagnostic_variable(self%id_phytoextinction, 'extinction',     '-',     'extinction',                           output=output_instantaneous,source=source_do                   )
   call self%register_diagnostic_variable(self%id_rPDS,            'rPDS',           '-',     'rPDS',                                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom            )
   call self%register_diagnostic_variable(self%id_rNDS,            'rNDS',           '-',     'rNDS',                                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom            )
   call self%register_diagnostic_variable(self%id_rCDS,            'rCDS',           '-',     'rCDS',                                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom            )
   call self%register_diagnostic_variable(self%id_aLLim,           'aLLim',          '-',     'light limitation factor',              output=output_instantaneous,source=source_do                   )
   call self%register_dependency(self%id_aLLim_in,                 'aLLim',          '-',     'light limitation factor')                                                                             
   call self%register_diagnostic_variable(self%id_aNutLim,         'aNutLim',        '-',     'nutrient limitation factor',           output=output_instantaneous,source=source_do                   )
   call self%register_diagnostic_variable(self%id_aPLim,           'aPLim',          '-',     'P limitation factor',                  output=output_instantaneous,source=source_do                   )
   call self%register_diagnostic_variable(self%id_aNLim,           'aNLim',          '-',     'N limitation factor',                  output=output_instantaneous,source=source_do                   )
   call self%register_dependency(self%id_aNutLim_in,               'aNutLim',        '-',     'nutrient limitation factor')
   ! Register diagnostic process output----------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_tDPOMS,          'tDPOMS',         'g/m3/s','rate DPOMS from mortality',            output=output_instantaneous,source=source_do_bottom, domain=domain_bottom            )
   call self%register_diagnostic_variable(self%id_Swim,            'Swim',           'm/s',   'rate Swim speed',                      output=output_instantaneous,source=source_get_vertical_movement)
   if (self%diagnostics) then                                                              
       call self%register_diagnostic_variable(self%id_wDAss,       'wDAss',          'g/m3/s','rate DW assimilation',                 output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wDRespW,     'wDRespW',        'g/m3/s','rate DW respiration',                  output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wDPOMW,      'wDPOMW',         'g/m3/s','rate DPOMW from mortality',            output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wDDOMW,      'wDDOMW',         'g/m3/s','rate DDOMW from mortality',            output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wPUpt,       'wPUpt',          'g/m3/s','rate P abs. uptake',                   output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wPExcrW,     'wPExcrW',        'g/m3/s','rate PO4W excreted',                   output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wPMortPO4W,  'wPMortPO4W',     'g/m3/s','rate PO4W dead',                       output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wPPOMW,      'wPPOMW',         'g/m3/s','rate PPOMW from mortality',            output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wPDOMW,      'wPDOMW',         'g/m3/s','rate PDOMW from mortality',            output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wNUptNH4,    'wNUptNH4',       'g/m3/s','rate NH4W uptake',                     output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wNUptNO3,    'wNUptNO3',       'g/m3/s','rate NO3W uptake',                     output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wNFix,       'wNFix',          'g/m3/s','rate N fixation',                      output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wNExcrW,     'wNExcrW',        'g/m3/s','rate NH4W excreted',                   output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wNMortNH4W,  'wNMortNH4W',     'g/m3/s','rate NH4W from mortality',             output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wNPOMW,      'wNPOMW',         'g/m3/s','rate NPOMW from mortality',            output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wNDOMW,      'wNDOMW',         'g/m3/s','rate NDOMW from mortality',            output=output_instantaneous,source=source_do          )
       if (self%lSi) then                                                                      
         call self%register_diagnostic_variable(self%id_wSiUpt,    'wSiUpt',         'g/m3/s','rate SiW uptake',                      output=output_instantaneous,source=source_do          )
         call self%register_diagnostic_variable(self%id_wSiExcrW,  'wSiExcrW',       'g/m3/s','rate SiW excreted',                    output=output_instantaneous,source=source_do          )
         call self%register_diagnostic_variable(self%id_wSiPaW,    'wSiPaW',         'g/m3/s','rate Si part. W from mortality',       output=output_instantaneous,source=source_do          )
         call self%register_diagnostic_variable(self%id_wSiO2MortW,'wSiO2MortW',     'g/m3/s','rate SiDOMW dead',                     output=output_instantaneous,source=source_do          )
       endif                                                                                  
       call self%register_diagnostic_variable(self%id_wO2Prod,     'wO2Prod',        'g/m3/s','rate O2 production',                   output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wO2RespW,    'wO2RespW',       'g/m3/s','rate O2 respiration',                  output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wCO2UptW,    'wCO2UptW',       'g/m3/s','rate CO2 uptake',                      output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wCO2RespW,   'wCO2RespW',      'g/m3/s','rate CO2 production',                  output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wCPOMW,      'wCPOMW',         'g/m3/s','rate CPOMW from mortality',            output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_wCDOMW,      'wCDOMW',         'g/m3/s','rate CDOMW from mortality',            output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_meanparout,  'meanparout',     'W',     'mean par for light',                   output=output_instantaneous,source=source_do          )
       call self%register_diagnostic_variable(self%id_tDSed,       'tDSed',          'g/m3/s','rate DW sedimentation',                output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tPSed,       'tPSed',          'g/m3/s','rate P sedimentation',                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tNSed,       'tNSed',          'g/m3/s','rate N sedimentation',                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tCSed,       'tCSed',          'g/m3/s','rate C sedimentation',                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tDResus,     'tDResus',        'g/m3/s','rate DW resuspension',                 output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tPResus,     'tPResus',        'g/m3/s','rate P resuspension',                  output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tNResus,     'tNResus',        'g/m3/s','rate N resuspension',                  output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tCResus,     'tCResus',        'g/m3/s','rate C resuspension',                  output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tDDOMS,      'tDDOMS',         'g/m3/s','rate DDOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tNMortNH4S,  'tNMortNH4S',     'g/m3/s','rate HN4S from mortality',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tNExcrS,     'tNExcrS',        'g/m3/s','rate HN4S excreted',                   output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tNPOMS,      'tNPOMS',         'g/m3/s','rate NPOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tNDOMS,      'tNDOMS',         'g/m3/s','rate NDOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tPMortPO4S,  'tPMortPO4S',     'g/m3/s','rate PO4S from mortality',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tPExcrS,     'tPExcrS',        'g/m3/s','rate PO4S excreted',                   output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tPPOMS,      'tPPOMS',         'g/m3/s','rate PPOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tPDOMS,      'tPDOMS',         'g/m3/s','rate PDOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tCRespS,     'tCRespS',        'g/m3/s','rate CO2 respired',                    output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tCPOMS,      'tCPOMS',         'g/m3/s','rate CPOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_tCDOMS,      'tCDOMS',         'g/m3/s','rate CDOMS from mortality',            output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )

       if (self%lSi) then                                                                                                              
         call self%register_diagnostic_variable(self%id_tSiPaS,      'tSiPaS',         'g/m3/s','rate Si part. S from mortality',       output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
         call self%register_diagnostic_variable(self%id_tSiO2S,      'tSiO2S',         'g/m3/s','rate SiDOMS from mortality',           output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
         call self%register_diagnostic_variable(self%id_tSiExcrS,    'tSiExcrS',       'g/m3/s','rate SiS excreted',                    output=output_instantaneous, domain=domain_bottom, source=source_do_bottom   )
       endif
   endif
   ! register contribution of state to global aggregate variables--------------------------------------------------------------------------------------------------------------------------------------
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totN',aggregate_variable=.true.),      self%id_sNW)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totP',aggregate_variable=.true.),      self%id_sPW)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totC',aggregate_variable=.true.),      self%id_sCW)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_chla',aggregate_variable=.true.),      self%id_oChla)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totSusPar',aggregate_variable=.true.),self%id_sDW)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_tDPOMbio',units='gDW/m2/s',aggregate_variable=.true.),self%id_tDPOMS,scale_factor=1._rk)
   ! register state variables dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_dependency(self%id_PO4poolW,           'PO4_pool_water',         'g/m3',            'PO4 pool water')
   call self%register_state_dependency(self%id_NH4poolW,           'NH4_pool_water',         'g/m3',            'NH4 pool water')
   call self%register_state_dependency(self%id_NO3poolW,           'NO3_pool_water',         'g/m3',            'NO3 pool water')
   call self%register_state_dependency(self%id_O2poolW,            'oxygen_pool_water',      'g/m3',            'oxygen_pool_water)')
   ! call self%register_state_dependency(self%id_CO2poolW,            'CO2_pool_water',      'g/m3',            'CO2_pool_water)')
   call self%register_state_dependency(self%id_DPOMpoolW,          'POM_DW_pool_water',      'g/m3',            'POM DW pool water')
   call self%register_state_dependency(self%id_NPOMpoolW,          'POM_N_pool_water',       'g/m3',            'POM N pool water')
   call self%register_state_dependency(self%id_PPOMpoolW,          'POM_P_pool_water',       'g/m3',            'POM P pool water')
   call self%register_state_dependency(self%id_CPOMpoolW,          'POM_C_pool_water',       'g/m3',            'POM C pool water')
   call self%register_state_dependency(self%id_DDOMpoolW,          'DOM_DW_pool_water',      'g/m3',            'DOM DW water')
   call self%register_state_dependency(self%id_NDOMpoolW,          'DOM_N_pool_water',       'g/m3',            'DOM N water')
   call self%register_state_dependency(self%id_PDOMpoolW,          'DOM_P_pool_water',       'g/m3',            'DOM P water')
   call self%register_state_dependency(self%id_CDOMpoolW,          'DOM_C_pool_water',       'g/m3',            'DOM C water')
   call self%register_state_dependency(self%id_PO4poolS,           'PO4_pool_sediment',      'g/m2',            'PO4 pool in sediment')
   ! call self%register_state_dependency(self%id_NO3poolS,           'NO3_pool_sediment',      'g/m2',            'NO3 pool in sediment')
   call self%register_state_dependency(self%id_NH4poolS,           'NH4_pool_sediment',      'g/m2',            'NH4 pool in sediment')
   call self%register_state_dependency(self%id_DPOMpoolS,          'POM_DW_pool_sediment',   'g/m2',            'POM DW pool in sediment')
   call self%register_state_dependency(self%id_NPOMpoolS,          'POM_N_pool_sediment',    'g/m2',            'POM N pool in sediment')
   call self%register_state_dependency(self%id_PPOMpoolS,          'POM_P_pool_sediment',    'g/m2',            'POM P pool in sediment')
   call self%register_state_dependency(self%id_CPOMpoolS,          'POM_C_pool_sediment',    'g/m2',            'POM C pool in sediment')
   call self%register_state_dependency(self%id_DPOMpoolS_PV,       'POM_DW_pool_sediment_PV','g/m2',            'POM DW pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_NPOMpoolS_PV,       'POM_N_pool_sediment_PV', 'g/m2',            'POM N pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_PPOMpoolS_PV,       'POM_P_pool_sediment_PV', 'g/m2',            'POM P pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_CPOMpoolS_PV,       'POM_C_pool_sediment_PV', 'g/m2',            'POM C pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_DDOMpoolS,          'DOM_DW_pool_sediment',   'g/m2',            'DOM DW in sediment')
   call self%register_state_dependency(self%id_NDOMpoolS,          'DOM_N_pool_sediment',    'g/m2',            'DOM N in sediment')
   call self%register_state_dependency(self%id_PDOMpoolS,          'DOM_P_pool_sediment',    'g/m2',            'DOM P in sediment')
   call self%register_state_dependency(self%id_CDOMpoolS,          'DOM_C_pool_sediment',    'g/m2',            'DOM C in sediment')
   call self%register_state_dependency(self%id_DDOMpoolS_PV,       'DOM_DW_pool_sediment_PV','g/m2',            'DOM DW in sediment pelagic mirror')
   call self%register_state_dependency(self%id_NDOMpoolS_PV,       'DOM_N_pool_sediment_PV', 'g/m2',            'DOM N in sediment pelagic mirror')
   call self%register_state_dependency(self%id_PDOMpoolS_PV,       'DOM_P_pool_sediment_PV', 'g/m2',            'DOM P in sediment pelagic mirror')
   call self%register_state_dependency(self%id_CDOMpoolS_PV,       'DOM_C_pool_sediment_PV', 'g/m2',            'DOM C in sediment pelagic mirror')
   call self%register_state_dependency(self%id_SiPapoolW,          'SiPa_pool_water',        'g/m3',            'SiPa pool water')
   call self%register_state_dependency(self%id_SiO2poolW,          'SiO2_pool_water',        'g/m3',            'SiO2 pool water')
   call self%register_state_dependency(self%id_SiPapoolS,          'SiPa_pool_sediment',     'g/m2',            'SiPa pool in sediment')
   call self%register_state_dependency(self%id_SiO2poolS,          'SiO2_pool_sediment',     'g/m2',            'SiO2 in sediment')
   ! register diagnostic dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_afCovSurfVeg,type_bulk_standard_variable(name='total_afCovSurfVeg',units='-'))
   call self%register_dependency(self%id_tDResusDead,     'base_resuspension_rate',          '-',              'base resuspension rate')
   call self%register_dependency(self%id_aFunTauTmSet,    'aFunTauTmSet',                    '-',              'basic settling rate')
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')
   ! register environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_uTm, standard_variables%temperature)
   call self%register_dependency(self%id_dz,  standard_variables%cell_thickness)
   call self%register_dependency(self%id_extc,standard_variables%attenuation_coefficient_of_photosynthetic_radiative_flux)
   call self%register_dependency(self%id_Day, standard_variables%number_of_days_since_start_of_the_year)
   call self%register_dependency(self%id_lat, standard_variables%latitude)
   call self%register_dependency(self%id_par, standard_variables%downwelling_photosynthetic_radiative_flux)
   call self%register_dependency(self%id_meanpar,temporal_mean(self%id_par,period=86400._rk,resolution=3600._rk,missing_value=0.0_rk))

   return

end subroutine initialize
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO (PELAGIC)                                                                                                                                                                       §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do(self,_ARGUMENTS_DO_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_phytoplankton), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_

   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)   :: uTm, dz, extc, Day, meanpar, meanparout, lat, aCorO2BOD, afCovSurfVeg, sDW, sPW, sNW, sSiO2W, sPO4W, sNH4W, sNO3W, sO2W, rPDW, rNDW, uFunTm, wDW, wPW, wNW, aPLim, aNLim, aSiLim, aNutLim
   real(rk)   :: aLPARBot, ufDay, uLPARSurf, uhL, uOpt, aLLim, aMuTmL, aMu, wDAss, wDRespW, ukDRespTm, wDMortW, wPMortW, wNMortW, wPUpt, aVPUpt, aVPUptMaxCr, aVNUptMaxCr, ahNUpt, aVNUpt, wNUpt
   real(rk)   :: sCW, rCDW, wCW, wCO2UptW, wCO2RespW, wCO2W, wCMortTOMW, wCPOMW, wCDOMW, wCMortW, wCAss, wCRespW, wCMortPOMW, wCMortDOMW
   real(rk)   :: wPExcrW, aNFixLim, aNFix, wNFix, wNExcrW, wNNH4W, wNNO3W, wPPO4W, wPPO4W_out, wSiSiO2W, wO2W, wDPOMW, wNPOMW, wPPOMW, wSiPaW, wDDOMW, wNDOMW, wPDOMW, wSiO2MortW, wNUptNH4, afNH4Upt, wNMortNH4W
   real(rk)   :: wNUptNO3, wPMortPO4W, wSiExcrW, wSiUpt, wO2Prod, wO2RespW, wO2UptNO3, wNMortTOMW, wPMortTOMW, wSiMortW, oSiW, rChD, oChla

   _LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
        ! 1.1 retrieve environmental dependencies                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        _GET_(self%id_uTm,uTm)                                                                                      !
        _GET_(self%id_extc,extc)                                                                                    !
        _GET_(self%id_meanpar,meanpar)                                                                              !
        meanpar=max(0.0_rk,meanpar) ! <===========================================================================================================================================================<<<<<<<<<<<
        meanparout = meanpar
        _GET_(self%id_dz,dz)                                                                                        !
        _GET_GLOBAL_(self%id_Day,Day)                                                                               !
        _GET_HORIZONTAL_(self%id_lat,lat)                                                                           !
        _GET_(self%id_afCovSurfVeg,afCovSurfVeg)                                                                    !
        afCovSurfVeg = min(1.0_rk,afCovSurfVeg)                                                                     !
        !===========================================================================================================!
        ! 1.2 retrieve state variables, & calc. current local nutrient ratios and relative abundances               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.1 phytoplankton state variables                                                                    !
           !--------------------------------------------------------------------------------------------------------!
           _GET_(self%id_sDW,sDW)                                                                                   !
           _GET_(self%id_sPW,sPW)                                                                                   !
           _GET_(self%id_sNW,sNW)                                                                                   !
           _GET_(self%id_sCW,sCW)                                                                                   !
           rPDW = sPW /(sDW+NearZero)                                                                               !
           rNDW = sNW /(sDW+NearZero)                                                                               !
           rCDW = sCW /(sDW+NearZero)                                                                               !
           if (self%lSi) then                                                                                       !
              oSiW=self%cSiD*sDW                                                                                    !
           endif                                                                                                    !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.2 nutrient variables                                                                               !
           !--------------------------------------------------------------------------------------------------------!
           _GET_(self%id_PO4poolW,sPO4W)                                                                            !
           _GET_(self%id_NH4poolW,sNH4W)                                                                            !
           _GET_(self%id_NO3poolW,sNO3W)                                                                            !
           _GET_(self%id_O2poolW,sO2W)                                                                              !
           ! _GET_(self%id_CO2poolW,sCO2W)                                                                           !
           if (self%lSi) then                                                                                       !
              _GET_(self%id_SiO2poolW,sSiO2W)                                                                       !
           endif                                                                                                    !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%! Light functions currently include 2 methods: 1) with depth dependent                                                     
   !  2. calculate temperature, light and nutrient functions                                                        ! PAR(bottom par and top par), originally from PCLake with self-shading.                                                       
   !================================================================================================================! For the monod type, we use the functions from Jef Huisman & Franz J. 1994. (eq. 7.)                                                     
        ! 2.1 temperature function                                                                                  ! The steele function is simplified. 2) Use layer-centered PAR
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::! with Monod type for non-photoinhibition based on Klepper et al. (1988)                                                     
        uFunTm = uFunTmGaus(uTm,self%cSigTm,self%cTmOpt)                                                            ! and Ebenhoh et al. (1997) with photoinhibition
        !===========================================================================================================!
        ! 2.2 Light functions for pelagic phytoplankton                                                             !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        uLPARSurf = meanpar / EXP( -extc * dz/2.0_rk )                                                              !  light at the top of the local layer
        aLPARBot = meanpar * EXP( -extc * dz/2.0_rk )                                                               !  light at the bottom of the local layer
        select case(self%qLightMethod)                                                                              !  select light limitation function
           case(1)                                                                                                  !    case 1, without photoinhibition, Chalker (1980) model
              uhL=self%hLRef*uFunTm                                                                                 !      half-saturation light intensity at current temperature
              aLLim= 1.0_rk /(extc * dz) * log((1.0_rk + uLPARSurf / uhL) / (1.0_rk + aLPARBot /uhL))               !      light limitation function, no photo-inhibition
           case(2)                                                                                                  !    case 2, Klepper et al. (1988) / Ebenhoh et al. (1997) model.
              uOpt=uFunTm*self%cLOptRef                                                                             !      half-saturation light intensity at current temperature
              aLLim = exp(1.0_rk) /(extc * dz) *(exp(- aLPARBot /uOpt) - exp(- uLPARSurf /uOpt))                    !      light limitation function, no photo-inhibition
        end select                                                                                                  !
        !===========================================================================================================!
        ! 2.2 Day length and current max growth                                                                     !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        ufDay = DayLength(lat,int(Day))                                                                             ! calculate day length
        aMuTmL = ufDay *(1.0_rk - afCovSurfVeg)*aLLim * uFunTm*self%cMuMax                                          ! calculate max growth rate as dictated by current light and temp.
        !===========================================================================================================!
        ! 2.3 nutrient limitation function                                                                          !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        aPLim = min(1.0_rk,max(0.0_rk,(1.0_rk - self%cPDMin / rPDW) * self%cPDMax /(self%cPDMax - self%cPDMin))) ! droop function for phospherous
        aNLim = min(1.0_rk,max(0.0_rk,(1.0_rk - self%cNDMin / rNDW) * self%cNDMax /(self%cNDMax - self%cNDMin))) ! droop function for nitrogen
        if (self%lSi) then                                                                                          ! if silica is used
           aSiLim = sSiO2W /(self%hSiAss + sSiO2W)                                                                  !   calculate growth dependence on silica
        else                                                                                                        !
           aSiLim = 100000000.0_rk                                                                                  !
        endif                                                                                                       !
        if (self%lNfix) then                                                                                        ! case N fiaxation turned on
           aNutLim = min(aPLim,aSiLim)                                                                              !   calculate total nutrient limitation (N not being limiting)
           aNFixLim = self%fMuNFix + aNLim*(1-self%fMuNFix)                                                         !   calculate growth rate limitation due to N fixation
           aNFix = self%cNFixMax * (1 - aNLim)                                                                      !   current specific N fixation rate
        else                                                                                                        ! case N fixation turned off (default)
           aNutLim = min(aPLim,(min(aNLim,aSiLim)))                                                                 !   calculate total nutrient limitation (N is potentially limiting)
           aNFixLim = 1.0_rk                                                                                        !   growth limitation due to N fixation equal to zero
           aNFix = 0.0_rk                                                                                           !   current specific N fixation rate equal to zero
        endif                                                                                                       !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!                                    
   !  3. Calculate growth and nutrient uptake                                                                       !                                        
   !================================================================================================================!
        ! 3.1 calculate growth rates                                                                                !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        aMu = aNutLim * aMuTmL * aNFixLim                                                                           ! calculate the current growth rate
        wDAss = aMu*sDW                                                                                             ! calculate current absolute dry weight assimilation
        wCAss = wDAss * self%cCPerDW                                                                                ! calculate current absolute C assimilation
        !===========================================================================================================!
        ! 3.2 calculate nutrient uptake rates                                                                       !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 3.2.1 Nitrogen                                                                                       !
             !------------------------------------------------------------------------------------------------------!
             aVNUptMaxCr = max(0.0_rk,self%cVNUptMax * uFunTm * (self%cNDMax - rNDW) /(self%cNDMax - self%cNDMin))  ! maximum specific N uptake rate, corrected for N/D ratio
             ahNUpt = aVNUptMaxCr / self%cAffNUpt                                                                   ! half-sat. N for uptake
             aVNUpt = (sNO3W + sNH4W) * aVNUptMaxCr /(ahNUpt + sNO3W + sNH4W)                                       ! current specific N uptake rate
             wNUpt = aVNUpt * sDW                                                                                   ! absolute N uptake rate
             wNFix = aNFix * sDW                                                                                    ! absolute N fixation rate
             !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 3.2.2 Phosphorous                                                                                    !
             !------------------------------------------------------------------------------------------------------!
             aVPUptMaxCr = max(0.0_rk,self%cVPUptMax * uFunTm *(self%cPDMax - rPDW)/(self%cPDMax - self%cPDMin))    ! maximum specific P uptake rate, corrected for P/D ratio
             aVPUpt = sPO4W * aVPUptMaxCr /(aVPUptMaxCr / self%cAffPUpt + sPO4W)                                    ! realized specific P uptake rate
             wPUpt = aVPUpt * sDW                                                                                   ! absolute P uptake rate
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. calculate respiration, excretion and mortality                                                              !
   !================================================================================================================!
        ! 4.1 calculate respiration                                                                                 !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        ukDRespTm = self%kDResp * uFunTm                                                                            ! calculate temperature corrected specific respiration
        wDRespW = ukDRespTm * sDW                                                                                   ! calculate absolute respiration rate in DW
        wCRespW = ukDRespTm * sCW                                                                                   ! calculate absolute respiration rate in C
        !===========================================================================================================!
        ! 4.2 calculate excretion                                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        wPExcrW = (2.0_rk * rPDW) /(self%cPDMax + rPDW) * rPDW * wDRespW                                            ! calculate absolute P excretion rate
        wNExcrW = (2.0_rk * rNDW) /(self%cNDMax + rNDW) * rNDW * wDRespW                                            ! calculate absolute N excretion rate
        !===========================================================================================================!
        ! 4.3 calculate mortality                                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        wDMortW = self%kMortW * sDW                                                                                 ! calculate mortality rate in DW
        wPMortW = self%kMortW * sPW                                                                                 ! calculate mortality rate in P
        wNMortW = self%kMortW * sNW                                                                                 ! calculate mortality rate in N
        wCMortW = self%kMortW * sCW                                                                                 ! calculate mortality rate in C
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 5. final flux calculations                                                                                     !
   !================================================================================================================!
        ! 5.1 final phytoplankton rate of change                                                                    !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        wDW = wDAss - wDRespW - wDMortW                                                                             ! calculate final ROC in DW
        wPW = wPUpt - wPExcrW  - wPMortW                                                                            ! calculate final ROC in P
        wNW = wNUpt + wNFix - wNExcrW - wNMortW                                                                     ! calculate final ROC in N
        wCW = wCAss - wCRespW - wCMortW                                                                             ! calculate final ROC in C
        !===========================================================================================================!
        ! 5.2 final fluxes to external abiotic variables                                                            !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.2.1 dry weight                                                                                       !
           !--------------------------------------------------------------------------------------------------------!
           wDPOMW = wDMortW * (1.0_rk - self%fDOMW)                                                                 ! mortality flux to POM
           wDDOMW = wDMortW * self%fDOMW                                                                            ! martality flux to DOM
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.2.2 nitrogen                                                                                         !
           !--------------------------------------------------------------------------------------------------------!
           afNH4Upt = sNH4W*sNO3W/((ahNUpt+sNH4W)*(ahNUpt+sNO3W)) + sNH4W*ahNUpt/((sNH4W+sNO3W)*(ahNUpt+sNO3W))     ! fraction of N uptake taken as ammonia
           wNUptNH4 = afNH4Upt * wNUpt                                                                              ! absolute ammonia uptake
           wNMortNH4W = self%fDissMort * wNMortW                                                                    ! fraction of mortality N released as ammonia
           wNNH4W = wNExcrW + wNMortNH4W - wNUptNH4                                                                 ! total flux of ammonia to the water column
           wNUptNO3 = wNUpt - wNUptNH4                                                                              ! absolute nitrogen uptake
           wNNO3W = - wNUptNO3                                                                                      ! total flux of nitrate to the water column
           wNMortTOMW = wNMortW - wNMortNH4W                                                                        ! part of mortality N bound in organic matter
           wNPOMW = wNMortTOMW * (1.0_rk - self%fDOMW)                                                              ! flux of POM-bound N to water column
           wNDOMW = wNMortTOMW * self%fDOMW                                                                         ! flux of DOM-bound N to water column
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.2.3 phosphorous                                                                                      !
           !--------------------------------------------------------------------------------------------------------!
           wPMortPO4W = self%fDissMort * wPMortW                                                                    ! fraction of mortality P released as phosphate
           wPPO4W = wPExcrW + wPMortPO4W - wPUpt                                                                    ! total flux of phosphate to the water column  
           wPMortTOMW = wPMortW - wPMortPO4W                                                                        ! part of mortality P bound in organic matter
           wPPOMW = wPMortTOMW * (1.0_rk - self%fDOMW)                                                              ! flux of POM-bound P to water column
           wPDOMW = wPMortTOMW * self%fDOMW                                                                         ! flux of DOM-bound P to water column
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.2.4 silica                                                                                           !
           !--------------------------------------------------------------------------------------------------------!
           if (self%lSi) then                                                                                       !
              wSiUpt = self%cSiD * wDAss                                                                            ! calculate Si uptake
              wSiExcrW = self%cSiD * wDRespW                                                                        ! calculate Si excretion
              wSiMortW = self%cSiD * wDMortW                                                                        ! silica bound in dead phytoplankton
              wSiPaW = wSiMortW * (1.0_rk - self%fDOMW)                                                             ! flux of particulate organic silica to water column
              wSiO2MortW = wSiMortW * self%fDOMW                                                                    ! flux of dissolved organic silica to water column
              wSiSiO2W = wSiExcrW + wSiO2MortW - wSiUpt                                                             ! total SiO2 flux to water column
           endif                                                                                                    !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.2.5 oxygen                                                                                           !
           !--------------------------------------------------------------------------------------------------------!
           wO2Prod = molO2molC * self%cCPerDW * wDAss                                                               ! calculate photosynthetic O2 production
           aCorO2BOD = sO2W / (self%hO2BOD + sO2W)                                                                  ! "correction_of_O2_demand_in_water_at_low_oxygen_conc"
           wO2RespW = molO2molC * self%cCPerDW * wDRespW * aCorO2BOD                                                ! calculate uptake of O2 due to respiration
           wO2UptNO3 = O2PerNO3 * molO2molN * wNUptNO3                                                              ! calculate O2 reduction due to NO3 uptake
           wO2W = wO2Prod - wO2RespW + wO2UptNO3                                                                    ! calculate total O2 flux to the water column
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.2.6 carbon                                                                                           !
           !--------------------------------------------------------------------------------------------------------!
           wCO2UptW = wCAss                                                                                         ! calculate photosynthetic CO2 uptake
           wCO2RespW = wCRespW * aCorO2BOD                                                                          ! calculate uptake of CO2 due to respiration
           wCO2W = wCO2UptW - wCO2RespW                                                                             ! calculate total CO2 flux to the water column
           wCMortTOMW = wCMortW                                                                                     ! flux of dead C in organic matter
           wCPOMW = wCMortTOMW * (1.0_rk - self%fDOMW)                                                              ! flux of POM-bound C to water column
           wCDOMW = wCMortTOMW * self%fDOMW                                                                         ! flux of DOM-bound C to water column
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 6. update model variables                                                                                      !
   !================================================================================================================!
      ! 6.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_ODE_(self%id_sDW, wDW)                                                                                   ! update phytoplankton DW ODE
      _SET_ODE_(self%id_sPW, wPW)                                                                                   ! update phytoplankton P ODE
      _SET_ODE_(self%id_sNW, wNW)                                                                                   ! update phytoplankton N ODE
      _SET_ODE_(self%id_sCW, wCW)                                                                                   ! update phytoplankton C ODE
      !=============================================================================================================!
      ! 6.2 update external abiotic state variables                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_ODE_(self%id_PO4poolW,       wPPO4W   )                                                                  ! update ODE
      _SET_ODE_(self%id_NO3poolW,       wNNO3W   )                                                                  ! update ODE
      _SET_ODE_(self%id_NH4poolW,       wNNH4W   )                                                                  ! update ODE
      _SET_ODE_(self%id_O2poolW,        wO2W     )                                                                  ! update ODE
      ! _SET_ODE_(self%id_CO2poolW,        wCO2W     )                                                                ! update ODE
      _SET_ODE_(self%id_DPOMpoolW,      wDPOMW   )                                                                  ! update ODE
      _SET_ODE_(self%id_NPOMpoolW,      wNPOMW   )                                                                  ! update ODE
      _SET_ODE_(self%id_PPOMpoolW,      wPPOMW   )                                                                  ! update ODE
      _SET_ODE_(self%id_DDOMpoolW,      wDDOMW   )                                                                  ! update ODE
      _SET_ODE_(self%id_NDOMpoolW,      wNDOMW   )                                                                  ! update ODE
      _SET_ODE_(self%id_PDOMpoolW,      wPDOMW   )                                                                  ! update ODE
      _SET_ODE_(self%id_CPOMpoolW,      wCPOMW   )                                                                  ! update ODE
      _SET_ODE_(self%id_CDOMpoolW,      wCDOMW   )                                                                  ! update ODE
      if (self%lSi) then                                                                                            !
         _SET_ODE_(self%id_SiPapoolW,  wSiPaW    )                                                                  ! update ODE
         _SET_ODE_(self%id_SiO2poolW,  wSiSiO2W  )                                                                  ! update ODE
      endif                                                                                                         !
      !=============================================================================================================!
      ! 6.3 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 6.3.1 chlorophyl-a                                                                                     !
           !--------------------------------------------------------------------------------------------------------!
           rChD = self%cChDMax - (self%cChDMax - self%cChDMin) * aLLim                                              ! calculate chlorophyll-a/DW ratio
           oChla = mgPerg * rChD * sDW                                                                              ! calculate chlorophyll-a concentration
           _SET_DIAGNOSTIC_(self%id_oChla, oChla)                                                                   ! save chlorophyl-a diagnostic
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 6.3.2 other diagnostics                                                                                !
           !--------------------------------------------------------------------------------------------------------!
           if (self%lSi) then                                                                                       !
              _SET_DIAGNOSTIC_(self%id_oSiW,         oSiW)                                                          ! save diagnostic
           endif                                                                                                    !
           _SET_DIAGNOSTIC_(self%id_rPDW,            rPDW)                                                          ! save diagnostic
           _SET_DIAGNOSTIC_(self%id_rNDW,            rNDW)                                                          ! save diagnostic
           _SET_DIAGNOSTIC_(self%id_rCDW,            rCDW)                                                          ! save diagnostic
           _SET_DIAGNOSTIC_(self%id_aLLim,           aLLim)                                                         ! save diagnostic
           _SET_DIAGNOSTIC_(self%id_aNutLim,         aNutLim)                                                       ! save diagnostic
           _SET_DIAGNOSTIC_(self%id_aPLim,           aPLim)                                                         ! save diagnostic
           _SET_DIAGNOSTIC_(self%id_aNLim,           aNLim)                                                         ! save diagnostic
           _SET_DIAGNOSTIC_(self%id_phytoextinction, extc)                                                          ! save diagnostic
      !=============================================================================================================!
      ! 6.4 update diagnostic output processes                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
          _SET_DIAGNOSTIC_(self%id_wDAss,      wDAss)                                                               !  
          _SET_DIAGNOSTIC_(self%id_wDRespW,    wDRespW)                                                             !
          _SET_DIAGNOSTIC_(self%id_wDPOMW,     wDPOMW)                                                              !
          _SET_DIAGNOSTIC_(self%id_wDDOMW,     wDDOMW)                                                              !
          _SET_DIAGNOSTIC_(self%id_wPUpt,      wPUpt)                                                               !
          _SET_DIAGNOSTIC_(self%id_wPExcrW,    wPExcrW)                                                             !
          _SET_DIAGNOSTIC_(self%id_wPMortPO4W, wPMortPO4W)                                                          !     
          _SET_DIAGNOSTIC_(self%id_wPPOMW,     wPPOMW)                                                              !
          _SET_DIAGNOSTIC_(self%id_wPDOMW,     wPDOMW)                                                              !
          _SET_DIAGNOSTIC_(self%id_wNUptNH4,   wNUptNH4)                                                            !
          _SET_DIAGNOSTIC_(self%id_wNUptNO3,   wNUptNO3)                                                            !
          _SET_DIAGNOSTIC_(self%id_wNFix,      wNFix)                                                               !
          _SET_DIAGNOSTIC_(self%id_wNExcrW,    wNExcrW)                                                             !
          _SET_DIAGNOSTIC_(self%id_wNMortNH4W, wNMortNH4W)                                                          !
          _SET_DIAGNOSTIC_(self%id_wNPOMW,     wNPOMW)                                                              !
          _SET_DIAGNOSTIC_(self%id_wNDOMW,     wNDOMW)                                                              !
          _SET_DIAGNOSTIC_(self%id_wCO2UptW,   wCO2UptW)                                                            !
          _SET_DIAGNOSTIC_(self%id_wCO2RespW,  wCO2RespW)                                                           !
          _SET_DIAGNOSTIC_(self%id_wCPOMW,     wCPOMW)                                                              !
          _SET_DIAGNOSTIC_(self%id_wCDOMW,     wCDOMW)                                                              !
          _SET_DIAGNOSTIC_(self%id_meanparout, meanparout)                                                          !
          if (self%lSi) then                                                                                        !
            _SET_DIAGNOSTIC_(self%id_wSiUpt,   wSiUpt)                                                              !
            _SET_DIAGNOSTIC_(self%id_wSiExcrW, wSiExcrW)                                                            !
            _SET_DIAGNOSTIC_(self%id_wSiPaW,   wSiPaW)                                                              !
            _SET_DIAGNOSTIC_(self%id_wSiO2MortW, wSiO2MortW)                                                        !
          endif                                                                                                     !
          _SET_DIAGNOSTIC_(self%id_wO2Prod,    wO2Prod)                                                             !
          _SET_DIAGNOSTIC_(self%id_wO2RespW,   wO2RespW)                                                            !
      endif                                                                                                         !
   !================================================================================================================!
   _LOOP_END_ !!! END OF MODEL CODE::
end subroutine do

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO BOTTOM                                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_phytoplankton), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)   :: sDS, sPS, sNS, sDW, sNW, sPW, oSiS, uTm, dz, sPO4S, sNH4S, sSiO2W, sDPOMS, sNPOMS, sPPOMS, sSiPaS, rPDS, rNDS, rNDW, rPDW, uFunTm, tDS, tDMortS, tDRespS, ukDRespTm, tDW
   real(rk)   :: tNS, tNMortS, tNExcrS, tNW, tPS, tPMortS, tPExcrS, tPW, tNNH4S, tNMortNH4S, tNNO3S, tPPO4S, tPMortPO4S, tDPOMS, tNPOMS, tNMortTOMS, tPPOMS, tPMortTOMS, tSiPaS, tSiMortS, tSiExcrS
   real(rk)   :: sCS, rCDS, sCW, rCDW, sCPOMS, tCRespS, tCMortS, tCSed, tCResus, tCS, tCW, tCPOMS, tCDOMS, sO2W, tO2W, aCorO2BOD, tO2RespS
   real(rk)   :: tSiO2S, tDDOMS, tNDOMS, tPDOMS, akResusRef, tDResusDead, aFunTauTmSet, tDResus, tNResus, tPResus, uCorVSed, tDSed, tNSed, tPSed, bot_pel_conv

   _HORIZONTAL_LOOP_BEGIN_  !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
        ! 1.1 retrieve environmental dependencies                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        _GET_(self%id_uTm,uTm)                                                                                      !
        _GET_(self%id_dz,dz)                                                                                        !
        _GET_HORIZONTAL_(self%id_tDResusDead,tDResusDead)                                                           !
        _GET_HORIZONTAL_(self%id_aFunTauTmSet,aFunTauTmSet)                                                         !
        !===========================================================================================================!
        ! 1.2 retrieve state variables, & calc. current local nutrient ratios and relative abundances               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.1 phytoplankton state variables                                                                    !
           !--------------------------------------------------------------------------------------------------------!
           _GET_HORIZONTAL_(self%id_sDS,sDS)                                                                        !
           _GET_HORIZONTAL_(self%id_sNS,sNS)                                                                        !
           _GET_HORIZONTAL_(self%id_sPS,sPS)                                                                        !
           _GET_HORIZONTAL_(self%id_sCS,sCS)                                                                        !
           rPDS = sPS /(sDS+NearZero)                                                                               !
           rNDS = sNS /(sDS+NearZero)                                                                               !
           rCDS = sCS /(sDS+NearZero)                                                                               !
           if (self%lSi) then                                                                                       !
              oSiS=self%cSiD*sDS                                                                                    !
           endif                                                                                                    !
           _GET_(self%id_sDW,sDW)                                                                                   !
           _GET_(self%id_sNW,sNW)                                                                                   !
           _GET_(self%id_sPW,sPW)                                                                                   !
           _GET_(self%id_sCW,sCW)                                                                                   !
           rPDW = sPW /(sDW+NearZero)                                                                               !
           rNDW = sNW /(sDW+NearZero)                                                                               !
           rCDW = sCW /(sDW+NearZero)                                                                               !                                                                                                           !
           _GET_(self%id_O2poolW,sO2W)                                                                              !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.2 nutrient variables                                                                               !
           !--------------------------------------------------------------------------------------------------------!
           _GET_HORIZONTAL_(self%id_PO4poolS,sPO4S)                                                                 !
           ! _GET_HORIZONTAL_(self%id_NO3poolS,sNO3S)                                                                 ! tka 27/3 2025: should be deleted 
           _GET_HORIZONTAL_(self%id_NH4poolS,sNH4S)                                                                 !
           _GET_HORIZONTAL_(self%id_DPOMpoolS,sDPOMS)                                                               !
           _GET_HORIZONTAL_(self%id_NPOMpoolS,sNPOMS)                                                               !
           _GET_HORIZONTAL_(self%id_PPOMpoolS,sPPOMS)                                                               !
           _GET_HORIZONTAL_(self%id_CPOMpoolS,sCPOMS)                                                               !
           if (self%lSi) then                                                                                       !
              _GET_HORIZONTAL_(self%id_SiPapoolS,sSiPaS)                                                           !
              _GET_(self%id_SiO2poolW,sSiO2W)                                                                       !
           endif                                                                                                    !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!                                      
   !  2. calculate respiration, excretion and mortality                                                             !                                          
   !================================================================================================================!                                                     
        ! 2.1 temperature function                                                                                  !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                        
        uFunTm = uFunTmGaus(uTm,self%cSigTm,self%cTmOpt)                                                            ! temperature correction of vital rates
        !===========================================================================================================!
        ! 2.2 calculate respiration                                                                                 !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        ukDRespTm = self%kDResp * uFunTm                                                                            ! temperature corrected specific respiration
        tDRespS = ukDRespTm * sDS                                                                                   ! absolute respiration rate in DW
        tCRespS = ukDRespTm * sCS                                                                                   ! absolute respiration rate in C
        !===========================================================================================================!
        ! 2.3 calculate excretion                                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tNExcrS = (2.0_rk * rNDS) /(self%cNDMax + rNDS) * rNDS * tDRespS                                            ! calculate absolute N excretion rate
        tPExcrS = (2.0_rk * rPDS) /(self%cPDMax + rPDS) * rPDS * tDRespS                                            ! calculate absolute P excretion rate
        !===========================================================================================================!
        ! 2.4 calculate mortality                                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDMortS = self%kMortS * sDS                                                                                 ! calculate absolute mortality rate in DW
        tNMortS = self%kMortS * sNS                                                                                 ! calculate absolute mortality rate in N
        tPMortS = self%kMortS * sPS                                                                                 ! calculate absolute mortality rate in P
        tCMortS = self%kMortS * sCS                                                                                 ! calculate absolute mortality rate in C
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 3. settling and reuspension                                                                                    !
   !================================================================================================================!
        ! 3.1 settling                                                                                              !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        uCorVSed = self%cVSed * aFunTauTmSet                                                                        ! corrected daily sedimentation rate
        uCorVSed = uCorVSed/secs_pr_day                                                                             ! corrected pr second sedimentation rate
        tDSed = uCorVSed * sDW                                                                                      ! absolute settlement flux, in DW
        tNSed = rNDW * tDSed                                                                                        ! absolute settlement flux, in N
        tPSed = rPDW * tDSed                                                                                        ! absolute settlement flux, in P
        tCSed = rCDW * tDSed                                                                                        ! absolute settlement flux, in C
        !===========================================================================================================!
        ! 3.2 resuspension                                                                                          !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        akResusRef = self%kResusMax * (1.0_rk - exp(self%cResusExp * tDResusDead))                                  ! corrected daily resuspension rate
        akResusRef = akResusRef/secs_pr_day                                                                         ! corrected pr second sedimentation rate
        tDResus=akResusRef*sDS                                                                                      ! absolute resuspension flux, in DW
        tNResus = rNDS * tDResus                                                                                    ! absolute resuspension flux, in N
        tPResus = rPDS * tDResus                                                                                    ! absolute resuspension flux, in P
        tCResus = rCDS * tDResus                                                                                    ! absolute resuspension flux, in C
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. final flux calculations                                                                                     !
   !================================================================================================================!
        ! 4.1 final sediment phytoplankton rate of change                                                           !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDS = tDSed - tDResus - tDMortS - tDRespS                                                                   ! calculate final ROC in DW
        tNS = tNSed - tNResus - tNMortS - tNExcrS                                                                   ! calculate final ROC in N
        tPS = tPSed - tPResus - tPMortS - tPExcrS                                                                   ! calculate final ROC in P
        tCS = tCSed - tCResus - tCMortS - tCRespS                                                                   ! calculate final ROC in C
        !===========================================================================================================!
        ! 4.2 final watercolumn phytoplankton rate of change                                                        !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDW = tDResus - tDSed                                                                                       ! calculate final ROC in DW
        tNW = tNResus - tNSed                                                                                       ! calculate final ROC in N
        tPW = tPResus - tPSed                                                                                       ! calculate final ROC in P
        tCW = tCResus - tCSed                                                                                       ! calculate final ROC in C
        !===========================================================================================================!
        ! 4.3 final fluxes to external abiotic variables                                                            !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.3.1 dry weight                                                                                       !
           !--------------------------------------------------------------------------------------------------------!
           tDPOMS = tDMortS * (1.0_rk - self%fDOMS)                                                                 ! calculate DW POM flux from mortality
           tDDOMS = tDMortS * self%fDOMS                                                                            ! calculate DW DOM flux from mortality
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.3.2 nitrogen                                                                                         !
           !--------------------------------------------------------------------------------------------------------!
           tNMortNH4S = self%fDissMort * tNMortS                                                                    ! calculate ammonia flux from mortality
           tNNH4S = tNExcrS + tNMortNH4S                                                                            ! calculate total ammonia flux to the sediment
           tNMortTOMS = tNMortS - tNMortNH4S                                                                        ! calculate organic matter N flux to the sediment
           tNPOMS = tNMortTOMS * (1.0_rk - self%fDOMS)                                                              ! calculate POM N flux to the sediment
           tNDOMS = tNMortTOMS * self%fDOMS                                                                         ! calculate DOM N flux to the sediment
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.3.3 phosphorous                                                                                      !
           !--------------------------------------------------------------------------------------------------------!
           tPMortPO4S = self%fDissMort * tPMortS                                                                    ! calculate PO4 flux from mortality
           tPPO4S = tPExcrS + tPMortPO4S                                                                            ! calculate total PO4 flux to the sediment
           tPMortTOMS = tPMortS - tPMortPO4S                                                                        ! calculate organic matter P flux to the sediment
           tPPOMS = tPMortTOMS * (1.0_rk - self%fDOMS)                                                              ! calculate POM P flux to the sediment
           tPDOMS = tPMortTOMS * self%fDOMS                                                                         ! calculate DOM P flux to the sediment
           !--------------------------------------------------------------------------------------------------------!
           ! 4.3.4 oxygen                                                                                           !
           !--------------------------------------------------------------------------------------------------------!
           aCorO2BOD = sO2W / (self%hO2BOD + sO2W)                                                                  ! "correction_of_O2_demand_in_water_at_low_oxygen_conc"
           tO2RespS = molO2molC * tCRespS * aCorO2BOD                                                               ! calculate uptake of O2 due to respiration
           tO2W = tO2RespS                                                                                          ! calculate total O2 flux to the water column
           !--------------------------------------------------------------------------------------------------------!
           ! 4.3.5 carbon                                                                                           !
           !--------------------------------------------------------------------------------------------------------!
           tCPOMS = tCMortS * (1.0_rk - self%fDOMS)                                                                 ! calculate C POM flux from mortality
           tCDOMS = tCMortS * self%fDOMS                                                                            ! calculate C DOM flux from mortality
           ! TODO: implement CO2 production, tCO2W from tO2RespS
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.3.6 silica                                                                                           !
           !--------------------------------------------------------------------------------------------------------!
           if (self%lSi) then                                                                                       ! 
              tSiMortS = self%cSiD * tDMortS                                                                        ! calculate silica flux from mortality
              tSiPaS = tSiMortS* (1.0_rk - self%fDOMS)                                                              ! calculate POM part of mortality silica flux
              tSiO2S = tSiMortS * self%fDOMS                                                                        ! calculate DOM part of mortality silica flux
              tSiExcrS = self%cSiD * tDRespS                                                                        ! calculate silica excretion rate
           endif                                                                                                    !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 5. update model variables                                                                                      !
   !================================================================================================================!
      ! 5.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
            ! 5.1.1 update sediment phytoplankton                                                                   !
            !-------------------------------------------------------------------------------------------------------!
            _SET_BOTTOM_ODE_(self%id_sDS, tDS)                                                                      ! update sediment phytoplankton DW ODE
            _SET_BOTTOM_ODE_(self%id_sPS, tPS)                                                                      ! update sediment phytoplankton N ODE
            _SET_BOTTOM_ODE_(self%id_sNS, tNS)                                                                      ! update sediment phytoplankton P ODE
            _SET_BOTTOM_ODE_(self%id_sCS, tCS)                                                                      ! update sediment phytoplankton C ODE
            _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)                                                     ! 
            _SET_BOTTOM_EXCHANGE_(self%id_sDS_PV, tDS*bot_pel_conv)                                                 ! update projected sediment phytoplankton DW ODE
            _SET_BOTTOM_EXCHANGE_(self%id_sNS_PV, tNS*bot_pel_conv)                                                 ! update projected sediment phytoplankton N ODE
            _SET_BOTTOM_EXCHANGE_(self%id_sPS_PV, tPS*bot_pel_conv)                                                 ! update projected sediment phytoplankton P ODE
            _SET_BOTTOM_EXCHANGE_(self%id_sCS_PV, tCS*bot_pel_conv)                                                 ! update projected sediment phytoplankton C ODE
            !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
            ! 5.2 update water column phytoplankton                                                                 !
            !-------------------------------------------------------------------------------------------------------!
            _SET_BOTTOM_EXCHANGE_(self%id_sDW, tDW)                                                                 ! update water column phytoplankton DW ODE
            _SET_BOTTOM_EXCHANGE_(self%id_sNW, tNW)                                                                 ! update water column phytoplankton N ODE
            _SET_BOTTOM_EXCHANGE_(self%id_sPW, tPW)                                                                 ! update water column phytoplankton P ODE
            _SET_BOTTOM_EXCHANGE_(self%id_sCW, tCW)                                                                 ! update water column phytoplankton C ODE
            ! TODO: incl DO uptake from respiration and CO2 production
      !=============================================================================================================!
      ! 5.2 update external abiotic state variables                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_ODE_(self%id_PO4poolS,             tPPO4S)                                                        ! update ODE
      _SET_BOTTOM_ODE_(self%id_NH4poolS,             tNNH4S)                                                        ! update ODE
      _SET_BOTTOM_ODE_(self%id_DPOMpoolS,            tDPOMS)                                                        ! update ODE
      _SET_BOTTOM_ODE_(self%id_NPOMpoolS,            tNPOMS)                                                        ! update ODE
      _SET_BOTTOM_ODE_(self%id_PPOMpoolS,            tPPOMS)                                                        ! update ODE
      _SET_BOTTOM_ODE_(self%id_CPOMpoolS,            tCPOMS)                                                        ! update ODE
      _SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolS_PV,    tDPOMS*bot_pel_conv)                                           ! update ODE
      _SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolS_PV,    tNPOMS*bot_pel_conv)                                           ! update ODE
      _SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolS_PV,    tPPOMS*bot_pel_conv)                                           ! update ODE
      _SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolS_PV,    tCPOMS*bot_pel_conv)                                           ! update ODE
      _SET_BOTTOM_ODE_(self%id_DDOMpoolS,            tDDOMS)                                                        ! update ODE
      _SET_BOTTOM_ODE_(self%id_NDOMpoolS,            tNDOMS)                                                        ! update ODE
      _SET_BOTTOM_ODE_(self%id_PDOMpoolS,            tPDOMS)                                                        ! update ODE
      _SET_BOTTOM_ODE_(self%id_CDOMpoolS,            tCDOMS)                                                        ! update ODE
      _SET_BOTTOM_EXCHANGE_(self%id_DDOMpoolS_PV,    tDDOMS*bot_pel_conv)                                           ! update ODE
      _SET_BOTTOM_EXCHANGE_(self%id_NDOMpoolS_PV,    tNDOMS*bot_pel_conv)                                           ! update ODE
      _SET_BOTTOM_EXCHANGE_(self%id_PDOMpoolS_PV,    tPDOMS*bot_pel_conv)                                           ! update ODE
      _SET_BOTTOM_EXCHANGE_(self%id_CDOMpoolS_PV,    tCDOMS*bot_pel_conv)                                           ! update ODE
      if (self%lSi) then                                                                                            !
         _SET_BOTTOM_ODE_(self%id_SiPapoolS,         tSiPaS)                                                        ! update ODE
         _SET_BOTTOM_ODE_(self%id_SiO2poolS, tSiExcrS+tSiO2S)                                                       ! update ODE
      endif                                                                                                         !
      _SET_BOTTOM_EXCHANGE_(self%id_O2poolW,         tO2W)                                                          ! update ODE
      !=============================================================================================================!
      ! 5.3 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%lSi) then                                                                                            !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_oSiS,   oSiS)                                                          !
      endif                                                                                                         !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_rPDS,      rPDS)                                                          !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_rNDS,      rNDS)                                                          !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_rCDS,      rCDS)                                                          !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDPOMS,    tDPOMS)                                                        !
      !=============================================================================================================!
      ! 5.4 update diagnostic output processes                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDSed,      tDSed)                                                     !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNSed,      tNSed)                                                     !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPSed,      tPSed)                                                     !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCSed,      tCSed)                                                     !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDResus,    tDResus)                                                   !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPResus,    tPResus)                                                   !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNResus,    tNResus)                                                   !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCResus,    tCResus)                                                   !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDDOMS,     tDDOMS)                                                    !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNMortNH4S, tNMortNH4S)                                                !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNExcrS,    tNExcrS)                                                   !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNPOMS,     tNPOMS)                                                    !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNDOMS,     tNDOMS)                                                    !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPMortPO4S, tPMortPO4S)                                                !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPExcrS,    tPExcrS)                                                   !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPPOMS,     tPPOMS)                                                    !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPDOMS,     tPDOMS)                                                    !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCRespS,    tCRespS)                                                   !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCPOMS,     tCPOMS)                                                    !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCDOMS,     tCDOMS)                                                    !

         if (self%lSi) then                                                                                         !
            _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiPaS,  tSiPaS)                                                    !
            _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiO2S,  tSiO2S)                                                    !
            _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiExcrS,tSiExcrS)                                                  !
         endif                                                                                                      !                                                                                                   
      endif                                                                                                         !
   !================================================================================================================!
   _HORIZONTAL_LOOP_END_ !!! END OF MODEL CODE::
end subroutine do_bottom
   
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: GET VERTICAL MOVEMENT                                                                                                                                                              §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine get_vertical_movement(self,_ARGUMENTS_GET_VERTICAL_MOVEMENT_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_phytoplankton),intent(in)    :: self
   _DECLARE_ARGUMENTS_GET_VERTICAL_MOVEMENT_

   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk) :: aNutLim, par, vSWIM

   _LOOP_BEGIN_  !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve oxygen concentration and determine vertical movements                                             !
   !================================================================================================================!
   if (self%qTrans .EQ. 1) then                                                                                     ! no vertical migration
      vSWIM = self%cVSet                                                                                            ! 
   elseif (self%qTrans .EQ. 2 .OR. self%qTrans .EQ. 4) then                                                         ! vertical migration based on nutrients
      _GET_(self%id_aNutLim_in,aNutLim)                                                                             !   get nutrient limitation factor
      if (aNutLim .LT. self%fNutLimVMdown) then                                                                     !   if starved for nutrients
         vSWIM = -self%cVSwim                                                                                       !     swim down
      elseif (self%qTrans .EQ. 4 .AND. aNutLim .GT. self%fNutLimVMup) then                                          !   elseif light-based vertical migration and nutrient replete
         _GET_(self%id_par,par)                                                                                     !     get light level
         if (par .GT. self%fLVMmin) then                                                                            !     if light level is over detection treshold
            vSWIM = self%cVSwim                                                                                     !       swim up towards (more) light
         else                                                                                                       !     else
            vSWIM = self%cVSet                                                                                      !       no swimming, so settling speed
         endif                                                                                                      !
      else                                                                                                          !   no nutrient starvation and no light-based VM
         vSWIM = self%cVSet                                                                                         !     no swimming, so settling speed
      endif                                                                                                         !
   elseif (self%qTrans .EQ. 3) then                                                                                 ! vertical migration only based on light (vertical movement functions based on Ross and Sharples (2007))
      _GET_(self%id_par,par)                                                                                        !   get light level
      if (par .GT. self%fLVMmin) then                                                                               !   if light level is over detection treshold  
         vSWIM = self%cVSwim                                                                                        !     swim up towards (more) light
      else                                                                                                          !   else
         vSWIM = self%cVSet                                                                                         !     no swimming, so settling speed
      endif                                                                                                         !
   endif                                                                                                            !
   _SET_VERTICAL_MOVEMENT_(self%id_sDW,vSWIM)                                                                       ! set DW migration speed to settling rate + movement
   _SET_VERTICAL_MOVEMENT_(self%id_sPW,vSWIM)                                                                       ! set P migration speed tto settling rate + movement
   _SET_VERTICAL_MOVEMENT_(self%id_sNW,vSWIM)                                                                       ! set N migration speed to settling rate + movement
   _SET_VERTICAL_MOVEMENT_(self%id_sCW,vSWIM)                                                                       ! set C migration speed to settling rate + movement
   !================================================================================================================!
   _SET_DIAGNOSTIC_(self%id_Swim, vSWIM)
   _LOOP_END_   !!! END OF MODEL CODE::  
end subroutine get_vertical_movement

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: GET LIGHT EXTINCTION                                                                                                                                                               §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine get_light_extinction(self,_ARGUMENTS_GET_EXTINCTION_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_phytoplankton), intent(in) :: self
   _DECLARE_ARGUMENTS_GET_EXTINCTION_
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk) :: sDW
   real(rk) :: ext

   _LOOP_BEGIN_  !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values                                                                                   !
   !================================================================================================================!
   _GET_(self%id_sDW,sDW)
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. calculate extinction coefficient                                                                           !
   !================================================================================================================!
   ext=self%cExtSp*sDW
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  3. update extinction coefficient                                                                              !
   !================================================================================================================!
   _SET_EXTINCTION_(ext)
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  4. output light extinction coefficient                                                                        !
   !================================================================================================================!
   _SET_DIAGNOSTIC_(self%id_ext,ext)                                                                                !
   !================================================================================================================!
   _LOOP_END_ !!! END OF MODEL CODE::
end subroutine get_light_extinction
!
end module wet_phytoplankton
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------

