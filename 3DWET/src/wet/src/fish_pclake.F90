#include "fabm_driver.h"
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ MODULE: FISH - THE LEGACY PCLake FISH MODULE WHERE FISH ARE PELAGIC VARIABLES WITH VERTICAL MIGRATION                                                                                            §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
module wet_fish_pclake
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use wet_utility, ONLY:uFunTmGaus
   use fabm_particle
   use fabm_expressions
   use fabm_builtin_models
   implicit none
   private

   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public :: type_wet_fish_pclake
      ! local state variable identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                                   :: id_sDFi, id_sPFi, id_sNFi, id_sVFi
      ! diagnostic variables for modular fluxes--------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)                              :: id_BioTurb
      ! state dependencies identifiers-----------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_model_id)                                            :: id_FiJu_target, id_FiAd_target
      type (type_model_id),                 allocatable, dimension(:) :: id_BEN_prey, id_PISC_prey, id_ZOO_prey, id_PRED
      type (type_bottom_state_variable_id), allocatable, dimension(:) :: id_DFoodBen, id_NFoodBen, id_PFoodBen
      type (type_state_variable_id),        allocatable, dimension(:) :: id_DFoodBen_PV, id_NFoodBen_PV, id_PFoodBen_PV
      type (type_state_variable_id),        allocatable, dimension(:) :: id_DFoodZoo, id_NFoodZoo, id_PFoodZoo
      type (type_state_variable_id),        allocatable, dimension(:) :: id_DFoodPisc, id_NFoodPisc, id_PFoodPisc
      type (type_state_variable_id),        allocatable, dimension(:) :: id_PRED_D, id_FiSt_D
      type (type_state_variable_id)                                   :: id_FiJu_D, id_FiJu_P, id_FiJu_N, id_FiAd_D, id_FiAd_P, id_FiAd_N
      type (type_state_variable_id)                                   :: id_DPOMpoolW, id_PPOMpoolW, id_NPOMpoolW, id_NH4poolW, id_DDOMpoolW, id_PDOMpoolW, id_NDOMpoolW, id_PO4poolW
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)                              :: id_tDMigrFi, id_tNMigrFi, id_tPMigrFi, id_tDEgesFi, id_tNEgesFi, id_tPEgesFi, id_tDFiPOMW, id_tDFiDOMW, id_tDMortFiBot 
      type (type_diagnostic_variable_id)                              :: id_tNMortFiBot, id_tPMortFiBot, id_tDRespFi, id_tDConsFiZooSum, id_tNConsFiZooSum, id_tPConsFiZooSum, id_tDConsFiBenSum
      type (type_diagnostic_variable_id)                              :: id_tNConsFiBenSum, id_tPConsFiBenSum, id_tDConsFiPiscSum, id_tNConsFiPiscSum, id_tPConsFiPiscSum, id_tNExcrFi, id_tNFiNH4W
      type (type_diagnostic_variable_id)                              :: id_tNFiPOMW, id_tNFiDOMW, id_tPExcrFi, id_tPFiPO4W, id_tPFiPOMW, id_tPFiDOMW, id_tDMortFi, id_tNMortFi, id_tPMortFi
      type (type_diagnostic_variable_id)                              :: id_tDAgeFish, id_tNAgeFish, id_tPAgeFish, id_tDReprFish, id_tNReprFish, id_tPReprFish
      ! environmental dependencies---------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_dependency_id)                            :: id_bot_pel_conv
      type (type_dependency_id)                                       :: id_uTm, id_oxygen, id_par
      type (type_diagnostic_variable_id),   allocatable, dimension(:) :: id_tDConsFiBen_out, id_tNConsFiBen_out, id_tPConsFiBen_out, id_tDConsFiZoo, id_tNConsFiZoo, id_tPConsFiZoo, id_tDConsFiPisc
      type (type_diagnostic_variable_id),   allocatable, dimension(:) :: id_tNConsFiPisc, id_tPConsFiPisc
      type (type_dependency_id),            allocatable, dimension(:) :: id_tDConsFiBen, id_tNConsFiBen, id_tPConsFiBen
      type (type_global_dependency_id)                                :: id_Day
      ! diagnostic dependencies------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_dependency_id)                                       :: id_aDSubVeg, id_aCovVeg
      ! parameters-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      integer                                                         :: nBENprey=0, nZOOprey=0, nPISCprey=0, qStageOpt, nMACS, nKShares, qTrans
      logical                                                         :: lVegOpt, lNutMeth, diagnostics
      real(rk)                                                        :: kMigrFish, cDFiIn, fDBone, fPBone, cDCarrFish, fDissEgesFish, kTurbFish, fDissMortFish, cTmOptFish, cSigTmFish, cDayReprFish
      real(rk)                                                        :: cDayAgeFish, fReprFish, fAgeFish, kDAssFi, hDZooFi, fDAssFi, kDRespFi, kMortFi, hDVegGrowth, hDPiscFi, cPDFishRef, cNDFishRef
      real(rk)                                                        :: cDFiMin, fFiDOMW, cRelVegBent, cRelVegZoo, hDBentFi, Vswim, fFishZoo, fFishBen, fFishPisc, cMinO2
      real(rk)                                                        :: cMinLight
      real(rk),                             allocatable, dimension(:) :: PISCpref, ZOOpref, BENpref
      
   contains

   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure :: initialize
   procedure :: do
   procedure :: do_bottom
   procedure :: get_vertical_movement

   end type type_wet_fish_pclake

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk)           :: Pi=3.14159265358979_rk
   real(rk),parameter :: FishZero=0.00001_rk

contains

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                       §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_fish_pclake), intent(inout), target :: self
   integer,                      intent(in)            :: configunit
   
   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer  :: i_prey, i_pred, i_mac, i_stage
   character(len=64)   :: index

   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! boundary condition and variable constrain parameters----------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%kMigrFish,        'kMigrFish',     '1/d',      'fish migration rate',                                              default=0.001_rk,   scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%cDFiIn,           'cDFiIn',        'gDW/m3',   'external density',                                                 default=0.005_rk                                   )
   ! vertical movement parameters----------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%qTrans,           'qTrans',        '-',        'vert. trans. method: 0=no trans.; 1=passive; 2=O2; 3=O2 & Light',  default=2                                          )
   call self%get_parameter(self%cMinO2,           'cMinO2',        'gO2/m3',   'qtrans > 1; oxygen conc. limit',                                   default=2.0_rk                                     )
   call self%get_parameter(self%cMinLight,        'cMinLight',     'W/m2',     'qTrans = 3; light level triggering downwards swimming',            default=1.0_rk                                     )
   call self%get_parameter(self%Vswim,            'Vswim',         'm/d',      'qTrans > 1; vertical migration speed',                             default=10.0_rk,    scale_factor=1.0_rk/secs_pr_day)
   ! fish population-level parameters------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cDCarrFish,       'cDCarrFish',    'gDW/m3',   'carrying capacity',                                                default=15.0_rk                                    )
   call self%get_parameter(self%cDFiMin,          'cDFiMin',       'gDW/m3',   'minimum DW density',                                               default=0.0001_rk                                  )
   call self%get_parameter(self%qStageOpt,        'qStageOpt',     '-',        'stage coupling method: 0=nothing; 1=repro.; 2=maturation; 3=both', default=0                                          )
   call self%get_parameter(self%cDayReprFish,     'cDayReprFish',  'day of the year', 'qStageOpt = 1 or 3; reproduction date',                     default=120.0_rk                                   )
   call self%get_parameter(self%fReprFish,        'fReprFish',     '1/d',      'qStageOpt = 1 or 3; yearly reproduction fraction',                 default=0.02_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%cDayAgeFish,      'cDayAgeFish',   'day of the year', 'qStageOpt = 2 or 3; aging day of year for fish ',           default=360.0_rk,   maximum=364.0_rk               )
   call self%get_parameter(self%fAgeFish,         'fAgeFish',      '1/d',      'qStageOpt = 2 or 3; yearly maturation fraction',                   default=0.5_rk,     scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%nKShares,         'nKShares',      '-',        'qStageOpt > 0; # of not-coupled other stages sharing carr. cap.',  default=0                                          )
   ! prey parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%fFishZoo,         'fFishZoo',      '-',        'zooplanktivory time fraction',                                     default=1.0_rk                                     )
   call self%get_parameter(self%fFishBen,         'fFishBen',      '-',        'zoobentivory time fraction',                                       default=0.0_rk                                     )
   call self%get_parameter(self%fFishPisc,        'fFishPisc',     '-',        'piscivory time fraction',                                          default=0.0_rk                                     )
   if (self%fFishZoo > 0.0_rk) then                                                                                                               
      call self%get_parameter(self%nZOOprey,      'nZOO',          '-',        'number of zooplankton prey',                                       default=0                                          )
      allocate (self%ZOOpref(self%nZOOprey))                                                                                                
      do i_prey = 1,self%nZOOprey                                                                                                         
         write(index,'(i0)') i_prey
         call self%get_parameter(self%ZOOpref(i_prey),  'ZOOpref'//trim(index), '-', 'preference factor for zooplankton prey '//trim(index),       default=1.0_rk                                     )
      end do
   endif
   if (self%fFishBen > 0.0_rk) then                                                                                                             
      call self%get_parameter(self%nBENprey,      'nBEN',          '-',        'number of zoobenthos prey',                                        default=0                                          )
      call self%get_parameter(self%kTurbFish,     'kTurbFish',     'g/gDW/d',  'relative resuspension by adult fish browsing',                     default=1.0_rk                                     )
      allocate (self%BENpref(self%nBENprey))                                                                                                      
      do i_prey = 1,self%nBENprey
         write(index,'(i0)') i_prey
         call self%get_parameter(self%BENpref(i_prey),  'BENpref'//trim(index), '-',  'preference factor for zoobenthos prey '//trim(index),       default=1.0_rk                                     )
      end do
   endif
   if (self%fFishPisc > 0.0_rk) then                                                                                                             
      call self%get_parameter(self%nPISCprey,     'nPISC',         '-',         'number of fish prey',                                             default=0                                          )
      allocate (self%PISCpref(self%nPISCprey))                                                                                                      
      do i_prey = 1,self%nPISCprey                                                                                                               
         write(index,'(i0)') i_prey
         call self%get_parameter(self%PISCpref(i_prey), 'PISCpref'//trim(index), '-', 'preference factor for fish prey '//trim(index),             default=1.0_rk                                     )
      end do
   endif                                                                                                                                             
   ! fish vital parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%kDAssFi,          'kDAssFi',       '1/d',       'maximum assimilation rate of fish at 20*C',                       default=0.12_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%hDZooFi,          'hDZooFi',       'g/m3',      'half-saturation zooplankton for zooplanktivory',                  default=1.1_rk                                     )
   call self%get_parameter(self%hDBentFi,         'hDBentFi',      'g/m2',      'half-saturation constant for zoobentivory',                       default=2.5_rk                                     )
   call self%get_parameter(self%fDAssFi,          'fDAssFi',       '-',         'C assimilation efficiency of fish',                               default=0.4_rk                                     )
   call self%get_parameter(self%kDRespFi,         'kDRespFi',      '1/d',       'maintenance respiration constant of fish at 20*C',                default=0.01_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%kMortFi,          'kMortFi',       '1/d',       'specific mortality of fish',                                      default=0.001_rk,   scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%hDPiscFi,         'hDPiscFi',      'g/m3',      'half-saturating DFish for fish predation',                        default=1.0_rk                                     )
   call self%get_parameter(self%cRelVegBent,      'cRelVegBent',   '-',         'decrease of fish feeding per macrophytes cover, max. 0.01',       default=0.009_rk                                   )
   call self%get_parameter(self%cRelVegZoo,       'cRelVegZoo',    '-',         'decrease of fish feeding per macrophytes cover, max. 0.01',       default=0.0_rk                                     )
   call self%get_parameter(self%lVegOpt,          'lVegOpt',        '-',        'switch for macrophyte dependence on fish max assimilation',       default=.false.                                    )
   call self%get_parameter(self%hDVegGrowth,      'hDVegGrowth',   'g/m2',      'lVegOpt = .true.; half-saturation macrophyte density for growth', default=0.015_rk                                   )
   ! stochiometric parameters--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%lNutMeth,         'lNutMeth',      '-',         'toggle fixed stochiometry',                                       default=.false.                                    )
   call self%get_parameter(self%fDBone,           'fDBone',        '-',         'fraction of fish C fixed in bones and scales',                    default=0.35_rk                                    )
   call self%get_parameter(self%fPBone,           'fPBone',        '-',         'fraction of fish P fixed in bones and scales',                    default=0.5_rk                                     )
   call self%get_parameter(self%fDissEgesFish,    'fDissEgesFish', '-',         'soluble nutrient frac. of fish egested food',                     default=0.25_rk                                    )
   call self%get_parameter(self%fDissMortFish,    'fDissMortFish', '-',         'soluble nutrient frac. of dead fish, excl. bones & scales',       default=0.1_rk                                     )
   call self%get_parameter(self%cPDFishRef,       'cPDFishRef',    'mgP/mgDW',  'reference P/C ratio of fish',                                     default=0.022_rk                                   )
   call self%get_parameter(self%cNDFishRef,       'cNDFishRef',    'mgN/mgDW',  'reference N/C ratio of fish',                                     default=0.1_rk                                     )
   call self%get_parameter(self%fFiDOMW,          'fFiDOMW',       '-',         'dissolved organic matter fraction from fish',                     default=0.5_rk                                     )
   ! fish temperature parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cTmOptFish,       'cTmOptFish',    '*C',        'optimal temperature of zoo- and benthivorous fish',               default=25.0_rk                                    )
   call self%get_parameter(self%cSigTmFish,       'cSigTmFish',    '*C',        'temperature constant of fish, sigma in Gaussian curve',           default=10.0_rk                                    )
   ! diagnostic  parameter-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,      'diagnostics',   '-',         'toggle diagnostic output',                                        default=.false.                                    )
   
   !REGISTER MODEL VARIABLES, DEPENDENCIES & COUPLINGS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! fish state variables, transportation is turned off------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sDFi,          'sD',      'gDW/m3',   'DW',       initial_value= 0.5_rk,    minimum=self%cDFiMin                  )
   call self%register_state_variable(self%id_sPFi,          'sP',      'gP/m3',    'P',        initial_value=0.011_rk,   minimum=self%cDFiMin * self%cPDFishRef)
   call self%register_state_variable(self%id_sNFi,          'sN',      'gN/m3',    'N',        initial_value=0.05_rk,    minimum=self%cDFiMin * self%cNDFishRef)
   if (self%qTrans == 0) then
       call self%set_variable_property(self%id_sDFi,   'disable_transport',   .true.)   
       call self%set_variable_property(self%id_sNFi,   'disable_transport',   .true.)
       call self%set_variable_property(self%id_sPFi,   'disable_transport',   .true.)
   endif
   ! register state variables dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_dependency(self%id_DPOMpoolW,    'POM_DW_pool_water',     'g/m3',     'POM DW pool in water'                                                                              )
   call self%register_state_dependency(self%id_NPOMpoolW,    'POM_N_pool_water',      'g/m3',     'POM N pool in water'                                                                               )
   call self%register_state_dependency(self%id_PPOMpoolW,    'POM_P_pool_water',      'g/m3',     'POM P pool in water'                                                                               )
   call self%register_state_dependency(self%id_NH4poolW,     'NH4_pool_water',        'g/m3',     'NH4 pool in water'                                                                                 )
   call self%register_state_dependency(self%id_PO4poolW,     'PO4_pool_water',        'g/m3',     'PO4 pool in water'                                                                                 )
   call self%register_state_dependency(self%id_DDOMpoolW,    'DOM_DW_pool_water',     'g/m3',     'DOM DW in water'                                                                                   )
   call self%register_state_dependency(self%id_NDOMpoolW,    'DOM_N_pool_water',      'g/m3',     'DOM N in water'                                                                                    )
   call self%register_state_dependency(self%id_PDOMpoolW,    'DOM_P_pool_water',      'g/m3',     'DOM P in water'                                                                                    )
   ! setup couplings to zooplankton prey variables-----------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%nZOOprey /= 0) then
      allocate(self%id_ZOO_prey(self%nZOOprey))
      allocate(self%id_DFoodZoo(self%nZOOprey))
      allocate(self%id_NFoodZoo(self%nZOOprey))
      allocate(self%id_PFoodZoo(self%nZOOprey))
      allocate(self%id_tDConsFiZoo(self%nZOOprey))
      allocate(self%id_tPConsFiZoo(self%nZOOprey))
      allocate(self%id_tNConsFiZoo(self%nZOOprey))
      do i_prey=1,self%nZOOprey
          write(index,'(i0)') i_prey
          call self%register_model_dependency(self%id_ZOO_prey(i_prey), 'ZOOprey'//trim(index))
          call self%register_state_dependency(self%id_DFoodZoo(i_prey), 'zooplankton_D_Food'//trim(index), 'g/m3', 'zooplankton D Food'//trim(index))
          call self%register_state_dependency(self%id_NFoodZoo(i_prey), 'zooplankton_N_Food'//trim(index), 'g/m3', 'zooplankton N Food'//trim(index))
          call self%register_state_dependency(self%id_PFoodZoo(i_prey), 'zooplankton_P_Food'//trim(index), 'g/m3', 'zooplankton P Food'//trim(index))
          call self%request_coupling_to_model(self%id_DFoodZoo(i_prey),self%id_ZOO_prey(i_prey), 'sD')
          call self%request_coupling_to_model(self%id_PFoodZoo(i_prey),self%id_ZOO_prey(i_prey), 'sP')
          call self%request_coupling_to_model(self%id_NFoodZoo(i_prey),self%id_ZOO_prey(i_prey), 'sN')
          if (self%diagnostics) then
              call self%register_diagnostic_variable(self%id_tDConsFiZoo(i_prey), 'tDConsFiZoo_'//trim(index),	'g/m3/s','rate Zoo D consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tPConsFiZoo(i_prey), 'tPConsFiZoo_'//trim(index),	'g/m3/s','rate Zoo P consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tNConsFiZoo(i_prey), 'tNConsFiZoo_'//trim(index),	'g/m3/s','rate Zoo N consumed '//trim(index),  output=output_instantaneous)
          endif 
      end do
   endif
   ! setup couplings to zoobenthos prey variables------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_BioTurb,       'Bioturbation',   'gDW/m3/d',   'Bioturbation')
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_bioturbation',units='gDW/m3/d',aggregate_variable=.true.),self%id_BioTurb,scale_factor=1._rk)
   if (self%nBENprey /= 0) then      
      allocate(self%id_BEN_prey(self%nBENprey))
      allocate(self%id_DFoodBen(self%nBENprey))
      allocate(self%id_NFoodBen(self%nBENprey))
      allocate(self%id_PFoodBen(self%nBENprey))
      allocate(self%id_DFoodBen_PV(self%nBENprey))
      allocate(self%id_NFoodBen_PV(self%nBENprey))
      allocate(self%id_PFoodBen_PV(self%nBENprey))
      
      allocate(self%id_tDConsFiBen(self%nBENprey))
      allocate(self%id_tDConsFiBen_out(self%nBENprey))
      allocate(self%id_tPConsFiBen(self%nBENprey))
      allocate(self%id_tPConsFiBen_out(self%nBENprey))
      allocate(self%id_tNConsFiBen(self%nBENprey))
      allocate(self%id_tNConsFiBen_out(self%nBENprey))
      do i_prey=1,self%nBENprey
          write(index,'(i0)') i_prey
          call self%register_model_dependency(self%id_BEN_prey(i_prey),'BENprey'//trim(index))
          call self%register_state_dependency(self%id_DFoodBen(i_prey), 'zoobenthos_D_Food'//trim(index), 'g/m3', 'zoobenthos D Food'//trim(index))
          call self%register_state_dependency(self%id_NFoodBen(i_prey), 'zoobenthos_N_Food'//trim(index), 'g/m3', 'zoobenthos N Food'//trim(index))
          call self%register_state_dependency(self%id_PFoodBen(i_prey), 'zoobenthos_P_Food'//trim(index), 'g/m3', 'zoobenthos P Food'//trim(index))
          call self%request_coupling_to_model(self%id_DFoodBen(i_prey),self%id_BEN_prey(i_prey),'sD')
          call self%request_coupling_to_model(self%id_PFoodBen(i_prey),self%id_BEN_prey(i_prey),'sP')
          call self%request_coupling_to_model(self%id_NFoodBen(i_prey),self%id_BEN_prey(i_prey),'sN')
          call self%register_state_dependency(self%id_DFoodBen_PV(i_prey), 'zoobenthos_D_Food'//trim(index)//'_PV', '-', 'zoobenthos D Food PV target number '//trim(index))
          call self%register_state_dependency(self%id_NFoodBen_PV(i_prey), 'zoobenthos_N_Food'//trim(index)//'_PV', '-', 'zoobenthos N Food PV target number '//trim(index))
          call self%register_state_dependency(self%id_PFoodBen_PV(i_prey), 'zoobenthos_P_Food'//trim(index)//'_PV', '-', 'zoobenthos P Food PV target number '//trim(index))
          call self%request_coupling_to_model(self%id_DFoodBen_PV(i_prey),self%id_BEN_prey(i_prey), 'sD_PV')
          call self%request_coupling_to_model(self%id_PFoodBen_PV(i_prey),self%id_BEN_prey(i_prey), 'sP_PV')
          call self%request_coupling_to_model(self%id_NFoodBen_PV(i_prey),self%id_BEN_prey(i_prey), 'sN_PV')
          
          call self%register_diagnostic_variable(self%id_tDConsFiBen_out(i_prey),  'tDConsFiBen_'//trim(index),         'gDW/m2', 'rate tDConsFiBen'//trim(index),     output=output_instantaneous, act_as_state_variable=.true.                   ) ! check with Nicolas
          call self%register_dependency(self%id_tDConsFiBen(i_prey),  'tDConsFiBen_'//trim(index),         'gDW m-2', 'tDConsFiBen'//trim(index))
          call self%register_diagnostic_variable(self%id_tNConsFiBen_out(i_prey),  'tNConsFiBen_'//trim(index),         'gDW/m2', 'rate sNConsFiBen'//trim(index),     output=output_instantaneous, act_as_state_variable=.true.                   )
          call self%register_dependency(self%id_tNConsFiBen(i_prey),  'tNConsFiBen_'//trim(index),         'gDW m-2', 'tNConsFiBen'//trim(index))
          call self%register_diagnostic_variable(self%id_tPConsFiBen_out(i_prey),  'tPConsFiBen_'//trim(index),         'gDW/m2', 'rate sPConsFiBen'//trim(index),     output=output_instantaneous, act_as_state_variable=.true.                   )
          call self%register_dependency(self%id_tPConsFiBen(i_prey),  'tPConsFiBen_'//trim(index),         'gDW m-2', 'tPConsFiBen'//trim(index))
      end do
    endif
   ! setup couplings to fish prey variables------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%nPISCprey /= 0) then
      allocate(self%id_PISC_prey(self%nPISCprey))
      allocate(self%id_DFoodPisc(self%nPISCprey))
      allocate(self%id_NFoodPisc(self%nPISCprey))
      allocate(self%id_PFoodPisc(self%nPISCprey))
      allocate(self%id_tDConsFiPisc(self%nPISCprey))
      allocate(self%id_tPConsFiPisc(self%nPISCprey))
      allocate(self%id_tNConsFiPisc(self%nPISCprey))
      do i_prey=1,self%nPISCprey
          write(index,'(i0)') i_prey
          call self%register_model_dependency(self%id_PISC_prey(i_prey),'PISCprey'//trim(index))
          call self%register_state_dependency(self%id_DFoodPisc(i_prey), 'fish_D_Food'//trim(index), 'g/m3', 'fish D Food'//trim(index))
          call self%register_state_dependency(self%id_NFoodPisc(i_prey), 'fish_N_Food'//trim(index), 'g/m3', 'fish N Food'//trim(index))
          call self%register_state_dependency(self%id_PFoodPisc(i_prey), 'fish_P_Food'//trim(index), 'g/m3', 'fish P Food'//trim(index))
          call self%request_coupling_to_model(self%id_DFoodPisc(i_prey),self%id_PISC_prey(i_prey),'sD')
          call self%request_coupling_to_model(self%id_PFoodPisc(i_prey),self%id_PISC_prey(i_prey),'sP')
          call self%request_coupling_to_model(self%id_NFoodPisc(i_prey),self%id_PISC_prey(i_prey),'sN')
          if (self%diagnostics) then
              call self%register_diagnostic_variable(self%id_tDConsFiPisc(i_prey), 'tDConsFiPisc_'//trim(index),	'g/m3/s','rate Pisc D consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tPConsFiPisc(i_prey), 'tPConsFiPisc_'//trim(index),	'g/m3/s','rate Pisc P consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tNConsFiPisc(i_prey), 'tNConsFiPisc_'//trim(index),	'g/m3/s','rate Pisc N consumed '//trim(index),  output=output_instantaneous)
          endif 
       end do
    endif
   ! setup couplings to other stages-------------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%qStageOpt == 1 .OR. self%qStageOpt == 3) then
      call self%register_state_dependency(self%id_FiJu_D,'juvenile_D','g/m3', 'juvenile D state')
      call self%register_state_dependency(self%id_FiJu_P,'juvenile_P','g/m3', 'juvenile P state')
      call self%register_state_dependency(self%id_FiJu_N,'juvenile_N','g/m3', 'juvenile N state')
      !call self%register_model_dependency(self%id_FiJu_target,'juvenile_target')                             !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiJu_D,self%id_FiJu_target,'sDFi')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiJu_P,self%id_FiJu_target,'sPFi')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiJu_N,self%id_FiJu_target,'sNFi')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
   endif
   if (self%qStageOpt == 2 .OR. self%qStageOpt == 3) then
      call self%register_state_dependency(self%id_FiAd_D,'adult_D','g/m3', 'adult D state')
      call self%register_state_dependency(self%id_FiAd_P,'adult_P','g/m3', 'adult P state')
      call self%register_state_dependency(self%id_FiAd_N,'adult_N','g/m3', 'adult N state')
      !call self%register_model_dependency(self%id_FiAd_target,'adult_target')                                !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiAd_D,self%id_FiAd_target,'sDFi')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiAd_P,self%id_FiAd_target,'sPFi')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiAd_N,self%id_FiAd_target,'sNFi')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
   endif
   if (self%nKShares > 0) then
      allocate(self%id_FiSt_D(self%nKShares))
      do i_stage = 1,self%nKShares
         write(index,'(i0)') i_stage
         call self%register_state_dependency(self%id_FiSt_D(i_stage),'otherStage'//trim(index),'g/m3', 'otherStage'//trim(index))
      end do
   endif
   ! Register diagnostic process output----------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%diagnostics) then   
       call self%register_diagnostic_variable(self%id_tDMigrFi,           'tDMigrFi',             'g/m3/s',         'rate DW migration',                      output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNMigrFi,           'tNMigrFi',             'g/m3/s',         'rate N migration',                       output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPMigrFi,           'tPMigrFi',             'g/m3/s',         'rate P migration',                       output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDConsFiZooSum,     'tDConsFiZooSum',       'g/m3/s',         'rate DW zooplankton consumed',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNConsFiZooSum,     'tNConsFiZooSum',       'g/m3/s',         'rate N zooplankton consumed',            output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPConsFiZooSum,     'tPConsFiZooSum',       'g/m3/s',         'rate P zooplankton consumed',            output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDConsFiBenSum,     'tDConsFiBenSum',       'g/m3/s',         'rate DW zoobenthos consumed',            output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNConsFiBenSum,     'tNConsFiBenSum',       'g/m3/s',         'rate N zoobenthos consumed',             output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPConsFiBenSum,     'tPConsFiBenSum',       'g/m3/s',         'rate P zoobenthos consumed',             output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDConsFiPiscSum,    'tDConsFiPiscSum',      'g/m3/s',         'rate DW fish consumed',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNConsFiPiscSum,    'tNConsFiPiscSum',      'g/m3/s',         'rate N fish consumed',                   output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPConsFiPiscSum,    'tPConsFiPiscSum',      'g/m3/s',         'rate P fish consumed',                   output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDEgesFi,           'tDEgesFi',             'g/m3/s',         'rate DW egested',                        output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNEgesFi,           'tNEgesFi',             'g/m3/s',         'rate N egested',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPEgesFi,           'tPEgesFi',             'g/m3/s',         'rate P egested',                         output=output_instantaneous)      
       call self%register_diagnostic_variable(self%id_tDMortFi,           'tDMortFi',             'g/m3/s',         'rate DW from mortality',                 output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNMortFi,           'tNMortFi',             'g/m3/s',         'rate N from mortality',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPMortFi,           'tPMortFi',             'g/m3/s',         'rate P from mortality',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDRespFi,           'tDRespFi',             'g/m3/s',         'rate DW respired',                       output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDFiPOMW,           'tDFiPOMW',             'g/m3/s',         'rate DPOMW egested',                     output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDFiDOMW,           'tDFiDOMW',             'g/m3/s',         'rate DDOMW egested',                     output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDMortFiBot,        'tDMortFiBot',          'g/m3/s',         'rate DW bone lost from system',          output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNMortFiBot,        'tNMortFiBot',          'g/m3/s',         'rate N bone lost from system',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPMortFiBot,        'tPMortFiBot',          'g/m3/s',         'rate P bone lost from system',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNExcrFi,           'tNExcrFi',             'g/m3/s',         'rate NH4 excreted',                      output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNFiNH4W,           'tNFiNH4W',             'g/m3/s',         'rate NH4 out',                           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNFiPOMW,           'tNFiPOMW',             'g/m3/s',         'rate NPOMW out',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNFiDOMW,           'tNFiDOMW',             'g/m3/s',         'rate NDOMW out',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPExcrFi,           'tPExcrFi',             'g/m3/s',         'rate PO4 excreted',                      output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPFiPO4W,           'tPFiPO4W',             'g/m3/s',         'rate PO4 out',                           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPFiPOMW,           'tPFiPOMW',             'g/m3/s',         'rate PPOMW out',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPFiDOMW,           'tPFiDOMW',             'g/m3/s',         'rate PDOMW out',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDAgeFish,          'tDAgeFish',            'g/m3/s',         'rate DW ageing',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNAgeFish,          'tNAgeFish',            'g/m3/s',         'rate N ageing',                          output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPAgeFish,          'tPAgeFish',            'g/m3/s',         'rate P ageing',                          output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDReprFish,         'tDReprFish',           'g/m3/s',         'rate DW reproduced',                     output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNReprFish,         'tNReprFish',           'g/m3/s',         'rate N reproduced',                      output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPReprFish,         'tPReprFish',           'g/m3/s',         'rate P reproduced',                      output=output_instantaneous)
   endif
   !  register environmental dependencies--------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_uTm,    standard_variables%temperature)
   call self%register_dependency(self%id_Day,    standard_variables%number_of_days_since_start_of_the_year)
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')  
   call self%register_dependency(self%id_oxygen, 'oxygen_pool_water', 'g/m3', 'Oxygen pool water')
   call self%register_dependency(self%id_par, standard_variables%downwelling_photosynthetic_radiative_flux)
   call self%register_dependency(self%id_aCovVeg,type_bulk_standard_variable(name='total_aCovVeg',units='%'))
   call self%register_dependency(self%id_aDSubVeg,type_bulk_standard_variable(name='total_aDSubVeg',units='gDW/m2'))
   
   return

end subroutine initialize

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO (PELAGIC)                                                                                                                                                                       §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do(self,_ARGUMENTS_DO_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_fish_pclake), intent(in)    :: self   
   _DECLARE_ARGUMENTS_DO_

   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk), dimension(self%nZOOprey)     :: sDZoo, sNZoo, sPZoo, rPDZoo, rNDZoo, relabZOO, tDConsFiZoo, tPConsFiZoo, tNConsFiZoo, afNAssFiZoo, tNAssFiZoo, afPAssFiZoo, tPAssFiZoo
   real(rk), dimension(self%nBENprey)     :: sDBent, sNBent, sPBent, rPDBent, rNDBent, relabBEN, tDConsFiBen, tPConsFiBen, tNConsFiBen, afNAssFiBen, tNAssFiBen, afPAssFiBen, tPAssFiBen
   real(rk), dimension(self%nPISCprey)    :: sDPisc, sNPisc, sPPisc, rPDPisc, rNDPisc, relabPISC, tDConsFiPisc, tPConsFiPisc, tNConsFiPisc, afNAssFiPisc, tNAssFiPisc, afPAssFiPisc, tPAssFiPisc
   real(rk), dimension(self%nKShares) :: sDFiSt_all
   real(rk)                               :: uTm, Day, sDFi, sPFi, sNFi, aDSubVeg, rPDFi, rNDFi, uFunTmFish, tDReprFish, tDAgeFish, tPReprFish, tPAgeFish, tNReprFish, tNAgeFish
   real(rk)                               :: tDFi, tDMigrFi, tDRespFi, tDMortFi, aDSatFiTot, tDEnvFi, ukDIncrFi, tPFi, tPMigrFi, tPExcrFi, tNFi, tNMigrFi, tNExcrFi, tNMortFi, sDFiSt
   real(rk)                               :: tNEgesFi, tNMortFiNH4, tNMortFiBot, tNEgesFiNH4, tNFiNH4W, tNEgesFiTOM, tNMortFiTOM, tVFi, sDFiJu, sDFiAd, tPEgesFiPO4, tPFiPO4W
   real(rk)                               :: tDEgesFi, tDMortFiTOM, tDMortFiBot, tDFiTOMW, tNFiTOMW, tPFiTOMW, tDAssFiTot, tDFiPOMW, tNFiPOMW, tPFiPOMW, tPAssFiTot, tPEgesFi, tPMortFi, tPMortFiBot
   real(rk)                               :: tDFiDOMW, tNFiDOMW, tPFiDOMW, tNAssFiTot, aCovVeg, aFunVegBent, aFunVegZoo, aFunVegAss, aDSatFiZoo, aDSatFiBen, aDSatFiPisc, tPMortFiPO4, tPEgesFiTOM
   real(rk)                               :: tDConsFiZooSum, tNConsFiZooSum, tPConsFiZooSum, tDConsFiBenSum, tNConsFiBenSum, tPConsFiBenSum, tDConsFiPiscSum, tNConsFiPiscSum, tPConsFiPiscSum
   real(rk)                               :: fFishZoo, fFishBen, fFishPisc, tDAssFiZoo, tDAssFiBen, tDAssFiPisc, tDConsFiTot, tPConsFiTot, tNConsFiTot, sDFiOS, sDAd, sDJu, BioTurb, tPMortFiTOM
   integer                                :: i_prey, i_pred, i

   _LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
        ! 1.1 retrieve environmental dependencies                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        _GET_(self%id_uTm,uTm)                                                                                      ! get local temperature
        _GET_GLOBAL_(self%id_Day,Day)                                                                               ! get the simulation day
        _GET_(self%id_aDSubVeg,aDSubVeg)                                                                            ! get macrophyte biomass
        _GET_(self%id_aCovVeg,aCovVeg)                                                                              ! get macrophyte cover percentage
        aCovVeg = min(1.0_rk,aCovVeg)                                                                               !
        !===========================================================================================================!
        ! 1.2 retrieve state variables, & calc. current local nutrient ratios and relative abundances               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.1 fish state variables                                                                             !
           !--------------------------------------------------------------------------------------------------------!
           _GET_(self%id_sDFi,sDFi)                                                                                 ! get fish dry weight
           _GET_(self%id_sPFi,sPFi)                                                                                 ! get fish P mass
           _GET_(self%id_sNFi,sNFi)                                                                                 ! get fish N mass
           if (.NOT. self%lNutMeth) then                                                                            ! case dynamic stochiometry
           rPDFi = sPFi /(sDFi+NearZero)                                                                            !   calculate P:DW ratio
           rNDFi = sNFi /(sDFi+NearZero)                                                                            !   calculate N:DW ratio
           else                                                                                                     ! case fixed stochiometry
               rPDFi = self%cPDFishRef                                                                              !   P ratio parameter
               rNDFi = self%cNDFishRef                                                                              !   N ratio parameter
           endif                                                                                                    !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.2 zooplankton prey                                                                                 !
           !--------------------------------------------------------------------------------------------------------!
           if (self%nZOOprey /= 0) then                                                                             ! case zooplanktivory 
              do i_prey=1,self%nZOOprey                                                                             !   for each prey
                 _GET_(self%id_DFoodZoo(i_prey),sDZoo(i_prey))                                                      !     get zoopl. dry weight (dimensions: nZOOprey)
                 _GET_(self%id_NFoodZoo(i_prey),sNZoo(i_prey))                                                      !     get zoopl. P weight (dimensions: nZOOprey)
                 _GET_(self%id_PFoodZoo(i_prey),sPZoo(i_prey))                                                      !     get zoopl. N weight (dimensions: nZOOprey)
              end do                                                                                                !
              rPDZoo = sPZoo / (sDZoo + NearZero)                                                                   !   calculate P:DW ratio
              rNDZoo = sNZoo / (sDZoo + NearZero)                                                                   !   calculate N:DW ratio
              relabZOO = (sDZoo*self%ZOOpref)/sum(sDZoo*self%ZOOpref)                                               !   calculate relative abundances of indiv. zoopl. prey
           else                                                                                                     ! case no zooplanktivory: values set to zero
               sDZoo = 0.0_rk                                                                                       !
               sNZoo = 0.0_rk                                                                                       !
               sPZoo = 0.0_rk                                                                                       !
               rPDZoo = 1.0_rk                                                                                      !
               rNDZoo = 1.0_rk                                                                                      !
               relabZOO = 0.0_rk                                                                                    !
           endif                                                                                                    !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.3 zoobenthos prey                                                                                  !
           !--------------------------------------------------------------------------------------------------------!
           if (self%nBENprey /= 0) then                                                                             ! case bentivory
              do i_prey=1,self%nBENprey                                                                             !   for each prey
                 _GET_(self%id_DFoodBen_PV(i_prey),sDBent(i_prey))                                                  !     get bent. dry weight (dimensions: nBENprey)
                 _GET_(self%id_NFoodBen_PV(i_prey),sNBent(i_prey))                                                  !     get bent. N weight (dimensions: nBENprey)
                 _GET_(self%id_PFoodBen_PV(i_prey),sPBent(i_prey))                                                  !     get bent. P weight (dimensions: nBENprey)
              end do                                                                                                !
              rPDBent = sPBent /(sDBent+NearZero)                                                                   !   calculate P:DW ratio
              rNDBent = sNBent/(sDBent+NearZero)                                                                    !   calculate N:DW ratio
              relabBEN = (sDBent*self%BENpref)/sum(sDBent*self%BENpref)                                             !   calculate relative abundances of indiv. bent. prey
           else                                                                                                     ! case no bentivory: values set to zero
              sDBent = 0.0_rk                                                                                       !
              sNBent = 0.0_rk                                                                                       !
              sPBent = 0.0_rk                                                                                       !
              rPDBent = 1.0_rk                                                                                      !
              rNDBent = 1.0_rk                                                                                      !
              relabBEN = 0.0_rk                                                                                     !
           endif                                                                                                    !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.4 fish prey                                                                                        !
           !--------------------------------------------------------------------------------------------------------!
           if (self%nPISCprey /= 0) then                                                                            ! case piscivory
               do i_prey=1,self%nPISCprey                                                                           !   for each prey
                  _GET_(self%id_DFoodPisc(i_prey),sDPisc(i_prey))                                                   !     get pisc. dry weight (dimensions: nPISCprey)
                  _GET_(self%id_NFoodPisc(i_prey),sNPisc(i_prey))                                                   !     get pisc. P weight (dimensions: nPISCprey)
                  _GET_(self%id_PFoodPisc(i_prey),sPPisc(i_prey))                                                   !     get pisc. N weight (dimensions: nPISCprey)
               end do                                                                                               !
               rPDPisc = sPPisc /(sDPisc+NearZero)                                                                  !   calculate P:DW ratio
               rNDPisc = sNPisc/(sDPisc+NearZero)                                                                   !   calculate N:DW ratio
               relabPISC = (sDPisc*self%PISCpref)/sum(sDPisc*self%PISCpref)                                         !   calculate relative abundances of indiv. fish prey
           else                                                                                                     ! case no piscivory: values set to zero
               sDPisc = 0.0_rk                                                                                      !
               sNPisc = 0.0_rk                                                                                      !
               sPPisc = 0.0_rk                                                                                      !
               rPDPisc = 1.0_rk                                                                                     !
               rNDPisc = 1.0_rk                                                                                     !
               relabPISC = 0.0_rk                                                                                   !
           endif                                                                                                    !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.5 other stages                                                                                     ! FIX: sDFiOS MUST HOLD ALL STAGES
           !--------------------------------------------------------------------------------------------------------!
           sDFiOS = 0.0_rk                                                                                          ! initialize total biomass of other stages (juv. + adults + other stages in stage structure)
           if (self%qStageOpt == 1 .OR. self%qStageOpt == 3) then                                                   ! case younger stage present
               _GET_(self%id_FiJu_D, sDJu)                                                                          !   get younger stage biomass
               sDFiOS = sDFiOS + sDJu                                                                               !   add younger stage biomass to sDFiOS
           endif                                                                                                    !
           if (self%qStageOpt == 2 .OR. self%qStageOpt == 3) then                                                   ! case older stage present
               _GET_(self%id_FiAd_D, sDAd)                                                                          !   get older stage biomass
               sDFiOS = sDFiOS + sDAd                                                                               !   add older stage biomass to sDFiOS
           endif                                                                                                    !
           if (self%nKShares > 0) then                                                                              ! case other not-coupled stages with shared carrying capacity
               do i = 1,self%nKShares                                                                               !   for each other stage
                  _GET_(self%id_FiSt_D(i), sDFiSt_all(i))                                                           !     get other stage biomasse
               end do                                                                                               !
               sDFiSt = sum(sDFiSt_all)                                                                             !   sum other stage biomasse
               sDFiOS = sDFiOS + sDFiSt                                                                             !   add biomass to sDFiOS
           endif                                                                                                    !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!                                                          
   !  2. calculate fish growth and assimilation of DW                                                               !                                                          
   !================================================================================================================!                                                          
        ! 2.1 temperature function of fish                                                                          !                                                          
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                          
        uFunTmFish = uFunTmGaus(uTm,self%cSigTmFish,self%cTmOptFish)                                                ! calc. temperature correction of fish vital rates
        !===========================================================================================================!
        ! 2.2 macrophyte dependency of fish                                                                         !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        aFunVegBent = max(0.0_rk,1.0_rk - self%cRelVegBent * aCovVeg)                                               ! calculate dependence of bentivory on macrophytes
        aFunVegZoo = max(0.0_rk,1.0_rk - self%cRelVegZoo * aCovVeg)                                                 ! calcuate dependence of zooplanktivory on macrophytes <==<< CHECK WITH DENNIS !!!
        if (self%lVegOpt) then                                                                                      ! case growth rate is macrophyte-dependent
            aFunVegAss = aDSubVeg /(self%hDVegGrowth + aDSubVeg + NearZero)                                         !   calculate macrophyte-dependence of growth
        else                                                                                                        !
            aFunVegAss = 1.0_rk                                                                                     !   otherwise no effect
        endif                                                                                                       !
        !===========================================================================================================!                                                          
        ! 2.2 calculate total food saturation and its contributions from zooplankton, zoobenthos, and piscivory     !                                                          
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                                                                                                                                         
        fFishZoo = self%fFishZoo / (self%fFishZoo + self%fFishBen + self%fFishPisc)                                 ! ensure that the proportion of time spent on different feeding modes sum to 1
        fFishBen = self%fFishBen / (self%fFishZoo + self%fFishBen + self%fFishPisc)                                 ! ensure that the proportion of time spent on different feeding modes sum to 1
        fFishPisc = self%fFishPisc / (self%fFishZoo + self%fFishBen + self%fFishPisc)                               ! ensure that the proportion of time spent on different feeding modes sum to 1
        BioTurb = fFishBen * sDfi * uFunTmFish * self%kTurbFish                                                     ! current bioturbation by fish (zero without benthivory)
                                                                                                                    !
        if (self%nZOOprey /= 0) then                                                                                ! case zooplanktivory 
            aDSatFiZoo = ((aFunVegZoo * sum(sDZoo*self%ZOOpref)) * (aFunVegZoo * sum(sDZoo*self%ZOOpref))) / &      !   calculate zooplanktivory saturation level
               (self%hDZooFi * self%hDZooFi + (aFunVegZoo * sum(sDZoo*self%ZOOpref)) * &                            !
               (aFunVegZoo * sum(sDZoo*self%ZOOpref)))                                                              !
        else                                                                                                        !
            aDSatFiZoo = 0.0_rk                                                                                     !
        endif                                                                                                       !
        if (self%nBENprey /= 0) then                                                                                ! case zooplanktivory 
           aDSatFiBen = ((aFunVegBent * sum(sDBent*self%BENpref)) * (aFunVegBent * sum(sDBent*self%BENpref))) / &   !   calculate bentivory saturation level
               (self%hDBentFi * self%hDBentFi + (aFunVegBent * sum(sDBent*self%BENpref)) * &                        !
               (aFunVegBent * sum(sDBent*self%BENpref)))                                                            !
        else                                                                                                        !
            aDSatFiBen = 0.0_rk                                                                                     !
        endif                                                                                                       !
        if (self%nPISCprey /= 0) then                                                                               ! case zooplanktivory 
           aDSatFiPisc = (sum(sDPisc*self%PISCpref)*sum(sDPisc*self%PISCpref)) / &                                  !   calculate piscivory saturation level
               (self%hDPiscFi*self%hDPiscFi + sum(sDPisc*self%PISCpref)*sum(sDPisc*self%PISCpref))                  !  
        else                                                                                                        !
            aDSatFiPisc = 0.0_rk                                                                                    !
        endif                                                                                                       !
        !                                                                                                           !
        aDSatFiTot = (aDSatFiZoo*fFishZoo + aDSatFiBen*fFishBen + aDSatFiPisc*fFishPisc)                            ! total (or mean) saturation level
        !===========================================================================================================!
        ! 2.3 calculate final assimilation rates and environmental correction                                       !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        ukDIncrFi = (self%kDAssFi * aFunVegAss - self%kDRespFi) * uFunTmFish - self%kMortFi                         ! calculate current maximum net population growth rate (dimensions: nlev)
        tDEnvFi = max(0.0_rk,(ukDIncrFi / (self%cDCarrFish - sDFiOS)) * sDFi*sDFi)                                  ! calculate environmental correction (dimensions: nlev) <====<< CHANGE IMPL. OF COMMON CARR. CAP.?
        tDAssFiZoo = aDSatFiZoo *(self%kDAssFi * aFunVegAss * uFunTmFish * sDfi - tDEnvFi) * fFishZoo               ! calculate zooplanktivorous assimilation rate
        tDAssFiBen = aDSatFiBen *(self%kDAssFi * aFunVegAss * uFunTmFish * sDfi - tDEnvFi) * fFishBen               ! calculate bentivorous assimilation rate
        tDAssFiPisc = aDSatFiPisc *(self%kDAssFi * aFunVegAss * uFunTmFish * sDfi - tDEnvFi) * fFishPisc            ! calculate piscivorous assimilation rate
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 3. calculate prey consumption rates (DW, N & P)                                                                !
   !================================================================================================================!
        ! 3.1 zooplankton consumption                                                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDConsFiZoo = relabZOO * (tDAssFiZoo / self%fDAssFi)                                                        ! calculate DW consumption of zooplankton (dimension: nZOOprey)
        tPConsFiZoo = rPDZoo * tDConsFiZoo                                                                          ! calculate P consumption of zooplankton (dimension: nZOOprey)
        tNConsFiZoo = rNDZoo * tDConsFiZoo                                                                          ! calculate N consumption of zooplankton (dimension: nZOOprey)
        !===========================================================================================================!
        ! 3.2 zoobenthos consumption                                                                                !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDConsFiBen = relabBEN * (tDAssFiBen / self%fDAssFi)                                                        ! calculate DW consumption of zoobenthos (dimension: nBENprey)
        tPConsFiBen = rPDBent * tDConsFiBen                                                                         ! calculate P consumption of zoobenthos (dimension: nBENprey)
        tNConsFiBen = rNDBent * tDConsFiBen                                                                         ! calculate N consumption of zoobenthos (dimension: nBENprey)
        !===========================================================================================================!
        ! 3.3 piscivorous consumption                                                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDConsFiPisc = relabPISC * (tDAssFiPisc / self%fDAssFi)                                                     ! calculate DW consumption of fish (dimension: nPISCprey)
        tPConsFiPisc = rPDPisc * tDConsFiPisc                                                                       ! calculate P consumption of fish (dimension: nPISCprey)
        tNConsFiPisc = rNDPisc * tDConsFiPisc                                                                       ! calculate N consumption of fish (dimension: nPISCprey)
        !===========================================================================================================!
        ! 3.4 total consumption                                                                                     !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDConsFiZooSum = sum(tDConsFiZoo)                                                                           ! calculate total zooplankton DW consumption
        tDConsFiBenSum = sum(tDConsFiBen)                                                                           ! calculate total zoobenthos DW consumption
        tDConsFiPiscSum = sum(tDConsFiPisc)                                                                         ! calculate total fish DW consumption
        tPConsFiZooSum = sum(tPConsFiZoo)                                                                           ! calculate total zooplankton P consumption
        tPConsFiBenSum = sum(tPConsFiBen)                                                                           ! calculate total zoobenthos P consumption
        tPConsFiPiscSum = sum(tPConsFiPisc)                                                                         ! calculate total fish P consumption
        tNConsFiZooSum = sum(tNConsFiZoo)                                                                           ! calculate total zooplankton N consumption
        tNConsFiBenSum = sum(tNConsFiBen)                                                                           ! calculate total zoobenthos N consumption
        tNConsFiPiscSum = sum(tNConsFiPisc)                                                                         ! calculate total fish N consumption
        tDConsFiTot = tDConsFiZooSum + tDConsFiBenSum + tDConsFiPiscSum                                             ! calculate total DW consumption
        tPConsFiTot = tPConsFiZooSum + tPConsFiBenSum + tPConsFiPiscSum                                             ! calculate total P consumption 
        tNConsFiTot = tNConsFiZooSum + tNConsFiBenSum + tNConsFiPiscSum                                             ! calculate total N consumption 
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. calculate N, and P assimilation                                                                             !
   !================================================================================================================!
        ! 4.1 zooplankton                                                                                           !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 4.1.1 Nitrogen                                                                                       !
             !------------------------------------------------------------------------------------------------------!
             afNAssFiZoo = min(1.0_rk,(self%cNDFishRef / rNDZoo) * self%fDAssFi)                                    ! calculate N assimilation efficiency of zooplankton
             tNAssFiZoo = afNAssFiZoo * tNConsFiZoo                                                                 ! calculate N assimilation rate from zooplanktivorous
             !======================================================================================================!
             ! 4.1.2 Phosphorous                                                                                    !
             !------------------------------------------------------------------------------------------------------!
             afPAssFiZoo = min(1.0_rk,(self%cPDFishRef / rPDZoo) * self%fDAssFi)                                    ! calculate P assimilation efficiency of zooplankton
             tPAssFiZoo = afPAssFiZoo * tPConsFiZoo                                                                 ! calculate P assimilation rate from zooplanktivorous
        !===========================================================================================================!
        ! 4.2 benthos                                                                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 4.2.1 Nitrogen                                                                                       !
             !------------------------------------------------------------------------------------------------------!
             afNAssFiBen = min(1.0_rk,(self%cNDFishRef / rNDBent) * self%fDAssFi)                                   ! calculate N assimilation efficiency of zoobenthos
             tNAssFiBen = afNAssFiBen * tNConsFiBen                                                                 ! calculate N assimilation rate from zoobentivory
             !======================================================================================================!
             ! 4.2.2 Phosphorous                                                                                    !
             !------------------------------------------------------------------------------------------------------!
             afPAssFiBen = min(1.0_rk,(self%cPDFishRef / rPDBent) * self%fDAssFi)                                   ! calculate P assimilation efficiency of zoobenthos 
             tPAssFiBen = afPAssFiBen * tPConsFiBen                                                                 ! calculate P assimilation rate from zoobentivory
        !===========================================================================================================!
        ! 4.3 piscivory                                                                                             !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 4.3.1 Nitrogen                                                                                       !
             !------------------------------------------------------------------------------------------------------!
             afNAssFiPisc = min(1.0_rk,(self%cNDFishRef / rNDPisc) * self%fDAssFi)                                  ! calculate N assimilation efficiency of fish
             tNAssFiPisc = afNAssFiPisc * tNConsFiPisc                                                              ! calculate N assimilation rate from piscivory
             !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 4.3.2 Phosphorous                                                                                    !
             !------------------------------------------------------------------------------------------------------!
             afPAssFiPisc = min(1.0_rk,(self%cPDFishRef / rPDPisc) * self%fDAssFi)                                  ! calculate P assimilation efficiency of fish
             tPAssFiPisc = afPAssFiPisc * tPConsFiPisc                                                              ! calculate P assimilation rate from piscivory
        !===========================================================================================================!
        ! 3.4 total assimilation                                                                                    ! 
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             tDAssFiTot = tDAssFiZoo + tDAssFiBen + tDAssFiPisc                                                     ! calculate total DW assimilation rate
             tPAssFiTot = sum(tPAssFiZoo) + sum(tPAssFiBen) + sum(tPAssFiPisc)                                      ! calculate total P assimilation rate
             tNAssFiTot = sum(tNAssFiZoo) + sum(tNAssFiBen) + sum(tNAssFiPisc)                                      ! calculate total N assimilation rate
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 5. calculate respiration, egestion, excretion, mortality and migration                                         !
   !================================================================================================================!
        ! 5.1 calculate respiration/excretion                                                                       !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDRespFi = (self%cPDFishRef / rPDFi) * self%kDRespFi * uFunTmFish * sDFi                                    ! calculate DW respiration rate
        if (.NOT. self%lNutMeth) then                                                                               ! case dynamic stochiometry
        tPExcrFi = (rPDFi / self%cPDFishRef) * self%kDRespFi * uFunTmFish * sPFi                                    !   calculate P excretion rate
        tNExcrFi = (rNDFi / self%cNDFishRef) * self%kDRespFi * uFunTmFish * sNFi                                    !   calculate N excretion rate
        else                                                                                                        ! case fixed stochiometry
            tPExcrFi = tDRespFi * self%cPDFishRef                                                                   !   calculate P excretion rate
            tNExcrFi = tDRespFi * self%cNDFishRef                                                                   !   calculate N excretion rate
        endif                                                                                                       !
        !===========================================================================================================!
        ! 5.2 calculate fish egestion                                                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDEgesFi = tDConsFiTot - tDAssFiTot                                                                         ! calculate DW egestion rate
        tPEgesFi = tPConsFiTot - tPAssFiTot                                                                         ! calculate P egestion rate
        tNEgesFi = tNConsFiTot - tNAssFiTot                                                                         ! calculate N egestion rate
        !===========================================================================================================!
        ! 5.3 calculate fish mortality                                                                              !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDMortFi = self%kMortFi * sDFi + (1.0_rk - aDSatFiTot) * tDEnvFi                                            ! calculate current mortality rate
        tPMortFi = rPDFi * tDMortFi                                                                                 !   calculate loss of P from mortality
        tNMortFi = rNDFi * tDMortFi                                                                                 !   calculate loss of N from mortality
        !===========================================================================================================!
        ! 5.4 calculate fish migration                                                                              !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDMigrFi = self%kMigrFish *(self%cDFiIn - sDFi)                                                             ! calculate current migration rate
        tPMigrFi = self%kMigrFish *(self%cPDFishRef * self%cDFiIn - sPFi)                                           !   calculate change in P from migration
        tNMigrFi = self%kMigrFish *(self%cNDFishRef * self%cDFiIn - sNFi)                                           !   calculate change in N from migration
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 6. special case: ageing/reproduction exchange between fish instances                                           !
   !================================================================================================================!
        ! 6.1 default case: no stages                                                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDReprFish = 0.0_rk                                                                                         ! initialize DW reproduction flux
        tPReprFish = 0.0_rk                                                                                         ! initialize P reproduction flux
        tNReprFish = 0.0_rk                                                                                         ! initialize N reproduction flux
        tDAgeFish = 0.0_rk                                                                                          ! initialize DW aging flux
        tPAgeFish = 0.0_rk                                                                                          ! initialize P aging flux
        tNAgeFish = 0.0_rk                                                                                          ! initialize N aging flux
        !===========================================================================================================!
        ! 6.2 case adult fish: calculate reproduction                                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        if (self%qStageOpt == 1 .OR. self%qStageOpt == 3) then                                                      ! case reproduction
           if (Day >= self%cDayReprFish .AND. Day <= self%cDayReprFish + 1.0_rk) then                               !   if it is time for reproduction
              tDReprFish = self%fReprFish * sDFi                                                                    !     calculate reproduction DW flux
              tPReprFish = rPDFi * tDReprFish                                                                       !     calculate reproduction P flux
              tNReprFish = rNDFi * tDReprFish                                                                       !     calculate reproduction N flux
           endif                                                                                                    !
        endif                                                                                                       !
        !===========================================================================================================!
        ! 6.3 case juvenile fish: calculate ageing                                                                  !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        if (self%qStageOpt == 2 .OR. self%qStageOpt == 3) then                                                      ! case aging
           if (Day >= self%cDayAgeFish .AND. Day <= self%cDayAgeFish + 1.0_rk) then                                 !   if it is time for aging
              tDAgeFish = self%fAgeFish * sDFi                                                                      !     calculate aging DW flux
              tPAgeFish = rPDFi * tDAgeFish                                                                         !     calculate aging P flux
              tNAgeFish = rNDFi * tDAgeFish                                                                         !     calculate aging N flux
           endif                                                                                                    !
        endif                                                                                                       !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 7. final flux calculations                                                                                     !
   !================================================================================================================!
        ! 7.1 final fish rate of change                                                                             !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDFi = tDMigrFi + tDAssFiTot - tDRespFi - tDMortFi - tDAgeFish - tDReprFish                                 ! calculate the final rate of change in DW
        tPFi = tPMigrFi + tPAssFiTot - tPExcrFi - tPMortFi - tPAgeFish - tPReprFish                                 ! calculate the final rate of change in P
        tNFi = tNMigrFi + tNAssFiTot - tNExcrFi - tNMortFi - tNAgeFish - tNReprFish                                 ! calculate the final rate of change in N
        !===========================================================================================================!
        ! 7.2 final fluxes to external abiotic variables                                                            !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 7.2.1 dry weight                                                                                       !
           !--------------------------------------------------------------------------------------------------------!
           tDMortFiBot = self%fDBone * (tDMortFi)                                                                   ! calculate flux out of the system (into the sediment) from mortality
           tDMortFiTOM = (tDMortFi) - tDMortFiBot                                                                   ! calculate part of dead fish staying in the system
           tDFiTOMW = tDEgesFi + tDMortFiTOM                                                                        ! calculate total flux of DW to the water column
           tDFiPOMW = tDFiTOMW * (1.0_rk - self%fFiDOMW)                                                            ! calculate particulate fraction of DW flux to water column
           tDFiDOMW = tDFiTOMW * self%fFiDOMW                                                                       ! calculate dissolved fraction of DW flux to water column
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 7.2.2 nitrogen                                                                                         !
           !--------------------------------------------------------------------------------------------------------!
           tNEgesFiNH4 = self%fDissEgesFish * tNEgesFi                                                              ! calculate dissolved N part of egestion flux
           tNMortFiBot = self%fDBone * tNMortFi                                                                     ! calculate flux of N out of the system (into the sediment) from mortality
           tNMortFiNH4 = self%fDissMortFish *(tNMortFi - tNMortFiBot)                                               ! calculate dissolved N part of mortality flux
           tNFiNH4W = tNExcrFi + tNEgesFiNH4 + tNMortFiNH4                                                          ! calculate total dissolved N flux to the water column
                                                                                                                    !
           tNMortFiTOM = tNMortFi - tNMortFiBot - tNMortFiNH4                                                       ! calculate organic N part of mortality flux
           tNEgesFiTOM = tNEgesFi - tNEgesFiNH4                                                                     ! calculate organic N part of egestion
           tNFiTOMW = tNEgesFiTOM + tNMortFiTOM                                                                     ! calculate total organic N flux to the water column
           tNFiPOMW = tNFiTOMW * (1.0_rk - self%fFiDOMW)                                                            ! calculate particulate part of organic N flux to water column
           tNFiDOMW = tNFiTOMW * self%fFiDOMW                                                                       ! calculate dissolved part of organic N flux to water column
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 7.2.3 phosphorous                                                                                      !
           !--------------------------------------------------------------------------------------------------------!
           tPEgesFiPO4 = self%fDissEgesFish * tPEgesFi                                                              ! calculate dissolved P part of egestion flux
           tPMortFiBot = self%fPBone * tPMortFi                                                                     ! calculate flux of P out of the system (into the sediment) from mortality
           tPMortFiPO4 = self%fDissMortFish *(tPMortFi - tPMortFiBot)                                               ! calculate dissolved P part of mortality flux
           tPFiPO4W= tPExcrFi + tPEgesFiPO4 + tPMortFiPO4                                                           ! calculate total dissolved P flux to the water column
                                                                                                                    !
           tPMortFiTOM = tPMortFi - tPMortFiBot - tPMortFiPO4                                                       ! calculate organic P part of mortality flux
           tPEgesFiTOM = tPEgesFi - tPEgesFiPO4                                                                     ! calculate organic P part of egestion
           tPFiTOMW = tPEgesFiTOM + tPMortFiTOM                                                                     ! calculate total organic P flux to the water column
           tPFiPOMW = tPFiTOMW * (1.0_rk - self%fFiDOMW)                                                            ! calculate particulate part of organic P flux to water column
           tPFiDOMW = tPFiTOMW * self%fFiDOMW                                                                       ! calculate dissolved part of organic P flux to water column
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 8. update model variables                                                                                      !
   !================================================================================================================!
      ! 8.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_ODE_(self%id_sDFi,tDFi)                                                                                  ! set fish DW ODE
      _SET_ODE_(self%id_sPFi,tPFi)                                                                                  ! set fish P ODE
      _SET_ODE_(self%id_sNFi,tNFi)                                                                                  ! set fish N ODE
      !=============================================================================================================!
      ! 8.2 update external biotic state variables                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 8.2.1 zooplankton                                                                                        !
         !----------------------------------------------------------------------------------------------------------!
         if (self%nZOOprey /= 0) then                                                                               ! case zooplanktivory
            do i_prey = 1, self%nZOOprey                                                                            !   for all zooplankton prey
               _SET_ODE_(self%id_DFoodZoo(i_prey),  -tDConsFiZoo(i_prey))                                           !     update zooplankton prey DW ODEs
               _SET_ODE_(self%id_NFoodZoo(i_prey),  -tNConsFiZoo(i_prey))                                           !     update zooplankton prey N ODEs 
               _SET_ODE_(self%id_PFoodZoo(i_prey),  -tPConsFiZoo(i_prey))                                           !     update zooplankton prey P ODEs
            end do                                                                                                  !
         endif                                                                                                      !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 8.2.2 zoobenthos                                                                                         !
         !----------------------------------------------------------------------------------------------------------!
         if (self%nBENprey /= 0) then                                                                               ! case bentivory
            do i_prey = 1,self%nBENprey                                                                             !   for all zoobenthos prey
               _SET_DIAGNOSTIC_(self%id_tDConsFiBen_out(i_prey), -tDConsFiBen(i_prey))                              !
               _SET_DIAGNOSTIC_(self%id_tNConsFiBen_out(i_prey), -tNConsFiBen(i_prey))                              !
               _SET_DIAGNOSTIC_(self%id_tPConsFiBen_out(i_prey), -tPConsFiBen(i_prey))                              !
            end do                                                                                                  !
         endif                                                                                                      !
         _SET_DIAGNOSTIC_(self%id_BioTurb,BioTurb)                                                                  !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 8.2.3 fish prey                                                                                          !
         !----------------------------------------------------------------------------------------------------------!
         if (self%nPISCprey /= 0) then                                                                              ! case piscivory
            do i_prey = 1,self%nPISCprey                                                                            !   for all fish prey
               _SET_ODE_(self%id_DFoodPisc(i_prey),  -tDConsFiPisc(i_prey))                                         !     update fish prey DW ODEs
               _SET_ODE_(self%id_NFoodPisc(i_prey),  -tNConsFiPisc(i_prey))                                         !     update fish prey N ODEs
               _SET_ODE_(self%id_PFoodPisc(i_prey),  -tPConsFiPisc(i_prey))                                         !     update fish prey P ODEs
            end do                                                                                                  !
         endif                                                                                                      !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 8.2.4 other stages                                                                                       !
         !----------------------------------------------------------------------------------------------------------!
         if (self%qStageOpt == 1 .OR. self%qStageOpt == 3) then                                                     ! case reproduction
            _SET_ODE_(self%id_FiJu_D,  tDReprFish)                                                                  !   update juvenile stage DW ODE
            _SET_ODE_(self%id_FiJu_N,  tNReprFish)                                                                  !   update juvenile stage N ODE
            _SET_ODE_(self%id_FiJu_P,  tPReprFish)                                                                  !   update juvenile stage P ODE
         endif                                                                                                      !
         if (self%qStageOpt == 2 .OR. self%qStageOpt == 3) then                                                     ! case aging
            _SET_ODE_(self%id_FiAd_D,  tDAgeFish)                                                                   !   update older stage DW ODE
            _SET_ODE_(self%id_FiAd_N,  tNAgeFish)                                                                   !   update older stage N ODE
            _SET_ODE_(self%id_FiAd_P,  tPAgeFish)                                                                   !   update older stage P ODE
         endif                                                                                                      !
      !=============================================================================================================!
      ! 8.3 update external abiotic state variables                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_ODE_(self%id_DPOMpoolW, tDFiPOMW)                                                                        ! update particular organic matter DW  water column ODE 
      _SET_ODE_(self%id_DDOMpoolW, tDFiDOMW)                                                                        ! update dissolved organic matter DW water column ODE
                                                                                                                    !
      _SET_ODE_(self%id_NH4poolW,  tNFiNH4W)                                                                        ! update dissolved inorganic N water column ODE
      _SET_ODE_(self%id_NPOMpoolW, tNFiPOMW)                                                                        ! update particulate organic N water column ODE
      _SET_ODE_(self%id_NDOMpoolW, tNFiDOMW)                                                                        ! update dissolved organic N water column ODE
                                                                                                                    !
      _SET_ODE_(self%id_PO4poolW,  tPFiPO4W)                                                                        ! update dissolved inorganic P water column ODE
      _SET_ODE_(self%id_PPOMpoolW, tPFiPOMW)                                                                        ! update particulate organic P water column ODE
      _SET_ODE_(self%id_PDOMpoolW, tPFiDOMW)                                                                        ! update dissolved organic P water column ODE
      !=============================================================================================================!
      ! 8.4 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
          _SET_DIAGNOSTIC_(self%id_tDMigrFi,         tDMigrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNMigrFi,         tNMigrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPMigrFi,         tPMigrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDConsFiZooSum,   tDConsFiZooSum)                                                !
          _SET_DIAGNOSTIC_(self%id_tNConsFiZooSum,   tNConsFiZooSum)                                                !
          _SET_DIAGNOSTIC_(self%id_tPConsFiZooSum,   tPConsFiZooSum)                                                !                  
          _SET_DIAGNOSTIC_(self%id_tDConsFiBenSum,   tDConsFiBenSum)                                                !
          _SET_DIAGNOSTIC_(self%id_tNConsFiBenSum,   tNConsFiBenSum)                                                !
          _SET_DIAGNOSTIC_(self%id_tPConsFiBenSum,   tPConsFiBenSum)                                                !      
          _SET_DIAGNOSTIC_(self%id_tDConsFiPiscSum,  tDConsFiPiscSum)                                               !
          _SET_DIAGNOSTIC_(self%id_tNConsFiPiscSum,  tNConsFiPiscSum)                                               !
          _SET_DIAGNOSTIC_(self%id_tPConsFiPiscSum,  tPConsFiPiscSum)                                               ! 
          _SET_DIAGNOSTIC_(self%id_tDEgesFi,         tDEgesFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNEgesFi,         tNEgesFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPEgesFi,         tPEgesFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDFiPOMW,         tDFiPOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDFiDOMW,         tDFiDOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDMortFi,         tDMortFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNMortFi,         tNMortFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPMortFi,         tPMortFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDMortFiBot,      tDMortFiBot)                                                   !
          _SET_DIAGNOSTIC_(self%id_tNMortFiBot,      tNMortFiBot)                                                   !
          _SET_DIAGNOSTIC_(self%id_tPMortFiBot,      tPMortFiBot)                                                   !
          _SET_DIAGNOSTIC_(self%id_tDRespFi,         tDRespFi)                                                      !                                                         !
          _SET_DIAGNOSTIC_(self%id_tNExcrFi,         tNExcrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNFiNH4W,         tNFiNH4W)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNFiPOMW,         tNFiPOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNFiDOMW,         tNFiDOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPExcrFi,         tPExcrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPFiPO4W,         tPFiPO4W)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPFiPOMW,         tPFiPOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPFiDOMW,         tPFiDOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDAgeFish,        tDAgeFish)                                                     !
          _SET_DIAGNOSTIC_(self%id_tNAgeFish,        tNAgeFish)                                                     !
          _SET_DIAGNOSTIC_(self%id_tPAgeFish,        tPAgeFish)                                                     !
          _SET_DIAGNOSTIC_(self%id_tDReprFish,       tDReprFish)                                                    !
          _SET_DIAGNOSTIC_(self%id_tNReprFish,       tNReprFish)                                                    !
          _SET_DIAGNOSTIC_(self%id_tPReprFish,       tPReprFish)                                                    !
         if (self%nZOOprey /= 0) then                                                                               ! case zooplanktivory
            do i_prey = 1, self%nZOOprey                                                                            !
                _SET_DIAGNOSTIC_(self%id_tDConsFiZoo(i_prey), tDConsFiZoo(i_prey))                                  !
                _SET_DIAGNOSTIC_(self%id_tPConsFiZoo(i_prey), tPConsFiZoo(i_prey))                                  !
                _SET_DIAGNOSTIC_(self%id_tNConsFiZoo(i_prey), tNConsFiZoo(i_prey))                                  !
            end do                                                                                                  !
         endif                                                                                                      !
         if (self%nPISCprey /= 0) then                                                                              ! case piscivory
            do i_prey = 1,self%nPISCprey                                                                            !
                _SET_DIAGNOSTIC_(self%id_tDConsFiPisc(i_prey), tDConsFiPisc(i_prey))                                !
                _SET_DIAGNOSTIC_(self%id_tPConsFiPisc(i_prey), tPConsFiPisc(i_prey))                                !
                _SET_DIAGNOSTIC_(self%id_tNConsFiPisc(i_prey), tNConsFiPisc(i_prey))                                !
            end do                                                                                                  !
         endif                                                                                                      !
      endif                                                                                                         !
   !================================================================================================================!
   _LOOP_END_ !!! END OF MODEL CODE::
end subroutine do

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO BOTTOM                                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_fish_pclake), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk), dimension(self%nBENprey) :: tDConsFiBen, tNConsFiBen, tPConsFiBen
   real(rk)                           :: bot_pel_conv
   integer                            :: i_prey

   _HORIZONTAL_LOOP_BEGIN_  !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve bentivorous consumption rates and apply/save                                                      !
   !================================================================================================================!
      if (self%nBENprey /= 0) then                                                                                  ! in case of bentivory
         _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)                                                        !
         do i_prey = 1,self%nBENprey                                                                                !   for each benthos prey
            _GET_(self%id_tDConsFiBen(i_prey),tDConsFiBen(i_prey))                                                  !     get the betivorous DW consumption
            _GET_(self%id_tNConsFiBen(i_prey),tNConsFiBen(i_prey))                                                  !     get the betivorous N consumption
            _GET_(self%id_tPConsFiBen(i_prey),tPConsFiBen(i_prey))                                                  !     get the betivorous P consumption
            _SET_BOTTOM_ODE_(self%id_DFoodBen(i_prey), tDConsFiBen(i_prey)*bot_pel_conv)                            !     apply consumption to zoobenthos prey DW
            _SET_BOTTOM_ODE_(self%id_NFoodBen(i_prey), tNConsFiBen(i_prey)*bot_pel_conv)                            !     apply consumption to zoobenthos prey N
            _SET_BOTTOM_ODE_(self%id_PFoodBen(i_prey), tPConsFiBen(i_prey)*bot_pel_conv)                            !     apply consumption to zoobenthos prey P
            _SET_BOTTOM_EXCHANGE_(self%id_DFoodBen_PV(i_prey),tDConsFiBen(i_prey)*bot_pel_conv*bot_pel_conv)        !     update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
            _SET_BOTTOM_EXCHANGE_(self%id_NFoodBen_PV(i_prey),tNConsFiBen(i_prey)*bot_pel_conv*bot_pel_conv)        !     update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
            _SET_BOTTOM_EXCHANGE_(self%id_PFoodBen_PV(i_prey),tPConsFiBen(i_prey)*bot_pel_conv*bot_pel_conv)        !     update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         end do                                                                                                     !
      endif                                                                                                         !
   !================================================================================================================!
   _HORIZONTAL_LOOP_END_  !!! END OF MODEL CODE::  
end subroutine do_bottom
   
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: GET VERTICAL MOVEMENT                                                                                                                                                              §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine get_vertical_movement(self,_ARGUMENTS_GET_VERTICAL_MOVEMENT_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_fish_pclake),intent(in)    :: self
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
         if (par .GT. self%cMinLight) then                                                                          !     if light level is higher than tresholds
            qSWIM = -1                                                                                              !       swim down
         endif                                                                                                      !
      endif                                                                                                         !
      _GET_(self%id_oxygen,O2)                                                                                      !   get oxygen concentration
      if (O2 < self%cMinO2) then                                                                                    !   low oxygen induces vertical movement
         qSWIM = 1                                                                                                  !     swim up
      endif                                                                                                         !
   elseif (self%qTrans == 1) then
       qSWIM = 0
   endif                                                                                                            !
   _SET_VERTICAL_MOVEMENT_(self%id_sDFi,qSWIM*self%Vswim)                                                           ! set DW migration speed
   _SET_VERTICAL_MOVEMENT_(self%id_sPFi,qSWIM*self%Vswim)                                                           ! set P migration speed
   _SET_VERTICAL_MOVEMENT_(self%id_sNFi,qSWIM*self%Vswim)                                                           ! set N migration speed
   !================================================================================================================!
   _LOOP_END_   !!! END OF MODEL CODE::  
end subroutine get_vertical_movement
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
end module wet_fish_pclake
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------