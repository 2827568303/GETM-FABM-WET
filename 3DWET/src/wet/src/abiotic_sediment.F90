#include "fabm_driver.h"
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ MODULE: ABIOTIC SEDIMENT                                                                                                                                                                       §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
module wet_abiotic_sediment
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_particle
   use wet_utility, ONLY: uFunTmArrh
   implicit none
   private

   !PUBLIC DERIVED TYPES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public :: type_wet_abiotic_sediment
      ! local state variable identifiers-------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                 :: id_sDPOMS_PV, id_sNPOMS_PV, id_sPPOMS_PV
      type (type_bottom_state_variable_id)          :: id_sDIMS, id_sDPOMS,id_sNPOMS, id_sPPOMS,id_sSiPaS, id_sDDOMS,id_sNDOMS, id_sPDOMS,id_sSiO2S, id_sPO4S,id_sPAIMS,id_sNH4S, id_sNO3S, id_sDHumS
      type (type_bottom_state_variable_id)          :: id_sNHumS,id_sPHumS
      ! diagnostic variables for local output--------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id) :: id_tDPOMdummy
      type (type_horizontal_diagnostic_variable_id) :: id_aPEqIMS,id_afOxySed, id_cDepthS, id_bPorCorS
      ! diagnostic variables for diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id) :: id_tDMinHumS, id_tDMinPOMS, id_tDMinDOMS, id_tPMinPOMS, id_tPSorpIMS, id_tPChemPO4, id_tPMinHumS, id_tPMinDOMS, id_tNNitrS, id_tNMinHumS, id_tNMinDOMS, id_tNDenitS
      type (type_horizontal_diagnostic_variable_id) :: id_tNMinPOMS, id_tSiMinPaS, id_fPEqIMS, uCorDif
      ! diagnostic variable for external dependencies:-----------------------------------------------------------------------------------------------------------------------------------------------
      type (type_horizontal_diagnostic_variable_id) :: id_tDAbioO2S, id_tDAbioIMS
      type (type_horizontal_diagnostic_variable_id) :: id_bPorS, id_fDepthDifS, id_bot_pel_conv_out
      type (type_horizontal_dependency_id), allocatable, dimension(:):: id_tDTrans_POM, id_tCTrans_POM, id_tDTrans_DOM, id_tCTrans_DOM
      ! state dependencies identifiers---------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                 :: id_O2ConsSed
      type (type_state_variable_id)                 :: id_sDDOMW, id_sNDOMW
      type (type_state_variable_id)                 :: id_sPDOMW
      ! environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------------
      type (type_dependency_id)                     :: id_dz, id_bot_pel_conv
      type (type_dependency_id)                     :: id_uTm
      type (type_horizontal_dependency_id)          :: id_depth, id_tDTrans, id_tCTrans
      ! parameters-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
      logical                                       :: diagnostics, hypsograph
      real(rk)                                      :: cDepthS,O2PerNH4S,bPorS,bPorCorS,kPSorpS,cRelPAdsDWS,cRelPAdsFeS,fFeDIM,cRelPAdsAlS,fAlDIMS ! cCPerDWS
      real(rk)                                      :: fRedMaxS,cKPAdsOxS,kPChemPO4,coPO4Max,NO3PerCS,hNO3DenitS,fRefrPOMS,kNitrS,cThetaNitrS,kDMinHum         
      real(rk)                                      :: fDepthDifS,cThetaDifO2,cTurbDifNut,kNDifNH4,kNDifNO3,kPDifPO4,kO2Dif,cTurbDifO2                      
      real(rk)                                      :: cThetaMinPOMS,kDMinPOMS,kNMinPOMS,kPMinPOMS,kSiMinPaS,cThetaMinDOMS,kDMinDOMS,kNMinDOMS             
      real(rk)                                      :: kPMinDOMS,kDDifDOM,kNDifDOM,kPDifDOM,kSiO2Dif, cThetaMinSiS
      integer                                       :: nPOM, nDOM
                                                                                                                                          
   contains                                                                                             
                                                                                                   
   !MODEL PROCEDURES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   procedure :: initialize
   procedure :: do_bottom
   
   end type type_wet_abiotic_sediment

   !private data members(API0.92)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk),parameter :: secs_pr_day= 86400.0_rk
   real(rk),parameter :: NearZero=0.000000000000000000000000000000001_rk
   real(rk),parameter :: molO2molC=2.6667_rk ! molar weight ratios
   real(rk),parameter :: molO2molN=2.2857_rk ! molar weight ratios
   real(rk),parameter :: molNmolC=1.1667_rk  ! molar weight ratios

contains

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: INITIALIZATION                                                                                                                                                                     §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine initialize(self,configunit)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_abiotic_sediment), intent(inout), target :: self
   integer,                              intent(in)            :: configunit
   
   !LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   integer             :: i_spec
   character(len=64)   :: index
   
   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%get_parameter(self%cDepthS,      'cDepthS',      'm',                'sediment depth',                                            default=0.1_rk                                       )
   call self%get_parameter(self%fDepthDifS,   'fDepthDifS',   '-',                'nutrient diffusion distance as fraction of sediment depth', default=0.5_rk                                       )
   call self%get_parameter(self%bPorCorS,     'bPorCorS',     'm3/m3',            'sediment porosity corrected for tortuosity',                default=0.737275_rk                                  )
   !call self%get_parameter(self%cCPerDWS,     'cCPerDWS',     'gC/gDW',           'C content of organic DW matter',                            default=0.4_rk                                       )
   call self%get_parameter(self%O2PerNH4S,    'O2PerNH4S',    'mol/mol',          'O2 used per NH4 nitrified',                                 default=2.0_rk                                       )
   call self%get_parameter(self%kNitrS,       'kNitrS',       '1/d',              'nitrification rate constant at 20*C',                       default=1.2_rk,     scale_factor =1.0_rk/secs_pr_day )
   call self%get_parameter(self%cThetaNitrS,  'cThetaNitrS',  '1/e^*C',           'temperature coefficient for nitrification',                 default=1.03_rk                                      )
   call self%get_parameter(self%NO3PerCS,     'NO3PerCS',     'mol/mol',          'NO3 denitrified per C mineralized',                         default=1.0_rk                                       )
   call self%get_parameter(self%hNO3DenitS,   'hNO3DenitS',   'mgN/l',            'quadratic half-sat. NO3 conc. for denitrification',         default=0.5_rk                                       )
   call self%get_parameter(self%kPSorpS,      'kPSorpS',      '1/d',              'P sorption rate constant',                                  default=0.03_rk,    scale_factor=1.0_rk/secs_pr_day  )
   call self%get_parameter(self%cRelPAdsDWS,  'cRelPAdsDWS',  'gP/gDW',           'max. P adsorption per g DW',                                default=0.00003_rk                                   )
   call self%get_parameter(self%cRelPAdsFeS,  'cRelPAdsFeS',  'gP/gFe',           'max. P adsorption per g Fe',                                default=0.06_rk                                      )
   call self%get_parameter(self%fFeDIM,       'fFeDIM',       'gFe/gD',           'Fe content of inorganic matter',                            default=0.04_rk                                      )
   call self%get_parameter(self%cRelPAdsAlS,  'cRelPAdsAlS',  'gP/gAl',           'max. P adsorption per g Al',                                default=0.134_rk                                     )
   call self%get_parameter(self%fAlDIMS,      'fAlDIMS',      'gAl/gD',           'Al content of inorganic matter',                            default=0.01_rk                                      )
   call self%get_parameter(self%fRedMaxS,     'fRedMaxS',     '-',                'max. reduction factor of P adsorption affinity',            default=0.96_rk                                      )
   call self%get_parameter(self%cKPAdsOxS,    'cKPAdsOxS',    'm3/gP',            'P adsorption affinity at oxidized conditions',              default=1.5_rk                                       )
   call self%get_parameter(self%kPChemPO4,    'kPChemPO4',    '1/d',              'chemical PO4 loss rate',                                    default=0.03_rk,    scale_factor=1.0_rk/secs_pr_day  )
   call self%get_parameter(self%coPO4Max,     'coPO4Max',     'mgP/l',            'max. soluble reactive P conc. in pore water',               default=1.4_rk                                       )
   call self%get_parameter(self%bPorS,        'bPorS',        'm3/m3',            'sediment porosity',                                         default=0.58_rk                                      )
   call self%get_parameter(self%cThetaDifO2,  'cThetaDifO2',  '1/e^*C',           'temperature coefficient for O2 diffusion',                  default=1.01_rk                                      )
   call self%get_parameter(self%kO2Dif,       'kO2Dif',       'm2/d',             'O2 diffusion constant at 20*C',                             default=0.00017_rk,  scale_factor=1.0_rk/secs_pr_day )
   call self%get_parameter(self%cTurbDifO2,   'cTurbDifO2',   '-',                'bioturbation factor for oxygen diffusion',                  default=5.0_rk                                       )
   call self%get_parameter(self%kDMinHum,     'kDMinHum',     '1/d',              'humic decomposition constant at 20*C',                      default=0.00005_rk,  scale_factor=1.0_rk/secs_pr_day )
   call self%get_parameter(self%cThetaMinSiS, 'cThetaMinSiS', '1/e^*C',           'temperature coefficient of SiO2 mineralization',            default=1.074_rk                                     )
   call self%get_parameter(self%kSiMinPaS,    'kSiMinPaS',    '1/d',              'SiPOM to SiO2 biodissolution constant at 20*C',             default=0.03_rk,     scale_factor=1.0_rk/secs_pr_day )
   call self%get_parameter(self%nPOM,         'nPOM',         '-',                'number of benthic particulate OM instances',                default=0                                            )
   call self%get_parameter(self%nDOM,         'nDOM',         '-',                'number of benthic dissolved OM instances',                  default=0                                            )
   ! diagnostic  parameter--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%get_parameter(self%diagnostics,  'diagnostics',  '-',                'toggle diagnostic output',                                  default=.false.                                      )
   call self%get_parameter(self%hypsograph,   'hypsograph',   '-',                'indicate hypsograph presence/absence'                                                                            )
   
   !REGISTER MODEL VARIBLES, DEPENDENCIES & COUPLINGS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! local state variables---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_state_variable(self%id_sDIMS,          'sDIMS',            'g/m2',  'inorganic matter',            initial_value=39611.3_rk,   minimum=10.0_rk  ) 
   call self%register_state_variable(self%id_sSiPaS,         'sSiPaS',           'g/m2',  'particulate Si',              initial_value=1.82_rk,      minimum=0.0_rk   )
   call self%register_state_variable(self%id_sSiO2S,         'sSiO2S',           'g/m2',  'dissolved SiO2',              initial_value=1.82_rk,      minimum=0.0_rk   )
   call self%register_state_variable(self%id_sPO4S,          'sPO4S',            'g/m2',  'phosphate',                   initial_value=0.182_rk,     minimum=0.0_rk   )
   call self%register_state_variable(self%id_sPAIMS,         'sPAIMS',           'g/m2',  'absorbed phosphate',          initial_value=17.99_rk,     minimum=0.0_rk   )
   call self%register_state_variable(self%id_sNH4S,          'sNH4S',            'g/m2',  'ammonium',                    initial_value=0.02_rk,      minimum=0.0_rk   )
   call self%register_state_variable(self%id_sNO3S,          'sNO3S',            'g/m2',  'nitrate',                     initial_value=0.002_rk,     minimum=0.0_rk   )
   ! register external dependencies-----------------------------------------------------------   -------------------------------------------------------------------------------------------------------
   call self%register_state_dependency(self%id_O2ConsSed,    'oxygen_pool_water','g/m3',  'oxygen pool water'                )
   ! register diagnostic variables-------------------------------------------------------------------------------------------------------------------------------------------------------------------   
   call self%register_diagnostic_variable(self%id_afOxySed,  'afOxySed',         '-',     'fraction of aerobic sediment',output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_aPEqIMS,   'aPEqIMS',          '-',     'equilibrium adsorbed PO4',    output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tDAbioO2S, 'tDAbioO2S',        'g/m2/d','O2 consumption',              output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tDAbioIMS, 'tDAbioIMS',        'g/m2/s','IM ROC',                      output=output_none,          domain=domain_bottom, source=source_do_bottom)
   ! tka to be used in sediment_exchange
   call self%register_diagnostic_variable(self%id_bPorS,     'bPorS',            'm3/m3', 'sediment porosity',                                 output=output_none, domain=domain_bottom,missing_value=self%bPorS, source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_bPorCorS,  'bPorCorS',         'm3/m3', 'sediment porosity corrected for tortuosity',        output=output_none, domain=domain_bottom,missing_value=self%bPorCorS, source=source_do_bottom)   
   call self%register_diagnostic_variable(self%id_cDepthS,   'cDepthS',          'm',     'sediment depth',                                    output=output_none, domain=domain_bottom,missing_value=self%cDepthS, source=source_do_bottom)   
   call self%register_diagnostic_variable(self%id_fDepthDifS,'fDepthDifS',       'm',     'diffusion distance as fraction of sediment depth',  output=output_none, domain=domain_bottom,missing_value=self%fDepthDifS, source=source_do_bottom)   
   call self%register_diagnostic_variable(self%id_tDPOMdummy,'tDPOMdummy',       'gDW/m2','dummy total sediment POM increase from biology',    domain=domain_bottom, source=source_do_bottom) ! for burial, in case there is no biology, 
   call self%add_to_aggregate_variable(type_bulk_standard_variable(name='total_tDPOMbio',units='gDW/m2/s',aggregate_variable=.true.),self%id_tDPOMdummy,scale_factor=1._rk)
   ! tka 12/4: get cDTrans and cCTrans from sediment_om
   allocate(self%id_tDTrans_POM(self%nPOM))
   allocate(self%id_tDTrans_DOM(self%nDOM))
   allocate(self%id_tCTrans_POM(self%nPOM))
   allocate(self%id_tCTrans_DOM(self%nDOM))
   do i_spec=1,self%nPOM
       write(index,'(i0)') i_spec
       call self%register_horizontal_dependency(self%id_tDTrans_POM(i_spec), 'Trans_DPOM_sediment_update'//trim(index),'g/m2/s','Transformation DPOM sediment update'//trim(index))
       call self%register_horizontal_dependency(self%id_tCTrans_POM(i_spec), 'Trans_CPOM_sediment_update'//trim(index),'g/m2/s','Transformation CPOM sediment update'//trim(index))
   end do    
   do i_spec=1,self%nDOM
       write(index,'(i0)') i_spec
       call self%register_horizontal_dependency(self%id_tDTrans_DOM(i_spec), 'Trans_DDOM_sediment_update'//trim(index),'g/m2/s','Transformation DDOM sediment update'//trim(index))
       call self%register_horizontal_dependency(self%id_tCTrans_DOM(i_spec), 'Trans_CDOM_sediment_update'//trim(index),'g/m2/s','Transformation CDOM sediment update'//trim(index))  
   end do    
   call self%register_diagnostic_variable(self%id_bot_pel_conv_out,  'bot_pel_conv','-',         'current conversion between m-2 and m-3', output=output_none, domain=domain_bottom, source=source_do_bottom)!,standard_variable=.true.) ! for fish, in case there is no macrophytes
   ! Register diagnostic process output-------------------------------------------------------------------------------------------------------------------------------------------------------------
   if (self%diagnostics) then
     call self%register_diagnostic_variable(self%id_tPChemPO4,'tPChemPO4','g/m2/s','rate chem. loss of diss. P from pore water',output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tPSorpIMS,'tPSorpIMS','g/m2/s','rate P sorped to IM',                       output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tNNitrS,  'tNNitrS',  'g/m2/s','rate nitrification',                        output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tNDenitS, 'tNDenitS', 'g/m2/s','rate denitrification',                      output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_tSiMinPaS,'tSiMinPaS','g/m2/s','rate Si particulate mineralization',        output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
     call self%register_diagnostic_variable(self%id_fPEqIMS,  'fPEqIMS',  '-',     'fraction of PAIMS in equilibrium',          output=output_instantaneous, domain=domain_bottom, source=source_do_bottom)
   endif
   ! register environmental dependencies-------------------------------------------------------------------------------------------------------------------------------------------------------------
   call self%register_dependency(   self%id_uTm,           standard_variables%temperature    )
   call self%register_dependency(   self%id_depth,         standard_variables%bottom_depth   )
   call self%register_dependency(   self%id_dz,            standard_variables%cell_thickness )
   if (self%hypsograph) then              
      call self%register_dependency(self%id_bot_pel_conv,  type_bulk_standard_variable(name='bot_pel_conv',units='-'))
   endif
   return
end subroutine initialize

!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
!§§ SUBROUTINE: DO_BOTTOM                                                                                                                                                                          §§
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   !INPUT PARAMETERS:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   class (type_wet_abiotic_sediment), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_
   
   !DECLARE LOCAL VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   real(rk)     :: sNH4S, sNO3S, sPO4S, sPAIMS, sDIMS, sSiPaS, sSiO2S, sPAIMW, uTm, depth, sO2W, afOxySed, aDepthOxySed, sDIMW, tTotSOD, uFunTmNitr
   real(rk)     :: tNAbioNH4S, tPAbioPO4S, tPSorpIMS, aPEqIMS, aPIsoAdsS, aPAdsMaxS, aKPAdsS, tPChemPO4, tPAbioAIMS, tNNitrS, oPO4S, tO2NitrS, tNAbioNO3S, tNDenitS, tCDenitS
   real(rk)     :: tDAbioIMS, aDepthDif,akO2DifCor, tO2Dif, uFunTmDifO2, tSiMinPaS, uFunTmMinSiS, tDMinDOMS, tNMinDOMS, tPMinDOMS, oNO3S
   real(rk)     :: tO2MinTOMS, tSiAbioPaS, tNNitrS_base, tSiO2AbioS, bot_pel_conv, dz, fPEqIMS
   real(rk), dimension(self%nPOM)   :: tDTrans_POM, tCTrans_POM
   real(rk), dimension(self%nDOM)   :: tDTrans_DOM, tCTrans_DOM
   integer      :: i_spec
                                                                                                                   
   _HORIZONTAL_LOOP_BEGIN_ !!! BEGINNING OF MODEL CODE:: 
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  1. retrieve variable values and calculate local nutrient ratios                                               !
   !================================================================================================================!
      ! 1.1 retrieve sediment state variables                                                                       !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
       _GET_HORIZONTAL_(self%id_sSiPaS,sSiPaS)                                                                      !
       _GET_HORIZONTAL_(self%id_sSiO2S,sSiO2S)                                                                      !
       _GET_HORIZONTAL_(self%id_sDIMS,sDIMS)                                                                        !
       _GET_HORIZONTAL_(self%id_sPO4S,sPO4S)                                                                        !
       _GET_HORIZONTAL_(self%id_sPAIMS,sPAIMS)                                                                      !
       _GET_HORIZONTAL_(self%id_sNH4S,sNH4S)                                                                        !
       _GET_HORIZONTAL_(self%id_sNO3S,sNO3S)                                                                        !
      !=============================================================================================================!
      ! 1.2 retrieve water column dependencies                                                                      !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _GET_(self%id_O2ConsSed,sO2W)                                                                                 !
      !=============================================================================================================!
      ! 1.3 retrieve environmental dependencies                                                                     !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _GET_(self%id_uTm,uTm)                                                                                        !
      _GET_HORIZONTAL_(self%id_depth,depth)                                                                         !
      do i_spec=1,self%nPOM                                                                                         !
            _GET_HORIZONTAL_(self%id_tDTrans_POM(i_spec),tDTrans_POM(i_spec))                                       !
            _GET_HORIZONTAL_(self%id_tCTrans_POM(i_spec),tCTrans_POM(i_spec))                                       !
      end do                                                                                                        !
      do i_spec=1,self%nDOM                                                                                         !
            _GET_HORIZONTAL_(self%id_tDTrans_DOM(i_spec),tDTrans_DOM(i_spec))                                       !
            _GET_HORIZONTAL_(self%id_tCTrans_DOM(i_spec),tCTrans_DOM(i_spec))                                       !
      end do                                                                                                        !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  2. calculate current dissolved matter conc. in interstitial water                                             !
   !================================================================================================================!
      ! 2.1 inorganic matter                                                                                        !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      oNO3S = max(0.0_rk, sNO3S / self%cDepthS / self%bPorS)                                                        ! conc. of dissolved NO3 in interstitial water
      !oNH4S=max(0.0_rk, sNH4S/self%cDepthS/self%bPorS)                                                             ! conc. of dissolved NH4 in interstitial water ! tka 16/5 not used
      oPO4S = max(0.0_rk, sPO4S / self%cDepthS / self%bPorS)                                                        ! conc. of dissolved PO4 in interstitial water
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  3. calculate O2 diffusion fluxes between sediment and water                                                   !
   !================================================================================================================!
       ! 3.1 temperature function for diffusion                                                                     !
       !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
       uFunTmDifO2= uFunTmArrh(uTm,self%cThetaDifO2)                                                                ! temperature function of O2 diffusion
       !============================================================================================================!
       ! 3.1 diffusion of oxygen                                                                                    !
       !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
       aDepthDif= max(NearZero, self%fDepthDifS*self%cDepthS)                                                       ! average diffusion distance
       akO2DifCor=self%kO2Dif*uFunTmDifO2*self%cTurbDifO2*self%bPorCorS                                             ! corrected O2 diffusion coefficient
       tO2Dif= akO2DifCor*sO2W/aDepthDif                                                                            ! O2_diffusion (water to sediment), tka 16/4: not used or in ouput
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  4. calculate oxygen consumption and oxygen dependent rates                                                    !
   !================================================================================================================!
      ! 4.1 calculate potential nitrification                                                                       !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      uFunTmNitr=uFunTmArrh(uTm,self%cThetaNitrS)                                                                   ! Temperature dependence of nitrification
      tNNitrS_base=self%kNitrS*uFunTmNitr*sNH4S                                                                     ! potential nitrification (before oxygen)
      !=============================================================================================================!
      ! 4.2 calculate oxygen conditions in sediment                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tTotSOD=max(NearZero, (molO2molC*(sum(tCTrans_POM) + sum(tCTrans_DOM)) +  &                                   !
          self%O2PerNH4S*molO2molN*tNNitrS_base) / self%cDepthS)                                                    ! calculate total sediment oxygen demand
      aDepthOxySed=(((2.0_rk * sO2W * akO2DifCor / tTotSOD) )** (0.5_rk))                                           ! calculate oxygen penetration depth
      afOxySed=min(1.0, max(0.0_rk, aDepthOxySed/self%cDepthS))                                                     ! calculate fraction aerobic sediment
      tO2MinTOMS=molO2molC*afOxySed*(sum(tCTrans_POM) + sum(tCTrans_DOM))                                           ! calculate total oxygen comsumption by TOM
      !=============================================================================================================!
      ! 4.3 calculate denitrification                                                                               !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tCDenitS=oNO3S*oNO3S/(self%hNO3DenitS*self%hNO3DenitS+oNO3S*oNO3S)*(1.0-afOxySed)* &                          !
          (sum(tCTrans_POM) + sum(tCTrans_DOM))                                                                     ! calculate C mineralization flux by denitrification
      tNDenitS=self%NO3PerCS*molNmolC*tCDenitS                                                                      ! calculate N denitrification_flux
      !=============================================================================================================!
      ! 4.4 calculate nitrification                                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tNNitrS=afOxySed*tNNitrS_base                                                                                 ! calculate nitrification flux
      tO2NitrS=self%O2PerNH4S*molO2molN*tNNitrS                                                                     ! calculate O2 flux due to nitrification
      !=============================================================================================================!
      ! 4.5 calculate oxygen dependent P absorbtion                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      aPAdsMaxS =self%cRelPAdsDWS+afOxySed*self%cRelPAdsFeS*self%fFeDIM+self%cRelPAdsAlS*self%fAlDIMS               ! calculate max. P adsorption per g of inorg. matter
      aKPAdsS=(1.0_rk-self%fRedMaxS*(1.0_rk-afOxySed))*self%cKPAdsOxS                                               ! calculate P adsorption affinity, corrected for redox conditions
      aPIsoAdsS=aPAdsMaxS*aKPAdsS*oPO4S/(1.0_rk+aKPAdsS*oPO4S)                                                      ! calculate P adsorption isotherm onto inorg. matter in sediment
      aPEqIMS = aPIsoAdsS * sDIMS                                                                                   ! calculate equilibrium amount
      fPEqIMS = sPAIMS / max(aPEqIMS, NearZero)                                                                     ! calculate fraction of PAIMS is in equilibrium
      tPSorpIMS=self%kPSorpS*(aPEqIMS-sPAIMS)                                                                       ! calculate sorption
      tPChemPO4=max( 0.0_rk,self%kPChemPO4*(oPO4S-self%coPO4Max))                                                   ! calculate chem. loss of dissolved P from pore water
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   !  5. calculate Si mineralization                                                                                !
   !================================================================================================================!
      ! 5.1 SiO2 POM mineralization                                                                                 !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      uFunTmMinSiS = uFunTmArrh(uTm,self%cThetaMinSiS)                                                              ! remineralization Si temperature function
      tSiMinPaS = self%kSiMinPaS*uFunTmMinSiS*sSiPaS                                                                ! calculate upper sediment Si decomposition
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 6. final state variable ROC calculations                                                                       !
   !================================================================================================================!
      ! 6.1 total abiotic fluxes                                                                                    !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      tDAbioIMS   = 0.0_rk                                                                                          !
      tPAbioPO4S  = - tPSorpIMS - tPChemPO4                                                                         ! total ROC of PO4 in the sediment
      tPAbioAIMS  = tPSorpIMS                                                                                       ! total ROC of absorbed P in the sediment
      tNAbioNH4S  = - tNNitrS                                                                                       ! total ROC of NH4 in the sediment
      tNAbioNO3S  = tNNitrS - tNDenitS                                                                              ! total ROC of NO3 in the sediment
      tSiAbioPaS = - tSiMinPaS                                                                                      ! total ROC of POM Si in the sediment
      tSiO2AbioS  = tSiMinPaS                                                                                       ! total ROC of SiO2 in the sediment
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 7. calculate and update conversion between benthos and pelagic (from m-2 to m-3)                               !
   !================================================================================================================!
   if (self%hypsograph) then                                                                                        ! if running in a lake setup with a hypsograph
       _GET_(self%id_bot_pel_conv,bot_pel_conv)                                                                     !
       bot_pel_conv = 1.0_rk/bot_pel_conv                                                                           !
   else                                                                                                             ! else
       _GET_(self%id_dz,bot_pel_conv)                                                                               !    get layer depth
       bot_pel_conv = 1.0_rk/bot_pel_conv                                                                           !    calculate the conversion factor from per area to per m3
   endif                                                                                                            !
   _SET_HORIZONTAL_DIAGNOSTIC_(self%id_bot_pel_conv_out,bot_pel_conv)                                               !
   !%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%!
   ! 8. update variables                                                                                            !
   !================================================================================================================!
      ! 8.1 update sediment state variables                                                                         !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_ODE_(self%id_sDIMS,tDAbioIMS)                                                                     !
      _SET_BOTTOM_ODE_(self%id_sSiPaS,tSiAbioPaS)                                                                   !
      _SET_BOTTOM_ODE_(self%id_sNH4S,tNAbioNH4S)                                                                    !
      _SET_BOTTOM_ODE_(self%id_sNO3S,tNAbioNO3S)                                                                    !
      _SET_BOTTOM_ODE_(self%id_sPO4S,tPAbioPO4S)                                                                    !
      _SET_BOTTOM_ODE_(self%id_sPAIMS,tPAbioAIMS)                                                                   !
      _SET_BOTTOM_ODE_(self%id_sSiO2S,tSiO2AbioS)                                                                   !
      !=============================================================================================================!
      ! 8.2 update water column variables                                                                           !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      _SET_BOTTOM_EXCHANGE_(self%id_O2ConsSed, - tO2MinTOMS - tO2NitrS)                                             !
      !=============================================================================================================!
      ! 8.3 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 8.3.1 output local diagnostic variables                                                                  !
         !----------------------------------------------------------------------------------------------------------!
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_afOxySed,afOxySed)                                                     !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_aPEqIMS,aPEqIMS)                                                       !
         !::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
         ! 8.3.2 output diagnostic values for external usage                                                        !
         !----------------------------------------------------------------------------------------------------------!
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDAbioIMS,tDAbioIMS)                                                   !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDAbioO2S,(-tO2MinTOMS - tO2NitrS)*secs_pr_day)                        !
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_bPorS,self%bPorS)                                                      ! 
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_bPorCorS,self%bPorCorS)                                                ! 
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_cDepthS,self%cDepthS)                                                  ! 
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_fDepthDifS,self%fDepthDifS)                                            ! 
         _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tDPOMdummy,0.0_rk)                                                     !
      !=============================================================================================================!
      ! 8.4 update diagnostic variables                                                                             !
      !:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::!
      if (self%diagnostics) then                                                                                    !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPChemPO4,  tPChemPO4)                                                  !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tPSorpIMS,  tPSorpIMS)                                                  !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNNitrS,    tNNitrS)                                                    !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tNDenitS,   tNDenitS)                                                   !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tSiMinPaS,  tSiMinPaS)                                                  !
        _SET_HORIZONTAL_DIAGNOSTIC_(self%id_fPEqIMS,    fPEqIMS)                                                    !
      endif                                                                                                         !
   !================================================================================================================!
   _HORIZONTAL_LOOP_END_ !!! END OF MODEL CODE::
end subroutine do_bottom
!§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§
end module wet_abiotic_sediment
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
