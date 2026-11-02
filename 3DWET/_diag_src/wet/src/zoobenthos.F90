#include "fabm_driver.h"
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ MODULE: ZOOBENTHOS                                                                                                                                                                            §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
module wet_zoobenthos
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_expressions
   use fabm_particle
   use wet_utility, ONLY:uFunTmGaus
   implicit none
   private

   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public :: type_wet_zoobenthos
      ! local state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_bottom_state_variable_id)                            :: id_sDBent, id_sPBent, id_sNBent, id_sCBent
      type (type_state_variable_id)                                   :: id_sDBent_PV, id_sPBent_PV, id_sNBent_PV, id_sCBent_PV
      ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_model_id),                 allocatable, dimension(:) :: id_prey
      type (type_bottom_state_variable_id), allocatable, dimension(:) :: id_PreyD, id_PreyN, id_PreyP, id_PreyC
      type (type_state_variable_id),        allocatable, dimension(:) :: id_PreyD_PV, id_PreyN_PV, id_PreyP_PV, id_PreyC_PV
      type (type_horizontal_dependency_id), allocatable, dimension(:) :: id_PreySi
      type (type_bottom_state_variable_id)                            :: id_NH4poolS, id_NO3poolS, id_PO4poolS, id_SiPapoolS, id_DPOMpoolS, id_NPOMpoolS, id_PPOMpoolS, id_DDOMpoolS, id_NDOMpoolS
      type (type_bottom_state_variable_id)                            :: id_CPOMpoolS, id_CDOMpoolS
      type (type_state_variable_id)                                   :: id_DPOMpoolS_PV, id_NPOMpoolS_PV, id_PPOMpoolS_PV, id_CPOMpoolS_PV, id_DDOMpoolS_PV, id_NDOMpoolS_PV, id_PDOMpoolS_PV, id_CDOMpoolS_PV
      type (type_bottom_state_variable_id)                            :: id_PDOMpoolS, id_SiO2poolS
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDMigrBent, id_tNMigrBent, id_tPMigrBent, id_tDConsBentTot, id_tNConsBentTot, id_tPConsBentTot, id_fO2
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDEgesBent, id_tNEgesBent, id_tPEgesBent, id_tDRespBent, id_tPBentPO4S, id_tNBentNH4S, id_tDBentTPOMS, id_tNBentTPOMS, id_tPBentTPOMS 
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDBentDOMS, id_tNBentDOMS, id_tPBentDOMS, id_tDMortBent, id_tNMortBent, id_tPMortBent, id_tDMortO2, id_tSiO2BentS, id_tSiBentPaS
      type (type_horizontal_diagnostic_variable_id)                   :: id_tCMigrBent, id_tCConsBentTot, id_tCEgesBent, id_tCRespBent, id_tCBentPOMS, id_tCBentDOMS, id_tCMortBent
      type (type_horizontal_diagnostic_variable_id)                   :: id_rPDBent, id_rNDBent, id_rCDBent
      type (type_horizontal_diagnostic_variable_id), allocatable, dimension(:)   :: id_tDConsBent, id_tPConsBent, id_tNConsBent, id_tCConsBent
      ! environmental dependencies identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDBentPOMS
      type (type_dependency_id)                                       :: id_uTm, id_pO2Sat, id_aDSubVeg
      type (type_horizontal_dependency_id)                            :: id_bot_pel_conv
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      real(rk)                                                        :: cDBentIn, kMigrBent, cDCarrBent, fDAssBent, fDissEgesBent, kDRespBent, kMortBent, kMortO2, fDissMortBent
      real(rk)                                                        :: cNDRef, cDBentMin, fBentDOMS, cTmOptBent, cSigTmBent, hO2stress, cPDRef, cDVegCarr, kDConsMaxBent, cCDRef
      real(rk),                  allocatable, dimension(:)            :: cClearPrey, fGutOccPrey
      integer                                                         :: nPrey
      character(len=64),         allocatable, dimension(:)            :: prey_suffix
      logical,                   allocatable, dimension(:)            :: lSi
      logical                                                         :: diagnostics, lVegOpt
      
   contains
   
   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure :: initialize
   procedure :: do_bottom
   
   end type type_wet_zoobenthos
   
   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: NearZero=0.000000000000000000000000000000001_rk

contains
    
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_zoobenthos), intent(inout),      target :: self
   integer,                          intent(in)            :: configunit

   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer  :: i_prey
   character(len=64)   :: index

   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! population-level parameters---------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cDCarrBent,      'cDCarrBent',      'gDW/m2',   'carrying capacity',                                        default=10.0_rk                                         )
   call self%get_parameter(self%cDBentIn,        'cDBentIn',        'gDW/m2',   'external density',                                         default=0.01_rk                                         )
   call self%get_parameter(self%kMigrBent,       'kMigrBent',       '1/d',      'migration rate',                                           default=0.001_rk,        scale_factor=1.0_rk/secs_pr_day)
   ! prey parameters---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%nPrey,           'nPrey',           '-',        'number of prey types',                                     default=1                                               )                                                                                                                                                 
   allocate (self%lSi(self%nPrey))                                              
   allocate (self%prey_suffix(self%nPrey))
   allocate (self%cClearPrey(self%nPrey)) 
   allocate (self%fGutOccPrey(self%nPrey))
   do i_prey=1,self%nPrey                                                                                                                                                             
       write(index,'(i0)') i_prey                                                                                                                                                     
       call self%get_parameter(self%fGutOccPrey(i_prey),'fGutOccPrey'//trim(index),'-',       'gut occupation factor for prey '//trim(index),default=1.0_rk                                         )
       call self%get_parameter(self%cClearPrey(i_prey), 'cClearPrey'//trim(index), 'm2/gDW/d','clearance rate for prey '//trim(index),       default=0.015_rk,       scale_factor=1.0_rk/secs_pr_day)
       call self%get_parameter(self%lSi(i_prey),        'lSi'//trim(index),        '-', 'toggle prey silica tracking '//trim(index),        default=.false.                                         )
       call self%get_parameter(self%prey_suffix(i_prey),'prey_suffix'//trim(index),'-', 'prey name suffix '//trim(index),                   default=''                                              )
   end do
   ! vital parameters--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%kDConsMaxBent,   'kDConsMaxBent',   'gDW/gDW/d','standard dry weight specific maximum consumption rate',    default=0.33_rk,         scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%fDAssBent,       'fDAssBent',       '-',        'C assimilation efficiency',                                default=0.3_rk)
   call self%get_parameter(self%kDRespBent,      'kDRespBent',      '1/d',      'respiration rate at 20*C',                                 default=0.005_rk,        scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%kMortBent,       'kMortBent',       '1/d',      'mortality rate',                                           default=0.005_rk,        scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%hO2stress,       'hO2stress',       'pct',      'Michaelis-Menten constant for oxygen limitation',          default=25.0_rk                                         )
   call self%get_parameter(self%kMortO2,         'kMortO2',         '1/d',      'specific max. add. mortality due to oxygen stress',        default=0.05_rk,         scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%lVegOpt,         'lVegOpt',         '-',        'switch for macrophyte dependence on zoobenthos carrying capacity',default=.false.                                  )
   call self%get_parameter(self%cDVegCarr,       'cDVegCarr',       'gDW/m2/gDW','lVegOpt = .true.; scaling factor for carr cap. with macrophyte biomass', default=0.025_rk                         )
   ! stochiometric parameters------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%fDissEgesBent,   'fDissEgesBent',   '-',        'soluble inorg. nut. fract. of egested food',               default=0.25_rk                                         )
   call self%get_parameter(self%fDissMortBent,   'fDissMortBent',   '-',        'soluble inorg. nut. fract. of dead ind.',                  default=0.1_rk                                          )
   call self%get_parameter(self%cPDRef,          'cPDRef',          'gP/gDW',   'reference P/DW ratio',                                     default=0.01_rk                                         )
   call self%get_parameter(self%cNDRef,          'cNDRef',          'gN/gDW',   'reference N/DW ratio',                                     default=0.07_rk                                         )
   call self%get_parameter(self%cCDRef,          'cCDRef',          'gC/gDW',   'reference C/DW ratio',                                     default=0.45_rk                                         )
   call self%get_parameter(self%fBentDOMS,       'fBentDOMS',        '-',       'DOM fraction of dead individuals',                         default=0.5_rk                                          )
   ! temperature parameters---------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cTmOptBent,      'cTmOptBent',      '*C',       'optimal temperature',                                      default=25.0_rk                                         )
   call self%get_parameter(self%cSigTmBent,      'cSigTmBent',      '*C',       'temp. constant; sigma in Gaussian curve',                  default=16.0_rk                                         )
   ! diagnostic  parameter---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,     'diagnostics',     '-',        'toggle diagnostic output',                                 default=.false.                                         )

   !REGISTER MODEL VARIBLES, DEPENDENCIES & COUPLINGS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! local state variables---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sDBent,      'sD',      'gDW/m2',    'DW',          initial_value=1.0_rk,    minimum=0.0_rk                                                            )
   call self%register_state_variable(self%id_sPBent,      'sP',      'gP/m2',     'P',           initial_value=0.1_rk,    minimum=0.0_rk                                                            )
   call self%register_state_variable(self%id_sNBent,      'sN',      'gN/m2',     'N',           initial_value=0.01_rk,   minimum=0.0_rk                                                            )
   call self%register_state_variable(self%id_sCBent,      'sC',      'gC/m2',     'C',           initial_value=0.40_rk,   minimum=0.0_rk                                                            )
   
   call self%register_state_variable(self%id_sDBent_PV,   'sD_PV',   'gDW/m2',    'DW pel. var', initial_value=1.0_rk,    minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)                     
   call self%register_state_variable(self%id_sPBent_PV,   'sP_PV',   'gP/m2',     'P pel. var',  initial_value=0.1_rk,    minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)                                   
   call self%register_state_variable(self%id_sNBent_PV,   'sN_PV',   'gN/m2',     'N pel. var',  initial_value=0.01_rk,   minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)
   call self%register_state_variable(self%id_sCBent_PV,   'sC_PV',   'gC/m2',     'C pel. var',  initial_value=0.40_rk,   minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE.)
   call self%set_variable_property(self%id_sDBent_PV,     'disable_transport',    .true.)   
   call self%set_variable_property(self%id_sNBent_PV,     'disable_transport',    .true.)
   call self%set_variable_property(self%id_sPBent_PV,     'disable_transport',    .true.)  
   call self%set_variable_property(self%id_sCBent_PV,     'disable_transport',    .true.)  
   ! register diagnostic variables-------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_tDBentPOMS,          'tDBentPOMS', 'g/m2/s','tDBentPOMS', output=output_none,domain=domain_bottom,source=source_do_bottom)
   ! Register diagnostic process output--------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_rPDBent,          'rPDBent',      'gP/gDW','P/D ratio',                output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_rNDBent,          'rNDBent',      'gN/gDW','N/D ratio',                output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_rCDBent,          'rCDBent',      'gC/gDW','C/D ratio',                output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
   if (self%diagnostics) then
       call self%register_diagnostic_variable(self%id_tDMigrBent,   'tDMigrBent',   'g/m2/s','rate DW migrated',         output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNMigrBent,   'tNMigrBent',   'g/m2/s','rate N migrated',          output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPMigrBent,   'tPMigrBent',   'g/m2/s','rate P migrated',          output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCMigrBent,   'tCMigrBent',   'g/m2/s','rate C migrated',          output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDConsBentTot,'tDConsBentTot','g/m2/s','rate D prey consumed',     output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNConsBentTot,'tNConsBentTot','g/m2/s','rate N prey consumed',     output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPConsBentTot,'tPConsBentTot','g/m2/s','rate P prey consumed',     output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCConsBentTot,'tCConsBentTot','g/m2/s','rate C prey consumed',     output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDEgesBent,   'tDEgesBent',   'g/m2/s','rate DW egested',          output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNEgesBent,   'tNEgesBent',   'g/m2/s','rate N egested',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPEgesBent,   'tPEgesBent',   'g/m2/s','rate P egested',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCEgesBent,   'tCEgesBent',   'g/m2/s','rate C egested',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDRespBent,   'tDRespBent',   'g/m2/s','rate DW respired',         output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCRespBent,   'tCRespBent',   'g/m2/s','rate C respired',          output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPBentPO4S,   'tPBentPO4S',   'g/m2/s','rate PO4S out',            output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNBentNH4S,   'tNBentNH4S',   'g/m2/s','rate NH4S out',            output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDBentTPOMS,  'tDBentTPOMS',  'g/m2/s','rate DPOMS out',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDBentDOMS,   'tDBentDOMS',   'g/m2/s','rate DDOMS out',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNBentTPOMS,  'tNBentTPOMS',  'g/m2/s','rate NPOMS out',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNBentDOMS,   'tNBentDOMS',   'g/m2/s','rate NDOMS out',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPBentTPOMS,  'tPBentTPOMS',  'g/m2/s','rate PPOMS out',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPBentDOMS,   'tPBentDOMS',   'g/m2/s','rate PDOMS out',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCBentPOMS,   'tCBentPOMS',   'g/m2/s','rate CPOMS out',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCBentDOMS,   'tCBentDOMS',   'g/m2/s','rate CDOMS out',           output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDMortBent,   'tDMortBent',   'g/m2/s','rate DW from mortality',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNMortBent,   'tNMortBent',   'g/m2/s','rate N from mortality',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPMortBent,   'tPMortBent',   'g/m2/s','rate P from mortality',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCMortBent,   'tCMortBent',   'g/m2/s','rate C from mortality',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDMortO2,     'tDMortO2',     'g/m2/s','rate DW from mort. due to O2', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_fO2,          'fO2',          '-',    'oxygen stress fraction',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tSiO2BentS,   'tSiO2BentS',   'g/m2/s','rate SiO2W egested',       output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tSiBentPaS,   'tSiBentPaS',   'g/m2/s','rate Si partic. S egested',output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
   endif    
   ! Register contribution of state to global aggregate variables------------------------------------------------------------------------------------------------------------------------------------
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_tDPOMbio',units='gDW/m2/s',aggregate_variable=.true.),self%id_tDBentPOMS,scale_factor=1._rk)
   ! register state variable dependencies------------------------------------------------------------------------------------------------------------------------------------------------------------
   allocate(self%id_prey(self%nPrey))
   allocate(self%id_PreyD(self%nPrey))
   allocate(self%id_PreyP(self%nPrey))
   allocate(self%id_PreyN(self%nPrey))
   allocate(self%id_PreyC(self%nPrey))
   allocate(self%id_PreyD_PV(self%nPrey))
   allocate(self%id_PreyP_PV(self%nPrey))
   allocate(self%id_PreyN_PV(self%nPrey))
   allocate(self%id_PreyC_PV(self%nPrey))
   allocate(self%id_PreySi(self%nPrey))
   allocate(self%id_tDConsBent(self%nPrey))
   allocate(self%id_tPConsBent(self%nPrey))
   allocate(self%id_tNConsBent(self%nPrey))
   allocate(self%id_tCConsBent(self%nPrey))
   do i_prey=1,self%nPrey
       write(index,'(i0)') i_prey
       call self%register_model_dependency(self%id_prey(i_prey), 'prey_model'//trim(index))
       call self%register_state_dependency(self%id_PreyD(i_prey), 'Prey_D_'//trim(index), 'g/m3', 'prey D'//trim(index))
       call self%register_state_dependency(self%id_PreyN(i_prey), 'Prey_N_'//trim(index), 'g/m3', 'prey N'//trim(index))
       call self%register_state_dependency(self%id_PreyP(i_prey), 'Prey_P_'//trim(index), 'g/m3', 'prey P'//trim(index))
       call self%register_state_dependency(self%id_PreyC(i_prey), 'Prey_C_'//trim(index), 'g/m3', 'prey C'//trim(index))
       call self%request_coupling_to_model(self%id_PreyD(i_prey),self%id_prey(i_prey), 'sD'//trim(self%prey_suffix(i_prey)))
       call self%request_coupling_to_model(self%id_PreyP(i_prey),self%id_prey(i_prey), 'sP'//trim(self%prey_suffix(i_prey)))
       call self%request_coupling_to_model(self%id_PreyN(i_prey),self%id_prey(i_prey), 'sN'//trim(self%prey_suffix(i_prey)))
       call self%request_coupling_to_model(self%id_PreyC(i_prey),self%id_prey(i_prey), 'sC'//trim(self%prey_suffix(i_prey)))
       
       call self%register_state_dependency(self%id_PreyD_PV(i_prey), 'Prey_D_'//trim(index)//'_PV', 'g/m3', 'prey D PV target number '//trim(index))
       call self%register_state_dependency(self%id_PreyN_PV(i_prey), 'Prey_N_'//trim(index)//'_PV', 'g/m3', 'prey N PV target number '//trim(index))
       call self%register_state_dependency(self%id_PreyP_PV(i_prey), 'Prey_P_'//trim(index)//'_PV', 'g/m3', 'prey P PV target number '//trim(index))
       call self%register_state_dependency(self%id_PreyC_PV(i_prey), 'Prey_C_'//trim(index)//'_PV', 'g/m3', 'prey C PV target number '//trim(index))
       call self%request_coupling_to_model(self%id_PreyD_PV(i_prey),self%id_prey(i_prey), 'sD'//trim(self%prey_suffix(i_prey))//'_PV')
       call self%request_coupling_to_model(self%id_PreyP_PV(i_prey),self%id_prey(i_prey), 'sP'//trim(self%prey_suffix(i_prey))//'_PV')
       call self%request_coupling_to_model(self%id_PreyN_PV(i_prey),self%id_prey(i_prey), 'sN'//trim(self%prey_suffix(i_prey))//'_PV')
       call self%request_coupling_to_model(self%id_PreyC_PV(i_prey),self%id_prey(i_prey), 'sC'//trim(self%prey_suffix(i_prey))//'_PV')
       
       if (self%lSi(i_prey)) then
           call self%register_horizontal_dependency(self%id_PreySi(i_prey), 'Prey_Si_'//trim(index), 'g/m3', 'prey Si'//trim(index))
           call self%request_coupling_to_model(self%id_PreySi(i_prey),self%id_prey(i_prey), 'oSi'//trim(self%prey_suffix(i_prey)))
       endif
       if (self%diagnostics) then
	       call self%register_diagnostic_variable(self%id_tDConsBent(i_prey),'tDConsBent_'//trim(index),'g/m3/s','rate D consumed '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tPConsBent(i_prey),'tPConsBent_'//trim(index),'g/m3/s','rate P consumed '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tNConsBent(i_prey),'tNConsBent_'//trim(index),'g/m3/s','rate N consumed '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tCConsBent(i_prey),'tCConsBent_'//trim(index),'g/m3/s','rate C consumed '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       endif 
   end do
   call self%register_state_dependency(self%id_DPOMpoolS,    'POM_DW_pool_sediment',        'g/m2',   'particulate organic matter DW pool in sediment')
   call self%register_state_dependency(self%id_PPOMpoolS,    'POM_P_pool_sediment',         'g/m2',   'particulate organic matter P pool in sediment')
   call self%register_state_dependency(self%id_NPOMpoolS,    'POM_N_pool_sediment',         'g/m2',   'particulate organic matter N pool in sediment')
   call self%register_state_dependency(self%id_CPOMpoolS,    'POM_C_pool_sediment',         'g/m2',   'particulate organic matter C pool in sediment')
   call self%register_state_dependency(self%id_DPOMpoolS_PV, 'POM_DW_pool_sediment_PV',     'g/m2',   'particulate organic matter DW pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_PPOMpoolS_PV, 'POM_P_pool_sediment_PV',      'g/m2',   'particulate organic matter P pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_NPOMpoolS_PV, 'POM_N_pool_sediment_PV',      'g/m2',   'particulate organic matter N pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_CPOMpoolS_PV, 'POM_C_pool_sediment_PV',      'g/m2',   'particulate organic matter C pool in sediment pelagic mirror')

   call self%register_state_dependency(self%id_SiPapoolS,    'SiPa_pool_sediment',          'g/m2',   'particulate Si pool sediment')
   call self%register_state_dependency(self%id_NH4poolS,     'NH4_pool_sediment',           'g/m2',   'NH4 pool in sediment')
   call self%register_state_dependency(self%id_NO3poolS,     'NO3_pool_sediment',           'g/m2',   'NO3 pool in sediment')
   call self%register_state_dependency(self%id_PO4poolS,     'PO4_pool_sediment',           'g/m2',   'PO4 pool in sediment')
   call self%register_state_dependency(self%id_DDOMpoolS,    'DOM_DW_pool_sediment',        'g/m2',   'dissolved organic matter DW in sediment')
   call self%register_state_dependency(self%id_NDOMpoolS,    'DOM_N_pool_sediment',         'g/m2',   'dissolved organic matter N in sediment')
   call self%register_state_dependency(self%id_PDOMpoolS,    'DOM_P_pool_sediment',         'g/m2',   'dissolved organic matter P in sediment')
   call self%register_state_dependency(self%id_CDOMpoolS,    'DOM_C_pool_sediment',         'g/m2',   'dissolved organic matter C in sediment')
   call self%register_state_dependency(self%id_DDOMpoolS_PV, 'DOM_DW_pool_sediment_PV',     'g/m2',   'dissolved organic matter DW pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_PDOMpoolS_PV, 'DOM_P_pool_sediment_PV',      'g/m2',   'dissolved organic matter P pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_NDOMpoolS_PV, 'DOM_N_pool_sediment_PV',      'g/m2',   'dissolved organic matter N pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_CDOMpoolS_PV, 'DOM_C_pool_sediment_PV',      'g/m2',   'dissolved organic matter C pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_SiO2poolS,    'SiO2_pool_sediment',          'g/m2',   'dissolved SiO2 in sediment')
   ! register environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_uTm,      standard_variables%temperature)
   call self%register_dependency(self%id_pO2Sat,   'pO2Sat', 'pct', 'oxygen saturation')
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')
   call self%register_dependency(self%id_aDSubVeg,type_bulk_standard_variable(name='total_aDSubVeg',units='gDW/m2'))

   return

end subroutine initialize

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO BOTTOM                                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_zoobenthos), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)                        :: sDBent, sPBent, sNBent, uTm, bot_pel_conv, rPDBent, rNDBent, rPDFoodBent, rNDFoodBent, uFunTmBent, fO2, pO2Sat, tDBenBent, tDMigrBent, aDSubVeg
   real(rk)                        :: tDRespBent, tDMortBent, tDMortO2, tDAssBent, aDSatBent, tDEnvBent, ukDIncrBent, tPBenBent, tPMigrBent, tPAssBent, tPExcrBent, tPMortBent, afPAssBent, tNBenBent
   real(rk)                        :: tNExcrBent, tNMortBent, afNAssBent, tNMigrBent, tNAssBent, tNBentNH4S, tNEgesBentNH4, tNEgesBent, tNMortBentNH4, tNBentNO3S, tPBentPO4S, tPEgesBentPO4, tPEgesBent
   real(rk)                        :: tDBentPOMS, tDEgesBent, tNBentPOMS, tNBentTPOMS, tNEgesBentTOM, tPMortBentPO4, tNMortBentTOM, tPBentPOMS, tPEgesBentTOM, tPMortBentTOM, tSiBentPaS, tDBentTOMS, tDBentTPOMS, tNBentTOMS
   real(rk)                        :: tDBentDOMS, tNBentDOMS, tPBentDOMS, tSiO2BentS, tPBentTOMS, tPBentTPOMS, oDFoodBent, tDConsBentTot, tNConsBentTot, tPConsBentTot, sDPOM, sNPOM, sPPOM, rNDPOM, rPDPOM
   real(rk)                        :: sCBent, rCDBent, rCDFoodBent, tCConsBentTot, afCAssBent, tCAssBent, aCorDRespBent, tCRespBent, tCEgesBent, tCMigrBent, tCMortBent, tCBenBent
   real(rk)                        :: tCBentCO2S, tCBentTOMS, tCBentPOMS, tCBentDOMS, tCBentTPOMS
   real(rk)                        :: fAssBentVeg, aFunVegAss, cDCarrBentVeg, aFeedLvlBent 
   real(rk), dimension(self%nPrey) :: sPprey, sDprey, sNprey, sCprey, rNDprey, rPDprey, rCDprey, sSiprey, tDConsBent, tNConsBent, tPConsBent, tCConsBent                                                        
   integer                         :: i_prey                                                                                                                                
   character(len=64)               :: index                                                                                         

   _HORIZONTAL_LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
      ! 1.1 retrieve environmental dependencies                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _GET_(self%id_uTm,uTm)                                                                                        ! get local temperature
      _GET_(self%id_pO2Sat,pO2Sat)                                                                                  ! get local oxygen saturation
      _GET_(self%id_aDSubVeg,aDSubVeg)                                                                              ! get macrophyte biomass
      !=============================================================================================================!
      ! 1.2 retrieve state variables, & calc. current local nutrient ratios and relative abundances                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.2.1 zoobenthos state variables                                                                         !
         !----------------------------------------------------------------------------------------------------------!
         _GET_HORIZONTAL_(self%id_sDBent,sDBent)                                                                    ! get zoobenthos dry weight
         _GET_HORIZONTAL_(self%id_sPBent,sPBent)                                                                    ! get zoobenthos phosphorous
         _GET_HORIZONTAL_(self%id_sNBent,sNBent)                                                                    ! get zoobenthos nitrogen
         _GET_HORIZONTAL_(self%id_sCBent,sCBent)                                                                    ! get zoobenthos carbon
         rPDBent=sPBent/(sDBent+NearZero)                                                                           ! calculate N:DW ratio
         rNDBent=sNBent/(sDBent+NearZero)                                                                           ! calculate P:DW ratio
         rCDBent=sCBent/(sDBent+NearZero)                                                                           ! calculate C:DW ratio
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.2.2 prey state variables                                                                               !
         !----------------------------------------------------------------------------------------------------------!
         do i_prey=1,self%nPrey                                                                                     ! for each prey
            _GET_HORIZONTAL_(self%id_PreyD(i_prey),sDprey(i_prey))                                                  ! get prey dry weight (dimensions: nPrey)
            _GET_HORIZONTAL_(self%id_PreyP(i_prey),sPprey(i_prey))                                                  ! get prey phosphorous (dimensions: nPrey)
            _GET_HORIZONTAL_(self%id_PreyN(i_prey),sNprey(i_prey))                                                  ! get prey nitrogen (dimensions: nPrey)
            _GET_HORIZONTAL_(self%id_PreyC(i_prey),sCprey(i_prey))                                                  ! get prey carbon (dimensions: nPrey)
            if (self%lSi(i_prey)) then                                                                              !   check whether Silica is tracked
               _GET_HORIZONTAL_(self%id_PreySi(i_prey),sSiprey(i_prey))                                             !     get prey silica (dimensions: nPrey)
            else                                                                                                    !   if silica is not tracked
                sSiprey(i_prey) = 0.0_rk                                                                            !     then content is set to zero
            endif                                                                                                   !
         end do                                                                                                     !
         rNDprey = sNprey/(sDprey+NearZero)                                                                         ! calculate prey N:DW ratios (dimensions: nPrey)
         rPDprey = sPprey/(sDprey+NearZero)                                                                         ! calculate prey P:DW ratios (dimensions: nPrey)
         rCDprey = sCprey/(sDprey+NearZero)                                                                         ! calculate prey C:DW ratios (dimensions: nPrey)
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!                                                          
   !  2. calculate growth and assimilation of DW                                                                    !                                                           
   !================================================================================================================!                                                          
      ! 2.1.1 temperature function                                                                                  ! 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                          
      uFunTmBent = uFunTmGaus(uTm,self%cSigTmBent,self%cTmOptBent)                                                  ! calc. temperature correction of zoobenthos vital rates
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      ! 2.1.2 oxygen stress function                                                                                ! 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                          
      fO2 = max(0.0_rk, pO2Sat**4 / max(NearZero,(self%hO2stress**4 + pO2Sat**4)))                                  ! calc. oxygen stress correction of zoobenthos vital rates
      !=============================================================================================================!
      ! 2.2 calculate prey consumption and environmental correction                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      aFeedLvlBent = sum(self%cClearPrey*self%fGutOccPrey*sDPrey) / &                                               !   calculate feeding level, based on all available zoobenthos prey
          (sum(self%cClearPrey*self%fGutOccPrey*sDPrey) + uFunTmBent*fO2*self%kDConsMaxBent)                        !
      tDConsBent = sDBent*self%cClearPrey*sDPrey*(1-aFeedLvlBent)                                                   !   calculate consumption of all available zoobenthos prey
      cDCarrBentVeg = self%cDVegCarr * aDSubVeg                                                                     !
      tDEnvBent = max(0.0_rk,(((self%kDConsMaxBent*self%fDAssBent-self%kDRespBent)*uFunTmBent*fO2-self%kMortBent) / &  !
          (self%cDCarrBent + cDCarrBentVeg)) * sDBent*sDBent)                                                       ! calculate environmental correction
      tDAssBent = self%fDAssBent * sum(tDConsBent)                                                                  ! calculate total assimilation - environmental correction from PCLake removed.
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 3. calculate prey consumption rates (DW, N & P)                                                                !
   !================================================================================================================!
   tNConsBent = tDConsBent * rNDprey                                                                                ! calculate prey N consumption (dimensions: nPrey)
   tPConsBent = tDConsBent * rPDprey                                                                                ! calculate prey P consumption (dimensions: nPrey)
   tCConsBent = tDConsBent * rCDprey                                                                                ! calculate prey C consumption (dimensions: nPrey)
   tDConsBentTot = sum(tDConsBent)                                                                                  ! calculate total prey DW consumption
   tNConsBentTot = sum(tNConsBent)                                                                                  ! calculate total prey N consumption
   tPConsBentTot = sum(tPConsBent)                                                                                  ! calculate total prey P consumption
   tCConsBentTot = sum(tCConsBent)                                                                                  ! calculate total prey P consumption
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. calculate N, and P assimilation                                                                             !
   !================================================================================================================!
      ! 4.1 nitrogen                                                                                                !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      rNDFoodBent = tNConsBentTot / max(NearZero,tDConsBentTot)                                                     ! calculate total available prey N ratio
      afNAssBent = min(1.0_rk,self%cNDRef / rNDFoodBent * self%fDAssBent)                                           ! calculate N assimilation efficiency
      tNAssBent = afNAssBent * tNConsBentTot                                                                        ! calculate N assimilation rate
      !=============================================================================================================!
      ! 4.2 phosphorous                                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      rPDFoodBent = tPConsBentTot / max(NearZero,tDConsBentTot)                                                     ! calculate total available prey P ratio
      afPAssBent = min(1.0_rk,self%cPDRef / rPDFoodBent * self%fDAssBent)                                           ! calculate P assimilation efficiency
      tPAssBent = afPAssBent * tPConsBentTot                                                                        ! calculate P assimilation rate
      !=============================================================================================================!
      ! 4.3 carbon                                                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      rCDFoodBent = tCConsBentTot / max(NearZero,tDConsBentTot)                                                     ! calculate total available prey P ratio
      afCAssBent = min(1.0_rk,self%cCDRef / rCDFoodBent * self%fDAssBent)                                           ! calculate P assimilation efficiency
      tCAssBent = afCAssBent * tCConsBentTot                                                                        ! calculate P assimilation rate
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 5. calculate respiration, egestion, excretion, mortality and migration                                         !
   !================================================================================================================!
      ! 5.1 calculate respiration/excretion                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      ! aCorDRespBent = max(self%cPDRef / rPDBent,self%cNDRef / rNDBent, self%cCDRef / rCDBent)                       ! calculate corr. factor between respiration and P, N, C content
      aCorDRespBent = self%cPDRef / rPDBent
      tDRespBent = aCorDRespBent * self%kDRespBent * uFunTmBent * fO2 * sDBent                                      ! calculate respiration (in DW)
      tCRespBent = (rCDBent / self%cCDRef) * self%kDRespBent * uFunTmBent * fO2 * sCBent                            ! calculate C respiration
      tPExcrBent = (rPDBent / self%cPDRef) * self%kDRespBent * uFunTmBent * fO2 * sPBent                            ! calculate P excretion
      tNExcrBent = (rNDBent / self%cNDRef) * self%kDRespBent * uFunTmBent * fO2 * sNBent                            ! calculate N excretion
      !=============================================================================================================!
      ! 5.2 calculate egestion                                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDEgesBent = tDConsBentTot - tDAssBent                                                                        ! calculate DW egestion
      tNEgesBent = tNConsBentTot - tNAssBent                                                                        ! calculate N egestion
      tPEgesBent = tPConsBentTot - tPAssBent                                                                        ! calculate P egestion
      tCEgesBent = tCConsBentTot - tCAssBent                                                                        ! calculate C egestion
      !=============================================================================================================!
      ! 5.3 calculate mortality                                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDMortO2 = self%kMortO2 *sDBent *  (1 - fO2) * uFunTmBent                                                     ! calculate add. mortality due to O2 stress
      tDMortBent = self%kMortBent*sDBent + tDEnvBent + tDMortO2                                                     ! calculate mortality in DW
      tPMortBent = rPDBent * tDMortBent                                                                             ! calculate mortality in P
      tNMortBent = rNDBent * tDMortBent                                                                             ! calculate mortality in N
      tCMortBent = rCDBent * tDMortBent                                                                             ! calculate mortality in C
      !=============================================================================================================!                                                          
      ! 5.4 migration flux                                                                                          ! 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                          
      tDMigrBent = self%kMigrBent *(self%cDBentIn - sDBent)                                                         ! calculate migration in DW
      tPMigrBent = self%kMigrBent *(self%cPDRef*self%cDBentIn - sPBent)                                             ! calculate migration in P
      tNMigrBent = self%kMigrBent *(self%cNDRef*self%cDBentIn - sNBent)                                             ! calculate migration in N
      tCMigrBent = self%kMigrBent *(self%cCDRef*self%cDBentIn - sCBent)                                             ! calculate migration in C
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 6. final flux calculations                                                                                     !
   !================================================================================================================!
      ! 6.1 final zoobenthos rate of change                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDBenBent = tDMigrBent + tDAssBent - tDRespBent - tDMortBent                                                  ! calculate final rate of change of DW
      tPBenBent = tPMigrBent + tPAssBent - tPExcrBent - tPMortBent                                                  ! calculate final rate of change of P
      tNBenBent = tNMigrBent + tNAssBent - tNExcrBent - tNMortBent                                                  ! calculate final rate of change of N
      tCBenBent = tCMigrBent + tCAssBent - tCRespBent - tCMortBent                                                  ! calculate final rate of change of C
      !=============================================================================================================!
      ! 6.2 final fluxes to external abiotic variables                                                              !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.1 dry weight                                                                                         !
         !----------------------------------------------------------------------------------------------------------!
         tDBentTOMS = tDEgesBent + tDMortBent                                                                       ! calculate total flux of DW to the sediment
         tDBentTPOMS = tDBentTOMS * (1.0_rk -self%fBentDOMS)                                                        ! calculate particulate organic DW flux from zoobenthos
         tDBentPOMS = tDBentTPOMS                                                                                   ! calculate particulate fraction of DW flux
         tDBentDOMS = tDBentTOMS * self%fBentDOMS                                                                   ! calculate dissolved fraction of DW flux
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.2 nitrogen                                                                                           !
         !----------------------------------------------------------------------------------------------------------!
         tNMortBentNH4 = self%fDissMortBent*tNMortBent                                                              ! calculate ammonia fraction of mortality flux to the sediment
         tNEgesBentNH4 = self%fDissEgesBent * tNEgesBent                                                            ! calculate ammonia fraction of egestion flux to the sediment
         tNBentNH4S = tNExcrBent + tNEgesBentNH4 + tNMortBentNH4                                                    ! calculate total ammonia flux to the sediment
         tNBentNO3S = 0.0_rk                                                                                        ! calculate total nitrate flux to the sediment
         tNMortBentTOM = (1.0_rk-self%fDissMortBent)*tNMortBent                                                     ! calculate organic fraction of mortality N flux to the sediment
         tNEgesBentTOM = (1.0_rk - self%fDissEgesBent) * tNEgesBent                                                 ! calculate organic fraction of egestion N flux to the sediment
         tNBentTOMS = tNEgesBentTOM + tNMortBentTOM                                                                 ! calculate total organic N flux to the sediment
         tNBentTPOMS = tNBentTOMS * (1.0_rk - self%fBentDOMS)                                                       ! calculate particulate organic N flux from zoobenthos
         tNBentPOMS = tNBentTPOMS                                                                                   ! calculate total particulate organic N flux to the sediment
         tNBentDOMS = tNBentTOMS * self%fBentDOMS                                                                   ! calculate total dissolved organic N flux to the sediment
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.3 phosphorous                                                                                        !
         !----------------------------------------------------------------------------------------------------------!
         tPMortBentPO4 = self%fDissMortBent * tPMortBent                                                            ! calculate phosphate fraction of mortality flux to the sediment
         tPEgesBentPO4 = self%fDissEgesBent * tPEgesBent                                                            ! calculate phosphate fraction of egestion flux to the sediment
         tPBentPO4S = tPExcrBent + tPEgesBentPO4 + tPMortBentPO4                                                    ! calculate total phosphate flux to the sediment
         tPMortBentTOM = (1.0_rk-self%fDissMortBent)*tPMortBent                                                     ! calculate organic fraction of mortality P flux to the sediment
         tPEgesBentTOM = (1.0_rk - self%fDissEgesBent) * tPEgesBent                                                 ! calculate organic fraction of egestion P flux to the sediment
         tPBentTOMS = tPEgesBentTOM + tPMortBentTOM                                                                 ! calculate total organic P flux to the sediment
         tPBentTPOMS = tPBentTOMS * (1.0_rk -self%fBentDOMS)                                                        ! calculate particulate organic P flux from zoobenthos
         tPBentPOMS = tPBentTPOMS                                                                                   ! calculate particulate organic P flux to the sediment
         tPBentDOMS = tPBentTOMS * self%fBentDOMS                                                                   ! calculate dissolved fraction of organic P flux to the sediment
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.4 carbon                                                                                             !
         !----------------------------------------------------------------------------------------------------------!
         tCBentCO2S = tCRespBent                                                                                    ! calculate total CO2 flux to the sediment
         tCBentTOMS = tCEgesBent + tCMortBent                                                                       ! calculate total organic C flux to the sediment
         tCBentTPOMS = tCBentTPOMS * (1.0_rk -self%fBentDOMS)                                                       ! calculate particulate organic C flux from zoobenthos
         tCBentPOMS =  tCBentTPOMS                                                                                  ! calculate particulate fraction of C flux
         tCBentDOMS = tCBentTPOMS * self%fBentDOMS                                                                  ! calculate dissolved fraction of organic C flux to the sediment
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 6.2.5 silica                                                                                             !
         !----------------------------------------------------------------------------------------------------------!
         tSiBentPaS = sum((sSiprey/sDprey) * tDConsBent) * (1.0_rk - self%fBentDOMS)                                ! flux of silica to the water column, particulate fraction
         tSiO2BentS = sum((sSiprey/sDprey) * tDConsBent) * self%fBentDOMS                                           ! flux of silica to the water column, dissolved fraction
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 7. update model variables                                                                                      !
   !================================================================================================================!
      ! 7.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_ODE_(self%id_sDBent,tDBenBent)                                                                    ! update zoobenthos DW ODE
      _SET_BOTTOM_ODE_(self%id_sPBent,tPBenBent)                                                                    ! update zoobenthos N ODE
      _SET_BOTTOM_ODE_(self%id_sNBent,tNBenBent)                                                                    ! update zoobenthos P ODE
      _SET_BOTTOM_ODE_(self%id_sCBent,tCBenBent)                                                                    ! update zoobenthos C ODE
      _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)                                                           ! 
      _SET_BOTTOM_EXCHANGE_(self%id_sDBent_PV,tDBenBent*bot_pel_conv)                                               ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      _SET_BOTTOM_EXCHANGE_(self%id_sPBent_PV,tPBenBent*bot_pel_conv)                                               ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      _SET_BOTTOM_EXCHANGE_(self%id_sNBent_PV,tNBenBent*bot_pel_conv)                                               ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      _SET_BOTTOM_EXCHANGE_(self%id_sCBent_PV,tCBenBent*bot_pel_conv)                                               ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      !=============================================================================================================!
      ! 7.2 update external biotic state variables                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      do i_prey = 1,self%nPrey                                                                                      ! for earch zoop. prey
         _SET_BOTTOM_ODE_(self%id_PreyD(i_prey),-tDConsBent(i_prey))                                                !   update prey DW ODEs
         _SET_BOTTOM_ODE_(self%id_PreyN(i_prey),-tNConsBent(i_prey))                                                !   update prey N ODEs
         _SET_BOTTOM_ODE_(self%id_PreyP(i_prey),-tPConsBent(i_prey))                                                !   update prey P ODEs
         _SET_BOTTOM_ODE_(self%id_PreyC(i_prey),-tCConsBent(i_prey))                                                !   update prey C ODEs
         _SET_BOTTOM_EXCHANGE_(self%id_PreyD_PV(i_prey),-tDConsBent(i_prey)*bot_pel_conv)                           !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_PreyN_PV(i_prey),-tNConsBent(i_prey)*bot_pel_conv)                           !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_PreyP_PV(i_prey),-tPConsBent(i_prey)*bot_pel_conv)                           !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_PreyC_PV(i_prey),-tCConsBent(i_prey)*bot_pel_conv)                           !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      end do                                                                                                        !
      !=============================================================================================================!
      ! 7.3 update external abiotic state variables                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_ODE_(self%id_NH4poolS,  tNBentNH4S)                                                               ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_NO3poolS,  tNBentNO3S)                                                               ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_PO4poolS,  tPBentPO4S)                                                               ! update the abiotic variables
      !_SET_BOTTOM_ODE_(self%id_CO2poolS,  tCBentCO2S)                                                               ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_DPOMpoolS, tDBentPOMS)                                                               ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_NPOMpoolS, tNBentPOMS)                                                               ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_PPOMpoolS, tPBentPOMS)                                                               ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_CPOMpoolS, tCBentPOMS)                                                               ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolS_PV, tNBentPOMS*bot_pel_conv)                                          ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolS_PV, tPBentPOMS*bot_pel_conv)                                          ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolS_PV, tDBentPOMS*bot_pel_conv)                                          ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolS_PV, tCBentPOMS*bot_pel_conv)                                          ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_SiPapoolS, tSiBentPaS)                                                               ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_DDOMpoolS, tDBentDOMS)                                                               ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_NDOMpoolS, tNBentDOMS)                                                               ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_PDOMpoolS, tPBentDOMS)                                                               ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_CDOMpoolS, tCBentDOMS)                                                               ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_NDOMpoolS_PV, tNBentDOMS*bot_pel_conv)                                          ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_PDOMpoolS_PV, tPBentDOMS*bot_pel_conv)                                          ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_DDOMpoolS_PV, tDBentDOMS*bot_pel_conv)                                          ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_CDOMpoolS_PV, tCBentDOMS*bot_pel_conv)                                          ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_SiO2poolS, tSiO2BentS)                                                               ! update the abiotic variables
      !=============================================================================================================!
      ! 7.4 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBentPOMS,tDBentPOMS)                                                    ! update the production of particulate organic matter (for calculating burial)
      !=============================================================================================================!
      ! 7.5 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_rPDBent,            rPDBent)                                              ! 
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_rNDBent,            rNDBent)                                              ! 
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_rCDBent,            rCDBent)                                              ! 
      if (self%diagnostics) then                                                                                    !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDMigrBent,     tDMigrBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNMigrBent,     tNMigrBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPMigrBent,     tPMigrBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCMigrBent,     tCMigrBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDConsBentTot,  tDConsBentTot)                                        !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNConsBentTot,  tNConsBentTot)                                        !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPConsBentTot,  tPConsBentTot)                                        !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCConsBentTot,  tCConsBentTot)                                        !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDEgesBent,     tDEgesBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNEgesBent,     tNEgesBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPEgesBent,     tPEgesBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCEgesBent,     tCEgesBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDRespBent,     tDRespBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCRespBent,     tCRespBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBentPO4S,     tPBentPO4S)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBentNH4S,     tNBentNH4S)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBentTPOMS,    tDBentTPOMS)                                          !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBentDOMS,     tDBentDOMS)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBentTPOMS,    tNBentTPOMS)                                          !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBentDOMS,     tNBentDOMS)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBentTPOMS,    tPBentTPOMS)                                          !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBentDOMS,     tPBentDOMS)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCBentDOMS,     tCBentDOMS)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCBentPOMS,     tCBentPOMS)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDMortBent,     tDMortBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNMortBent,     tNMortBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPMortBent,     tPMortBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCMortBent,     tCMortBent)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDMortO2,       tDMortO2)                                             !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_fO2,            fO2)                                                  !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiO2BentS,     tSiO2BentS)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiBentPaS,     tSiBentPaS)                                           !
          do i_prey = 1,self%nPrey                                                                                  !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDConsBent(i_prey), tDConsBent(i_prey))                            !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPConsBent(i_prey), tPConsBent(i_prey))                            !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNConsBent(i_prey), tNConsBent(i_prey))                            !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCConsBent(i_prey), tCConsBent(i_prey))                            !
		  end do                                                                                                    !
      endif                                                                                                         !
      !=============================================================================================================!
   _HORIZONTAL_LOOP_END_ !!! END OF MODEL CODE::
end subroutine do_bottom
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
end module wet_zoobenthos
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
