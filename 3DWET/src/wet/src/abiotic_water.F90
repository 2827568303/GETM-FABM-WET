#include "fabm_driver.h"
!
! MODULE: ABIOTIC WATER                                                                                                                                                                          
!
   module wet_abiotic_water
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_standard_variables
   use fabm_particle
   use wet_utility, ONLY: uFunTmArrh, uFunO2Sat
   implicit none
   private
   
   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public :: type_wet_abiotic_water
      ! local state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                 :: id_sDIMW,id_sSiPaW
      type (type_state_variable_id)                 :: id_sPO4W,id_sPAIMW,id_sNH4W,id_sNO3W
      type (type_state_variable_id)                 :: id_sSiO2W,id_sO2W
      ! diagnostic variables for local output--------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)            :: id_pO2Sat
      type (type_diagnostic_variable_id)            :: id_extIM,id_extPOM
      type (type_horizontal_diagnostic_variable_id) :: id_wind,id_tO2Aer
      type (type_diagnostic_variable_id)            :: id_BTdummy, id_TMdummy, id_aCovVegdummy, id_aDSubVegdummy, id_afCovSurfVegdummy, id_chladummy
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)            :: id_wSiMinPaW, id_wPSorpIMW, id_wNNitrW
      type (type_diagnostic_variable_id)            :: id_wO2NitrW
      ! diagnostic variable for external dependencies:-----------------------------------------------------------------------------------------------------------------------------------------------
      type (type_dependency_id)                     :: id_uTm, id_salt
      type (type_horizontal_dependency_id)          :: id_uVWind
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      logical                                       :: diagnostics
      real(rk)                                      :: cThetaMinSiW, kSiMinPaW, kNitrW, cThetaNitrW
      real(rk)                                      :: cThetaAer, hO2BOD, O2PerNH4W, hO2Nitr, kPSorpW, cRelPAdsDWW, cRelPAdsFeW, fFeDIMW, cRelPAdsAlW, fAlDIMW, fRedMaxW
      real(rk)                                      :: cVSetIM, cVSetSi, cKPAdsOxW, tDDepoIM, tPDepoPO4, tNDepoNH4, tNDepoNO3, cExtSpIM, cDVegMin
      real(rk)                                      :: cNVegMin,cPVegMin

   contains
                                                                                                   
   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure :: initialize
   procedure :: do
   procedure :: get_light_extinction
   procedure :: do_surface

   end type type_wet_abiotic_water

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk),parameter :: molO2molC = 2.6667_rk
   real(rk),parameter :: molO2molN = 2.2857_rk
   real(rk),parameter :: molNmolC = 1.1667_rk

contains

!
! SUBROUTINE: INITIALIZATION                                                                                                                                                                     
!
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_abiotic_water), intent(inout), target  :: self
   integer,                          intent(in)            :: configunit

   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   !call self%get_parameter(self%cCPerDWW,       'cCPerDWW',     'gC/gDW',      'C content of organic matter',                               default=0.4_rk                                          )
   call self%get_parameter(self%cExtSpIM,       'cExtSpIM',     'm2/gDW',      'specific extinction inorganic matter',                      default=0.05_rk                                         )
   call self%get_parameter(self%cKPAdsOxW,      'cKPAdsOxW',    'm3/gP',       'P adsorption affinity at oxidized conditions',              default=0.6_rk                                          )
   call self%get_parameter(self%cRelPAdsAlW,    'cRelPAdsAlW',  'gP/gAl',      'maximum P adsorption per g Al',                             default=0.134_rk                                        )
   call self%get_parameter(self%cRelPAdsDWW,    'cRelPAdsDWW',  'gP/gDW',      'maximum P adsorption per g DW',                             default=0.00003_rk                                      )
   call self%get_parameter(self%cRelPAdsFeW,    'cRelPAdsFeW',  'gP/gFe',      'maximum P adsorption per g Fe',                             default=0.0675_rk                                       )
   call self%get_parameter(self%cThetaAer,      'cThetaAer',    '1/e^*C',      'temperature coefficient for reaeration',                    default=1.011_rk                                        )
   call self%get_parameter(self%cThetaNitrW,    'cThetaNitrW',  '1/e^*C',      'temperature coefficient for nitrification',                 default=1.03_rk                                         )
   call self%get_parameter(self%cVSetSi,        'cVSetSi',      'm/d',         'maximum settling rate of Si particulate',                   default=-0.3_rk,   scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%cVSetIM,        'cVSetIM',      'm/d',         'maximum settling rate of inorganic matter',                 default=-1.1_rk,   scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%fAlDIMW,        'fAlDIMW',      'gAl/gDW',     'Al content of inorganic matter',                            default=0.01_rk                                         )
   call self%get_parameter(self%fFeDIMW,        'fFeDIMW',      'gFe/gDW',     'Fe content of inorganic matter',                            default=0.01_rk                                         )
   call self%get_parameter(self%fRedMaxW,       'fRedMaxW',     '-',           'maximum reduction factor of P adsorption affinity',         default=0.9_rk                                          )
   call self%get_parameter(self%hO2BOD,         'hO2BOD',       'mgO2/l',      'half saturation oxygen conc. for BOD',                      default=1.0_rk                                          )
   call self%get_parameter(self%hO2Nitr,        'hO2Nitr',      'mgO2/l',      'half saturation oxygen conc. for nitrification',            default=2.0_rk                                          )
   call self%get_parameter(self%kNitrW,         'kNitrW',       '1/d',         'nitrification rate constant in water at 20*C',              default=0.3_rk,    scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%kPSorpW,        'kPSorpW',      '1/d',         'P adsorption rate constant',                                default=0.05_rk,   scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%O2PerNH4W,      'O2PerNH4W',    'mol/mol',     'used O2 per NH4 nitrified',                                 default=2.0_rk                                          )
   ! mineralization parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cThetaMinSiW,   'cThetaMinSiW', '1/e^*C',      'temperature coefficient of SiO2 mineralization',            default=1.02_rk                                         )
   call self%get_parameter(self%kSiMinPaW,      'kSiMinPaW',    '1/d',         'biodissolution constant of particulate Si to SiO2 at 20*C', default=0.03_rk,   scale_factor=1.0_rk/secs_pr_day      )
   ! deposition  parameters--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%tDDepoIM,       'tDDepoIM',     'g/m2/d',      'inorganic matter deposition',                               default=0.0_rk,    scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%tPDepoPO4,      'tPDepoPO4',    'g/m2/d',      'phosphate deposition',                                      default=0.0_rk,    scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%tNDepoNH4,      'tNDepoNH4',    'g/m2/d',      'ammonium deposition',                                       default=0.0_rk,    scale_factor=1.0_rk/secs_pr_day      )
   call self%get_parameter(self%tNDepoNO3,      'tNDepoNO3',    'g/m2/d',      'nitrate deposition',                                        default=0.0_rk,    scale_factor=1.0_rk/secs_pr_day      )
   ! diagnostic  parameter---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,    'diagnostics',  '-',           'toggle diagnostic output',                                  default=.false.                                         )
   
   !REGISTER MODEL VARIBLES, DEPENDENCIES & COUPLINGS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! dissolved inorganic matter----------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sDIMW,  'sDIMW',  'g/m3','inorganic matter',          initial_value=5.0_rk,   minimum=0.0_rk,vertical_movement=self%cVSetIM, no_river_dilution=.TRUE.)
   ! particulate organic matter----------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sSiPaW, 'sSiPaW', 'g/m3','particulate Si',            initial_value=0.02_rk,  minimum=0.0_rk,vertical_movement=self%cVSetSi, no_river_dilution=.TRUE.)
   ! dissolved nutrients----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sPO4W,  'sPO4W',  'g/m3','phosphate',                 initial_value=0.01_rk,  minimum=0.0_rk,                                no_river_dilution=.TRUE.)
   call self%register_state_variable(self%id_sPAIMW, 'sPAIMW', 'g/m3','IM-adsorbed P',             initial_value=0.0_rk,   minimum=0.0_rk,vertical_movement=self%cVSetIM, no_river_dilution=.TRUE.)
   call self%register_state_variable(self%id_sNH4W,  'sNH4W',  'g/m3','ammonium',                  initial_value=0.1_rk,   minimum=0.0_rk,                                no_river_dilution=.TRUE.)
   call self%register_state_variable(self%id_sNO3W,  'sNO3W',  'g/m3','nitrate',                   initial_value=0.1_rk,   minimum=0.0_rk,                                no_river_dilution=.TRUE.)
   call self%register_state_variable(self%id_sSiO2W, 'sSiO2W', 'g/m3','silica dioxide',            initial_value=3.0_rk,   minimum=0.0_rk,                                no_river_dilution=.TRUE.)
   ! oxygen-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sO2W,   'sO2W',   'g/m3','oxygen',                    initial_value=10.0_rk,  minimum=0.0_rk,                                no_river_dilution=.TRUE.)
   ! Register diagnostic variables -----------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_wind,          'wind',        'm/s',       'windspeed',                              output=output_instantaneous, source=source_do_surface)
   call self%register_diagnostic_variable(self%id_extIM,         'extIM',       '-',         'extIM',                                  output=output_instantaneous) !,source=source_get_light_extinction
   !call self%register_diagnostic_variable(self%id_extPOM,        'extPOM',      '-',         'extPOM',                                 output=output_instantaneous) !,source=source_get_light_extinction
   call self%register_diagnostic_variable(self%id_tO2Aer,        'tO2Aer',      'g/m2/s',    'O2_reareation',                          output=output_instantaneous, source=source_do_surface)
   ! Register diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_pO2Sat,        'pO2Sat',      'pct',       'oxygen saturation',                      output=output_instantaneous)
   if (self%diagnostics) then
     call self%register_diagnostic_variable(self%id_wSiMinPaW,   'wSiMinPaW',   'g/m3/s',    'rate Si particulate mineralization',     output=output_instantaneous)
     call self%register_diagnostic_variable(self%id_wPSorpIMW,   'wPSorpIMW',   'g/m3/s',    'rate P adsorped',                        output=output_instantaneous)
     call self%register_diagnostic_variable(self%id_wNNitrW,     'wNNitrW',     'g/m3/s',    'rate nitrification',                     output=output_instantaneous)
     !call self%register_diagnostic_variable(self%id_wNDenitW,    'wNDenitW',    'g/m3/s',    'rate denitrification',                   output=output_instantaneous) ! tka: moved to om_pool
     call self%register_diagnostic_variable(self%id_wO2NitrW,    'wO2NitrW',    'g/m3/s',    'rate O2 cons. by nitrification',         output=output_instantaneous)
     !call self%register_diagnostic_variable(self%id_wO2MinOMW,   'wO2MinOMW',   'g/m3/s',    'rate O2 cons. by OM biotransformation',  output=output_instantaneous) ! tka: moved to om_pool
   endif 
   
   ! Register contribution of state variables to global aggregate variables-------------------------------------------------------------------------------------------------------------------------
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totN',aggregate_variable=.true.),self%id_sNH4W )
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totN',aggregate_variable=.true.),self%id_sNO3W )
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totP',aggregate_variable=.true.),self%id_sPO4W )
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totP',aggregate_variable=.true.),self%id_sPAIMW)
   ! Register dummy contributions for aggregate variables of modularized modules--------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_BTdummy,                 'BTdummy',   'gDW/m2/d',   'bioturbation dummy',output=output_none) ! for resus_sed, in case there is no bioturbation    
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_bioturbation',units='gDW/m3/d',aggregate_variable=.true.),self%id_BTdummy,scale_factor=1._rk)     
   call self%register_diagnostic_variable(self%id_TMdummy,                 'TMdummy',   'gDW/m2',   'total macrophyte dummy',output=output_none) ! for resus_sed, in case there is no macrophytes
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_macrophyte_biomass',units='gDW/m2',aggregate_variable=.true.),self%id_TMdummy,scale_factor=1._rk)
   
   call self%register_diagnostic_variable(self%id_aDSubVegdummy,           'aDSubVegdummy',   'gDW/m2',   'dummy aDSubVeg',output=output_none) ! for fish, in case there is no macrophytes
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_aDSubVeg',units='gDW/m2',aggregate_variable=.true.),self%id_aDSubVegdummy,scale_factor=1._rk)
   call self%register_diagnostic_variable(self%id_aCovVegdummy,                 'aCovVegdummy',   '%',   'dummy aCovVeg',output=output_none) ! for fish, in case there is no macrophytes
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_aCovVeg',units='%',aggregate_variable=.true.),self%id_aCovVegdummy,scale_factor=1._rk)

   call self%register_diagnostic_variable(self%id_afCovSurfVegdummy,        'afCovSurfVegdummy',   '-',   'dummy afCovSurfVeg',output=output_none) ! for phytoplankton, in case there is no macrophytes
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_afCovSurfVeg',units='-',aggregate_variable=.true.),self%id_afCovSurfVegdummy,scale_factor=1._rk)
   
   call self%register_diagnostic_variable(self%id_chladummy,        'chladummy',   'ug/L',   'dummy chlorophyl a',output=output_none) ! for phytoplankton, in case there is no macrophytes
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_chla',units='ug/L',aggregate_variable=.true.),      self%id_chladummy,scale_factor=1._rk)
   ! register environmental dependencies------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_uTm,   standard_variables%temperature)
   call self%register_dependency(self%id_uVWind,standard_variables%wind_speed)
   call self%register_dependency(self%id_salt,standard_variables%practical_salinity)

   return

end subroutine initialize

!
! SUBROUTINE: DO                                                                                                                                                                                 
!
subroutine do(self,_ARGUMENTS_DO_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_abiotic_water), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)     :: sNH4W, sNO3W, sPO4W, sPAIMW, sSiO2W, sO2W, uTm, salt, uFunTmNitr, aCorO2BOD, aCorO2NitrW, wO2NitrW, wPSorpIMW, aPEqIMW, aPIsoAdsW
   real(rk)     :: wNNitrW, aPAdsMaxW, aKPAdsW, wNAbioNH4W, wNAbioNO3W, wPAbioPO4W, wPAbioAIMW, wDAbioIMW, wSiAbioSiO2W, wO2AbioW, sDIMW, sSiPaW !wCDenitW, wNDenitW,
   real(rk)     :: kSiMinPaW, uFunTmMinPOMW, wSiMinPaW, wDAbioPOMW, wNAbioPOMW, wPAbioPOMW, wSiAbioPaW, uFunTmMinSiW
   real(rk)     :: wO2MinPOMW, wDMinDOMW, wNMinDOMW, wPMinDOMW, wSiMinDOMW, uFunTmMinDOMW, wDAbioDOMW, wNAbioDOMW, wPAbioDOMW, wSiAbioDOMW, cO2Sat, pO2Sat
 
   _LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE:: 
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values and calculate local nutrient ratios                                               !
   !================================================================================================================!
      ! 1.1 retrieve state variables                                                                                !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.1.1 particulate organic matter                                                                         !
         !----------------------------------------------------------------------------------------------------------!
         _GET_(self%id_sSiPaW,sSiPaW)                                                                               !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.1.3 inorganic matter                                                                                   !
         !----------------------------------------------------------------------------------------------------------!
         _GET_(self%id_sPO4W,sPO4W)                                                                                 !
         _GET_(self%id_sPAIMW,sPAIMW)                                                                               !
         _GET_(self%id_sNH4W,sNH4W)                                                                                 !
         _GET_(self%id_sNO3W,sNO3W)                                                                                 !
         _GET_(self%id_sO2W,sO2W)                                                                                   !
         _GET_(self%id_sSiO2W,sSiO2W)                                                                               !
         _GET_(self%id_sDIMW,sDIMW)                                                                                 !
      !=============================================================================================================!
      ! 1.2 retrieve environmental dependencies                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _GET_(self%id_uTm,uTm)                                                                                        !
      _GET_(self%id_salt,salt)                                                                                      !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. calculate decomposition and remineralization                                                               !
   !================================================================================================================!
      ! 2.1 temperature functions                                                                                   !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      uFunTmNitr = uFunTmArrh(uTm,self%cThetaNitrW)                                                                 ! nitrification temperature function
      uFunTmMinSiW = uFunTmArrh(uTm,self%cThetaMinSiW)                                                              ! remineralization Si temperature function
      !=============================================================================================================!
      ! 2.2 calculate Si particulate mineralization                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      wSiMinPaW = self%kSiMinPaW * uFunTmMinSiW * sSiPaW                                                            ! particulate_OM_Si mineralization
      aCorO2BOD = sO2W / (self%hO2BOD + sO2W)                                                                       ! correction_of_O2_demand_in_water_at_low_oxygen_conc.
      ! tka: should Si-POM also be sensitive to O2 conc?
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  3. calculate inorganic nutrient dynamics                                                                      !
   !================================================================================================================!
      ! 3.1 phosphorous adsorption                                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      aPAdsMaxW = self%cRelPAdsDWW+aCorO2BOD*self%cRelPAdsFeW*self%fFeDIMW+self%cRelPAdsAlW*self%fAlDIMW            ! max. P adsorption per g inorg. matter in water
      aKPAdsW = (1.0_rk - self%fRedMaxW * (1.0_rk-aCorO2BOD)) * self%cKPAdsOxW                                      ! P adsorption affinity, corrected for redox conditions
      aPIsoAdsW = aPAdsMaxW * aKPAdsW * sPO4W / (1.0_rk + aKPAdsW * sPO4W)                                          ! P adsorption isotherm onto inorg. matter in sediment
      aPEqIMW = aPIsoAdsW * sDIMW                                                                                   ! equilibrium conc.
      wPSorpIMW = self%kPSorpW * (aPEqIMW - sPAIMW)                                                                 ! adsorption flux in water
      !=============================================================================================================!
      ! 3.2 nitrification                                                                                           !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      aCorO2NitrW = sO2W*sO2W / (self%hO2Nitr*self%hO2Nitr + sO2W*sO2W)                                             !
      wNNitrW = self%kNitrW * uFunTmNitr * aCorO2NitrW * sNH4W                                                      ! nitrification flux
      !=============================================================================================================!
      ! 3.3 denitrification                                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      ! tkan 2025: moved all dentrificaation code to om_pool to be handle for each OM instance
      !=============================================================================================================!
      ! 3.4 oxygen dynamics                                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      !wO2MinDOMW = molO2molC * self%cCPerDWW * aCorO2BOD * wDMinDOMW                                               ! O2 flux due to mineralization of organic matter, tka: moved wO2MinOMW to om_pool
      wO2NitrW = self%O2PerNH4W * molO2molN * wNNitrW                                                               ! O2 flux due to nitrification
      cO2Sat = uFunO2Sat(salt,uTm)                                                                                  ! O2 saturation in water
      pO2Sat = sO2W / cO2Sat * 100                                                                                  ! O2 pct saturation in water
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. final state variable ROC calculations                                                                       !
   !================================================================================================================!
   wDAbioIMW    = 0.0_rk                                                                                            ! DW inorganic matter flux in water
   wSiAbioPaW   = - wSiMinPaW                                                                                       ! Si particulate OM flux in water
   wPAbioPO4W   = - wPSorpIMW                                                                                       ! PO4 flux in water
   wPAbioAIMW   = wPSorpIMW                                                                                         ! P absorbed on inorganic matter flux in water
   wNAbioNH4W   = - wNNitrW                                                                                         ! NH4 flux in water
   wSiAbioSiO2W = wSiMinPaW                                                                                         ! SiO2 flux in water
   wNAbioNO3W   = wNNitrW                                                                                           ! NO3 flux in water, tka: moved DenitW to om_pool
   wO2AbioW     = - wO2NitrW                                                                                        ! O2 flux in water, tka: moved wO2MinOMW to om_pool
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 5. update variables                                                                                            !
   !================================================================================================================!
      ! 5.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_ODE_(self%id_sDIMW,wDAbioIMW)                                                                            !
      _SET_ODE_(self%id_sPO4W,wPAbioPO4W)                                                                           !
      _SET_ODE_(self%id_sPAIMW,wPAbioAIMW)                                                                          !
      _SET_ODE_(self%id_sNH4W,wNAbioNH4W)                                                                           !
      _SET_ODE_(self%id_sNO3W,wNAbioNO3W)                                                                           !
      _SET_ODE_(self%id_sSiO2W,wSiAbioSiO2W)                                                                        !
      _SET_ODE_(self%id_sO2W,wO2AbioW)                                                                              !
      _SET_ODE_(self%id_sSiPaW,wSiAbioPaW)                                                                          !
      !=============================================================================================================!
      ! 5.2 update local diagnostic variables                                                                       !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_DIAGNOSTIC_(self%id_pO2Sat,pO2Sat)                                                                       !
      !=============================================================================================================!
      ! 5.3 update dummy diagnostics for aggregate variables                                                        !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_DIAGNOSTIC_(self%id_TMdummy,0.0_rk)                                                                      !
      _SET_DIAGNOSTIC_(self%id_BTdummy,0.0_rk)                                                                      !
      _SET_DIAGNOSTIC_(self%id_chladummy,0.0_rk)                                                                    !
      _SET_DIAGNOSTIC_(self%id_aCovVegdummy,0.0_rk)                                                                 !
      _SET_DIAGNOSTIC_(self%id_aDSubVegdummy,0.0_rk)                                                                !
      _SET_DIAGNOSTIC_(self%id_afCovSurfVegdummy,0.0_rk)                                                            !
      !=============================================================================================================!
      ! 5.4 update diagnostic output processes                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
        _SET_DIAGNOSTIC_(self%id_wSiMinPaW,   wSiMinPaW)                                                            !
        _SET_DIAGNOSTIC_(self%id_wPSorpIMW,   wPSorpIMW)                                                            !
        _SET_DIAGNOSTIC_(self%id_wNNitrW,     wNNitrW)                                                              !
        _SET_DIAGNOSTIC_(self%id_wO2NitrW,    wO2NitrW)                                                             !
      endif                                                                                                         !
   !================================================================================================================!
   _LOOP_END_ !!! END OF MODEL CODE::
end subroutine do

!
! SUBROUTINE: GET LIGHT EXTINCTION                                                                                                                                                               
!
subroutine get_light_extinction(self,_ARGUMENTS_GET_EXTINCTION_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_abiotic_water), intent(in) :: self
   _DECLARE_ARGUMENTS_GET_EXTINCTION_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk) :: sDIMW, extIM
 
   _LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE:: 
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values                                                                                   !
   !================================================================================================================!
   _GET_(self%id_sDIMW,sDIMW)                                                                                       !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. calculate local light extinction coefficients                                                              !
   !================================================================================================================!
   extIM=self%cExtSpIM*sDIMW                                                                                        !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  3. update light extinction and diagnostics                                                                    !
   !================================================================================================================!
   _SET_EXTINCTION_(extIM)                                                                                          !
   _SET_DIAGNOSTIC_(self%id_extIM,extIM)                                                                            !
   !================================================================================================================!
   _LOOP_END_ !!! END OF MODEL CODE::
end subroutine get_light_extinction

!
! SUBROUTINE: DO SURFACE                                                                                                                                                                         
!
subroutine do_surface(self,_ARGUMENTS_DO_SURFACE_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_abiotic_water),intent(in) :: self
   _DECLARE_ARGUMENTS_DO_SURFACE_

   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)                   :: uVWind,sO2W,uTm
   real(rk)                   :: tO2Aer,uO2Sat,aFunLemnAer,kAer,uFunTmAer

   _HORIZONTAL_LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE:: 
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve state variable values and environmental dependencies                                              !
   !================================================================================================================!
   _GET_HORIZONTAL_(self%id_uVWind,uVWind)                                                                          !
   _GET_(self%id_uTm,uTm)                                                                                           !
   _GET_(self%id_sO2W,sO2W)                                                                                         !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. oxygen reaeration functions                                                                                !
   !================================================================================================================!
   uFunTmAer =  uFunTmArrh(uTm,self%cThetaAer)                                                                      ! temperature function of reaeration
   uO2Sat = 14.652_rk - 0.41022 * uTm + 0.007991_rk * uTm*uTm - 0.000077774_rk * uTm*uTm*uTm                        ! oxygen saturation concentration
   kAer=(0.727_rk*((uVWind)**(0.5_rk))-0.371_rk*uVWind+0.0376_rk*uVWind*uVWind)                                     ! reaeration coefficient
   aFunLemnAer = 1.0_rk                                                                                             ! duckweed function of reaeration
   tO2Aer = kAer * uFunTmAer * (uO2Sat - sO2W) * aFunLemnAer                                                        ! reaeration flux of O2 into the water
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  3. update state variable values and diagnostics                                                               !
   !================================================================================================================!
   _SET_SURFACE_EXCHANGE_(self%id_sO2W,tO2Aer/secs_pr_day)                                                          !
   _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tO2Aer,tO2Aer/secs_pr_day)                                                   !
   _SET_HORIZONTAL_DIAGNOSTIC_(self%id_wind,uVWind)                                                                 !
   _SET_SURFACE_EXCHANGE_(self%id_sDIMW,  self%tDDepoIM)                                                            !
   _SET_SURFACE_EXCHANGE_(self%id_sNH4W,  self%tNDepoNH4)                                                           !
   _SET_SURFACE_EXCHANGE_(self%id_sNO3W,  self%tNDepoNO3)                                                           !
   _SET_SURFACE_EXCHANGE_(self%id_sPO4W,  self%tPDepoPO4)                                                           !
   !================================================================================================================!
   _HORIZONTAL_LOOP_END_                                                                                            
end subroutine do_surface
!
end module wet_abiotic_water
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
