#include "fabm_driver.h"
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ MODULE: MACROPHYTES                                                                                                                                                                            §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
module wet_macrophytes
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_expressions
   use fabm_particle
   use fabm_standard_variables
   use wet_utility, ONLY:uFunTmQ10, uFunTmGaus, DayLength
   implicit none
   private

   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model), public :: type_wet_macrophytes
      ! local state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_bottom_state_variable_id)                            :: id_sDVeg,id_sNVeg,id_sPVeg, id_sCVeg
      type (type_state_variable_id)                                   :: id_sDVeg_PV,id_sNVeg_PV,id_sPVeg_PV, id_sCVeg_PV
      ! diagnostic variable for external dependencies:-----------------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)                              :: id_aDSubVeg_PV,id_aCovVeg_PV,id_afCovSurfVeg_PV, id_bfRootVeg_PV
      type (type_horizontal_diagnostic_variable_id)                   :: id_aDSubVeg,id_aCovVeg
      type (type_horizontal_diagnostic_variable_id)                   :: id_afCovSurfVeg, id_tDBedPOMS
      type (type_diagnostic_variable_id)                              :: id_aDayInitVeg_out
      type (type_dependency_id)                                       :: id_aDayInitVeg
      ! diagnostic variables for local output--------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                   :: id_tO2BedW,id_tDBedVeg, id_ufDay
      type (type_horizontal_diagnostic_variable_id)                   :: id_tNBedVeg,id_tPBedVeg, id_tCBedVeg
      type (type_horizontal_diagnostic_variable_id)                   :: id_aLPAR1Veg,id_aLPAR2Veg
      type (type_horizontal_diagnostic_variable_id)                   :: id_aLLimVeg,id_aNutLimVeg
      type (type_horizontal_diagnostic_variable_id)                   :: id_macroextinction
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDMigrVeg, id_tDProdVeg, id_tDMortVeg, id_wDBedPOMW, id_wDBedDOMW, id_tDRespVeg, id_tNMigrVeg, id_tNUptVegW, id_tNUptVegS
      type (type_horizontal_diagnostic_variable_id)                   :: id_tNUptNH4VegW, id_tNExcrVegW, id_wNBedPOMW, id_wNBedDOMW, id_tO2ProdVegW, id_tO2RespVegW, id_tO2UptNO3VegW, id_tNExcrVeg
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDBedDOMS, id_tNUptNO3VegW, id_tNMortVegNH4W, id_tO2ProdVegS, id_aMuVeg, id_tDEnvProdVeg, id_tPMigrVeg
      type (type_horizontal_diagnostic_variable_id)                   :: id_tCProdVeg, id_tCMortVeg, id_tCRespVeg, id_tCMigrVeg, id_tCO2RespVegW,id_wCBedPOMW, id_wCBedDOMW, id_tCBedPOMS, id_tCBedDOMS
      type (type_horizontal_diagnostic_variable_id)                   :: id_tPUptVegW, id_tPExcrVegW, id_tPMortVegPO4W, id_wPBedPOMW, id_wPBedDOMW, id_tPUptVegS, id_tPExcrVegS, id_tPMortVegPO4S
      type (type_horizontal_diagnostic_variable_id)                   :: id_tNUptNH4VegS, id_tNExcrVegS, id_tNMortVegNH4S, id_tNUptNO3VegS, id_tNBedPOMS, id_tNBedDOMS, id_tPBedPOMS, id_tPBedDOMS
      ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                                   :: id_NH4poolW,id_NO3poolW,id_PO4poolW,id_O2poolW !, id_CO2poolW
      type (type_state_variable_id)                                   :: id_DPOMpoolW,id_NPOMpoolW,id_PPOMpoolW, id_CPOMpoolW
      type (type_bottom_state_variable_id)                            :: id_NH4poolS,id_NO3poolS,id_PO4poolS
      type (type_bottom_state_variable_id)                            :: id_DPOMpoolS,id_NPOMpoolS,id_PPOMpoolS, id_CPOMpoolS
      type (type_state_variable_id)                                   :: id_DPOMpoolS_PV,id_NPOMpoolS_PV,id_PPOMpoolS_PV, id_CPOMpoolS_PV, id_DDOMpoolW,id_NDOMpoolW,id_PDOMpoolW, id_CDOMpoolW
      type (type_bottom_state_variable_id)                            :: id_DDOMpoolS,id_NDOMpoolS,id_PDOMpoolS, id_CDOMpoolS
      type (type_state_variable_id)                                   :: id_DDOMpoolS_PV,id_NDOMpoolS_PV,id_PDOMpoolS_PV, id_CDOMpoolS_PV
      type (type_bottom_state_variable_id), allocatable, dimension(:) :: id_Compts
      type (type_model_id), allocatable, dimension(:)                 :: id_Compt_Models
      ! environmental dependencies identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_global_dependency_id)                                :: id_Day
      type (type_dependency_id)                                       :: id_uTm,id_extc,id_dz
      type (type_dependency_id)                                       :: id_par,id_meanpar
      type (type_horizontal_dependency_id)                            :: id_sDepthW,id_lat,id_lon,id_bPorS, id_cDepthS, id_bot_pel_conv
      ! diagnostic dependencies identifiers----------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_dependency_id)                            :: id_afOxySed
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      real(rk)    :: cDVegIn, kMigrVeg, cMuMaxVeg, cDCarrVeg, kDRespVeg, hLRefVeg, cNDVegMin, cNDVegMax, cPDVegMin, cPDVegMax, cDayWinVeg, cDaySumVegMin, cLengAllo, fRootVegWin, fRootVegSum
      real(rk)    :: fFloatVeg, cDLayerVeg, cCovSpVeg, kMortVegSum, cLengMort, fWinVeg, cQ10ProdVeg, cQ10RespVeg, cPDVeg0, cNDVeg0, fSedUptVegMax, fSedUptVegCoef, fSedUptVegExp, cAffNUptVeg
      real(rk)    :: cVNUptMaxVeg, cVPUptMaxVeg, cAffPUptVeg, fDissMortVeg, cDepthS, bPorS, cCPerDW, hO2BOD, cExtSpVeg, fTOMWMortVeg, cHeightVeg, cDVegMin, cNVegMin, cPVegMin, fVegDOMW, fVegDOMS
      real(rk)    :: aDSubVeg, cTmInitVeg, fEmergVeg, cSigTmVeg, cTmOptVeg
      integer     :: nCompts
      logical     :: lEmpUpt, diagnostics, lCarrVeg, lGausVeg
      
   contains

   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure :: initialize
   procedure :: do_bottom
   procedure :: do
   procedure :: get_light_extinction
   procedure :: calc_veg_fractions
   end type type_wet_macrophytes

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk),parameter :: Pi=3.14159265358979_rk
   real(rk),parameter :: molO2molC = 2.6667_rk
   real(rk),parameter :: O2PerNO3 = 1.5_rk
   real(rk),parameter :: molO2molN = 2.2857_rk

integer, save :: debug_bottom_seq=0

contains

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_macrophytes), intent(inout), target :: self
   integer,                          intent(in)        :: configunit
   
   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer  :: i_mac
   character(len=64)   :: index
   
   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! population-level parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%nCompts,       'nCompts',       '-',               'number of macrophyte competitors',                           default=0                                            )
   call self%get_parameter(self%cDVegIn,       'cDVegIn',       'gDW/m2',          'external macrophyte density',                                default=1.0_rk                                       )
   call self%get_parameter(self%kMigrVeg,      'kMigrVeg',      '1/d',             'macrophytes immigration rate',                               default=0.001_rk,   scale_factor=1.0_rk/secs_pr_day  )
   call self%get_parameter(self%cDCarrVeg,     'cDCarrVeg',     'gDW/m2',          'carrying capacity',                                          default=300.0_rk                                     )
   call self%get_parameter(self%cDVegMin,      'cDVegMin',      'gDW/m2',          'minimum dry weight',                                         default=0.00001_rk                                   )
   ! photosynthesis parameters-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%hLRefVeg,      'hLRefVeg',      'W/m2',            'half-saturation PAR of macrophyte growth at 20*C',           default=17.0_rk                                      )
   ! nutrient uptake parameters------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%lEmpUpt,       'lEmpUpt',       '-',               'toggle empirical relat. for sed. fract. of nut. upt.',       default=.false.                                      )
   call self%get_parameter(self%fSedUptVegMax, 'fSedUptVegMax', '-',               'lEmpUpt = .true.; max. sediment nutrient fraction',          default=0.5_rk                                       )
   call self%get_parameter(self%fSedUptVegCoef,'fSedUptVegCoef','-',               'lEmpUpt = .true.; sediment nutrient fraction sigma',         default=2.66_rk                                      )
   call self%get_parameter(self%fSedUptVegExp, 'fSedUptVegExp', '-',               'lEmpUpt = .true.; sediment nutrient fraction exp.',          default=-0.83_rk                                     )
   call self%get_parameter(self%cAffNUptVeg,   'cAffNUptVeg',   'l/mgDW/d',        'N uptake affinity',                                          default=0.2_rk,     scale_factor=1.0_rk/secs_pr_day  )
   call self%get_parameter(self%cVNUptMaxVeg,  'cVNUptMaxVeg',  'mgN/mgDW/d',      'N uptake capacity at 20*C',                                  default=0.1_rk,     scale_factor=1.0_rk/secs_pr_day  )
   call self%get_parameter(self%cAffPUptVeg,   'cAffPUptVeg',   'l/mgDW/d',        'P uptake affinity',                                          default=0.2_rk,     scale_factor=1.0_rk/secs_pr_day  )
   call self%get_parameter(self%cVPUptMaxVeg,  'cVPUptMaxVeg',  'mgP/mgDW/d',      'P uptake capacity at 20*C',                                  default=0.01_rk,    scale_factor=1.0_rk/secs_pr_day  )
   ! vital rate parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cMuMaxVeg,     'cMuMaxVeg',     '1/d',             'maximum growth rate at 20*C',                                default=0.08_rk,    scale_factor=1.0_rk/secs_pr_day  )
   call self%get_parameter(self%kDRespVeg,     'kDRespVeg',     '1/d',             'dark respiration rate at 20*C',                              default=0.02_rk,    scale_factor=1.0_rk/secs_pr_day  )
   call self%get_parameter(self%cDayWinVeg,    'cDayWinVeg',    'day of the year', 'end of growing season date',                                 default=259.0_rk                                     )
   call self%get_parameter(self%cDaySumVegMin, 'cDaySumVegMin', 'day of the year', 'earliest start of growing season date',                      default=1.0_rk                                       )
   call self%get_parameter(self%cLengAllo,     'cLengAllo',     'd',               'duration of allocation and reallocation phase',              default=15.0_rk                                      )
   call self%get_parameter(self%fRootVegWin,   'fRootVegWin',   'groot/gveg',      'root fraction outside of growing season',                    default=0.6_rk                                       )
   call self%get_parameter(self%fRootVegSum,   'fRootVegSum',   'groot/gveg',      'root fraction during growing season',                        default=0.1_rk                                       )
   call self%get_parameter(self%fEmergVeg,     'fEmergVeg',     'gfloating/gshoot','emergent fraction of shoot',                                 default=0.0_rk                                       )
   call self%get_parameter(self%fFloatVeg,     'fFloatVeg',     'gfloating/gshoot','floating fraction of shoot',                                 default=0.0_rk                                       )
   call self%get_parameter(self%cDLayerVeg,    'cDLayerVeg',    'gD/m2',           'biomass of a single layer of floating leaves',               default=0.0_rk                                       )
   call self%get_parameter(self%cCovSpVeg,     'cCovSpVeg',     'l/gDW/m2',        'specific cover',                                             default=0.5_rk                                       )
   call self%get_parameter(self%kMortVegSum,   'kMortVegSum',   '1/d',             'mortality rate during growing season',                       default=0.005_rk,   scale_factor=1.0_rk/secs_pr_day  )
   call self%get_parameter(self%cLengMort,     'cLengMort',     'd',               'length of shoot mortality period',                           default=15.0_rk                                      )
   call self%get_parameter(self%fWinVeg,       'fWinVeg',       '-',               'fraction surviving outside of growing season',               default=0.3_rk                                       )
   call self%get_parameter(self%hO2BOD,        'hO2BOD',        'mgO2/l',          'half-saturation constant for oxygen conc. on BOD',           default=1.0_rk                                       )
   call self%get_parameter(self%cHeightVeg,    'cHeightVeg',    'm',               'macrophyte height',                                          default=0.5_rk                                       )
   call self%get_parameter(self%cExtSpVeg,     'cExtSpVeg',     'm2/gDW',          'specific extinction',                                        default=0.0035_rk                                    )
   ! temperature parameters----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cTmInitVeg,    'cTmInitVeg',    '*C',              'temperature for onset of initial growth',                    default=9.0_rk                                       )
   call self%get_parameter(self%cQ10ProdVeg,   'cQ10ProdVeg',   '-',               'temperature q10 of growth',                                  default=1.2_rk                                       )
   call self%get_parameter(self%cQ10RespVeg,   'cQ10RespVeg',   '-',               'temperature q10 of respiration',                             default=2.0_rk                                       )
   call self%get_parameter(self%cSigTmVeg,     'cSigTmVeg',     '*C',              'lGausVeg = .true.; temp. const.; sigma in Gaussian curve',   default=20.0_rk                                      )
   call self%get_parameter(self%cTmOptVeg,     'cTmOptVeg',     '*C',              'lGausVeg = .true.; optimum temperature',                     default=20.0_rk                                      )
   ! stochiometric parameters--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cNDVegMin,     'cNDVegMin',     'mgN/mgDW',        'minimum N/DW ratio',                                         default=0.01_rk                                      )
   call self%get_parameter(self%cNDVegMax,     'cNDVegMax',     'mgN/mgDW',        'maximum N/DW ratio',                                         default=0.035_rk                                     )
   call self%get_parameter(self%cPDVegMin,     'cPDVegMin',     'mgP/mg',          'minimum P/DW ratio',                                         default=0.001_rk                                     )
   call self%get_parameter(self%cPDVegMax,     'cPDVegMax',     'mgP/mgDW',        'maximum P/DW ratio',                                         default=0.004_rk                                     )
   call self%get_parameter(self%fDissMortVeg,  'fDissMortVeg',  '-',               'dissolved inorganic nutrient fraction of dead plants',       default=0.25_rk                                      )
   call self%get_parameter(self%cCPerDW,       'cCPerDW',       'gC/gDW',          'C content of organic matter DW',                             default=0.4_rk                                       )
   call self%get_parameter(self%fTOMWMortVeg,  'fTOMWMortVeg',  '-',               'organic matter fraction of dead shoots to sediment',         default=0.1_rk                                       )
   call self%get_parameter(self%fVegDOMS,      'fVegDOMS',      '-',               'dissolved organic matter fraction of dead roots',            default=0.0_rk                                       )
   call self%get_parameter(self%fVegDOMW,      'fVegDOMW',      '-',               'dissolved organic matter fraction of dead shoots',           default=0.0_rk                                       )
   call self%get_parameter(self%cPDVeg0,       'cPDVeg0',       'gP/gDW',          'reference P fraction in external veg',                       default=0.002_rk                                     )
   call self%get_parameter(self%cNDVeg0,       'cNDVeg0',       'gN/gDW',          'reference N fraction in external veg',                       default=0.02_rk                                      )
   call self%get_parameter(self%lCarrVeg,      'lCarrVeg',      '-',               'toggle carrying capacity',                                   default=.true.                                       )
   call self%get_parameter(self%lGausVeg,      'lGausVeg',      '-',               'toggle gaussian temperature modifier',                       default=.false.                                      )
   ! diagnostic  parameter-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,   'diagnostics',   '-',               'toggle diagnostic output',                                   default=.false.                                      )

   !REGISTER MODEL VARIBLES, DEPENDENCIES & COUPLINGS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! local state variables---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sDVeg,   'sD',   'gDW/m2','DW',         initial_value=1.0_rk,     minimum=0.0_rk   )
   call self%register_state_variable(self%id_sNVeg,   'sN',   'gN/m2', 'N',          initial_value=0.02_rk,    minimum=0.0_rk   )
   call self%register_state_variable(self%id_sPVeg,   'sP',   'gP/m2', 'P',          initial_value=0.002_rk,   minimum=0.0_rk   )
   call self%register_state_variable(self%id_sCVeg,   'sC',   'gC/m2', 'P',          initial_value=0.4_rk,     minimum=0.0_rk   )
   
   call self%register_state_variable(self%id_sDVeg_PV,'sD_PV','gDW/m2','DW pel. var',initial_value=1.0_rk,     minimum=0.0_rk,    no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)                                                                       
   call self%register_state_variable(self%id_sPVeg_PV,'sP_PV','gP/m2', 'P pel. var', initial_value=0.02_rk,    minimum=0.0_rk,    no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)                                                                       
   call self%register_state_variable(self%id_sNVeg_PV,'sN_PV','gN/m2', 'N pel. var', initial_value=0.002_rk,   minimum=0.0_rk,    no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)
   call self%register_state_variable(self%id_sCVeg_PV,'sC_PV','gC/m2', 'C pel. var', initial_value=0.4_rk,     minimum=0.0_rk,    no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)
   call self%set_variable_property(self%id_sDVeg_PV,'disable_transport',.true.)
   call self%set_variable_property(self%id_sPVeg_PV,'disable_transport',.true.)
   call self%set_variable_property(self%id_sNVeg_PV,'disable_transport',.true.)
   call self%set_variable_property(self%id_sCVeg_PV,'disable_transport',.true.)
   
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')  
   ! register diagnostic variables-------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_bfRootVeg_PV,     'bfRootVeg_PV',   'gDW/m2','bfRootVeg',                         output=output_instantaneous,missing_value=0.0_rk,source=source_do)
                                                                                      
   call self%register_diagnostic_variable(self%id_aDSubVeg_PV,      'aDSubVeg_PV',    'gDW/m2','aDSubVeg_PV',                       output=output_instantaneous,missing_value=0.0_rk,source=source_do)
                                                                                      
   call self%register_diagnostic_variable(self%id_aCovVeg_PV,       'aCovVeg_PV',     '%',     'aCovVeg_PV',                        output=output_instantaneous,missing_value=0.0_rk,source=source_do)
   call self%register_diagnostic_variable(self%id_afCovSurfVeg_PV,  'afCovSurfVeg_PV','-',     'afCovSurfVeg',                      output=output_none,         missing_value=0.0_rk,source=source_do)                                                                                                                                                                                                                         
   call self%register_diagnostic_variable(self%id_aDSubVeg,         'aDSubVeg',       'gDW/m2','aDSubVeg',                          output=output_instantaneous,missing_value=0.0_rk,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_aCovVeg,          'aCovVeg',        '%',     'aCovVeg',                           output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_afCovSurfVeg,     'afCovSurfVeg',   '-',     'afCovSurfVeg',                      output=output_none,         domain=domain_bottom,source=source_do_bottom)                              
   call self%register_diagnostic_variable(self%id_aNutLimVeg,       'aNutLimVeg',     '-',     'nutrient limitation factor',        output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_macroextinction,  'macroextinction','-',     'macroextinction',                   output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_aLLimVeg,         'aLLimVeg',       '-',     'light limitation factor',           output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_aLPAR1Veg,        'aLPAR1Veg',      'W/m2',  'light at top of the macrophytes',   output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_aLPAR2Veg,        'aLPAR2Veg',      'W/m2',  'light at bottom of the macrophytes',output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tDBedPOMS,        'tDBedPOMS',      'g/m2/s','tDBedPOMS',                         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)   ! what is happening here?
   call self%register_diagnostic_variable(self%id_tDBedVeg,         'tDBedVeg',       'g/m2/s','DVeg exchange',                     output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tNBedVeg,         'tNBedVeg',       'g/m2/s','NVeg exchange',                     output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tPBedVeg,         'tPBedVeg',       'g/m2/s','PVeg exchange',                     output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tCBedVeg,         'tCBedVeg',       'g/m2/s','CVeg exchange',                     output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tO2BedW,          'tO2BedW',        'g/m2/s','tO2BedW exchange',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   ! Register diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%diagnostics) then
       call self%register_diagnostic_variable(self%id_ufDay,        'ufDay',          'd',     'day length',                        output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_aMuVeg,       'aMuVeg',         '1/s',   'rate DW actual growth',             output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDEnvProdVeg, 'tDEnvProdVeg',   'g/m2/s','logistic correction of production', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDMigrVeg,    'tDMigrVeg',      'g/m2/s','rate DW migration',                 output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDProdVeg,    'tDProdVeg',      'g/m2/s','rate DW production',                output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDMortVeg,    'tDMortVeg',      'g/m2/s','rate DW mortality',                 output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_wDBedPOMW,    'wDBedPOMW',      'g/m2/s','rate DPOMW from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_wDBedDOMW,    'wDBedDOMW',      'g/m2/s','rate DDOMW from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)     
       call self%register_diagnostic_variable(self%id_tDRespVeg,    'tDRespVeg',      'g/m2/s','rate DW respiration',               output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNMigrVeg,    'tNMigrVeg',      'g/m2/s','rate N migration',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNUptVegW,    'tNUptVegW',      'g/m2/s','rate N uptake from water',          output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNExcrVeg,    'tNExcrVeg',      'g/m2/s','rate N excretion',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNUptNH4VegW, 'tNUptNH4VegW',   'g/m2/s','rate NH4W uptake',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNExcrVegW,   'tNExcrVegW',     'g/m2/s','rate NH4W excreted',                output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNMortVegNH4W,'tNMortVegNH4W',  'g/m2/s','rate NH4W from mortality',          output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNUptNO3VegW, 'tNUptNO3VegW',   'g/m2/s','rate NO3W uptake',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_wNBedPOMW,    'wNBedPOMW',      'g/m2/s','rate NPOMW from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_wNBedDOMW,    'wNBedDOMW',      'g/m2/s','rate NDOMW from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPMigrVeg,    'tPMigrVeg',      'g/m2/s','rate P migration',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPUptVegW,    'tPUptVegW',      'g/m2/s','rate PO4W uptake from water',       output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPExcrVegW,   'tPExcrVegW',     'g/m2/s','rate PO4W excreted',                output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPMortVegPO4W,'tPMortVegPO4W',  'g/m2/s','rate PO4W from mortality',          output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_wPBedPOMW,    'wPBedPOMW',      'g/m2/s','rate PPOMW from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_wPBedDOMW,    'wPBedDOMW',      'g/m2/s','rate PDOMW from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tO2ProdVegW,  'tO2ProdVegW',    'g/m2/s','rate O2W production',               output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tO2RespVegW,  'tO2RespVegW',    'g/m2/s','rate O2W respiration',              output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tO2UptNO3VegW,'tO2UptNO3VegW',  'g/m2/s','rate O2W release due to NO3 uptake',output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCMigrVeg,    'tCMigrVeg',      'g/m2/s','rate C migration',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCProdVeg,    'tCProdVeg',      'g/m2/s','rate C production',                 output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCMortVeg,    'tCMortVeg',      'g/m2/s','rate C mortality',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_wCBedPOMW,    'wCBedPOMW',      'g/m2/s','rate CPOMW from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_wCBedDOMW,    'wCBedDOMW',      'g/m2/s','rate CDOMW from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)     
       call self%register_diagnostic_variable(self%id_tCRespVeg,    'tCRespVeg',      'g/m2/s','rate C respiration',                output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       ! sediment diagnostics 
       call self%register_diagnostic_variable(self%id_tDBedDOMS,    'tDBedDOMS',      'g/m2/s','rate DDOMS from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNUptNH4VegS, 'tNUptNH4VegS',   'g/m2/s','rate NH4S uptake',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNUptVegS,    'tNUptVegS',      'g/m2/s','rate N uptake from sediment',       output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNExcrVegS,   'tNExcrVegS',     'g/m2/s','rate NH4S excreted',                output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNMortVegNH4S,'tNMortVegNH4S',  'g/m2/s','rate NH4S from mortality',          output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNUptNO3VegS, 'tNUptNO3VegS',   'g/m2/s','rate NO3S uptake',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNBedPOMS,    'tNBedPOMS',      'g/m2/s','rate NPOMS from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNBedDOMS,    'tNBedDOMS',      'g/m2/s','rate NDOMS from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPUptVegS,    'tPUptVegS',      'g/m2/s','rate PO4S uptake from sediment',    output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPExcrVegS,   'tPExcrVegS',     'g/m2/s','rate PO4S excreted',                output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPMortVegPO4S,'tPMortVegPO4S',  'g/m2/s','rate PO4S from mortality',          output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPBedPOMS,    'tPBedPOMS',      'g/m2/s','rate PPOMS from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPBedDOMS,    'tPBedDOMS',      'g/m2/s','rate PDOMS from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tO2ProdVegS,  'tO2ProdVegS',    'g/m2/s','rate O2S production',               output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCBedPOMS,    'tCBedPOMS',      'g/m2/s','rate CPOMS from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCBedDOMS,    'tCBedDOMS',      'g/m2/s','rate CDOMS from mortality',         output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
   endif    
   ! Register contribution of state to global aggregate variables------------------------------------------------------------------------------------------------------------------------------------
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_macrophyte_biomass',units='gDW/m2',aggregate_variable=.true.),self%id_sDVeg_PV,scale_factor=1._rk)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_tDPOMbio',units='gDW/m2/s',aggregate_variable=.true.),self%id_tDBedPOMS,scale_factor=1._rk)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_aDSubVeg',units='gDW/m2',aggregate_variable=.true.),self%id_aDSubVeg_PV,scale_factor=1._rk)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_aCovVeg',units='%',aggregate_variable=.true.),self%id_aCovVeg_PV,scale_factor=1._rk)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_afCovSurfVeg',units='-',aggregate_variable=.true.),self%id_afCovSurfVeg_PV,scale_factor=1._rk)
   ! register state variable dependencies------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_dependency(self%id_NH4poolW,     'NH4_pool_water',             'g/m3',    'NH4 pool for nutrient uptake'          )
   call self%register_state_dependency(self%id_NO3poolW,     'NO3_pool_water',             'g/m3',    'NO3 pool for nutrient uptake'          )
   call self%register_state_dependency(self%id_PO4poolW,     'PO4_pool_water',             'g/m3',    'PO4 pool for nutrient uptake'          )
   call self%register_state_dependency(self%id_O2poolW,      'oxygen_pool_water',          'g/m3',    'oxygen pool in water'                  )
   !call self%register_state_dependency(self%id_CO2poolW,     'CO2_pool_water',             'g/m3',    'CO2 pool in water'                     )
   call self%register_state_dependency(self%id_DPOMpoolW,    'POM_DW_pool_water',          'g/m3',    'POM DW pool in water'                  )
   call self%register_state_dependency(self%id_NPOMpoolW,    'POM_N_pool_water',           'g/m3',    'POM N pool in water'                   )
   call self%register_state_dependency(self%id_PPOMpoolW,    'POM_P_pool_water',           'g/m3',    'POM P pool in water'                   )
   call self%register_state_dependency(self%id_CPOMpoolW,    'POM_C_pool_water',           'g/m3',    'POM C pool in water'                   )
   call self%register_state_dependency(self%id_NH4poolS,     'NH4_pool_sediment',          'g/m2',    'NH4 pool for nutrient uptake'          )
   call self%register_state_dependency(self%id_NO3poolS,     'NO3_pool_sediment',          'g/m2',    'NO3 pool for nutrient uptake'          )
   call self%register_state_dependency(self%id_PO4poolS,     'PO4_pool_sediment',          'g/m2',    'PO4 pool for nutrient uptake'          )
   call self%register_state_dependency(self%id_DPOMpoolS,    'POM_DW_pool_sediment',       'g/m2',    'POM DW pool sediment'                  )
   call self%register_state_dependency(self%id_NPOMpoolS,    'POM_N_pool_sediment',        'g/m2',    'POM N pool sediment'                   )
   call self%register_state_dependency(self%id_PPOMpoolS,    'POM_P_pool_sediment',        'g/m2',    'POM P pool sediment'                   )
   call self%register_state_dependency(self%id_CPOMpoolS,    'POM_C_pool_sediment',        'g/m2',    'POM C pool sediment'                   )
   call self%register_state_dependency(self%id_DPOMpoolS_PV, 'POM_DW_pool_sediment_PV',    'g/m2',    'POM DW pool sediment pelagic mirror'   )
   call self%register_state_dependency(self%id_NPOMpoolS_PV, 'POM_N_pool_sediment_PV',     'g/m2',    'POM N pool sediment pelagic mirror'    )
   call self%register_state_dependency(self%id_PPOMpoolS_PV, 'POM_P_pool_sediment_PV',     'g/m2',    'POM P pool sediment pelagic mirror'    )
   call self%register_state_dependency(self%id_CPOMpoolS_PV, 'POM_C_pool_sediment_PV',     'g/m2',    'POM C pool sediment pelagic mirror'    )

   call self%register_state_dependency(self%id_DDOMpoolW,    'DOM_DW_pool_water',          'g/m3',    'DOM DW in water'                       )
   call self%register_state_dependency(self%id_NDOMpoolW,    'DOM_N_pool_water',           'g/m3',    'DOM N in water'                        )
   call self%register_state_dependency(self%id_PDOMpoolW,    'DOM_P_pool_water',           'g/m3',    'DOM P in water'                        )
   call self%register_state_dependency(self%id_CDOMpoolW,    'DOM_C_pool_water',           'g/m3',    'DOM C in water'                        )
   call self%register_state_dependency(self%id_DDOMpoolS,    'DOM_DW_pool_sediment',       'g/m2',    'DOM DW in sediment'                    )
   call self%register_state_dependency(self%id_NDOMpoolS,    'DOM_N_pool_sediment',        'g/m2',    'DOM N in sediment'                     )
   call self%register_state_dependency(self%id_PDOMpoolS,    'DOM_P_pool_sediment',        'g/m2',    'DOM P in sediment'                     )
   call self%register_state_dependency(self%id_CDOMpoolS,    'DOM_C_pool_sediment',        'g/m2',    'DOM C in sediment'                     )
   call self%register_state_dependency(self%id_DDOMpoolS_PV, 'DOM_DW_pool_sediment_PV',    'g/m2',    'DOM DW in sediment pelagic mirror'     )
   call self%register_state_dependency(self%id_NDOMpoolS_PV, 'DOM_N_pool_sediment_PV',     'g/m2',    'DOM N in sediment pelagic mirror'      )
   call self%register_state_dependency(self%id_PDOMpoolS_PV, 'DOM_P_pool_sediment_PV',     'g/m2',    'DOM P in sediment pelagic mirror'      )
   call self%register_state_dependency(self%id_CDOMpoolS_PV, 'DOM_C_pool_sediment_PV',     'g/m2',    'DOM C in sediment pelagic mirror'      )
   
   allocate(self%id_Compts(self%nCompts))
   allocate(self%id_Compt_Models(self%nCompts))
   do i_mac=1,self%nCompts
      write(index,'(i0)') i_mac
      call self%register_state_dependency(self%id_Compts(i_mac),  'DW_macrophyte'//trim(index),'gDW/m2',       'DW of macrophyte'//trim(index))
      call self%register_model_dependency(self%id_Compt_Models(i_mac), 'macrophyte_competitor'//trim(index))
      call self%request_coupling_to_model(self%id_Compts(i_mac),self%id_Compt_Models(i_mac),'sD')
   end do

   ! register diagnostic dependencies----------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(           self%id_afOxySed,        'oxic_layer_fraction', '-',                     'oxic layer fraction'                                                          )
   call self%register_diagnostic_variable(  self%id_aDayInitVeg_out, 'aDayInitVeg',         'd',                     'aDayInitVeg', output=output_instantaneous, missing_value=-1.0_rk, source=source_do)
   call self%register_dependency(           self%id_aDayInitVeg,     'aDayInitVeg',         'd',                     'aDayInitVeg'                                                                  )
   call self%register_horizontal_dependency(self%id_bPorS,           'bPorS',               'm3/m3',                 'sediment porosity'                                                            )
   call self%register_horizontal_dependency(self%id_cDepthS,         'cDepthS',             'm',                     'sediment depth'                                                               )
   ! register environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_uTm,    standard_variables%temperature)
   call self%register_dependency(self%id_extc,   standard_variables%attenuation_coefficient_of_photosynthetic_radiative_flux)
   call self%register_dependency(self%id_Day,    standard_variables%number_of_days_since_start_of_the_year)
   call self%register_dependency(self%id_sDepthW,standard_variables%bottom_depth)
   call self%register_horizontal_dependency(self%id_lon,standard_variables%longitude)
   call self%register_dependency(self%id_lat,    standard_variables%latitude)
   call self%register_dependency(self%id_dz,     standard_variables%cell_thickness)
   call self%register_dependency(self%id_par,    standard_variables%downwelling_photosynthetic_radiative_flux)
   call self%register_dependency(self%id_meanpar,temporal_mean(self%id_par,period=86400._rk,resolution=3600._rk,missing_value=0.0_rk))

   return

end subroutine initialize

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO BOTTOM                                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_macrophytes), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)   :: uTm, extc, meanpar, par, dz, Day, sDepthW, lat, lon, sDVeg, sNVeg, sPVeg, sDCompts, sNH4W, sNO3W, sPO4W, sNH4S, sNO3S, sPO4S, sO2W, CorO2BOD, bot_pel_conv !, Af_below, Af_last, Vc, Af
   real(rk)   :: oNH4S, oNO3S, oNDissS, oNDissW, oPO4S, afOxySed, bfRootVeg, bfShootVeg, aDRootVeg, aDShootVeg, aDEmergVeg, aDFloatVeg, bfSubVeg, aDSubVeg, bkMortVeg, aDayInitVeg, afCovEmergVeg
   real(rk)   :: uFunTmProdVeg, uFunTmRespVeg, aCovVeg, afCovSurfVeg, aLLimShootVeg, uhLVeg, aMuTmLVeg, ufDay, par_bott, aLPAR1Veg, aLPAR2Veg, rPDVeg, rNDVeg, tDBedVeg, tDMigrVeg, tDProdVeg
   real(rk)   :: aMuVeg, aNutLimVeg, aPLimVeg, aNLimVeg, tDRespVeg, tDEnvProdVeg, akDIncrVeg, tDEnvVeg, tDMortVeg, tDEnvMortVeg, tNBedVeg, tNMigrVeg, tNUptVeg, tNUptVegW, tNUptVegS, afNUptVegS
   real(rk)   :: aVNUptMaxCrVeg, ahNUptVeg, aVNUptVegW, aVNUptVegS, tNExcrVeg, tNMortVeg, tPBedVeg, tPMigrVeg, tPUptVeg, tPUptVegW, tPUptVegS, aVPUptMaxCrVeg, ahPUptVeg, aVPUptVegW, aVPUptVegS
   real(rk)   :: tPExcrVeg, tPMortVeg, afPUptVegS, wNBedNH4W, tNUptNH4VegW, afNH4UptVegW, tNMortVegNH4W, tNMortVegNH4, wNBedNO3W, tNUptNO3VegW, tNExcrVegS, tNExcrVegW, tNBedNH4S, tNUptNH4VegS
   real(rk)   :: tNMortVegNH4S, tNBedNO3S, afNH4UptVegS, tNUptNO3VegS, wPBedPO4W, tPExcrVegS, tPExcrVegW, tPBedPO4S, tPMortVegPO4W, tPMortVegPO4, tPMortVegPO4S, tO2BedW, tO2ProdVegW, tO2ProdVeg
   real(rk)   :: tO2RespVegS, tO2RespVegW, tO2UptNO3VegW, tO2ProdVegS, wDBedTOMW, tDMortVegW, wNBedTOMW, tNMortVegTOMW, tNMortVegTOM, wPBedTOMW, tPMortVegTOMW, tPMortVegTOM, tDBedPOMS, tDMortVegS
   real(rk)   :: tNBedPOMS, tNMortVegTOMS, tPBedPOMS, tPMortVegTOMS, tDBedDOMS, tNBedDOMS, tPBedDOMS, wDBedDOMW, wNBedDOMW, wPBedDOMW, wDBedPOMW, wNBedPOMW, wPBedPOMW, aCorO2BOD, bPorS, cDepthS
   real(rk)   :: sCVeg, rCDVeg, tCMortVeg, tCMigrVeg, tCO2BedW, tCMortVegW, wCBedTOMW, wCBedPOMW, wCBedDOMW, tCMortVegS, tCBedPOMS, tCBedDOMS, tCProdVeg, tCRespVeg, tCBedVeg
   ! TODO: sCO2W, 
   real(rk), dimension(self%nCompts)   :: sDCompts_all
   integer    :: i
   
   _HORIZONTAL_LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
        ! 1.1 retrieve environmental dependencies                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        _GET_(self%id_uTm,uTm)                                                                                      !
        _GET_(self%id_dz,dz)                                                                                      !
        _GET_(self%id_meanpar,meanpar)
        _GET_(self%id_par,par)                                                                              !
       ! meanpar=max(0.0_rk,meanpar)     ! <==========================================================================================================<<<<<<<<<<<
        _GET_GLOBAL_(self%id_Day,Day)                                                                               !
        _GET_(self%id_extc,extc)                                                                                    !
        _GET_HORIZONTAL_(self%id_sDepthW,sDepthW)                                                                   !
        _GET_HORIZONTAL_(self%id_lat,lat)
        _GET_HORIZONTAL_(self%id_lon,lon)
        debug_bottom_seq=debug_bottom_seq+1
        write(0,'(A,I0,1X,7(ES24.16,1X))') 'DBG_MACRO_BOTTOM ',debug_bottom_seq,meanpar,par,extc,dz,sDepthW,lat,lon
        flush(0)
        flush(0)                                                                           !
        do i = 1,self%nCompts                                                                                       ! for each competitor
           _GET_HORIZONTAL_(self%id_Compts(i),sDCompts_all(i))                                                      !
        end do                                                                                                      !
        sDCompts = sum(sDCompts_all)                                                                                !
        _GET_HORIZONTAL_(self%id_bPorS,bPorS)                                                                       !
        _GET_HORIZONTAL_(self%id_cDepthS,cDepthS)                                                                   !
        !===========================================================================================================!
        ! 1.2 retrieve state variables, & calc. current local nutrient ratios and derived quantities                !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.1 macrophyte state variables                                                                       !
           !--------------------------------------------------------------------------------------------------------!
           _GET_HORIZONTAL_(self%id_sDVeg,sDVeg)                                                                    !
           _GET_HORIZONTAL_(self%id_sNVeg,sNVeg)                                                                    !
           _GET_HORIZONTAL_(self%id_sPVeg,sPVeg)                                                                    !
           _GET_HORIZONTAL_(self%id_sCVeg,sCVeg)                                                                    !
           rPDVeg = sPVeg/(sDVeg+NearZero)                                                                          !
           rNDVeg = sNVeg /(sDVeg+NearZero)                                                                         !
           rCDVeg = sCVeg /(sDVeg+NearZero)                                                                         !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.2 nutrient variables                                                                               !
           !--------------------------------------------------------------------------------------------------------!
           _GET_(self%id_NH4poolW,sNH4W)                                                                            !
           _GET_(self%id_NO3poolW,sNO3W)                                                                            !
           _GET_(self%id_PO4poolW,sPO4W)                                                                            !
           _GET_(self%id_O2poolW,sO2W)                                                                              !
           ! _GET_(self%id_CO2poolW,sCO2W)                                                                              !
           _GET_HORIZONTAL_(self%id_NH4poolS,sNH4S)                                                                 !
           _GET_HORIZONTAL_(self%id_NO3poolS,sNO3S)                                                                 !
           _GET_HORIZONTAL_(self%id_PO4poolS,sPO4S)                                                                 !
           oNDissW = sNO3W + sNH4W                                                                                  !
           oNDissS = (sNO3S + sNH4S)/cDepthS / bPorS                                                                !
           oNH4S=sNH4S/cDepthS / bPorS                                                                              !
           oNO3S=sNO3S/cDepthS / bPorS                                                                              !
           oPO4S=sPO4S/cDepthS / bPorS                                                                              !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.3 diagnostic dependencies                                                                          !
           !--------------------------------------------------------------------------------------------------------!
           _GET_(self%id_aDayInitVeg,aDayInitVeg)                                                                   !
           _GET_HORIZONTAL_(self%id_afOxySed,afOxySed)                                                              !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!                                     
   !  2. calculate temperature, biomass fractions, light and nutrient functions                                     !                                         
   !================================================================================================================!                                                    
        ! 2.1 temperature functions                                                                                 !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        if (self%lGausVeg) then                                                                                     !
            uFunTmProdVeg = uFunTmGaus(uTm,self%cSigTmVeg,self%cTmOptVeg)                                           !
            uFunTmRespVeg = uFunTmProdVeg                                                                           !
        else                                                                                                        !
            uFunTmProdVeg = uFunTmQ10(uTm,self%cQ10ProdVeg)                                                         !
            uFunTmRespVeg = uFunTmQ10(uTm,self%cQ10RespVeg)                                                         !
        endif                                                                                                       !
        !===========================================================================================================!
        ! 2.2 calculate fractions of biomass in shoots, roots etc. (function at file end, shared with do routine)   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        call self%calc_veg_fractions(Day,sDVeg,uTm,lat,aDSubVeg,aCovVeg,afCovSurfVeg,aDayInitVeg,aDShootVeg,aDRootVeg,aDEmergVeg, &  !
            aDFloatVeg,bfShootVeg,bfRootVeg,bfSubVeg)                                                               !
        !===========================================================================================================!
        ! 2.3 calculate surface cover variables                                                                     !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        afCovEmergVeg = min(1.0_rk, 0.01_rk * self%cCovSpVeg * aDEmergVeg)                                          ! fraction_emergent_coverage
        !===========================================================================================================!
        ! 2.4 Light functions                                                                                       !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        uhLVeg = self%hLRefVeg * uFunTmProdVeg                                                                      ! half-sat. light at current temp.
        par_bott= meanpar                                                                                           !
        aLPAR2Veg = par_bott*exp(- extc *dz/2.0_rk)                                                                 !
        aLPAR1Veg = aLPAR2Veg / exp(- extc * min(self%cHeightVeg,sDepthW-dz/2.0_rk))
        write(0,'(A,I0,1X,2(ES24.16,1X))') 'DBG_MACRO_PAR ',debug_bottom_seq,par_bott,aLPAR1Veg
        flush(0)
        flush(0)                                !
        aLLimShootVeg = self%fEmergVeg + self%fFloatVeg * (1.0 - afCovEmergVeg) &                                   !
                 + bfSubVeg* (1.0 - afCovSurfVeg) * 1.0 / (extc * self%cHeightVeg) &                                !
                 * log( (1.0 + aLPAR1Veg / uhLVeg) / (1.0 + aLPAR2Veg / uhLVeg))                                    !
        ufDay = DayLength(lat,int(Day))                                                                             !
        aMuTmLVeg =ufDay * bfShootVeg * aLLimShootVeg * uFunTmProdVeg * self%cMuMaxVeg                              ! max. growth rate at current temp. AND light
        !===========================================================================================================!
        ! 2.5 nutrient limitation function                                                                          !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        aPLimVeg = min(1.0_rk,max(0.0_rk,(1.0_rk - self%cPDVegMin/rPDVeg) * self%cPDVegMax / (self%cPDVegMax - self%cPDVegMin)))! Droop function (P) for macrophytes
        aNLimVeg = min(1.0_rk,max(0.0_rk,(1.0_rk - self%cNDVegMin/rNDVeg) * self%cNDVegMax / (self%cNDVegMax - self%cNDVegMin)))! Droop function (N) for macrophytes
        aNutLimVeg = min(aPLimVeg,aNLimVeg)                                                                         ! nutrient limitation function of macrophytes
        aMuVeg = aMuTmLVeg * aNutLimVeg                                                                             ! actual growth rate of macrophytes
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!                                    
   !  3. Calculate growth rate                                                                                      !                                        
   !================================================================================================================!
        ! 3.1 calculate mortality                                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        if (Day < self%cDayWinVeg) then                                                                             !
           bkMortVeg = self%kMortVegSum                                                                             !
        else if (Day < self%cDayWinVeg + self%cLengMort) then                                                       !
           bkMortVeg = - log(self%fWinVeg) / self%cLengMort/secs_pr_day                                             !
        else                                                                                                        !
           bkMortVeg = self%kMortVegSum                                                                             !
        endif                                                                                                       !
        !===========================================================================================================!
        ! 3.2 calculate growth rates                                                                                !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        akDIncrVeg = aMuTmLVeg - self%kDRespVeg * uFunTmRespVeg -bkMortVeg                                          ! intrinsic net increase rate of macrophytes
        tDEnvVeg = max(0.0_rk, (sDVeg+sDCompts)*sDVeg*akDIncrVeg / (self%cDCarrVeg+NearZero))                       ! logistic correction of macrophytes
        tDEnvProdVeg = aMuVeg / self%cMuMaxVeg * tDEnvVeg                                                           ! logistic correction of production
        if (self%lCarrVeg) then                                                                                     !
           tDProdVeg = max(0.0_rk, aMuVeg * sDVeg - tDEnvProdVeg)                                                   ! macrophytes production w/ correction
        else                                                                                                        !
           tDProdVeg = max(0.0_rk, aMuVeg * sDVeg)                                                                  ! macrophytes production w/o correction
        endif                                                                                                       !
        tCProdVeg = tDProdVeg * self%cCPerDW                                                                        ! macrophyte C production
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. calculate nutrient uptake                                                                                   !
   !================================================================================================================!
        ! 4.1 calculate sediment fractions of nutrient uptake                                                       !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.1.1 nitrogen                                                                                         !
           !--------------------------------------------------------------------------------------------------------!
           if (.NOT. self%lEmpUpt .OR. bfRootVeg <= NearZero) then                                                  !
               afNUptVegS = 0.0_rk                                                                                  ! fraction of N uptake from sediment
           else if (self%fFloatVeg + bfSubVeg <= NearZero) then                                                     !
              afNUptVegS = 1.0_rk                                                                                   ! fraction of N uptake from sediment
           else                                                                                                     !
              afNUptVegS = self%fSedUptVegMax / (1.0_rk + self%fSedUptVegCoef * ((((oNDissS+NearZero) / &           !
                  (oNDissW+NearZero)) )** self%fSedUptVegExp))                                                      ! fraction of N uptake from sediment
           endif                                                                                                    !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.2.2 phosphorous                                                                                      !
           !--------------------------------------------------------------------------------------------------------!
           if (.NOT. self%lEmpUpt .OR. bfRootVeg <= NearZero) then                                                  !
              afPUptVegS = 0.0_rk                                                                                   ! fraction of P uptake from sediment
           else if (self%fFloatVeg + bfSubVeg <= NearZero) then                                                     !
              afPUptVegS = 1.0_rk                                                                                   ! fraction of P uptake from sediment
           else                                                                                                     !
              afPUptVegS = self%fSedUptVegMax / (1.0_rk + self%fSedUptVegCoef * ((((oPO4S+NearZero) / &             !
                  (sPO4W+NearZero)) )** self%fSedUptVegExp))                                                        ! fraction of P uptake from sediment
           endif                                                                                                    !   
        !===========================================================================================================!
        ! 4.2 calculate maximum stochiometrically corrected nutirent uptake rates                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.1.1 nitrogen                                                                                         !
           !--------------------------------------------------------------------------------------------------------!
           aVNUptMaxCrVeg = max( 0.0_rk, self%cVNUptMaxVeg * uFunTmProdVeg * (self%cNDVegMax - rNDVeg) / &          !
               (self%cNDVegMax - self%cNDVegMin))                                                                   ! maximum N uptake rate of macrophytes, corrected for N/D ratio
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.2.2 phosphorous                                                                                      !
           !--------------------------------------------------------------------------------------------------------!
           aVPUptMaxCrVeg = max( 0.0_rk, self%cVPUptMaxVeg * uFunTmProdVeg * (self%cPDVegMax-rPDVeg) / &            !
               (self%cPDVegMax-self%cPDVegMin))                                                                     ! maximum P uptake rate of macrophytes, corrected for P/D ratio
        !===========================================================================================================!
        ! 4.3 calculate realized uptake rates by different plant parts                                              !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.1.1 nitrogen                                                                                         !
           !--------------------------------------------------------------------------------------------------------!
           ahNUptVeg = aVNUptMaxCrVeg / self%cAffNUptVeg                                                            ! half-sat. 'constant' for N uptake
           if (.NOT. self%lEmpUpt) then                                                                             !
              aVNUptVegW = oNDissW * aVNUptMaxCrVeg / (ahNUptVeg + oNDissW)                                         ! N uptake RATE by subm AND floating parts
              tNUptVegW = aVNUptVegW * (aDSubVeg + aDFloatVeg)                                                      ! N uptake from water (by shoots)
              aVNUptVegS = oNDissS * aVNUptMaxCrVeg / (ahNUptVeg + oNDissS)                                         ! N uptake RATE of roots
              tNUptVegS = aVNUptVegS * aDRootVeg                                                                    ! N uptake from pore water (by roots)
           else                                                                                                     !
              aVNUptVegW = 0.0_rk                                                                                   ! N uptake RATE by subm AND floating parts
              tNUptVegW = (1.0_rk - afNUptVegS) * aVNUptMaxCrVeg * oNDissW / (ahNUptVeg + oNDissW) * sDVeg          ! N uptake from water (by shoots)
              aVNUptVegS = 0.0                                                                                      ! N uptake RATE of roots
              tNUptVegS = afNUptVegS * aVNUptMaxCrVeg * oNDissS / (ahNUptVeg + oNDissS) * sDVeg                     ! N uptake from pore water (by roots)
           endif                                                                                                    !
           tNUptVeg = tNUptVegW+ tNUptVegS                                                                          ! total Nitrogen uptake of water column and sediment
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.2.2 phosphorous                                                                                      !
           !--------------------------------------------------------------------------------------------------------!
           ahPUptVeg = aVPUptMaxCrVeg / self%cAffPUptVeg                                                            ! half-sat. 'constant' for P uptake
           if (.NOT. self%lEmpUpt) then                                                                             !
              aVPUptVegW = sPO4W * aVPUptMaxCrVeg / (ahPUptVeg + sPO4W)                                             ! P uptake RATE by subm AND floating parts
              aVPUptVegS = oPO4S * aVPUptMaxCrVeg / (ahPUptVeg + oPO4S + NearZero)                                  ! P uptake rate by roots
              tPUptVegW = aVPUptVegW * (aDSubVeg + aDFloatVeg)                                                      ! P uptake from water
              tPUptVegS = aVPUptVegS * aDRootVeg                                                                    ! P uptake from pore water (by root fraction)
           else                                                                                                     !               
              aVPUptVegW = 0.0_rk                                                                                   ! P uptake RATE by subm AND floating parts
              aVPUptVegS = 0.0_rk                                                                                   ! P uptake rate by roots
              tPUptVegW = (1.0 - afPUptVegS) * aVPUptMaxCrVeg * sPO4W / (ahPUptVeg + sPO4W) * sDVeg                 ! P uptake from water
              tPUptVegS = afPUptVegS * aVPUptMaxCrVeg * oPO4S / (ahPUptVeg + oPO4S) * sDVeg                         ! P uptake from pore water (by root fraction)
           endif                                                                                                    !
           tPUptVeg = tPUptVegW + tPUptVegS                                                                         ! total P uptake macrophytes
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. calculate respiration, migration, excretion and mortality                                                   !
   !================================================================================================================!
        ! 4.1 calculate respiration                                                                                 !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDRespVeg = self%kDRespVeg * uFunTmRespVeg * sDVeg                                                          ! dark respiration of macrophytes in DW
        tCRespVeg = tDRespVeg * rCDVeg                                                                              ! dark respiration of macrophytes in C
        !===========================================================================================================!
        ! 4.2 calculate excretion                                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tNExcrVeg = (2.0_rk * rNDVeg) / (self%cNDVegMax + rNDVeg) * rNDVeg * tDRespVeg                              ! N excretion by macrophytes
        tPExcrVeg = rPDVeg / (self%cPDVegMin + rPDVeg) * rPDVeg * tDRespVeg                                         ! P excretion by macrophytes
        !===========================================================================================================!
        ! 4.3 calculate mortality                                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.3.1 dry weight                                                                                       !
           !--------------------------------------------------------------------------------------------------------!
           tDEnvMortVeg = tDEnvVeg - tDEnvProdVeg                                                                   ! logistic correction of mortality
           if (self%lCarrVeg) then
              tDMortVeg = bkMortVeg * sDVeg + tDEnvMortVeg                                                          ! total mortality flux DW macrophytes w/ correction
           else
              tDMortVeg = bkMortVeg * sDVeg                                                                         ! total mortality flux DW macrophytes w/o correction
           endif
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 4.3.2 N, P and C                                                                                       !
           !--------------------------------------------------------------------------------------------------------!
           tNMortVeg = rNDVeg * tDMortVeg                                                                           ! N mortality flux of macrophytes
           tPMortVeg = rPDVeg * tDMortVeg                                                                           ! P mortality flux of macrophytes
           tCMortVeg = rCDVeg * tDMortVeg                                                                           ! C mortality flux of macrophytes
        !===========================================================================================================!
        ! 4.4 calculate migration                                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDMigrVeg = self%kMigrVeg * (self%cDVegIn - sDVeg)                                                          ! migration flux dry weight
        tPMigrVeg = self%kMigrVeg * (self%cPDVeg0*self%cDVegIn - sPVeg)                                             ! net migration flux P
        tNMigrVeg = self%kMigrVeg * (self%cNDVeg0*self%cDVegIn - sNVeg)                                             ! net migration flux N
        tCMigrVeg = self%kMigrVeg * (self%cCPerDW*self%cDVegIn - sCVeg)                                             ! net migration flux N
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 5. final flux calculations                                                                                     !
   !================================================================================================================!
        ! 5.1 final macrophyte rate of change                                                                       !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDBedVeg = tDMigrVeg + tDProdVeg- tDMortVeg - tDRespVeg                                                     ! derivative of macrophytes biomass
        tNBedVeg = tNMigrVeg + tNUptVeg - tNExcrVeg - tNMortVeg                                                     ! total macrophytes N flux in bed module
        tPBedVeg = tPMigrVeg + tPUptVeg - tPExcrVeg - tPMortVeg                                                     ! total macrophytes P flux in bed module
        tCBedVeg = tCMigrVeg + tCProdVeg- tCRespVeg - tCMortVeg                                                     ! total macrophytes P flux in bed module
        !===========================================================================================================!
        ! 5.2 final fluxes to external dry weight variables                                                         !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.2.1 water                                                                                            !
           !--------------------------------------------------------------------------------------------------------!
           tDMortVegW = self%fTOMWMortVeg * (1.0_rk - bfRootVeg) * tDMortVeg                                        ! mortality flux to watercolumn organic matter
           wDBedTOMW = tDMortVegW                                                                                   ! total DW flux to watercolumn organic matter
           wDBedPOMW = wDBedTOMW * (1.0_rk - self%fVegDOMW)                                                         ! total DW flux to watercolumn particulate organic matter
           wDBedDOMW = wDBedTOMW * self%fVegDOMW                                                                    ! total DW flux to watercolumn dissolved organic matter
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.2.2 sediment                                                                                         !
           !--------------------------------------------------------------------------------------------------------!
           tDMortVegS = tDMortVeg - tDMortVegW                                                                      ! mortality flux to sediment organic matter
           tDBedPOMS = tDMortVegS * (1.0_rk - self%fVegDOMS)                                                        ! total DW flux to sediment particulate organic matter
           tDBedDOMS = tDMortVegS * self%fVegDOMS                                                                   ! total DW flux to sediment dissolved organic matter
        !===========================================================================================================!
        ! 5.3 final fluxes to external nitrogen variables                                                           !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.3.1 water                                                                                            !
           !--------------------------------------------------------------------------------------------------------!
           afNH4UptVegW = sNH4W * sNO3W / ((ahNUptVeg + sNH4W) * (ahNUptVeg + sNO3W + NearZero)) &                  !
               + sNH4W * ahNUptVeg / ((sNH4W + sNO3W + NearZero) * (ahNUptVeg + sNO3W + NearZero))                  ! fraction of ammonium uptake from water column (adapted from WASP model, EPA)
           tNUptNH4VegW = afNH4UptVegW * tNUptVegW                                                                  ! NH4 uptake from_water
           tNExcrVegW = tNExcrVeg * (1.0_rk-bfRootVeg)                                                              ! N excretion to water
           tNMortVegNH4 = self%fDissMortVeg * tNMortVeg                                                             ! mortality flux as ammonia
           tNMortVegNH4W = tNMortVegNH4 * (1.0_rk-bfRootVeg)                                                        ! mortality flux to watercolumn NH4
           wNBedNH4W = - tNUptNH4VegW + tNExcrVegW + tNMortVegNH4W                                                  ! total N flux to watercolumn NH4
           tNUptNO3VegW = tNUptVegW - tNUptNH4VegW                                                                  ! NO3 uptake from the watercolumn
           wNBedNO3W = - tNUptNO3VegW                                                                               ! total N flux to watercolumn NO3
           tNMortVegTOM = tNMortVeg - tNMortVegNH4                                                                  ! mortality flux as organic N
           tNMortVegTOMW = self%fTOMWMortVeg * (1.0_rk - bfRootVeg) * tNMortVegTOM                                  ! mortality flux to watercolumn organic N
           wNBedTOMW = tNMortVegTOMW                                                                                ! total N flux to watercolumn organic matter
           wNBedPOMW = wNBedTOMW * (1.0_rk - self%fVegDOMW)                                                         ! total particulate organic N flux to watercolumn
           wNBedDOMW = wNBedTOMW * self%fVegDOMW                                                                    ! total dissolved organic N flux to watercolumn
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.3.2 sediment                                                                                         !
           !--------------------------------------------------------------------------------------------------------!
           afNH4UptVegS = oNH4S * oNO3S / ((ahNUptVeg + oNH4S +NearZero) * (ahNUptVeg + oNO3S +NearZero)) + &       !
               oNH4S * ahNUptVeg / ((oNH4S + oNO3S+NearZero) * (ahNUptVeg + oNO3S+NearZero))                        ! fraction of ammonium uptake from pore water (from WASP model, EPA)
           tNExcrVegS = bfRootVeg * tNExcrVeg                                                                       ! N excretion to sediment
           tNMortVegNH4S = bfRootVeg * tNMortVegNH4                                                                 ! mortality flux as ammonia
           tNUptNH4VegS = afNH4UptVegS * tNUptVegS                                                                  ! NH4 uptake of macrophytes from sediment
           tNBedNH4S = - tNUptNH4VegS + tNExcrVegS + tNMortVegNH4S                                                  ! total N flux to NH4 in pore water
           tNUptNO3VegS = tNUptVegS - tNUptNH4VegS                                                                  ! NO3 uptake of macrophytes from sediment
           tNBedNO3S = - tNUptNO3VegS                                                                               ! total N flux to NO3 in pore water
           tNMortVegTOMS = tNMortVegTOM - tNMortVegTOMW                                                             ! mortality flux as organic N in sediment
           tNBedPOMS = tNMortVegTOMS* (1.0_rk - self%fVegDOMS)                                                      ! total particulate organic N flux to sediment
           tNBedDOMS = tNMortVegTOMS * self%fVegDOMS                                                                ! total dissolved organic N flux to sediment 
        !===========================================================================================================!
        ! 5.4 final fluxes to external phosphorous variables                                                        !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.4.1 water                                                                                            !
           !--------------------------------------------------------------------------------------------------------!
           tPExcrVegW = tPExcrVeg * (1.0_rk-bfRootVeg)                                                              ! P excretion to the watercolumn
           tPMortVegPO4 = self%fDissMortVeg * tPMortVeg                                                             ! mortality flux as phosphate
           tPMortVegPO4W = tPMortVegPO4 * (1.0_rk-bfRootVeg)                                                        ! mortality flux of phosphate to the watercolumn
           wPBedPO4W = - tPUptVegW + tPExcrVegW + tPMortVegPO4W                                                     ! total P flux as PO4 to the watercolumn
           tPMortVegTOM = tPMortVeg - tPMortVegPO4                                                                  ! mortality flux as organic P
           tPMortVegTOMW = self%fTOMWMortVeg * (1.0_rk - bfRootVeg) * tPMortVegTOM                                  ! mortality flux as organic P to the watercolumn
           wPBedTOMW = tPMortVegTOMW                                                                                ! total P flux as organic matter to the watercolumn
           wPBedPOMW = wPBedTOMW * (1.0_rk - self%fVegDOMW)                                                         ! total particulate organic P flux to watercolumn
           wPBedDOMW = wPBedTOMW * self%fVegDOMW                                                                    ! total dissolved organic P flux to watercolumn
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.4.2 sediment                                                                                         !
           !--------------------------------------------------------------------------------------------------------!
           tPExcrVegS = bfRootVeg * tPExcrVeg                                                                       ! P excretion to the sediment
           tPMortVegPO4S = bfRootVeg * tPMortVegPO4                                                                 ! mortality flux of phosphate to the sediment
           tPBedPO4S = - tPUptVegS + tPExcrVegS + tPMortVegPO4S                                                     ! total P flux as PO4 to the sediment
           tPMortVegTOMS = tPMortVegTOM - tPMortVegTOMW                                                             ! mortality flux as organic P to the sediment
           tPBedPOMS = tPMortVegTOMS * (1.0_rk - self%fVegDOMS)                                                     ! total particulate organic P flux to the sediment
           tPBedDOMS = tPMortVegTOMS * self%fVegDOMS                                                                ! total dissolved organic P flux to the sediment
        !===========================================================================================================!
        ! 5.5 final fluxes to external O2 variables                                                                 !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.5.1 water                                                                                            !
           !--------------------------------------------------------------------------------------------------------!
           tO2UptNO3VegW = O2PerNO3 * molO2molN * bfSubVeg * tNUptNO3VegW                                           ! O2 release to the watercolumn due to NO3 uptake
           aCorO2BOD = sO2W / (self%hO2BOD + sO2W)                                                                  ! correction of O2 demand in water at low oxygen conc.
           tO2RespVegW = molO2molC * self%cCPerDW * bfSubVeg * tDRespVeg * aCorO2BOD                                ! submerged O2 respiration
           tO2RespVegS = molO2molC * self%cCPerDW * bfRootVeg * tDRespVeg * afOxySed                                ! root O2 respiration
           tO2ProdVeg = molO2molC * self%cCPerDW * tDProdVeg                                                        ! macrophytes O2 production
           tO2ProdVegS = min (tO2RespVegS,tO2ProdVeg)                                                               ! O2 transport to roots
           tO2ProdVegW = min( tO2ProdVeg - tO2ProdVegS, bfSubVeg * tO2ProdVeg)                                      ! O2 used for macrophytes production
           tO2BedW = tO2ProdVegW - tO2RespVegW + tO2UptNO3VegW                                                      ! total O2 flux to the watercolumn          
        !===========================================================================================================!
        ! 5.6 final fluxes to external CO2 variables                                                                !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.6.1 water                                                                                            !
           !--------------------------------------------------------------------------------------------------------!
           tCO2BedW = (tO2ProdVegW - tO2RespVegW) / molO2molC                                                       ! total CO2 flux to the watercolumn
           tCMortVegW = self%fTOMWMortVeg * (1.0_rk - bfRootVeg) * tCMortVeg                                        ! mortality flux to watercolumn organic matter
           wCBedTOMW = tCMortVegW                                                                                   ! total C flux to watercolumn organic matter
           wCBedPOMW = wCBedTOMW * (1.0_rk - self%fVegDOMW)                                                         ! total C flux to watercolumn particulate organic matter
           wCBedDOMW = wCBedTOMW * self%fVegDOMW                                                                    ! total C flux to watercolumn dissolved organic matter
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 5.6.2 sediment                                                                                         !
           !--------------------------------------------------------------------------------------------------------!
           tCMortVegS = tCMortVeg - tCMortVegW                                                                      ! mortality flux to sediment organic matter
           tCBedPOMS = tCMortVegS * (1.0_rk - self%fVegDOMS)                                                        ! total C flux to sediment particulate organic matter
           tCBedDOMS = tCMortVegS * self%fVegDOMS                                                                   ! total C flux to sediment dissolved organic matter
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 6. update model variables                                                                                      !
   !================================================================================================================!
      ! 6.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_ODE_(self%id_sDVeg,tDBedVeg)                                                                      !
      _SET_BOTTOM_ODE_(self%id_sNVeg,tNBedVeg)                                                                      !
      _SET_BOTTOM_ODE_(self%id_sPVeg,tPBedVeg)                                                                      !
      _SET_BOTTOM_ODE_(self%id_sCVeg,tCBedVeg)                                                                      !
                                                                                                                    !
      _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)                                                           !
      _SET_BOTTOM_EXCHANGE_(self%id_sDVeg_PV,tDBedVeg*bot_pel_conv)                                                 !
      _SET_BOTTOM_EXCHANGE_(self%id_sPVeg_PV,tPBedVeg*bot_pel_conv)                                                 !
      _SET_BOTTOM_EXCHANGE_(self%id_sNVeg_PV,tNBedVeg*bot_pel_conv)                                                 !
      _SET_BOTTOM_EXCHANGE_(self%id_sCVeg_PV,tCBedVeg*bot_pel_conv)                                                 !
      !=============================================================================================================!
      ! 6.2 update external abiotic state variables                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_EXCHANGE_(self%id_NH4poolW,wNBedNH4W)                                                             !
      _SET_BOTTOM_EXCHANGE_(self%id_NO3poolW,wNBedNO3W)                                                             !
      _SET_BOTTOM_EXCHANGE_(self%id_PO4poolW,wPBedPO4W)                                                             !
      _SET_BOTTOM_EXCHANGE_(self%id_O2poolW,tO2BedW)                                                                !
      !_SET_BOTTOM_EXCHANGE_(self%id_CO2poolW,tCO2BedW)                                                              ! until GHG module implemented
      _SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolW,wDBedPOMW)                                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolW,wNBedPOMW)                                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolW,wPBedPOMW)                                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolW,wCBedPOMW)                                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_DDOMpoolW,wDBedDOMW)                                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_NDOMpoolW,wNBedDOMW)                                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_PDOMpoolW,wPBedDOMW)                                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_CDOMpoolW,wCBedDOMW)                                                            !
      _SET_BOTTOM_ODE_(self%id_NH4poolS,tNBedNH4S)                                                                  !
      _SET_BOTTOM_ODE_(self%id_NO3poolS,tNBedNO3S)                                                                  !
      _SET_BOTTOM_ODE_(self%id_PO4poolS,tPBedPO4S)                                                                  !
      _SET_BOTTOM_ODE_(self%id_DPOMpoolS,tDBedPOMS)                                                                 !
      _SET_BOTTOM_ODE_(self%id_NPOMpoolS,tNBedPOMS)                                                                 !
      _SET_BOTTOM_ODE_(self%id_PPOMpoolS,tPBedPOMS)                                                                 !
      _SET_BOTTOM_ODE_(self%id_CPOMpoolS,tCBedPOMS)                                                                 !
      _SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolS_PV,tDBedPOMS*bot_pel_conv)                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolS_PV,tNBedPOMS*bot_pel_conv)                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolS_PV,tPBedPOMS*bot_pel_conv)                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolS_PV,tCBedPOMS*bot_pel_conv)                                            !
      _SET_BOTTOM_ODE_(self%id_DDOMpoolS,tDBedDOMS)                                                                 !
      _SET_BOTTOM_ODE_(self%id_NDOMpoolS,tNBedDOMS)                                                                 !
      _SET_BOTTOM_ODE_(self%id_PDOMpoolS,tPBedDOMS)                                                                 !
      _SET_BOTTOM_ODE_(self%id_CDOMpoolS,tCBedDOMS)                                                                 !
      _SET_BOTTOM_EXCHANGE_(self%id_DDOMpoolS_PV,tDBedDOMS*bot_pel_conv)                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_NDOMpoolS_PV,tNBedDOMS*bot_pel_conv)                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_PDOMpoolS_PV,tPBedDOMS*bot_pel_conv)                                            !
      _SET_BOTTOM_EXCHANGE_(self%id_CDOMpoolS_PV,tCBedDOMS*bot_pel_conv)                                            !
      !=============================================================================================================!
      ! 6.3 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tO2BedW,tO2BedW)                                                          !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_aDSubVeg,aDSubVeg)                                                        !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_aCovVeg,aCovVeg)                                                          !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBedPOMS,tDBedPOMS)                                                      !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_afCovSurfVeg,afCovSurfVeg)                                                !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBedVeg,tDBedVeg)                                                        !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_macroextinction,extc)                                                     !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_aLPAR1Veg,aLPAR1Veg)                                                      !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_aLPAR2Veg,aLPAR2Veg)                                                      !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_aLLimVeg,aLLimShootVeg)                                                   !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_aNutLimVeg,aNutLimVeg)                                                    !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBedVeg,tDBedVeg)                                                        !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBedVeg,tNBedVeg)                                                        !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBedVeg,tPBedVeg)                                                        !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCBedVeg,tCBedVeg)                                                        !
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_ufDay,ufDay)                                                              !
      !=============================================================================================================!
      ! 6.4 update local diagnostic output processes                                                                !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_aMuVeg,        aMuVeg)                                                !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDEnvProdVeg,  tDEnvProdVeg)                                          !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDMigrVeg,     tDMigrVeg)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDProdVeg,     tDProdVeg)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDMortVeg,     tDMortVeg)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_wDBedPOMW,     wDBedPOMW)                                             !   
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_wDBedDOMW,     wDBedDOMW)                                             !   
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDRespVeg,     tDRespVeg)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNMigrVeg,     tNMigrVeg)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNUptVegW,     tNUptVegW)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNExcrVeg,     tNExcrVeg)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNUptNH4VegW,  tNUptNH4VegW)                                          !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNExcrVegW,    tNExcrVegW)                                            !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNMortVegNH4W, tNMortVegNH4W)                                         !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNUptNO3VegW,  tNUptNO3VegW)                                          !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_wNBedPOMW,     wNBedPOMW)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_wNBedDOMW,     wNBedDOMW)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPUptVegW,     tPUptVegW)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPExcrVegW,    tPExcrVegW)                                            !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPMortVegPO4W, tPMortVegPO4W)                                         !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_wPBedPOMW,     wPBedPOMW)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_wPBedDOMW,     wPBedDOMW)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tO2ProdVegW,   tO2ProdVegW)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tO2RespVegW,   tO2RespVegW)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tO2UptNO3VegW, tO2UptNO3VegW)                                         !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCMigrVeg,     tCMigrVeg)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCProdVeg,     tCProdVeg)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCMortVeg,     tCMortVeg)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_wCBedPOMW,     wCBedPOMW)                                             !   
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_wCBedDOMW,     wCBedDOMW)                                             !   
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCRespVeg,     tCRespVeg)                                             !
          ! sediment diagnostics                                                                                    ! 
!          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBedPOMS,    tDBedPOMS) ! already set above                         !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBedDOMS,     tDBedDOMS)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNUptNH4VegS,  tNUptNH4VegS)                                          !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNUptVegS,     tNUptVegS)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNExcrVegS,    tNExcrVegS)                                            !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNMortVegNH4S, tNMortVegNH4S)                                         !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNUptNO3VegS,  tNUptNO3VegS)                                          !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBedPOMS,     tNBedPOMS)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBedDOMS,     tNBedDOMS)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPMigrVeg,     tPMigrVeg)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPUptVegS,     tPUptVegS)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPExcrVegS,    tPExcrVegS)                                            !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPMortVegPO4S, tPMortVegPO4S)                                         !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBedPOMS,     tPBedPOMS)                                             ! 
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBedDOMS,     tPBedDOMS)                                             ! 
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tO2ProdVegS,   tO2ProdVegS)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCBedPOMS,     tCBedPOMS)                                             ! 
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCBedDOMS,     tCBedDOMS)                                             ! 
      endif                                                                                                         !
   !================================================================================================================!
   _HORIZONTAL_LOOP_END_
end subroutine do_bottom

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: GET LIGHT EXTINCTION                                                                                                                                                               §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine get_light_extinction(self,_ARGUMENTS_GET_EXTINCTION_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_macrophytes), intent(in) :: self
   _DECLARE_ARGUMENTS_GET_EXTINCTION_
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk):: aDSubVeg, aCovVeg, afCovSurfVeg, sDVeg, uTm, Day, lat, aDayInitVeg, aDShootVeg, aDRootVeg, aDEmergVeg, aDFloatVeg, bfShootVeg, bfRootVeg, bfSubVeg

   _LOOP_BEGIN_  !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve current state and environmental variables                                                         !
   !================================================================================================================!
   _GET_(self%id_sDVeg_PV,sDVeg)
   _GET_(self%id_uTm,uTm)
   _GET_GLOBAL_(self%id_Day,Day)
   _GET_HORIZONTAL_(self%id_lat,lat)
   _GET_(self%id_aDayInitVeg,aDayInitVeg)
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. Recompute submerged biomass from current state, not the previous do() diagnostic.                          !
   !================================================================================================================!
   call self%calc_veg_fractions(Day,sDVeg,uTm,lat,aDSubVeg,aCovVeg,afCovSurfVeg,aDayInitVeg,aDShootVeg,aDRootVeg,aDEmergVeg,aDFloatVeg,bfShootVeg,bfRootVeg,bfSubVeg)
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  3. Self-shading with explicit contribution from background phytoplankton concentration.                       !
   !================================================================================================================!
   _SET_EXTINCTION_(self%cExtSpVeg*aDSubVeg)                                                                   !
   !================================================================================================================!
   _LOOP_END_ !!! END OF MODEL CODE::   

end subroutine get_light_extinction
   
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO                                                                                                                                                                                 §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do(self,_ARGUMENTS_DO_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_macrophytes), intent(in) :: self
   _DECLARE_ARGUMENTS_DO_
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)     :: sDVeg, aDSubVeg, aCovVeg, afCovSurfVeg, aDayInitVeg, Day, lat, uTm , aDShootVeg, aDRootVeg, aDEmergVeg, aDFloatVeg, bfShootVeg, bfRootVeg, bfSubVeg

   _LOOP_BEGIN_  !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
   _GET_(self%id_uTm,uTm)                                                                                           !
   _GET_GLOBAL_(self%id_Day,Day)                                                                                    !
   _GET_HORIZONTAL_(self%id_lat,lat)
   _GET_(self%id_aDayInitVeg,aDayInitVeg)                                                                           !
   _GET_(self%id_sDVeg_PV,sDVeg)                                                                                    !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. calculate fractions of biomass in shoots, roots etc. (function at file end, shared with do_bottom routine) !
   !================================================================================================================!
   call self%calc_veg_fractions(Day,sDVeg,uTm,lat,aDSubVeg,aCovVeg,afCovSurfVeg,aDayInitVeg,aDShootVeg,aDRootVeg,aDEmergVeg,aDFloatVeg,bfShootVeg,bfRootVeg,bfSubVeg)                               !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  3. update diagnostic variables                                                                                !
   !================================================================================================================!
   _SET_DIAGNOSTIC_(self%id_aDSubVeg_PV,aDSubVeg)                                                                   !
   _SET_DIAGNOSTIC_(self%id_aCovVeg_PV,aCovVeg)                                                                     !
   _SET_DIAGNOSTIC_(self%id_afCovSurfVeg_PV,afCovSurfVeg)                                                           !
   _SET_DIAGNOSTIC_(self%id_aDayInitVeg_out,aDayInitVeg)                                                            !
   _SET_DIAGNOSTIC_(self%id_bfRootVeg_PV,bfRootVeg)
   !================================================================================================================!
   _LOOP_END_ !!! END OF MODEL CODE::
end subroutine do
   
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: CALCULATE VEGETATIVE FRACTIONS AND DIAGNOSTICS                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine calc_veg_fractions(self,Day,sDVeg,uTm,lat,aDSubVeg,aCovVeg,afCovSurfVeg,aDayInitVeg,aDShootVeg,aDRootVeg,aDEmergVeg,aDFloatVeg,bfShootVeg,bfRootVeg,bfSubVeg)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_macrophytes), intent(in), target :: self
   real(rk),                          intent(in)          :: Day,sDVeg,uTm,lat
   real(rk),                          intent(out)         :: aDSubVeg, aCovVeg, afCovSurfVeg
   real(rk),                          intent(inout)       :: aDayInitVeg
   real(rk), optional,                intent(out)         :: aDShootVeg,aDRootVeg,aDEmergVeg,aDFloatVeg,bfShootVeg,bfRootVeg,bfSubVeg
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)  :: aDShootVeg_int,aDRootVeg_int,bfShootVeg_int,bfRootVeg_int,bfSubVeg_int,aDFloatVeg_int,aDEmergVeg_int
   integer   :: season
   logical   :: yeartrans
   
   !!! BEGINNING OF MODEL CODE::
   yeartrans = .false. ! Local state must not persist across calls.
   if (aDayInitVeg < -1.0_rk) aDayInitVeg = -1.0_rk ! Normalize external missing sentinels to the no-onset state.
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. the germination, allocation and reallocation processes                                                     !  NOTE: This section only really works for northern hemisphere temperate regions
   !================================================================================================================!
   if (Day < self%cDayWinVeg .AND. Day >= self%cDaySumVegMin) then                                                  ! clear case: spring or summer (probably northern hemisphere)
       season = 4                                                                                                   !   it is winter until the onset of growth 
       if (aDayInitVeg .eq. -1.0_rk .AND. uTm >= self%cTmInitVeg) then                                              !   first day of growing season
           season = 1                                                                                               !     set season case to winter/summer transition
           aDayInitVeg = Day                                                                                        !     record first day of the growing season
       elseif (aDayInitVeg > 0.0_rk .AND. Day <= aDayInitVeg + self%cLengAllo) then                                 !   still in the transition period
           season = 1                                                                                               !     set season case to winter/summer transition
       elseif (aDayInitVeg > 0.0_rk) then                                                                           !   past transition period
           season = 2                                                                                               !     set season case to summer
       endif                                                                                                        !
   elseif (Day >= self%cDayWinVeg .AND. Day < self%cDaySumVegMin) then                                              ! clear case: winter (probably southern hemisphere)
       if (Day < self%cDayWinVeg + self%cLengAllo) then                                                             !   still in transition period
           season = 3                                                                                               !     set season case to summer/winter transition
       elseif (Day >= self%cDayWinVeg + self%cLengAllo) then                                                        !   past transition period
           season = 4                                                                                               !     set season case to winter
       endif                                                                                                        !
   elseif (Day < self%cDayWinVeg .AND. Day < self%cDaySumVegMin) then                                               ! beginning of the year: can be either summer or winter
       if (self%cDayWinVeg < self%cDaySumVegMin) then                                                               !   summer case
           if (aDayInitVeg + self%cLengAllo >= 366.0_rk .AND. Day <= aDayInitVeg + self%cLengAllo - 366.0_rk) then  !     transition period in progress (inherited from previous year)
               yeartrans = .true.                                                                                   !       record that we are in an inherited transition
               season = 1                                                                                           !       set season case to winter/summer transition
           else                                                                                                     !     past transition period
               season = 2                                                                                           !       set  season tracker to summer
           endif                                                                                                    !
       elseif (self%cDaySumVegMin < self%cDayWinVeg) then                                                           !   winter case
           if (self%cDayWinVeg+self%cLengAllo >= 366.0_rk .AND. Day < self%cDayWinVeg+self%cLengAllo-366.0_rk) then !     transition period in progress (inherited from previous year)
               yeartrans = .true.                                                                                   !       record that we are in an inherited transition
               season = 3                                                                                           !       set season case to summer/winter transition
           else                                                                                                     !     past transition period
               season = 4                                                                                           !       set  season tracker to winter
           endif                                                                                                    !
       endif                                                                                                        !
   elseif (Day >= self%cDayWinVeg .AND. Day >= self%cDaySumVegMin) then                                              ! end of the year: can be either summer or winter
       if (self%cDayWinVeg < self%cDaySumVegMin) then                                                               !   summer case
           if (aDayInitVeg .eq. -1.0_rk .AND. uTm >= self%cTmInitVeg) then                                          !     first day of growing season
               season = 1                                                                                           !       set season case to winter/summer transition
               aDayInitVeg = Day                                                                                    !       record first day og the growing season
           elseif (aDayInitVeg > 0.0_rk .AND. Day >= aDayInitVeg + self%cLengAllo) then                             !     still in the transition period
               season = 1                                                                                           !       set season case to winter/summer transition
           elseif (aDayInitVeg > 0.0_rk) then                                                                       !     past transition period
               season = 2                                                                                           !       set season case to summer
           endif                                                                                                    !
       elseif (self%cDaySumVegMin < self%cDayWinVeg) then                                                           !   winter case
           if (Day < self%cDayWinVeg + self%cLengAllo) then                                                         !     still in transition period
               season = 3                                                                                           !       set season case to summer/winter transition
           elseif (Day >= self%cDayWinVeg + self%cLengAllo) then                                                    !     past transition period
               season = 4                                                                                           !       set season case to winter
           endif                                                                                                    !     
       endif                                                                                                        !
   endif                                                                                                            !
                                                                                                                    !
   if (season == 1) then                                                                                            ! case: winter/summer transition
       if (yeartrans) then                                                                                          !   special case: transition period inherited from previous year
           bfRootVeg_int = 0.5*(self%fRootVegWin + self%fRootVegSum) + 0.5*(self%fRootVegWin - self%fRootVegSum)* & !   
               cos(Pi/self%cLengAllo * (Day + 366.0_rk - aDayInitVeg))                                              !     calculate root fraction as a sinusoid transition from winter to summer value
       else                                                                                                         !   normal within-year transition
           bfRootVeg_int = 0.5*(self%fRootVegWin + self%fRootVegSum) + 0.5*(self%fRootVegWin - self%fRootVegSum)* & !   
               cos(Pi/self%cLengAllo * (Day - aDayInitVeg))                                                         !     calculate root fraction as a sinusoid transition from winter to summer value
       endif                                                                                                        !
   elseif (season == 2) then                                                                                        ! case: summer
       bfRootVeg_int = self%fRootVegSum                                                                             !     root fraction is set to summer value
   elseif (season == 3) then                                                                                        ! case: summer/winter transition
       if (yeartrans) then                                                                                          !   special case: transition period inherited from previous year
           bfRootVeg_int = 0.5*(self%fRootVegWin + self%fRootVegSum) - 0.5*(self%fRootVegWin - self%fRootVegSum)* & !  
               cos(Pi/self%cLengAllo * (Day + 366.0_rk - self%cDayWinVeg))                                          !     calculate root fraction as a sinusoid transition from summer to winter value 
       else                                                                                                         !   normal within-year transition
           bfRootVeg_int = 0.5*(self%fRootVegWin + self%fRootVegSum) - 0.5*(self%fRootVegWin - self%fRootVegSum)* & !  
               cos(Pi/self%cLengAllo * (Day - self%cDayWinVeg))                                                     !     calculate root fraction as a sinusoid transition from summer to winter value 
       endif                                                                                                        !
       aDayInitVeg = -1.0_rk                                                                                        !   reset aDayInitVeg
   elseif (season == 4) then                                                                                        ! case: winter
       bfRootVeg_int = self%fRootVegWin                                                                             !   root fraction is set to winter setting
       aDayInitVeg = -1.0_rk                                                                                        !   reset aDayInitVeg
   endif                                                                                                            !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. calculate fractions of biomass in roots and shoots                                                         !
   !================================================================================================================!
   bfShootVeg_int = 1.0_rk - bfRootVeg_int                                                                          ! calculate shoot fraction
   aDRootVeg_int = bfRootVeg_int * sDVeg                                                                            ! calculate root biomass
   aDShootVeg_int = bfShootVeg_int * sDVeg                                                                          ! calculate shoot biomass
   aDEmergVeg_int = self%fEmergVeg * aDShootVeg_int                                                                 ! calculate emergent biomass
   aDFloatVeg_int = self%fFloatVeg * aDShootVeg_int                                                                 ! calculate floating biomass
   bfSubVeg_int = 1.0_rk - self%fFloatVeg - self%fEmergVeg                                                          ! calculate submerged fraction of shoot (self%fFloatVeg + self%fEmergVeg must not exceed 1)
   aDSubVeg = bfSubVeg_int * aDShootVeg_int                                                                         ! calculate submerged biomass
   aCovVeg = min(100.0_rk, self%cCovSpVeg * aDShootVeg_int)                                                         ! calculate percent cover
   afCovSurfVeg = min(1.0_rk, max(aDFloatVeg_int / (self%cDLayerVeg + NearZero), aDEmergVeg_int / (&                !
        self%fEmergVeg * self%cDCarrVeg + NearZero) ))                                                              ! fraction of water SURFACE covered by plant species
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  3. output calculated variables                                                                                !
   !================================================================================================================!
   if (present(bfShootVeg)) bfShootVeg = bfShootVeg_int                                                             !
   if (present(bfRootVeg)) bfRootVeg = bfRootVeg_int                                                                !
   if (present(bfSubVeg)) bfSubVeg = bfSubVeg_int                                                                   !
   if (present(aDShootVeg)) aDShootVeg = aDShootVeg_int                                                             !
   if (present(aDRootVeg)) aDRootVeg = aDRootVeg_int                                                                !
   if (present(aDEmergVeg)) aDEmergVeg = aDEmergVeg_int                                                             !
   if (present(aDFloatVeg)) aDFloatVeg = aDFloatVeg_int                                                             !
   !================================================================================================================!
end subroutine calc_veg_fractions
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
end module wet_macrophytes
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
