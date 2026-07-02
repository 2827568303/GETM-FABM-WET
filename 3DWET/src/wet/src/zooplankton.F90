#include "fabm_driver.h"
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ MODULE: ZOOPLANKTON                                                                                                                                                                            §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
module wet_zooplankton
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_particle
   use wet_utility, ONLY:uFunTmGaus
   implicit none
   private
   
   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public                   :: type_wet_zooplankton
      ! local state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                            :: id_sDZoo, id_sPZoo, id_sNZoo, id_sCZoo
      ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_model_id),          allocatable, dimension(:) :: id_prey
      type (type_state_variable_id), allocatable, dimension(:) :: id_PreyD, id_PreyN, id_PreyP, id_PreyC
      type (type_dependency_id),     allocatable, dimension(:) :: id_PreySi
      type (type_state_variable_id)                            :: id_NPOMpoolW, id_PPOMpoolW, id_SiPapoolW, id_DPOMpoolW, id_DDOMpoolW, id_NDOMpoolW, id_PDOMpoolW, id_SiO2poolW, id_NH4poolW
      type (type_state_variable_id)                            :: id_PO4poolW, id_CPOMpoolW, id_CDOMpoolW
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)                       :: id_wDConsZooTot, id_wNConsZooTot, id_wPConsZooTot, id_wCConsZooTot, id_wDEgesZoo, id_wNEgesZoo, id_wPEgesZoo, id_wCEgesZoo
      type (type_diagnostic_variable_id)                       :: id_wDMortZoo, id_wNMortZoo, id_wPMortZoo, id_wCMortZoo, id_wDZooPOMW, id_wNZooPOMW, id_wPZooPOMW, id_wCZooPOMW 
      type (type_diagnostic_variable_id)                       :: id_wDZooDOMW, id_wNZooDOMW, id_wPZooDOMW, id_wCZooDOMW, id_rPDZoo, id_rNDZoo, id_rCDZoo
      type (type_diagnostic_variable_id)                       :: id_wDRespZoo, id_wCRespZoo, id_wNZooNH4W, id_wPZooPO4W, id_wSiO2ZooW, id_wSiPaZooW, id_aFeedLvlZoo
      type (type_diagnostic_variable_id), allocatable, dimension(:)  :: id_wDConsZoo, id_wPConsZoo, id_wNConsZoo, id_wCConsZoo
      ! environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_dependency_id)                                :: id_uTm, id_dz, id_par, id_oxygen
      type (type_horizontal_dependency_id)                     :: id_sDepthW
      type (type_diagnostic_variable_id)                       :: id_par_out
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      real(rk)                                                 :: cSigTmZoo, cTmOptZoo, cDCarrZoo, kMortZoo, kDRespZoo, fDAssZoo, kDConsMaxZoo, cPDRef, cNDRef, cCDRef, fDissEgesZoo, fDissMortZoo
      real(rk)                                                 :: cDMinZoo, fZooDOMW, cMinO2, cMinLight, cMaxLight, cVswim
      real(rk),                      allocatable, dimension(:) :: fGutOccPrey, cClearPrey
      integer                                                  :: nPrey, qTrans, qODB
      character(len=64),             allocatable, dimension(:) :: prey_suffix
      logical,                       allocatable, dimension(:) :: lSi
      logical                                                  :: diagnostics

   contains

   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure :: initialize
   procedure :: do
   procedure :: get_vertical_movement
   procedure :: calc_ODB

   end type type_wet_zooplankton

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk

contains
    
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_zooplankton), intent(inout), target :: self
   integer,                     intent(in)            :: configunit
   
   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer             :: i_prey
   character(len=64)   :: index
   
   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! population-level parameters---------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cDMinZoo,     'cDMinZoo',     'gDW/m3',    'minimum DW concentration',                                            default=0.00001_rk                                )
   call self%get_parameter(self%cDCarrZoo,    'cDCarrZoo',    'gDW/m3',    'carrying capacity',                                                   default=25.0_rk                                   )
   ! vertical movement parameters--------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%qTrans,       'qTrans',       '-',         'vert. trans. method: 0=no trans.; 1=passive; 2=O2; 3=O2 & Light',     default=2                                         )
   call self%get_parameter(self%cMinO2,       'cMinO2',       'gO2/m3',    'qtrans > 1; oxygen conc. limit',                                      default=2.0_rk                                    )
   call self%get_parameter(self%cMinLight,    'cMinLight',    'W/m2',      'qtrans = 3; light level triggering upwards swimming',                 default=40.0_rk                                   )
   call self%get_parameter(self%cMaxLight,    'cMaxLight',    'W/m2',      'qtrans = 3; light level triggering downwards swimming',               default=40.0_rk                                   )
   call self%get_parameter(self%cVswim,       'cVswim',       'm/d',       'qtrans > 1; vertical migration speed',                                default=15.0_rk,   scale_factor=1.0_rk/secs_pr_day)
   ! prey parameters---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%nPrey,        'nPrey',        '-',         'number of prey types',                                                default=1                                         )
   call self%get_parameter(self%qODB,         'qODB',         '-',         'toggle optimal diet breadth: 0=off; 1=on',                            default=0                                         )
   allocate (self%lSi(self%nPrey))                                                                                                                    
   allocate (self%prey_suffix(self%nPrey))
   allocate (self%cClearPrey(self%nPrey))
   allocate (self%fGutOccPrey(self%nPrey))
   do i_prey=1,self%nPrey                                                                                                                                                      
       write(index,'(i0)') i_prey                                                                                                                                          
       call self%get_parameter(self%lSi(i_prey),           'lSi'//trim(index),        '-',         'toggle prey silica tracking '//trim(index),   default=.false.                                   )
       call self%get_parameter(self%prey_suffix(i_prey),   'prey_suffix'//trim(index),'-',         'prey name suffix'//trim(index),               default=''                                        )
       call self%get_parameter(self%cClearPrey(i_prey),    'cClearPrey'//trim(index), 'm3/gDW/d',  'clearance rate for prey '//trim(index),       default=2.0_rk,    scale_factor=1.0_rk/secs_pr_day)
       call self%get_parameter(self%fGutOccPrey(i_prey),   'fGutOccPrey'//trim(index),'-',         'gut occupation factor for prey '//trim(index),default=1.0_rk                                    )   
   end do
   ! vital parameters--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%kDRespZoo,    'kDRespZoo',    '1/d',       'maintenance respiration rate at 20*C',                                default=0.2_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%fDAssZoo,     'fDAssZoo',     '-',         'dry weight assimilation efficiency',                                  default=0.35_rk                                   )
   call self%get_parameter(self%kMortZoo,     'kMortZoo',     '1/d',       'mortality rate',                                                      default=0.04_rk,   scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%kDConsMaxZoo, 'kDConsMaxZoo', 'gDW/gDW/d', 'standard dry weight specific maximum consumption rate',               default=0.5_rk,    scale_factor=1.0_rk/secs_pr_day)
   ! stochiometric parameters------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cPDRef,       'cPDRef',       'mgP/mgDW',  'reference P/DW-ratio',                                                default=0.01_rk                                   )
   call self%get_parameter(self%cNDRef,       'cNDRef',       'mgN/mgDW',  'reference N/DW-ratio',                                                default=0.07_rk                                   )
   call self%get_parameter(self%cCDRef,       'cCDRef',       'mgC/mgDW',  'reference C/DW-ratio',                                                default=0.45_rk                                   )
   call self%get_parameter(self%fDissEgesZoo, 'fDissEgesZoo', '-',         'soluble inorg. nutrient fraction of egested food',                    default=0.25_rk                                   )
   call self%get_parameter(self%fDissMortZoo, 'fDissMortZoo', '-',         'soluble inorg. nutrient fraction of dead ind.',                       default=0.1_rk                                    )
   call self%get_parameter(self%fZooDOMW,     'fZooDOMW',     '-',         'DOM fraction of dead individuals',                                    default=0.35_rk                                   )
   ! temperature parameters--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cSigTmZoo,    'cSigTmZoo',    '*C',        'temperature constant; sigma in Gaussian curve',                       default=13.0_rk                                   )
   call self%get_parameter(self%cTmOptZoo,    'cTmOptZoo',    '*C',        'optimum temperature',                                                 default=22.0_rk                                   )
   ! diagnostic  parameter--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,  'diagnostics',  '-',         'toggle diagnostic output',                                            default=.false.                                   )
   
   !REGISTER MODEL VARIBLES, DEPENDENCIES & COUPLINGS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! local state variables---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sDZoo,     'sD',  'gDW/m3',    'DW',    initial_value=0.05_rk,      minimum=self%cDMinZoo,                    no_river_dilution=.TRUE.)
   call self%register_state_variable(self%id_sPZoo,     'sP',  'gP/m3',     'P',     initial_value=0.0005_rk,    minimum=self%cDMinZoo * self%cPDRef,      no_river_dilution=.TRUE.)
   call self%register_state_variable(self%id_sNZoo,     'sN',  'gN/m3',     'N',     initial_value=0.0035_rk,    minimum=self%cDMinZoo * self%cNDRef,      no_river_dilution=.TRUE.)
   call self%register_state_variable(self%id_sCZoo,     'sC',  'gC/m3',     'C',     initial_value=0.02_rk,      minimum=self%cDMinZoo * self%cCDRef,      no_river_dilution=.TRUE.)
   if (self%qTrans == 0) then
       call self%set_variable_property(self%id_sDZoo,   'disable_transport',   .true.)   
       call self%set_variable_property(self%id_sNZoo,   'disable_transport',   .true.)
       call self%set_variable_property(self%id_sPZoo,   'disable_transport',   .true.)
       call self%set_variable_property(self%id_sCZoo,   'disable_transport',   .true.)
   endif
   ! Register contribution of state to global aggregate variables------------------------------------------------------------------------------------------------------------------------------------
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totN',aggregate_variable=.true.),      self%id_sNZoo)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totP',aggregate_variable=.true.),      self%id_sPZoo)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totC',aggregate_variable=.true.),      self%id_sCZoo)
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_totSusPar',aggregate_variable=.true.), self%id_sDZoo)
   ! register state variable dependencies------------------------------------------------------------------------------------------------------------------------------------------------------------
   allocate(self%id_prey(self%nPrey))
   allocate(self%id_PreyD(self%nPrey))
   allocate(self%id_PreyP(self%nPrey))
   allocate(self%id_PreyN(self%nPrey))
   allocate(self%id_PreyC(self%nPrey))
   allocate(self%id_PreySi(self%nPrey))
   allocate(self%id_wDConsZoo(self%nPrey))
   allocate(self%id_wPConsZoo(self%nPrey))
   allocate(self%id_wNConsZoo(self%nPrey))
   allocate(self%id_wCConsZoo(self%nPrey))
   do i_prey=1,self%nPrey
       write(index,'(i0)') i_prey
       call self%register_model_dependency(self%id_prey(i_prey),  'prey_model'//trim(index))
       call self%register_state_dependency(self%id_PreyD(i_prey), 'Prey_D_'//trim(index), 'g/m3', 'prey D'//trim(index))
       call self%register_state_dependency(self%id_PreyN(i_prey), 'Prey_N_'//trim(index), 'g/m3', 'prey N'//trim(index))
       call self%register_state_dependency(self%id_PreyP(i_prey), 'Prey_P_'//trim(index), 'g/m3', 'prey P'//trim(index))
       call self%register_state_dependency(self%id_PreyC(i_prey), 'Prey_C_'//trim(index), 'g/m3', 'prey C'//trim(index))
       call self%request_coupling_to_model(self%id_PreyD(i_prey),self%id_prey(i_prey), 'sD'//trim(self%prey_suffix(i_prey)))
       call self%request_coupling_to_model(self%id_PreyP(i_prey),self%id_prey(i_prey), 'sP'//trim(self%prey_suffix(i_prey)))
       call self%request_coupling_to_model(self%id_PreyN(i_prey),self%id_prey(i_prey), 'sN'//trim(self%prey_suffix(i_prey)))
       call self%request_coupling_to_model(self%id_PreyC(i_prey),self%id_prey(i_prey), 'sC'//trim(self%prey_suffix(i_prey)))
       if (self%lSi(i_prey)) then
           call self%register_dependency(self%id_PreySi(i_prey), 'Prey_Si_'//trim(index), 'g/m3', 'prey Si'//trim(index))
           call self%request_coupling_to_model(self%id_PreySi(i_prey),self%id_prey(i_prey), 'oSi'//trim(self%prey_suffix(i_prey)))
       endif
       if (self%diagnostics) then
	       call self%register_diagnostic_variable(self%id_wDConsZoo(i_prey), 'wDConsZoo_'//trim(index),	'g/m3/s','rate D consumed '//trim(index),  output=output_instantaneous)
           call self%register_diagnostic_variable(self%id_wPConsZoo(i_prey), 'wPConsZoo_'//trim(index),	'g/m3/s','rate P consumed '//trim(index),  output=output_instantaneous)
           call self%register_diagnostic_variable(self%id_wNConsZoo(i_prey), 'wNConsZoo_'//trim(index),	'g/m3/s','rate N consumed '//trim(index),  output=output_instantaneous)
           call self%register_diagnostic_variable(self%id_wCConsZoo(i_prey), 'wCConsZoo_'//trim(index),	'g/m3/s','rate C consumed '//trim(index),  output=output_instantaneous)
       endif 
   end do
   call self%register_state_dependency(self%id_DPOMpoolW,                   'POM_DW_pool_water',     'g/m3',     'POM DW pool in water'     )
   call self%register_state_dependency(self%id_NPOMpoolW,                   'POM_N_pool_water',      'g/m3',     'POM N pool in water'      )
   call self%register_state_dependency(self%id_PPOMpoolW,                   'POM_P_pool_water',      'g/m3',     'POM P pool in water'      )
   call self%register_state_dependency(self%id_CPOMpoolW,                   'POM_C_pool_water',      'g/m3',     'POM C pool in water'      )
   call self%register_state_dependency(self%id_SiPapoolW,                   'SiPa_pool_water',       'g/m3',     'particulate Si pool water')
   call self%register_state_dependency(self%id_NH4poolW,                    'NH4_pool_water',        'g/m3',     'NH4 pool in water'        )
   call self%register_state_dependency(self%id_PO4poolW,                    'PO4_pool_water',        'g/m3',     'PO4 pool in water'        )
   !call self%register_state_dependency(self%id_CO2poolW,                    'CO2_pool_water',        'g/m3',     'CO2 pool in water'        ) ! to be used with GHG module enabled
   call self%register_state_dependency(self%id_DDOMpoolW,                   'DOM_DW_pool_water',     'g/m3',     'DOM DW in water'          )
   call self%register_state_dependency(self%id_NDOMpoolW,                   'DOM_N_pool_water',      'g/m3',     'DOM N in water'           )
   call self%register_state_dependency(self%id_PDOMpoolW,                   'DOM_P_pool_water',      'g/m3',     'DOM P in water'           )
   call self%register_state_dependency(self%id_CDOMpoolW,                   'DOM_C_pool_water',      'g/m3',     'DOM C in water'           )
   call self%register_state_dependency(self%id_SiO2poolW,                   'SiO2_pool_water',       'g/m3',     'SiO2 in water'            )
   ! Register diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_rPDZoo,                   'rPDZoo',                'gP/gDW',   'P/D ratio',                       output=output_instantaneous,source=source_do)
   call self%register_diagnostic_variable(self%id_rNDZoo,                   'rNDZoo',                'gN/gDW',   'N/D ratio',                       output=output_instantaneous,source=source_do)
   call self%register_diagnostic_variable(self%id_rCDZoo,                   'rCDZoo',                'gC/gDW',   'C/D ratio',                       output=output_instantaneous,source=source_do)
   if (self%diagnostics) then
       call self%register_diagnostic_variable(self%id_wDConsZooTot,         'wDConsZooTot',          'g/m3/s',   'rate D prey consumed',            output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wNConsZooTot,         'wNConsZooTot',          'g/m3/s',   'rate N prey consumed',            output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wPConsZooTot,         'wPConsZooTot',          'g/m3/s',   'rate P prey consumed',            output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wCConsZooTot,         'wCConsZooTot',          'g/m3/s',   'rate C prey consumed',            output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_aFeedLvlZoo,          'aFeedLvlZoo',           '-',        'feeding level',                   output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wDEgesZoo,            'wDEgesZoo',             'g/m3/s',   'rate DW egested',                 output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wNEgesZoo,            'wNEgesZoo',             'g/m3/s',   'rate N egested',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wPEgesZoo,            'wPEgesZoo',             'g/m3/s',   'rate P egested',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wCEgesZoo,            'wCEgesZoo',             'g/m3/s',   'rate C egested',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wDMortZoo,            'wDMortZoo',             'g/m3/s',   'rate DW from mortality',          output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wNMortZoo,            'wNMortZoo',             'g/m3/s',   'rate N from mortality',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wPMortZoo,            'wPMortZoo',             'g/m3/s',   'rate P from mortality',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wCMortZoo,            'wCMortZoo',             'g/m3/s',   'rate C from mortality',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wDZooPOMW,            'wDZooPOMW',             'g/m3/s',   'rate DPOMW out',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wNZooPOMW,            'wNZooPOMW',             'g/m3/s',   'rate NPOMW out',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wPZooPOMW,            'wPZooPOMW',             'g/m3/s',   'rate PPOMW out',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wCZooPOMW,            'wCZooPOMW',             'g/m3/s',   'rate CPOMW out',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wDZooDOMW,            'wDZooDOMW',             'g/m3/s',   'rate DDOMW out',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wNZooDOMW,            'wNZooDOMW',             'g/m3/s',   'rate NDOMW out',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wPZooDOMW,            'wPZooDOMW',             'g/m3/s',   'rate PDOMW out',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wCZooDOMW,            'wCZooDOMW',             'g/m3/s',   'rate CDOMW out',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wDRespZoo,            'wDRespZoo',             'g/m3/s',   'rate DW respired',                output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wCRespZoo,            'wCRespZoo',             'g/m3/s',   'rate C respired',                 output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wNZooNH4W,            'wNZooNH4W',             'g/m3/s',   'rate NH4W out',                   output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wPZooPO4W,            'wPZooPO4W',             'g/m3/s',   'rate PO4W out',                   output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wSiO2ZooW,            'wSiO2ZooW',             'g/m3/s',   'rate SiO2W out',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_wSiPaZooW,            'wSiPaZooW',             'g/m3/s',   'rate Si particulate W egested',   output=output_instantaneous)
   endif  
   ! register environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_uTm,     standard_variables%temperature)
   call self%register_dependency(self%id_dz,      standard_variables%cell_thickness)
   call self%register_dependency(self%id_sDepthW, standard_variables%bottom_depth)
   call self%register_dependency(self%id_oxygen,  'oxygen_pool_water', 'g/m3', 'Oxygen pool water')
   call self%register_dependency(self%id_par,     standard_variables%downwelling_photosynthetic_radiative_flux)

   return

end subroutine initialize

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO (PELAGIC)                                                                                                                                                                       §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do(self,_ARGUMENTS_DO_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_zooplankton), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)                           :: uTm, dz, sDepthW, sDZoo, sNZoo, sPZoo, sCZoo, rPDZoo, rNDZoo, rCDZoo, uFunTmZoo, aDSatZoo, wDEnvZoo, ukDIncrZoo, oDFoodZoo, aCorDRespZoo, wDConsZooTot
   real(rk)                           :: wDZoo, wDAssZoo, wDRespZoo, wDMortZoo, wNZoo, wNAssZoo, wNExcrZoo, wNMortZoo
   real(rk)                           :: wNConsZooTot, wPConsZooTot, wCConsZooTot, rNDFoodZoo, rPDFoodZoo, rCDFoodZoo, afPAssZoo, afCAssZoo, afNAssZoo
   real(rk)                           :: wNZooNH4W, wNEgesZoo, wPZooPO4W, wPEgesZoo, wDZooPOMW, wDEgesZoo, wNZooPOMW, wPExcrZoo, wPMortZoo, wPZooPOMW, wSiPaZooW, wDZooTOMW, wNZooTOMW, wPZooTOMW
   real(rk)                           :: wCAssZoo, wCRespZoo, wCEgesZoo, wCMortZoo, wCZooCO2W, wCZooTOMW, wCZooPOMW, wCZooDOMW, wCZoo
   real(rk)                           :: wDZooDOMW, wNZooDOMW, wPZooDOMW, wSiO2ZooW, sDPOM, sNPOM, sPPOM, rNDPOM, rPDPOM, aFeedLvlZoo, tDEnvZoo, wPZoo, wPAssZoo
   real(rk),   dimension(self%nPrey)  :: sPprey, sDprey, sNprey, sCprey, rNDprey, rPDprey, rCDprey, rSiDprey, sSiprey, wDConsZoo, wNConsZoo, wPConsZoo, wCConsZoo
   integer                            :: i_prey

   _LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
      ! 1.1 retrieve environmental dependencies                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _GET_(self%id_uTm,uTm)                                                                                        ! get local temperature
      _GET_(self%id_dz,dz)                                                                                          ! get layer depth
      _GET_HORIZONTAL_(self%id_sDepthW,sDepthW)                                                                     !
      !=============================================================================================================!
      ! 1.2 retrieve state variables, & calc. current local nutrient ratios and relative abundances                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.2.1 zooplankton state variables                                                                        !
         !----------------------------------------------------------------------------------------------------------!
         _GET_(self%id_sDZoo,sDZoo)                                                                                 ! get zooplankton dry weight
         _GET_(self%id_sNZoo,sNZoo)                                                                                 ! get zooplankton nitrogen
         _GET_(self%id_sPZoo,sPZoo)                                                                                 ! get zooplankton phosphorous
         _GET_(self%id_sCZoo,sCZoo)                                                                                 ! get zooplankton carbon
         rPDZoo = sPZoo/(sDZoo+NearZero)                                                                            ! calculate P:DW ratio
         rNDZoo = sNZoo/(sDZoo+NearZero)                                                                            ! calculate N:DW ratio
         rCDZoo = sCZoo/(sDZoo+NearZero)                                                                            ! calculate C:DW ratio
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.2.2 prey state variables                                                                               !
         !----------------------------------------------------------------------------------------------------------!
         do i_prey=1,self%nPrey                                                                                     ! for each prey
            _GET_(self%id_PreyD(i_prey),sDprey(i_prey))                                                             !   get prey dry weight (dimensions: nPrey)
            _GET_(self%id_PreyP(i_prey),sPprey(i_prey))                                                             !   get prey phosphorous (dimensions: nPrey)
            _GET_(self%id_PreyN(i_prey),sNprey(i_prey))                                                             !   get prey nitrogen (dimensions: nPrey)
            _GET_(self%id_PreyC(i_prey),sCprey(i_prey))                                                             !   get prey carbon (dimensions: nPrey)
             if (self%lSi(i_prey)) then                                                                             !   check whether Silica is tracked
                _GET_(self%id_PreySi(i_prey),sSiprey(i_prey))                                                       !     get prey silica (dimensions: nPrey)
             else                                                                                                   !   if silica is not tracked
                 sSiprey(i_prey) = 0.0_rk                                                                           !     then content is set to zero
             endif                                                                                                  !
         end do                                                                                                     !
         rNDprey = sNprey/(sDprey+NearZero)                                                                         ! calculate prey N:DW ratios (dimensions: nPrey)
         rPDprey = sPprey/(sDprey+NearZero)                                                                         ! calculate prey P:DW ratios (dimensions: nPrey)
         rCDprey = sCprey/(sDprey+NearZero)                                                                         ! calculate prey C:DW ratios (dimensions: nPrey)
         rSiDprey = sSiPrey/(sDprey+NearZero)                                                                       ! calculate prey Si:DW ratios (dimensions: nPrey)
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!                                                          
   !  2. calculate growth and assimilation of DW                                                                    !                                                           
   !================================================================================================================!                                                          
      ! 2.1 temperature function                                                                                    ! 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                          
      uFunTmZoo =uFunTmGaus(uTm,self%cSigTmZoo,self%cTmOptZoo)                                                      ! calc. temperature correction of zooplankton vital rates
      !=============================================================================================================!
      ! 2.2 calculate prey consumption and assimilation rates                                                       !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%qODB == 0) then                                                                                      ! if optimal diet breadth is turned off   
          aFeedLvlZoo = sum(self%cClearPrey*self%fGutOccPrey*sDPrey) / &                                            !   calculate feeding level, based on all available zoop. prey
              (sum(self%cClearPrey*self%fGutOccPrey*sDPrey) + uFunTmZoo*self%kDConsMaxZoo)                          !
          wDConsZoo = sDZoo*self%cClearPrey*sDPrey*(1-aFeedLvlZoo)                                                  !   calculate consumption of all available zoop. prey
      elseif (self%qODB == 1) then                                                                                  ! elseif optimal diet breadth is turned on
          call self%calc_ODB(wDConsZoo,aFeedLvlZoo,sDPrey,uFunTmZoo,sDZoo)                                          ! calculate ODB for planktivory
      endif                                                                                                         !
      tDEnvZoo = max(0.0_rk,(((self%kDConsMaxZoo*self%fDAssZoo-self%kDRespZoo)*uFunTmZoo-self%kMortZoo) / &         ! calculate environmental correction
          self%cDCarrZoo) * sDZoo*sDZoo)                                                                            !
      wDAssZoo = self%fDAssZoo * sum(wDConsZoo)                                                                     ! calculate total assimilation - environmental correction from PCLake removed.
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 3. calculate prey consumption rates (N & P)                                                                    !
   !================================================================================================================!
   wNConsZoo = wDConsZoo * rNDprey                                                                                  ! calculate prey N consumption (dimensions: nPrey)
   wPConsZoo = wDConsZoo * rPDprey                                                                                  ! calculate prey P consumption (dimensions: nPrey)
   wCConsZoo = wDConsZoo * rCDprey                                                                                  ! calculate prey C consumption (dimensions: nPrey)
   wDConsZooTot = sum(wDConsZoo)                                                                                    ! calculate total prey DW consumption
   wNConsZooTot = sum(wNConsZoo)                                                                                    ! calculate total prey N consumption
   wPConsZooTot = sum(wPConsZoo)                                                                                    ! calculate total prey P consumption
   wCConsZooTot = sum(wCConsZoo)                                                                                    ! calculate total prey P consumption
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. calculate N, and P assimilation                                                                             !
   !================================================================================================================!
      ! 4.1 nitrogen                                                                                                !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      rNDFoodZoo = wNConsZooTot / wDConsZooTot                                                                      ! calculate total available prey nitrogen ratio
      afNAssZoo = min(1.0_rk,self%cNDRef / rNDFoodZoo * self%fDAssZoo)                                              ! calculate N assimilation efficiency
      wNAssZoo = afNAssZoo* wNConsZooTot                                                                            ! calculate N assimilation rate
      !=============================================================================================================!
      ! 4.2 phosphorous                                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      rPDFoodZoo = wPConsZooTot / wDConsZooTot                                                                      ! calculate total available prey nitrogen ratio
      afPAssZoo = min(1.0_rk,self%cPDRef / rPDFoodZoo * self%fDAssZoo)                                              ! calculate N assimilation efficiency
      wPAssZoo = afPAssZoo* wPConsZooTot                                                                            ! calculate N assimilation rate
      !=============================================================================================================!
      ! 4.3 carbon                                                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      rCDFoodZoo = wCConsZooTot / wDConsZooTot                                                                      ! calculate total available prey carbon ratio
      afCAssZoo = min(1.0_rk,self%cCDRef / rCDFoodZoo * self%fDAssZoo)                                              ! calculate C assimilation efficiency
      wCAssZoo = afCAssZoo* wCConsZooTot                                                                            ! calculate C assimilation rate
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 5. calculate respiration, egestion, excretion, mortality and migration                                         !
   !================================================================================================================!
      ! 5.1 calculate respiration/excretion                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      aCorDRespZoo = max(self%cPDRef / rPDZoo,self%cNDRef / rNDZoo, self%cCDRef / rCDZoo)                           ! calculate corr. factor between respiration and P, N, C content
      wDRespZoo = aCorDRespZoo * self%kDRespZoo * uFunTmZoo * sDZoo                                                 ! calculate zooplankton respiration (in DW)
      wCRespZoo = rCDZoo / self%cCDRef * self%kDRespZoo * uFunTmZoo * sCZoo                                         ! calculate C respired
      wNExcrZoo = rNDZoo / self%cNDRef * self%kDRespZoo * uFunTmZoo * sNZoo                                         ! calculate N excretion
      wPExcrZoo = rPDZoo / self%cPDRef * self%kDRespZoo * uFunTmZoo * sPZoo                                         ! calculate P excretion
      !=============================================================================================================!
      ! 5.2 calculate egestion                                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      wDEgesZoo = wDConsZooTot - wDAssZoo                                                                           ! calculate DW egestion
      wNEgesZoo = wNConsZooTot - wNAssZoo                                                                           ! calculate N egestion
      wPEgesZoo = wPConsZooTot - wPAssZoo                                                                           ! calculate P egestion
      wCEgesZoo = wCConsZooTot - wCAssZoo                                                                           ! calculate P egestion
      !=============================================================================================================!
      ! 5.3 calculate mortality                                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      wDMortZoo = self%kMortZoo * sDZoo + tDEnvZoo                                                                  ! calculate mortality in DW
      wNMortZoo = rNDZoo * wDMortZoo                                                                                ! calculate mortality in N
      wPMortZoo = rPDZoo * wDMortZoo                                                                                ! calculate mortality in P
      wCMortZoo = rCDZoo * wDMortZoo                                                                                ! calculate mortality in C
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 6. final flux calculations                                                                                     !
   !================================================================================================================!
      ! 6.1 final zooplankton rate of change                                                                        !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      wDZoo = wDAssZoo - wDRespZoo - wDMortZoo                                                                      ! calculate final rate of change of DW
      wNZoo = wNAssZoo - wNExcrZoo - wNMortZoo                                                                      ! calculate final rate of change of N
      wPZoo = wPAssZoo - wPExcrZoo - wPMortZoo                                                                      ! calculate final rate of change of P
      wCZoo = wCAssZoo - wCRespZoo - wCMortZoo                                                                      ! calculate final rate of change of C
      !=============================================================================================================!
      ! 6.2 final fluxes to external abiotic variables                                                              !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.1 dry weight                                                                                         !
         !----------------------------------------------------------------------------------------------------------!
         wDZooTOMW = wDEgesZoo + wDMortZoo                                                                          ! calculate total flux of DW to the water column
         wDZooPOMW = wDZooTOMW * (1.0_rk - self%fZooDOMW)                                                           ! calculate particulate fraction of DW flux
         wDZooDOMW = wDZooTOMW * self%fZooDOMW                                                                      ! calculate dissolved fraction of DW flux
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.2 nitrogen                                                                                           !
         !----------------------------------------------------------------------------------------------------------!
         wNZooNH4W = wNExcrZoo + self%fDissEgesZoo*wNEgesZoo + self%fDissMortZoo*wNMortZoo                          ! calculate dissolved fraction of N flux to the water column                                                                                                                    !
         wNZooTOMW = wNMortZoo * (1.0_rk - self%fDissMortZoo) + wNEgesZoo * (1.0_rk - self%fDissEgesZoo)            ! calculate total organic nitrogen flux
         wNZooPOMW = wNZooTOMW * (1.0_rk - self%fZooDOMW)                                                           ! calculate particulate fraction of organic nitrogen flux
         wNZooDOMW = wNZooTOMW * self%fZooDOMW                                                                      ! calcualte dissolved fraction of organic nitrogen flux
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.3 phosphorous                                                                                        !
         !----------------------------------------------------------------------------------------------------------!
         wPZooPO4W = wPExcrZoo + self%fDissEgesZoo*wPEgesZoo + self%fDissMortZoo * wPMortZoo                        ! calculate dissolved fraction of P flux to the water column
         wPZooTOMW = wPMortZoo * (1.0_rk - self%fDissMortZoo) + wPEgesZoo * (1.0_rk - self%fDissEgesZoo)            ! calculate total organic phosphorous flux
         wPZooPOMW = wPZooTOMW * (1.0_rk - self%fZooDOMW)                                                           ! calculate particulate fraction of organic phosphorous flux
         wPZooDOMW = wPZooTOMW * self%fZooDOMW                                                                      ! calcualte dissolved fraction of organic phosphorous flux
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.4 carbon                                                                                             !
         !----------------------------------------------------------------------------------------------------------!
         wCZooCO2W = wCRespZoo                                                                                      ! calculate C flux to CO2 in water
         wCZooTOMW = wCMortZoo + wCEgesZoo                                                                          ! calculate total organic carbon flux
         wCZooPOMW = wCZooTOMW * (1.0_rk - self%fZooDOMW)                                                           ! calculate particulate fraction of organic carbon flux
         wCZooDOMW = wCZooTOMW * self%fZooDOMW                                                                      ! calcualte dissolved fraction of organic carbon flux
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.5 silica                                                                                             !
         !----------------------------------------------------------------------------------------------------------!
         wSiO2ZooW = sum((sSiprey/sDprey) * wDConsZoo) * self%fZooDOMW                                              ! flux of silica to the water column, dissolved fraction
         wSiPaZooW = sum((sSiprey/sDprey) * wDConsZoo) * (1.0_rk - self%fZooDOMW)                                   ! flux of silica to the water column, particulate fraction
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 7. update model variables                                                                                      !
   !================================================================================================================!
      ! 7.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_ODE_(self%id_sDZoo,wDZoo)                                                                                ! update zooplankton DW ODE
      _SET_ODE_(self%id_sNZoo,wNZoo)                                                                                ! update zooplankton N ODE
      _SET_ODE_(self%id_sPZoo,wPZoo)                                                                                ! update zooplankton P ODE
      _SET_ODE_(self%id_sCZoo,wCZoo)                                                                                ! update zooplankton C ODE
      !=============================================================================================================!
      ! 7.2 update external biotic state variables                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      do i_prey = 1,self%nPrey                                                                                      ! for earch zoop. prey
         _SET_ODE_(self%id_PreyD(i_prey),-wDConsZoo(i_prey))                                                        !   update prey DW ODEs
         _SET_ODE_(self%id_PreyN(i_prey),-wNConsZoo(i_prey))                                                        !   update prey N ODEs
         _SET_ODE_(self%id_PreyP(i_prey),-wPConsZoo(i_prey))                                                        !   update prey P ODEs
         _SET_ODE_(self%id_PreyC(i_prey),-wCConsZoo(i_prey))                                                        !   update prey C ODEs
      end do                                                                                                        !
      !=============================================================================================================!
      ! 7.3 update external biotic state variables                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_ODE_(self%id_NH4poolW,      wNZooNH4W)                                                                   ! update dissolved ammonia ODE
      _SET_ODE_(self%id_PO4poolW,      wPZooPO4W)                                                                   ! update dissolved phosphate ODE
      !_SET_ODE_(self%id_CO2poolW,      wCZooCO2W)                                                                   ! update dissolved CO2 ODE
      _SET_ODE_(self%id_DPOMpoolW,     wDZooPOMW)                                                                   ! update particulate organic DW ODE
      _SET_ODE_(self%id_NPOMpoolW,     wNZooPOMW)                                                                   ! update particulate organic N ODE
      _SET_ODE_(self%id_PPOMpoolW,     wPZooPOMW)                                                                   ! update particulate organic P ODE
      _SET_ODE_(self%id_CPOMpoolW,     wCZooPOMW)                                                                   ! update particulate organic C ODE
      _SET_ODE_(self%id_SiPapoolW,     wSiPaZooW)                                                                   ! update particulate organic Si ODE
      _SET_ODE_(self%id_DDOMpoolW,     wDZooDOMW)                                                                   ! update dissolved organic DW ODE
      _SET_ODE_(self%id_NDOMpoolW,     wNZooDOMW)                                                                   ! update dissolved organic N ODE
      _SET_ODE_(self%id_PDOMpoolW,     wPZooDOMW)                                                                   ! update dissolved organic P ODE
      _SET_ODE_(self%id_CDOMpoolW,     wCZooDOMW)                                                                   ! update dissolved organic C ODE
      _SET_ODE_(self%id_SiO2poolW,     wSiO2ZooW)                                                                   ! update dissolved organic Si ODE
      !=============================================================================================================!
      ! 7.4 update diagnostic output processes                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_DIAGNOSTIC_(self%id_rPDZoo,       rPDZoo)                                                                ! 
      _SET_DIAGNOSTIC_(self%id_rNDZoo,       rNDZoo)                                                                ! 
      _SET_DIAGNOSTIC_(self%id_rCDZoo,       rCDZoo)                                                                ! 
      if (self%diagnostics) then                                                                                    !
         _SET_DIAGNOSTIC_(self%id_wDConsZooTot, wDConsZooTot)                                                       !                                                      
         _SET_DIAGNOSTIC_(self%id_wNConsZooTot, wNConsZooTot)                                                       !
         _SET_DIAGNOSTIC_(self%id_wPConsZooTot, wPConsZooTot)                                                       !
         _SET_DIAGNOSTIC_(self%id_wCConsZooTot, wCConsZooTot)                                                       !
         _SET_DIAGNOSTIC_(self%id_aFeedLvlZoo,  aFeedLvlZoo)                                                        !
         _SET_DIAGNOSTIC_(self%id_wDRespZoo,    wDRespZoo)                                                          !
         _SET_DIAGNOSTIC_(self%id_wCRespZoo,    wCRespZoo)                                                          !
         _SET_DIAGNOSTIC_(self%id_wDEgesZoo,    wDEgesZoo)                                                          !
         _SET_DIAGNOSTIC_(self%id_wNEgesZoo,    wNEgesZoo)                                                          !
         _SET_DIAGNOSTIC_(self%id_wPEgesZoo,    wPEgesZoo)                                                          !
         _SET_DIAGNOSTIC_(self%id_wDMortZoo,    wDMortZoo)                                                          !
         _SET_DIAGNOSTIC_(self%id_wNMortZoo,    wNMortZoo)                                                          !
         _SET_DIAGNOSTIC_(self%id_wPMortZoo,    wPMortZoo)                                                          !
         _SET_DIAGNOSTIC_(self%id_wCMortZoo,    wCMortZoo)                                                          !
         _SET_DIAGNOSTIC_(self%id_wDZooPOMW,    wDZooPOMW)                                                          !
         _SET_DIAGNOSTIC_(self%id_wNZooPOMW,    wNZooPOMW)                                                          !
         _SET_DIAGNOSTIC_(self%id_wPZooPOMW,    wPZooPOMW)                                                          !
         _SET_DIAGNOSTIC_(self%id_wCZooPOMW,    wCZooPOMW)                                                          !
         _SET_DIAGNOSTIC_(self%id_wDZooDOMW,    wDZooDOMW)                                                          !
         _SET_DIAGNOSTIC_(self%id_wNZooDOMW,    wNZooDOMW)                                                          !
         _SET_DIAGNOSTIC_(self%id_wPZooDOMW,    wPZooDOMW)                                                          !
         _SET_DIAGNOSTIC_(self%id_wCZooDOMW,    wCZooDOMW)                                                          !
         _SET_DIAGNOSTIC_(self%id_wNZooNH4W,    wNZooNH4W)                                                          !
         _SET_DIAGNOSTIC_(self%id_wPZooPO4W,    wPZooPO4W)                                                          !
         _SET_DIAGNOSTIC_(self%id_wSiO2ZooW,    wSiO2ZooW)                                                          !
         _SET_DIAGNOSTIC_(self%id_wSiPaZooW,    wSiPaZooW)                                                          !
         do i_prey = 1,self%nPrey                                                                                   !
             _SET_DIAGNOSTIC_(self%id_wDConsZoo(i_prey), wDConsZoo(i_prey))                                         !
             _SET_DIAGNOSTIC_(self%id_wPConsZoo(i_prey), wPConsZoo(i_prey))                                         !
             _SET_DIAGNOSTIC_(self%id_wNConsZoo(i_prey), wNConsZoo(i_prey))                                         !
             _SET_DIAGNOSTIC_(self%id_wCConsZoo(i_prey), wCConsZoo(i_prey))                                         !
		 end do                                                                                                     !
      endif                                                                                                         !
      !=============================================================================================================!
   _LOOP_END_ !!! END OF MODEL CODE::
end subroutine do
   
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: GET VERTICAL MOVEMENT                                                                                                                                                              §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine get_vertical_movement(self,_ARGUMENTS_GET_VERTICAL_MOVEMENT_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_zooplankton),intent(in)    :: self
   _DECLARE_ARGUMENTS_GET_VERTICAL_MOVEMENT_

   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk) :: O2, par
   integer  :: qSWIM
   
   _LOOP_BEGIN_  !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve oxygen concentration and determine vertical movements                                             !
   !================================================================================================================!
   if (self%qTrans == 2 .OR. self%qTrans ==3) then                                                                  ! transport method based on oxygen
      qSWIM = 0                                                                                                     !   default setting: no swimming
      if (self%qTrans == 3) then                                                                                    !   transport also based on light
         _GET_(self%id_par,par)                                                                                     !     get par level
         if (par .GT. self%cMaxLight) then                                                                          !     if light level is higher than tresholds
            qSWIM = -1                                                                                              !       swim down
         elseif (par .LT. self%cMinLight) then                                                                      !     if light level is less than tresholds
            qSWIM = 1                                                                                               !       swim up
         endif                                                                                                      !
      endif                                                                                                         !
      _GET_(self%id_oxygen,O2)                                                                                      !   get oxygen concentration
      if (O2 < self%cMinO2) then                                                                                    !   low oxygen induces vertical movement
         qSWIM = 1                                                                                                  !     swim up
      endif                                                                                                         !
   elseif (self%qTrans == 1) then
       qSWIM = 0
   endif                                                                                                            !
   _SET_VERTICAL_MOVEMENT_(self%id_sDZoo,qSWIM*self%cVswim)                                                         ! set DW migration speed
   _SET_VERTICAL_MOVEMENT_(self%id_sPZoo,qSWIM*self%cVswim)                                                         ! set P migration speed
   _SET_VERTICAL_MOVEMENT_(self%id_sNZoo,qSWIM*self%cVswim)                                                         ! set N migration speed
   _SET_VERTICAL_MOVEMENT_(self%id_sCZoo,qSWIM*self%cVswim)                                                         ! set C migration speed
   !================================================================================================================!
   _LOOP_END_   !!! END OF MODEL CODE::  
end subroutine get_vertical_movement

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: CALCULATE OPTIMAL DIET BREATH                                                                                                                                                      §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine calc_ODB(self,wDConsZoo,aFeedLvl,sDPrey,uFunTmZoo,sDZoo)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_zooplankton), intent(in), target :: self
   real(rk),                          intent(in)          :: sDPrey(:),uFunTmZoo,sDZoo
   real(rk),dimension(size(sDPrey)),  intent(out)         :: wDConsZoo
   real(rk),                          intent(out)         :: aFeedLvl
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)                           :: wDConsZoo_last, wDConsZooTot
   real(rk),dimension(size(sDPrey))   :: fGutOcc, FoodProf, wDConsZoo_temp
   integer                            :: i, maxid
   integer,dimension(size(sDPrey))    :: incl
   logical,dimension(size(sDPrey))    :: mask
   logical                            :: cease
   
   !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. determine macrophyte dependency, and calculate prey profitabilities                                        !
   !================================================================================================================!
   FoodProf = 1.0_rk/self%fGutOccPrey                                                                                        ! calculate food profitabilities
   mask(:) = .false.                                                                                                ! initialize mask (all positions are initially .false.) 
   cease = .false.                                                                                                  ! initialize flag for stopping the iterations
   i = 0                                                                                                            ! initialize iteration counter
   wDConsZoo_last = 0.0_rk                                                                                          ! initialize saved consumption variable
   wDConsZoo_temp(:) = 0.0_rk                                                                                       ! initialize temp. consumption variable
   incl(:) = 0                                                                                                      ! initialize included prey array
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. iterate over prey, and calculate optimal diet breadth and prey consumption                                 !
   !================================================================================================================!
   do while ((i < size(sDPrey)) .and. (cease .eqv. .false.))                                                        ! while no stop flag and not yet through all prey   
       i = i + 1                                                                                                    !    update iteration counter
       maxid = maxloc(FoodProf,DIM=1,MASK=.not. mask)                                                               !    find most profitable of remaining prey
       mask(maxid) = .true.                                                                                         !    include that prey in consumption calculation
       incl(maxid) = 1                                                                                              !
       aFeedLvl = sum(self%cClearPrey*self%fGutOccPrey*sDPrey*incl)/ &                                                                !    calculate feeding level using included prey
           (sum(self%cClearPrey*self%fGutOccPrey*sDPrey*incl) + uFunTmZoo*self%kDConsMaxZoo)                                          !
       wDConsZoo_temp = sDZoo*self%cClearPrey*sDPrey*incl*(1-aFeedLvl)                                                       ! calculate consumption of included prey
       wDConsZooTot = sum(wDConsZoo_temp)                                                                           !    sum up total consumption from included prey
       if (i > 1 .and. wDConsZooTot < wDConsZoo_last) then                                                          !    if new total consumption is lower than previous consumption
           cease = .true.                                                                                           !       stop iterating, and do not include latest prey
           incl(maxid) = 0                                                                                          !
       endif                                                                                                        !
       wDConsZoo_last = wDConsZooTot                                                                                !    save current highest total consumption
   end do                                                                                                           !
   aFeedLvl = sum(incl*self%cClearPrey*self%fGutOccPrey*sDPrey)/(sum(incl*self%cClearPrey*self%fGutOccPrey*sDPrey) + uFunTmZoo*self%kDConsMaxZoo)       ! calculate final feeding level, ignoring not included prey
   wDConsZoo = sDZoo*incl*self%cClearPrey*sDPrey*(1-aFeedLvl)                                                                ! calculate final consumption of all food, ignoring not included food
   !================================================================================================================!
end subroutine calc_ODB
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
end module wet_zooplankton
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
