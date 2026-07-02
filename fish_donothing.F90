#include "fabm_driver.h"
!-----------------------------------------------------------------------
! MODULE: FISH - EMPTY VERSION FOR DEBUGGING
!-----------------------------------------------------------------------
module wet_fish
   use fabm_types
   use wet_utility, ONLY:uFunTmGaus
   use fabm_particle
   use fabm_expressions
   use fabm_builtin_models
   implicit none
   private

   type, extends(type_particle_model),public :: type_wet_fish
      type (type_state_variable_id)                                   :: id_sDFi, id_sPFi, id_sNFi, id_sCFi, id_sFRes, id_sDSiz, id_fVul
      type (type_diagnostic_variable_id)                              :: id_BioTurb, id_PStar, id_predD, id_recrD, id_Day_last_save
      type (type_model_id)                                            :: id_FiJu_target, id_FiAd_target
      type (type_model_id),                 allocatable, dimension(:) :: id_BEN_prey, id_PISC_prey, id_PLAN_prey
      type (type_bottom_state_variable_id), allocatable, dimension(:) :: id_DFoodBent, id_NFoodBent, id_PFoodBent, id_CFoodBent
      type (type_state_variable_id),        allocatable, dimension(:) :: id_DFoodBent_PV, id_NFoodBent_PV, id_PFoodBent_PV, id_CFoodBent_PV, id_VFoodBent
      type (type_state_variable_id),        allocatable, dimension(:) :: id_DFoodPlan, id_NFoodPlan, id_PFoodPlan, id_CFoodPlan
      type (type_state_variable_id),        allocatable, dimension(:) :: id_DFoodPisc, id_NFoodPisc, id_PFoodPisc, id_CFoodPisc, id_PredPisc, id_pred_dummy_Pisc, id_fVulPisc
      type (type_state_variable_id),        allocatable, dimension(:) :: id_PRED_D, id_FiSt_D
      type (type_state_variable_id)                                   :: id_FiJu_D, id_FiJu_P, id_FiJu_N, id_FiJu_Res, id_FiAd_D, id_FiAd_P, id_FiAd_N, id_FiAd_Res, id_FiJu_Siz, id_FiAd_Siz
      type (type_state_variable_id)                                   :: id_DPOMpoolW, id_PPOMpoolW, id_NPOMpoolW, id_NH4poolW, id_DDOMpoolW, id_PDOMpoolW, id_NDOMpoolW, id_PO4poolW
      type (type_state_variable_id)                                   :: id_CPOMpoolW, id_CDOMpoolW, id_CO2poolW, id_FiJu_C, id_FiAd_C
      type (type_diagnostic_variable_id)                              :: id_tDMigrFi, id_tNMigrFi, id_tPMigrFi, id_tCMigrFi, id_tDEgesFi, id_tNEgesFi, id_tPEgesFi, id_tCEgesFi, id_tDFiPOMW, id_tDFiDOMW 
      type (type_diagnostic_variable_id)                              :: id_tDMortFiBot, id_tNMortFiBot, id_tPMortFiBot, id_tCMortFiBot, id_tDRespFi, id_tCRespFi, id_tNExcrFi, id_tNFiNH4W, id_aFeedLvlPlan
      type (type_diagnostic_variable_id)                              :: id_tDConsFiPlanSum, id_tDConsFiBentSum, id_tDConsFiPiscSum, id_fFishPlan, id_fFishBent, id_tDAssFiTot, id_aFeedLvlBent
      type (type_diagnostic_variable_id)                              :: id_tNFiPOMW, id_tNFiDOMW, id_tPExcrFi, id_tPFiPO4W, id_tPFiPOMW, id_tPFiDOMW, id_tDMortFi, id_tNMortFi, id_tPMortFi, id_tCMortFi
      type (type_diagnostic_variable_id)                              :: id_tCFiPOMW, id_tCFiDOMW
      type (type_diagnostic_variable_id)                              :: id_tDAgeFish, id_tNAgeFish, id_tPAgeFish, id_tCAgeFish, id_aFeedLvlPisc, id_fFishPisc, id_tDReproPOM, id_tNReproPOM, id_tPReproPOM, id_tCReproPOM
      type (type_diagnostic_variable_id),   allocatable, dimension(:) :: id_tDConsFiPlan, id_tNConsFiPlan, id_tPConsFiPlan, id_tCConsFiPlan, id_tDConsFiPisc, id_tNConsFiPisc, id_tPConsFiPisc, id_tCConsFiPisc
      type (type_horizontal_dependency_id)                            :: id_bot_pel_conv
      type (type_dependency_id)                                       :: id_uTm, id_oxygen, id_par, id_depth, id_pred_sms, id_recr_sms, id_Day_last
      type (type_diagnostic_variable_id),   allocatable, dimension(:) :: id_tDConsFiBent_out
      type (type_dependency_id),            allocatable, dimension(:) :: id_tDConsFiBent
      type (type_diagnostic_variable_id),   allocatable, dimension(:) :: id_tNConsFiBent_out
      type (type_dependency_id),            allocatable, dimension(:) :: id_tNConsFiBent
      type (type_diagnostic_variable_id),   allocatable, dimension(:) :: id_tPConsFiBent_out
      type (type_dependency_id),            allocatable, dimension(:) :: id_tPConsFiBent
      type (type_diagnostic_variable_id),   allocatable, dimension(:) :: id_tCConsFiBent_out
      type (type_dependency_id),            allocatable, dimension(:) :: id_tCConsFiBent
      type (type_global_dependency_id)                                :: id_Day
      type (type_dependency_id)                                       :: id_aDSubVeg, id_aCovVeg, id_aTotFish
      integer                                                         :: nPLANprey=0, nBENprey=0, nPISCprey=0, qStage, nPRED=0, nMACS, qTrans, qOPT, qODB
      logical                                                         :: lVegOpt, lJUfa, lADfa, lNutMeth, predation, diagnostics, lAggr
      real(rk)                                                        :: kMigrFish, cDFiIn, fDBone, fPBone, cDCarrFish, fDissEgesFish, kTurbFish, fDissMortFish, cTmOptFish, cSigTmFish, cDayReprFish
      real(rk)                                                        :: cDinit, cDfin, cDegg, fGonad, fReproFish, fDAssFi, kDRespFi, kMortFi, hDVegGrowth, cPDRef, cNDRef, cCDRef
      real(rk)                                                        :: cDFiMin, fFiDOMW, cRelVegBent, cRelVegPlan, cVswim, vFAOut, vFAKPred, vFARel, afrFA, cMinO2, cMinLight, cMaxLight
      real(rk)                                                        :: fFC, fPV, fDRespActFi, kDConsMax, cAggr, fResMax, fResMin, cMortStarv
      real(rk),                             allocatable, dimension(:) :: cClearPlan, cClearBent, cClearPisc, fGutOccPlan, fGutOccBent
      real(rk),                             allocatable, dimension(:) :: fGutOccPisc
      character(len=64),                    allocatable, dimension(:) :: PLANprey_suffix, BENprey_suffix
      
   contains
      procedure :: initialize
      procedure :: do
      procedure :: do_bottom
      procedure :: get_vertical_movement
      procedure :: check_state
      procedure :: calc_ODB
   end type type_wet_fish

   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk)           :: Pi=3.14159265358979_rk
   real(rk),parameter :: FishZero=0.00001_rk

contains

subroutine initialize(self,configunit)
   class (type_wet_fish), intent(inout), target :: self
   integer,                     intent(in)          :: configunit
   integer  :: i_prey, i_pred, i_mac, i_stage
   character(len=64)   :: index

   call self%get_parameter(self%kMigrFish,        'kMigrFish',     '1/d',      'fish migration rate',                                              default=0.001_rk,   scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%cDFiIn,           'cDFiIn',        'gDW/m3',   'external density',                                                 default=0.005_rk                                   )
   call self%get_parameter(self%qTrans,           'qTrans',        '-',        'vert. trans. method: 0=no trans.; 1=passive; 2=O2; 3=O2 & Light',  default=2                                          )
   call self%get_parameter(self%cMinO2,           'cMinO2',        'gO2/m3',   'qtrans >= 2; oxygen conc. limit',                                  default=2.0_rk                                     )
   call self%get_parameter(self%cMinLight,        'cMinLight',     'W/m2',     'qtrans = 3; light level triggering upwards swimming',              default=1.0_rk                                     )
   call self%get_parameter(self%cMaxLight,        'cMaxLight',     'W/m2',     'qtrans = 3; light level triggering downwards swimming',            default=40.0_rk                                    )
   call self%get_parameter(self%cVswim,           'cVswim',        'm/d',      'qtrans > 1; vertical migration speed',                             default=10.0_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%cDFiMin,          'cDFiMin',       'gDW/m3',   'minimum DW density',                                               default=0.0001_rk                                  )
   call self%get_parameter(self%qStage,           'qStage',        '-',        'stage coupling method: 0=nothing; 1=repro.; 2=maturation; 3=both', default=0                                          )
   if (self%qStage > 0) then
       call self%get_parameter(self%fResMax,      'fResMax',       '-',        'maximum reserve fraction of total biomass',                        default=0.5_rk                                     )
       call self%get_parameter(self%fResMin,      'fResMin',       '-',        'minimum reserve fraction of total biomass',                        default=0.16_rk                                    )
       call self%get_parameter(self%cMortStarv,   'cMortStarv',    '-',        'starvation mortality proportionality constant',                    default=0.2_rk                                    )
       call self%get_parameter(self%cDinit,       'cDinit',        'gDW',      'initial individual dry weight of stage',                           default=0.0_rk                                     )
       call self%get_parameter(self%cDfin,        'cDfin',         'gDW',      'final individual dry weight of stage',                             default=0.0_rk                                     )
   endif
   if (self%qStage .eq. 1 .OR. self%qStage .eq. 3) then
       call self%get_parameter(self%cDayReprFish, 'cDayReprFish',  'day-of-year', 'qStage = 1 or 3; reproduction date',                            default=120.0_rk                                   )
       call self%get_parameter(self%fReproFish,   'fReproFish',    '-',        'reproductive conversion efficiency',                               default=0.01_rk                                    )
       call self%get_parameter(self%fGonad,       'fGonad',        '-',        'maximum gonad fraction of reserve biomass',                          default=0.0_rk                                     )
       call self%get_parameter(self%cDegg,        'cDegg',         'gDW',      'hatching size',                                                    default=0.0_rk                                     )
   endif
   call self%get_parameter(self%qODB,             'qODB',          '-',        'toggle optimal diet breadth: 0=off; 1=on',                         default=1                                          )
   call self%get_parameter(self%qOPT,             'qOPT',          '-',        'toggle optimal behavior: 0=off; 1=on',                             default=0                                          )
   call self%get_parameter(self%lAggr,            'lAggr',         '-',        'toggle intraspecific aggresion',                                   default=.false.                                    )
   call self%get_parameter(self%cAggr,            'cAggr',         'm3/gDW/d', 'intraspecific aggresion level',                                    default=0.0_rk,     scale_factor=1.0_rk/secs_pr_day)
   if (self%qOPT .eq. 0) then
      call self%get_parameter(self%fFC,           'fFC',           '-',        'feeding efficiency in refuge relative to arena',                   default=1.0_rk                                     )
      call self%get_parameter(self%fPV,           'fPV',           '-',        'predation vulnerability in refuge relative to arena',              default=1.0_rk                                     )
   else
      call self%get_parameter(self%fFC,           'fFC',           '-',        'feeding efficiency in refuge relative to arena',                   default=0.0_rk                                     )
      call self%get_parameter(self%fPV,           'fPV',           '-',        'predation vulnerability in refuge relative to arena',              default=0.0_rk                                     )
   endif
   call self%get_parameter(self%predation,        'predation',     '-',        'toggle predation',                                                 default=.false.                                    )
   call self%get_parameter(self%diagnostics,      'diagnostics',   '-',        'toggle diagnostic output',                                         default=.true.                                     )
   call self%get_parameter(self%lNutMeth,         'lNutMeth',      '-',        'fixed stoichiometry (0 = variable, 1 = fixed)',                    default=.false.                                    )
   call self%get_parameter(self%cPDRef,           'cPDRef',        '-',        'reference P:DW ratio of fish',                                     default=0.022_rk                                   )
   call self%get_parameter(self%cNDRef,           'cNDRef',        '-',        'reference N:DW ratio of fish',                                     default=0.1_rk                                      )
   call self%get_parameter(self%cCDRef,           'cCDRef',        '-',        'reference C:DW ratio of fish',                                     default=0.4_rk                                      )
   call self%get_parameter(self%fDAssFi,          'fDAssFi',       '-',        'assimilation efficiency of fish',                                  default=0.4_rk                                     )
   call self%get_parameter(self%kDRespFi,         'kDRespFi',      '1/d',      'maintenance respiration rate constant of fish at 20*C',             default=0.01_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%fDRespActFi,      'fDRespActFi',   '-',        'activity respiration as fraction of maintenance',                   default=0.5_rk                                     )
   call self%get_parameter(self%kDConsMax,        'kDConsMax',     '1/d',      'maximum consumption rate of fish',                                 default=0.1_rk,     scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%kMortFi,          'kMortFi',       '1/d',      'specific mortality rate of fish',                                  default=0.001_rk,   scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%fDissMortFish,    'fDissMortFish', '-',        'soluble inorg. nut. frac. of dead fish',                           default=0.1_rk                                     )
   call self%get_parameter(self%fDissEgesFish,    'fDissEgesFish', '-',        'soluble inorg. nut. frac. of egested food',                        default=0.25_rk                                    )
   call self%get_parameter(self%fDBone,           'fDBone',        '-',        'fraction of fish dry weight fixed in bones and scales',            default=0.35_rk                                    )
   call self%get_parameter(self%fPBone,           'fPBone',        '-',        'fraction of fish P fixed in bones and scales',                     default=0.5_rk                                     )
   call self%get_parameter(self%cTmOptFish,       'cTmOptFish',    '*C',       'optimal temperature of fish',                                      default=25.0_rk                                    )
   call self%get_parameter(self%cSigTmFish,       'cSigTmFish',    '*C',       'sigma of temperature Gaussian curve of fish',                       default=10.0_rk                                    )
   call self%get_parameter(self%fFiDOMW,          'fFiDOMW',       '-',        'dissolved organic matter fraction from fish mortality',            default=0.5_rk                                     )
   call self%get_parameter(self%cDCarrFish,       'cDCarrFish',    'gDW/m3',   'fish carrion density',                                             default=0.0_rk                                     )
   call self%get_parameter(self%vFAOut,           'vFAOut',        'm/d',      'foraging arena outward movement speed',                             default=0.0_rk,     scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%vFAKPred,         'vFAKPred',      'm/d',      'foraging arena predation-driven inward speed',                      default=0.0_rk,     scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%vFARel,           'vFARel',        '-',        'relative foraging arena inflow speed',                             default=0.0_rk                                     )
   call self%get_parameter(self%afrFA,            'afrFA',         '-',        'foraging arena asymmetry factor',                                  default=0.5_rk                                     )
   call self%get_parameter(self%nPLANprey,        'nPLAN',         '-',        'number of plankton prey types',                                    default=0                                          )
   call self%get_parameter(self%nBENprey,         'nBENT',         '-',        'number of benthos prey types',                                     default=0                                          )
   call self%get_parameter(self%nPISCprey,        'nPISC',         '-',        'number of fish prey types',                                        default=0                                          )
   call self%get_parameter(self%lVegOpt,          'lVegOpt',       '-',        'switch for macrophyte dependence on fish max assimilation',         default=.false.                                    )
   call self%get_parameter(self%hDVegGrowth,      'hDVegGrowth',   'gDW/m2',   'half saturation macrophyte biomass for max. feeding reduction',     default=10.0_rk                                    )
   call self%get_parameter(self%cRelVegPlan,      'cRelVegPlan',   '-',        'decrease of fish feeding per macrophytes cover; max. 0.01',        default=0.0_rk                                     )
   call self%get_parameter(self%cRelVegBent,      'cRelVegBent',   '-',        'decrease of fish feeding per macrophytes cover; max. 0.01',        default=0.009_rk                                   )
   if (self%predation) call self%get_parameter(self%nPRED,'nPRED','-','number of predator types',default=0)

   call self%register_state_variable(self%id_sDFi, 'sD', 'gDW/m3', 'fish dry weight', self%cDFiIn)
   call self%register_state_variable(self%id_sPFi, 'sP', 'gP/m3', 'fish P mass', self%cDFiIn*self%cPDRef)
   call self%register_state_variable(self%id_sNFi, 'sN', 'gN/m3', 'fish N mass', self%cDFiIn*self%cNDRef)
   call self%register_state_variable(self%id_sCFi, 'sC', 'gC/m3', 'fish C mass', self%cDFiIn*self%cCDRef)

   call self%register_diagnostic_variable(self%id_BioTurb,       'Bioturbation',   'gDW/m3/d',   'Bioturbation')
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_bioturbation',units='gDW/m3/d',aggregate_variable=.true.),self%id_BioTurb,scale_factor=1._rk)

   call self%register_dependency(self%id_uTm, type_bulk_standard_variable(name='temperature',units='degrees_C'))
   call self%register_dependency(self%id_oxygen,type_bulk_standard_variable(name='oxygen',units='gO2 m-3'))
   call self%register_horizontal_dependency(self%id_bot_pel_conv,type_bulk_standard_variable(name='bot_pel_conv',units='m-1'))
   call self%register_dependency(self%id_depth,type_bulk_standard_variable(name='depth',units='m'))
   call self%register_global_dependency(self%id_Day, type_global_standard_variable(name='day',units='d'))
   call self%register_dependency(self%id_aDSubVeg, type_bulk_standard_variable(name='submerged_vegetation_biomass',units='gDW m-3'))
   call self%register_dependency(self%id_aCovVeg, type_bulk_standard_variable(name='submerged_vegetation_cover',units='-'))
   call self%register_dependency(self%id_aTotFish, type_bulk_standard_variable(name='total_fish',units='gDW m-3'))
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_fish',units='gDW/m3',aggregate_variable=.true.),self%id_sDFi,scale_factor=1._rk)

   call self%register_diagnostic_variable(self%id_tDMigrFi, 'tDMigrFi',  'gDW/m3/s', 'net vertical migration flux of fish D',  output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_tDRespFi, 'tDRespFi',  'gDW/m3/s', 'fish respiration',                      output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_tDMortFi, 'tDMortFi',  'gDW/m3/s', 'fish natural mortality',                output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_tDConsFiPlanSum, 'tDConsFiPlanSum',  'gDW/m3/s', 'total plankton consumed by fish',       output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_tDConsFiBentSum, 'tDConsFiBentSum',  'gDW/m3/s', 'total benthos consumed by fish',        output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_tDConsFiPiscSum, 'tDConsFiPiscSum',  'gDW/m3/s', 'total fish consumed by fish',           output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_fFishPlan, 'fFishPlan',       '-',        'fraction of food from plankton',        output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_fFishBent, 'fFishBent',       '-',        'fraction of food from benthos',         output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_tDAssFiTot, 'tDAssFiTot',      'gDW/m3/s', 'total fish assimilation',               output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_aFeedLvlPlan, 'aFeedLvlPlan',    '-',        'planktivorous feeding level',           output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_aFeedLvlBent, 'aFeedLvlBent',    '-',        'benthivorous feeding level',            output=output_instantaneous)

   if (self%nPLANprey /= 0) then
      allocate(self%id_PLAN_prey(self%nPLANprey))
      allocate(self%id_DFoodPlan(self%nPLANprey))
      allocate(self%id_NFoodPlan(self%nPLANprey))
      allocate(self%id_PFoodPlan(self%nPLANprey))
      allocate(self%id_CFoodPlan(self%nPLANprey))
      allocate(self%id_tDConsFiPlan(self%nPLANprey))
      allocate(self%id_tPConsFiPlan(self%nPLANprey))
      allocate(self%id_tNConsFiPlan(self%nPLANprey))
      allocate(self%id_tCConsFiPlan(self%nPLANprey))
      allocate (self%cClearPlan(self%nPLANprey))
      allocate (self%fGutOccPlan(self%nPLANprey))
      allocate (self%PLANprey_suffix(self%nPLANprey))
      do i_prey=1,self%nPLANprey
          write(index,'(i0)') i_prey
          call self%register_model_dependency(self%id_PLAN_prey(i_prey), 'PLANprey'//trim(index))
          call self%register_state_dependency(self%id_DFoodPlan(i_prey), 'plankton_D_Food'//trim(index), 'g/m3', 'plankton D Food'//trim(index))
          call self%register_state_dependency(self%id_NFoodPlan(i_prey), 'plankton_N_Food'//trim(index), 'g/m3', 'plankton N Food'//trim(index))
          call self%register_state_dependency(self%id_PFoodPlan(i_prey), 'plankton_P_Food'//trim(index), 'g/m3', 'plankton P Food'//trim(index))
          call self%register_state_dependency(self%id_CFoodPlan(i_prey), 'plankton_C_Food'//trim(index), 'g/m3', 'plankton C Food'//trim(index))
          call self%request_coupling_to_model(self%id_DFoodPlan(i_prey),self%id_PLAN_prey(i_prey), 'sD'//trim(self%PLANprey_suffix(i_prey)))
          call self%request_coupling_to_model(self%id_PFoodPlan(i_prey),self%id_PLAN_prey(i_prey), 'sP'//trim(self%PLANprey_suffix(i_prey)))
          call self%request_coupling_to_model(self%id_NFoodPlan(i_prey),self%id_PLAN_prey(i_prey), 'sN'//trim(self%PLANprey_suffix(i_prey)))
          call self%request_coupling_to_model(self%id_CFoodPlan(i_prey),self%id_PLAN_prey(i_prey), 'sC'//trim(self%PLANprey_suffix(i_prey)))
          call self%get_parameter(self%cClearPlan(i_prey),'cClearPlan'//trim(index),'m3/gDW/d','clearance rate for plankton prey '//trim(index),   default=0.24_rk,     scale_factor=1.0_rk/secs_pr_day)
          call self%get_parameter(self%fGutOccPlan(i_prey),'fGutOccPlan'//trim(index),'-',     'gut occupation factor for plankton prey '//trim(index),default=1.0_rk                                  )
          call self%get_parameter(self%PLANprey_suffix(i_prey),'PLANprey_suffix'//trim(index),'-',     'plankton prey name suffix'//trim(index),       default=''                                      )
          if (self%diagnostics) then
              call self%register_diagnostic_variable(self%id_tDConsFiPlan(i_prey), 'tDConsFiPlan_'//trim(index),	'g/m3/s','rate plankton D consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tPConsFiPlan(i_prey), 'tPConsFiPlan_'//trim(index),	'g/m3/s','rate plankton P consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tNConsFiPlan(i_prey), 'tNConsFiPlan_'//trim(index),	'g/m3/s','rate plankton N consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tCConsFiPlan(i_prey), 'tCConsFiPlan_'//trim(index),	'g/m3/s','rate plankton C consumed '//trim(index),  output=output_instantaneous)
          endif 
      end do
   endif

   if (self%nBENprey /= 0) then      
      allocate(self%id_BEN_prey(self%nBENprey))
      allocate(self%id_DFoodBent(self%nBENprey))
      allocate(self%id_NFoodBent(self%nBENprey))
      allocate(self%id_PFoodBent(self%nBENprey))
      allocate(self%id_CFoodBent(self%nBENprey))
      allocate(self%id_DFoodBent_PV(self%nBENprey))
      allocate(self%id_NFoodBent_PV(self%nBENprey))
      allocate(self%id_PFoodBent_PV(self%nBENprey))
      allocate(self%id_CFoodBent_PV(self%nBENprey))
      allocate(self%id_tDConsFiBent(self%nBENprey))
      allocate(self%id_tDConsFiBent_out(self%nBENprey))
      allocate(self%id_tPConsFiBent(self%nBENprey))
      allocate(self%id_tPConsFiBent_out(self%nBENprey))
      allocate(self%id_tNConsFiBent(self%nBENprey))
      allocate(self%id_tNConsFiBent_out(self%nBENprey))
      allocate(self%id_tCConsFiBent(self%nBENprey))
      allocate(self%id_tCConsFiBent_out(self%nBENprey))
      allocate (self%cClearBent(self%nBENprey))
      allocate (self%fGutOccBent(self%nBENprey))
      allocate (self%BENprey_suffix(self%nBENprey))
      do i_prey=1,self%nBENprey
          write(index,'(i0)') i_prey
          call self%register_model_dependency(self%id_BEN_prey(i_prey),'BENTprey'//trim(index))
          call self%register_state_dependency(self%id_DFoodBent(i_prey), 'benthos_D_Food'//trim(index), 'g/m3', 'benthos D Food'//trim(index))
          call self%register_state_dependency(self%id_NFoodBent(i_prey), 'benthos_N_Food'//trim(index), 'g/m3', 'benthos N Food'//trim(index))
          call self%register_state_dependency(self%id_PFoodBent(i_prey), 'benthos_P_Food'//trim(index), 'g/m3', 'benthos P Food'//trim(index))
          call self%register_state_dependency(self%id_CFoodBent(i_prey), 'benthos_C_Food'//trim(index), 'g/m3', 'benthos C Food'//trim(index))
          call self%request_coupling_to_model(self%id_DFoodBent(i_prey),self%id_BEN_prey(i_prey),'sD'//trim(self%BENprey_suffix(i_prey)))
          call self%request_coupling_to_model(self%id_PFoodBent(i_prey),self%id_BEN_prey(i_prey),'sP'//trim(self%BENprey_suffix(i_prey)))
          call self%request_coupling_to_model(self%id_NFoodBent(i_prey),self%id_BEN_prey(i_prey),'sN'//trim(self%BENprey_suffix(i_prey)))
          call self%request_coupling_to_model(self%id_CFoodBent(i_prey),self%id_BEN_prey(i_prey),'sC'//trim(self%BENprey_suffix(i_prey)))
          call self%register_state_dependency(self%id_DFoodBent_PV(i_prey), 'benthos_D_Food'//trim(index)//'_PV', '-', 'benthos D Food PV target number '//trim(index))
          call self%register_state_dependency(self%id_NFoodBent_PV(i_prey), 'benthos_N_Food'//trim(index)//'_PV', '-', 'benthos N Food PV target number '//trim(index))
          call self%register_state_dependency(self%id_PFoodBent_PV(i_prey), 'benthos_P_Food'//trim(index)//'_PV', '-', 'benthos P Food PV target number '//trim(index))
          call self%register_state_dependency(self%id_CFoodBent_PV(i_prey), 'benthos_C_Food'//trim(index)//'_PV', '-', 'benthos C Food PV target number '//trim(index))
          call self%request_coupling_to_model(self%id_DFoodBent_PV(i_prey),self%id_BEN_prey(i_prey), 'sD'//trim(self%BENprey_suffix(i_prey))//'_PV')
          call self%request_coupling_to_model(self%id_PFoodBent_PV(i_prey),self%id_BEN_prey(i_prey), 'sP'//trim(self%BENprey_suffix(i_prey))//'_PV')
          call self%request_coupling_to_model(self%id_NFoodBent_PV(i_prey),self%id_BEN_prey(i_prey), 'sN'//trim(self%BENprey_suffix(i_prey))//'_PV')
          call self%request_coupling_to_model(self%id_CFoodBent_PV(i_prey),self%id_BEN_prey(i_prey), 'sC'//trim(self%BENprey_suffix(i_prey))//'_PV')
          call self%register_diagnostic_variable(self%id_tDConsFiBent_out(i_prey),  'tDConsFiBent_'//trim(index),         'gDW/m2/s', 'rate benthic D consumed'//trim(index),   output=output_instantaneous)
          call self%register_dependency(self%id_tDConsFiBent(i_prey),  'tDConsFiBent_'//trim(index),         'gDW m-2', 'tDConsFiBent'//trim(index))
          call self%register_diagnostic_variable(self%id_tNConsFiBent_out(i_prey),  'tNConsFiBent_'//trim(index),         'gDW/m2', 'rate benthic N consumed'//trim(index),     output=output_instantaneous)
          call self%register_dependency(self%id_tNConsFiBent(i_prey),  'tNConsFiBent_'//trim(index),         'gN m-2',  'tNConsFiBent'//trim(index))
          call self%register_diagnostic_variable(self%id_tPConsFiBent_out(i_prey),  'tPConsFiBent_'//trim(index),         'gDW/m2', 'rate benthic P consumed'//trim(index),     output=output_instantaneous)
          call self%register_dependency(self%id_tPConsFiBent(i_prey),  'tPConsFiBent_'//trim(index),         'gP m-2',  'tPConsFiBent'//trim(index))
          call self%register_diagnostic_variable(self%id_tCConsFiBent_out(i_prey),  'tCConsFiBent_'//trim(index),         'gC/m2',  'rate benthic C consumed'//trim(index),     output=output_instantaneous)
          call self%register_dependency(self%id_tCConsFiBent(i_prey),  'tCConsFiBent_'//trim(index),         'gC m-2',  'tCConsFiBent'//trim(index))
          call self%get_parameter(self%cClearBent(i_prey),'cClearBent'//trim(index),'m2/gDW/d','clearance rate for benthos prey '//trim(index),    default=0.06_rk,      scale_factor=1.0_rk/secs_pr_day)
          call self%get_parameter(self%fGutOccBent(i_prey),'fGutOccBent'//trim(index),'-',     'gut occupation factor for benthos prey '//trim(index),default=1.0_rk                                   )
          call self%get_parameter(self%BENprey_suffix(i_prey),'BENprey_suffix'//trim(index),'-',     'benthos prey name suffix'//trim(index),       default=''                                      )
      end do
   endif

   if (self%nPISCprey /= 0) then
      allocate(self%id_PISC_prey(self%nPISCprey))
      allocate(self%id_DFoodPisc(self%nPISCprey))
      allocate(self%id_NFoodPisc(self%nPISCprey))
      allocate(self%id_PFoodPisc(self%nPISCprey))
      allocate(self%id_CFoodPisc(self%nPISCprey))
      allocate(self%id_fVulPisc(self%nPISCprey))
      allocate(self%id_PredPisc(self%nPISCprey))
      allocate(self%id_tDConsFiPisc(self%nPISCprey))
      allocate(self%id_tPConsFiPisc(self%nPISCprey))
      allocate(self%id_tNConsFiPisc(self%nPISCprey))
      allocate(self%id_tCConsFiPisc(self%nPISCprey))
      allocate(self%id_pred_dummy_Pisc(self%nPISCprey))
      allocate (self%cClearPisc(self%nPISCprey))
      allocate (self%fGutOccPisc(self%nPISCprey))
      do i_prey=1,self%nPISCprey
          write(index,'(i0)') i_prey
          call self%register_model_dependency(self%id_PISC_prey(i_prey),'PISCprey'//trim(index))
          call self%register_state_dependency(self%id_DFoodPisc(i_prey), 'fish_D_Food'//trim(index), 'g/m3', 'fish D Food'//trim(index))
          call self%register_state_dependency(self%id_NFoodPisc(i_prey), 'fish_N_Food'//trim(index), 'g/m3', 'fish N Food'//trim(index))
          call self%register_state_dependency(self%id_PFoodPisc(i_prey), 'fish_P_Food'//trim(index), 'g/m3', 'fish P Food'//trim(index))
          call self%register_state_dependency(self%id_CFoodPisc(i_prey), 'fish_C_Food'//trim(index), 'g/m3', 'fish C Food'//trim(index))
          call self%request_coupling_to_model(self%id_DFoodPisc(i_prey),self%id_PISC_prey(i_prey),'sD')
          call self%request_coupling_to_model(self%id_PFoodPisc(i_prey),self%id_PISC_prey(i_prey),'sP')
          call self%request_coupling_to_model(self%id_NFoodPisc(i_prey),self%id_PISC_prey(i_prey),'sN')
          call self%request_coupling_to_model(self%id_CFoodPisc(i_prey),self%id_PISC_prey(i_prey),'sC')
          call self%register_state_dependency(self%id_fVulPisc(i_prey),'fVulPisc'//trim(index),'-','fraction of vulnerable prey '//trim(index)//' biomass')
          call self%request_coupling_to_model(self%id_fVulPisc(i_prey),self%id_PISC_prey(i_prey),'fVul')
          call self%register_state_dependency(self%id_pred_dummy_Pisc(i_prey),'pred_dummy'//trim(index),'DW/m3','total predation on prey'//trim(index))
          call self%request_coupling_to_model(self%id_pred_dummy_Pisc(i_prey),self%id_PISC_prey(i_prey),'pred_dummy')
          call self%get_parameter(self%cClearPisc(i_prey),'cClearPisc'//trim(index),'m3/gDW/d','clearance rate for fish prey '//trim(index),       default=0.021_rk,    scale_factor=1.0_rk/secs_pr_day)
          call self%get_parameter(self%fGutOccPisc(i_prey),'fGutOccPisc'//trim(index),'-',     'gut occupation factor for fish prey '//trim(index),default=1.0_rk                                      )
          if (self%diagnostics) then
              call self%register_diagnostic_variable(self%id_tDConsFiPisc(i_prey), 'tDConsFiPisc_'//trim(index),	'g/m3/s','rate fish D consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tPConsFiPisc(i_prey), 'tPConsFiPisc_'//trim(index),	'g/m3/s','rate fish P consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tNConsFiPisc(i_prey), 'tNConsFiPisc_'//trim(index),	'g/m3/s','rate fish N consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tCConsFiPisc(i_prey), 'tCConsFiPisc_'//trim(index),	'g/m3/s','rate fish C consumed '//trim(index),  output=output_instantaneous)
          endif 
      end do
   endif

   if (self%qStage == 1 .OR. self%qStage == 3) then
      call self%register_state_dependency(self%id_FiJu_D,'juvenile_D','g/m3', 'juvenile D state')
      call self%register_state_dependency(self%id_FiJu_P,'juvenile_P','g/m3', 'juvenile P state')
      call self%register_state_dependency(self%id_FiJu_N,'juvenile_N','g/m3', 'juvenile N state')
      call self%register_state_dependency(self%id_FiJu_C,'juvenile_C','g/m3', 'juvenile C state')
      call self%register_state_dependency(self%id_FiJu_Res,'juvenile_Res','g/m3', 'juvenile Res state')
      call self%register_state_dependency(self%id_FiJu_Siz,'juvenile_Siz','g/ind', 'juvenile ind. size')
   endif
   if (self%qStage == 2 .OR. self%qStage == 3) then
      call self%register_state_dependency(self%id_FiAd_D,'adult_D','g/m3', 'adult D state')
      call self%register_state_dependency(self%id_FiAd_P,'adult_P','g/m3', 'adult P state')
      call self%register_state_dependency(self%id_FiAd_N,'adult_N','g/m3', 'adult N state')
      call self%register_state_dependency(self%id_FiAd_C,'adult_C','g/m3', 'adult C state')
      call self%register_state_dependency(self%id_FiAd_Res,'adult_Res','g/m3', 'adult Res state')
      call self%register_state_dependency(self%id_FiAd_Siz,'adult_Siz','g/ind', 'adult ind. size')
   endif

   call self%register_diagnostic_variable(self%id_PStar, 'PStar',     'DW/m3',   'starvation threshold',         output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_predD, 'predD',     'gDW/m3/s','predation mortality',         output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_recrD, 'recrD',     'gDW/m3/s','recruitment',                 output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_aFeedLvlPisc, 'aFeedLvlPisc', '-',    'piscivorous feeding level',   output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_fFishPisc, 'fFishPisc',       '-',    'fraction of food from fish',  output=output_instantaneous)
   call self%register_diagnostic_variable(self%id_Day_last_save, 'Day_last_save', '-',   'Day of last save instant',    output=output_instantaneous)
   call self%register_dependency(self%id_Day_last, 'Day_last',  'd', 'previous day of year')

   if (self%predation) then
      allocate(self%id_PRED_D(self%nPRED))
      allocate(self%id_FiSt_D(self%nPRED))
      do i_pred=1,self%nPRED
         write(index,'(i0)') i_pred
         call self%register_model_dependency(self%id_PRED_D(i_pred),'PRED'//trim(index))
         call self%register_state_dependency(self%id_FiSt_D(i_pred), 'fish_stress_D'//trim(index), 'g/m3', 'fish stress D'//trim(index))
         call self%request_coupling_to_model(self%id_FiSt_D(i_pred),self%id_PRED_D(i_pred),'stress_D')
      end do
   endif

end subroutine initialize

subroutine do(self,_ARGUMENTS_DO_)
   class (type_wet_fish), intent(in)    :: self   
   _DECLARE_ARGUMENTS_DO_
   real(rk) :: sDFi

   _LOOP_BEGIN_
      _GET_(self%id_sDFi, sDFi)
   _LOOP_END_
end subroutine do

subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   class (type_wet_fish), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
end subroutine do_bottom

subroutine get_vertical_movement(self, _ARGUMENTS_VERTICAL_MOVEMENT_)
   class (type_wet_fish), intent(in) :: self
   _DECLARE_ARGUMENTS_VERTICAL_MOVEMENT_
   real(rk) :: uTm, sDFi, oxygen
   _LOOP_BEGIN_
      vertical_movement = 0.0_rk
   _LOOP_END_
end subroutine get_vertical_movement

subroutine check_state(self, _ARGUMENTS_CHECK_STATE_)
   class (type_wet_fish), intent(inout) :: self
   _DECLARE_ARGUMENTS_CHECK_STATE_
end subroutine check_state

subroutine calc_ODB(self,tDConsFiPot,aFeedLvl,incl,PreyD,uFunTmFish,cClear,fGutOcc,kDConsMax,aFunVegPrey)
   class (type_wet_fish), intent(in)        :: self
   real(rk), intent(inout), dimension(:) :: tDConsFiPot
   real(rk), intent(inout)                :: aFeedLvl
   integer,  intent(inout), dimension(:) :: incl
   real(rk), intent(in),  dimension(:)   :: PreyD
   real(rk), intent(in)                   :: uFunTmFish
   real(rk), intent(in),  dimension(:)   :: cClear
   real(rk), intent(in),  dimension(:)   :: fGutOcc
   real(rk), intent(in)                   :: kDConsMax
   real(rk), intent(in), optional         :: aFunVegPrey
end subroutine calc_ODB

end module wet_fish
