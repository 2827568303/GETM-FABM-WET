#include "fabm_driver.h"
!������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
!�� MODULE: FISH - THE STANDARD FISH MODULE WHERE FISH ARE PELAGIC VARIABLES, WITH OPTIONS FOR FORAGING ARENAS, VERTICAL MIGRATION                                                                   ��
!������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
module wet_fish
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use wet_utility, ONLY:uFunTmGaus
   use fabm_particle
   use fabm_expressions
   use fabm_builtin_models
   implicit none
   private

   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public :: type_wet_fish
      ! local state variable identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                                   :: id_sDFi, id_sPFi, id_sNFi, id_sCFi, id_sFRes, id_sDSiz, id_fVul
      ! diagnostic variables for modular fluxes--------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)                              :: id_BioTurb, id_PStar, id_predD, id_recrD, id_Day_last_save
      ! state dependencies identifiers-----------------------------------------------------------------------------------------------------------------------------------------------------------------
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
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)                              :: id_tDMigrFi, id_tNMigrFi, id_tPMigrFi, id_tCMigrFi, id_tDEgesFi, id_tNEgesFi, id_tPEgesFi, id_tCEgesFi, id_tDFiPOMW, id_tDFiDOMW 
      type (type_diagnostic_variable_id)                              :: id_tDMortFiBot, id_tNMortFiBot, id_tPMortFiBot, id_tCMortFiBot, id_tDRespFi, id_tCRespFi, id_tNExcrFi, id_tNFiNH4W, id_aFeedLvlPlan
      type (type_diagnostic_variable_id)                              :: id_tDConsFiPlanSum, id_tDConsFiBentSum, id_tDConsFiPiscSum, id_fFishPlan, id_fFishBent, id_tDAssFiTot, id_aFeedLvlBent
      type (type_diagnostic_variable_id)                              :: id_tNFiPOMW, id_tNFiDOMW, id_tPExcrFi, id_tPFiPO4W, id_tPFiPOMW, id_tPFiDOMW, id_tDMortFi, id_tNMortFi, id_tPMortFi, id_tCMortFi
      type (type_diagnostic_variable_id)                              :: id_tCFiPOMW, id_tCFiDOMW
      type (type_diagnostic_variable_id)                              :: id_tDAgeFish, id_tNAgeFish, id_tPAgeFish, id_tCAgeFish, id_aFeedLvlPisc, id_fFishPisc, id_tDReproPOM, id_tNReproPOM, id_tPReproPOM, id_tCReproPOM
      type (type_diagnostic_variable_id),   allocatable, dimension(:) :: id_tDConsFiPlan, id_tNConsFiPlan, id_tPConsFiPlan, id_tCConsFiPlan, id_tDConsFiPisc, id_tNConsFiPisc, id_tPConsFiPisc, id_tCConsFiPisc
      ! environmental dependencies---------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
      ! diagnostic dependencies------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_dependency_id)                                       :: id_aDSubVeg, id_aCovVeg, id_aTotFish
      ! parameters-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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

   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure :: initialize
   procedure :: do
   procedure :: do_bottom
   procedure :: get_vertical_movement
   procedure :: check_state
   procedure :: calc_ODB

   end type type_wet_fish

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk)           :: Pi=3.14159265358979_rk
   real(rk),parameter :: FishZero=0.00001_rk

contains

!������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
!�� SUBROUTINE: INITIALIZATION                                                                                                                                                                       ��
!������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_fish), intent(inout), target :: self
   integer,                     intent(in)          :: configunit

   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer  :: i_prey, i_pred, i_mac, i_stage
   character(len=64)   :: index

   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! boundary condition and variable constrain parameters----------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%kMigrFish,        'kMigrFish',     '1/d',      'fish migration rate',                                              default=0.001_rk,   scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%cDFiIn,           'cDFiIn',        'gDW/m3',   'external density',                                                 default=0.005_rk                                   )
   ! vertical movement parameters----------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%qTrans,           'qTrans',        '-',        'vert. trans. method: 0=no trans.; 1=passive; 2=O2; 3=O2 & Light',  default=2                                          )
   call self%get_parameter(self%cMinO2,           'cMinO2',        'gO2/m3',   'qtrans >= 2; oxygen conc. limit',                                  default=2.0_rk                                     )
   call self%get_parameter(self%cMinLight,        'cMinLight',     'W/m2',     'qTrans = 3; light level triggering upwards swimming',              default=1.0_rk                                     )
   call self%get_parameter(self%cMaxLight,        'cMaxLight',     'W/m2',     'qtrans = 3; light level triggering downwards swimming',            default=40.0_rk                                    )
   call self%get_parameter(self%cVswim,           'cVswim',        'm/d',      'qTrans > 1; vertical migration speed',                             default=10.0_rk,    scale_factor=1.0_rk/secs_pr_day)
   ! fish population-level parameters------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cDFiMin,          'cDFiMin',       'gDW/m3',   'minimum DW density',                                               default=0.0001_rk                                  )
   ! fish stage-structure parameters-------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
   ! prey parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
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
   call self%get_parameter(self%nPLANprey,        'nPLAN',         '-',        'number of plankton prey',                                          default=0                                          )
   allocate (self%cClearPlan(self%nPLANprey))
   allocate (self%fGutOccPlan(self%nPLANprey))
   allocate (self%PLANprey_suffix(self%nPLANprey)) 
   if (self%nPLANprey > 0) then                                                                                                               
      do i_prey = 1,self%nPLANprey                                                                                                         
         write(index,'(i0)') i_prey
         call self%get_parameter(self%cClearPlan(i_prey),'cClearPlan'//trim(index),'m3/gDW/d','clearance rate for plankton prey '//trim(index),   default=0.24_rk,     scale_factor=1.0_rk/secs_pr_day)
         call self%get_parameter(self%fGutOccPlan(i_prey),'fGutOccPlan'//trim(index),'-',     'gut occupation factor for plankton prey '//trim(index),default=1.0_rk                                  )
         call self%get_parameter(self%PLANprey_suffix(i_prey),'PLANprey_suffix'//trim(index),'-',     'plankton prey name suffix'//trim(index),       default=''                                      )
      end do
   endif
   call self%get_parameter(self%nBENprey,         'nBEN',          '-',        'number of benthos prey',                                          default=0                                           )
   allocate (self%cClearBent(self%nBENprey))
   allocate (self%fGutOccBent(self%nBENprey))
   allocate (self%BENprey_suffix(self%nBENprey))
   if (self%nBENprey > 0) then                                                                                                               
      call self%get_parameter(self%kTurbFish,     'kTurbFish',     'g/gDW/d',  'relative resuspension by fish bentivory',                         default=1.0_rk                                      )                                                                                                   
      do i_prey = 1,self%nBENprey
         write(index,'(i0)') i_prey
         call self%get_parameter(self%cClearBent(i_prey),'cClearBent'//trim(index),'m2/gDW/d','clearance rate for benthos prey '//trim(index),    default=0.06_rk,      scale_factor=1.0_rk/secs_pr_day)
         call self%get_parameter(self%fGutOccBent(i_prey),'fGutOccBent'//trim(index),'-',     'gut occupation factor for benthos prey '//trim(index),default=1.0_rk                                   )
         call self%get_parameter(self%BENprey_suffix(i_prey),'BENprey_suffix'//trim(index),'-',     'benthos prey name suffix'//trim(index),         default=''                                       )
      end do 
   endif
   call self%get_parameter(self%nPISCprey,        'nPISC',         '-',        'number of fish prey',                                             default=0                                           )
   allocate (self%cClearPisc(self%nPISCprey))
   allocate (self%fGutOccPisc(self%nPISCprey))
   if (self%nPISCprey > 0) then                                                                                                                                                                                                                 
      do i_prey = 1,self%nPISCprey                                                                                                               
         write(index,'(i0)') i_prey
         call self%get_parameter(self%cClearPisc(i_prey),'cClearPisc'//trim(index),'m3/gDW/d','clearance rate for fish prey '//trim(index),       default=0.021_rk,    scale_factor=1.0_rk/secs_pr_day)
         call self%get_parameter(self%fGutOccPisc(i_prey),'fGutOccPisc'//trim(index),'-',     'gut occupation factor for fish prey '//trim(index),default=1.0_rk                                      )
      end do
   endif                                                                                                                                             
   ! fish vital parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%kDConsMax,        'kDConsMax',     'gDW/gDW/d', 'standard dry weight specific maximum consumption rate',           default=0.25_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%fDAssFi,          'fDAssFi',       '-',         'C assimilation efficiency of fish',                               default=0.4_rk                                     )
   call self%get_parameter(self%kDRespFi,         'kDRespFi',      '1/d',       'maintenance respiration constant of fish at 20*C',                default=0.01_rk,    scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%fDRespActFi,      'fDRespActFi',   '-',         'additional feeding respiration as fraction of kDRespFi',          default=1.0_rk                                     )   
   call self%get_parameter(self%kMortFi,          'kMortFi',       '1/d',       'specific mortality of fish',                                      default=0.001_rk,   scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%cRelVegBent,      'cRelVegBent',   '-',         'decrease of fish feeding per macrophytes cover; max. 0.01',       default=0.009_rk                                   )
   call self%get_parameter(self%cRelVegPlan,      'cRelVegPlan',   '-',         'decrease of fish feeding per macrophytes cover; max. 0.01',       default=0.0_rk                                     )
   call self%get_parameter(self%lVegOpt,          'lVegOpt',       '-',         'switch for macrophyte dependence on fish max assimilation',       default=.false.                                    )
   call self%get_parameter(self%hDVegGrowth,      'hDVegGrowth',   'g/m2',      'lVegOpt = .true.; half-saturation macrophyte density for growth', default=0.015_rk                                   )
   ! stochiometric parameters--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%lNutMeth,         'lNutMeth',      '-',         'toggle fixed stochiometry',                                       default=.false.                                    )
   call self%get_parameter(self%fDBone,           'fDBone',        '-',         'fraction of fish C fixed in bones and scales',                    default=0.35_rk                                    )
   call self%get_parameter(self%fPBone,           'fPBone',        '-',         'fraction of fish P fixed in bones and scales',                    default=0.5_rk                                     )
   call self%get_parameter(self%fDissEgesFish,    'fDissEgesFish', '-',         'soluble inorg. nut. frac. of fish egested food',                  default=0.25_rk                                    )
   call self%get_parameter(self%fDissMortFish,    'fDissMortFish', '-',         'soluble inorg. nut. frac. of dead fish; excl. bones & scales',    default=0.1_rk                                     )
   call self%get_parameter(self%cPDRef,           'cPDRef',        'gP/gDW',    'reference P/DW ratio of fish',                                    default=0.022_rk                                   )
   call self%get_parameter(self%cNDRef,           'cNDRef',        'gN/gDW',    'reference N/DW ratio of fish',                                    default=0.1_rk                                     )
   call self%get_parameter(self%cCDRef,           'cCDRef',        'gC/gDW',    'reference C/DW ratio of fish',                                    default=0.45_rk                                    )
   call self%get_parameter(self%fFiDOMW,          'fFiDOMW',       '-',         'dissolved organic matter fraction from fish',                     default=0.5_rk                                     )
   ! fish temperature parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%cTmOptFish,       'cTmOptFish',    '*C',        'optimal temperature of fish',                                     default=25.0_rk                                    )
   call self%get_parameter(self%cSigTmFish,       'cSigTmFish',    '*C',        'temperature constant of fish; sigma in Gaussian curve',           default=10.0_rk                                    )
   ! diagnostic  parameter-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,      'diagnostics',   '-',         'toggle diagnostic output',                                        default=.false.                                    )
   
   !REGISTER MODEL VARIBLES, DEPENDENCIES & COUPLINGS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! fish state variables, transportation is turned off------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sDFi,  'sD',      'gDW/m3',  'DW',                                      initial_value= 0.5_rk,  minimum=self%cDFiMin,                   no_river_dilution=.TRUE.,  no_precipitation_dilution=.TRUE.)
   call self%register_state_variable(self%id_sPFi,  'sP',      'gP/m3',   'P',                                       initial_value= 0.011_rk,minimum=self%cDFiMin * self%cPDRef,     no_river_dilution=.TRUE.,  no_precipitation_dilution=.TRUE.)
   call self%register_state_variable(self%id_sNFi,  'sN',      'gN/m3',   'N',                                       initial_value= 0.05_rk, minimum=self%cDFiMin * self%cNDRef,     no_river_dilution=.TRUE.,  no_precipitation_dilution=.TRUE.)
   call self%register_state_variable(self%id_sCFi,  'sC',      'gN/m3',   'C',                                       initial_value= 0.05_rk, minimum=self%cDFiMin * self%cCDRef,     no_river_dilution=.TRUE.,  no_precipitation_dilution=.TRUE.)
   call self%register_state_variable(self%id_fVul,  'fVul',    '-',       'biomass fraction vulnerable to predation',initial_value= 1.0_rk,  minimum=0.0_rk,                         no_river_dilution=.TRUE.,  no_precipitation_dilution=.TRUE.)
   if (self%qStage > 0) then
	   call self%register_state_variable(self%id_sFRes, 'sFRes',   'gDW/m3',  'reserve fraction of biomass',         initial_value= 0.0_rk,  minimum=0.0_rk,                         no_river_dilution=.TRUE.,  no_precipitation_dilution=.TRUE.)
       call self%register_state_variable(self%id_sDSiz, 'sDSiz',   'gDW/ind', 'average individual fish size',        initial_value= 0.0_rk,  minimum=0.0_rk,                         no_river_dilution=.TRUE.,  no_precipitation_dilution=.TRUE.)
   endif
   call self%set_variable_property(self%id_fVul,   'disable_transport',   .true.)
   if (self%qTrans == 0) then
       if (self%qStage > 0) then
	       call self%set_variable_property(self%id_sDSiz,  'disable_transport',   .true.)
		   call self%set_variable_property(self%id_sFRes,  'disable_transport',   .true.)
	   endif
       call self%set_variable_property(self%id_sDFi,   'disable_transport',   .true.)   
       call self%set_variable_property(self%id_sNFi,   'disable_transport',   .true.)
       call self%set_variable_property(self%id_sPFi,   'disable_transport',   .true.)
   endif
   
   call self%register_dependency(self%id_pred_sms,  'pred_sms',   '-',  'predation rate')
   call self%register_diagnostic_variable(self%id_predD,       'pred_dummy',   '-',   'predation dummy', output=output_none, act_as_state_variable=.true., source=source_none)
   call self%request_coupling(self%id_pred_sms,'./pred_dummy_sms_tot')

   ! Register contribution of state to global aggregate variables------------------------------------------------------------------------------------------------------------------------------------
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='wet_fish_totD', units='g/m3', aggregate_variable=.true.),      self%id_sDFi)
   ! register state variables dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_dependency(self%id_DPOMpoolW,    'POM_DW_pool_water',     'g/m3',     'POM DW pool in water'                                                                              )
   call self%register_state_dependency(self%id_NPOMpoolW,    'POM_N_pool_water',      'g/m3',     'POM N pool in water'                                                                               )
   call self%register_state_dependency(self%id_PPOMpoolW,    'POM_P_pool_water',      'g/m3',     'POM P pool in water'                                                                               )
   call self%register_state_dependency(self%id_CPOMpoolW,    'POM_C_pool_water',      'g/m3',     'POM C pool in water'                                                                               )
   call self%register_state_dependency(self%id_NH4poolW,     'NH4_pool_water',        'g/m3',     'NH4 pool in water'                                                                                 )
   call self%register_state_dependency(self%id_PO4poolW,     'PO4_pool_water',        'g/m3',     'PO4 pool in water'                                                                                 )
   call self%register_state_dependency(self%id_DDOMpoolW,    'DOM_DW_pool_water',     'g/m3',     'DOM DW in water'                                                                                   )
   call self%register_state_dependency(self%id_NDOMpoolW,    'DOM_N_pool_water',      'g/m3',     'DOM N in water'                                                                                    )
   call self%register_state_dependency(self%id_PDOMpoolW,    'DOM_P_pool_water',      'g/m3',     'DOM P in water'                                                                                    )
   call self%register_state_dependency(self%id_CDOMpoolW,    'DOM_C_pool_water',      'g/m3',     'DOM C in water'                                                                                    )
   ! call self%register_state_dependency(self%id_CO2poolW,    'CO2_pool_water',      'g/m3',     'CO2 in water'                                                                                    )
   ! setup couplings to plankton prey variables--------------------------------------------------------------------------------------------------------------------------------------------------------
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
      ! allocate(self%id_VFoodPlan(self%nPLANprey))
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
          if (self%diagnostics) then
              call self%register_diagnostic_variable(self%id_tDConsFiPlan(i_prey), 'tDConsFiPlan_'//trim(index),	'g/m3/s','rate plankton D consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tPConsFiPlan(i_prey), 'tPConsFiPlan_'//trim(index),	'g/m3/s','rate plankton P consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tNConsFiPlan(i_prey), 'tNConsFiPlan_'//trim(index),	'g/m3/s','rate plankton N consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tCConsFiPlan(i_prey), 'tCConsFiPlan_'//trim(index),	'g/m3/s','rate plankton C consumed '//trim(index),  output=output_instantaneous)
          endif 
      end do
   endif
   ! setup couplings to benthos prey variables------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_BioTurb,       'Bioturbation',   'gDW/m3/d',   'Bioturbation')
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_bioturbation',units='gDW/m3/d',aggregate_variable=.true.),self%id_BioTurb,scale_factor=1._rk)   

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
          
          call self%register_diagnostic_variable(self%id_tDConsFiBent_out(i_prey),  'tDConsFiBent_'//trim(index),         'gDW/m2/s', 'rate benthic D consumed'//trim(index),   output=output_instantaneous)!, act_as_state_variable=.true.                 )
          call self%register_dependency(self%id_tDConsFiBent(i_prey),  'tDConsFiBent_'//trim(index),         'gDW m-2', 'tDConsFiBent'//trim(index))
          call self%register_diagnostic_variable(self%id_tNConsFiBent_out(i_prey),  'tNConsFiBent_'//trim(index),         'gDW/m2', 'rate benthic N consumed'//trim(index),     output=output_instantaneous)!, act_as_state_variable=.true.                   )
          call self%register_dependency(self%id_tNConsFiBent(i_prey),  'tNConsFiBent_'//trim(index),         'gN m-2',  'tNConsFiBent'//trim(index))
          call self%register_diagnostic_variable(self%id_tPConsFiBent_out(i_prey),  'tPConsFiBent_'//trim(index),         'gDW/m2', 'rate benthic P consumed'//trim(index),     output=output_instantaneous)!, act_as_state_variable=.true.                   )
          call self%register_dependency(self%id_tPConsFiBent(i_prey),  'tPConsFiBent_'//trim(index),         'gP m-2',  'tPConsFiBent'//trim(index))
          call self%register_diagnostic_variable(self%id_tCConsFiBent_out(i_prey),  'tCConsFiBent_'//trim(index),         'gC/m2',  'rate benthic C consumed'//trim(index),     output=output_instantaneous)!, act_as_state_variable=.true.                   )
          call self%register_dependency(self%id_tCConsFiBent(i_prey),  'tCConsFiBent_'//trim(index),         'gC m-2',  'tCConsFiBent'//trim(index))
      end do
   endif
   ! setup couplings to fish prey variables------------------------------------------------------------------------------------------------------------------------------------------------------------
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
          if (self%diagnostics) then
              call self%register_diagnostic_variable(self%id_tDConsFiPisc(i_prey), 'tDConsFiPisc_'//trim(index),	'g/m3/s','rate fish D consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tPConsFiPisc(i_prey), 'tPConsFiPisc_'//trim(index),	'g/m3/s','rate fish P consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tNConsFiPisc(i_prey), 'tNConsFiPisc_'//trim(index),	'g/m3/s','rate fish N consumed '//trim(index),  output=output_instantaneous)
              call self%register_diagnostic_variable(self%id_tCConsFiPisc(i_prey), 'tCConsFiPisc_'//trim(index),	'g/m3/s','rate fish C consumed '//trim(index),  output=output_instantaneous)
          endif 
      end do
   
   endif
   ! if stage-structure is on-------------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%qStage == 1 .OR. self%qStage == 3) then
      call self%register_state_dependency(self%id_FiJu_D,'juvenile_D','g/m3', 'juvenile D state')
      call self%register_state_dependency(self%id_FiJu_P,'juvenile_P','g/m3', 'juvenile P state')
      call self%register_state_dependency(self%id_FiJu_N,'juvenile_N','g/m3', 'juvenile N state')
      call self%register_state_dependency(self%id_FiJu_C,'juvenile_C','g/m3', 'juvenile C state')
      call self%register_state_dependency(self%id_FiJu_Res,'juvenile_Res','g/m3', 'juvenile Res state')
      call self%register_state_dependency(self%id_FiJu_Siz,'juvenile_Siz','g/ind', 'juvenile ind. size')
      
      !call self%register_model_dependency(self%id_FiJu_target,'juvenile_target')                             !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiJu_D,self%id_FiJu_target,'sD')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiJu_P,self%id_FiJu_target,'sP')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiJu_N,self%id_FiJu_target,'sN')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiJu_Res,self%id_FiJu_target,'sFRes')
      !call self%request_coupling_to_model(self%id_FiJu_Siz,self%id_FiJu_target,'sDSiz')
   endif
   if (self%qStage == 2 .OR. self%qStage == 3) then
      call self%register_state_dependency(self%id_FiAd_D,'adult_D','g/m3', 'adult D state')
      call self%register_state_dependency(self%id_FiAd_P,'adult_P','g/m3', 'adult P state')
      call self%register_state_dependency(self%id_FiAd_N,'adult_N','g/m3', 'adult N state')
      call self%register_state_dependency(self%id_FiAd_C,'adult_C','g/m3', 'adult C state')
      call self%register_state_dependency(self%id_FiAd_Res,'adult_Res','g/m3', 'adult Res state')
      call self%register_state_dependency(self%id_FiAd_Siz,'adult_Siz','g/ind','adult ind. size')
      
      !call self%register_model_dependency(self%id_FiAd_target,'adult_target')                                !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiAd_D,self%id_FiAd_target,'sD')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiAd_P,self%id_FiAd_target,'sP')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiAd_N,self%id_FiAd_target,'sN')                         !!! Currently, automatic coupling results in a circular dependency error message. Manual coupling works
      !call self%request_coupling_to_model(self%id_FiAd_Res,self%id_FiAd_target,'sFRes')
      !call self%request_coupling_to_model(self%id_FiAd_Siz,self%id_FiAd_target,'sDSiz')
   endif
   ! Register diagnostic process output----------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%diagnostics) then   
       call self%register_diagnostic_variable(self%id_tDMigrFi,           'tDMigrFi',             'g/m3/s',         'rate DW migration',                      output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNMigrFi,           'tNMigrFi',             'g/m3/s',         'rate N migration',                       output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPMigrFi,           'tPMigrFi',             'g/m3/s',         'rate P migration',                       output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tCMigrFi,           'tCMigrFi',             'g/m3/s',         'rate C migration',                       output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDEgesFi,           'tDEgesFi',             'g/m3/s',         'rate DW egested',                        output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNEgesFi,           'tNEgesFi',             'g/m3/s',         'rate N egested',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPEgesFi,           'tPEgesFi',             'g/m3/s',         'rate P egested',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tCEgesFi,           'tCEgesFi',             'g/m3/s',         'rate C egested',                         output=output_instantaneous)      
       call self%register_diagnostic_variable(self%id_tDMortFi,           'tDMortFi',             'g/m3/s',         'rate DW from mortality',                 output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNMortFi,           'tNMortFi',             'g/m3/s',         'rate N from mortality',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPMortFi,           'tPMortFi',             'g/m3/s',         'rate P from mortality',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tCMortFi,           'tCMortFi',             'g/m3/s',         'rate C from mortality',                  output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDRespFi,           'tDRespFi',             'g/m3/s',         'rate DW respired',                       output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tCRespFi,           'tCRespFi',             'g/m3/s',         'rate C respired',                        output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDAssFiTot,         'tDAssFiTot',           'g/m3/s',         'rate DW assimilated',                    output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDFiPOMW,           'tDFiPOMW',             'g/m3/s',         'rate DPOMW egested',                     output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDFiDOMW,           'tDFiDOMW',             'g/m3/s',         'rate DDOMW egested',                     output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDMortFiBot,        'tDMortFiBot',          'g/m3/s',         'rate DW bone lost from system',          output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNMortFiBot,        'tNMortFiBot',          'g/m3/s',         'rate N bone lost from system',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPMortFiBot,        'tPMortFiBot',          'g/m3/s',         'rate P bone lost from system',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tCMortFiBot,        'tCMortFiBot',          'g/m3/s',         'rate C bone lost from system',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNExcrFi,           'tNExcrFi',             'g/m3/s',         'rate NH4 excreted',                      output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNFiNH4W,           'tNFiNH4W',             'g/m3/s',         'rate NH4 out',                           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNFiPOMW,           'tNFiPOMW',             'g/m3/s',         'rate NPOMW out',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNFiDOMW,           'tNFiDOMW',             'g/m3/s',         'rate NDOMW out',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPExcrFi,           'tPExcrFi',             'g/m3/s',         'rate PO4 excreted',                      output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPFiPO4W,           'tPFiPO4W',             'g/m3/s',         'rate PO4 out',                           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPFiPOMW,           'tPFiPOMW',             'g/m3/s',         'rate PPOMW out',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPFiDOMW,           'tPFiDOMW',             'g/m3/s',         'rate PDOMW out',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tCFiPOMW,           'tCFiPOMW',             'g/m3/s',         'rate CPOMW out',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tCFiDOMW,           'tCFiDOMW',             'g/m3/s',         'rate CDOMW out',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDAgeFish,          'tDAgeFish',            'g/m3/s',         'rate DW ageing',                         output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNAgeFish,          'tNAgeFish',            'g/m3/s',         'rate N ageing',                          output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPAgeFish,          'tPAgeFish',            'g/m3/s',         'rate P ageing',                          output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tCAgeFish,          'tCAgeFish',            'g/m3/s',         'rate C ageing',                          output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDConsFiPlanSum,    'tDConsFiPlanSum',      'g/m3/s',         'rate total plankton consumed',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDConsFiBentSum,    'tDConsFiBentSum',      'g/m3/s',         'rate total benthos consumed',            output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDConsFiPiscSum,    'tDConsFiPiscSum',      'g/m3/s',         'rate total fish consumed',               output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_aFeedLvlPlan,       'aFeedLvlPlan',         '-',              'feeding level planktivore',              output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_aFeedLvlBent,       'aFeedLvlBent',         '-',              'feeding level benthivore',               output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_aFeedLvlPisc,       'aFeedLvlPisc',         '-',              'feeding level piscivore',                output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_fFishPlan,          'fFishPlan',            '-',              'time fraction on planktivory',           output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_fFishBent,          'fFishBent',            '-',              'time fraction on benthivory',            output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_fFishPisc,          'fFishPisc',            '-',              'time fraction on piscivory',             output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tDReproPOM,         'tDReproPOM',           'gDW/m3',         'absolute reproduction flux to DPOMW',    output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tNReproPOM,         'tNReproPOM',           'gN/m3',          'absolute reproduction flux to NPOMW',    output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tPReproPOM,         'tPReproPOM',           'gP/m3',          'absolute reproduction flux to PPOMW',    output=output_instantaneous)
       call self%register_diagnostic_variable(self%id_tCReproPOM,         'tCReproPOM',           'gC/m3',          'absolute reproduction flux to CPOMW',    output=output_instantaneous)
   endif
   ! setup couplings to predators----------------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%qOPT .eq. 0) then
       call self%register_diagnostic_variable(     self%id_PStar,          'PStar',       '-',          'extent of risk-reducing behaviors employed',output=output_none, missing_value=0.0_rk          )
   else
       call self%register_diagnostic_variable(     self%id_PStar,          'PStar',       '-',          'extent of risk-reducing behaviors employed',output=output_instantaneous, missing_value=0.0_rk )
   endif
   !  register environmental dependencies--------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_Day_last_save,  'Day_last',         'd', 'last time step day',   output=output_none)!, act_as_state_variable=.true.                 )
   call self%register_dependency(self%id_Day_last,  'Day_last',         'd', 'last time step day')
   
   call self%register_dependency(self%id_uTm,    standard_variables%temperature)
   call self%register_dependency(self%id_Day,    standard_variables%number_of_days_since_start_of_the_year)
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')
   call self%register_dependency(self%id_oxygen, 'oxygen_pool_water', 'g/m3', 'Oxygen pool water')
   call self%register_dependency(self%id_par, standard_variables%downwelling_photosynthetic_radiative_flux)
   call self%register_dependency(self%id_aCovVeg,type_bulk_standard_variable(name='total_aCovVeg',units='%'))
   call self%register_dependency(self%id_aDSubVeg,type_bulk_standard_variable(name='total_aDSubVeg',units='gDW/m2'))
   call self%register_dependency(self%id_aTotFish,type_bulk_standard_variable(name='wet_fish_totD', units='g/m3'))
   
   return

end subroutine initialize

!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
!�� SUBROUTINE: DO (PELAGIC)                                                                                                                                                                       ��
!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
subroutine do(self,_ARGUMENTS_DO_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_fish), intent(in)    :: self   
   _DECLARE_ARGUMENTS_DO_

   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk), dimension(self%nPLANprey)   :: sDPlan, sNPlan, sPPlan, rPDPlan, rNDPlan, tDConsFiPlan, tPConsFiPlan, tNConsFiPlan, afNAssFiPlan, tNAssFiPlan, afPAssFiPlan, tPAssFiPlan, tDConsFiPlanPot, relConsPlan
   real(rk), dimension(self%nPLANprey)   :: sCPlan, rCDPlan, tCConsFiPlan, afCAssFiPlan, tCAssFiPlan
   real(rk), dimension(self%nBENprey)    :: sDBent, sNBent, sPBent, rPDBent, rNDBent, tDConsFiBent, tPConsFiBent, tNConsFiBent, afNAssFiBent, tNAssFiBent, afPAssFiBent, tPAssFiBent, tDConsFiBentPot, relConsBent
   real(rk), dimension(self%nBENprey)    :: sCBent, rCDBent, tCConsFiBent, afCAssFiBent, tCAssFiBent
   real(rk), dimension(self%nPISCprey)   :: sDPisc, sNPisc, sPPisc, rPDPisc, rNDPisc, tDConsFiPisc, tPConsFiPisc, tNConsFiPisc, afNAssFiPisc, tNAssFiPisc, afPAssFiPisc, tPAssFiPisc, tDConsFiPiscPot, relConsPisc
   real(rk), dimension(self%nPISCprey)   :: fVulPisc, vPiscPred, vPiscPredPot, sCPisc, rCDPisc, tCConsFiPisc, afCAssFiPisc, tCAssFiPisc
   real(rk), dimension(self%nPRED)       :: sDPRED
   real(rk)                              :: uTm, Day, sDFi, sPFi, sNFi, fFeed, aDSubVeg, rPDFi, rNDFi, uFunTmFish, tDAgeFish, tPAgeFish, tNAgeFish, tDFi
   real(rk)                              :: sCFi, rCDFi, tCConsFiTot, tCMortFi, tCEgesFi, tCAssFiTot, tCRespFi, tCAgeFish, tCFiCO2W, tCMortFiBot, tCMortFiTOM, tCFiTOMW, tCFiPOMW, tCFiDOMW, tCFi, tCMigrFi
   real(rk)                              :: tDMigrFi, tDRespFi, tDMortFi, aDSatFiTot, tDEnvFi, ukDIncrFi, tPFi, tPMigrFi, tPExcrFi, tNFi, tNMigrFi, tNExcrFi, tNMortFi, sDFiSt, tNEgesFi, tNMortFiNH4
   real(rk)                              :: tNMortFiBot, tNEgesFiNH4, tNFiNH4W, tNEgesFiTOM, tNMortFiTOM, tVFi, v_in, sDFiJu, sVFiJu, sDFiAd, sVFiAd, tPEgesFiPO4, tPFiPO4W, tDEgesFi, tDMortFiTOM
   real(rk)                              :: tDMortFiBot, tDFiTOMW, tNFiTOMW, tPFiTOMW, tDAssFiTot, tDFiPOMW, tNFiPOMW, tPFiPOMW, tPAssFiTot, tPEgesFi, tPMortFi, tPMortFiBot, tDFiDOMW, tNFiDOMW
   real(rk)                              :: tPFiDOMW, tNAssFiTot, aCovVeg, aFunVegBent, aFunVegPlan, aFunVegAss, aFeedLvlPlan, aFeedLvlBent, aFeedLvlPisc, aFeedLvlPisc_, tPMortFiPO4, tPEgesFiTOM
   real(rk)                              :: fFishPlan, fFishBent, fFishPisc, fFishPisc_, tDAssFiPlan, tDAssFiBent, tDAssFiPisc, tDConsFiTot, tPConsFiTot, tNConsFiTot
   real(rk)                              :: BioTurb, tPMortFiTOM, PStar, PStar_last, vPred, vPredS, Pred_last, Pred_now, Pred_save, timer_last, timer_now, TS, dz, R_scaled, v, Metab, Vol
   real(rk)                              :: tDAssFiTotPot, tDAssFiPlanPot, tDAssFiBentPot, tDAssFiPiscPot, NetGrowthFA, fPiscArena, fPiscRefuge, fRes_now
   real(rk)                              :: tDConsFiPlanTotPot, tDConsFiBentTotPot, tDConsFiPiscTotPot, FMaxCurr, fGot, R, M, FMax, fAgeFish, tDAgeRes, fIrreversible
   real(rk)                              :: tDConsFiPlanSum, tDConsFiBentSum, tDConsFiPiscSum, aTotFish, Day_last, Day_save, fFC, vPred_old, sFRes, tFRes, fVul, sDFiEff, fMat, q, FiAd_Res, FiAd_D, pred_sms
   real(rk)                              :: PStar_now, tfVul, tDSiz, rG, eAge, sDSiz, FiAd_Siz, tDAgeSiz, FiJu_Siz, kDConsMax, k_mat
   integer                               :: i_prey, i_pred, i
   LOGICAL                               :: lCon
   integer, dimension(self%nPLANprey)    :: inclPlan
   integer, dimension(self%nBENprey)     :: inclBent
   integer, dimension(self%nPISCprey)    :: inclPisc

   _LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
        ! 1.1 retrieve environmental dependencies                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        _GET_(self%id_uTm,uTm)                                                                                      ! get local temperature
        _GET_(self%id_aDSubVeg,aDSubVeg)                                                                            ! get macrophyte biomass
        _GET_(self%id_aCovVeg,aCovVeg)                                                                              ! get macrophyte cover percentage
        aCovVeg = min(1.0_rk,aCovVeg)                                                                               !
        !===========================================================================================================!
        ! 1.2 retrieve state variables, & calc. current local nutrient ratios and relative abundances               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.1 fish state variables                                                                             !
           !--------------------------------------------------------------------------------------------------------!
           _GET_GLOBAL_(self%id_Day,Day)                                                                            ! get the simulation day
           _GET_(self%id_sDFi,sDFi)                                                                                 ! get fish dry weight
           _GET_(self%id_sPFi,sPFi)                                                                                 ! get fish P mass
           _GET_(self%id_sNFi,sNFi)                                                                                 ! get fish N mass
           _GET_(self%id_sCFi,sCFi)                                                                                 ! get fish N mass
           if (.NOT. self%lNutMeth) then                                                                            ! case dynamic stochiometry
               rPDFi = sPFi /(sDFi+NearZero)                                                                        !   calculate P:DW ratio
               rNDFi = sNFi /(sDFi+NearZero)                                                                        !   calculate N:DW ratio
               rCDFi = sCFi /(sDFi+NearZero)                                                                        !   calculate N:DW ratio
           else                                                                                                     ! case fixed stochiometry
               rPDFi = self%cPDRef                                                                                  !   P ratio parameter
               rNDFi = self%cNDRef                                                                                  !   N ratio parameter
               rCDFi = self%cCDRef                                                                                  !   N ratio parameter
           endif                                                                                                    !
           if (self%qStage > 0) then                                                                                ! case stage structure
               _GET_(self%id_sFRes,sFRes)                                                                           !   get current reserve biomass
               sDFiEff = sDFi - sFRes*sDFi + sDFi*(self%fResMax-self%fGonad)                                        !   calculate effective biomass of fish (ignoring condition)
               lCon = sFRes > self%fResMin*1.75_rk                                                                  !   check state of reserves
           else                                                                                                     !
               lCon = .False.                                                                                       !
               sDFiEff = sDFi                                                                                       !
           endif                                                                                                    !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.2 plankton prey                                                                                    !
           !--------------------------------------------------------------------------------------------------------!
           if (self%nPLANprey /= 0) then                                                                            ! case planktivory 
              do i_prey=1,self%nPLANprey                                                                            !   for each prey
                 _GET_(self%id_DFoodPlan(i_prey),sDPlan(i_prey))                                                    !     get plankton dry weight (dimensions: nPLANprey)
                 _GET_(self%id_NFoodPlan(i_prey),sNPlan(i_prey))                                                    !     get plankton P weight (dimensions: nPLANprey)
                 _GET_(self%id_PFoodPlan(i_prey),sPPlan(i_prey))                                                    !     get plankton N weight (dimensions: nPLANprey)
                 _GET_(self%id_CFoodPlan(i_prey),sCPlan(i_prey))                                                    !     get plankton C weight (dimensions: nPLANprey)
              end do                                                                                                !
              rPDPlan = sPPlan / (sDPlan + NearZero)                                                                !   calculate P:DW ratio
              rNDPlan = sNPlan / (sDPlan + NearZero)                                                                !   calculate N:DW ratio
              rCDPlan = sCPlan / (sDPlan + NearZero)                                                                !   calculate C:DW ratio
           else                                                                                                     ! case no planktivory: values set to zero
               sDPlan = 0.0_rk                                                                                      !
               sNPlan = 0.0_rk                                                                                      !
               sPPlan = 0.0_rk                                                                                      !
               sCPlan = 0.0_rk                                                                                      !
               rPDPlan = 1.0_rk                                                                                     !
               rNDPlan = 1.0_rk                                                                                     !
               rCDPlan = 1.0_rk                                                                                     !
           endif                                                                                                    !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.3 benthos prey                                                                                     !
           !--------------------------------------------------------------------------------------------------------!
           if (self%nBENprey /= 0) then                                                                             ! case bentivory
              do i_prey=1,self%nBENprey                                                                             !   for each prey
                 _GET_(self%id_DFoodBent_PV(i_prey),sDBent(i_prey))                                                 !     get bent. dry weight (dimensions: nBENprey)
                 _GET_(self%id_NFoodBent_PV(i_prey),sNBent(i_prey))                                                 !     get bent. N weight (dimensions: nBENprey)
                 _GET_(self%id_PFoodBent_PV(i_prey),sPBent(i_prey))                                                 !     get bent. P weight (dimensions: nBENprey)
                 _GET_(self%id_CFoodBent_PV(i_prey),sCBent(i_prey))                                                 !     get bent. C weight (dimensions: nBENprey)
              end do                                                                                                !
              rPDBent = sPBent/(sDBent+NearZero)                                                                    !   calculate P:DW ratio
              rNDBent = sNBent/(sDBent+NearZero)                                                                    !   calculate N:DW ratio
              rCDBent = sCBent/(sDBent+NearZero)                                                                    !   calculate C:DW ratio
           else                                                                                                     ! case no bentivory: values set to zero
              sDBent = 0.0_rk                                                                                       !
              sNBent = 0.0_rk                                                                                       !
              sPBent = 0.0_rk                                                                                       !
              sCBent = 0.0_rk                                                                                       !
              rPDBent = 1.0_rk                                                                                      !
              rNDBent = 1.0_rk                                                                                      !
              rCDBent = 1.0_rk                                                                                      !
           endif                                                                                                    !
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 1.2.4 fish prey                                                                                        !
           !--------------------------------------------------------------------------------------------------------!
           if (self%nPISCprey /= 0) then                                                                            ! case piscivory
              do i_prey=1,self%nPISCprey                                                                            !   for each prey
                 _GET_(self%id_DFoodPisc(i_prey),sDPisc(i_prey))                                                    !     get pisc. dry weight (dimensions: nPISCprey)
                 _GET_(self%id_NFoodPisc(i_prey),sNPisc(i_prey))                                                    !     get pisc. P weight (dimensions: nPISCprey)
                 _GET_(self%id_PFoodPisc(i_prey),sPPisc(i_prey))                                                    !     get pisc. N weight (dimensions: nPISCprey)
                 _GET_(self%id_CFoodPisc(i_prey),sCPisc(i_prey))                                                    !     get pisc. C weight (dimensions: nPISCprey)
                 _GET_(self%id_fVulPisc(i_prey),fVulPisc(i_prey))                                                   !
              end do                                                                                                !
              sDPisc=sDPisc*fVulPisc                                                                                !
              sNPisc=sNPisc*fVulPisc                                                                                !
              sPPisc=sPPisc*fVulPisc                                                                                !
              sCPisc=sCPisc*fVulPisc                                                                                !
              rPDPisc = sPPisc/(max(sDPisc,NearZero))                                                               !   calculate P:DW ratio
              rNDPisc = sNPisc/(max(sDPisc,NearZero))                                                               !   calculate N:DW ratio
              rCDPisc = sCPisc/(max(sDPisc,NearZero))                                                               !   calculate C:DW ratio
           else                                                                                                     ! case no piscivory: values set to zero
               sDPisc = 0.0_rk                                                                                      !
               sNPisc = 0.0_rk                                                                                      !
               sPPisc = 0.0_rk                                                                                      !
               sCPisc = 0.0_rk                                                                                      !
               rPDPisc = 1.0_rk                                                                                     !
               rNDPisc = 1.0_rk                                                                                     !
               rCDPisc = 1.0_rk                                                                                     !
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
        aFunVegPlan = max(0.0_rk,1.0_rk - self%cRelVegPlan * aCovVeg)                                               ! calcuate dependence of planktivory on macrophytes
        if (self%lVegOpt) then                                                                                      ! case growth rate is macrophyte-dependent
            aFunVegAss = aDSubVeg /(self%hDVegGrowth + aDSubVeg + NearZero)                                         !   calculate macrophyte-dependence of growth
        else                                                                                                        !
            aFunVegAss = 1.0_rk                                                                                     !   otherwise no effect
        endif                                                                                                       !
        !===========================================================================================================!                                                          
        ! 2.2 pre-calculate total food consumption from plankton, benthos, and piscivory, assuming maximum feeding  !                                                          
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        if (self%qStage == 1) then                                                                                  ! if at the end of a size structure chain
            _GET_(self%id_sDSiz,sDSiz)                                                                              !   get average size
            kDConsMax = min(self%kDConsMax,max(NearZero,self%kDConsMax*(1._rk-(sDSiz-self%cDinit)/(self%cDfin-self%cDinit)))) !   limit max consumption as average size approaches max size
        else                                                                                                        !
            kDConsMax = self%kDConsMax                                                                              !
        endif                                                                                                       !
        if (self%qODB == 0) then                                                                                    ! if optimal diet breadth is turned off
            aFeedLvlPlan = aFunVegPlan*sum(self%cClearPlan*self%fGutOccPlan*sDPlan)/ &                              !   calculate feeding level, based on all available plankton prey
                (aFunVegPlan*sum(self%cClearPlan*self%fGutOccPlan*sDPlan) + uFunTmFish*kDConsMax)                   !
            aFeedLvlBent = aFunVegBent*sum(self%cClearBent*self%fGutOccBent*sDBent)/ &                              !   calculate feeding level, based on all available plankton prey
                (aFunVegBent*sum(self%cClearBent*self%fGutOccBent*sDBent) + uFunTmFish*kDConsMax)                   !
            aFeedLvlPisc = sum(self%cClearPisc*self%fGutOccPisc*sDPisc)/ &                                          !   calculate feeding level, based on all available fish prey
                (sum(self%cClearPisc*self%fGutOccPisc*sDPisc) + uFunTmFish*kDConsMax)                               !
            tDConsFiPlanPot = aFunVegPlan*(self%cClearPlan*sDPlan)*(1._rk-aFeedLvlPlan)                             !   calculate potential consumption of all available plankton prey
            tDConsFiBentPot = aFunVegBent*(self%cClearBent*sDBent)*(1._rk-aFeedLvlBent)                             !   calculate potential consumption of all available plankton prey
            tDConsFiPiscPot = (self%cClearPisc*sDPisc)*(1._rk-aFeedLvlPisc)                                         !   calculate potential consumption of all available fish. prey
            inclPlan = 1                                                                                            !   include all prey types
            inclBent = 1                                                                                            !   include all prey types
            inclPisc = 1                                                                                            !   include all prey types
        elseif (self%qODB == 1) then                                                                                ! elseif optimal diet breadth is turned on
            call self%calc_ODB(tDConsFiPlanPot,aFeedLvlPlan,inclPlan,sDPlan,uFunTmFish,self%cClearPlan, &           !    calculate ODB for planktivory
                self%fGutOccPlan,kDConsMax,aFunVegPrey=aFunVegPlan)                                                 !
            call self%calc_ODB(tDConsFiBentPot,aFeedLvlBent,inclBent,sDBent,uFunTmFish,self%cClearBent, &           !    calculate ODB for bentivory
                self%fGutOccBent,kDConsMax,aFunVegPrey=aFunVegBent)                                                 !
            call self%calc_ODB(tDConsFiPiscPot,aFeedLvlPisc,inclPisc,sDPisc,uFunTmFish,self%cClearPisc, &           !    calculate ODB for piscivory
                self%fGutOccPisc,kDConsMax)                                                                         !
        endif                                                                                                       !
        relConsPlan = tDConsFiPlanPot/sum(tDConsFiPlanPot)                                                          ! Calculate weighted average of consumption in order to estimate relative contributions of prey towards fGutOcc and R_scaled
        relConsBent = tDConsFiBentPot/sum(tDConsFiBentPot)                                                          !
        relConsPisc = tDConsFiPiscPot/sum(tDConsFiPiscPot)                                                          !
                                                                                                                    !
        tDConsFiPlanTotPot = sum(tDConsFiPlanPot)                                                                   ! total plankton consumption
        tDConsFiBentTotPot = sum(tDConsFiBentPot)                                                                   ! total benthos consumption
        tDConsFiPiscTotPot = sum(tDConsFiPiscPot)                                                                   ! total fish consumption
                                                                                                                    !
        fFishPlan = tDConsFiPlanTotPot/(tDConsFiPlanTotPot+tDConsFiBentTotPot+tDConsFiPiscTotPot+NearZero)          ! time allocation to planktivory equal to its consumption, weighted by all consumption
        fFishBent = tDConsFiBentTotPot/(tDConsFiPlanTotPot+tDConsFiBentTotPot+tDConsFiPiscTotPot+NearZero)          ! time allocation to bentivory equal to its consumption, weighted by all consumption
        fFishPisc = tDConsFiPiscTotPot/(tDConsFiPlanTotPot+tDConsFiBentTotPot+tDConsFiPiscTotPot+NearZero)          ! time allocation to piscivory equal to its consumption, weighted by all consumption
        !===========================================================================================================!                                                          
        ! 2.3 calculate potential assimilation, net energy gain and predation mortality                             !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDAssFiPlanPot = tDConsFiPlanTotPot * self%fDAssFi * fFishPlan                                              ! calculate planktivorous assimilation rate at constant feeding
        tDAssFiBentPot = tDConsFiBentTotPot * self%fDAssFi * fFishBent                                              ! calculate bentivorous assimilation rate at constant feeding
        tDAssFiPiscPot = tDConsFiPiscTotPot * self%fDAssFi * fFishPisc                                              ! calculate piscivorous assimilation rate at constant feeding
        tDAssFiTotPot = tDAssFiPlanPot + tDAssFiBentPot + tDAssFiPiscPot                                            ! calculate total DW assimilation rate at constant feeding
        NetGrowthFA = tDAssFiTotPot - (1.0_rk+self%fDRespActFi)*self%kDRespFi*uFunTmFish                            ! calculate net energy gain from constant feeding
                                                                                                                    !
        _GET_(self%id_pred_sms,vPred)                                                                               ! get current predation mortality
        !===========================================================================================================!                                                          
        ! 2.4 calculate optimal foraging arena use and feeding fraction of population                               !                                                       
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        _GET_(self%id_fVul,fVul)                                                                                    ! get current predation vulnerability
        PStar_now = (1._rk-fVul)/self%fPV                                                                           ! back-calculate current feeding behavior
        if (self%qOPT .eq. 0) then                                                                                  ! optimal behavior is turned off
            PStar = NearZero                                                                                        !
            fFeed = 1.0_rk                                                                                          !          
        elseif (NetGrowthFA .LT. 0.0_rk .AND. (NetGrowthFA .LT. -self%kDRespFi*uFunTmFish .OR. lCon)) then          ! fish are starving; cost of feeding higher than gain, or sufficient reserves present
            PStar = 1.0_rk                                                                                          !
            fFeed = 0.0_rk                                                                                          !
        elseif (NetGrowthFA .LT. 0.0_rk .AND. NetGrowthFA >= -self%kDRespFi*uFunTmFish) then                        ! fish are starving; feeding gains are higher than costs
            fFeed = 1.0_rk                                                                                          !
            if (self%fFC == 0.0_rk .AND. self%fPV > 0.0_rk) then                                                    !   if risk reduction does not reduce feeding and risk reduction is possible
                PStar = 1.0_rk                                                                                      !
            else                                                                                                    !   if risk reduction is not possible
                PStar = NearZero                                                                                    !
            endif                                                                                                   !
        elseif (NetGrowthFA >= 0.0_rk) then                                                                         ! if net energy gain is positive
            fFC = max(NearZero,self%fFC)                                                                            !
            fGOT = fFishPlan*sum(relConsPlan*self%fGutOccPlan) + fFishBent*sum(relConsBent*self%fGutOccBent) &      ! calculate overall fGutOcc value (weighted by relative consumption of each food item)
                + fFishPisc*sum(relConsPisc*self%fGutOccPisc)                                                       ! 
            R = fFishPlan*aFunVegPlan*sum(inclPlan*sDPlan*self%cClearPlan) + fFishBent*aFunVegBent*sum(inclBent*sDBent*self%cClearBent) &   ! calculate overall food availability
                + fFishPisc*sum(inclPisc*sDPisc*self%cClearPisc)                                                    !
            M = self%kDRespFi*uFunTmFish                                                                            ! temperature-corrected metabolism
            Fmax = kDConsMax*uFunTmFish                                                                             ! temperature-corrected max consumption
            PStar = (fFC*fGOT*Fmax*self%fPV*R**2._rk*vPred + M*fFC*fGOT*R*(Fmax + fGOT*R)*(fFC*(self%kMortFi + vPred)*self%fDRespActFi - self%fPV*vPred*(1._rk + self%fDRespActFi)) &
                - sqrt(max(0.0_rk,fFC**2._rk*fGOT*Fmax**2._rk*R**2._rk*(Fmax*self%fPV*R*vPred*(-self%fPV*vPred + fFC*(self%kMortFi + vPred)) &
                + M*(-self%fPV*(Fmax + fGOT*R)*vPred + fFC*fGOT*R*(self%kMortFi + vPred))*(fFC*(self%kMortFi + vPred)*self%fDRespActFi - self%fPV*vPred*(1._rk + self%fDRespActFi)))))) &
                /(fFC**2._rk*fGOT*R**2._rk*(Fmax*self%fPV*vPred + M*fGOT*(fFC*(self%kMortFi + vPred)*self%fDRespActFi - self%fPV*vPred*(1._rk + self%fDRespActFi))))
            PStar = max(NearZero,min(1.0_rk,PStar))                                                                 ! constrain PStar to values between zero and one
            fFeed = 1.0_rk-PStar_now*self%fFC                                                                       ! calculate fFeed (total fish feeding efficiency)
        endif                                                                                                       !
        tfVul = (PStar_now-PStar)*self%fPV*(1._rk/secs_pr_day)                                                      ! calculate rate of change in predation vulnerability
        !===========================================================================================================!
        ! 2.5 calculate final consumption and assimilation rates                                                    !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        aFeedLvlPlan = aFunVegPlan*sum(inclPlan*self%cClearPlan*self%fGutOccPlan*sDPlan)*fFeed/ &                   !   calculate feeding level, based on all available plankton prey
            (aFunVegPlan*sum(inclPlan*self%cClearPlan*self%fGutOccPlan*sDPlan)*fFeed + uFunTmFish*kDConsMax)        !
        aFeedLvlBent = aFunVegBent*sum(inclBent*self%cClearBent*self%fGutOccBent*sDBent)*fFeed/ &                   !   calculate feeding level, based on all available plankton prey
            (aFunVegBent*sum(inclBent*self%cClearBent*self%fGutOccBent*sDBent)*fFeed + uFunTmFish*kDConsMax)        !
        aFeedLvlPisc = sum(inclPisc*self%cClearPisc*self%fGutOccPisc*sDPisc)*fFeed/ &                               !   calculate feeding level, based on all available fish prey
            (sum(inclPisc*self%cClearPisc*self%fGutOccPisc*sDPisc)*fFeed + uFunTmFish*kDConsMax)                    !
        tDConsFiPlan = sDFiEff*fFeed*aFunVegPlan*(inclPlan*self%cClearPlan*sDPlan)*(1._rk-aFeedLvlPlan)             !   calculate potential consumption of all available plankton prey
        tDConsFiBent = sDFiEff*fFeed*aFunVegBent*(inclBent*self%cClearBent*sDBent)*(1._rk-aFeedLvlBent)             !   calculate potential consumption of all available plankton prey
        tDConsFiPisc = sDFiEff*fFeed*(inclPisc*self%cClearPisc*sDPisc)*(1._rk-aFeedLvlPisc)                         !   calculate potential consumption of all available fish. prey
        tDConsFiPlan = tDConsFiPlan*fFishPlan                                                                       !
        tDConsFiBent = tDConsFiBent*fFishBent                                                                       !
        tDConsFiPisc = tDConsFiPisc*fFishPisc                                                                       !
                                                                                                                    !
        tDConsFiPlanSum = sum(tDConsFiPlan)                                                                         !
        tDConsFiBentSum = sum(tDConsFiBent)                                                                         !
        tDConsFiPiscSum = sum(tDConsFiPisc)                                                                         !
        tDAssFiPlan = tDConsFiPlanSum*self%fDAssFi  !- tDEnvFi * fFishPlan                                          ! calculate planktivorous assimilation rate - environmental correction from PCLake removed.
        tDAssFiBent = tDConsFiBentSum*self%fDAssFi  !- tDEnvFi * fFishBent                                          ! calculate bentivorous assimilation rate - environmental correction from PCLake removed.
        tDAssFiPisc = tDConsFiPiscSum*self%fDAssFi !- tDEnvFi * fFishPisc                                           ! calculate piscivorous assimilation rate - environmental correction from PCLake removed.
        tDAssFiTot = tDAssFiPlan + tDAssFiBent + tDAssFiPisc                                                        ! calculate total DW assimilation rate
                                                                                                                    !
        BioTurb = fFishBent * fFeed*sDfiEff * uFunTmFish * self%kTurbFish                                           ! current bioturbation by fish (zero without benthivory)
        !===========================================================================================================!
        ! 2.6 for fish prey using a foraging arena; calculate predation in case fVulPisc=1                          !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        if (self%nPISCprey /= 0) then                                                                               !
            vPiscPredPot = sDFiEff*(inclPisc*self%cClearPisc)*(1._rk-aFeedLvlPisc)                                  ! calculate potential predation rate on all available fish. prey
            vPiscPred = vPiscPredPot*fFishPisc*fFeed                                                                ! calculate final mortality rate for all fish prey  
        endif                                                                                                       !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 3. calculate prey consumption rates (DW, N & P)                                                                !
   !================================================================================================================!
        ! 3.1 plankton consumption                                                                                  !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tPConsFiPlan = rPDPlan * tDConsFiPlan                                                                       ! calculate P consumption of plankton (dimension: nPLANprey)
        tNConsFiPlan = rNDPlan * tDConsFiPlan                                                                       ! calculate N consumption of plankton (dimension: nPLANprey)
        tCConsFiPlan = rCDPlan * tDConsFiPlan                                                                       ! calculate C consumption of plankton (dimension: nPLANprey)
        !===========================================================================================================!
        ! 3.2 benthos consumption                                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tPConsFiBent = rPDBent * tDConsFiBent                                                                       ! calculate P consumption of benthos (dimension: nBENprey)
        tNConsFiBent = rNDBent * tDConsFiBent                                                                       ! calculate N consumption of benthos (dimension: nBENprey)
        tCConsFiBent = rCDBent * tDConsFiBent                                                                       ! calculate C consumption of benthos (dimension: nBENprey)
        !===========================================================================================================!
        ! 3.3 piscivorous consumption                                                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tPConsFiPisc = rPDPisc * tDConsFiPisc                                                                       ! calculate P consumption of fish (dimension: nPISCprey)
        tNConsFiPisc = rNDPisc * tDConsFiPisc                                                                       ! calculate N consumption of fish (dimension: nPISCprey)
        tCConsFiPisc = rCDPisc * tDConsFiPisc                                                                       ! calculate C consumption of fish (dimension: nPISCprey)
        !===========================================================================================================!
        ! 3.4 total consumption                                                                                     !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDConsFiTot = sum(tDConsFiPlan) + sum(tDConsFiBent) + sum(tDConsFiPisc)                                     ! calculate total DW consumption
        tPConsFiTot = sum(tPConsFiPlan) + sum(tPConsFiBent) + sum(tPConsFiPisc)                                     ! calculate total P consumption 
        tNConsFiTot = sum(tNConsFiPlan) + sum(tNConsFiBent) + sum(tNConsFiPisc)                                     ! calculate total N consumption 
        tCConsFiTot = sum(tCConsFiPlan) + sum(tCConsFiBent) + sum(tCConsFiPisc)                                     ! calculate total C consumption 
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. calculate N, and P assimilation                                                                             !
   !================================================================================================================!
        ! 4.1 plankton                                                                                              !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 4.1.1 Nitrogen                                                                                       !
             !------------------------------------------------------------------------------------------------------!
             afNAssFiPlan = min(1.0_rk,(self%cNDRef / rNDPlan) * self%fDAssFi)                                      ! calculate N assimilation efficiency of plankton
             tNAssFiPlan = afNAssFiPlan * tNConsFiPlan                                                              ! calculate N assimilation rate from planktivory
             !======================================================================================================!
             ! 4.1.2 Phosphorous                                                                                    !
             !------------------------------------------------------------------------------------------------------!
             afPAssFiPlan = min(1.0_rk,(self%cPDRef / rPDPlan) * self%fDAssFi)                                      ! calculate P assimilation efficiency of plankton
             tPAssFiPlan = afPAssFiPlan * tPConsFiPlan                                                              ! calculate P assimilation rate from planktivy
             !======================================================================================================!
             ! 4.1.3 Carbon                                                                                         !
             !------------------------------------------------------------------------------------------------------!
             afCAssFiPlan = min(1.0_rk,(self%cCDRef / rCDPlan) * self%fDAssFi)                                      ! calculate C assimilation efficiency of plankton
             tCAssFiPlan = afCAssFiPlan * tCConsFiPlan                                                              ! calculate C assimilation rate from planktivy
        !===========================================================================================================!
        ! 4.2 benthos                                                                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 4.2.1 Nitrogen                                                                                       !
             !------------------------------------------------------------------------------------------------------!
             afNAssFiBent = min(1.0_rk,(self%cNDRef / rNDBent) * self%fDAssFi)                                      ! calculate N assimilation efficiency of benthos
             tNAssFiBent = afNAssFiBent * tNConsFiBent                                                              ! calculate N assimilation rate from bentivory
             !======================================================================================================!
             ! 4.2.2 Phosphorous                                                                                    !
             !------------------------------------------------------------------------------------------------------!
             afPAssFiBent = min(1.0_rk,(self%cPDRef / rPDBent) * self%fDAssFi)                                      ! calculate P assimilation efficiency of benthos 
             tPAssFiBent = afPAssFiBent * tPConsFiBent                                                              ! calculate P assimilation rate from bentivory
             !======================================================================================================!
             ! 4.2.2 Carbon                                                                                         !
             !------------------------------------------------------------------------------------------------------!
             afCAssFiBent = min(1.0_rk,(self%cCDRef / rCDBent) * self%fDAssFi)                                      ! calculate C assimilation efficiency of benthos 
             tCAssFiBent = afCAssFiBent * tCConsFiBent                                                              ! calculate C assimilation rate from bentivory
        !===========================================================================================================!
        ! 4.3 piscivory                                                                                             !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 4.3.1 Nitrogen                                                                                       !
             !------------------------------------------------------------------------------------------------------!
             afNAssFiPisc = min(1.0_rk,(self%cNDRef / rNDPisc) * self%fDAssFi)                                      ! calculate N assimilation efficiency of fish
             tNAssFiPisc = afNAssFiPisc * tNConsFiPisc                                                              ! calculate N assimilation rate from piscivory
             !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 4.3.2 Phosphorous                                                                                    !
             !------------------------------------------------------------------------------------------------------!
             afPAssFiPisc = min(1.0_rk,(self%cPDRef / rPDPisc) * self%fDAssFi)                                      ! calculate P assimilation efficiency of fish
             tPAssFiPisc = afPAssFiPisc * tPConsFiPisc                                                              ! calculate P assimilation rate from piscivory
             !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             ! 4.3.2 Carbon                                                                                         !
             !------------------------------------------------------------------------------------------------------!
             afCAssFiPisc = min(1.0_rk,(self%cCDRef / rCDPisc) * self%fDAssFi)                                      ! calculate C assimilation efficiency of fish
             tCAssFiPisc = afCAssFiPisc * tCConsFiPisc                                                              ! calculate C assimilation rate from piscivory
        !===========================================================================================================!
        ! 4.4 total assimilation                                                                                    ! 
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
             tPAssFiTot = sum(tPAssFiPlan) + sum(tPAssFiBent) + sum(tPAssFiPisc)                                    ! calculate total P assimilation rate
             tNAssFiTot = sum(tNAssFiPlan) + sum(tNAssFiBent) + sum(tNAssFiPisc)                                    ! calculate total N assimilation rate
             tCAssFiTot = sum(tCAssFiPlan) + sum(tCAssFiBent) + sum(tCAssFiPisc)                                    ! calculate total C assimilation rate
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 5. calculate respiration, egestion, excretion, mortality and migration                                         !
   !================================================================================================================!
        ! 5.1 calculate respiration/excretion                                                                       !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDRespFi = (self%cPDRef / rPDFi) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi * uFunTmFish * sDFi        ! calculate DW respiration rate
        if (.NOT. self%lNutMeth) then                                                                               ! case dynamic stochiometry
            tPExcrFi = (rPDFi / self%cPDRef) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi*uFunTmFish*sPFi        !   calculate P excretion rate
            tNExcrFi = (rNDFi / self%cNDRef) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi*uFunTmFish*sNFi        !   calculate N excretion rate
            tCRespFi = (rCDFi / self%cCDRef) * (1.0_rk+self%fDRespActFi*fFeed)*self%kDRespFi*uFunTmFish*sCFi        !   calculate C respiration rate
        else                                                                                                        ! case fixed stochiometry
            tPExcrFi = tDRespFi * self%cPDRef                                                                       !   calculate P excretion rate
            tNExcrFi = tDRespFi * self%cNDRef                                                                       !   calculate N excretion rate
            tCRespFi = tDRespFi * self%cCDRef                                                                       !   calculate C respiration rate
        endif                                                                                                       !
        !===========================================================================================================!
        ! 5.2 calculate fish egestion                                                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDEgesFi = tDConsFiTot - tDAssFiTot                                                                         ! calculate DW egestion rate
        tPEgesFi = tPConsFiTot - tPAssFiTot                                                                         ! calculate P egestion rate
        tNEgesFi = tNConsFiTot - tNAssFiTot                                                                         ! calculate N egestion rate
        tCEgesFi = tCConsFiTot - tCAssFiTot                                                                         ! calculate C egestion rate
        !===========================================================================================================!
        ! 5.3 calculate fish mortality                                                                              !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDMortFi = self%kMortFi * sDFi !+ (1.0_rk - aDSatFiTot) * tDEnvFi                                           ! calculate current mortality rate  - environmental correction from PCLake removed.
        tPMortFi = rPDFi * tDMortFi                                                                                 !   calculate loss of P from mortality
        tNMortFi = rNDFi * tDMortFi                                                                                 !   calculate loss of N from mortality
        tCMortFi = rCDFi * tDMortFi                                                                                 !   calculate loss of C from mortality
        !===========================================================================================================!
        ! 5.4 calculate fish migration                                                                              !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDMigrFi = self%kMigrFish *(self%cDFiIn - sDFi)                                                             ! calculate current migration rate
        tPMigrFi = self%kMigrFish *(self%cPDRef * self%cDFiIn - sPFi)                                               !   calculate change in P from migration
        tNMigrFi = self%kMigrFish *(self%cNDRef * self%cDFiIn - sNFi)                                               !   calculate change in N from migration
        tCMigrFi = self%kMigrFish *(self%cCDRef * self%cDFiIn - sCFi)                                               !   calculate change in C from migration
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 6. special case: ageing/reproduction exchange between fish instances                                           !
   !================================================================================================================!
        ! 6.1 default case: no stages                                                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDAgeFish = 0.0_rk                                                                                          ! initialize DW aging flux
        tPAgeFish = 0.0_rk                                                                                          ! initialize P aging flux
        tNAgeFish = 0.0_rk                                                                                          ! initialize N aging flux
        tCAgeFish = 0.0_rk                                                                                          ! initialize N aging flux
        !===========================================================================================================!
        ! 6.2 case bioenergetics: calculate energy reserve allocation                                               !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        if (self%qStage > 0 ) then                                                                                  ! case size structure
            _GET_(self%id_sDSiz,sDSiz)                                                                              !   get current average size
            rG = (tDAssFiTot - tDRespFi)/sDFi                                                                       !   calculate specific growth rate
            fRes_now = sFRes/(1.0_rk-sFRes)                                                                         !   calculate current q value (Persson & de Roos 1998)
            if (sDSiz < self%cDfin .AND. sFRes > self%fResMin) tDSiz = rG*sDSiz                                     !   if size less than max. and reserve fraction larger than min, average size grows
            if (tDAssFiTot - tDRespFi > 0._rk) then                                                                 !   check for net positive growth
                q=self%fResMax/(1.0_rk-self%fResMax)                                                                !     adapted from Persson & de Roos 1998
                fIrreversible = 1.0_rk/((1.0_rk+q)*q)   *   fRes_now                                                !     calculate allocation of growth to structural mass
                tFRes = ((1._rk-fIrreversible)-sFRes)*((tDAssFiTot - tDRespFi)/sDFi) !((tDAssFiTot - tDRespFi)/(tDAssFiTot-tDRespFi + sDFi))        !     calculate reserve fraction rate of change
            else                                                                                                    !   if net growth is negative
                tFRes = (1.0_rk-sFRes)*((tDAssFiTot - tDRespFi)/sDFi) !(tDAssFiTot-tDRespFi + sDFi))                       !     calculate reserve fraction rate of change
            endif                                                                                                   !
            if (sFRes < self%fResMin .AND. tDAssFiTot - tDRespFi <= 0._rk) then                                     !   if reserve fraction is less than min., and net growth is negative
                tDMortFi = tDMortFi + min(0.2_rk,sDFi*self%cMortStarv*(self%fResMin/(1.0_rk-self%fResMin)*(1.0_rk/fRes_now)-1.0_rk))/secs_pr_day ! calculate added mortality from starvation
                tPMortFi = rPDFi * tDMortFi                                                                         !   calculate loss of P from mortality
                tNMortFi = rNDFi * tDMortFi                                                                         !   calculate loss of N from mortality
                tCMortFi = rCDFi * tDMortFi                                                                         !   calculate loss of C from mortality
            endif                                                                                                   !
        endif                                                                                                       !
        !===========================================================================================================!
        ! 6.3 case juvenile fish: calculate aging                                                                   !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        if ((self%qStage == 2 .OR. self%qStage == 3) .AND. (((tDAssFiTot - tDRespFi)/sDFi) > 0._rk)) then           ! case aging and net positive growth 
           eAge = ((sDSiz-self%cDinit)/(self%cDfin-self%cDinit))                                                    !
           k_mat = 0.5e-6_rk !rG*secs_pr_day*1e-5_rk                                                                                 !   calculate current daily growth rate
           fAgeFish = max(0._rk,min(1._rk,((((1._rk- k_mat)/ k_mat)**(2._rk*eAge)-1._rk)/(((1._rk- k_mat)/ k_mat)**(2._rk)-1._rk))))/secs_pr_day     !   calculate specific maturation rate 
           tDAgeFish = fAgeFish*sDFi                                                                                !   calculate maturation flux
           tDSiz = tDSiz - abs(fAgeFish*(sDSiz-self%cDfin))                                                         !   calculate rate of change of individual size
           tPAgeFish = rPDFi * tDAgeFish                                                                            !   calculate aging P flux
           tNAgeFish = rNDFi * tDAgeFish                                                                            !   calculate aging N flux
           tCAgeFish = rCDFi * tDAgeFish                                                                            !   calculate aging C flux
           _GET_(self%id_FiAd_Res,FiAd_Res)                                                                         !   get next stage reserve fraction
           _GET_(self%id_FiAd_D,  FiAd_D)                                                                           !   get next stage biomass
           _GET_(self%id_FiAd_Siz,FiAd_Siz)                                                                         !   get next stage mean size
           tDAgeRes = min(1._rk/3600._rk,(sFRes - FiAd_Res)*(tDAgeFish/FiAd_D)) !(tDAgeFish+FiAd_D)))                         !   calculate rate of change of next stage reserve fraction
           tDAgeSiz = (tDAgeFish/FiAd_D)*((FiAd_Siz+NearZero)/self%cDfin)*(self%cDfin-FiAd_Siz)                     !   calculate rate of change of next stage mean size
        endif                                                                                                       !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 7. final flux calculations                                                                                     !
   !================================================================================================================!
        ! 7.1 final fish rate of change                                                                             !
        !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
        tDFi = tDMigrFi + tDAssFiTot - tDRespFi - tDMortFi - tDAgeFish                                              ! calculate the final rate of change in DW
        tPFi = tPMigrFi + tPAssFiTot - tPExcrFi - tPMortFi - tPAgeFish                                              ! calculate the final rate of change in P
        tNFi = tNMigrFi + tNAssFiTot - tNExcrFi - tNMortFi - tNAgeFish                                              ! calculate the final rate of change in N
        tCFi = tCMigrFi + tCAssFiTot - tCRespFi - tCMortFi - tCAgeFish                                              ! calculate the final rate of change in C
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
           tPMortFiTOM = tPMortFi - tPMortFiBot - tPMortFiPO4                                                       ! calculate organic P part of mortality flux
           tPEgesFiTOM = tPEgesFi - tPEgesFiPO4                                                                     ! calculate organic P part of egestion
           tPFiTOMW = tPEgesFiTOM + tPMortFiTOM                                                                     ! calculate total organic P flux to the water column
           tPFiPOMW = tPFiTOMW * (1.0_rk - self%fFiDOMW)                                                            ! calculate particulate part of organic P flux to water column
           tPFiDOMW = tPFiTOMW * self%fFiDOMW                                                                       ! calculate dissolved part of organic P flux to water column
           !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
           ! 7.2.4 carbon                                                                                           !
           !--------------------------------------------------------------------------------------------------------!
           tCFiCO2W = tCRespFi                                                                                      ! calculate total CO2 flux to the sediment
           tCMortFiBot = self%fDBone * (tCMortFi)                                                                   ! calculate C flux out of the system (into the sediment) from mortality
           tCMortFiTOM = (tDMortFi) - tDMortFiBot                                                                   ! calculate part of dead fish C staying in the system
           tCFiTOMW = tCEgesFi + tCMortFiTOM                                                                        ! calculate total flux of C to the water column
           tCFiPOMW = tCFiTOMW * (1.0_rk - self%fFiDOMW)                                                            ! calculate particulate fraction of C flux to water column
           tCFiDOMW = tCFiTOMW * self%fFiDOMW                                                                       ! calculate dissolved fraction of C flux to water column
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 8. update model variables                                                                                      !
   !================================================================================================================!
      ! 8.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_ODE_(self%id_sDFi,tDFi)                                                                                  ! set fish DW ODE
      _SET_ODE_(self%id_sPFi,tPFi)                                                                                  ! set fish P ODE
      _SET_ODE_(self%id_sNFi,tNFi)                                                                                  ! set fish N ODE
      _SET_ODE_(self%id_sCFi,tCFi)                                                                                  ! set fish C ODE
      if (self%qStage > 0 ) then                                                                                    ! case size structure	  if qStage 
          _SET_ODE_(self%id_sDSiz,tDSiz)                                                                            !   set fish average size ODE
          _SET_ODE_(self%id_sFRes,tFRes)! - tDAgeRes)                                                               !   set fish reserve fraction ODE
	  endif                                                                                                         !  
      _SET_ODE_(self%id_fVul,tfVul)                                                                                 ! set fish predation vulnerability ODE
      _SET_DIAGNOSTIC_(self%id_PStar, PStar_now)                                                                    ! save fish optimal behavior
      !=============================================================================================================!
      ! 8.2 update external biotic state variables                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 8.2.1 plankton                                                                                           !
         !----------------------------------------------------------------------------------------------------------!
         if (self%nPLANprey /= 0) then                                                                              ! case planktivory
            do i_prey = 1, self%nPLANprey                                                                           !   for all plankton prey
               _SET_ODE_(self%id_DFoodPlan(i_prey),  -tDConsFiPlan(i_prey))                                         !     update plankton prey DW ODEs
               _SET_ODE_(self%id_NFoodPlan(i_prey),  -tNConsFiPlan(i_prey))                                         !     update plankton prey N ODEs 
               _SET_ODE_(self%id_PFoodPlan(i_prey),  -tPConsFiPlan(i_prey))                                         !     update plankton prey P ODEs
               _SET_ODE_(self%id_CFoodPlan(i_prey),  -tCConsFiPlan(i_prey))                                         !     update plankton prey C ODEs
            end do                                                                                                  !
         endif                                                                                                      !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 8.2.2 benthos                                                                                            !
         !----------------------------------------------------------------------------------------------------------!
         if (self%nBENprey /= 0) then                                                                               ! case bentivory
            do i_prey = 1,self%nBENprey                                                                             !   for all benthos prey
               _SET_DIAGNOSTIC_(self%id_tDConsFiBent_out(i_prey), tDConsFiBent(i_prey))                             !
               _SET_DIAGNOSTIC_(self%id_tNConsFiBent_out(i_prey), tNConsFiBent(i_prey))                             !
               _SET_DIAGNOSTIC_(self%id_tPConsFiBent_out(i_prey), tPConsFiBent(i_prey))                             !
               _SET_DIAGNOSTIC_(self%id_tCConsFiBent_out(i_prey), tCConsFiBent(i_prey))                             !
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
               _SET_ODE_(self%id_CFoodPisc(i_prey),  -tCConsFiPisc(i_prey))                                         !     update fish prey P ODEs
               _SET_ODE_(self%id_pred_dummy_Pisc(i_prey),    vPiscPred(i_prey))                                     !
            end do                                                                                                  !
         endif                                                                                                      !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 8.2.4 other stages                                                                                       !
         !----------------------------------------------------------------------------------------------------------!
         if (self%qStage == 2 .OR. self%qStage == 3) then                                                           ! case aging
            _SET_ODE_(self%id_FiAd_D,  tDAgeFish)                                                                   !   update older stage DW ODE
            _SET_ODE_(self%id_FiAd_N,  tNAgeFish)                                                                   !   update older stage N ODE
            _SET_ODE_(self%id_FiAd_P,  tPAgeFish)                                                                   !   update older stage P ODE
            _SET_ODE_(self%id_FiAd_Res,tDAgeRes)                                                                    !   update older stage Gonads
            _SET_ODE_(self%id_FiAd_Siz,tDAgeSiz)                                                                    !
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
      
      !_SET_ODE_(self%id_CO2poolW,  tCFiCO2W)                                                                        ! update DIC water column ODE
      _SET_ODE_(self%id_CPOMpoolW, tCFiPOMW)                                                                        ! update particulate organic C water column ODE
      _SET_ODE_(self%id_CDOMpoolW, tCFiDOMW)                                                                        ! update dissolved organic C water column ODE
   !================================================================================================================!
      !=============================================================================================================!
      ! 8.4 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
          _SET_DIAGNOSTIC_(self%id_tDMigrFi,         tDMigrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNMigrFi,         tNMigrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPMigrFi,         tPMigrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tCMigrFi,         tCMigrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDEgesFi,         tDEgesFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNEgesFi,         tNEgesFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPEgesFi,         tPEgesFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tCEgesFi,         tCEgesFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDFiPOMW,         tDFiPOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDFiDOMW,         tDFiDOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNFiPOMW,         tNFiPOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNFiDOMW,         tNFiDOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPFiPOMW,         tPFiPOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPFiDOMW,         tPFiDOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tCFiPOMW,         tCFiPOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tCFiDOMW,         tCFiDOMW)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDMortFi,         tDMortFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNMortFi,         tNMortFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPMortFi,         tPMortFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tCMortFi,         tCMortFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDMortFiBot,      tDMortFiBot)                                                   !
          _SET_DIAGNOSTIC_(self%id_tNMortFiBot,      tNMortFiBot)                                                   !
          _SET_DIAGNOSTIC_(self%id_tPMortFiBot,      tPMortFiBot)                                                   !
          _SET_DIAGNOSTIC_(self%id_tCMortFiBot,      tCMortFiBot)                                                   !
          _SET_DIAGNOSTIC_(self%id_tDRespFi,         tDRespFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tCRespFi,         tCRespFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDAssFiTot,       tDAssFiTot)                                                    !
          _SET_DIAGNOSTIC_(self%id_tNExcrFi,         tNExcrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tNFiNH4W,         tNFiNH4W)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPExcrFi,         tPExcrFi)                                                      !
          _SET_DIAGNOSTIC_(self%id_tPFiPO4W,         tPFiPO4W)                                                      !
          _SET_DIAGNOSTIC_(self%id_tDAgeFish,        tDAgeFish)                                                     !
          _SET_DIAGNOSTIC_(self%id_tNAgeFish,        tNAgeFish)                                                     !
          _SET_DIAGNOSTIC_(self%id_tPAgeFish,        tPAgeFish)                                                     !
          _SET_DIAGNOSTIC_(self%id_tCAgeFish,        tCAgeFish)                                                     !
          _SET_DIAGNOSTIC_(self%id_tDConsFiPlanSum,  tDConsFiPlanSum)                                               !
          _SET_DIAGNOSTIC_(self%id_tDConsFiBentSum,  tDConsFiBentSum)                                               !
          _SET_DIAGNOSTIC_(self%id_tDConsFiPiscSum,  tDConsFiPiscSum)                                               !
          _SET_DIAGNOSTIC_(self%id_aFeedLvlPlan,     aFeedLvlPlan)                                                  !
          _SET_DIAGNOSTIC_(self%id_aFeedLvlBent,     aFeedLvlBent)                                                  !
          _SET_DIAGNOSTIC_(self%id_aFeedLvlPisc,     aFeedLvlPisc)                                                  !
          _SET_DIAGNOSTIC_(self%id_fFishPlan,        fFishPlan)                                                     !
          _SET_DIAGNOSTIC_(self%id_fFishBent,        fFishBent)                                                     !
          _SET_DIAGNOSTIC_(self%id_fFishPisc,        fFishPisc)                                                     !
         if (self%nPlanprey /= 0) then                                                                              ! case planktivory
            do i_prey = 1, self%nPlanprey                                                                           !
                _SET_DIAGNOSTIC_(self%id_tDConsFiPlan(i_prey), tDConsFiPlan(i_prey))                                !
                _SET_DIAGNOSTIC_(self%id_tPConsFiPlan(i_prey), tPConsFiPlan(i_prey))                                !
                _SET_DIAGNOSTIC_(self%id_tNConsFiPlan(i_prey), tNConsFiPlan(i_prey))                                !
                _SET_DIAGNOSTIC_(self%id_tCConsFiPlan(i_prey), tCConsFiPlan(i_prey))                                !
            end do                                                                                                  !
         endif                                                                                                      !
         if (self%nPISCprey /= 0) then                                                                              ! case piscivory
            do i_prey = 1,self%nPISCprey                                                                            !
                _SET_DIAGNOSTIC_(self%id_tDConsFiPisc(i_prey), tDConsFiPisc(i_prey))                                !
                _SET_DIAGNOSTIC_(self%id_tPConsFiPisc(i_prey), tPConsFiPisc(i_prey))                                !
                _SET_DIAGNOSTIC_(self%id_tNConsFiPisc(i_prey), tNConsFiPisc(i_prey))                                !
                _SET_DIAGNOSTIC_(self%id_tCConsFiPisc(i_prey), tCConsFiPisc(i_prey))                                !
            end do                                                                                                  !
         endif                                                                                                      !
      endif                                                                                                         !
   !================================================================================================================!
   _LOOP_END_ !!! END OF MODEL CODE::
end subroutine do

!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
!�� SUBROUTINE: DO BOTTOM                                                                                                                                                                          ��
!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_fish), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk), dimension(self%nBENprey) :: tDConsFiBent, tNConsFiBent, tPConsFiBent, tCConsFiBent
   real(rk)                           :: bot_pel_conv
   integer                            :: i_prey

   _HORIZONTAL_LOOP_BEGIN_  !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. calculate bottom/pelagic convertion and apply bentivorous consumption rates                                !
   !================================================================================================================!
   if (self%nBENprey /= 0) then                                                                                     ! in case of bentivory
        _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)                                                         !
       do i_prey = 1,self%nBENprey                                                                                  ! for each benthos prey
          _GET_(self%id_tDConsFiBent(i_prey),tDConsFiBent(i_prey))                                                  !   get the bentivorous DW consumption
          _GET_(self%id_tNConsFiBent(i_prey),tNConsFiBent(i_prey))                                                  !   get the bentivorous N consumption
          _GET_(self%id_tPConsFiBent(i_prey),tPConsFiBent(i_prey))                                                  !   get the bentivorous P consumption
          _GET_(self%id_tCConsFiBent(i_prey),tCConsFiBent(i_prey))                                                  !   get the bentivorous C consumption
                                                                                                                    ! 
          _SET_BOTTOM_ODE_(self%id_DFoodBent(i_prey), -tDConsFiBent(i_prey)*bot_pel_conv)                           !   apply consumption to benthos prey DW
          _SET_BOTTOM_ODE_(self%id_NFoodBent(i_prey), -tNConsFiBent(i_prey)*bot_pel_conv)                           !   apply consumption to benthos prey N
          _SET_BOTTOM_ODE_(self%id_PFoodBent(i_prey), -tPConsFiBent(i_prey)*bot_pel_conv)                           !   apply consumption to benthos prey P
          _SET_BOTTOM_ODE_(self%id_CFoodBent(i_prey), -tCConsFiBent(i_prey)*bot_pel_conv)                           !   apply consumption to benthos prey C
          _SET_BOTTOM_EXCHANGE_(self%id_DFoodBent_PV(i_prey),-tDConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)       !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
          _SET_BOTTOM_EXCHANGE_(self%id_NFoodBent_PV(i_prey),-tNConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)       !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
          _SET_BOTTOM_EXCHANGE_(self%id_PFoodBent_PV(i_prey),-tPConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)       !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
          _SET_BOTTOM_EXCHANGE_(self%id_CFoodBent_PV(i_prey),-tCConsFiBent(i_prey)*bot_pel_conv*bot_pel_conv)       !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
       end do                                                                                                       !
   endif                                                                                                            !
   !================================================================================================================!
   _HORIZONTAL_LOOP_END_  !!! END OF MODEL CODE::  
end subroutine do_bottom
   
!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
!�� SUBROUTINE: GET VERTICAL MOVEMENT                                                                                                                                                              ��
!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
subroutine get_vertical_movement(self,_ARGUMENTS_GET_VERTICAL_MOVEMENT_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_fish),intent(in)    :: self
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
   else                                                                                                             !
      qSWIM = 0                                                                                                     !
   endif                                                                                                            !
   _SET_VERTICAL_MOVEMENT_(self%id_sDFi,qSWIM*self%cVswim)                                                          ! set DW migration speed
   _SET_VERTICAL_MOVEMENT_(self%id_sPFi,qSWIM*self%cVswim)                                                          ! set P migration speed
   _SET_VERTICAL_MOVEMENT_(self%id_sNFi,qSWIM*self%cVswim)                                                          ! set N migration speed
   _SET_VERTICAL_MOVEMENT_(self%id_sCFi,qSWIM*self%cVswim)                                                          ! set C migration speed
   !================================================================================================================!
   _LOOP_END_   !!! END OF MODEL CODE::  
end subroutine get_vertical_movement

!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
!�� SUBROUTINE: CHECK STATE (REPRODUCTION)                                                                                                                                                         ��
!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
subroutine check_state(self, _ARGUMENTS_CHECK_STATE_)
   class (type_wet_fish), intent(in) :: self
   _DECLARE_ARGUMENTS_CHECK_STATE_

   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk) :: sFRes, sDFi, sNFi, sPFi, sCFi, rPDFi, rNDFi, rCDFi, tDReprFish, tNReprFish, tPReprFish, tCReprFish, Day, FiJu_D, FiJu_N, FiJu_P, FiJu_C, FiJu_Res, DPOMpoolW, NPOMpoolW, PPOMpoolW, CPOMpoolW 
   real(rk) :: FiJu_Siz_new, rDReprFish, FiJu_Res_new, sDSiz, FiJu_Siz, Day_last, tDReproPOM, tNReproPOM, tPReproPOM, tCReproPOM
   
   _LOOP_BEGIN_
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. calculate and apply reproductive flux once per year                                                        !
   !================================================================================================================!
   _GET_GLOBAL_(self%id_Day,Day)                                                                                    ! get the simulation day
   _GET_(self%id_Day_last,Day_last)                                                                                 !
   _SET_DIAGNOSTIC_(self%id_Day_last_save,Day)                                                                      !
   _GET_(self%id_sFRes,sFRes)                                                                                       !
   tDReproPOM = 0.0_rk                                                                                              !
   tNReproPOM = 0.0_rk                                                                                              !
   tPReproPOM = 0.0_rk                                                                                              !
   tCReproPOM = 0.0_rk                                                                                              !
   if (sFRes > self%fResMax) sFRes = self%fResMax                                                                   !
   if ((self%qStage == 1 .OR. self%qStage == 3) .AND. Day >= self%cDayReprFish .AND. Day_last < self%cDayReprFish) then ! case reproduction
      if (sFRes > self%fResMin) then                                                                                !
         _GET_(self%id_sDFi,sDFi)                                                                                   !
         _GET_(self%id_sDSiz,sDSiz)                                                                                 !
         _GET_(self%id_sNFi,sNFi)                                                                                   !
         _GET_(self%id_sPFi,sPFi)                                                                                   !
         _GET_(self%id_sCFi,sCFi)                                                                                   !
         _GET_(self%id_FiJu_D,FiJu_D)                                                                               !
         _GET_(self%id_FiJu_N,FiJu_N)                                                                               !
         _GET_(self%id_FiJu_P,FiJu_P)                                                                               !
         _GET_(self%id_FiJu_C,FiJu_C)                                                                               !
         _GET_(self%id_FiJu_Res,FiJu_Res)                                                                           !
         _GET_(self%id_FiJu_Siz,FiJu_Siz)                                                                           !
         _GET_(self%id_DPOMpoolW,DPOMpoolW)                                                                         !
         _GET_(self%id_NPOMpoolW,NPOMpoolW)                                                                         !
         _GET_(self%id_PPOMpoolW,PPOMpoolW)                                                                         !
         _GET_(self%id_CPOMpoolW,CPOMpoolW)                                                                         !
         rPDFi = sPFi /(sDFi+NearZero)                                                                              !   calculate P:DW ratio
         rNDFi = sNFi /(sDFi+NearZero)                                                                              !   calculate N:DW ratio
         rCDFi = sCFi /(sDFi+NearZero)                                                                              !   calculate C:DW ratio
         rDReprFish = self%fGonad*(sFRes-self%fResmin)/(self%fResMax-self%fResMin)                                  !   calculate total resproduction investment fraction
         tDReprFish = sDFi*rDReprFish                                                                               !   calculate total resproduction investment
         tNReprFish = tDReprFish*rNDFi                                                                              !   
         tPReprFish = tDReprFish*rPDFi                                                                              !
         tCReprFish = tDReprFish*rCDFi                                                                              !
         FiJu_Res_new = (FiJu_Res + sFRes*rDReprFish*self%fReproFish)/(1._rk + rDReprFish*self%fReproFish)          !   calculate new juvenile reserve fraction
         FiJu_Siz_new = (FiJu_D+tDReprFish*self%fReproFish)/(FiJu_D/FiJu_Siz+tDReprFish*self%fReproFish/self%cDegg) !   calculate new juvenile mean size
         _SET_(self%id_sFRes,sFRes-tDReprFish/sDFi)                                                                 !
         _SET_(self%id_sDFi,sDFi-tDReprFish)                                                                        !
         _SET_(self%id_sNFi,sNFi-tNReprFish)                                                                        !
         _SET_(self%id_sPFi,sPFi-tPReprFish)                                                                        !
         _SET_(self%id_sCFi,sCFi-tCReprFish)                                                                        !
         _SET_(self%id_sDSiz,sDSiz-rDReprFish*sDSiz)                                                                !
         _SET_(self%id_FiJu_D,  FiJu_D+tDReprFish*self%fReproFish)                                                  !   update juvenile stage DW
         _SET_(self%id_FiJu_N,  FiJu_N+tNReprFish*self%fReproFish)                                                  !   update juvenile stage N
         _SET_(self%id_FiJu_P,  FiJu_P+tPReprFish*self%fReproFish)                                                  !   update juvenile stage P
         _SET_(self%id_FiJu_C,  FiJu_C+tCReprFish*self%fReproFish)                                                  !   update juvenile stage C
         _SET_(self%id_FiJu_Res,FiJu_Res_new)                                                                       !   update juvenile reserve DW
         _SET_(self%id_FiJu_Siz,FiJu_Siz_new)                                                                       !   update juvenile individual size DW
         _SET_(self%id_DPOMpoolW, DPOMpoolW+tDReprFish*(1.0_rk-self%fReproFish))                                    !   update dissolved organic matter DW water colum
         _SET_(self%id_NPOMpoolW, NPOMpoolW+tNReprFish*(1.0_rk-self%fReproFish))                                    !   update particulate organic N water column
         _SET_(self%id_PPOMpoolW, PPOMpoolW+tPReprFish*(1.0_rk-self%fReproFish))                                    !   update particulate organic P water column
         _SET_(self%id_CPOMpoolW, CPOMpoolW+tCReprFish*(1.0_rk-self%fReproFish))                                    !   update particulate organic C water column
         tDReproPOM = tDReprFish*(1.0_rk-self%fReproFish)                                                           !   diagnostic DPOMW from reproduction
         tNReproPOM = tNReprFish*(1.0_rk-self%fReproFish)                                                           !   diagnostic NPOMW from reproduction
         tPReproPOM = tPReprFish*(1.0_rk-self%fReproFish)                                                           !   diagnostic PPOMW from reproduction
         tCReproPOM = tCReprFish*(1.0_rk-self%fReproFish)                                                           !   diagnostic CPOMW from reproduction
      endif                                                                                                         !
   elseif (self%qTrans > 1) then                                                                                    !
      _SET_(self%id_sFRes,sFRes)                                                                                    !
   endif                                                                                                            !
   _SET_DIAGNOSTIC_(self%id_tDReproPOM,     tDReproPOM)                                                             !
   _SET_DIAGNOSTIC_(self%id_tNReproPOM,     tNReproPOM)                                                             !
   _SET_DIAGNOSTIC_(self%id_tPReproPOM,     tPReproPOM)                                                             !
   _SET_DIAGNOSTIC_(self%id_tCReproPOM,     tCReproPOM)                                                             !
   !================================================================================================================!
   _LOOP_END_   !!! END OF MODEL CODE:: 
end subroutine check_state

!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
!�� SUBROUTINE: CALCULATE OPTIMAL DIET BREATH                                                                                                                                                      ��
!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
subroutine calc_ODB(self,tDConsFiPreyPot,aFeedLvlPrey,incl,sDPrey,uFunTmFish,cClearPrey,fGutOccPrey,kDConsMax,fFeed,aFunVegPrey)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_fish), intent(in), target :: self
   real(rk),                          intent(in)          :: sDPrey(:),uFunTmFish,cClearPrey(:),fGutOccPrey(:),kDConsMax
   real(rk),optional,                 intent(in)          :: aFunVegPrey, fFeed
   real(rk),dimension(size(sDPrey)),  intent(out)         :: tDConsFiPreyPot
   real(rk),                          intent(out)         :: aFeedLvlPrey
   integer,dimension(size(sDPrey)),   intent(out)         :: incl
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)                           :: tDConsFiPreyPot_last, tDConsFiPreyPotTot, aFunVegPrey_in, fFeed_in
   real(rk),dimension(size(sDPrey))   :: PreyProf, tDConsFiPreyPot_temp
   integer                            :: i, maxid
   
   logical,dimension(size(sDPrey))    :: mask
   logical                            :: cease
   
   !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. determine macrophyte dependency, and calculate prey profitabilities                                        !
   !================================================================================================================!
   if(present(aFunVegPrey)) then                                                                                    !
       aFunVegPrey_in = aFunVegPrey                                                                                 !
   else                                                                                                             !
       aFunVegPrey_in = 1.0_rk                                                                                      !
   endif                                                                                                            !
   if(present(fFeed)) then                                                                                          !
       fFeed_in = fFeed                                                                                             !
   else                                                                                                             !
       fFeed_in = 1.0_rk                                                                                            !
   endif                                                                                                            !
   PreyProf = 1._rk/fGutOccPrey                                                                                     !
   mask(:) = .false.                                                                                                ! initialize mask (all positions are initially .false.) 
   cease = .false.                                                                                                  ! initialize flag for stopping the iterations
   tDConsFiPreyPot_temp(:) = 0.0_rk                                                                                 ! initialize temp consumption variable
   tDConsFiPreyPot_last = 0.0_rk                                                                                    ! initialize saved consumption variable
   incl(:) = 0                                                                                                      ! initially, no prey is included
   i = 0                                                                                                            ! initialize included prey array
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. iterate over prey, and calculate optimal diet breadth and prey consumption                                 !
   !================================================================================================================!
   do while ((i < size(sDPrey)) .and. (cease .eqv. .false.))                                                        ! while no stop flag and not yet through all prey   
       i = i + 1                                                                                                    !    update iteration counter
       maxid = maxloc(PreyProf,DIM=1,MASK=.not. mask)                                                               !    find most profitable of remaining prey
       mask(maxid) = .true.                                                                                         !    include that prey in consumption calculation
       incl(maxid) = 1                                                                                              !
       aFeedLvlPrey = aFunVegPrey_in*sum(cClearPrey*fGutOccPrey*sDPrey*incl)*fFeed_in/ &                            !    calculate feeding level using included prey
           (aFunVegPrey_in*sum(cClearPrey*fGutOccPrey*sDPrey*incl)*fFeed_in + uFunTmFish*kDConsMax)                 !
       tDConsFiPreyPot_temp=fFeed_in*aFunVegPrey_in*cClearPrey*sDPrey*incl*(1._rk-aFeedLvlPrey)                     ! calculate consumption of included prey
       tDConsFiPreyPotTot = sum(tDConsFiPreyPot_temp)                                                               !    sum up total consumption from included prey
       if (i > 1 .and. tDConsFiPreyPotTot < tDConsFiPreyPot_last) then                                              !    if new total consumption is lower than previous consumption
           cease = .true.                                                                                           !       stop iterating, and do not include latest prey
           incl(maxid) = 0                                                                                          !       exclude the current prey
       endif                                                                                                        !
       tDConsFiPreyPot_last = tDConsFiPreyPotTot                                                                    !    save current highest total consumption
   end do                                                                                                           !
   aFeedLvlPrey = aFunVegPrey_in*sum(incl*cClearPrey*fGutOccPrey*sDPrey)*fFeed_in/ &                                !    calculate final feeding level, ignoring not included prey
       (aFunVegPrey_in*sum(incl*cClearPrey*fGutOccPrey*sDPrey)*fFeed_in + uFunTmFish*kDConsMax)                     !
   tDConsFiPreyPot = fFeed_in*aFunVegPrey_in*incl*cClearPrey*sDPrey*(1._rk-aFeedLvlPrey)                            ! calculate final consumption of all prey, ignoring not included prey
   !================================================================================================================!
end subroutine calc_ODB
!����������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������������
end module wet_fish
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------