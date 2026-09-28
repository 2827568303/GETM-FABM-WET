#include "fabm_driver.h"
!*******************************************************************************
!* MODULE: METHANE (CH4) - WET greenhouse gas extension                        *
!*                                                                             *
!* 模块功能（状态变量 sCH4W 以 gCH4-C/m3 计，即甲烷中的碳；×16/12 得 gCH4）：  *
!*   1. 沉积物甲烷产生：沉积物有机碳矿化通量（om_pool 的 tCTrans）在缺氧      *
!*      区（1-afOxySed）按比例 fMeth 转化为 CH4（甲烷化）                      *
!*   2. 冒泡（ebullition）：浅水湖泊中大部分 CH4 以气泡形式直接逸出，         *
!*      比例 fEbul 不经过水柱                                                  *
!*   3. 水柱有氧氧化：CH4 + 2O2 -> CO2 + 2H2O，受 O2 半饱和与温度控制，       *
!*      氧化的碳进入 DIC（耦合 inorganic_carbon/sDICW），耗氧进入 sO2W        *
!*   4. 气-水扩散逸出：k600 风速公式（Cole & Caraco 1998）+ CH4 Schmidt 数    *
!*      （Wanninkhof 1992）                                                    *
!*   5. 碳循环闭合：沉积物矿化碳的其余部分（含全部含氧区矿化）以 DIC 形式     *
!*      进入底层水体（_SET_BOTTOM_EXCHANGE_ 到 inorganic_carbon/sDICW）       *
!*                                                                             *
!* 科学依据：                                                                  *
!*   - 甲烷化比例与冒泡比例：Liikanen et al. (2002); Bastviken (2008)         *
!*     浅水富营养湖泊冒泡占比通常 0.4-0.9                                     *
!*   - CH4 氧化速率常数 0.01-3 /d（20C），典型湖泊水柱氧化去除 30-90%         *
!*   - CH4 亨利常数 1.4e-3 mol/L/atm @25C，van 't Hoff 指数 ~1700 K           *
!*******************************************************************************
   module wet_methane
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_standard_variables
   use fabm_particle
   use wet_utility, ONLY: uFunTmArrh
   implicit none
   private

   !PUBLIC DERIVED TYPES::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public :: type_wet_methane
      ! state variables--------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                 :: id_sCH4W
      ! diagnostic variables--------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)            :: id_wCH4Oxid
      type (type_horizontal_diagnostic_variable_id) :: id_tCH4Prod, id_tCH4Ebul, id_tCH4Diff
      ! dependencies----------------------------------------------------------------------------------------------------------------
      type (type_dependency_id)                     :: id_uTm
      type (type_state_variable_id)                 :: id_sDICW, id_sO2W            ! coupled to inorganic_carbon/sDICW, abiotic_water/sO2W
      type (type_horizontal_dependency_id)          :: id_uVWind, id_bot_pel_conv, id_afOxySed
      type (type_horizontal_dependency_id), allocatable, dimension(:) :: id_tCMinOM  ! sediment C mineralization (om_pool tCTrans)
      ! parameters------------------------------------------------------------------------------------------------------------------
      integer                                       :: nOM
      real(rk)                                      :: fMeth, fEbul, kCH4Oxid, cThetaCH4Oxid, hO2CH4Oxid, cPch4Atm

   contains
      procedure :: initialize
      procedure :: do
      procedure :: do_surface
      procedure :: do_bottom
   end type type_wet_methane

   !private data members-----------------------------------------------------------------------------------------------------------
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk),parameter :: molO2molCH4C = 2.0_rk*32.0_rk/12.011_rk   ! CH4+2O2->CO2+2H2O: gO2 / gC
   real(rk),parameter :: gCpermol = 12.011_rk

contains

!*******************************************************************************
subroutine initialize(self,configunit)
   class (type_wet_methane), intent(inout), target  :: self
   integer,                 intent(in)            :: configunit

   integer :: i_spec

   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%get_parameter(self%nOM,           'nOM',           '-',   'number of sediment OM instances providing C mineralization', default=2)
   ! 甲烷化比例：缺氧区矿化碳转化为 CH4 的比例（0.3-0.7，Liikanen et al. 2002）
   call self%get_parameter(self%fMeth,         'fMeth',         '-',   'fraction of anoxic C mineralization converted to CH4',     default=0.5_rk)
   ! 冒泡比例：浅水富营养湖 0.4-0.9（Bastviken 2008）；直接逸出大气、不经过水柱
   call self%get_parameter(self%fEbul,         'fEbul',         '-',   'fraction of CH4 production emitted by ebullition',         default=0.6_rk)
   ! CH4 氧化：一级动力学 0.01-3 /d @20C，Q10~2（cTheta=1.07 等效 Arrhenius）
   call self%get_parameter(self%kCH4Oxid,      'kCH4Oxid',      '1/d', 'CH4 oxidation rate constant at 20 C',                     default=0.5_rk, scale_factor=1.0_rk/secs_pr_day)
   call self%get_parameter(self%cThetaCH4Oxid, 'cThetaCH4Oxid', '1/e^*C','temperature coefficient CH4 oxidation',               default=1.07_rk)
   call self%get_parameter(self%hO2CH4Oxid,    'hO2CH4Oxid',    'g/m3','half-saturation O2 for CH4 oxidation',                  default=0.5_rk)
   call self%get_parameter(self%cPch4Atm,      'cPch4Atm',      'ppm', 'atmospheric CH4 mole fraction',                           default=1.9_rk)

   !REGISTER STATE VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%register_state_variable(self%id_sCH4W,'sCH4W','g/m3','methane C in water', 0.01_rk, minimum=1.0e-9_rk)

   !REGISTER DIAGNOSTIC VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%register_diagnostic_variable(self%id_wCH4Oxid,'wCH4Oxid','g/m3/s','CH4 oxidation rate in water',      output=output_time_step_averaged,source=source_do)
   call self%register_diagnostic_variable(self%id_tCH4Prod,'tCH4Prod','g/m2/s','CH4 production in sediment',       output=output_time_step_averaged,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tCH4Ebul,'tCH4Ebul','g/m2/s','CH4 ebullition flux',              output=output_time_step_averaged,source=source_do_bottom)
   call self%register_diagnostic_variable(self%id_tCH4Diff,'tCH4Diff','g/m2/s','CH4 diffusive emission at surface',output=output_time_step_averaged,source=source_do_surface)

   !REGISTER ENVIRONMENTAL DEPENDENCIES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%register_dependency(self%id_uTm,   standard_variables%temperature)
   call self%register_dependency(self%id_uVWind,standard_variables%wind_speed)

   !REGISTER BIOGEOCHEMICAL DEPENDENCIES (coupled in fabm.yaml)::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%register_state_dependency(self%id_sDICW,'DIC_pool_water','g/m3','dissolved inorganic carbon pool')
   call self%register_state_dependency(self%id_sO2W, 'oxygen_pool_water','g/m3','oxygen pool in water')
   call self%register_horizontal_dependency(self%id_afOxySed,'aerobic_fraction_sediment','-','fraction of aerobic sediment')
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')

   allocate(self%id_tCMinOM(self%nOM))
   do i_spec=1,self%nOM
      call self%register_horizontal_dependency(self%id_tCMinOM(i_spec),'C_mineralization_sediment_'//char(48+i_spec),'g/m2/s','C mineralization in sediment by OM pool')
   end do

end subroutine initialize

!*******************************************************************************
!* DO (pelagic): 水柱有氧氧化                                                 *
!*   CH4 + 2O2 -> CO2 + 2H2O：氧化碳进入 DIC，按 64/12 gO2/gC 耗氧            *
!*******************************************************************************
subroutine do(self,_ARGUMENTS_DO_)
   class (type_wet_methane), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_

   real(rk) :: uTm, sCH4W, sO2W, aCorO2, wCH4Oxid

   _LOOP_BEGIN_
   _GET_(self%id_uTm,uTm)
   _GET_(self%id_sCH4W,sCH4W)
   _GET_(self%id_sO2W,sO2W)

   ! O2 半饱和限制 + Arrhenius 温度函数（20C 参考）
   aCorO2   = sO2W/(self%hO2CH4Oxid + sO2W)
   wCH4Oxid = self%kCH4Oxid*uFunTmArrh(uTm,self%cThetaCH4Oxid)*aCorO2*sCH4W

   _SET_ODE_(self%id_sCH4W,-wCH4Oxid)
   _SET_ODE_(self%id_sDICW, wCH4Oxid)                       ! 氧化的碳 -> DIC
   _SET_ODE_(self%id_sO2W, -wCH4Oxid*molO2molCH4C)          ! 耗氧
   _SET_DIAGNOSTIC_(self%id_wCH4Oxid,wCH4Oxid)

   _LOOP_END_
end subroutine do

!*******************************************************************************
!* DO SURFACE: CH4 扩散逸出                                                   *
!*   Sc(CH4) = 1897.7 - 114.28*T + 3.2902*T^2 - 0.039061*T^3 (Wanninkhof 1992)*
!*   k = k600*(600/Sc)^0.5；逸出通量 = k*(CH4水体 - CH4饱和)，正值为逸出      *
!*******************************************************************************
subroutine do_surface(self,_ARGUMENTS_DO_SURFACE_)
   class (type_wet_methane), intent(in) :: self
   _DECLARE_ARGUMENTS_DO_SURFACE_

   real(rk) :: uTm, uVWind, sCH4W, ScCH4, k600, kCH4, CH4Sat, tCH4Diff

   _HORIZONTAL_LOOP_BEGIN_
   _GET_(self%id_uTm,uTm)
   _GET_HORIZONTAL_(self%id_uVWind,uVWind)
   _GET_(self%id_sCH4W,sCH4W)

   ScCH4 = 1897.7_rk - 114.28_rk*uTm + 3.2902_rk*uTm*uTm - 0.039061_rk*uTm*uTm*uTm
   if (ScCH4 < 100.0_rk) ScCH4 = 100.0_rk
   k600    = (2.07_rk + 0.215_rk*max(uVWind,0.0_rk)**1.7_rk)*0.24_rk      ! cm/h -> m/d
   kCH4    = k600*sqrt(600.0_rk/ScCH4)
   CH4Sat  = HenryCH4(uTm)*(self%cPch4Atm*1.0e-6_rk)*gCpermol*1000.0_rk   ! gC/m3
   tCH4Diff= kCH4*(sCH4W - CH4Sat)/secs_pr_day                             ! gC/m2/s，正=逸出

   _SET_SURFACE_EXCHANGE_(self%id_sCH4W,-tCH4Diff)
   _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCH4Diff,tCH4Diff)

   _HORIZONTAL_LOOP_END_
end subroutine do_surface

!*******************************************************************************
!* DO BOTTOM: 沉积物 CH4 产生、冒泡与 DIC 分配                                *
!*   产生: P = fMeth*(1-afOxySed)*sum(tCMin_OM)                              *
!*   冒泡: E = fEbul*P （直接进大气，诊断量输出）                              *
!*   入水柱: (1-fEbul)*P 进入底层网格                                         *
!*   其余矿化碳 -> DIC 进入底层网格（碳循环闭合）                              *
!*******************************************************************************
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   class (type_wet_methane), intent(in) :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_

   real(rk) :: afOxySed, bot_pel_conv, tCMin, tCMinTot, tCH4Prod, tCH4Ebul
   integer  :: i_spec

   _HORIZONTAL_LOOP_BEGIN_
   _GET_HORIZONTAL_(self%id_afOxySed,afOxySed)
   _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)
   afOxySed = min(1.0_rk, max(0.0_rk, afOxySed))

   tCMinTot = 0.0_rk
   do i_spec=1,self%nOM
      _GET_HORIZONTAL_(self%id_tCMinOM(i_spec),tCMin)
      tCMinTot = tCMinTot + tCMin
   end do

   ! 沉积物 CH4 产生与冒泡
   tCH4Prod = self%fMeth*(1.0_rk - afOxySed)*tCMinTot
   tCH4Ebul = self%fEbul*tCH4Prod

   ! CH4 进入底层水柱（溶解态），其余冒泡直接进大气
   _SET_BOTTOM_EXCHANGE_(self%id_sCH4W,(tCH4Prod - tCH4Ebul)*bot_pel_conv)
   ! 非甲烷化的矿化碳 -> DIC 进入底层水柱
   _SET_BOTTOM_EXCHANGE_(self%id_sDICW,(tCMinTot - tCH4Prod)*bot_pel_conv)

   _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCH4Prod,tCH4Prod)
   _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCH4Ebul,tCH4Ebul)

   _HORIZONTAL_LOOP_END_
end subroutine do_bottom

!*******************************************************************************
!* CH4 亨利常数（淡水）：1.4e-3 mol/L/atm @25C，van 't Hoff 指数 1700 K        *
!*******************************************************************************
pure real(rk) function HenryCH4(uTm)
   real(rk), intent(in) :: uTm
   HenryCH4 = 0.0014_rk*exp(1700.0_rk*(1.0_rk/(uTm+273.15_rk) - 1.0_rk/298.15_rk))
end function HenryCH4

end module wet_methane
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
