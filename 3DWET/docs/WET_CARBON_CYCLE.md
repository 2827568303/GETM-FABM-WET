# WET 模型碳循环完整说明

> **文档定位**：全面剖析 WET 模型中的碳循环实现，对比完整湖泊碳循环理论，识别 WET 已实现与缺失的过程，并提出在 3DWET 中完善碳循环的具体方程与实现路径。
> **核心结论**：WET 模型实现了**完整的有机碳循环**（生物量碳 sC + POC + DOC + 埋藏），但**无机碳循环（DIC/CO₂/碳酸盐系统）和温室气体排放（CO₂ 大气交换、CH₄ 产生/氧化/排放）完全未启用**——所有相关代码被注释，标注 "until GHG module implemented"。模型当前**碳不守恒**：呼吸/矿化产生的 CO₂ 既不进入 DIC 池，也不计入任何出流通量。

---

## 目录

- [一、完整湖泊碳循环过程（理论参考）](#一完整湖泊碳循环过程理论参考)
- [二、WET 模型中已实现的碳循环过程](#二wet-模型中已实现的碳循环过程)
- [三、WET 模型中缺失的碳循环过程](#三wet-模型中缺失的碳循环过程)
- [四、3DWET 完善碳循环的实施方案](#四3dwet-完善碳循环的实施方案)
- [五、关键化学计量参数](#五关键化学计量参数)
- [六、碳守恒分析与质量平衡](#六碳守恒分析与质量平衡)
- [七、参考文献](#七参考文献)

---

## 一、完整湖泊碳循环过程（理论参考）

完整的湖泊碳循环包含 **无机碳系统、有机碳系统、钙化系统、温室气体排放、沉积物碳循环** 五大子系统，涉及源、汇、内部转化三大类过程。

### 1.1 无机碳系统（DIC 系统）

**碳酸平衡（三级电离）：**

```
CO₂(g) ⇌ CO₂(aq)                    Henry 定律
CO₂(aq) + H₂O ⇌ H₂CO₃               水合反应 (K_h ≈ 1.7×10⁻³)
H₂CO₃ ⇌ H⁺ + HCO₃⁻                  一级电离 (pK₁ ≈ 6.35, 25°C)
HCO₃⁻ ⇌ H⁺ + CO₃²⁻                  二级电离 (pK₂ ≈ 10.33, 25°C)
```

**DIC 定义：**
```
DIC = [CO₂*] + [HCO₃⁻] + [CO₃²⁻]
其中 [CO₂*] = [CO₂(aq)] + [H₂CO₃] ≈ [CO₂(aq)]
```

**总碱度（TAlk）：**
```
TAlk = [HCO₃⁻] + 2[CO₃²⁻] + [OH⁻] - [H⁺] + [B(OH)₄⁻] + ...
```

**pH 控制三大机制**（Middelburg 2024）：
1. 化学平衡（碳酸盐平衡）
2. 生态系统代谢（NEP = GPP − R：光合升 pH，呼吸降 pH）
3. 钙化作用（消耗碱度，释放 CO₂）

### 1.2 有机碳系统

**POC（颗粒有机碳）**：
- 来源：浮游植物现存量、碎屑、陆源输入、微生物团聚体
- 去除：沉降、摄食、矿化分解
- C:N:P（Redfield 比）≈ 106:16:1

**DOC（溶解有机碳）**：
- 来源：浮游植物胞外释放、有机质降解、陆源输入
- 去除：生物降解、光降解、UV 矿化

**POC ↔ DOC 相互转化**：渗滤、酶解、微生物同化、凝结

### 1.3 钙化系统（Calcite System）

**核心反应**：
```
Ca²⁺ + 2HCO₃⁻ ⇌ CaCO₃(s) + CO₂ + H₂O
```

**方解石饱和度**：
```
Ω = [Ca²⁺][CO₃²⁻] / K_sp      (K_sp ≈ 3.3×10⁻⁹, 25°C)
```
- Ω > 1：过饱和，发生沉淀（钙化）
- Ω < 1：欠饱和，发生溶解

**化学计量**：每沉淀 1 mol CaCO₃ → 消耗 2 mol 碱度 + 释放 1 mol CO₂

**白化事件（whiting event）**：夏季高温 + 光合作用旺盛时，pH 升高使 Ω 急剧增大，方解石快速沉淀，水体变浑浊。

> **2024 年突破性发现**（Many et al. 2024, *Sci. Adv.*）：钙化是湖泊 CO₂ 排放的关键过程。日内瓦湖净生产量为 +105 Gg C/yr，但仍是 CO₂ 排放源（~12 Gg C/yr），其中钙化贡献约 20 Gg C/yr。

### 1.4 温室气体排放

#### 1.4.1 CO₂ 水-气交换

**基本公式**：
```
F_CO₂ = k · K₀ · (pCO₂_water − pCO₂_air)
```
- F：通量（mmol C m⁻² d⁻¹），正值=向大气排放
- k：气体传输速度（m/d）
- K₀：CO₂ 溶解度系数（Henry 常数，mol L⁻¹ atm⁻¹）
- pCO₂_water：水体 CO₂ 分压（µatm）
- pCO₂_air：大气 CO₂ 分压（~420 µatm，2024）

**Henry 定律**：[CO₂(aq)] = K₀ · pCO₂

**Weiss (1974) K₀ 经验式**（淡水 S=0）：
```
ln K₀ = -58.0931 + 90.5069·(100/T) + 22.2940·ln(T/100) + 0.027766·(100/T)²
```
（T 为绝对温度 K）

**Cole & Caraco (1998) k600 公式**（湖泊最常用）：
```
k600 [cm/h] = 2.07 + 0.215 · U₁₀^1.7
```

**温度校正至其他气体**：
```
k_gas = k600 · (Sc_gas / 600)^(-n)
```
- n = 0.5（U₁₀ > 3.6 m/s，波浪破碎）
- n = 0.667（U₁₀ < 3.6 m/s，平滑表面）

#### 1.4.2 CH₄ 排放（三大途径）

**甲烷产生（Methanogenesis）**：
```
乙酸营养型：CH₃COOH → CH₄ + CO₂                        (淡水湖主导, 60-70%)
氢营养型：  CO₂ + 4H₂ → CH₄ + 2H₂O                     (深层沉积物)
甲基营养型：4CH₃OH → 3CH₄ + CO₂ + 2H₂O                (盐湖/碱湖)
```

**甲烷氧化**：
```
好氧氧化：  CH₄ + 2O₂ → CO₂ + 2H₂O
厌氧氧化(AOM)：CH₄ + 4SO₄²⁻ → HCO₃⁻ + HS⁻ + H₂O      (硫酸盐型, 高盐湖)
              3CH₄ + 8NO₂⁻ + 8H⁺ → 3CO₂ + 4N₂ + 10H₂O (反硝化型, 淡水湖主导)
```

**三大排放途径**：
1. **扩散传输**：沉积物→上覆水→大气（沿途好氧氧化消耗 50-90%）
2. **气泡传输（ebullition）**：沉积物 CH₄ 过饱和形成气泡直接上浮（主导深水湖，10-1000 mg CH₄ m⁻² d⁻¹）
3. **植物介导传输**：挺水植物通气组织（aerenchyma）输送（浅水湖主导；凤眼莲入侵区可达开阔水域 17 倍）

**产甲烷动力学**：
```
R_CH₄ = R_max · [S]/(K_s + [S]) · Q₁₀^((T-20)/10) · f(O₂)
```
- Q₁₀ = 2-8（高于一般生物过程）
- f(O₂)：严格厌氧，O₂ < 0.1-1 mg/L 时 f → 1

#### 1.4.3 N₂O 排放

**产生途径**：硝化副产物、反硝化中间产物、硝化-反硝化耦合
- 控制因素：低-中 O₂、高 NO₃⁻/NH₄⁺、低 pH

### 1.5 沉积物碳循环

**有机碳埋藏**：
- 湖泊埋藏效率 BE = 20-80%（高于海洋 0.1-10%）
- 全球湖泊埋藏量 ~0.06 Pg C/yr

**沉积物矿化（按电子受体顺序）**：
```
有氧矿化：    CH₂O + O₂ → CO₂ + H₂O
反硝化：      5CH₂O + 4NO₃⁻ → 5CO₂ + 2N₂ + 3H₂O
锰还原：      CH₂O + 2MnO₂ + 4H⁺ → CO₂ + 2Mn²⁺ + 3H₂O
铁还原：      CH₂O + 4Fe(OH)₃ + 7H⁺ → CO₂ + 4Fe²⁺ + 10H₂O
硫酸盐还原：  2CH₂O + SO₄²⁻ → 2HCO₃⁻ + H₂S
产甲烷：      CH₃COOH → CH₄ + CO₂  (最终环节)
```

### 1.6 完整湖泊碳收支模型

```
dC_lake/dt = F_river,in + F_GW,in + F_atm,inv         [源]
           − F_river,out − F_atm,eva − F_burial        [汇]
           + GPP − R_eco                               [内部代谢]
           + F_calc                                     [钙化]
```

---

## 二、WET 模型中已实现的碳循环过程

WET 模型实现了**完整的有机碳循环体系**，但所有无机碳和温室气体相关代码均被注释。已实现过程清单如下：

### 2.1 含碳(C)状态变量

| 变量名 | 单位 | 维度 | 所在模块 | 文件位置 |
|--------|------|------|----------|----------|
| `sCW`（浮游植物） | gC/m³ | 3D 浮游 | phytoplankton | [phytoplankton.F90:156](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/phytoplankton.F90#L156) |
| `sCS`（浮游植物沉降） | gC/m² | 2D 底栖 | phytoplankton | [phytoplankton.F90:166](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/phytoplankton.F90#L166) |
| `sCW`（有机质池） | gC/m³ | 3D 浮游 | om_pool | [om_pool.F90:132](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/om_pool.F90#L132) |
| `sCS`（有机质池沉积物） | gC/m² | 2D 底栖 | om_pool | [om_pool.F90:142](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/om_pool.F90#L142) |
| `sCZoo` | gC/m³ | 3D 浮游 | zooplankton | [zooplankton.F90:127](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/zooplankton.F90#L127) |
| `sCVeg` | gC/m² | 2D 底栖 | macrophytes | [macrophytes.F90:160](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/macrophytes.F90#L160) |
| `sCBent` | gC/m² | 2D 底栖 | zoobenthos | [zoobenthos.F90:119](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/zoobenthos.F90#L119) |
| `sCFi` | gC/m³ | 3D 浮游 | fish | [fish.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/fish.F90) |
| `sCBiv` | gC/m² | 2D 底栖 | bivalves | [bivalves.F90:165](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/bivalves.F90#L165) |
| `POM_C_X`（多组 POM 碳） | gC/m²/m³ | 3D+2D | om_pool + burial + sediment_exchange | [burial.F90:152](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/burial.F90#L152) |
| `DOM_C_X`（多组 DOM 碳） | gC/m²/m³ | 3D+2D | om_pool + burial + sediment_exchange | [burial.F90:187](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/burial.F90#L187) |
| `humus_C_in_deep_sediment` | gC/m² | 2D 深层 | burial | [burial.F90:91](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/burial.F90#L91) |

**设计要点**：
- 每个生物模块维护 `sC*` 与 `sC*_PV` 两个变量（`_PV` 为 3D 浮游镜像，`disable_transport=.true.`）
- POM/DOM 通过 `nPOM`、`nDOM` 参数支持多组分类（不同降解速率池）
- 关键化学计量参数 `cCPerDW = 0.4 gC/gDW`

### 2.2 已实现的碳过程

#### 2.2.1 光合作用固碳

```fortran
! phytoplankton.F90:421
wCAss = aMu * sDW * cCPerDW          ! 浮游植物固碳 (gC/m³/s)
wCO2UptW = wCAss                       ! CO2 吸收（但未从 DIC 池扣除）

! macrophytes.F90:456
tCProdVeg = tDProdVeg * cCPerDW       ! 大型植物固碳 (gC/m²/s)
```

**化学计量**：光合作用 O2 产出与 CO2 消耗的摩尔比
```fortran
! phytoplankton.F90:508, 510
wO2Prod = molO2molC * cCPerDW * wDAss  ! O2 产出 (molO2molC = 2.6667)
```

#### 2.2.2 呼吸释放碳

```fortran
! phytoplankton.F90:445, 517
wCRespW = kDResp * uFunTm * sDW * cCPerDW
wCO2RespW = wCRespW * aCorO2BOD        ! CO2 产出（受 O2 限制修正）

! macrophytes.F90:535
tCRespVeg = tDRespVeg * rCDVeg

! zooplankton.F90:332, zoobenthos.F90:367, fish.F90:837,841, bivalves.F90:504
wCRespZoo / tCRespBent / tCRespFi / tCRespBiv
```

#### 2.2.3 死亡与降解

```fortran
! 浮游植物死亡
wCMortW = kMort * sDW * cCPerDW        ! phytoplankton.F90:457

! 死亡碳按 fDOMW 比例分配到 POM 和 DOM
wCPOMW = wCMortTOMW * (1 - fDOMW)      ! phytoplankton.F90:520
wCDOMW = wCMortTOMW * fDOMW            ! phytoplankton.F90:521

! 大型植物分根/枝叶分别分配
wCBedPOMW, wCBedDOMW, tCBedPOMS, tCBedDOMS  ! macrophytes.F90:666-673
```

#### 2.2.4 矿化（POM → DOM → CO₂）

**水柱矿化** ([om_pool.F90:306-318](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/om_pool.F90#L306))：
```fortran
wCMin = kDMinW * uFunTmMinW * sCW                           ! 有机质 C 矿化
wO2Min = molO2molC * rCDW * aCorO2BOD * wDMin               ! O2 消耗
wDDenitW = ... * (1 - aCorO2BOD) * wDMin                     ! 反硝化矿化
wNDenitW = NO3PerCW * molNmolC * rCDW * wDDenitW             ! 反硝化 N 产出
```

**沉积物矿化** ([om_pool.F90:432-436](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/om_pool.F90#L432))：
```fortran
tCMin = kDMinS * uFunTmMinS * sCS
```

**矿化产物去向**：矿化产生的 CO₂ **未进入任何状态变量**（`CO2poolW/S` 全部被注释）。仅通过 O2 收支间接反映（计算沉积物氧需求 SOD）。

#### 2.2.5 沉降与再悬浮

```fortran
! sediment_exchange.F90
tCSedPOM = uCorVSedPOM * sCPOMW          ! POM 沉降 (line 484)
tCResusPOM = rCDPOMS * tDResusPOM        ! POM 再悬浮 (line 450)
tCDifDOM = kDDifDOM * ... * (oCDOMS - sCDOMW)/aDepthDif  ! DOM 扩散 (line 529)
tCAbioPOMS = tCSedPOM - tCResusPOM       ! 净交换 (line 539)
```

> **疑似 bug**：[sediment_exchange.F90:529](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/sediment_exchange.F90#L529) 中 `tCDifDOM` 使用 `kDDifDOM`（DW 扩散常数）而非独立的 C 扩散常数 `kCDifDOM`（后者在 line 122 被注释）。

#### 2.2.6 埋藏

[burial.F90:339-381](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/burial.F90#L339) 实现双分支：

```fortran
! 当 vDeltaS ≥ 0（沉积物增长）：
tCBurPOM = rCDPOMS * tDBurPOM           ! POM 碳埋藏（按组）
tCBurDOM = sCDOMS * (vDeltaS/cDepthS)   ! DOM 碳埋藏（按组）

! 当 vDeltaS < 0（沉积物侵蚀）：
tCBurHum = 0.50 * tDBurOM               ! 腐殖质碳埋藏（按 50% C 含量）
```

#### 2.2.7 摄食传递（食物网碳流）

```fortran
! 浮游动物 (zooplankton.F90:300, 324, 341)
wCConsZoo = wDConsZoo * rCDprey         ! 摄食碳
wCAssZoo = afCAssZoo * wCConsZooTot     ! 同化碳
wCEgesZoo = wCConsZooTot - wCAssZoo     ! 排出碳（粪便）

! 底栖动物 (zoobenthos.F90:334, 358, 376)
tCConsBent / tCAssBent / tCEgesBent

! 鱼类 (fish.F90:749-827)
tCConsFiPlan / tCConsFiBent / tCConsFiPisc  ! 三类猎物
tCAssFiTot = sum(tCAssFiPlan) + sum(tCAssFiBent) + sum(tCAssFiPisc)
tCEgesFi = tCConsFiTot - tCAssFiTot

! 双壳类 (bivalves.F90:447, 489)
tCConsBiv / tCAssBiv
```

#### 2.2.8 迁移、衰老与繁殖

```fortran
! 鱼类迁移
tCMigrFi = kMigrFish * (cCDRef*cDFiIn - sCFi)         ! fish.F90:863

! 大型植物迁移
tCMigrVeg = kMigrVeg * (cCPerDW*cDVegIn - sCVeg)      ! macrophytes.F90:564

! 鱼类骨骼埋藏（唯一显式"出系统"的碳通量）
tCMortFiBot = fDBone * tCMortFi                        ! fish.F90:960

! 难降解池转化
tCRefr = fRefrNutS * tCMin                             ! om_pool.F90:461
```

### 2.3 已实现的诊断变量

| 变量 | 含义 | 注册位置 |
|------|------|----------|
| `wet_totC` | 总碳（**仅覆盖部分浮游碳池，不完整**） | [om_pool.F90:199](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/om_pool.F90#L199) |
| `total_wCMin` | 水柱 C 矿化总通量 | [om_pool.F90:202](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/om_pool.F90#L202) |

---

## 三、WET 模型中缺失的碳循环过程

### 3.1 缺失过程总表

| 缺失过程 | 严重程度 | 影响 | 证据 |
|----------|----------|------|------|
| **无机碳库（DIC/CO₂/TIC）状态变量** | 极高 | 无法闭合碳循环 | abiotic_water 8 变量无 DIC |
| **大气-水柱 CO₂ 交换** | 极高 | 无法模拟湖泊是碳源/汇 | 只有 O2 复氧，无 CO2 对应 |
| **光合作用碳源通量** | 高 | 浮游植物生长的碳来源不明 | 营养盐吸收只列 P/N，无 C 吸收 |
| **呼吸 CO₂ 产物通量** | 高 | 呼吸产生的 CO₂ 无去向 | 仅文字描述，无方程 |
| **矿化碳产物通量** | 高 | 矿化释放的碳无去向 | 只提"释放 NH4、PO4" |
| **沉积物-水 DIC 扩散** | 高 | 底栖碳无法回到水柱 | 扩散只列 NH4/NO3/PO4/SiO2 |
| **CH₄ 产生/氧化/排放** | 极高 | 无法模拟厌氧产甲烷 | 全部源文件 0 匹配 |
| **碳酸盐平衡（pH 计算）** | 高 | 无法模拟 pH 动态 | 无 pH、HCO3⁻、CO3²⁻ 变量 |
| **钙化（CaCO₃ 沉淀/溶解）** | 高 | 忽略重要 CO₂ 释放机制 | 无 calcium、CaCO3、carbonate |
| **N₂O 排放** | 中 | 忽略强温室气体 | 无 N2O 变量 |
| **碳质量平衡校验** | 高 | 无法验证碳守恒 | PCLake 只校验 DW/P/N |
| **碳专属参数** | 中 | C/D 比被假设恒定 | 所有呼吸/矿化参数以 DW 为基础 |

### 3.2 关键代码注释证据

WET 源代码中多处明确标注 GHG 模块为"计划中"：

```fortran
! macrophytes.F90:696
!_SET_BOTTOM_EXCHANGE_(self%id_CO2poolW,tCO2BedW)  ! until GHG module implemented

! zooplankton.F90:169
!to be used with GHG module enabled

! phytoplankton.F90:765
! TODO: implement CO2 production, tCO2W from tO2RespS

! phytoplankton.F90:798
! TODO: incl DO uptake from respiration and CO2 production
```

### 3.3 被注释的 CO₂ 池代码

所有模块的 `id_CO2pool*` 类型声明保留，但 `register_state_dependency` 和 `_SET_ODE_` 均被注释：

| 文件 | 行号 | 状态 |
|------|------|------|
| [phytoplankton.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/phytoplankton.F90) | 33, 265, 367, 538 | 类型声明保留，注册和 ODE 被注释 |
| [zooplankton.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/zooplankton.F90) | 169, 415 | "to be used with GHG module enabled" |
| [zoobenthos.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/zoobenthos.F90) | 481 | `_SET_BOTTOM_ODE_(CO2poolS, tCBentCO2S)` 被注释 |
| [fish.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/fish.F90) | 31, 236, 1041 | 类型声明保留，注册和 ODE 被注释 |
| [bivalves.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/bivalves.F90) | 641 | `_SET_BOTTOM_ODE_(CO2poolS, tCBivCO2S)` 被注释 |
| [macrophytes.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/macrophytes.F90) | 40, 258, 379, 696 | "until GHG module implemented" |

### 3.4 碳不守恒的根源

1. **呼吸/矿化产生的 CO₂ 既不进入 DIC 池，也不计入任何出流通量** → 碳"消失"
2. **光合作用消耗的 CO₂ 不从任何池中扣除** → 碳"凭空产生"
3. **鱼类骨骼埋藏 `tCMortFiBot`** 是唯一显式"出系统"的碳通量
4. **`wet_totC` 聚合变量覆盖不完整**：未包含 macrophytes/zoobenthos/fish/bivalves 的 sC、所有沉积物 sCS、深沉积物腐殖质

---

## 四、3DWET 完善碳循环的实施方案

### 4.1 总体架构

建议分 **三个阶段** 实施碳循环完善：

```
阶段 1（基础）：无机碳库 + 大气 CO₂ 交换 + 碳守恒
    → 实现 DIC 状态变量、CO₂ 水-气交换、连接呼吸/光合到 DIC

阶段 2（扩展）：碳酸盐系统 + 钙化
    → 实现 pH 计算、HCO₃⁻/CO₃²⁻、CaCO₃ 沉淀/溶解

阶段 3（完整）：温室气体（CH₄ + N₂O）
    → 实现产甲烷、甲烷氧化、CH₄ 排放（扩散+气泡+植物传输）
```

### 4.2 阶段 1：无机碳库 + 大气 CO₂ 交换

#### 4.2.1 新增状态变量（abiotic_water.F90）

```fortran
! 在 type_wet_abiotic_water 中添加：
type (type_state_variable_id) :: id_sCO2W      ! 溶解 CO2* (gC/m³)
type (type_state_variable_id) :: id_sHCO3W     ! HCO3⁻ (gC/m³)
type (type_state_variable_id) :: id_sCO3W      ! CO3²⁻ (gC/m³)
type (type_state_variable_id) :: id_sDICW      ! DIC 总量 (gC/m³) [诊断]
type (type_horizontal_state_variable_id) :: id_sCO2S  ! 沉积物 CO2 (gC/m²)
```

#### 4.2.2 DIC 系统方程

```fortran
! 碳酸平衡（已知 DIC 和 pH 求 three pools）
! 分布系数：
alpha0 = [H+]^2 / ([H+]^2 + K1*[H+] + K1*K2)    ! CO2* 占比
alpha1 = K1*[H+] / ([H+]^2 + K1*[H+] + K1*K2)   ! HCO3⁻ 占比
alpha2 = K1*K2 / ([H+]^2 + K1*[H+] + K1*K2)     ! CO3²⁻ 占比

! 各组分：
sCO2W  = DIC * alpha0
sHCO3W = DIC * alpha1
sCO3W  = DIC * alpha2

! 平衡常数温度依赖（Van't Hoff）：
K1(T) = K1(T_ref) * exp(-dH1/R * (1/T - 1/T_ref))
K2(T) = K2(T_ref) * exp(-dH2/R * (1/T - 1/T_ref))
! K1(25°C) = 10^(-6.35), K2(25°C) = 10^(-10.33)
! dH1 = -598 kJ/mol, dH2 = -593 kJ/mol (Plummer & Busenberg 1982)
```

#### 4.2.3 pH 计算（碱度法）

```fortran
! 已知 TAlk 和 DIC，迭代求 [H+]：
! TAlk = DIC * (alpha1 + 2*alpha2) + Kw/[H+] - [H+]
! 用牛顿迭代法或 Brent 法求解

! 简化（忽略 [H+] 和 [OH-]）：
! TAlk ≈ DIC * (K1*[H+] + 2*K1*K2) / ([H+]^2 + K1*[H+] + K1*K2)
! 二次方程求解 [H+]
```

#### 4.2.4 大气 CO₂ 交换（do_surface 子程序）

```fortran
! 在 abiotic_water.F90 的 do_surface 中添加：

! 1. CO2 溶解度（Weiss 1974，淡水）
TK = uTm + 273.15
lnK0 = -58.0931 + 90.5069*(100/TK) + 22.2940*log(TK/100) + 0.027766*(100/TK)^2
K0 = exp(lnK0)   ! mol/(L·atm)

! 2. 水体 pCO2（µatm）
! [CO2*] (mol/L) = sCO2W / 12.0 / 1000.0
pCO2_water = (sCO2W / 12.0 / 1000.0) / K0 * 1e6   ! µatm

! 3. 气体传输速度 k600（Cole & Caraco 1998）
k600_cmh = 2.07 + 0.215 * uU10^1.7                ! cm/h

! 4. Schmidt 数温度校正
Sc_CO2 = 600.0   ! 简化，实际为温度函数
n = 0.5
if (uU10 < 3.6) n = 0.667
k_CO2_cmh = k600_cmh * (Sc_CO2 / 600.0)**(-n)     ! cm/h
k_CO2_md = k_CO2_cmh / 100.0 * 24.0                ! m/d

! 5. CO2 通量（mmol C m⁻² d⁻¹ → gC/m³/s）
pCO2_air = 420.0   ! µatm（可从气象数据读取）
F_CO2_mmol = k_CO2_md * K0 * (pCO2_water - pCO2_air) * 1000.0  ! mmol/m²/d
tCO2Air = F_CO2_mmol * 12.0 / 1e6 / 86400.0 * aFunAreaAir      ! gC/m³/s
! 正值 = 向大气排放（从 sCO2W 扣除）

! 6. 更新 ODE
_SET_ODE_(id_sCO2W, -tCO2Air)   ! 表层网格
```

#### 4.2.5 连接呼吸/矿化到 DIC

**取消注释并修正所有被注释的 CO₂ 池代码**：

```fortran
! phytoplankton.F90（光合吸收 CO2）
! 原注释：_SET_ODE_(self%id_CO2poolW, wCO2W)
! 修改为：
wCO2UptW = wCAss                              ! 光合固碳消耗 CO2
! 通过 _SET_DIAGNOSTIC_ 或 dependency 传递给 abiotic_water
! 在 abiotic_water.do 中：
! _ADD_SOURCE_(id_sCO2W, -wCO2UptW)
! _ADD_SOURCE_(id_sCO2W, +wCO2RespW)         ! 呼吸释放 CO2

! zooplankton.F90（呼吸释放 CO2）
! 原注释：_SET_ODE_(self%id_CO2poolW, wCZooCO2W)
! 修改为：通过诊断变量传递 wCRespZoo 到 abiotic_water

! zoobenthos.F90（底栖呼吸释放 CO2）
! 原注释：_SET_BOTTOM_ODE_(self%id_CO2poolS, tCBentCO2S)
! 修改为：
_SET_BOTTOM_EXCHANGE_(id_sCO2W_PV, tCRespBent * bot_pel_conv)

! fish.F90, bivalves.F90, macrophytes.F90：类似处理
```

#### 4.2.6 沉积物-水柱 DIC 扩散

```fortran
! 在 sediment_exchange.F90 中添加：
tCDifCO2 = kDDifCO2 * uFunTmDif * cTurbDifNut * bPorCorS * (sCO2S - sCO2W)/aDepthDif
! 正值 = 从沉积物向水柱扩散
```

#### 4.2.7 碳质量平衡诊断

```fortran
! 完善 wet_totC 聚合变量，注册所有碳池：
! 在各模块的 register_variables 中：
call self%register_variable(id_sCW, 'wet_totC')     ! 已有
call self%register_variable(id_sCVeg, 'wet_totC')   ! macrophytes 新增
call self%register_variable(id_sCBent, 'wet_totC')  ! zoobenthos 新增
call self%register_variable(id_sCFi, 'wet_totC')    ! fish 新增
call self%register_variable(id_sCS, 'wet_totC')     ! 沉积物有机碳新增
call self%register_variable(id_sDICW, 'wet_totC')   ! DIC 新增

! 新增碳通量诊断：
call self%register_diagnostic_variable(id_tCO2Air, 'tCO2Air', 'gC/m2/d', 'CO2 air-water flux')
call self%register_diagnostic_variable(id_tCBurTot, 'tCBurTot', 'gC/m2/d', 'Total C burial')
call self%register_diagnostic_variable(id_tCNEP, 'tCNEP', 'gC/m3/d', 'Net Ecosystem Production')
```

### 4.3 阶段 2：碳酸盐系统 + 钙化

#### 4.3.1 新增变量

```fortran
! abiotic_water.F90：
type (type_state_variable_id) :: id_sCaW          ! 溶解 Ca²⁺ (g/m³)
type (type_horizontal_state_variable_id) :: id_sCaCO3S  ! 沉积物 CaCO3 (g/m²)
type (type_dependency_id) :: id_pH                 ! pH（诊断变量）
type (type_dependency_id) :: id_Omega              ! 方解石饱和度（诊断）
```

#### 4.3.2 钙化方程

```fortran
! 方解石饱和度
Omega = (sCaW / 40.0) * (sCO3W / 60.0) / K_sp   ! K_sp = 3.3e-9 (25°C)
! 单位转换：g/m³ → mol/L (Ca: 40 g/mol, CO3: 60 g/mol, 1 m³ = 1000 L)

! 钙化速率（净沉淀为正）
if (Omega > 1.0) then
    R_calc = k_calc * (Omega - 1.0)^n_calc      ! n_calc = 1-2
else
    R_calc = -k_diss * (1.0 - Omega)             ! 溶解
end if

! 化学计量：
! Ca²⁺ + 2HCO3⁻ → CaCO3(s) + CO2 + H2O
! 每沉淀 1 mol CaCO3:
!   - 消耗 1 mol Ca²⁺
!   - 消耗 2 mol HCO3⁻ (= 2 mol 碱度)
!   - 释放 1 mol CO2
!   - 生成 1 mol CaCO3

tCaCO3Precip = R_calc                            ! mol/m³/s
! 更新状态变量：
_SET_ODE_(id_sCaW, -tCaCO3Precip * 40.0)         ! Ca²⁺ 减少
_SET_ODE_(id_sHCO3W, -2.0 * tCaCO3Precip * 12.0)  ! HCO3⁻ 减少
_SET_ODE_(id_sCO2W, +tCaCO3Precip * 12.0)        ! CO2 增加
! CaCO3 沉降到沉积物：
_SET_BOTTOM_EXCHANGE_(id_sCaCO3S, tCaCO3Precip * 100.0 * bot_pel_conv)
```

#### 4.3.3 CaCO₃ 溶解（沉积物中）

```fortran
! 在 abiotic_sediment.F90 的 do_bottom 中：
if (Omega_sed < 1.0) then
    R_diss = k_diss_sed * (1.0 - Omega_sed) * sCaCO3S
    ! CaCO3(s) + CO2 + H2O → Ca²⁺ + 2HCO3⁻
    _SET_BOTTOM_ODE_(id_sCaCO3S, -R_diss)
    _SET_BOTTOM_EXCHANGE_(id_sCaW_PV, +R_diss * 40.0 * bot_pel_conv)
    _SET_BOTTOM_EXCHANGE_(id_sHCO3W_PV, +2.0 * R_diss * 12.0 * bot_pel_conv)
    _SET_BOTTOM_EXCHANGE_(id_sCO2W_PV, -R_diss * 12.0 * bot_pel_conv)
end if
```

### 4.4 阶段 3：温室气体（CH₄ + N₂O）

#### 4.4.1 新增 CH₄ 模块（建议新建 `methane.F90`）

```fortran
module wet_methane
   use fabm_types
   use fabm_particle
   implicit none
   private

   type, extends(type_particle_model), public :: type_wet_methane
      ! 状态变量
      type (type_state_variable_id) :: id_sCH4W        ! 水柱 CH4 (gC/m³)
      type (type_bottom_state_variable_id) :: id_sCH4S ! 沉积物 CH4 (gC/m²)

      ! 依赖
      type (type_dependency_id) :: id_uTm, id_sO2W, id_sDPOMpoolS, id_sDDOMpoolS
      type (type_horizontal_dependency_id) :: id_bot_pel_conv

      ! 参数
      real(rk) :: kMethMax, Q10Meth, hO2Meth, kMethOx, Q10MethOx, hO2MethOx
      real(rk) :: kEbul, CH4SatThresh, fAcetoclastic
   contains
      procedure :: initialize
      procedure :: do
      procedure :: do_bottom
      procedure :: get_vertical_movement
   end type
contains
```

#### 4.4.2 产甲烷方程（do_bottom）

```fortran
! 产甲烷（严格厌氧，沉积物中）
! 底物：沉积物 POM/DOM 矿化产物
uFunTmMeth = Q10Meth^((uTm - 20)/10)                   ! 温度增强, Q10=2-8
fO2Inhib = 1.0 / (1.0 + (sO2W/hO2Meth)^2)              ! O2 抑制 (hO2Meth ≈ 0.1 mg/L)

! 乙酸营养型 + 氢营养型
R_acetate = fAcetoclastic * kMethMax * sDPOMpoolS      ! 乙酸途径 (60-70%)
R_hydrogen = (1.0 - fAcetoclastic) * kMethMax * sDDOMpoolS  ! 氢途径
tMethProd = (R_acetate + R_hydrogen) * uFunTmMeth * fO2Inhib

! 化学计量：CH3COOH → CH4 + CO2 (1:1:1)
! 4H2 + CO2 → CH4 + 2H2O (4:1)

! 更新沉积物 CH4 池
_SET_BOTTOM_ODE_(id_sCH4S, tMethProd)

! 消耗沉积物有机碳（已通过 om_pool 矿化提供，避免重复计算）
```

#### 4.4.3 甲烷氧化方程（do）

```fortran
! 好氧氧化（水柱中）
! CH4 + 2O2 → CO2 + 2H2O
uFunTmMethOx = Q10MethOx^((uTm - 20)/10)               ! Q10 = 2-3
fO2Lim = sO2W / (hO2MethOx + sO2W)                     ! O2 限制 (Monod)

tMethOx = kMethOx * uFunTmMethOx * fO2Lim * sCH4W      ! 甲烷氧化速率

! 化学计量：1 mol CH4 → 1 mol CO2，消耗 2 mol O2
_SET_ODE_(id_sCH4W, -tMethOx)
! 释放 CO2（通过诊断变量传递给 abiotic_water）
! _ADD_SOURCE_(id_sCO2W, +tMethOx)   ! 碳守恒
! _ADD_SOURCE_(id_sO2W, -2.0*tMethOx * 32.0/12.0)  ! O2 消耗
```

#### 4.4.4 CH₄ 排放通量（do_surface）

```fortran
! 三大途径：

! (1) 扩散传输
Sc_CH4 = 600.0   ! 简化
k_CH4 = k600 * (Sc_CH4/600)^(-n)
K0_CH4 = ...      ! CH4 Henry 常数
F_diff = k_CH4 * K0_CH4 * (pCH4_water - pCH4_air)

! (2) 气泡传输（ebullition）
if (sCH4S > CH4SatThresh) then
    F_ebul = kEbul * (sCH4S - CH4SatThresh)
else
    F_ebul = 0.0
end if

! (3) 植物介导传输（如有 macrophytes）
! F_plant = kPlant * sCH4S * aCovVeg   ! 与 macrophytes 耦合

! 总排放
F_CH4_total = F_diff + F_ebul  ! + F_plant

! 更新状态变量
_SET_ODE_(id_sCH4W, -F_diff * aFunAreaAir / dz_surf)
_SET_BOTTOM_ODE_(id_sCH4S, -F_ebul)  ! 气泡直接从沉积物排出
```

#### 4.4.5 N₂O 排放（可选，扩展 abiotic_water）

```fortran
! 新增状态变量
type (type_state_variable_id) :: id_sN2OW      ! 溶解 N2O (gN/m³)

! 硝化副产物（abiotic_water.do）
! NH4⁺ + 1.5O2 → NO2⁻ + H2O + 2H⁺ (主反应)
! 副反应：NH2OH → N2O (羟胺途径)
fN2ONitr = 0.001   ! 硝化 N2O 产率 (0.1-0.5%)
tN2OProdNitr = fN2ONitr * wNNitrW

! 反硝化中间产物（om_pool.do）
! NO3⁻ → NO2⁻ → NO → N2O → N2
fN2ODenit = 0.05   ! 反硝化 N2O 累积比例
tN2OProdDenit = fN2ODenit * wNDenitW

! N2O 大气排放
F_N2O = k_N2O * K0_N2O * (pN2O_water - pN2O_air)

! 更新
_SET_ODE_(id_sN2OW, +tN2OProdNitr + tN2OProdDenit - F_N2O/dz)
```

### 4.5 实施步骤汇总

| 步骤 | 模块 | 修改内容 | 优先级 |
|------|------|----------|--------|
| 1 | abiotic_water.F90 | 添加 DIC/CO₂/HCO₃⁻/CO₃²⁻ 状态变量、pH 计算、CO₂ 大气交换 | 极高 |
| 2 | phytoplankton.F90 | 取消注释 CO₂ 池连接（光合吸收、呼吸释放） | 极高 |
| 3 | zooplankton/zoobenthos/fish/bivalves/macrophytes.F90 | 取消注释所有 CO₂ 池 ODE 设置 | 极高 |
| 4 | sediment_exchange.F90 | 添加 DIC 沉积物-水柱扩散；**修复 tCDifDOM 的 bug**（kDDifDOM → kCDifDOM） | 高 |
| 5 | om_pool.F90 | 矿化产物 CO₂ 连接到 DIC 池 | 高 |
| 6 | 各模块 | 完善 wet_totC 聚合变量注册 | 高 |
| 7 | abiotic_water.F90 | 添加 Ca²⁺、CaCO₃ 饱和度、钙化/溶解 | 中 |
| 8 | abiotic_sediment.F90 | 添加 CaCO₃ 溶解 | 中 |
| 9 | 新建 methane.F90 | 产甲烷、甲烷氧化、CH₄ 排放（扩散+气泡） | 中 |
| 10 | macrophytes.F90 | 添加植物介导 CH₄ 传输 | 低 |
| 11 | abiotic_water.F90 | 添加 N₂O 状态变量和排放 | 低 |

---

## 五、关键化学计量参数

### 5.1 WET 已有参数

| 参数 | 值 | 含义 | 定义位置 |
|------|-----|------|----------|
| `molO2molC` | 2.6667 | O2:C 摩尔比（呼吸/矿化） | abiotic_water.F90:51 |
| `molO2molN` | 2.2857 | O2:N 摩尔比（硝化） | abiotic_water.F90:52 |
| `molNmolC` | 1.1667 | N:C 摩尔比（反硝化） | abiotic_water.F90:53 |
| `O2PerNO3` | 1.5 | O2/NO3 比（NO3 呼吸替代） | phytoplankton.F90:79 |
| `cCPerDW` | 0.4 gC/gDW | 有机质 C 含量 | phytoplankton.F90:135, macrophytes.F90:144 |
| `NO3PerCW` | 1.0 mol/mol | 反硝化 NO3:C 比 | om_pool.F90:101 |

### 5.2 完善碳循环需新增的参数

| 参数 | 建议值 | 含义 | 用于 |
|------|--------|------|------|
| `K1` (25°C) | 10⁻⁶·³⁵ | 碳酸一级电离常数 | 碳酸盐平衡 |
| `K2` (25°C) | 10⁻¹⁰·³³ | 碳酸二级电离常数 | 碳酸盐平衡 |
| `K_sp` (25°C) | 3.3×10⁻⁹ | 方解石溶度积 | 钙化 |
| `k_calc` | 0.1-1.0 /d | 钙化动力学常数 | 钙化 |
| `n_calc` | 1.5 | 钙化反应级数 | 钙化 |
| `kMethMax` | 0.01-0.1 /d | 最大产甲烷速率 | 产甲烷 |
| `Q10Meth` | 4-8 | 产甲烷温度系数 | 产甲烷 |
| `hO2Meth` | 0.1 mg/L | 产甲烷 O2 抑制半饱和 | 产甲烷 |
| `kMethOx` | 0.5-5.0 /d | 甲烷氧化速率常数 | 甲烷氧化 |
| `Q10MethOx` | 2-3 | 甲烷氧化温度系数 | 甲烷氧化 |
| `hO2MethOx` | 0.5 mg/L | 甲烷氧化 O2 半饱和 | 甲烷氧化 |
| `kEbul` | 0.1-1.0 /d | 气泡传输速率常数 | CH₄ 排放 |
| `CH4SatThresh` | 0.1 gC/m² | CH₄ 气泡触发阈值 | CH₄ 排放 |
| `fAcetoclastic` | 0.65 | 乙酸营养型占比 | 产甲烷 |
| `fN2ONitr` | 0.002 | 硝化 N₂O 产率 | N₂O 排放 |
| `fN2ODenit` | 0.05 | 反硝化 N₂O 累积比例 | N₂O 排放 |
| `pCO2_air` | 420 µatm | 大气 CO₂ 分压 | CO₂ 交换 |
| `k600_a` | 2.07 | Cole-Caraco 截距 | 气体传输 |
| `k600_b` | 0.215 | Cole-Caraco 系数 | 气体传输 |
| `k600_exp` | 1.7 | Cole-Caraco 指数 | 气体传输 |

---

## 六、碳守恒分析与质量平衡

### 6.1 当前碳不守恒的根源

```
当前 WET 碳收支：
dC_lake/dt = F_river,in(POC+DOC)                      [输入]
           − F_river,out(无碳输出)                     [输出缺失]
           − F_burial(POM/DOM/Humus)                   [埋藏]
           − F_bone(鱼类骨骼)                          [骨骼埋藏]
           + GPP(固碳，但 CO2 来源不明)                 [内部代谢-源]
           − R(呼吸，但 CO2 去向不明)                   [内部代谢-汇]

问题：
1. GPP 的 CO2 来源：未从 DIC 扣除 → 碳凭空产生
2. R 的 CO2 去向：未进入 DIC → 碳消失
3. 矿化的 CO2 去向：未进入 DIC → 碳消失
4. 河流输出：无碳 → 碳无法随出流离开
5. 大气交换：无 → 无法与大气交换
```

### 6.2 完善后的碳守恒方程

```
dC_lake/dt = F_river,in(POC+DOC+DIC)                  [输入]
           − F_river,out(POC+DOC+DIC)                  [输出]
           − F_burial(POM/DOM/Humus/CaCO3)             [埋藏]
           − F_bone(鱼类骨骼)                          [骨骼埋藏]
           − F_atm,CO2(CO2 大气交换)                   [大气交换]
           − F_atm,CH4(CH4 大气交换)                   [大气交换]
           + GPP(固碳，从 DIC 扣除)                     [内部代谢]
           − R(呼吸，进入 DIC)                         [内部代谢]
           − R_calc(钙化，释放 CO2 到 DIC)              [钙化]

守恒检验：wet_totC(t+dt) − wet_totC(t) = Σ(通量) × dt
```

### 6.3 验证方法

1. **总碳质量平衡**：`wet_totC` 应等于所有碳池之和（生物量 + POM + DOM + DIC + CH4 + CaCO3 + 腐殖质）
2. **碳通量收支**：`d(wet_totC)/dt` 应等于所有源汇通量之和
3. **与 O2 收支交叉验证**：`ΔO2` 应与 `(GPP − R) × molO2molC` 一致
4. **pCO2 合理性**：模拟的 pCO2 应在 100-5000 µatm 范围内（典型湖泊）

---

## 七、参考文献

1. **Many G., Escoffier N., Perolo P., et al. (2024)** Calcite precipitation: The forgotten piece of lakes' carbon cycle. *Sci. Adv.* 10, eado5924. DOI: 10.1126/sciadv.ado5924
2. **Middelburg J.J. (2024)** Closing the inland water carbon cycle. *Sci. Adv.* 10, eadt3893.
3. **唐千, 薛校风, 王惠, 邢鹏 (2018)** 湖泊生态系统产甲烷与甲烷氧化微生物研究进展. *湖泊科学* 30(3): 597-610.
4. **周文昌等 (2024)** 长江中游湖泊湿地不同植被类型的甲烷排放和植物传输能力. *生态学杂志* 43(12): 3726-3734.
5. **Cole J.J., Caraco N.F. (1998)** Atmospheric exchange of carbon dioxide in a low-wind oligotrophic lake. *Limnol. Oceanogr.* 43: 647-656.
6. **Wanninkhof R. (1992)** Relationship between wind speed and gas exchange over the ocean. *J. Geophys. Res.* 97: 7373-7382.
7. **Weiss R.F. (1974)** Carbon dioxide in water and seawater: the solubility of a non-ideal gas. *Mar. Chem.* 2: 203-215.
8. **Plummer L.N., Busenberg E. (1982)** The solubilities of calcite, aragonite and vaterite in CO2-H2O solutions. *Geochim. Cosmochim. Acta* 46: 1011-1040.

---

## 附录：WET 源文件中的碳过程位置索引

| 文件 | 碳相关行号 | 主要内容 |
|------|-----------|----------|
| [phytoplankton.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/phytoplankton.F90) | 33, 135, 156, 166, 256, 265, 367, 421, 445, 457, 508, 510, 516, 517, 520, 521, 538, 682, 694, 702-714, 765, 798 | 光合固碳、呼吸、死亡、沉降、CO2 池（注释） |
| [zooplankton.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/zooplankton.F90) | 127, 169, 300, 324, 332, 341, 348, 415 | 摄食、同化、呼吸、排出、死亡、CO2 池（注释） |
| [zoobenthos.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/zoobenthos.F90) | 48, 119, 124, 334, 358, 367, 376, 384, 391, 481 | 摄食、同化、呼吸、排出、死亡、迁移、CO2 池（注释） |
| [macrophytes.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/macrophytes.F90) | 40, 78, 144, 160, 165, 258, 379, 456, 535, 557, 564, 666-673, 696 | 固碳、呼吸、死亡、迁移、POM/DOM 分配、CO2 池（注释） |
| [fish.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/fish.F90) | 31, 236, 442, 749-827, 837, 841, 849, 856, 863, 892, 906, 960, 1041 | 摄食（三类猎物）、呼吸、排出、死亡、迁移、衰老、骨骼埋藏、CO2 池（注释） |
| [bivalves.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/bivalves.F90) | 165, 179, 194, 447, 489, 504, 524, 550, 563, 641 | 摄食、同化、呼吸、死亡、繁殖、衰老、CO2 池（注释） |
| [om_pool.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/om_pool.F90) | 69, 72, 101, 132, 142, 146, 199, 202, 241, 306-318, 432-436, 457, 461-464 | 矿化、反硝化、难降解池、wet_totC |
| [abiotic_water.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90) | 51, 52, 53, 66, 313-349 | O2 复氧（无 CO2 交换）、化学计量参数 |
| [abiotic_sediment.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_sediment.F90) | 57, 58, 59, 83, 139, 243-247, 251-252 | SOD 计算、反硝化 C 矿化 |
| [sediment_exchange.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/sediment_exchange.F90) | 122, 155, 164, 220, 229, 450, 484, 529, 539 | POM 沉降/再悬浮、DOM 扩散（bug: kDDifDOM） |
| [burial.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/burial.F90) | 91, 95, 148-156, 152, 187, 339-381, 396, 410, 421 | POM/DOM/Humus 碳埋藏、双分支 |

---

*本文档基于 WET 源代码（11 个 Fortran 模块）和 2024-2026 年最新湖泊碳循环文献编写，适用于指导 3DWET 模型碳循环完善工作。*
