#include "fabm_driver.h"
!*******************************************************************************
!* MODULE: INORGANIC CARBON (DIC) - WET greenhouse gas extension               *
!*                                                                             *
!* 模块功能：                                                                  *
!*   1. DIC（溶解性无机碳，gC/m3）与碱度（TA，mEq/m3）状态变量               *
!*   2. 淡水碳酸盐平衡（Plummer & Busenberg 1982 的 K1/K2，                   *
!*      二分法求解 pH，输出 pH / pCO2 / CO2* / HCO3- / CO3--）                *
!*   3. 气-水 CO2 交换（Cole & Caraco 1998 湖泊 k600-风速公式 +               *
!*      Wanninkhof 1992 Schmidt 数修正）                                       *
!*   4. 与 WET 食物网的碳通量耦合（关闭碳循环）：                             *
!*      - 浮游植物光合吸收 wCO2UptW / 呼吸释放 wCO2RespW（诊断量耦合）        *
!*      - 浮游动物呼吸 wCRespZoo、鱼类呼吸 tCRespFi                          *
!*      - 终端 DOM 矿化 wCMin（ formerly 直接消失的碳，现进入 DIC）           *
!*      - 大型植物生产/呼吸 tCProdVeg/tCRespVeg、底栖动物呼吸 tCRespBent     *
!*                                                                             *
!* 设计说明（为什么用诊断量耦合而不改既有模块）：                              *
!*   WET 上游在各模块中预留了注释掉的 CO2_pool_water 状态依赖钩子             *
!*   （标注 "to be used with GHG module enabled"）。本模块不改任何既有        *
!*   源码，仅通过 fabm.yaml 将既有模块已激活的 CO2/C 通量诊断变量耦合为       *
!*   DIC 的源/汇，实现碳循环闭合，且启用/停用完全由 yaml 配置控制。           *
!*******************************************************************************
   module wet_inorganic_carbon
   !USES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   use fabm_types
   use fabm_standard_variables
   use fabm_particle
   use wet_utility, ONLY: uFunTmArrh
   implicit none
   private

   !PUBLIC DERIVED TYPES::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   type, extends(type_particle_model),public :: type_wet_inorganic_carbon
      ! state variables--------------------------------------------------------------------------------------------------------------
      type (type_state_variable_id)                 :: id_sDICW, id_sAlkW
      ! diagnostic variables--------------------------------------------------------------------------------------------------------
      type (type_diagnostic_variable_id)            :: id_pH, id_pCO2W, id_CO2W, id_HCO3W, id_CO3W
      type (type_horizontal_diagnostic_variable_id) :: id_tCO2Flux, id_k600
      ! dependencies----------------------------------------------------------------------------------------------------------------
      type (type_dependency_id)                     :: id_uTm, id_salt
      type (type_horizontal_dependency_id)          :: id_uVWind, id_bot_pel_conv
      ! biological flux couplings (existing WET diagnostics)------------------------------------------------------------------------
      type (type_dependency_id),     allocatable, dimension(:) :: id_wCO2UptPhyt, id_wCO2RespPhyt   ! per phytoplankton group
      type (type_dependency_id),     allocatable, dimension(:) :: id_wCRespZoo, id_wCMinDOM        ! zooplankton respiration, terminal DOM mineralization
      type (type_dependency_id)                                   :: id_tCRespFi                    ! fish respiration (pelagic)
      type (type_horizontal_dependency_id), allocatable, dimension(:) :: id_tCProdMac, id_tCRespMac ! macrophyte production / respiration
      type (type_horizontal_dependency_id), allocatable, dimension(:) :: id_tCRespBent, id_tCRespBiv ! zoobenthos / bivalves respiration
      ! parameters------------------------------------------------------------------------------------------------------------------
      integer                                       :: nPHYT, nZOO, nDOM, nMAC, nBENT, nBIV
      logical                                       :: lFish
      real(rk)                                      :: cPco2Atm, hDICW

   contains
      procedure :: initialize
      procedure :: do
      procedure :: do_surface
      procedure :: do_bottom
   end type type_wet_inorganic_carbon

   !private data members-----------------------------------------------------------------------------------------------------------
   real(rk),parameter :: secs_pr_day=86400.0_rk
   real(rk),parameter :: NearZero = 0.000000000000000000000000000000001_rk
   real(rk),parameter :: gCpermol = 12.011_rk          ! gC per mol C
   real(rk),parameter :: molL_from_gCm3 = 1.0_rk/(gCpermol*1000.0_rk)  ! gC/m3 -> mol/L
   real(rk),parameter :: gCm3_from_molL = gCpermol*1000.0_rk           ! mol/L -> gC/m3

contains

!*******************************************************************************
subroutine initialize(self,configunit)
   class (type_wet_inorganic_carbon), intent(inout), target  :: self
   integer,                          intent(in)            :: configunit

   integer :: i_spec

   !REGISTER MODEL PARAMETERS::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   ! 组数参数：与案例 fabm.yaml 中的模块实例数一致（由 GUI 自动生成，参照 burial 模块的做法）
   call self%get_parameter(self%nPHYT,  'nPHYT',  '-', 'number of phytoplankton instances',            default=3)
   call self%get_parameter(self%nZOO,   'nZOO',   '-', 'number of zooplankton instances',              default=2)
   call self%get_parameter(self%nDOM,   'nDOM',   '-', 'number of terminal DOM instances (C mineralization in water)', default=1)
   call self%get_parameter(self%nMAC,   'nMAC',   '-', 'number of macrophyte instances',               default=1)
   call self%get_parameter(self%nBENT,  'nBENT',  '-', 'number of zoobenthos instances',               default=1)
   call self%get_parameter(self%nBIV,   'nBIV',   '-', 'number of bivalve instances',                  default=0)
   call self%get_parameter(self%lFish,  'lFish',  '-', 'couple fish respiration',                      default=.false.)
   call self%get_parameter(self%cPco2Atm,'cPco2Atm','ppm','atmospheric CO2 mole fraction',             default=420.0_rk)
   ! DIC 半饱和限制：仅当生物吸收汇超过所有来源、DIC 趋向负值时起保护作用（正常浓度 20 gC/m3 >> 0.1，影响可忽略）
   call self%get_parameter(self%hDICW,  'hDICW',  'g/m3','half-saturation DIC availability guard',     default=0.1_rk)

   !REGISTER STATE VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%register_state_variable(self%id_sDICW,'sDICW','g/m3','dissolved inorganic carbon', 20.0_rk, minimum=1.0e-6_rk)
   call self%register_state_variable(self%id_sAlkW,'sAlkW','mEq/m3','total alkalinity', 2000.0_rk, minimum=1.0_rk)

   !REGISTER DIAGNOSTIC VARIABLES::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%register_diagnostic_variable(self%id_pH,     'pH',     '-',      'pH (freshwater carbonate system)',     output=output_time_step_averaged,source=source_do)
   call self%register_diagnostic_variable(self%id_pCO2W,  'pCO2W',  'ppm',    'CO2 partial pressure in water',        output=output_time_step_averaged,source=source_do)
   call self%register_diagnostic_variable(self%id_CO2W,   'sCO2W',  'g/m3',   'free dissolved CO2',                   output=output_time_step_averaged,source=source_do)
   call self%register_diagnostic_variable(self%id_HCO3W,  'sHCO3W', 'g/m3',   'bicarbonate C',                        output=output_time_step_averaged,source=source_do)
   call self%register_diagnostic_variable(self%id_CO3W,   'sCO3W',  'g/m3',   'carbonate C',                          output=output_time_step_averaged,source=source_do)
   call self%register_diagnostic_variable(self%id_tCO2Flux,'tCO2Flux','g/m2/s','air-water CO2 flux (positive into water)',output=output_time_step_averaged,source=source_do_surface)
   call self%register_diagnostic_variable(self%id_k600,   'k600',   'm/d',    'gas transfer velocity k600',           output=output_time_step_averaged,source=source_do_surface)

   !REGISTER ENVIRONMENTAL DEPENDENCIES:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
   call self%register_dependency(self%id_uTm,  standard_variables%temperature)
   call self%register_dependency(self%id_salt, standard_variables%practical_salinity)
   call self%register_dependency(self%id_uVWind,standard_variables%wind_speed)

   !REGISTER BIOLOGICAL FLUX DEPENDENCIES (coupled in fabm.yaml to existing WET diagnostics):::::::::::::::::::::::::::::::::::::::
   allocate(self%id_wCO2UptPhyt(self%nPHYT),self%id_wCO2RespPhyt(self%nPHYT))
   do i_spec=1,self%nPHYT
      call self%register_dependency(self%id_wCO2UptPhyt(i_spec),'CO2_uptake_water_'//char(48+i_spec),      'g/m3/s','CO2 uptake by phytoplankton')
      call self%register_dependency(self%id_wCO2RespPhyt(i_spec),'CO2_respiration_water_'//char(48+i_spec),'g/m3/s','CO2 respiration by phytoplankton')
   end do
   allocate(self%id_wCRespZoo(self%nZOO))
   do i_spec=1,self%nZOO
      call self%register_dependency(self%id_wCRespZoo(i_spec),'C_respiration_zooplankton_'//char(48+i_spec),'g/m3/s','C respiration by zooplankton')
   end do
   allocate(self%id_wCMinDOM(self%nDOM))
   do i_spec=1,self%nDOM
      call self%register_dependency(self%id_wCMinDOM(i_spec),'C_mineralization_water_'//char(48+i_spec),    'g/m3/s','C mineralization of terminal DOM in water')
   end do
   if (self%lFish) then
      call self%register_dependency(self%id_tCRespFi,'C_respiration_fish','g/m3/s','C respiration by fish')
   end if
   allocate(self%id_tCProdMac(self%nMAC),self%id_tCRespMac(self%nMAC))
   do i_spec=1,self%nMAC
      call self%register_horizontal_dependency(self%id_tCProdMac(i_spec),'C_production_macrophyte_'//char(48+i_spec),   'g/m2/s','C production by macrophytes')
      call self%register_horizontal_dependency(self%id_tCRespMac(i_spec),'C_respiration_macrophyte_'//char(48+i_spec), 'g/m2/s','C respiration by macrophytes')
   end do
   allocate(self%id_tCRespBent(self%nBENT))
   do i_spec=1,self%nBENT
      call self%register_horizontal_dependency(self%id_tCRespBent(i_spec),'C_respiration_zoobenthos_'//char(48+i_spec),'g/m2/s','C respiration by zoobenthos')
   end do
   allocate(self%id_tCRespBiv(self%nBIV))
   do i_spec=1,self%nBIV
      call self%register_horizontal_dependency(self%id_tCRespBiv(i_spec),'C_respiration_bivalves_'//char(48+i_spec),'g/m2/s','C respiration by bivalves')
   end do
   call self%register_horizontal_dependency(self%id_bot_pel_conv,'bot_pel_conv','-','bottom/pelagic conversion factor')

end subroutine initialize

!*******************************************************************************
!* DO (pelagic): 碳酸盐平衡诊断 + 生物源汇                                     *
!*******************************************************************************
subroutine do(self,_ARGUMENTS_DO_)
   class (type_wet_inorganic_carbon), intent(in)    :: self
   _DECLARE_ARGUMENTS_DO_

   real(rk) :: uTm, sDICW, sAlkW
   real(rk) :: pH, pCO2W, CO2W, HCO3W, CO3W
   real(rk) :: wCUpt, wCResp, wCMin, wCDIC, aGuard
   integer  :: i_spec

   _LOOP_BEGIN_
   ! 1. 环境与状态变量
   _GET_(self%id_uTm,uTm)
   _GET_(self%id_sDICW,sDICW)
   _GET_(self%id_sAlkW,sAlkW)

   ! 2. 淡水碳酸盐平衡（二分法，绝不发散）
   call CarbonateEq(sDICW,sAlkW,uTm,pH,pCO2W,CO2W,HCO3W,CO3W)
   _SET_DIAGNOSTIC_(self%id_pH,pH)
   _SET_DIAGNOSTIC_(self%id_pCO2W,pCO2W)
   _SET_DIAGNOSTIC_(self%id_CO2W,CO2W)
   _SET_DIAGNOSTIC_(self%id_HCO3W,HCO3W)
   _SET_DIAGNOSTIC_(self%id_CO3W,CO3W)

   ! 3. 生物碳通量（读取既有 WET 模块的诊断通量，gC/m3/s）
   wCDIC = 0.0_rk
   do i_spec=1,self%nPHYT
      _GET_(self%id_wCO2RespPhyt(i_spec),wCResp)
      _GET_(self%id_wCO2UptPhyt(i_spec),wCUpt)
      wCDIC = wCDIC + wCResp - wCUpt
   end do
   do i_spec=1,self%nZOO
      _GET_(self%id_wCRespZoo(i_spec),wCResp)
      wCDIC = wCDIC + wCResp
   end do
   do i_spec=1,self%nDOM
      _GET_(self%id_wCMinDOM(i_spec),wCMin)
      wCDIC = wCDIC + wCMin
   end do
   if (self%lFish) then
      _GET_(self%id_tCRespFi,wCResp)
      wCDIC = wCDIC + wCResp
   end if

   ! 4. 正值保护：当净通量为汇时用半饱和形式限制（正常浓度下影响 <0.5%）。
   !    为什么需要：外部诊断通量（如浮游植物吸收）不随 DIC 本身减小，
   !    Patankar 正性积分器无法保护状态变量被外部汇抽成负值。
   if (wCDIC < 0.0_rk) then
      aGuard = sDICW/(self%hDICW + sDICW)
      wCDIC = wCDIC * aGuard
   end if
   _SET_ODE_(self%id_sDICW,wCDIC)

   _LOOP_END_
end subroutine do

!*******************************************************************************
!* DO SURFACE: 气-水 CO2 交换                                                  *
!*   k600 (cm/h) = 2.07 + 0.215*U10^1.7   (Cole & Caraco 1998, 湖泊)          *
!*   Sc(CO2) = 1911.1 - 118.63*T + 3.4527*T^2 - 0.04132*T^3 (Wanninkhof 1992) *
!*   k = k600*(600/Sc)^0.5；通量 = k*(CO2饱和 - CO2水体)，正值为进入水体      *
!*******************************************************************************
subroutine do_surface(self,_ARGUMENTS_DO_SURFACE_)
   class (type_wet_inorganic_carbon), intent(in) :: self
   _DECLARE_ARGUMENTS_DO_SURFACE_

   real(rk) :: uTm, uVWind, sDICW, sAlkW
   real(rk) :: pH, pCO2W, CO2W, HCO3W, CO3W
   real(rk) :: k600, ScCO2, kCO2, CO2Sat, tCO2Flux

   _HORIZONTAL_LOOP_BEGIN_
   _GET_(self%id_uTm,uTm)
   _GET_HORIZONTAL_(self%id_uVWind,uVWind)
   _GET_(self%id_sDICW,sDICW)
   _GET_(self%id_sAlkW,sAlkW)

   ! 表层碳酸盐平衡，得到游离 CO2（gC/m3）
   call CarbonateEq(sDICW,sAlkW,uTm,pH,pCO2W,CO2W,HCO3W,CO3W)

   ! 气体传输速度
   ScCO2 = 1911.1_rk - 118.63_rk*uTm + 3.4527_rk*uTm*uTm - 0.04132_rk*uTm*uTm*uTm
   if (ScCO2 < 100.0_rk) ScCO2 = 100.0_rk
   k600   = (2.07_rk + 0.215_rk*max(uVWind,0.0_rk)**1.7_rk)*0.24_rk        ! cm/h -> m/d
   kCO2   = k600*sqrt(600.0_rk/ScCO2)
   CO2Sat = HenryCO2(uTm)*(self%cPco2Atm*1.0e-6_rk)*gCm3_from_molL          ! 大气平衡浓度 gC/m3
   tCO2Flux = kCO2*(CO2Sat - CO2W)/secs_pr_day                               ! gC/m2/s，正=入水

   _SET_SURFACE_EXCHANGE_(self%id_sDICW,tCO2Flux)
   _SET_HORIZONTAL_DIAGNOSTIC_(self%id_tCO2Flux,tCO2Flux)
   _SET_HORIZONTAL_DIAGNOSTIC_(self%id_k600,k600)

   _HORIZONTAL_LOOP_END_
end subroutine do_surface

!*******************************************************************************
!* DO BOTTOM: 底部生物呼吸通量进入底层网格（大型植物/底栖/贝类）               *
!*******************************************************************************
subroutine do_bottom(self,_ARGUMENTS_DO_BOTTOM_)
   class (type_wet_inorganic_carbon), intent(in) :: self
   _DECLARE_ARGUMENTS_DO_BOTTOM_

   real(rk) :: bot_pel_conv, tCProd, tCResp, tCBot, sDICW, aGuard
   integer  :: i_spec

   _HORIZONTAL_LOOP_BEGIN_
   _GET_(self%id_sDICW,sDICW)
   _GET_HORIZONTAL_(self%id_bot_pel_conv,bot_pel_conv)

   tCBot = 0.0_rk
   do i_spec=1,self%nMAC
      _GET_HORIZONTAL_(self%id_tCProdMac(i_spec),tCProd)
      _GET_HORIZONTAL_(self%id_tCRespMac(i_spec),tCResp)
      tCBot = tCBot + tCResp - tCProd
   end do
   do i_spec=1,self%nBENT
      _GET_HORIZONTAL_(self%id_tCRespBent(i_spec),tCResp)
      tCBot = tCBot + tCResp
   end do
   do i_spec=1,self%nBIV
      _GET_HORIZONTAL_(self%id_tCRespBiv(i_spec),tCResp)
      tCBot = tCBot + tCResp
   end do

   ! 与 pelagic 相同的正值保护（净汇时限制）
   if (tCBot < 0.0_rk) then
      aGuard = sDICW/(self%hDICW + sDICW)
      tCBot = tCBot * aGuard
   end if
   _SET_BOTTOM_EXCHANGE_(self%id_sDICW,tCBot*bot_pel_conv)

   _HORIZONTAL_LOOP_END_
end subroutine do_bottom

!*******************************************************************************
!* 淡水碳酸盐平衡：由 DIC(gC/m3) 与 TA(mEq/m3) 求解 pH 及各组分               *
!*   K1/K2: Plummer & Busenberg (1982) 淡水常数（PHREEQC 采用）               *
!*   KW: 1e-14（湖泊温度范围内足够）                                           *
!*   亨利常数: kH = 0.034*exp(2400*(1/Tk - 1/298.15)) mol/L/atm               *
!*   二分法在 pH∈[2,12] 内求根，100 次迭代，无条件收敛                        *
!*******************************************************************************
pure subroutine CarbonateEq(sDICW,sAlkW,uTm,pH,pCO2W,CO2W,HCO3W,CO3W)
   real(rk), intent(in)  :: sDICW, sAlkW, uTm
   real(rk), intent(out) :: pH, pCO2W, CO2W, HCO3W, CO3W

   real(rk) :: Tk, K1, K2, KW, kH, CT, TA, H, Hlo, Hhi, f, denom
   integer  :: it

   Tk  = uTm + 273.15_rk
   K1  = 10.0_rk**(-356.3094_rk - 0.06091964_rk*Tk + 21834.37_rk/Tk + 126.8339_rk*log10(Tk))
   K2  = 10.0_rk**(-107.8871_rk - 0.03252849_rk*Tk + 5151.79_rk/Tk + 38.92561_rk*log10(Tk))
   KW  = 1.0e-14_rk
   kH  = HenryCO2(uTm)

   CT  = sDICW*molL_from_gCm3           ! mol/L
   TA  = sAlkW*1.0e-6_rk                ! mol-eq/L
   CT  = max(CT,NearZero)

   ! TA(H) 随 H 单调递减：TA = CT*K1*H/D + 2*CT*K1*K2/D + KW/H - H
   Hlo = 1.0e-12_rk                     ! pH 12
   Hhi = 1.0e-2_rk                      ! pH 2
   do it=1,100
      H = 0.5_rk*(Hlo + Hhi)
      denom = H*H + K1*H + K1*K2
      f = CT*K1*H/denom + 2.0_rk*CT*K1*K2/denom + KW/H - H - TA
      if (f > 0.0_rk) then
         Hlo = H                        ! TA 偏大 -> 需要更大的 H
      else
         Hhi = H
      end if
   end do
   H = 0.5_rk*(Hlo + Hhi)

   pH    = -log10(H)
   denom = H*H + K1*H + K1*K2
   CO2W  = CT*H*H/denom*gCm3_from_molL
   HCO3W = CT*K1*H/denom*gCm3_from_molL
   CO3W  = CT*K1*K2/denom*gCm3_from_molL
   pCO2W = (CT*H*H/denom)/kH*1.0e6_rk   ! ppm
end subroutine CarbonateEq

!*******************************************************************************
!* CO2 亨利常数（淡水）：0.034 mol/L/atm @25C，van 't Hoff 温度依赖            *
!*******************************************************************************
pure real(rk) function HenryCO2(uTm)
   real(rk), intent(in) :: uTm
   HenryCO2 = 0.034_rk*exp(2400.0_rk*(1.0_rk/(uTm+273.15_rk) - 1.0_rk/298.15_rk))
end function HenryCO2

end module wet_inorganic_carbon
!------------------------------------------------------------------------------
! Copyright by the WET-team under the GNU Public License - www.gnu.org
!------------------------------------------------------------------------------
