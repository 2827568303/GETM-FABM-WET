#include "fabm_driver.h"
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ MODULE: BIVALVES                                                                                                                                                                               §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
module wet_bivalves
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_expressions
   use fabm_particle
   
   implicit none
   private
   
   !PUBLIC FUNCTIONS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   public flength_weight_bivalve
   public ftemp_bivalve
   public fdens_bivalve
   public fSS_bivalve
   public fmortality_bivalve

   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model), public :: type_wet_bivalves
      ! local state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_bottom_state_variable_id)                            :: id_sDBiv, id_sPBiv, id_sNBiv, id_sCBiv
      type (type_bottom_state_variable_id)                            :: id_BivJu_D, id_BivJu_P, id_BivJu_N, id_BivJu_C, id_BivAd_D, id_BivAd_P, id_BivAd_N, id_BivAd_C
      type (type_state_variable_id)                                   :: id_sDBiv_PV, id_sPBiv_PV, id_sNBiv_PV, id_sCBiv_PV
      type (type_state_variable_id)                                   :: id_BivJu_D_PV, id_BivJu_P_PV, id_BivJu_N_PV,id_BivJu_C_PV, id_BivAd_D_PV, id_BivAd_P_PV, id_BivAd_N_PV, id_BivAd_C_PV
      ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_model_id),          allocatable, dimension(:) :: id_prey
      type (type_state_variable_id), allocatable, dimension(:) :: id_PreyD, id_PreyN, id_PreyP, id_PreyC
      type (type_dependency_id),     allocatable, dimension(:) :: id_PreySi
      type (type_state_variable_id)                            :: id_NPOMpoolW, id_PPOMpoolW, id_CPOMpoolW, id_SiPapoolW, id_DPOMpoolW, id_DDOMpoolW, id_NDOMpoolW, id_PDOMpoolW, id_SiO2poolW, id_NH4poolW, id_PO4poolW
      type (type_state_variable_id)                            :: id_DPOMpoolS_PV, id_NPOMpoolS_PV, id_PPOMpoolS_PV, id_CPOMpoolS_PV
      type (type_bottom_state_variable_id)                     :: id_DPOMpoolS, id_NPOMpoolS, id_PPOMpoolS, id_CPOMpoolS, id_SiPapoolS
      type (type_bottom_state_variable_id),  allocatable, dimension(:) :: id_BivSt_D
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDConsBivTot, id_tNConsBivTot, id_tPConsBivTot, id_tCConsBivTot, id_tDBivPOMS, id_tCBivPOMS, id_tCBivDOMS
      type (type_horizontal_diagnostic_variable_id), allocatable, dimension(:)   :: id_tDConsBiv, id_tPConsBiv, id_tNConsBiv, id_tCConsBiv
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDAssBiv,id_tNAssBiv,id_tPAssBiv,id_tCAssBiv,id_tDEgesBiv,id_tNEgesBiv,id_tPEgesBiv, id_tCEgesBiv,id_tDRespBiv,id_tCRespBiv,id_tNExcrBiv,id_tPExcrBiv
      type (type_horizontal_diagnostic_variable_id)                   :: id_tDMortBiv,id_tNMortBiv,id_tPMortBiv,id_tCMortBiv,id_tDAgeBiv,id_tNAgeBiv,id_tPAgeBiv,id_tCAgeBiv,id_tDReprBiv,id_tNReprBiv,id_tPReprBiv,id_tCReprBiv,id_tDpseudofaecesBiv
      type (type_horizontal_diagnostic_variable_id)                   :: id_f_food,id_f_temp,id_f_dens,id_f_SS,id_FR,id_f_DOmort,id_tSiO2EgestBiv, id_weight, id_Imax
      
      ! environmental dependencies identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_global_dependency_id)                         :: id_Day
      type (type_dependency_id)                                :: id_uTm, id_oxygen, id_sDIMW 
      type (type_horizontal_dependency_id)                     :: id_bot_pel_conv
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      real(rk)                                                        :: aL, cAw, cBw, cNDRef, cPDRef, cCDRef                                                                                        ! general parameters
      real(rk)                                                        :: kAi, cBi, fDAssBiv, hKfood, cTmin, cTminOpt, cTmaxOpt, cTmax                                                                ! ingestion parameters
      real(rk)                                                        :: cDmaxOpt, cDmax, cSSIMmaxOpt, cSSIMmax                                                                                      ! ingestion parameters 
      real(rk)                                                        :: kAr, cBr, cThetaResp                                                                                                        ! respiration parameters
      real(rk)                                                        :: fRegst, cgegst                                                                                                              ! egestion parameters
     ! real(rk)                                                        :: fRexcr                                                                                                                      ! excretion parameters
      real(rk)                                                        :: kmort, kbdo, hkdo                                                                                                           ! mortality parameters
      real(rk)                                                        :: cTempReprBiv, cDayReprBiv, fReprBiv, cDayAgeBiv, fAgeBiv, sDBivOS                                                           ! reproduction and aging parameters
      real(rk)                                                        :: tDConsBivTot, tNConsBivTot, tPConsBivTot, tCConsBivTot
      integer                                                         :: nPrey
      character(len=64),         allocatable, dimension(:)            :: prey_suffix
      real(rk),                  allocatable, dimension(:)            :: pref, tDConsBiv
      logical,                   allocatable, dimension(:)            :: lSi
      integer                                                         :: i_prey, i_stage, nKShares, qStageOpt
      logical                                                         :: diagnostics
 
   contains
   
   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure :: initialize
   procedure :: do_bottom
   
   end type type_wet_bivalves
   
   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: NearZero=0.000000000000000000000000000000001_rk

contains
    
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_bivalves),   intent(inout),    target :: self
   integer,                        intent(in)            :: configunit

   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer  :: i_prey, i_stage
   character(len=64)   :: index

   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! general parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%aL,              'aL',              'mm',       'bivalve length',                                           default=10.0_rk                                         )
   call self%get_parameter(self%cAw,             'cAw',             '-',        'constant 2 for length to total shell-on dry-weight conversion',                 default=2.766_rk                   )
   call self%get_parameter(self%cBw,             'cBw',             '-',        'constant 2 for length to total shell-on dry-weight conversion',                 default=9.472_rk                   )
   call self%get_parameter(self%cNDRef,          'cNDRef',          'gN/gDW',   'reference total body nitrogen to DW ratio ',               default=0.1_rk                                          )
   call self%get_parameter(self%cPDRef,          'cPDRef',          'gP/gDW',   'reference total body phosphorus to DW ratio ',             default=0.01_rk                                         )
   call self%get_parameter(self%cCDRef,          'cCDRef',          'gC/gDW',   'reference total body carbon to DW ratio',                  default=0.45_rk                                         )
   call self%get_parameter(self%kAi,             'kAi',             'g DW/g DW/d',  'maximum standard ingestion rate',                      default=0.003_rk,   scale_factor=1.0_rk/secs_pr_day     )
   call self%get_parameter(self%cBi,             'cBi',             '-',        'exponent for weight effect on ingestion',                  default=-0.39_rk                                        )
   ! ingestion and filtration parameters-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%fDAssBiv,        'fDAssBiv',          '-',      'fraction of filtered food that is assimilated',            default=0.34_rk                                         )
   call self%get_parameter(self%hKfood,          'hKfood',          'gDW/m3',   'saturation food concentration',                            default=5.0_rk                                          )
   call self%get_parameter(self%cTmin,           'cTmin',           '*C',       'minimum temperature threshold for onset of ingestion',     default=4.0_rk                                          )
   call self%get_parameter(self%cTminOpt,        'cTminOpt',        '*C',       'minimum temperature for optimal ingestion to occur',       default=12.0_rk                                         )
   call self%get_parameter(self%cTmaxOpt,        'cTmaxOpt',        '*C',       'maximum temperature for optimal ingestion to occur',       default=20.0_rk                                         )
   call self%get_parameter(self%cTmax,           'cTmax',           '*C',       'maximum temperature where ingestion stops',                default=31.0_rk                                         )
   call self%get_parameter(self%cDmaxOpt,        'cDmaxOpt',        'gDW/m2',   'maximum bivalves density for optimal ingestion to occur',  default=175.0_rk                                        )
   call self%get_parameter(self%cDmax,           'cDmax',           'gDW/m2',   'maximum bivalves density where ingestion stops',           default=550.0_rk                                        )
   call self%get_parameter(self%cSSIMmaxOpt,     'cSSIMmaxOpt',     'gDW/m3',   'maximum suspended (inorganic) solids concentration for optimal ingestion to occur',  default=20.0_rk               )
   call self%get_parameter(self%cSSIMmax,        'cSSIMmax',        'gDW/m3',   'maximum suspended (inorganic) solids concentration where ingestion stops',           default=100.0_rk              )
   ! respiration parameters-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%kAr,             'kAr',             '1/d',      'intercept for maximum standard respiration',               default=0.0019_rk,   scale_factor=1.0_rk/secs_pr_day    )
   call self%get_parameter(self%cBr,             'cBr',             '-',        'exponent for maximum standard respiration',                default=-0.25_rk                                        )
   call self%get_parameter(self%cThetaResp,      'cThetaResp',      '-',        'temperature multiplier for respiration',                   default=1.08_rk                                         )
   ! egestion parameters----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%fRegst,          'fRegst',             '-',     'minimum proportion egested as faeces',                     default=0.315_rk                                        )
   call self%get_parameter(self%cgegst,          'cgegst',             '-',     'gamma coefficient for egestions food availability dependence',   default=0.88_rk                                   )
   ! excretion parameters---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   !call self%get_parameter(self%fRexcr,          'fRexcr',             '-',     'excretion fraction of ingestion',                          default=0.0064_rk                                       )
   ! mortality parameters---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%kmort,           'kmort',             '1/d',    'mortality rate coefficient',                               default=0.0002_rk,   scale_factor=1.0_rk/secs_pr_day    )
   call self%get_parameter(self%kbdo,            'kbdo',             'g/m3',    'basal respiration rate',                                   default=5.0_rk                                          )
   call self%get_parameter(self%hKdo,            'hKdo',             'g/m3',    'half saturation constant for metabolic response to dissolved oxygen',      default=0.25_rk                         )
   ! reproduction and aging parameters--------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%qStageOpt,        'qStageOpt',      '-',        'stage coupling method: 0=nothing; 1=repro.; 2=maturation;',default=0                                               )
   call self%get_parameter(self%nKShares,         'nKShares',      '-',         'for qStageOpt > 0; # of not-coupled other stages sharing carr. cap.',  default=0                                   )
   if (self%qStageOpt > 0) then
       call self%get_parameter(self%cDayReprBiv, 'cDayReprBiv', 'day of year',  'earliest day-of-year where spawning may occur',          default=60.0_rk                                           )
       call self%get_parameter(self%cTempReprBiv,'cTempReprBiv', '*C',           'minimum water temperature at which spawning can occur', default=4.0_rk                                            )
       call self%get_parameter(self%fReprBiv,    'fReprBiv', '1/d',  'fraction of adult biomass which is transferred to juveniles during spawning',default=0.001_rk, scale_factor=1.0_rk/secs_pr_day)
       call self%get_parameter(self%cDayAgeBiv,  'cDayAgeBiv',  'day of year',  'day-of-year where aging of juveniles to adults occurs',              default=360.0_rk                              )
       call self%get_parameter(self%fAgeBiv,     'fAgeBiv', '1/d','fraction of juvenile biomass which is transferred to adult biomass through aging', default=0.001_rk, scale_factor=1.0_rk/secs_pr_day)
   endif
   if (self%nKShares > 0) then
      allocate(self%id_BivSt_D(self%nKShares))
      do i_stage = 1,self%nKShares
         write(index,'(i0)') i_stage
         call self%register_state_dependency(self%id_BivSt_D(i_stage),'otherStage'//trim(index),'g/m2', 'otherStage'//trim(index))
      end do
   endif
   ! food/prey parameters---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%nPrey,           'nPrey',           '-',        'number of prey types',                                     default=1                                               )                                                                                                                                                 
   allocate (self%pref(self%nPrey))
   allocate (self%lSi(self%nPrey))                                              
   allocate (self%prey_suffix(self%nPrey))
   do i_prey=1,self%nPrey                                                                                                                                                             
       write(index,'(i0)') i_prey                                                                                                                                                     
       call self%get_parameter(self%pref(i_prey),       'pref'//trim(index),       '-', 'preference for prey '//trim(index),                default=1.0_rk                                          ) 
       call self%get_parameter(self%lSi(i_prey),        'lSi'//trim(index),        '-', 'toggle prey silica tracking '//trim(index),        default=.false.                                         )
       call self%get_parameter(self%prey_suffix(i_prey),'prey_suffix'//trim(index),'-', 'prey name suffix '//trim(index),                   default=''                                              )
   end do
   ! diagnostics toggle------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,     'diagnostics',     '-',        'toggle diagnostic output',                                 default=.false.                                         )
   
   !REGISTER MODEL VARIABLES, DEPENDENCIES & COUPLINGS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! local state variables---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sDBiv,      'sD',      'gDW/m2',    'DW',          initial_value=1.0_rk,    minimum=0.0_rk                                                             )
   call self%register_state_variable(self%id_sNBiv,      'sN',      'gN/m2',     'N',           initial_value=0.1_rk,    minimum=0.0_rk                                                             )
   call self%register_state_variable(self%id_sPBiv,      'sP',      'gP/m2',     'P',           initial_value=0.01_rk,   minimum=0.0_rk                                                             )
   call self%register_state_variable(self%id_sCBiv,      'sC',      'gC/m2',     'C',           initial_value=0.40_rk,   minimum=0.0_rk                                                            )
   
   call self%register_state_variable(self%id_sDBiv_PV,   'sD_PV',   'gDW/m2',    'DW pel. var', initial_value=1.0_rk,    minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )                                      
   call self%register_state_variable(self%id_sNBiv_PV,   'sN_PV',   'gN/m2',     'N pel. var',  initial_value=0.01_rk,   minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )
   call self%register_state_variable(self%id_sPBiv_PV,   'sP_PV',   'gP/m2',     'P pel. var',  initial_value=0.1_rk,    minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )
   call self%register_state_variable(self%id_sCBiv_PV,   'sC_PV',   'gC/m2',     'C pel. var',  initial_value=0.40_rk,   minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )
   call self%set_variable_property(self%id_sDBiv_PV,     'disable_transport',    .true.                                                                                                             )   
   call self%set_variable_property(self%id_sNBiv_PV,     'disable_transport',    .true.                                                                                                             )
   call self%set_variable_property(self%id_sPBiv_PV,     'disable_transport',    .true.                                                                                                             )    
   call self%set_variable_property(self%id_sCBiv_PV,     'disable_transport',    .true.                                                                                                             )    
   
   if (self%qStageOpt == 1 .OR. self%qStageOpt == 3) then
       call self%register_state_dependency(self%id_BivJu_D,'juvenile_D','gDW/m2', 'juvenile D state')
       call self%register_state_dependency(self%id_BivJu_N,'juvenile_N','gN/m2', 'juvenile N state')
       call self%register_state_dependency(self%id_BivJu_P,'juvenile_P','gP/m2', 'juvenile P state')
       call self%register_state_dependency(self%id_BivJu_C,'juvenile_C','gC/m2', 'juvenile C state')
       call self%register_state_variable(self%id_BivJu_D_PV,   'sD_PV',   'gDW/m2',    'DW pel. var', initial_value=1.0_rk,    minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )                     
       call self%register_state_variable(self%id_BivJu_N_PV,   'sN_PV',   'gN/m2',     'N pel. var',  initial_value=0.01_rk,   minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )
       call self%register_state_variable(self%id_BivJu_P_PV,   'sP_PV',   'gP/m2',     'P pel. var',  initial_value=0.1_rk,    minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )                                   
       call self%register_state_variable(self%id_BivJu_C_PV,   'sC_PV',   'gC/m2',     'C pel. var',  initial_value=0.4_rk,    minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )                                   
       call self%set_variable_property(self%id_BivJu_D_PV,     'disable_transport',    .true.                                                                                                             )   
       call self%set_variable_property(self%id_BivJu_N_PV,     'disable_transport',    .true.                                                                                                             )
       call self%set_variable_property(self%id_BivJu_P_PV,     'disable_transport',    .true.                                                                                                             )    
       call self%set_variable_property(self%id_BivJu_C_PV,     'disable_transport',    .true.                                                                                                             )    
   endif
   
   if (self%qStageOpt == 2 .OR. self%qStageOpt == 3) then
       call self%register_state_dependency(self%id_BivAd_D,'adult_D','gDW/m2', 'adult D state')
       call self%register_state_dependency(self%id_BivAd_N,'adult_N','gDW/m2', 'adult N state')
       call self%register_state_dependency(self%id_BivAd_P,'adult_P','gDW/m2', 'adult P state')
       call self%register_state_dependency(self%id_BivAd_C,'adult_C','gDW/m2', 'adult C state')    
       call self%register_state_variable(self%id_BivAd_D_PV,   'sD_PV',   'gDW/m2',    'DW pel. var', initial_value=1.0_rk,    minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )                     
       call self%register_state_variable(self%id_BivAd_N_PV,   'sN_PV',   'gDW/m2',    'N pel. var',  initial_value=0.01_rk,   minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )
       call self%register_state_variable(self%id_BivAd_P_PV,   'sP_PV',   'gDW/m2',    'P pel. var',  initial_value=0.1_rk,    minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )                                   
       call self%register_state_variable(self%id_BivAd_C_PV,   'sC_PV',   'gDW/m2',    'C pel. var',  initial_value=0.4_rk,    minimum=0.0_rk, no_river_dilution=.TRUE., no_precipitation_dilution=.TRUE. )                                   
       call self%set_variable_property(self%id_BivAd_D_PV,     'disable_transport',    .true.                                                                                                             )   
       call self%set_variable_property(self%id_BivAd_N_PV,     'disable_transport',    .true.                                                                                                             )
       call self%set_variable_property(self%id_BivAd_P_PV,     'disable_transport',    .true.                                                                                                             )    
       call self%set_variable_property(self%id_BivAd_C_PV,     'disable_transport',    .true.                                                                                                             )    
   endif   
   
   ! register state variable dependencies------------------------------------------------------------------------------------------------------------------------------------------------------------
   allocate(self%id_prey(self%nPrey))
   allocate(self%id_PreyD(self%nPrey))
   allocate(self%id_PreyN(self%nPrey))
   allocate(self%id_PreyP(self%nPrey))
   allocate(self%id_PreyC(self%nPrey))
   allocate(self%id_PreySi(self%nPrey))
   allocate(self%id_tDConsBiv(self%nPrey))
   allocate(self%id_tNConsBiv(self%nPrey))
   allocate(self%id_tPConsBiv(self%nPrey))
   allocate(self%id_tCConsBiv(self%nPrey))
   
   do i_prey=1,self%nPrey
       write(index,'(i0)') i_prey
       call self%register_model_dependency(self%id_prey(i_prey), 'prey_model'//trim(index))
       call self%register_state_dependency(self%id_PreyD(i_prey), 'Prey_D_'//trim(index), 'g/m3', 'prey D'//trim(index))
       call self%register_state_dependency(self%id_PreyN(i_prey), 'Prey_N_'//trim(index), 'g/m3', 'prey N'//trim(index))
       call self%register_state_dependency(self%id_PreyP(i_prey), 'Prey_P_'//trim(index), 'g/m3', 'prey P'//trim(index))
       call self%register_state_dependency(self%id_PreyC(i_prey), 'Prey_C_'//trim(index), 'g/m3', 'prey C'//trim(index))
       call self%request_coupling_to_model(self%id_PreyD(i_prey),self%id_prey(i_prey), 'sD'//trim(self%prey_suffix(i_prey)))
       call self%request_coupling_to_model(self%id_PreyN(i_prey),self%id_prey(i_prey), 'sN'//trim(self%prey_suffix(i_prey)))
       call self%request_coupling_to_model(self%id_PreyP(i_prey),self%id_prey(i_prey), 'sP'//trim(self%prey_suffix(i_prey)))
       call self%request_coupling_to_model(self%id_PreyC(i_prey),self%id_prey(i_prey), 'sC'//trim(self%prey_suffix(i_prey)))
              
       if (self%lSi(i_prey)) then
           call self%register_dependency(self%id_PreySi(i_prey), 'Prey_Si_'//trim(index), 'g/m3', 'prey Si'//trim(index))
           call self%request_coupling_to_model(self%id_PreySi(i_prey),self%id_prey(i_prey), 'oSi'//trim(self%prey_suffix(i_prey)))
       endif       

       if (self%diagnostics) then
	       call self%register_diagnostic_variable(self%id_tDConsBiv(i_prey),'tDConsBiv_'//trim(index),'g/m2/s','consumption rate DW'//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tNConsBiv(i_prey),'tNConsBiv_'//trim(index),'g/m2/s','consumption rate N'//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tPConsBiv(i_prey),'tPConsBiv_'//trim(index),'g/m2/s','consumption rate P'//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tCConsBiv(i_prey),'tCConsBiv_'//trim(index),'g/m2/s','consumption rate C'//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       endif 
   end do
   
   call self%register_state_dependency(self%id_DPOMpoolS,    'POM_DW_pool_sediment',        'g/m2',   'particulate organic matter DW pool in sediment')
   call self%register_state_dependency(self%id_PPOMpoolS,    'POM_P_pool_sediment',         'g/m2',   'particulate organic matter P pool in sediment')
   call self%register_state_dependency(self%id_NPOMpoolS,    'POM_N_pool_sediment',         'g/m2',   'particulate organic matter N pool in sediment')
   call self%register_state_dependency(self%id_CPOMpoolS,    'POM_C_pool_sediment',         'g/m2',   'particulate organic matter C pool in sediment')
   call self%register_state_dependency(self%id_DPOMpoolS_PV, 'POM_DW_pool_sediment_PV',     'g/m2',   'particulate organic matter DW pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_CPOMpoolS_PV, 'POM_C_pool_sediment_PV',      'g/m2',   'particulate organic matter C pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_PPOMpoolS_PV, 'POM_P_pool_sediment_PV',      'g/m2',   'particulate organic matter P pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_NPOMpoolS_PV, 'POM_N_pool_sediment_PV',      'g/m2',   'particulate organic matter N pool in sediment pelagic mirror')
   call self%register_state_dependency(self%id_SiPapoolS,    'SiPa_pool_sediment',          'g/m2',   'particulate Si pool sediment')
      
   call self%register_state_dependency(self%id_DPOMpoolW,    'POM_DW_pool_water',           'g/m3',   'POM DW pool in water'     )
   call self%register_state_dependency(self%id_NPOMpoolW,    'POM_N_pool_water',            'g/m3',   'POM N pool in water'      )
   call self%register_state_dependency(self%id_PPOMpoolW,    'POM_P_pool_water',            'g/m3',   'POM P pool in water'      )
   call self%register_state_dependency(self%id_CPOMpoolW,    'POM_C_pool_water',            'g/m3',   'POM C pool in water'      )
   !call self%register_state_dependency(self%id_SiPapoolW,    'SiPa_pool_water',             'g/m3',   'particulate Si pool water')
   call self%register_state_dependency(self%id_NH4poolW,     'NH4_pool_water',              'g/m3',   'NH4 pool in water'        )
   call self%register_state_dependency(self%id_PO4poolW,     'PO4_pool_water',              'g/m3',   'PO4 pool in water'        )
   
   ! register environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(self%id_uTm,      standard_variables%temperature                                                                                                                   )
   call self%register_dependency(self%id_oxygen, 'oxygen_pool_water', 'g/m3', 'Oxygen pool water'                                                                                                   )
   call self%register_dependency(self%id_sDIMW,  'sDIMW',             'g/m3', 'inorganic matter'                                                                                                    )
   call self%register_dependency(self%id_Day,    standard_variables%number_of_days_since_start_of_the_year                                                                                          )
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor'                                                                              )
   
   ! register compulsary diagnostic variables--------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_tDBivPOMS,      'tDBivPOMS', 'g/m2/s', 'tDBivPOMS',  output=output_none,  domain=domain_bottom,source=source_do_bottom                            )
   
   ! register optional diagnostic variables----------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%diagnostics) then
       call self%register_diagnostic_variable(self%id_tDConsBivTot,   'tDConsBivTot','g/m2/s', 'total prey consumption DW', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tNConsBivTot,   'tNConsBivTot', 'g/m2/s','total prey consumption N',  output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tPConsBivTot,   'tPConsBivTot', 'g/m2/s','total prey consumption P',  output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tCConsBivTot,   'tCConsBivTot', 'g/m2/s','total prey consumption C',  output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_tDAssBiv,       'tDAssBiv',  'g/m2/s', 'assimilation rate DW',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom     )
       call self%register_diagnostic_variable(self%id_tNAssBiv,       'tNAssBiv',  'g/m2/s', 'assimilation rate N',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom     )
       call self%register_diagnostic_variable(self%id_tPAssBiv,       'tPAssBiv',  'g/m2/s', 'assimilation rate P',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom     )
       call self%register_diagnostic_variable(self%id_tCAssBiv,       'tCAssBiv',  'g/m2/s', 'assimilation rate C',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom     )
       call self%register_diagnostic_variable(self%id_tDEgesBiv,      'tDEgesBiv',  'g/m2/s', 'egestion rate DW ',  output=output_instantaneous, domain=domain_bottom,source=source_do_bottom        )
       call self%register_diagnostic_variable(self%id_tNEgesBiv,      'tNEgesBiv',  'g/m2/s', 'egestion rate N',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom         )
       call self%register_diagnostic_variable(self%id_tPEgesBiv,      'tPEgesBiv',  'g/m2/s', 'egestion rate P',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom         )
       call self%register_diagnostic_variable(self%id_tCEgesBiv,      'tCEgesBiv',  'g/m2/s', 'egestion rate C',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom         )
       call self%register_diagnostic_variable(self%id_tDRespBiv,      'tDRespBiv',  'g/m2/s', 'respiration rate DW',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom    )
       call self%register_diagnostic_variable(self%id_tNExcrBiv,      'tNExcrBiv',  'g/m2/s', 'excretion rate N',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom       )
       call self%register_diagnostic_variable(self%id_tPExcrBiv,      'tPExcrBiv',  'g/m2/s', 'excretion rate P',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom       )
       call self%register_diagnostic_variable(self%id_tCRespBiv,      'tCRespBiv',  'g/m2/s', 'respiration rate C',    output=output_instantaneous, domain=domain_bottom,source=source_do_bottom    )
       call self%register_diagnostic_variable(self%id_tDMortBiv,      'tDMortBiv',  'g/m2/s', 'mortality rate DW',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom      )
       call self%register_diagnostic_variable(self%id_tNMortBiv,      'tNMortBiv',  'g/m2/s', 'mortality rate N',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom       )
       call self%register_diagnostic_variable(self%id_tPMortBiv,      'tPMortBiv',  'g/m2/s', 'mortality rate P',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom       )
       call self%register_diagnostic_variable(self%id_tCMortBiv,      'tCMortBiv',  'g/m2/s', 'mortality rate C',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom       )
       call self%register_diagnostic_variable(self%id_tDAgeBiv,       'tDAgeBiv',  'g/m2/s',  'aging rate DW',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom          )
       call self%register_diagnostic_variable(self%id_tNAgeBiv,       'tNAgeBiv',  'g/m2/s',  'aging rate N',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom           )
       call self%register_diagnostic_variable(self%id_tPAgeBiv,       'tPAgeBiv',  'g/m2/s',  'aging rate P',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom           )
       call self%register_diagnostic_variable(self%id_tCAgeBiv,       'tCAgeBiv',  'g/m2/s',  'aging rate C',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom           )
       call self%register_diagnostic_variable(self%id_tDReprBiv,      'tDReprBiv',  'g/m2/s','reproduction rate DW',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom    )
       call self%register_diagnostic_variable(self%id_tNReprBiv,      'tNReprBiv',  'g/m2/s', 'reproduction rate N',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom    )
       call self%register_diagnostic_variable(self%id_tPReprBiv,      'tPReprBiv',  'g/m2/s', 'reproduction rate P',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom    )
       call self%register_diagnostic_variable(self%id_tCReprBiv,      'tCReprBiv',  'g/m2/s', 'reproduction rate C',   output=output_instantaneous, domain=domain_bottom,source=source_do_bottom    )
       call self%register_diagnostic_variable(self%id_tCBivPOMS,      'tCBivPOMS',  'g/m2/s','rate CPOMS',             output=output_instantaneous, domain=domain_bottom,source=source_do_bottom    )
       call self%register_diagnostic_variable(self%id_tDpseudofaecesBiv,'tDpseudofaecesBiv',  'g/m2/s','pseudofaeces production rate DW',output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)      
       call self%register_diagnostic_variable(self%id_f_food,      'f_food',    '-',      'limitation function for food',output=output_instantaneous, domain=domain_bottom,source=source_do_bottom     )
       call self%register_diagnostic_variable(self%id_f_temp,      'f_temp',    '-',    'limitation function for temperature', output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       call self%register_diagnostic_variable(self%id_f_dens,      'f_dens',    '-',      'limitation function for density',output=output_instantaneous, domain=domain_bottom,source=source_do_bottom  )
       call self%register_diagnostic_variable(self%id_f_SS,        'f_SS',      '-',      'limitation function for SS IM', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom   )
       call self%register_diagnostic_variable(self%id_f_DOmort,    'f_DOmort',  '/sec',      'mortality function DO', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom    )
       call self%register_diagnostic_variable(self%id_FR,          'FR',        'm3/gDW/s', 'water filtration rate', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom     )
       call self%register_diagnostic_variable(self%id_weight,      'weight',    'g DW', 'weight', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom                        )
       call self%register_diagnostic_variable(self%id_Imax,        'Imax',      'g DW/g DW/s', 'maximum potential ingestion rate', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
       !call self%register_diagnostic_variable(self%id_tSiO2EgestBiv,'tSiO2EgestBiv',      'g/m2/s', 'SiO2W egestion rate', output=output_instantaneous, domain=domain_bottom,source=source_do_bottom)
   endif
       
   ! Register contribution of state to global aggregate variables------------------------------------------------------------------------------------------------------------------------------------
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_tDPOMbio',units='gDW/m2/s',aggregate_variable=.true.),self%id_tDBivPOMS,scale_factor=1._rk                           ) 

   return

end subroutine initialize

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO BOTTOM                                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_bivalves), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   
   real(rk)                                                        :: sDBiv, sNBiv, sPBiv, sCBiv, rNDBiv, rPDBiv, rCDBiv, tDpseudofaecesBiv, tNpseudofaecesBiv, tPpseudofaecesBiv, tCpseudofaecesBiv
!   real(rk)                                                        :: BivJu_D_PV, BivJu_N_PV, BivJu_P_PV, BivAd_D_PV, BivAd_N_PV, BivAd_P_PV
   real(rk)                                                        :: uTm, Day, O2, sDIMW, bot_pel_conv, weight, Imax, total_food_DW, FR, f_temp, f_food, f_SS, f_dens, f_DOmort 
   real(rk)                                                        :: rNDFoodBiv, rPDFoodBiv, rCDFoodBiv 
   real(rk)                                                        :: aL, cAw, cBw, cNDRef, cPDRef, cCDRef                                                                                        ! general parameters
   real(rk)                                                        :: kAi, cBi, fDAssBiv, hKfood, cTmin, cTminOpt, cTmaxOpt, cTmax                                                                ! ingestion parameters 
   real(rk)                                                        :: cDmaxOpt, cDmax, cSSIMmaxOpt, cSSIMmax                                                                                      ! ingestion parameters
   real(rk)                                                        :: kAr, cBr, cThetaResp, tRespInd                                                                                                        ! respiration parameters
   real(rk)                                                        :: fRegst, cgegst                                                                                                              ! egestion parameters
   !real(rk)                                                        :: fRexcr                                                                                                                      ! excretion parameters
   real(rk)                                                        :: kmort, kbdo, hkdo                                                                                                           ! mortality parameters
   real(rk)                                                        :: cTempReprBiv, cDayReprBiv, fReprBiv, cDayAgeBiv, fAgeBiv, sDBivOS, sDBivSt, sDJu, sDAd                                      ! reproduction and aging parameters
   real(rk), dimension(self%nKShares)                              :: sDBivSt_all
   real(rk)                                                        :: tDConsBivTot, tNConsBivTot, tPConsBivTot, tCConsBivTot, tDAssBiv, tCAssBiv, afCAssBiv, afDAssBiv, afNAssBiv, tNAssBiv, afPAssBiv, tPAssBiv 
   real(rk)                                                        :: tDRespBiv, tCRespBiv, tNExcrBiv, tPExcrBiv, tDEgesBiv, tCEgesBiv, tNEgesBiv, tPEgesBiv, tDmortBiv,tCmortBiv,tNmortBiv, tPmortBiv
   real(rk)                                                        :: tDReprBiv,tCReprBiv, tNReprBiv, tPReprBiv, tDAgeBiv, tCAgeBiv,tNAgeBiv, tPAgeBiv, tDBivBiva, tCBivBiva, tNBivBiva, tPBivBiva
   real(rk)                                                        :: tCBivCO2S,tCBivTOMS,tDBivPOMW, tDBivPOMS,tCBivPOMW,tCBivPOMS,tNBivPOMW, tNBivPOMS, tPBivPOMW, tPBivPOMS, tNBivNH4W, tPBivPO4W, tSiO2BivS 
   logical                                                         :: lSi, reproduction_occurred 
   real(rk), dimension(self%nPrey)                                 :: sDprey, sNprey, sPprey, sCprey, rNDprey, rPDprey, rCDprey, sSiprey, food_DW,tDConsBiv,tCConsBiv, tNConsBiv, tPConsBiv, pref                                                        
   integer                                                         :: i_prey, i_stage, i, nKShares, qStageOpt                                                                                                                                
   character(len=64)                                               :: index                                                                                         

   _HORIZONTAL_LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
      ! 1.1 retrieve environmental dependencies                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _GET_(self%id_uTm,uTm)                                                                                        ! get local temperature
      _GET_(self%id_oxygen,O2)                                                                                      ! get local oxygen concentration
      _GET_(self%id_sDIMW,sDIMW)                                                                                    ! get local inorganic SS concentration
      _GET_GLOBAL_(self%id_Day,Day)                                                                                 ! get day of the year
      !=============================================================================================================!
      ! 1.2 retrieve state variables, & calc. current local nutrient ratios                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.2.1 bivalve state variables                                                                            !
         !----------------------------------------------------------------------------------------------------------!
         _GET_HORIZONTAL_(self%id_sDBiv,sDBiv)                                                                      ! get bivalves dry weight
         _GET_HORIZONTAL_(self%id_sNBiv,sNBiv)                                                                      ! get bivalves nitrogen
         _GET_HORIZONTAL_(self%id_sPBiv,sPBiv)                                                                      ! get bivalves phosphorous
         _GET_HORIZONTAL_(self%id_sCBiv,sCBiv)                                                                      ! get bivalves carbon
         rNDBiv=sNBiv/(sDBiv+NearZero)                                                                              ! calculate N:DW ratio
         rPDBiv=sPBiv/(sDBiv+NearZero)                                                                              ! calculate P:DW ratio
         rCDBiv=sCBiv/(sDBiv+NearZero)                                                                              ! calculate C:DW ratio
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.2.2 prey state variables                                                                               !
         !----------------------------------------------------------------------------------------------------------!
         total_food_DW = NearZero                                                                                   ! 
         do i_prey=1,self%nPrey                                                                                     ! for each prey
            _GET_(self%id_PreyD(i_prey),sDprey(i_prey))                                                             ! get prey dry weight (dimensions: nPrey)
            _GET_(self%id_PreyN(i_prey),sNprey(i_prey))                                                             ! get prey nitrogen (dimensions: nPrey)
            _GET_(self%id_PreyP(i_prey),sPprey(i_prey))                                                             ! get prey phosphorus (dimensions: nPrey)
            _GET_(self%id_PreyC(i_prey),sCprey(i_prey))                                                             ! get prey carbon (dimensions: nPrey)
            if (self%lSi(i_prey)) then                                                                              ! check whether silica is tracked
               _GET_(self%id_PreySi(i_prey),sSiprey(i_prey))                                                        !   get prey silica (dimensions: nPrey)
            else                                                                                                    !   if silica is not tracked
                sSiprey(i_prey) = 0.0_rk                                                                            !   then content is set to zero
            endif                                                                                                   !
       !     food_DW = sDprey(i_prey)*self%pref(i_prey)                                                             ! include preference for individual food items
            total_food_DW = total_food_DW + sDprey(i_prey)*self%pref(i_prey)
         end do                                                                                                     ! 
         rNDprey = sNprey/(sDprey+NearZero)                                                                         ! calculate prey N:DW ratios (dimensions: nPrey)
         rPDprey = sPprey/(sDprey+NearZero)                                                                         ! calculate prey P:DW ratios (dimensions: nPrey)
         rCDprey = sCprey/(sDprey+NearZero)                                                                         ! calculate prey C:DW ratios (dimensions: nPrey)
         total_food_DW = max(NearZero,total_food_DW)
       !  total_food_DW = sum(food_DW)                                                                               !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 1.2.3 get total bivalve concentration in case several stages are included                                ! sDBivOS MUST HOLD ALL STAGES
         !----------------------------------------------------------------------------------------------------------!
           sDBivOS = 0.0_rk                                                                                         ! initialize total biomass of other stages (juv. + adults + other stages in stage structure)
           if (self%qStageOpt == 1 .OR. self%qStageOpt == 3) then                                                   ! case younger stage present
               _GET_HORIZONTAL_(self%id_BivJu_D, sDJu)                                                              !   get younger stage biomass
               sDBivOS = sDBivOS + sDJu                                                                             !   add younger stage biomass to sDBivOS
           endif                                                                                                    !
           if (self%qStageOpt == 2 .OR. self%qStageOpt == 3) then                                                   ! case older stage present
               _GET_HORIZONTAL_(self%id_BivAd_D, sDAd)                                                              !   get older stage biomass
               sDBivOS = sDBivOS + sDAd                                                                             !   add older stage biomass to sDBivOS
           endif                                                                                                    !
           if (self%nKShares > 0) then                                                                              ! case other not-coupled stages with shared carrying capacity (needed for density dependence function)
               do i = 1,self%nKShares                                                                               !   for each other stage
                  _GET_HORIZONTAL_(self%id_BivSt_D(i), sDBivSt_all(i))                                              !     get other stage biomasse
               end do                                                                                               !
               sDBivSt = sum(sDBivSt_all)                                                                           !   sum other stage biomasse
               sDBivOS = sDBivOS + sDBivSt                                                                          !   add biomass to sDBivOS
           endif                                                                                                    !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!                                                          
   !  2. calculate size, ingestion and consumption (grazing) of DW, N, P and C                                      !                                                           
   !================================================================================================================!
      ! 2.1 bivalve size                                                                                            ! 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                          
      weight = flength_weight_bivalve(self%aL,self%cAw,self%cBw)                                                    ! calc. dry weight (g) of individual bivalve from length (mm)
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!  
      ! 2.2 maximum potential ingestion                                                                             ! 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                          
      Imax = self%kAi*weight**self%cBi                                                                              ! calc. Imax (g DW/g DW/s) 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!  
      ! 2.3 food limitation function                                                                                ! 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                          
      f_food = min(total_food_DW/self%hKfood,1.0)                                                                   ! calc. food limitation function (-)
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!  
      ! 2.4 temperature function                                                                                    ! 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                          
      f_temp = ftemp_bivalve(uTm, self%cTmin, self%cTminOpt, self%cTmaxOpt, self%cTmax)     ! calc. temperature adjustment for ingestion (-)
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::! 
      ! 2.5 density function                                                                                        ! 
      if (self%nKShares > 0) then                                                                                   ! 
         f_dens = fdens_bivalve(sDBivOS, self%cDmaxOpt, self%cDmax)                           ! calc. density correction for ingestion (-)
      else                                                                                                          !
         f_dens = fdens_bivalve(sDBiv, self%cDmaxOpt, self%cDmax)                             ! calc. density correction for ingestion (-) 
      endif                                                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                         
      ! 2.6 suspended (inorganic) solids function                                                                   ! 
      f_SS = fSS_bivalve(sDIMW, self%cSSIMmaxOpt, self%cSSIMmax)                              ! calc. SS correction for ingestion (-)
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                              
      !=============================================================================================================!
      ! 2.7 calculate prey consumption (grazing)                                                                    !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      do i_prey=1,self%nPrey                                                                                        ! for each prey type (inspired by ERGOM model preference factor implementation)
         tDConsBiv(i_prey) = (Imax*f_food*f_temp*f_dens*f_SS)*sDBiv*self%pref(i_prey)                               ! calculate consumption of all available food items (g DW/m2/s) (dimensions: nPrey)                                                                                                        
         tNConsBiv(i_prey) = tDConsBiv(i_prey) * rNDprey(i_prey)                                                    ! calculate prey N consumption (dimensions: nPrey)
         tPConsBiv(i_prey) = tDConsBiv(i_prey) * rPDprey(i_prey)                                                    ! calculate prey P consumption (dimensions: nPrey)
         tCConsBiv(i_prey) = tDConsBiv(i_prey) * rCDprey(i_prey)                                                    ! calculate prey C consumption (dimensions: nPrey)
      end do      
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 3. calculate total prey consumption (DW, N & P) and filtration rate                                            !
   !================================================================================================================!
      ! 3.1 calculate total consumption rates                                                                       ! 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                                
      tDConsBivTot = sum(tDConsBiv)                                                                                 ! calculate total prey DW consumption
      tNConsBivTot = sum(tNConsBiv)                                                                                 ! calculate total prey N consumption
      tPConsBivTot = sum(tPConsBiv)                                                                                 ! calculate total prey P consumption   
      tCConsBivTot = sum(tCConsBiv)                                                                                 ! calculate total prey C consumption   
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!  
      ! 3.2 calculate water filtration rate diagnostic                                                              ! 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!                                                          
      if (total_food_DW < self%hKfood) then                                                                         !
         FR = tDConsBivTot / (self%hKfood * self%fDAssBiv)                                                          ! water filtration rate (m3/g DW/s)
      else                                                                                                          !   
         FR = tDConsBivTot / (total_food_DW * self%fDAssBiv)                                                        !
      endif                                                                                                         !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 4. calculate DW, N, and P assimilation                                                                         !
   !================================================================================================================!
      ! 4.1 dry weight assimilation (ingestion)                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDAssBiv = self%fDAssBiv * tDConsBivTot                                                                       ! calculate total DW assimilation 
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!  
      ! 4.2 nitrogen                                                                                                !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      rNDFoodBiv = tNConsBivTot / max(NearZero,tDConsBivTot)                                                        ! calculate total available prey N ratio
      afNAssBiv = min(1.0_rk,self%cNDRef / max(NearZero,rNDFoodBiv) * self%fDAssBiv)                                ! calculate N assimilation efficiency
      tNAssBiv = afNAssBiv * tNConsBivTot                                                                           ! calculate N assimilation rate
      !=============================================================================================================!
      ! 4.3 phosphorus                                                                                              !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      rPDFoodBiv = tPConsBivTot / max(NearZero,tDConsBivTot)                                                        ! calculate total available prey P ratio
      afPAssBiv = min(1.0_rk,self%cPDRef / max(NearZero,rPDFoodBiv) * self%fDAssBiv)                                ! calculate P assimilation efficiency
      tPAssBiv = afPAssBiv * tPConsBivTot                                                                           ! calculate P assimilation rate
      !=============================================================================================================!
      ! 4.4 carbon                                                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      rCDFoodBiv = tCConsBivTot / max(NearZero,tDConsBivTot)                                                        ! calculate total available prey C ratio
      afCAssBiv = min(1.0_rk,self%cCDRef / max(NearZero,rCDFoodBiv) * self%fDAssBiv)                                ! calculate C assimilation efficiency
      tCAssBiv = afCAssBiv * tCConsBivTot                                                                           ! calculate C assimilation rate
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 5. calculate pseudofaeces, respiration, egestion and excretion                                                 !
   !================================================================================================================!
      ! 5.1 calculate pseudofaeces diagnostics                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDpseudofaecesBiv = (1.0 - self%fDAssBiv) * tDConsBivTot                                                      ! calculate pseudofaeces (in DW) diagnostic
      !tNpseudofaecesBiv = tDpsuedofaecesBiv * rNDprey                                                              ! calculate pseudofaeces N (assume ND ratio of food), note: rNDprey has i_prey dimensions and does not match tNpseudofaecesBiv
      !tPpseudofaecesBiv = tDpsuedofaecesBiv * rPDprey                                                              ! calculate pseudofaeces P (assume PD ratio of food)
      !tCpseudofaecesBiv = tDpsuedofaecesBiv * rCDprey                                                              ! calculate pseudofaeces C (assume CD ratio of food)
      ! 5.2 calculate respiration and excretion                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      ! aCorDRespBiv = max(self%cPDRef / rPDBiv,self%cNDRef / rNDBiv, self%cCDRef / rCDBiv)                         ! calculate corr. factor between respiration and P, N, C content
      tRespInd = self%cThetaResp**(uTm-20.0) * self%kAr*weight**self%cBr                                            ! calculate individual respiration (g DW/g DW mussel)
      tDRespBiv = tRespInd*sDBiv                                                                                    ! calculate respiration (g DW/m2)
      tCRespBiv = (rCDBiv / self%cCDRef) * tDRespBiv * sCBiv                                                        ! calculate C respiration
      tNExcrBiv = (rNDBiv / self%cNDRef) * tDRespBiv * sNBiv                                                        ! calculate N excretion (goes to NH4)
      tPExcrBiv = (rPDBiv / self%cPDRef) * tDRespBiv * sPBiv                                                        ! calculate P excretion (goes to PO4)
      !=============================================================================================================!
      ! 5.3 calculate egestion                                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
     ! tDEgesBiv = tDConsBivTot - tDAssBiv                                                                          ! just for reference, this is the zoobenthos approach for calculating DW egestion
      tDEgesBiv = tDAssBiv * self%fRegst * exp(self%cgegst*min(total_food_DW/self%hKfood,1.0))                      ! calculate DW egestion (goes to POM)
      tNEgesBiv = tDEgesBiv * rNDBiv                                                                                ! calculate N egestion (goes to POMN)
      tPEgesBiv = tDEgesBiv * rPDBiv                                                                                ! calculate P egestion (goes to POMP)     
      tCEgesBiv = tDEgesBiv * rCDBiv                                                                                ! calculate C egestion (goes to POMC)     
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 6. calculate mortality due to low oxygen levels                                                                !
   !================================================================================================================!
      ! 6.1 calculate mortality                                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      f_DOmort = fmortality_bivalve(O2, self%kmort, self%kbdo, self%hKdo)                                           !
      tDmortBiv = sDBiv*f_DOmort                                                                                    ! calculate POM DW produced from mortality
      tNmortBiv = tDmortBiv * rNDBiv                                                                                ! calculate mortality POMP 
      tPmortBiv = tDmortBiv * rPDBiv                                                                                ! calculate mortality POMN  
      tCmortBiv = tDmortBiv * rCDBiv                                                                                ! calculate mortality POMC  
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 7. optional (used if qStageOpt > 0): reproduction and aging exchange between bivalve instances                 !
   !================================================================================================================!
      ! 7.1 default case: no stages                                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDReprBiv = 0.0_rk                                                                                            ! initialize DW reproduction flux
      tPReprBiv = 0.0_rk                                                                                            ! initialize P reproduction flux
      tNReprBiv = 0.0_rk                                                                                            ! initialize N reproduction flux
      tCReprBiv = 0.0_rk                                                                                            ! initialize C reproduction flux
      tDAgeBiv = 0.0_rk                                                                                             ! initialize DW aging flux
      tPAgeBiv = 0.0_rk                                                                                             ! initialize P aging flux
      tNAgeBiv = 0.0_rk                                                                                             ! initialize N aging flux
      tCAgeBiv = 0.0_rk                                                                                             ! initialize C aging flux
      !=============================================================================================================!
      ! 7.2 case adult bivalve with reproduction                                                                    !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%qStageOpt == 1 .OR. self%qStageOpt == 3) then                                                        ! case reproduction
       !  if (Day == 1) then                                                                                        !  
       !     reproduction_occurred = .false.                                                                        ! set to false at the beginning of each year
       !  endif                                                                                                     !
         if (uTm >= self%cTempReprBiv) then                                                                         ! check if temperature is above minimum threshold
       !     if (Day >= self%cDayReprBiv .and. reproduction_occurred == .false.) then                               !  
               tDReprBiv = self%fReprBiv * sDBiv                                                                    !  
               tNReprBiv = rNDBiv * tDReprBiv                                                                       ! calculate reproduction N flux
               tPReprBiv = rPDBiv * tDReprBiv                                                                       ! calculate reproduction P flux
               tCReprBiv = rCDBiv * tDReprBiv                                                                       ! calculate reproduction C flux
       !        reproduction_occurred = .true.                                                                      ! set flag to true when spawning has occured for the year
       !     endif                                                                                                  !
         endif                                                                                                      !  
      endif                                                                                                         !
      !=============================================================================================================!
      ! 7.3 case juvenile bivalve with aging                                                                        !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%qStageOpt == 2 .OR. self%qStageOpt == 3) then                                                        ! case aging
        ! if (Day >= self%cDayAgeBiv .and. Day <= self%cDayAgeBiv + 1.0) then                                       ! 
             tDAgeBiv = self%fAgeBiv * sDBiv                                                                        ! 
             tNAgeBiv = rNDBiv * tDAgeBiv                                                                           ! calculate aging N flux
             tPAgeBiv = rPDBiv * tDAgeBiv                                                                           ! calculate aging P flux
             tCAgeBiv = rCDBiv * tDAgeBiv                                                                           ! calculate aging C flux
        ! endif                                                                                                     !
      endif                                                                                                         !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 8. final flux calculations                                                                                     !
   !================================================================================================================!
      ! 8.1 final bivalve rate of change                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDBivBiva = tDAssBiv - tDRespBiv - tDEgesBiv - tDMortBiv - tDAgeBiv - tDReprBiv                               ! calculate final rate of change of DW
      tNBivBiva = tNAssBiv - tNExcrBiv - tNEgesBiv - tNMortBiv - tNAgeBiv - tNReprBiv                               ! calculate final rate of change of N
      tPBivBiva = tPAssBiv - tPExcrBiv - tPEgesBiv - tPMortBiv - tPAgeBiv - tPReprBiv                               ! calculate final rate of change of P
      tCBivBiva = tCAssBiv - tCRespBiv - tCEgesBiv - tCMortBiv - tCAgeBiv - tCReprBiv                               ! calculate final rate of change of C
      !=============================================================================================================!
      ! 7.2 final fluxes to external abiotic variables                                                              !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 7.2.1 dry weight                                                                                         !
         !----------------------------------------------------------------------------------------------------------!
         tDBivPOMW = tDEgesBiv                                                                                      ! calculate total flux of DW to the water column
         tDBivPOMS = tDMortBiv                                                                                      ! calculate total flux of DW to the sediment
         !!:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         !! 7.2.2 nitrogen                                                                                          !
         !!---------------------------------------------------------------------------------------------------------!
         tNBivNH4W = tNExcrBiv                                                                                      ! calculate total flux of NH4 to the water column
         tNBivPOMW = tNEgesBiv                                                                                      ! calculate total flux of NPOM to the water column
         tNBivPOMS = tNMortBiv                                                                                      ! calculate total flux of NPOM to the sediment
         !!:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         !! 7.2.3 phosphorus                                                                                        !
         !!---------------------------------------------------------------------------------------------------------!
         tPBivPO4W = tPExcrBiv                                                                                      ! calculate total flux of PO4 to the water column 
         tPBivPOMW = tPEgesBiv                                                                                      ! calculate total flux of PPOM to the water column
         tPBivPOMS = tPMortBiv                                                                                      ! calculate total flux of PPOM to the sediment
         !!:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         !! 7.2.4 carbon!
         !!---------------------------------------------------------------------------------------------------------!
         tCBivCO2S = tCRespBiv                                                                                      ! calculate total CO2 flux to the sediment
         tCBivPOMW = tCEgesBiv                                                                                      ! calculate total organic C flux to water
         tCBivPOMS = tCMortBiv                                                                                      ! calculate total organic C flux to the sediment
         !!:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         !! 7.2.4 silica                                                                                            !
         !!---------------------------------------------------------------------------------------------------------!
         tSiO2BivS = sum((sSiprey/max(NearZero,sDprey)) * tDConsBiv)                                                ! flux of silica to the sediment due to bivalve feeding
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 8. update model variables                                                                                      !
   !================================================================================================================!
      ! 8.1 update local state variables                                                                            !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_ODE_(self%id_sDBiv,tDBivBiva)                                                                     ! update bivalves DW ODE
      _SET_BOTTOM_ODE_(self%id_sNBiv,tNBivBiva)                                                                     ! update bivalves N ODE
      _SET_BOTTOM_ODE_(self%id_sPBiv,tPBivBiva)                                                                     ! update bivalves P ODE
      _SET_BOTTOM_ODE_(self%id_sCBiv,tCBivBiva)                                                                     ! update bivalves C ODE
      _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)                                                           ! 
      _SET_BOTTOM_EXCHANGE_(self%id_sDBiv_PV,tDBivBiva*bot_pel_conv)                                                ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      _SET_BOTTOM_EXCHANGE_(self%id_sNBiv_PV,tNBivBiva*bot_pel_conv)                                                ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      _SET_BOTTOM_EXCHANGE_(self%id_sPBiv_PV,tPBivBiva*bot_pel_conv)                                                ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      _SET_BOTTOM_EXCHANGE_(self%id_sCBiv_PV,tCBivBiva*bot_pel_conv)                                                ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      !=============================================================================================================!
      ! 8.2 update external biotic state variables                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      do i_prey = 1,self%nPrey                                                                                      ! 
         _SET_BOTTOM_EXCHANGE_(self%id_PreyD(i_prey),-tDConsBiv(i_prey))                                            !   update prey DW ODEs
         _SET_BOTTOM_EXCHANGE_(self%id_PreyN(i_prey),-tNConsBiv(i_prey))                                            !   update prey N ODEs
         _SET_BOTTOM_EXCHANGE_(self%id_PreyP(i_prey),-tPConsBiv(i_prey))                                            !   update prey P ODEs
         _SET_BOTTOM_EXCHANGE_(self%id_PreyC(i_prey),-tCConsBiv(i_prey))                                            !   update prey C ODEs
      end do                                                                                                        ! 
      !=============================================================================================================!
      ! 8.3 update external abiotic state variables                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolW,  tDBivPOMW)                                                          ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolW,  tNBivPOMW)                                                          ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolW,  tPBivPOMW)                                                          ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolW,  tCBivPOMW)                                                          ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_NH4poolW,  tNBivNH4W)                                                           ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_PO4poolW,  tPBivPO4W)                                                           ! update the abiotic variables      
      _SET_BOTTOM_ODE_(self%id_DPOMpoolS, tDBivPOMS)                                                                ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_NPOMpoolS, tNBivPOMS)                                                                ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_PPOMpoolS, tPBivPOMS)                                                                ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_CPOMpoolS, tCBivPOMS)                                                                ! update the abiotic variables
      _SET_BOTTOM_ODE_(self%id_SiPapoolS, tSiO2BivS)                                                                ! update the abiotic variables
      !_SET_BOTTOM_ODE_(self%id_CO2poolS,  tCBivCO2S)                                                               ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_DPOMpoolS_PV, tDBivPOMS*bot_pel_conv)                                           ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_NPOMpoolS_PV, tNBivPOMS*bot_pel_conv)                                           ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_PPOMpoolS_PV, tPBivPOMS*bot_pel_conv)                                           ! update the abiotic variables
      _SET_BOTTOM_EXCHANGE_(self%id_CPOMpoolS_PV, tCBivPOMS*bot_pel_conv)                                           ! update the abiotic variables
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      ! 8.4 update other life stages (optional, only used if qStageOpt > 0)                                         !
      !-------------------------------------------------------------------------------------------------------------!
      if (self%qStageOpt == 1 .OR. self%qStageOpt == 3) then                                                        ! case reproduction
         _SET_BOTTOM_ODE_(self%id_BivJu_D,  tDReprBiv)                                                              !   update juvenile stage DW ODE
         _SET_BOTTOM_ODE_(self%id_BivJu_N,  tNReprBiv)                                                              !   update juvenile stage N ODE
         _SET_BOTTOM_ODE_(self%id_BivJu_P,  tPReprBiv)                                                              !   update juvenile stage P ODE
         _SET_BOTTOM_ODE_(self%id_BivJu_C,  tCReprBiv)                                                              !   update juvenile stage C ODE
         _SET_BOTTOM_EXCHANGE_(self%id_BivJu_D_PV,tDReprBiv*bot_pel_conv)                                           ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_BivJu_N_PV,tNReprBiv*bot_pel_conv)                                           ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_BivJu_P_PV,tPReprBiv*bot_pel_conv)                                           ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_BivJu_C_PV,tCReprBiv*bot_pel_conv)                                           ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      endif                                                                                                         !
      if (self%qStageOpt == 2 .OR. self%qStageOpt == 3) then                                                        ! case aging
         _SET_BOTTOM_ODE_(self%id_BivAd_D,  tDAgeBiv)                                                               !   update older stage DW ODE
         _SET_BOTTOM_ODE_(self%id_BivAd_N,  tNAgeBiv)                                                               !   update older stage N ODE
         _SET_BOTTOM_ODE_(self%id_BivAd_P,  tPAgeBiv)                                                               !   update older stage P ODE
         _SET_BOTTOM_ODE_(self%id_BivAd_C,  tCAgeBiv)                                                               !   update older stage C ODE
         _SET_BOTTOM_EXCHANGE_(self%id_BivAd_D_PV,tDAgeBiv*bot_pel_conv)                                            ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_BivAd_N_PV,tNAgeBiv*bot_pel_conv)                                            ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_BivAd_P_PV,tPAgeBiv*bot_pel_conv)                                            ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_BivAd_C_PV,tCAgeBiv*bot_pel_conv)                                            ! update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      endif                                                                                                         ! 
      !=============================================================================================================!
      ! 8.4 update compulsary diagnostic variables                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBivPOMS,tDBivPOMS)                                                      ! update the production of particulate organic matter (for calculating burial)
      !=============================================================================================================!
      ! 8.5 update optional diagnostic variables                                                                    !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDConsBivTot, tDConsBivTot)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNConsBivTot, tNConsBivTot)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPConsBivTot, tPConsBivTot)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCConsBivTot, tCConsBivTot)                                           !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDAssBiv,     tDAssBiv)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNAssBiv,     tNAssBiv)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPAssBiv,     tPAssBiv)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCAssBiv,     tCAssBiv)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDEgesBiv,    tDEgesBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNEgesBiv,    tNEgesBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPEgesBiv,    tPEgesBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCEgesBiv,    tCEgesBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDRespBiv,    tDRespBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCRespBiv,    tCRespBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNExcrBiv,    tNExcrBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPExcrBiv,    tPExcrBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDMortBiv,    tDMortBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCMortBiv,    tCMortBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNMortBiv,    tNMortBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPMortBiv,    tPMortBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDAgeBiv,     tDAgeBiv)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNAgeBiv,     tNAgeBiv)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPAgeBiv,     tPAgeBiv)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCAgeBiv,     tCAgeBiv)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDReprBiv,    tDReprBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNReprBiv,    tNReprBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPReprBiv,    tPReprBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCReprBiv,    tCReprBiv)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDpseudofaecesBiv, tDpseudofaecesBiv)                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCBivPOMS,    tCBivPOMS)                                              !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_f_food,       f_food)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_f_temp,       f_temp)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_f_dens,       f_dens)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_f_SS,         f_SS)                                                   ! 
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_f_DOmort,     f_DOmort)                                               !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_weight,       weight)                                                 !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_Imax,         Imax)                                                   !
          _SET_HORIZONTAL_DIAGNOSTIC_(self%id_FR,         FR)                                                       !
          !_SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiO2EgestBiv,   tSiO2BivS)                                          !
          do i_prey = 1,self%nPrey                                                                                  !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDConsBiv(i_prey), tDConsBiv(i_prey))                              !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNConsBiv(i_prey), tNConsBiv(i_prey))                              !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPConsBiv(i_prey), tPConsBiv(i_prey))                              !
             _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCConsBiv(i_prey), tCConsBiv(i_prey))                              !
		  end do                                                                                                    !
      endif                                                                                                         !
      !=============================================================================================================!
   _HORIZONTAL_LOOP_END_ !!! END OF MAIN MODEL CODE

end subroutine do_bottom

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
! Functions for the dependency of bivalve ingestion, respiration and mortality on temperature, suspended solids, bivalve density, and oxygen concentration 
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§


!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
! bivalve weight function
pure real(rk) function flength_weight_bivalve(aL,cAw,cBw)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk), intent(in)                :: aL,cAw,cBw
   real(rk)                            :: bivalve_weight
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. function code                                                                                              !
   !================================================================================================================!
   ! Compute respiration rate coefficient from length
   !bivalve_weight = cAw*aL**cBw
   bivalve_weight = exp((cAw*log(aL)-cBw))
   flength_weight_bivalve = bivalve_weight
   !================================================================================================================!
end function flength_weight_bivalve


!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
! bivalve temperature limitation function
pure real(rk) function ftemp_bivalve(uTm, cTmin, cTminOpt, cTmaxOpt, cTmax)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk), intent(in)                :: uTm, cTmin, cTminOpt, cTmaxOpt, cTmax
   real(rk)                            :: a
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. function code                                                                                              !
   !================================================================================================================!

   a = 1

   ! If temp below extreme, temp fn = 0, ie filtration ceases
   if (uTm <= cTmin) then 
      ftemp_bivalve = 0.0
      
   ! If below min temp for optimal range, limited as below
   elseif (uTm>cTmin .and. uTm<cTminOpt) then
      ftemp_bivalve = a*(1.0/(-((cTminOpt - cTmin) * (cTminOpt - cTmin)/  &
                       (cTminOpt * cTminOpt)) + (2.0*( cTminOpt - cTmin)/   &
                       cTminOpt)))*(-((uTm- cTmin)*(uTm - cTmin)/(cTminOpt * cTminOpt))  &
                       + 2.0*((uTm - cTmin)/cTminOpt))
   
   ! If between cTminOpt and cTmaxOpt, ie in the optimal temp range, then not limited
   elseif (uTm >=cTminOpt .and. uTm<=cTmaxOpt) then
      ftemp_bivalve = a
   
   ! If above max temp for optimal range, limited as below
   elseif (uTm>cTmaxOpt .and. uTm <cTmax) then
      ftemp_bivalve = a*((-(uTm * uTm) + 2.0*(cTmaxOpt * uTm) - 2.0*(cTmaxOpt * cTmax) &
                 + ( cTmax * cTmax))/ ((cTmaxOpt - cTmax)*         &
                 ( cTmaxOpt - cTmax)))
   
   ! If temp above extreme, temp fn = 0, ie filtration ceases
   elseif (uTm>=cTmax) then
       ftemp_bivalve = 0.0
   endif

end function ftemp_bivalve
   

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
! bivalve density limitation function
pure real(rk) function fdens_bivalve(sDBiv, cDmaxOpt, cDmax)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk), intent(in)                :: sDBiv, cDmaxOpt, cDmax

   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. function code                                                                                              !
   !================================================================================================================!
   
   if (sDBiv <= cDmaxOpt) then
      fdens_bivalve = 1.0
   elseif (sDBiv>cDmaxOpt .and. sDBiv<cDmax) then
      fdens_bivalve = (-sDBiv ** 2 + 2 * cDmaxOpt * sDBiv - 2 * cDmaxOpt * cDmax + cDmax ** 2) / &
               ((cDmaxOpt - cDmax) ** 2)
   else
      fdens_bivalve = 0.0
   endif

end function fdens_bivalve


!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
! bivalve suspended (inorganic) solids limitation function
pure real(rk) function fSS_bivalve(sDIMW, cSSIMmaxOpt, cSSIMmax)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk), intent(in)                :: sDIMW, cSSIMmaxOpt, cSSIMmax

   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. function code                                                                                              !
   !================================================================================================================!
   
   if (sDIMW <= cSSIMmaxOpt) then
      fSS_bivalve = 1.0
   elseif (sDIMW>cSSIMmaxOpt .and. sDIMW<cSSIMmax) then
      fSS_bivalve = (-sDIMW ** 2 + 2 * cSSIMmaxOpt * sDIMW - 2 * cSSIMmaxOpt * cSSIMmax + cSSIMmax ** 2) / &
               ((cSSIMmaxOpt - cSSIMmax) ** 2)
   else
      fSS_bivalve  = 0.0
   endif

end function fSS_bivalve 

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
! bivalve mortality function
pure real(rk) function fmortality_bivalve(O2, kmort, kbdo, hKdo)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk), intent(in)                :: O2, kmort, kbdo, hKdo
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. function code                                                                                              !
   !================================================================================================================!
   fmortality_bivalve = kmort * (1 + kbdo * (hKdo / (hKdo + O2)))

end function fmortality_bivalve 

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§

end module wet_bivalves

!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------