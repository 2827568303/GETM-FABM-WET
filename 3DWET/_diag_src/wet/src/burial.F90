#include "fabm_driver.h"
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ MODULE: SEDIMENT BURIAL                                                                                                                                                                        §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
module wet_burial
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_expressions
   use fabm_particle
   use wet_utility, ONLY: uFunTmArrh,uFunTmGaus
   implicit none
   private
   
   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public :: type_wet_burial
      ! state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_bottom_state_variable_id)                           :: id_WSPO4,id_WSPAIM,id_WSNH4,id_WSNO3, id_WSSiPa
      type (type_bottom_state_variable_id)                           :: id_WSDIM, id_WSDHum,id_WSNHum,id_WSPHum, id_WSDDOM, id_WSPDOM, id_WSNDOM, id_WSCHum, id_WSCDOM
      type (type_state_variable_id)                                  :: id_WSDHum_PV, id_WSNHum_PV, id_WSPHum_PV, id_WSCHum_PV
      ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_model_id),                 allocatable, dimension(:) :: id_pom, id_dom, id_pomx
      type (type_bottom_state_variable_id), allocatable, dimension(:) :: id_POMD, id_POMN, id_POMP, id_POMC, id_DOMD, id_DOMN, id_DOMP, id_DOMC
      type (type_state_variable_id),        allocatable, dimension(:) :: id_POMD_PV, id_POMN_PV, id_POMP_PV, id_POMC_PV, id_DOMD_PV, id_DOMN_PV, id_DOMP_PV, id_DOMC_PV
      ! environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                  :: id_VDeltaS
      type(type_horizontal_dependency_id)                            :: id_tDPOMbio
      ! diagnostic variables-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_dependency_id)                           :: id_tDAbioHumS, id_tDAbioIMS, id_bPorS, id_cDepthS, id_bot_pel_conv, id_tDAbioPOMS
      type (type_horizontal_dependency_id), allocatable, dimension(:):: id_tDPOMS_Phyt, id_tDPOMS_Bent, id_tDPOMS_Macro, id_tDPOMS_POM, id_tDReSedPOMS
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id)                  :: id_tDBurIM,  id_tSiBurPa, id_tPBurPO4, id_tPBurAIM
      type (type_horizontal_diagnostic_variable_id)                  :: id_tNBurNH4, id_tNBurNO3, id_tDBurHum, id_tPBurHum, id_tNBurHum, id_tCBurHum
      type (type_horizontal_diagnostic_variable_id), allocatable, dimension(:)  :: id_tDBurPOM, id_tPBurPOM, id_tNBurPOM, id_tCBurPOM, id_tDBurDOM, id_tPBurDOM, id_tNBurDOM, id_tCBurDOM
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      logical    :: diagnostics
      real(rk)   :: cRhoIM, cRhoOM, fDOrgSoil, cPO4Ground, cNH4Ground, cNO3Ground
      integer    :: nPHYT, nMACRO, nBENT, nPOM, nDOM, nPOMexch 
      
   contains

   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure ::  initialize
   procedure ::  do_bottom
   
   end type type_wet_burial

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk),parameter :: secs_pr_day=86400.0_rk

contains

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_burial), intent(inout), target :: self
   integer,                 intent(in)            :: configunit

   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer  :: i_spec
   character(len=64)   :: index
   
   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%get_parameter(self%cRhoIM,       'cRhoIM',       'g/m3',      'density of sediment inorganic matter', default=2500000.0_rk   )
   call self%get_parameter(self%cRhoOM,       'cRhoOM',       'g/m3',      'density of sediment organic matter',   default=1400000.0_rk   )
   call self%get_parameter(self%fDOrgSoil,    'fDOrgSoil',    '-',         'deep sediment organic matter fraction',default=0.1_rk         )
   call self%get_parameter(self%cPO4Ground,   'cPO4Ground',   'mgP/l',     'PO4 concentration in groundwater',     default=0.1_rk         )
   call self%get_parameter(self%cNH4Ground,   'cNH4Ground',   'mgN/l',     'NH4 concentration in groundwater',     default=1.0_rk         )
   call self%get_parameter(self%cNO3Ground,   'cNO3Ground',   'mgN/l',     'NO3 concentration in groundwater',     default=0.1_rk         )
   call self%get_parameter(self%nPHYT,        'nPHYT',        '-',         'number of phytoplankton instances',    default=0              )
   call self%get_parameter(self%nMACRO,       'nMACRO',       '-',         'number of macrophyte instances',       default=0              )
   call self%get_parameter(self%nBENT,        'nBENT',        '-',         'number of zoobenthos instances',       default=0              )
   call self%get_parameter(self%nPOM,         'nPOM',         '-',         'number of benthic particulate OM instances',default=0         )
   call self%get_parameter(self%nPOMexch,     'nPOMexch',     '-',         'number of resuspended benthic  POM instances',default=0       )
   call self%get_parameter(self%nDOM,         'nDOM',         '-',         'number of benthic dissolved OM instances',  default=0         )
   ! diagnostic  parameter--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,'diagnostics',    '-',         'toggle diagnostic output',             default=.false.        )
   
   !REGISTER MODEL VARIBLES, DEPENDENCIES & COUPLINGS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! register state variable dependencies------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_dependency(        self%id_WSNH4,         'NH4_pool_in_sediment',              'g/m2',                    'NH4 pool in sediment'                )
   call self%register_state_dependency(        self%id_WSNO3,         'NO3_pool_in_sediment',              'g/m2',                    'NO3 pool in sediment'                )
   call self%register_state_dependency(        self%id_WSPO4,         'PO4_pool_in_sediment',              'g/m2',                    'PO4 pool in sediment'                )
   call self%register_state_dependency(        self%id_WSPAIM,        'PAIM_in_sediment',                  'g/m2',                    'adsorbed phosphorus in sediment'     )
   call self%register_state_dependency(        self%id_WSDIM,         'inorg_pool_in_sediment',            'g/m2',                    'inorganic matter pool in sediment'   )
   call self%register_state_dependency(        self%id_WSDHum,        'humus_DW_in_deep_sediment',         'g/m2',                    'humus DW in deep sediment'           )
   call self%register_state_dependency(        self%id_WSNHum,        'humus_N_in_deep_sediment',          'g/m2',                    'humus N in deep sediment'            )
   call self%register_state_dependency(        self%id_WSPHum,        'humus_P_in_deep_sediment',          'g/m2',                    'humus P in deep sediment'            )
   call self%register_state_dependency(        self%id_WSCHum,        'humus_C_in_deep_sediment',          'g/m2',                    'humus C in deep sediment'            )
   call self%register_state_dependency(        self%id_WSDHum_PV,     'humus_DW_in_deep_sediment_PV',      'g/m2',                    'humus DW in deep sediment pelagic mirror')
   call self%register_state_dependency(        self%id_WSNHum_PV,     'humus_N_in_deep_sediment_PV',       'g/m2',                    'humus N in deep sediment pelagic mirror')
   call self%register_state_dependency(        self%id_WSPHum_PV,     'humus_P_in_deep_sediment_PV',       'g/m2',                    'humus P in deep sediment pelagic mirror')
   call self%register_state_dependency(        self%id_WSCHum_PV,     'humus_C_in_deep_sediment_PV',       'g/m2',                    'humus C in deep sediment pelagic mirror')
   call self%register_state_dependency(        self%id_WSSiPa,        'particulate_Si_in_sediment',        'g/m2',                    'Particulate Si in sediment'          )
   ! register other dependencies---------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(              self%id_tDAbioIMS,     'IM_abiotic_update',                 'g/m2/s',                  'IM abiotic update'                   )
   call self%register_horizontal_dependency(   self%id_bPorS,         'bPorS',                             'm3/m3',                   'sediment porosity'                   )
   call self%register_horizontal_dependency(   self%id_cDepthS,       'cDepthS',                           'm',                       'sediment depth'                      )

   allocate(self%id_tDPOMS_Phyt(self%nPHYT))
   allocate(self%id_tDPOMS_Bent(self%nBENT))
   allocate(self%id_tDPOMS_Macro(self%nMACRO))
   allocate(self%id_tDPOMS_POM(self%nPOM))
   allocate(self%id_tDReSedPOMS(self%nPOMexch))
   allocate(self%id_pom(self%nPOM))
   allocate(self%id_POMD(self%nPOM))
   allocate(self%id_POMP(self%nPOM))
   allocate(self%id_POMN(self%nPOM))
   allocate(self%id_POMC(self%nPOM))
   allocate(self%id_POMD_PV(self%nPOM))
   allocate(self%id_POMP_PV(self%nPOM))
   allocate(self%id_POMN_PV(self%nPOM))
   allocate(self%id_POMC_PV(self%nPOM))
   allocate(self%id_dom(self%nDOM))
   allocate(self%id_DOMD(self%nDOM))
   allocate(self%id_DOMP(self%nDOM))
   allocate(self%id_DOMN(self%nDOM))
   allocate(self%id_DOMC(self%nDOM))
   allocate(self%id_DOMD_PV(self%nDOM))
   allocate(self%id_DOMP_PV(self%nDOM))
   allocate(self%id_DOMN_PV(self%nDOM))
   allocate(self%id_DOMC_PV(self%nDOM))
   allocate(self%id_tDBurPOM(self%nPOM))   
   allocate(self%id_tNBurPOM(self%nPOM))   
   allocate(self%id_tPBurPOM(self%nPOM))   
   allocate(self%id_tCBurPOM(self%nPOM))   
   allocate(self%id_tDBurDOM(self%nDOM))   
   allocate(self%id_tNBurDOM(self%nDOM))   
   allocate(self%id_tPBurDOM(self%nDOM))   
   allocate(self%id_tCBurDOM(self%nDOM))   
   do i_spec=1,self%nPHYT
       write(index,'(i0)') i_spec
       call self%register_horizontal_dependency(self%id_tDPOMS_Phyt(i_spec), 'POM_phytoplankton_update'//trim(index),'g/m2/s','POM phytoplankton update'//trim(index))
   end do
   do i_spec=1,self%nBENT
       write(index,'(i0)') i_spec
       call self%register_horizontal_dependency(self%id_tDPOMS_Bent(i_spec), 'POM_zoobenthos_update'//trim(index),'g/m2/s','POM zoobenthos update'//trim(index))
   end do
   do i_spec=1,self%nMACRO
       write(index,'(i0)') i_spec
       call self%register_horizontal_dependency(self%id_tDPOMS_Macro(i_spec), 'POM_macrophyte_update'//trim(index),'g/m2/s','POM macrophyte update'//trim(index))
   end do
   ! tka: POM
   do i_spec=1,self%nPOM
       write(index,'(i0)') i_spec
       call self%register_model_dependency(self%id_pom(i_spec),   'POM_group'//trim(index))
       call self%register_state_dependency(self%id_POMD(i_spec),  'POM_D_'//trim(index), 'g/m2', 'POM D '//trim(index))
       call self%register_state_dependency(self%id_POMN(i_spec),  'POM_N_'//trim(index), 'g/m2', 'POM N '//trim(index))
       call self%register_state_dependency(self%id_POMP(i_spec),  'POM_P_'//trim(index), 'g/m2', 'POM P '//trim(index))
       call self%register_state_dependency(self%id_POMC(i_spec),  'POM_C_'//trim(index), 'g/m2', 'POM C '//trim(index))
       call self%request_coupling_to_model(self%id_POMD(i_spec),self%id_pom(i_spec), 'sDS')
       call self%request_coupling_to_model(self%id_POMP(i_spec),self%id_pom(i_spec), 'sPS')
       call self%request_coupling_to_model(self%id_POMN(i_spec),self%id_pom(i_spec), 'sNS')
       call self%request_coupling_to_model(self%id_POMC(i_spec),self%id_pom(i_spec), 'sCS')
       call self%register_state_dependency(self%id_POMD_PV(i_spec), 'POM_D_'//trim(index)//'_PV', 'g/m2', 'POM D PV group number '//trim(index))
       call self%register_state_dependency(self%id_POMN_PV(i_spec), 'POM_N_'//trim(index)//'_PV', 'g/m2', 'POM N PV group number '//trim(index))
       call self%register_state_dependency(self%id_POMP_PV(i_spec), 'POM_P_'//trim(index)//'_PV', 'g/m2', 'POM P PV group number '//trim(index))
       call self%register_state_dependency(self%id_POMC_PV(i_spec), 'POM_C_'//trim(index)//'_PV', 'g/m2', 'POM C PV group number '//trim(index))
       call self%request_coupling_to_model(self%id_POMD_PV(i_spec),self%id_pom(i_spec), 'sDS_PV')
       call self%request_coupling_to_model(self%id_POMP_PV(i_spec),self%id_pom(i_spec), 'sPS_PV')
       call self%request_coupling_to_model(self%id_POMN_PV(i_spec),self%id_pom(i_spec), 'sNS_PV')
       call self%request_coupling_to_model(self%id_POMC_PV(i_spec),self%id_pom(i_spec), 'sCS_PV')
       call self%register_horizontal_dependency(self%id_tDPOMS_POM(i_spec), 'POM_sediment_update'//trim(index),'g/m2/s','POM pool to DOM update'//trim(index))
       if (self%diagnostics) then
	       call self%register_diagnostic_variable(self%id_tDBurPOM(i_spec),'tDBurPOM_'//trim(index),'g/m2/s','rate D POM buried '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tPBurPOM(i_spec),'tPBurPOM_'//trim(index),'g/m2/s','rate P POM buried '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tNBurPOM(i_spec),'tNBurPOM_'//trim(index),'g/m2/s','rate N POM buried '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tCBurPOM(i_spec),'tCBurPOM_'//trim(index),'g/m2/s','rate C POM buried '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       endif 
   end do
   
   do i_spec=1,self%nPOMexch
       write(index,'(i0)') i_spec
       ! call self%register_model_dependency(self%id_pomx(i_spec),   'POM_exchange'//trim(index)) !
       call self%register_horizontal_dependency(self%id_tDReSedPOMS(i_spec),'POM_exchange_update'//trim(index),'g/m2/s','POM net sedimentation update'//trim(index))
   end do    
   
   ! tka: DOM
   do i_spec=1,self%nDOM
       write(index,'(i0)') i_spec
       call self%register_model_dependency(self%id_dom(i_spec),   'DOM_group'//trim(index))
       call self%register_state_dependency(self%id_DOMD(i_spec),  'DOM_D_'//trim(index), 'g/m2', 'DOM D '//trim(index))
       call self%register_state_dependency(self%id_DOMN(i_spec),  'DOM_N_'//trim(index), 'g/m2', 'DOM N '//trim(index))
       call self%register_state_dependency(self%id_DOMP(i_spec),  'DOM_P_'//trim(index), 'g/m2', 'DOM P '//trim(index))
       call self%register_state_dependency(self%id_DOMC(i_spec),  'DOM_C_'//trim(index), 'g/m2', 'DOM C '//trim(index))
       call self%request_coupling_to_model(self%id_DOMD(i_spec),self%id_dom(i_spec), 'sDS')
       call self%request_coupling_to_model(self%id_DOMP(i_spec),self%id_dom(i_spec), 'sPS')
       call self%request_coupling_to_model(self%id_DOMN(i_spec),self%id_dom(i_spec), 'sNS')
       call self%request_coupling_to_model(self%id_DOMC(i_spec),self%id_dom(i_spec), 'sCS')
       call self%register_state_dependency(self%id_DOMD_PV(i_spec),  'DOM_D_'//trim(index)//'_PV', 'g/m2', 'DOM D PV group number'//trim(index))
       call self%register_state_dependency(self%id_DOMN_PV(i_spec),  'DOM_N_'//trim(index)//'_PV', 'g/m2', 'DOM N PV group number'//trim(index))
       call self%register_state_dependency(self%id_DOMP_PV(i_spec),  'DOM_P_'//trim(index)//'_PV', 'g/m2', 'DOM P PV group number'//trim(index))
       call self%register_state_dependency(self%id_DOMC_PV(i_spec),  'DOM_C_'//trim(index)//'_PV', 'g/m2', 'DOM C PV group number'//trim(index))
       call self%request_coupling_to_model(self%id_DOMD_PV(i_spec),self%id_dom(i_spec), 'sDS_PV')
       call self%request_coupling_to_model(self%id_DOMP_PV(i_spec),self%id_dom(i_spec), 'sPS_PV')
       call self%request_coupling_to_model(self%id_DOMN_PV(i_spec),self%id_dom(i_spec), 'sNS_PV')
       call self%request_coupling_to_model(self%id_DOMC_PV(i_spec),self%id_dom(i_spec), 'sCS_PV')
       if (self%diagnostics) then
	       call self%register_diagnostic_variable(self%id_tDBurDOM(i_spec),'tDBurDOM_'//trim(index),'g/m2/s','rate D DOM buried '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tPBurDOM(i_spec),'tPBurDOM_'//trim(index),'g/m2/s','rate P DOM buried '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tNBurDOM(i_spec),'tNBurDOM_'//trim(index),'g/m2/s','rate N DOM buried '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
           call self%register_diagnostic_variable(self%id_tCBurDOM(i_spec),'tCBurDOM_'//trim(index),'g/m2/s','rate C DOM buried '//trim(index),output=output_instantaneous,domain=domain_bottom,source=source_do_bottom)
       endif 
   end do
       
   !call self%register_horizontal_dependency(self%id_tDPOMbio,type_bulk_standard_variable(name='total_tDPOMbio',units='g/m2/s',aggregate_variable=.true.),domain=domain_bottom) ! remove, do not function
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')  
   ! register diagnostic variables--------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_diagnostic_variable(self%id_VDeltaS,    'VDeltaS',   'm',            'sediment turnover depth',     output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   ! register diagnostic variables for diagnostic process output--------------------------------------------------------------------------------------------------------------------------------------
   if (self%diagnostics) then
     call self%register_diagnostic_variable(self%id_tDBurIM,  'tDBurIM',   'g/m2/s',       'rate IM burial',              output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tSiBurPa, 'tSiBurPa',  'g/m2/s',       'rate Si particulate burial',  output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tPBurPO4, 'tPBurPO4',  'g/m2/s',       'rate PO4 burial',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tPBurAIM, 'tPBurAIM',  'g/m2/s',       'rate P adsorped to IM burial',output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tNBurNH4, 'tNBurNH4',  'g/m2/s',       'rate NH4 burial',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tNBurNO3, 'tNBurNO3',  'g/m2/s',       'rate NO3 burial',             output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tDBurHum, 'tDBurHum',  'g/m2/s',       'rate DW humus burial',        output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tPBurHum, 'tPBurHum',  'g/m2/s',       'rate P humus burial',         output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tNBurHum, 'tNBurHum',  'g/m2/s',       'rate N humus burial',         output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tCBurHum, 'tCBurHum',  'g/m2/s',       'rate C humus burial',         output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   endif
   return

end subroutine initialize

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO BOTTOM                                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_burial), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)                          :: sDIMS, sSiPaS, sPO4S, sPAIMS, sNH4S, sNO3S 
   real(rk)                          :: rSiDPOMS, tDAbioIMS, vDeltaS, tDBurIM, tPBurAIM, bot_pel_conv, sDPOMSTot, tDPOMS
   real(rk)                          :: tNBurNH4, tNBurNO3, tSiBurPa, tPBurPO4, bPorS, cDepthS, tDBurOM, tDBurHum, tNBurHum, tPBurHum, tCBurHum
   real(rk), dimension(self%nPHYT)   :: tDPOMS_Phyt
   real(rk), dimension(self%nMACRO)  :: tDPOMS_Macro
   real(rk), dimension(self%nBENT)   :: tDPOMS_Bent
   real(rk), dimension(self%nPOM)    :: tDPOMS_POM, sDPOMS, sPPOMS, sNPOMS, sCPOMS, tDBurPOM, tNBurPOM, tPBurPOM, tCBurPOM, rNDPOMS, rPDPOMS, rCDPOMS ! NearZero as vector
   real(rk), dimension(self%nPOMexch):: tDReSedPOMS
   real(rk), dimension(self%nDOM)    :: sDDOMS, sPDOMS, sNDOMS, sCDOMS, tDBurDOM, tPBurDOM, tNBurDOM, tCBurDOM
   integer                           :: i_spec
   character(len=64)                 :: index
 
   _HORIZONTAL_LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE::
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values, calc. current nutrient ratios                                                    !
   !================================================================================================================!
      ! 1.1 retrieve environmental dependencies                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _GET_HORIZONTAL_(self%id_WSNH4,sNH4S)                                                                         !
      _GET_HORIZONTAL_(self%id_WSNO3,sNO3S)                                                                         !
      _GET_HORIZONTAL_(self%id_WSPO4,sPO4S)                                                                         !
      _GET_HORIZONTAL_(self%id_WSPAIM,sPAIMS)                                                                       !
      _GET_HORIZONTAL_(self%id_WSDIM,sDIMS)                                                                         !
      _GET_HORIZONTAL_(self%id_WSSiPa,sSiPaS)                                                                       !
      do i_spec=1,self%nPOM                                                                                         ! for each POM group
         _GET_HORIZONTAL_(self%id_POMD(i_spec),sDPOMS(i_spec))                                                      ! get POM dry weight (dimensions: nPOM)
         _GET_HORIZONTAL_(self%id_POMP(i_spec),sPPOMS(i_spec))                                                      ! get POM phosphorous (dimensions: nPOM)
         _GET_HORIZONTAL_(self%id_POMN(i_spec),sNPOMS(i_spec))                                                      ! get POM nitrogen (dimensions: nPOM)
         _GET_HORIZONTAL_(self%id_POMC(i_spec),sCPOMS(i_spec))                                                      ! get POM carbon (dimensions: nPOM)
      end do
      do i_spec=1,self%nDOM                                                                                         ! for each DOM group
         _GET_HORIZONTAL_(self%id_DOMD(i_spec),sDDOMS(i_spec))                                                      ! get DOM dry weight (dimensions: nDOM)
         _GET_HORIZONTAL_(self%id_DOMP(i_spec),sPDOMS(i_spec))                                                      ! get DOM phosphorous (dimensions: nDOM)
         _GET_HORIZONTAL_(self%id_DOMN(i_spec),sNDOMS(i_spec))                                                      ! get DOM nitrogen (dimensions: nDOM)	  
         _GET_HORIZONTAL_(self%id_DOMC(i_spec),sCDOMS(i_spec))                                                      ! get DOM carbon (dimensions: nDOM)	  
      end do
      !=============================================================================================================!
      ! 1.2 diagnostic dependencies                                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _GET_HORIZONTAL_(self%id_tDAbioIMS,tDAbioIMS)                                                                 !
      _GET_HORIZONTAL_(self%id_bPorS,bPorS)                                                                         !
      _GET_HORIZONTAL_(self%id_cDepthS,cDepthS)                                                                     !
      do i_spec=1,self%nPHYT                                                                                        !
            _GET_HORIZONTAL_(self%id_tDPOMS_Phyt(i_spec),tDPOMS_Phyt(i_spec))                                       !
      end do                                                                                                        !
      do i_spec=1,self%nBENT                                                                                        !
            _GET_HORIZONTAL_(self%id_tDPOMS_Bent(i_spec),tDPOMS_Bent(i_spec))                                       !
      end do                                                                                                        !
      do i_spec=1,self%nMACRO                                                                                       !
            _GET_HORIZONTAL_(self%id_tDPOMS_Macro(i_spec),tDPOMS_Macro(i_spec))                                     !
      end do      
      do i_spec=1,self%nPOM                                                                                         !
            _GET_HORIZONTAL_(self%id_tDPOMS_POM(i_spec),tDPOMS_POM(i_spec))                                         !
      !      _GET_HORIZONTAL_(self%id_tDReSedPOMS(i_spec),tDReSedPOMS(i_spec))                                      !
      end do                                                                                                        !
      do i_spec=1,self%nPOMexch                                                                                     !
            _GET_HORIZONTAL_(self%id_tDReSedPOMS(i_spec),tDReSedPOMS(i_spec))                                       !
      end do                                                                                                        !
      !=============================================================================================================!
      ! 1.3 calculate current nutrients ratios                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      sDPOMSTot = sum(sDPOMS)                                                                                       ! calculate total DW POM in sediment
      rPDPOMS=sPPOMS/(sDPOMS+NearZero)                                                                              ! (dim: nPOM)
      rNDPOMS=sNPOMS/(sDPOMS+NearZero)                                                                              ! (dim: nPOM)
      rCDPOMS=sCPOMS/(sDPOMS+NearZero)                                                                              ! (dim: nPOM)
      rSiDPOMS=sSiPaS/(sDPOMSTot+NearZero)                                                                          !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. Burial of sediment components                                                                              !
   !================================================================================================================!
      ! 2.1 calculate current ROC of POM & sediment turnover depth                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDPOMS= sum(tDReSedPOMS) + sum(tDPOMS_POM) + sum(tDPOMS_Phyt) + sum(tDPOMS_Bent) + sum(tDPOMS_Macro)          ! current ROC of total sediment POM
      vDeltaS = (tDAbioIMS / self%cRhoIM + tDPOMS / self%cRhoOM)/(1.0_rk - bPorS)                                   ! turnover_depth_in_lake
      !=============================================================================================================!
      ! 2.2 burial fluxes in the case of turnover depth >= 0                                                        !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (vDeltaS >= 0.0_rk) then                                                                                   !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.2.1 DW                                                                                                 !
         !----------------------------------------------------------------------------------------------------------!
         tDBurIM = (tDPOMS + (self%cRhoOM / self%cRhoIM) * tDAbioIMS) / &                                           !
              (sDPOMSTot / (sDIMS+NearZero) + self%cRhoOM / self%cRhoIM)                                            ! burial_flux_of_DW_in_inorganic_matter_in_lake
         tDBurOM = sDPOMSTot / (sDIMS+NearZero) * tDBurIM                                                           ! burial_flux_of_DW_in_organic_matter_in_lake
         tDBurPOM = sDPOMS /(sDPOMSTot) * tDBurOM                                                                   ! burial_flux_of_DW_in_POM_in_lake per POM group (dim: nPOM)
         tDBurDOM = sDDOMS *(vDeltaS / cDepthS)                                                                     ! burial_flux_of_DDOM_in_lake (dim: nDOM)
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.2.2 P                                                                                                  !
         !----------------------------------------------------------------------------------------------------------!
         tPBurPOM = rPDPOMS * tDBurPOM                                                                              ! burial_flux_of_P_in_POM_in_lake (dim: nPOM)
         tPBurAIM = sPAIMS / sDIMS * tDBurIM                                                                        ! burial_flux_of_P_adsorbed_onto_inorganic_matter_in_lake
         tPBurPO4 = sPO4S *(vDeltaS / cDepthS)                                                                      ! burial_flux_of_dissolved_P_in_lake
         tPBurDOM = sPDOMS *(vDeltaS / cDepthS)                                                                     ! burial_flux_of_PDOM_in_lake (dim: nDOM)
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.2.3 N                                                                                                  !
         !----------------------------------------------------------------------------------------------------------!
         tNBurPOM = rNDPOMS * tDBurPOM                                                                              ! burial_flux_of_N_in_POMritus_in_lake (dim: nPOM)
         tNBurNH4 = sNH4S *(vDeltaS /cDepthS)                                                                       ! burial_flux_of_dissolved_NH4_in_lake
         tNBurNO3 = sNO3S *(vDeltaS / cDepthS)                                                                      ! burial_flux_of_dissolved_NO3_in_lake
         tNBurDOM = sNDOMS *(vDeltaS / cDepthS)                                                                     ! burial_flux_of_NDOM_in_lake (dim: nDOM)
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.2.4 C                                                                                                  !
         !----------------------------------------------------------------------------------------------------------!
         tCBurPOM = rCDPOMS * tDBurPOM                                                                              ! burial_flux_of_C_in_POM_in_lake (dim: nPOM)
         tCBurDOM = sCDOMS *(vDeltaS / cDepthS)                                                                     ! burial_flux_of_CDOM_in_lake (dim: nDOM)
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.2.5 Si                                                                                                 !
         !----------------------------------------------------------------------------------------------------------!
         tSiBurPa = rSiDPOMS * tDBurOM                                                                              ! burial_flux_of_particulate_Si_in_lake
      !=============================================================================================================!
      ! 2.3 burial fluxes in the case of turnover depth < 0                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      else                                                                                                          !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.3.1 DW                                                                                                 !
         !----------------------------------------------------------------------------------------------------------!
         tDBurIM = ( tDPOMS +(self%cRhoOM / self%cRhoIM) * tDAbioIMS) / (self%fDOrgSoil &                           !
             /(1.0_rk - self%fDOrgSoil) + self%cRhoOM / self%cRhoIM)                                                ! burial_flux_of_DW_in_inorganic_matter_in_lake
         tDBurOM = self%fDOrgSoil /(1.0 - self%fDOrgSoil) * tDBurIM                                                 ! burial_flux_of_DW_in_organic_matter_in_lake
         tDBurPOM = 0.0_rk                                                                                          ! burial_flux_of_DW_in_POM_in_lake
         tDBurDOM = 0.0_rk                                                                                          ! burial_flux_of_DW_in_DOM_in_lake
         tDBurHum = tDBurOM                                                                                         ! burial_flux_of_DW_in_humus_in_lake
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.3.2 P                                                                                                  !
         !----------------------------------------------------------------------------------------------------------!
         tPBurPOM = 0.0_rk                                                                                          ! burial_flux_of_P_in_POM_in_lake
         tPBurDOM = 0.0_rk                                                                                          ! burial_flux_of_P_in_DOM_in_lake
         tPBurAIM = 0.0_rk                                                                                          ! burial_flux_of_P_adsorbed_onto_inorganic_matter_in_lake
         tPBurPO4 = self%cPO4Ground *(bPorS * vDeltaS)                                                              ! burial_flux_of_dissolved_P_in_lake
         tPBurHum = 0.001_rk * tDBurHum                                                                             ! burial_flux_of_P_in_humus_in_lake
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.3.3 N                                                                                                  !
         !----------------------------------------------------------------------------------------------------------!
         tNBurPOM = 0.0_rk                                                                                          ! burial_flux_of_N_in_POM_in_lake
         tNBurDOM = 0.0_rk                                                                                          ! burial_flux_of_N_in_DOM_in_lake
         tNBurNH4 = self%cNH4Ground *(bPorS * vDeltaS)                                                              ! burial_flux_of_dissolved_NH4_in_lake
         tNBurNO3 = self%cNO3Ground *(bPorS * vDeltaS)                                                              ! burial_flux_of_dissolved_NO3_in_lake
         tNBurHum = 0.01_rk * tDBurHum                                                                              ! burial_flux_of_N_in_humus_in_lake
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.3.4 C                                                                                                  !
         !----------------------------------------------------------------------------------------------------------!
         tCBurPOM = 0.0_rk                                                                                          ! burial_flux_of_C_in_POM_in_lake
         tCBurDOM = 0.0_rk                                                                                          ! burial_flux_of_C_in_DOM_in_lake
         tCBurHum = 0.50_rk * tDBurOM                                                                               ! burial_flux_of_C_in_humus_in_lake
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 2.3.5 Si                                                                                                 !
         !----------------------------------------------------------------------------------------------------------!
         tSiBurPa = 0.0_rk                                                                                          ! burial_flux_of_particulate_Si_in_lake
      endif                                                                                                         !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  3. Update variables                                                                                           !
   !================================================================================================================!
      ! 3.1 update state variables                                                                                  !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)                                                           ! 
      do i_spec = 1,self%nPOM                                                                                       ! for each POM group
         _SET_BOTTOM_ODE_(self%id_POMD(i_spec),-tDBurPOM(i_spec))                                                   !   update POM DW ODEs
         _SET_BOTTOM_ODE_(self%id_POMN(i_spec),-tNBurPOM(i_spec))                                                   !   update POM N ODEs
         _SET_BOTTOM_ODE_(self%id_POMP(i_spec),-tPBurPOM(i_spec))                                                   !   update POM P ODEs
         _SET_BOTTOM_ODE_(self%id_POMC(i_spec),-tCBurPOM(i_spec))                                                   !   update POM C ODEs
         _SET_BOTTOM_EXCHANGE_(self%id_POMD_PV(i_spec),-tDBurPOM(i_spec)*bot_pel_conv)                              !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_POMN_PV(i_spec),-tNBurPOM(i_spec)*bot_pel_conv)                              !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_POMP_PV(i_spec),-tPBurPOM(i_spec)*bot_pel_conv)                              !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
         _SET_BOTTOM_EXCHANGE_(self%id_POMC_PV(i_spec),-tCBurPOM(i_spec)*bot_pel_conv)                              !   update ROC of projected bottom variables (to allow pelagic modules to read bottom variables)
      end do                                                                                                        !
      do i_spec = 1,self%nDOM                                                                                       ! for each DOM group
         _SET_BOTTOM_ODE_(self%id_DOMD(i_spec),-tDBurDOM(i_spec))                                                   !   update DOM DW ODEs
         _SET_BOTTOM_ODE_(self%id_DOMN(i_spec),-tNBurDOM(i_spec))                                                   !   update DOM N ODEs
         _SET_BOTTOM_ODE_(self%id_DOMP(i_spec),-tPBurDOM(i_spec))                                                   !   update DOM P ODEs
         _SET_BOTTOM_ODE_(self%id_DOMC(i_spec),-tCBurDOM(i_spec))                                                   !   update DOM P ODEs
         _SET_BOTTOM_EXCHANGE_(self%id_DOMD_PV(i_spec),-tDBurDOM(i_spec)*bot_pel_conv)                              !   update DOM DW ODEs of projected bottom variables
         _SET_BOTTOM_EXCHANGE_(self%id_DOMN_PV(i_spec),-tNBurDOM(i_spec)*bot_pel_conv)                              !   update DOM N ODEs of projected bottom variables
         _SET_BOTTOM_EXCHANGE_(self%id_DOMP_PV(i_spec),-tPBurDOM(i_spec)*bot_pel_conv)                              !   update DOM P ODEs of projected bottom variables
         _SET_BOTTOM_EXCHANGE_(self%id_DOMC_PV(i_spec),-tCBurDOM(i_spec)*bot_pel_conv)                              !   update DOM P ODEs of projected bottom variables
      end do                                                                                                        !
      _SET_BOTTOM_ODE_(self%id_WSDIM,  -tDBurIM)                                                                    !
      _SET_BOTTOM_ODE_(self%id_WSSiPa, -tSiBurPa)                                                                   !
      _SET_BOTTOM_ODE_(self%id_WSPO4,  -tPBurPO4)                                                                   !
      _SET_BOTTOM_ODE_(self%id_WSPAIM, -tPBurAIM)                                                                   !
      _SET_BOTTOM_ODE_(self%id_WSNH4,  -tNBurNH4)                                                                   !
      _SET_BOTTOM_ODE_(self%id_WSNO3,  -tNBurNO3)                                                                   !
      _SET_BOTTOM_ODE_(self%id_WSDHum, tDBurHum)                                                                    !
      _SET_BOTTOM_ODE_(self%id_WSPHum, tPBurHum)                                                                    !
      _SET_BOTTOM_ODE_(self%id_WSNHum, tNBurHum)                                                                    !
      _SET_BOTTOM_ODE_(self%id_WSCHum, tCBurHum)                                                                    !
      _SET_BOTTOM_EXCHANGE_(self%id_WSDHum_PV, tDBurHum*bot_pel_conv)                                               !
      _SET_BOTTOM_EXCHANGE_(self%id_WSPHum_PV, tPBurHum*bot_pel_conv)                                               !
      _SET_BOTTOM_EXCHANGE_(self%id_WSNHum_PV, tNBurHum*bot_pel_conv)                                               !
      _SET_BOTTOM_EXCHANGE_(self%id_WSCHum_PV, tCBurHum*bot_pel_conv)                                               !
      !=============================================================================================================!
      ! 3.2 update diagnostics                                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_HORIZONTAL_DIAGNOSTIC_(self%id_VDeltaS, VDeltaS)                                                         !
      !=============================================================================================================!
      !=============================================================================================================!
      ! 3.2 update local diagnostic output processes                                                                !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
        do i_spec = 1,self%nPOM                                                                                     ! 
           _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBurPOM(i_spec),tDBurPOM(i_spec))                                   ! 
           _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBurPOM(i_spec),tNBurPOM(i_spec))                                   ! 
           _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBurPOM(i_spec),tPBurPOM(i_spec))                                   ! 
           _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCBurPOM(i_spec),tCBurPOM(i_spec))                                   ! 
        end do
        do i_spec = 1,self%nDOM                                                                                     ! 
           _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBurDOM(i_spec),tDBurDOM(i_spec))                                   ! 
           _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBurDOM(i_spec),tNBurDOM(i_spec))                                   ! 
           _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBurDOM(i_spec),tPBurDOM(i_spec))                                   ! 
           _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCBurDOM(i_spec),tCBurDOM(i_spec))                                   ! 
        end do
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBurIM,  tDBurIM)                                                      !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiBurPa, tSiBurPa)                                                     !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBurPO4, tPBurPO4)                                                     !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBurAIM, tPBurAIM)                                                     !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBurNH4, tNBurNH4)                                                     !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBurNO3, tNBurNO3)                                                     !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDBurHum, tDBurHum)                                                     !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPBurHum, tPBurHum)                                                     !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNBurHum, tNBurHum)                                                     !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCBurHum, tCBurHum)                                                     !
      endif                                                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!      
   _HORIZONTAL_LOOP_END_ !!! END OF MODEL CODE::
end subroutine do_bottom
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
end module wet_burial
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
