#include "fabm_driver.h"
!
! MODULE: ORGANIC MATTER POOL                                                                                                                                                                          
!
module wet_om_pool
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_expressions
   use fabm_standard_variables
   use fabm_particle
   use wet_utility, ONLY:uFunTmArrh, DayLength
   implicit none
   private
   
   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public  :: type_wet_om_pool
   !ORGANIC MATTER IN WATER COLUMN::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! local state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------
   type (type_state_variable_id)                                         :: id_sDW,id_sNW,id_sPW, id_sCW
   ! diagnostic variables for local output--------------------------------------------------------------------------------------------------------------------------------------------------------
   type (type_diagnostic_variable_id)                                    :: id_rPDW,id_rNDW, id_rCDW
   type (type_diagnostic_variable_id)                                    :: id_ext
   ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
   type (type_diagnostic_variable_id)                                    :: id_wDMin, id_wNMin, id_wPMin, id_wCMin, id_wNDenitW, id_wO2Min 
   ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
   type (type_state_variable_id)                                         :: id_DTransW, id_NTransW, id_PTransW, id_CTransW
   type (type_state_variable_id)                                         :: id_O2poolW, id_NO3poolW
   ! diagnostic variable for external dependencies:-----------------------------------------------------------------------------------------------------------------------------------------------
   type (type_dependency_id)                                             :: id_uTm
   ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   logical                                                               :: diagnostics
   real(rk)                                                              :: cThetaMinW, kDMinW, kNMinW, kPMinW, kCMinW, cVSet, cExtSp
   real(rk)                                                              :: hO2BOD, hNO3DenitW, NO3PerCW ! cCPerDWW
   integer                                                               :: qTrans
   !ORGANIC MATTER IN SEDIMENT::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! local state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------
   type (type_bottom_state_variable_id)                                  :: id_sDS,id_sPS,id_sNS, id_sCS
   type (type_state_variable_id)                                         :: id_sDS_PV,id_sPS_PV,id_sNS_PV, id_sCS_PV
   ! diagnostic variable identifiers--------------------------------------------------------------------------------------------------------------------------------------------------------------
   type (type_horizontal_diagnostic_variable_id)                         :: id_rPDS, id_rNDS, id_rCDS, id_tDPOMS
   ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
   type (type_horizontal_diagnostic_variable_id)                         :: id_tDMin, id_tNMin, id_tPMin, id_tCMin, id_tDTrans, id_tNTrans, id_tPTrans, id_tCTrans
   type (type_horizontal_diagnostic_variable_id)                         :: id_tDRefr, id_tNRefr, id_tPRefr, id_tCRefr, id_tDRefr_PV, id_tNRefr_PV, id_tPRefr_PV, id_tCRefr_PV
   ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
   type (type_bottom_state_variable_id)                                  :: id_DTransS, id_NTransS, id_PTransS, id_CTransS
   type (type_bottom_state_variable_id)                                  :: id_DRefrS, id_NRefrS, id_PRefrS, id_CRefrS
   type (type_state_variable_id)                                         :: id_DTransS_PV, id_NTransS_PV, id_PTransS_PV, id_CTransS_PV, id_DRefrS_PV, id_NRefrS_PV, id_PRefrS_PV, id_CRefrS_PV
   type (type_horizontal_dependency_id)                                  :: id_bot_pel_conv, id_afOxySed
   ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   real(rk)                                                              :: cThetaMinS, kDMinS, kNMinS, kPMinS, kCMinS, fRefrDWS, fRefrNutS ! cCPerDWS
   integer                                                               :: qExch
   logical                                                               :: lTransPV, lRefrPV, lPOMtoDOM, lRefrpool, lTransDWtarget
    
   contains                                                                          

   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure :: initialize
   procedure :: do
   procedure :: do_bottom
   !procedure :: get_vertical_movement
   procedure :: get_light_extinction
   
   end type type_wet_om_pool

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: Pi=3.14159265358979_rk
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk),parameter :: molO2molC = 2.6667_rk
   !real(rk),parameter :: O2PerNO3 = 1.5_rk
   !real(rk),parameter :: molO2molN = 2.2857_rk
   real(rk),parameter :: molNmolC = 1.1667_rk
   real(rk),parameter :: mgPerg = 1000_rk

contains

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_om_pool),    intent(inout), target :: self
   integer,                     intent(in)            :: configunit
   
   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer  :: i_mac
   character(len=64)   :: index

   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   !ORGANIC MATTER IN WATER COLUMN----------------------------------------------------------------------------------------------------------------------------------------------------------------------------   
   call self%get_parameter(self%cExtSp,            'cExtSp',       'm2/gDW',      'specific extinction factor for OM',                         default=0.15_rk                                         )
   call self%get_parameter(self%cVSet,             'cVSet',        'm/d',         'maximum settling rate of OM',                               default=-0.3_rk,   scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%qTrans,            'qTrans',       '-',           'vert. trans. method: 0=no trans.; 1=constant)',             default=1                                               )
   ! bio-transformation (aka mineralization) parameters------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cThetaMinW,        'cThetaMinW',   '1/e^*C',      'temperature coefficient of biotransformation in water',     default=1.02_rk                                         )
   call self%get_parameter(self%kDMinW,            'kDMinW',       '1/d',         'bio-transform. in water constant of OM-DW at 20*C',         default=0.001_rk,  scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%kNMinW,            'kNMinW',       '1/d',         'bio-transform. in water constant of OM-N at 20*C',          default=0.01_rk,   scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%kPMinW,            'kPMinW',       '1/d',         'bio-transform. in water constant of OM-P at 20*C',          default=0.01_rk,   scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%hO2BOD,            'hO2BOD',       'mgO2/l',      'half saturation oxygen conc. for BOD',                      default=1.0_rk                                          )
   call self%get_parameter(self%hNO3DenitW,        'hNO3DenitW',   'mgN/l',       'quadratic half saturation NO3 conc. for denitrification',   default=1.0_rk                                          )
   call self%get_parameter(self%NO3PerCW,          'NO3PerCW',     'mol/mol',     'denitrified NO3 per C mineralised',                         default=1.0_rk                                          )
   ! photo-transformation parameters-------------------------------------------------------------------------------------------------------------------------------------------------------------------
   ! tka: cOptCross parameter value not yet converted  (20/2/2024)
   !call self%get_parameter(self%cOptCross,        'cOptCross',    'm2/mg DOM',   'optical cross section of OM',                               default=0.00_rk,   scale_factor=1.0_rk/secs_pr_day      )
   !call self%get_parameter(self%cQuantYield,      'cQuantYield',  '-',           'quantum yield',                                             default=0.1_rk,    scale_factor=1.0_rk/secs_pr_day      )
   !call self%get_parameter(self%fPAR,             'fPAR',         '-',           'PAR fraction',                                              default=0.45_rk,   scale_factor=1.0_rk/secs_pr_day      )
   !call self%get_parameter(self%ePAR,             'ePAR',         'J/mol',       'energy of PAR photons',                                     default=240800_rk, scale_factor=1.0_rk/secs_pr_day      )
   ! aggregation parameters----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   !call self%get_parameter(self%kFloc,            'kFloc',        '1/d',         'flocculation rate of OM',                                   default=0.01_rk,   scale_factor=1.0_rk/secs_pr_day      )
   !ORGANIC MATTER IN SEDIMENT-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   ! bio-transformation (aka mineralization) parameters------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cThetaMinS,    'cThetaMinS',       '1/e^*C',      'temperature coefficient of biotransformation in sediment',  default=1.02_rk                                         )
   call self%get_parameter(self%kDMinS,        'kDMinS',           '1/d',         'bio-transform. in sediment constant of OM-DW at 20*C',      default=0.001_rk,  scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%kNMinS,        'kNMinS',           '1/d',         'bio-transform. in sediment constant of OM-N at 20*C',       default=0.01_rk,   scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%kPMinS,        'kPMinS',           '1/d',         'bio-transform. in sediment constant of OM-P at 20*C',       default=0.01_rk,   scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%lTransPV,      'lTransPV',         '-',           'bio-transform. target to be projected to water',            default=.false.                                         )
   call self%get_parameter(self%lPOMtoDOM,     'lPOMtoDOM',        '-',           'toggle POM to DOM transformation',                          default=.false.                                         )
   call self%get_parameter(self%lRefrpool,     'lRefrpool',        '-',           'toggle bio-transform. dependent on oxic sediment fraction', default=.false.                                         )
   call self%get_parameter(self%lTransDWtarget,'lTransDWtarget',   '-',           'toggle DW bio-transformation target',                       default=.true.                                         )
   ! refractory fraction from bio-transformation
   call self%get_parameter(self%fRefrDWS,      'fRefrDWS',         '-',           'refractory fraction of sediment DW OM',                     default=0.0_rk                                          )
   call self%get_parameter(self%fRefrNutS,     'fRefrNutS',        '-',           'refractory fraction of sediment N and P OM',                default=0.0_rk                                          )
   call self%get_parameter(self%lRefrPV,       'lRefrPV',          '-',           'refractory fraction to be projected to water',              default=.true.                                          )
   ! diagnostic  parameter-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,   'diagnostics',      '-',           'toggle diagnostic output',                                  default=.false.                                         )
      
   !REGISTER MODEL VARIABLES, DEPENDENCIES & COUPLINGS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! state variables-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sDW,     'sDW',       'gDW/m3', 'water column DW',initial_value=0.5_rk,    minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.        )
   call self%register_state_variable(self%id_sPW,     'sPW',       'gP/m3',  'water column P', initial_value=0.005_rk,  minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.        )
   call self%register_state_variable(self%id_sNW,     'sNW',       'gN/m3',  'water column N', initial_value=0.05_rk,   minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.        )
   call self%register_state_variable(self%id_sCW,     'sCW',       'gC/m3',  'water column C', initial_value=0.20_rk,   minimum=0.0_rk, vertical_movement= self%cVSet, no_river_dilution=.TRUE.        )
   if (self%qTrans == 0) then
       call self%set_variable_property(self%id_sDW,   'disable_transport',   .true.                                                                                                                    )   
       call self%set_variable_property(self%id_sNW,   'disable_transport',   .true.                                                                                                                    )
       call self%set_variable_property(self%id_sPW,   'disable_transport',   .true.                                                                                                                    )
       call self%set_variable_property(self%id_sCW,   'disable_transport',   .true.                                                                                                                    )
   endif
   call self%register_state_variable(self%id_sDS,     'sDS',       'gDW/m2', 'sediment DW',    initial_value=0.001_rk,  minimum=0.0_rk                                                                 )
   call self%register_state_variable(self%id_sPS,     'sPS',       'gP/m2',  'sediment P',     initial_value=0.00001_rk,minimum=0.0_rk                                                                 )
   call self%register_state_variable(self%id_sNS,     'sNS',       'gN/m2',  'sediment N',     initial_value=0.0001_rk, minimum=0.0_rk                                                                 )
   call self%register_state_variable(self%id_sCS,     'sCS',       'gC/m2',  'sediment C',     initial_value=0.0004_rk, minimum=0.0_rk                                                                 )
   call self%register_state_variable(self%id_sDS_PV,  'sDS_PV',    'gDW/m2', 'sediment DW PV', initial_value=0.001_rk,  minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.     )
   call self%register_state_variable(self%id_sPS_PV,  'sPS_PV',    'gP/m2',  'sediment P  PV', initial_value=0.00001_rk,minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.     )
   call self%register_state_variable(self%id_sNS_PV,  'sNS_PV',    'gN/m2',  'sediment N  PV', initial_value=0.0001_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.     )
   call self%register_state_variable(self%id_sCS_PV,  'sCS_PV',    'gC/m2',  'sediment C  PV', initial_value=0.0004_rk, minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.     )
   call self%set_variable_property(self%id_sDS_PV,    'disable_transport',   .true.                                                                                                                    )   
   call self%set_variable_property(self%id_sNS_PV,    'disable_transport',   .true.                                                                                                                    )
   call self%set_variable_property(self%id_sPS_PV,    'disable_transport',   .true.                                                                                                                    )
   call self%set_variable_property(self%id_sCS_PV,    'disable_transport',   .true.                                                                                                                    )
   ! register diagnostic variables---------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_rPDW,            'rPDW',           '-',     'P/D ratio water',                output=output_instantaneous,source=source_do                           )
   call self%register_diagnostic_variable(self%id_rNDW,            'rNDW',           '-',     'N/D ratio water',                output=output_instantaneous,source=source_do                           )
   call self%register_diagnostic_variable(self%id_rCDW,            'rCDW',           '-',     'C/D ratio water',                output=output_instantaneous,source=source_do                           )
   call self%register_diagnostic_variable(self%id_wCMin,           'wCMin',          '-',     'C bio-transformation in water',  output=output_instantaneous,source=source_do                           )
   call self%register_diagnostic_variable(self%id_ext,             'extinction',     '-',     'extinction',                     output=output_instantaneous,source=source_do                           )
   call self%register_diagnostic_variable(self%id_rPDS,            'rPDS',           '-',     'P/D ratio sediment',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_rNDS,            'rNDS',           '-',     'N/D ratio sediment',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_rCDS,            'rCDS',           '-',     'C/D ratio sediment',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   ! Register diagnostic process output----------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_tDPOMS,          'tDPOMS',         'g/m2/s','ROC DW OM pool in sediment',           output=output_instantaneous,source=source_do_bottom, domain=domain_bottom) ! tka 17/4: use for burial ROC
   if (self%lRefrpool) then
       call self%register_horizontal_dependency(self%id_afOxySed,  'afOxySed',       'm/m',   'fraction of aerobic sediment'                                                                          )
   endif    
   call self%register_diagnostic_variable(self%id_tDTrans,         'tDTrans',        'g/m2/s','rate DW biotrans. minus refraction',   output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tCTrans,         'tCTrans',        'g/m2/s','rate C biotrans. minus refraction',    output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   if (self%diagnostics) then
       ! water 
       call self%register_diagnostic_variable(self%id_wDMin,       'wDMin',          'g/m3/s',  'rate D OM bio-transform. in water',  output=output_instantaneous                                     )
       call self%register_diagnostic_variable(self%id_wNMin,       'wNMin',          'g/m3/s',  'rate N OM bio-transform. in water',  output=output_instantaneous                                     )
       call self%register_diagnostic_variable(self%id_wPMin,       'wPMin',          'g/m3/s',  'rate P OM bio-transform. in water',  output=output_instantaneous                                     )
       call self%register_diagnostic_variable(self%id_wNDenitW,    'wNDenitW',       'g/m3/s',  'rate denitrification in water',      output=output_instantaneous                                     )
       call self%register_diagnostic_variable(self%id_wO2Min,      'wO2Min',         'g/m3/s',  'rate O2 cons. by OM biotransformation in water',  output=output_instantaneous                        )
       ! sediment
       !call self%register_diagnostic_variable(self%id_wO2Prod,    'wO2Prod',        'g/m3/s','rate O2 production',                   output=output_instantaneous,source=source_do                    )
       call self%register_diagnostic_variable(self%id_tDMin,       'tDMin',          'g/m2/s',  'rate DW biotransform. in sediment',  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNMin,       'tNMin',          'g/m2/s',  'rate N biotransform. in sediment',   output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPMin,       'tPMin',          'g/m2/s',  'rate P biotransform. in sediment',   output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCMin,       'tCMin',          'g/m2/s',  'rate C biotransform. in sediment',   output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       !call self%register_diagnostic_variable(self%id_tDTrans,     'tDTrans',        'g/m2/s',  'rate DW biotrans. minus refraction', output=output_instantaneous,source=source_do                    )
       call self%register_diagnostic_variable(self%id_tNTrans,     'tNTrans',        'g/m2/s',  'rate N biotrans. minus refraction',  output=output_instantaneous,source=source_do                    )
       call self%register_diagnostic_variable(self%id_tPTrans,     'tPTrans',        'g/m2/s',  'rate P biotrans. minus refraction',  output=output_instantaneous,source=source_do                    )
       if (max(self%fRefrDWS, self%fRefrNutS) /= 0) then                                                                                                                                                
          call self%register_diagnostic_variable(self%id_tDRefr,   'tDRefr',         'g/m2/s',  'rate DW refraction',                 output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
          call self%register_diagnostic_variable(self%id_tNRefr,   'tNRefr',         'g/m2/s',  'rate N refraction',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
          call self%register_diagnostic_variable(self%id_tPRefr,   'tPRefr',         'g/m2/s',  'rate P refraction',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
          call self%register_diagnostic_variable(self%id_tCRefr,   'tCRefr',         'g/m2/s',  'rate C refraction',                  output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
          if (self%lRefrPV) then
             call self%register_diagnostic_variable(self%id_tDRefr_PV, 'tDRefr_PV',  'g/m3/s',  'rate DW refraction pelagic mirror',  output=output_instantaneous,source=source_do                    )
             call self%register_diagnostic_variable(self%id_tNRefr_PV, 'tNRefr_PV',  'g/m3/s',  'rate N refraction pelagic mirror',   output=output_instantaneous,source=source_do                    )
             call self%register_diagnostic_variable(self%id_tPRefr_PV, 'tPRefr_PV',  'g/m3/s',  'rate P refraction pelagic mirror',   output=output_instantaneous,source=source_do                    )
             call self%register_diagnostic_variable(self%id_tCRefr_PV, 'tCRefr_PV',  'g/m3/s',  'rate C refraction pelagic mirror',   output=output_instantaneous,source=source_do                    )
          endif
       endif  
   endif
   ! register contribution of state to global aggregate variables--------------------------------------------------------------------------------------------------------------------------------------
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totN',aggregate_variable=.true.),      self%id_sNW)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totP',aggregate_variable=.true.),      self%id_sPW)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totC',aggregate_variable=.true.),      self%id_sCW)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totSusPar',aggregate_variable=.true.), self%id_sDW)
   !call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_tDPOMbio',units='gDW/m2/s',aggregate_variable=.true.),self%id_tDS,scale_factor=1._rk) ! tka: not functioning
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_wCMin',units='gC/m3/s',aggregate_variable=.true.),self%id_wCMin,scale_factor=1._rk)
   ! register state variables dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   ! water column
   ! bio_transformation
   if (self%lTransDWtarget) then
       call self%register_state_dependency(self%id_DTransW,         'DW_transformation_water',      'g/m3',            'DW biotransformation target water')
       call self%register_state_dependency(self%id_CTransW,         'C_transformation_water',       'g/m3',            'C biotransformation target water')
   endif                                                            
   call self%register_state_dependency(self%id_NTransW,             'N_transformation_water',       'g/m3',            'N biotransformation target water')
   call self%register_state_dependency(self%id_PTransW,             'P_transformation_water',       'g/m3',            'P biotransformation target water')
   call self%register_state_dependency(self%id_O2poolW,             'oxygen_pool_water',            'g/m3',            'oxygen_pool_water')
   call self%register_state_dependency(self%id_NO3poolW,            'NO3_pool_water',               'g/m3',            'NO3 pool water')
   ! photo_transformation                                           
   !call self%register_state_dependency(self%id_DPhotoW,             'DW_phototransform_water',      'g/m3',            'DW phototransformation water')
   !call self%register_state_dependency(self%id_NPhotoW,             'N_phototransform_water',       'g/m3',            'N phototransformation water')
   !call self%register_state_dependency(self%id_PPhotoW,             'P_phototransform_water',       'g/m3',            'P phototransformation water')   
   ! aggregation // floculation                                     
   !call self%register_state_dependency(self%id_DAggW,               'DW_aggregation_water',         'g/m3',            'DW aggregation water')
   !call self%register_state_dependency(self%id_NAggW,               'N_aggregation_water',          'g/m3',            'N aggregation water')
   !call self%register_state_dependency(self%id_PAggW,               'P_aggregation_water',          'g/m3',            'P aggregation water')  
   ! sediment                                                       
   ! bio_transformation                                             
   if (self%lTransDWtarget) then                                    
       call self%register_state_dependency(self%id_DTransS,         'DW_transformation_sediment',    'g/m2',            'DW biotransformation target sediment')
       call self%register_state_dependency(self%id_CTransS,         'C_transformation_sediment',     'g/m2',            'C biotransformation target sediment')   
   endif                                                            
   call self%register_state_dependency(self%id_NTransS,             'N_transformation_sediment',     'g/m2',            'N biotransformation target sediment')
   call self%register_state_dependency(self%id_PTransS,             'P_transformation_sediment',     'g/m2',            'P biotransformation target sediment')   
   if (self%lTransPV) then                                          
       call self%register_state_dependency(self%id_DTransS_PV,      'DW_transformation_sediment_PV', 'g/m3',            'DW biotransformation sediment pelagic mirror')
       call self%register_state_dependency(self%id_NTransS_PV,      'N_transformation_sediment_PV',  'g/m3',            'N biotransformation sediment pelagic mirror')
       call self%register_state_dependency(self%id_PTransS_PV,      'P_transformation_sediment_PV',  'g/m3',            'P biotransformation sediment pelagic mirror')
       call self%register_state_dependency(self%id_CTransS_PV,      'C_transformation_sediment_PV',  'g/m3',            'C biotransformation sediment pelagic mirror')
   endif                                                            
   ! refractory fraction (from biotransformation)                   
   if (max(self%fRefrDWS, self%fRefrNutS) /= 0) then                
       call self%register_state_dependency(self%id_DRefrS,          'DW_refractory_sediment',        'g/m2',            'DW refractory target sediment')
       call self%register_state_dependency(self%id_NRefrS,          'N_refractory_sediment',         'g/m2',            'N refractory target sediment')
       call self%register_state_dependency(self%id_PRefrS,          'P_refractory_sediment',         'g/m2',            'P refractory target sediment')
       call self%register_state_dependency(self%id_CRefrS,          'C_refractory_sediment',         'g/m2',            'C refractory target sediment')
       if (self%lTransPV) then
           call self%register_state_dependency(self%id_DRefrS_PV,   'DW_refractory_sediment_PV',     'g/m3',            'DW refractory target sediment pelagic mirror')
           call self%register_state_dependency(self%id_NRefrS_PV,   'N_refractory_sediment_PV',      'g/m3',            'N refractory target sediment pelagic mirror')
           call self%register_state_dependency(self%id_PRefrS_PV,   'P_refractory_sediment_PV',      'g/m3',            'P refractory target sediment pelagic mirror')
           call self%register_state_dependency(self%id_CRefrS_PV,   'C_refractory_sediment_PV',      'g/m3',            'C refractory target sediment pelagic mirror')
       endif
   endif
   ! register diagnostic dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   !call self%register_dependency(self%id_afCovSurfVeg,type_bulk_standard_variable(name='total_afCovSurfVeg',units='-')) ! tka: to be used in photo-transformation?
   !call self%register_dependency(self%id_tDResusDead,     'base_resuspension_rate',          '-',              'base resuspension rate')
   !call self%register_dependency(self%id_aFunTauTmSet,    'aFunTauTmSet',                    '-',              'basic settling rate')
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')
   ! register environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_uTm, standard_variables%temperature)
   !call self%register_dependency(self%id_dz,  standard_variables%cell_thickness)
   !call self%register_dependency(self%id_extc,standard_variables%attenuation_coefficient_of_photosynthetic_radiative_flux)
   !all self%register_dependency(self%id_Day, standard_variables%number_of_days_since_start_of_the_year)
   !call self%register_dependency(self%id_lat, standard_variables%latitude)
   !call self%register_dependency(self%id_par, standard_variables%downwelling_photosynthetic_radiative_flux)
   !call self%register_dependency(self%id_meanpar,temporal_mean(self%id_par,period=86400._rk,resolution=3600._rk,missing_value=0.0_rk))
   !call self%register_dependency(self%id_swf,  standard_variables%downwelling_shortwave_flux) ! for photo-transformation
   return

end subroutine initialize
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO (PELAGIC)                                                                                                                                                                       §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do(self,_ARGUMENTS_DO_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_om_pool), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_

   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)   :: uTm, sDW, sPW, sNW, sCW, rPDW, rNDW, rCDW, uFunTmMinW ! afCovSurfVeg
   real(rk)   :: wDMin, wPMin, wNMin, wCMin, aCorO2BOD, wO2Min, wDDenitW, wNDenitW, sNO3W, sO2W ! cCPerDWS 

   _LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
        ! 1.1 retrieve environmental dependencies                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        _GET_(self%id_uTm,uTm)                                                                                      !
        !_GET_(self%id_afCovSurfVeg,afCovSurfVeg)                                                                    ! tka: to be used in photo-transformation?
        !afCovSurfVeg = min(1.0_rk,afCovSurfVeg)                                                                     ! tka: to be used in photo-transformation?
        !===========================================================================================================!
        ! 1.2 retrieve state variables                                                                              !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        _GET_(self%id_sDW,sDW)                                                                                      !
        _GET_(self%id_sPW,sPW)                                                                                      !
        _GET_(self%id_sNW,sNW)                                                                                      !
        _GET_(self%id_sCW,sCW)                                                                                      !
        rPDW = sPW /(sDW+NearZero)                                                                                  !
        rNDW = sNW /(sDW+NearZero)                                                                                  !
        rCDW = sCW /(sDW+NearZero)                                                                                  !
        _GET_(self%id_NO3poolW,sNO3W)                                                                               !
        _GET_(self%id_O2poolW,sO2W)                                                                                 !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. calculate transformations                                                                                  !
   !================================================================================================================!
      ! 2.1 temperature functions                                                                                   !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      uFunTmMinW = uFunTmArrh(uTm,self%cThetaMinW)                                                                  ! bio-transformation temperature function
      !=============================================================================================================!
      ! 2.2.1 calculate bio-transformation (aka decomposition or remineralization)                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      wDMin = self%kDMinW * uFunTmMinW * sDW                                                                        ! decomposition
      wPMin = self%kPMinW * uFunTmMinW * sPW                                                                        ! particulate_OM_P mineralization
      wNMin = self%kNMinW * uFunTmMinW * sNW                                                                        ! particulate_OM_N mineralization
      wCMin = self%kDMinW * uFunTmMinW * sCW                                                                        ! particulate_OM_C mineralization
      !=============================================================================================================!
      ! 2.2.2 calculate oxygen consumption and denitrification                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      aCorO2BOD = sO2W / (self%hO2BOD + sO2W)                                                                       ! correction_of_O2_demand_in_water_at_low_oxygen_conc.
      wO2Min = molO2molC * rCDW * aCorO2BOD * wDMin                                                                 ! O2 consumption for biotransformation
      wDDenitW = sNO3W*sNO3W/(self%hNO3DenitW*self%hNO3DenitW+sNO3W*sNO3W)*(1.0_rk-aCorO2BOD)*wDMin                 ! mineralization flux by denitrification
      wNDenitW=self%NO3PerCW*molNmolC*rCDW*wDDenitW                                                                 ! Denitrification flux
      !=============================================================================================================!
      ! 2.3 calculate photo-transformation (from DOMCAST)                                                           !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      ! tka: not implemented yet,                                                                                   !
      ! from DOMCAST // FABM                                                                                        !
      ! include shading from surface vegetation: (1.0_rk - afCovSurfVeg) as in phytoplankton?                       !
      ! wDPhoto = self%cOptCross * self%cQuantYield * self%fPAR * 1._rk/self%ePAR * swfz                            ! photo-transformation
      ! wNPhoto = wDPhoto * rNDW                                                                                    ! photo-transformation
      ! wPPhoto = wDPhoto * rPDW                                                                                    ! photo-transformation
      !=============================================================================================================!
      ! 2.4 calculate aggregations                                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      ! tka: aggregation due to flocculation implemented, but not yet tested                                        !
      !wDAggr = self%kFlocW * sDW                                                                                   ! aggregations
      !wNAggr = wDAggr * rNDW                                                                                       ! aggregations
      !wPAggr = wDAggr * rPDW                                                                                       ! aggregations
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 3. update variables                                                                                            !
   !================================================================================================================!
      ! 3.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      ! bio-transformation
      _SET_ODE_(self%id_sDW,-wDMin)                                                                                 !
      _SET_ODE_(self%id_sNW,-wNMin)                                                                                 !
      _SET_ODE_(self%id_sPW,-wPMin)                                                                                 !
      _SET_ODE_(self%id_sCW,-wCMin)                                                                                 !
      !=============================================================================================================!
      ! 3.2 update local diagnostic variables                                                                       !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_DIAGNOSTIC_(self%id_rPDW,rPDW)                                                                           !
      _SET_DIAGNOSTIC_(self%id_rNDW,rNDW)                                                                           !
      _SET_DIAGNOSTIC_(self%id_rCDW,rCDW)                                                                           !
      _SET_DIAGNOSTIC_(self%id_wCMin,wCMin)                                                                         !
      !=============================================================================================================!
      ! 3.3 update external state variables                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      ! Bio-transformation                                                                                          !
      if (self%lTransDWtarget) then                                                                                 !
         _SET_ODE_(self%id_DTransW,wDMin)                                                                           !
         _SET_ODE_(self%id_CTransW,wCMin)                                                                           !
      endif                                                                                                         !
      _SET_ODE_(self%id_NTransW,wNMin)                                                                              !
      _SET_ODE_(self%id_PTransW,wPMin)                                                                              !
      _SET_ODE_(self%id_O2poolW,-wO2Min)                                                                            !
      _SET_ODE_(self%id_NO3poolW,-wNDenitW)                                                                         !
      ! Photo-transformation                                                                                        !
      !_SET_ODE_(self%id_DPhotoW,wDPhoto)                                                                           !
      !_SET_ODE_(self%id_NPhotoW,wNPhoto)                                                                           !
      !_SET_ODE_(self%id_PPhotoW,wPPhoto)                                                                           !
      ! Aggregation                                                                                                 !
      !_SET_ODE_(self%id_DAggW,wDAggr)                                                                              !
      !_SET_ODE_(self%id_NAggW,wNAggr)                                                                              !
      !_SET_ODE_(self%id_PAggW,wPAggr)                                                                              !
      !=============================================================================================================!
      ! 3.4 update diagnostic output processes                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
        _SET_DIAGNOSTIC_(self%id_wDMin,     wDMin)                                                                  !
        _SET_DIAGNOSTIC_(self%id_wNMin,     wNMin)                                                                  !
        _SET_DIAGNOSTIC_(self%id_wPMin,     wPMin)                                                                  !
        _SET_DIAGNOSTIC_(self%id_wNDenitW,  wNDenitW)                                                               !
        _SET_DIAGNOSTIC_(self%id_wO2Min,    wO2Min)                                                                 !
      endif                                                                                                         !
   !================================================================================================================!
   _LOOP_END_ !!! END OF MODEL CODE::
end subroutine do

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO BOTTOM                                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_om_pool), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)   :: sDS, sPS, sNS, sCS, uTm, rPDS, rNDS, rCDS, uFunTmMinS, tDMin, tNMin, tPMin, tCMin, tDS, tNS, tPS, tCS 
   real(rk)   :: tDTrans, tNTrans, tPTrans, tCTrans, tDRefr, tNRefr, tPRefr, tCRefr
   real(rk)   :: bot_pel_conv, afOxySed

   _HORIZONTAL_LOOP_BEGIN_  !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
        ! 1.1 retrieve environmental dependencies                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        _GET_(self%id_uTm,uTm)                                                                                      !
        !===========================================================================================================!
        ! 1.2 retrieve state variables, & calc. current local nutrient ratios and relative abundances               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.1 sediment OM state variables                                                                      !
           !--------------------------------------------------------------------------------------------------------!
           _GET_HORIZONTAL_(self%id_sDS,sDS)                                                                        !
           _GET_HORIZONTAL_(self%id_sNS,sNS)                                                                        !
           _GET_HORIZONTAL_(self%id_sPS,sPS)                                                                        !
           _GET_HORIZONTAL_(self%id_sCS,sCS)                                                                        !
           rPDS = sPS /(sDS+NearZero)                                                                               !
           rNDS = sNS /(sDS+NearZero)                                                                               !
           rCDS = sCS /(sDS+NearZero)                                                                               !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!                                      
   !  2. calculate biotransformation                                                                                !                                          
   !================================================================================================================!                                                     
        ! 2.1 temperature function                                                                                  !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                        
        uFunTmMinS = uFunTmArrh(uTm,self%cThetaMinS)                                                                ! bio-transformation temperature function
        !===========================================================================================================!
        ! 2.2 calculate bio-transformation (aka decomposition or remineralization)                                  !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        if (self%lRefrpool) then                                                                                    ! bio-transformation dependent on oxic sediment fraction
            tDMin = self%kDMinS * uFunTmMinS * sDS * afOxySed                                                       !    calculate DW bio-transform. of refractory OM pool
            tNMin = self%kNMinS * uFunTmMinS * sNS * afOxySed                                                       !    calculate N bio-transform. of refractory OM pool
            tPMin = self%kPMinS * uFunTmMinS * sPS * afOxySed                                                       !    calculate P bio-transform. of refractory OM pool
            tCMin = self%kDMinS * uFunTmMinS * sCS * afOxySed                                                       !    calculate C bio-transform. of refractory OM pool
        else                                                                                                        ! bio-transformation contributing to sediment oxygen demand
            tDMin = self%kDMinS * uFunTmMinS * sDS                                                                  !    calculate DW bio-transform. of OM pool
            tNMin = self%kNMinS * uFunTmMinS * sNS                                                                  !    calculate N bio-transform. of OM pool
            tPMin = self%kPMinS * uFunTmMinS * sPS                                                                  !    calculate P bio-transform. of OM pool
            tCMin = self%kDMinS * uFunTmMinS * sCS                                                                  !    calculate C bio-transform. of OM pool
        endif                                                                                                       !
        !===========================================================================================================!
        ! 2.2 calculate oxygen consumption due to bio-transformation                                                !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        !tSOD = (molO2molC * self%cCPerDWS * (1.0_rk-self%fRefrDW) * tDMin                                          ! sediment oxygen demand due to biotransform.
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 3. final flux calculations                                                                                     !
   !================================================================================================================!
        ! 3.1 final sediment OM rate of change                                                                      !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDS = -tDMin                                                                                                ! calculate final ROC in DW
        tNS = -tNMin                                                                                                ! calculate final ROC in N
        tPS = -tPMin                                                                                                ! calculate final ROC in P
        tCS = -tCMin                                                                                                ! calculate final ROC in P
        !===========================================================================================================!
        ! 3.2 final biotransformation target ROC                                                                    !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDTrans = (1.0_rk - self%fRefrDWS) * tDMin                                                                  ! calculate final ROC in biotransformation_target DW
        tNTrans = (1.0_rk - self%fRefrNutS) * tNMin                                                                 ! calculate final ROC in biotransformation_target N
        tPTrans = (1.0_rk - self%fRefrNutS) * tPMin                                                                 ! calculate final ROC in biotransformation_target P 
        ! tka 12/4: for use in SOD code                                                                             !
        tCTrans = (1.0_rk - self%fRefrDWS) * tCMin                                                                  ! calculate final ROC in biotransformation_target C
        !===========================================================================================================!
        ! 3.3 final refractory target of bio-transformation ROC                                                     !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDRefr = self%fRefrDWS * tDMin                                                                              ! calculate final ROC in refractory_target DW
        tNRefr = self%fRefrNutS * tNMin                                                                             ! calculate final ROC in refractory_target N
        tPRefr = self%fRefrNutS * tPMin                                                                             ! calculate final ROC in refractory_target P
        tCRefr = self%fRefrNutS * tCMin                                                                             ! calculate final ROC in refractory_target C
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. update model variables                                                                                      !
   !================================================================================================================!
      ! 4.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
            ! 4.1.1 update sediment phytoplankton                                                                   !
            !-------------------------------------------------------------------------------------------------------!
            _SET_BOTTOM_ODE_(self%id_sDS, tDS)                                                                      ! update sediment OM DW ODE
            _SET_BOTTOM_ODE_(self%id_sPS, tPS)                                                                      ! update sediment OM P ODE
            _SET_BOTTOM_ODE_(self%id_sNS, tNS)                                                                      ! update sediment OM N ODE
            _SET_BOTTOM_ODE_(self%id_sCS, tCS)                                                                      ! update sediment OM C ODE
            _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)                                                     ! 
            _SET_BOTTOM_EXCHANGE_(self%id_sDS_PV, tDS*bot_pel_conv)                                                 ! update projected sediment OM DW ODE
            _SET_BOTTOM_EXCHANGE_(self%id_sNS_PV, tNS*bot_pel_conv)                                                 ! update projected sediment OM N ODE
            _SET_BOTTOM_EXCHANGE_(self%id_sPS_PV, tPS*bot_pel_conv)                                                 ! update projected sediment OM P ODE
            _SET_BOTTOM_EXCHANGE_(self%id_sCS_PV, tCS*bot_pel_conv)                                                 ! update projected sediment OM C ODE
      !=============================================================================================================!
      ! 4.2 update external abiotic state variables                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%lTransDWtarget) then                                                                                 !
          _SET_BOTTOM_ODE_(self%id_DTransS,            tDTrans)                                                     ! update ODE for DW bio-transformation target
          _SET_BOTTOM_ODE_(self%id_CTransS,            tCTrans)                                                     ! update ODE for C bio-transformation target
      endif                                                                                                         !
      _SET_BOTTOM_ODE_(self%id_NTransS,                tNTrans)                                                     ! update ODE for N bio-transformation target
      _SET_BOTTOM_ODE_(self%id_PTransS,                tPTrans)                                                     ! update ODE for P bio-transformation target
      if (self%lTransPV) then                                                                                       !
          _SET_BOTTOM_EXCHANGE_(self%id_DTransS_PV,    tDTrans*bot_pel_conv)                                        ! update ODE for DW bio-transf. target pelagic mirror
          _SET_BOTTOM_EXCHANGE_(self%id_NTransS_PV,    tNTrans*bot_pel_conv)                                        ! update ODE for N bio-transf. target pelagic mirror
          _SET_BOTTOM_EXCHANGE_(self%id_PTransS_PV,    tPTrans*bot_pel_conv)                                        ! update ODE for P bio-transf. target pelagic mirror
          _SET_BOTTOM_EXCHANGE_(self%id_CTransS_PV,    tCTrans*bot_pel_conv)                                        ! update ODE for C bio-transf. target pelagic mirror
      endif                                                                                                         !
      if (max(self%fRefrDWS, self%fRefrNutS) /= 0) then                                                             !
          _SET_BOTTOM_ODE_(self%id_DRefrS,             tDRefr)                                                      ! update ODE for DW refractory target
          _SET_BOTTOM_ODE_(self%id_NRefrS,             tNRefr)                                                      ! update ODE for N refractory target
          _SET_BOTTOM_ODE_(self%id_PRefrS,             tPRefr)                                                      ! update ODE for P refractory target
          _SET_BOTTOM_ODE_(self%id_CRefrS,             tCRefr)                                                      ! update ODE for C refractory target    
          if (self%lRefrPV) then                                                                                    !
              _SET_BOTTOM_EXCHANGE_(self%id_DRefrS_PV, tDRefr*bot_pel_conv)                                         ! update ODE for DW refractory target pelagic mirror
              _SET_BOTTOM_EXCHANGE_(self%id_NRefrS_PV, tNRefr*bot_pel_conv)                                         ! update ODE for N refractory target pelagic mirror
              _SET_BOTTOM_EXCHANGE_(self%id_PRefrS_PV, tPRefr*bot_pel_conv)                                         ! update ODE for P refractory target pelagic mirror
              _SET_BOTTOM_EXCHANGE_(self%id_CRefrS_PV, tCRefr*bot_pel_conv)                                         ! update ODE for C refractory target pelagic mirror
          endif                                                                                                     !
      endif                                                                                                         !
      !=============================================================================================================!
      ! 4.3 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_rPDS,       rPDS)                                                         ! update diagn. P:DW ratio
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_rNDS,       rNDS)                                                         ! update diagn. N:DW ratio
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_rCDS,       rCDS)                                                         ! update diagn. C:DW ratio
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDTrans,    tDTrans)                                                      ! update diagn. DW transformation
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCTrans,    tCTrans)                                                      ! update diagn. C transformation
      if (self%lPOMtoDOM) then                                                                                      !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDPOMS, tDS)                                                          ! update diagn. for ROC in DW
      else                                                                                                          !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDPOMS, 0.0_rk)                                                       !
      endif                                                                                                         !
      !=============================================================================================================!
      ! 4.4 update diagnostic output processes                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDMin,      tDMin)                                                     !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNMin,      tNMin)                                                     !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPMin,      tPMin)                                                     !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCMin,      tCMin)                                                     !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNTrans,    tNTrans)                                                   !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPTrans,    tPTrans)                                                   !
         if (max(self%fRefrDWS, self%fRefrNutS) /= 0) then                                                          !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDRefr, tDRefr)                                                    !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNRefr, tNRefr)                                                    !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPRefr, tPRefr)                                                    !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCRefr, tCRefr)                                                    !
         endif                                                                                                      !
      endif                                                                                                         !
   !================================================================================================================!
   _HORIZONTAL_LOOP_END_ !!! END OF MODEL CODE::
end subroutine do_bottom

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: GET LIGHT EXTINCTION                                                                                                                                                               §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine get_light_extinction(self,_ARGUMENTS_GET_EXTINCTION_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_om_pool), intent(in) :: self
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
end module wet_om_pool
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------

