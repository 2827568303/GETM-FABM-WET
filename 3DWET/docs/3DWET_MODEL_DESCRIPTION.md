# 3DWET 模型完整说明

> **文档定位**：3DWET（GETM + GOTM + FABM + WET）耦合体系的全本技术说明
> **核心问题**：阐明模型结构、生态学假设、各模块方程、耦合方式，以及鱼类 / 水生植物 / 底栖动物等食物网组分在三维模拟中的求解方式
> **关键结论**：**所有 WET 生态模块的内部动力学均采用常微分方程（ODE）求解，并非偏微分方程（PDE）。三维空间分布通过 FABM 的变量类型系统 + GETM 的平流-扩散输运实现**——浮游生物（3D 变量）受完整 3D 输运，底栖生物（2D 变量）无输运仅局部 ODE，通过 `bot_pel_conv` 桥接两个域。

---

## 目录

- [一、模型总体架构](#一模型总体架构)
- [二、模型逻辑与数据流](#二模型逻辑与数据流)
- [三、基本生态学假设](#三基本生态学假设)
- [四、食物网结构](#四食物网结构)
- [五、各模块方程详解](#五各模块方程详解)
- [六、GETM-FABM-WET 耦合方式](#六getm-fabm-wet-耦合方式)
- [七、食物网组分的三维实现方式（核心问题）](#七食物网组分的三维实现方式核心问题)
- [八、数值求解方法](#八数值求解方法)
- [九、模型文件与配置](#九模型文件与配置)

---

## 一、模型总体架构

3DWET 由四个开源组件深度耦合而成，层次清晰、职责明确：

| 组件 | 全称 | 角色 | 主要职责 |
|------|------|------|----------|
| **GETM** | General Estuarine Transport Model | 3D 水动力模型 | 水流、水温、物质 3D 输运 |
| **GOTM** | General Ocean Turbulence Model | 垂向湍流模型 | 垂直涡粘性 / 扩散系数 |
| **FABM** | Framework for Aquatic Biogeochemical Models | 生地化耦合框架 | 状态变量注册、时间积分、诊断变量管理 |
| **WET** | Water Ecology Treatment | 生态模型 | PCLake 的 FABM 版本，提供完整食物网 |

**架构层次**：

```
┌─────────────────────────────────────────────────────────────┐
│              WET (生态食物网模型，17 个 Fortran 模块)           │
│  浮游植物 / 浮游动物 / 底栖动物 / 鱼类 / 沉水植物 / 有机质 / 营养盐  │
└─────────────────────────────────────────────────────────────┘
                          ▲ ▼
┌─────────────────────────────────────────────────────────────┐
│                   FABM (生地化耦合框架)                        │
│       状态变量注册 / 时间积分 / 诊断变量 / 类型系统 / 桥接         │
└─────────────────────────────────────────────────────────────┘
                          ▲ ▼
┌────────────────────────────┐  ┌────────────────────────────┐
│   GETM (3D 水动力)           │  │   GOTM (垂向湍流)           │
│   水流 / 水温 / 3D 物质输运    │←→│   k-ε 模型 / 垂直混合       │
└────────────────────────────┘  └────────────────────────────┘
```

**WET 由瓦赫宁根大学开发**，是经典 PCLake 模型的 FABM 重构版本，保留 PCLake 完整食物网结构，同时获得 FABM 框架带来的多模型耦合能力，使原本零维（池式）的 PCLake 可以在 GETM 三维水动力场中运行。

---

## 二、模型逻辑与数据流

### 2.1 一个时间步内的计算流程

```
[GETM 水动力推进]
   ├─ 读取气象强迫、边界条件
   ├─ 求解 3D 动量方程 → u, v, w
   ├─ 求解标量输运方程 → T, S
   └─ 调用 GOTM 计算垂直湍流 → avm, avh
          │
          ▼
[GETM → FABM 提供物理环境]
   ├─ 水温 temp、流速 u/v/w、PAR 光强
   ├─ 层厚 dz、水深 sDepthW
   ├─ 剪切应力（用于再悬浮）
   └─ bot_pel_conv = 1/dz（底栖-浮游桥接因子）
          │
          ▼
[FABM 调度 WET 各模块]
   ├─ 对每个水平单元 (i,j)：
   │    ├─ 浮游模块 do()             → 计算所有 3D 变量的局部 ODE 右端
   │    ├─ 底栖模块 do_bottom()      → 计算所有 2D 变量的局部 ODE 右端
   │    ├─ _SET_BOTTOM_EXCHANGE_     → 将底栖通量 × bot_pel_conv 投影到 3D 镜像
   │    └─ get_vertical_movement()    → 鱼类等主动迁移速度
   │
   ├─ 时间积分（ode_method 控制求解器）
   │    ├─ 浮游变量：x_pel(t+dt) = x_pel(t) + dt·(local_rhs + transport_rhs)
   │    └─ 底栖变量：x_ben(t+dt) = x_ben(t) + dt·(local_rhs)   ← 无 transport
   │
   └─ GETM 用浮游变量 rhs 中的 transport 部分做 3D 平流-扩散输运
          │
          ▼
[输出]  netCDF 结果（output.nc）
```

### 2.2 关键数据流

- **物理 → 生物**：GETM 通过 FABM 接口提供水温、光、流速、层厚等
- **生物 → 物理**：WET 通过 `shade` 反馈改变水体消光系数（生物自遮蔽）
- **底栖 ↔ 浮游**：通过 `bot_pel_conv = 1/dz` 转换单位（g/m² ↔ g/m³），底栖通量投影到 3D 镜像变量（`_PV`）

---

## 三、基本生态学假设

3DWET 继承 PCLake 的核心生态学假设，并将其扩展至三维：

### 3.1 营养级与能量流假设

1. **5 个营养级**：顶级鱼类 → 鱼类 → 浮游/底栖动物 → 浮游植物/沉水植物 → POM/DOM/营养盐
2. **能量按 Dry Weight（DW）追踪**：所有生物量以 gDW/m³（浮游）或 gDW/m²（底栖）为单位
3. **化学计量比可变**：每种生物同时追踪 D（干重）、N、P、C 四个状态变量，比值随摄食/同化/排出动态变化
4. **质量守恒**：D、N、P、C 在底栖-浮游耦合系统中严格守恒（Patankar 求解器保证正性）

### 3.2 浮游植物生态学假设

- **4 类藻类**：蓝藻（Cyanobacteria）、硅藻（Diatoms）、绿藻（Greens）
- **光限制**：采用 Steele 形式或 Monod 形式的光限制函数，考虑水面植被遮蔽
- **营养盐限制**：Liebig 最小定律（min(P, N, Si)），硅藻受 Si 限制，蓝藻可固氮
- **温度响应**：高斯型最适温度曲线（不同藻类有不同的最适温度和宽度）
- **无光抑制版本可选**：通过参数切换是否考虑光抑制

### 3.3 浮游动物生态学假设

- **3 类浮游动物**：枝角类（Cladocerans）、桡足类（Copepods）
- **多猎物配置**：每个捕食者可配置 nPrey 个猎物类型，每个猎物有独立的清除率参数
- **饱和摄食**：Holling Type II 功能响应（Michaelis-Menten 形式）
- **温度依赖**：高斯型最适温度曲线

### 3.4 底栖生态学假设

- **底栖动物**：清除率单位 m²/gDW/d，体现"面积扫描"摄食策略，可摄取浮游和底栖两类猎物
- **沉水植物**：2D 底栖固着生长，通过 `_PV` 镜像与浮游域耦合（消耗营养盐来自水柱）
- **底栖-浮游桥接**：所有底栖生物量以 g/m² 存储，需要时通过 `bot_pel_conv = 1/dz` 转换为 g/m³ 与浮游域交互

### 3.5 鱼类生态学假设

- **3 个鱼群阶段**：幼鱼（JuFish）、成鱼（AdFish）、食鱼鱼（PiscFish）
- **结构-储能动态**：每个鱼群分为结构质量（sDStruc）和储能（sDReser），储能优先消耗
- **最优食谱选择（ODB）**：根据猎物可获得性动态调整食谱
- **垂直迁移**：可配置 O2 和/或光照驱动的主动垂直迁移

### 3.6 沉积物-水柱交换假设

- **再悬浮**：由底部剪切应力驱动
- **沉降**：浮游 POM、藻类等沉降到沉积物
- **扩散交换**：营养盐在间隙水与上覆水间扩散

---

## 四、食物网结构

### 4.1 完整食物网示意

```
                    ┌──────────────────┐
                    │   PiscFish (顶级)  │  ← 食鱼鱼，捕食 AdFish/JuFish
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼───────┐         ┌───────▼───────┐
        │   AdFish       │         │   JuFish       │  ← 成鱼、幼鱼
        │  (成鱼)         │         │  (幼鱼)         │
        └───────┬───────┘         └───────┬───────┘
                │                         │
    ┌───────────┼──────────────┬──────────┼──────────┐
    │           │              │          │          │
┌───▼────┐ ┌───▼────┐ ┌──────▼──────┐ ┌──▼───┐ ┌───▼────┐
│Cladoc. │ │Copep.  │ │ Zoobenthos  │ │POM/DOM│ │ 藻类    │
│枝角类   │ │桡足类   │ │  底栖动物    │ │有机质 │ │(沉降)   │
└───┬────┘ └───┬────┘ └──────┬──────┘ └──────┘ └────────┘
    │           │              │
    └───────────┼──────────────┘
                │
    ┌───────────┼─────────────────────┐
    │           │                     │
┌───▼────┐ ┌───▼────┐ ┌──────────▼──────────┐ ┌──────────┐
│Cyanob. │ │Diatoms │ │      Greens          │ │Macrophytes│
│蓝藻    │ │硅藻    │ │      绿藻            │ │沉水植物   │
└────────┘ └────────┘ └─────────────────────┘ └──────────┘
                │
        ┌───────┴────────┐
        │                │
   ┌────▼────┐     ┌─────▼─────┐
   │ POM/DOM │     │ Nutrients │
   │ 有机质  │     │  N/P/Si   │
   └─────────┘     └───────────┘
```

### 4.2 营养级流转

| 营养级 | 组分 | 主要食物 | 主要捕食者 |
|--------|------|----------|------------|
| 5 | PiscFish | AdFish, JuFish | （顶级） |
| 4 | AdFish, JuFish | Cladocerans, Copepods, Zoobenthos, POM | PiscFish |
| 3 | Cladocerans, Copepods, Zoobenthos | 藻类, POM, 底栖藻类 | Fish |
| 2 | Cyanobacteria, Diatoms, Greens, Macrophytes | 营养盐, 光, CO2 | Zooplankton, Zoobenthos |
| 1 | POM, DOM, NH4, NO3, PO4, SiO2 | （基础资源） | 藻类、细菌 |

---

## 五、各模块方程详解

### 5.1 浮游植物模块（phytoplankton.F90）

**变量类型**：3D 浮游（`type_state_variable_id`），单位 gDW/m³，同时追踪 N、P、C、Si（硅藻）
**过程**：`do`（3D 浮游动力学）、`do_bottom`（沉降通量）、`get_vertical_movement`（被动沉降速度）

**核心方程**：

```
# 生长率
aMu = aNutLim · aMuTmL · aNFixLim        # 实际生长率
aMuTmL = ufDay · (1 - afCovSurfVeg) · aLLim · uFunTm · cMuMax

# 光限制（无光抑制形式）
aLLim = 1/(extc·dz) · ln[(1 + uLPARSurf/uhL) / (1 + aLPARBot/uhL)]

# 营养盐限制（Liebig 最小定律）
aNutLim = min(aPLim, min(aNLim, aSiLim))   # 硅藻
aNutLim = min(aPLim, aSiLim)               # 蓝藻（可固氮）
aPLim = sPO4W / (hP + sPO4W)
aNLim = sNH4W + sNO3W / (hN + sNH4W + sNO3W)
aSiLim = sSiO2W / (hSiAss + sSiO2W)

# 温度响应（高斯曲线）
uFunTm = exp(-((uTm - cTmOpt) / cSigTm)²)

# 同化（生长）
wDAss = aMu · sDW

# 呼吸
wDRespW = kDResp · uFunTm · sDW

# 死亡
wDMortW = kMortW · sDW

# 营养盐摄取（Droop 型，参照最佳 N/D, P/D 比）
wPUpt = wDAss · cPDDes
wNUpt = wDAss · cNDDes
```

**状态变量**：sDW, sPW, sNW, sCW, sSiW（硅藻）

### 5.2 浮游动物模块（zooplankton.F90）

**变量类型**：3D 浮游，单位 gDW/m³
**核心方程**：

```
# 摄食（Holling Type II，多猎物）
aFeedLvl = sum(cClearPrey·fGutOccPrey·sDPrey) /
           (sum(cClearPrey·fGutOccPrey·sDPrey) + uFunTm·fO2·kDConsMax)
tDConsPrey = sDZoo · cClearPrey · sDPrey · (1 - aFeedLvl)

# 同化
tDAssZoo = fDAss · sum(tDConsPrey)

# 呼吸、死亡、排出
tDRespZoo = kDResp · uFunTm · sDZoo
tDMortZoo = kMort · sDZoo
tDEgesZoo = sum(tDConsPrey) - tDAssZoo
```

### 5.3 沉水植物模块（macrophytes.F90）

**变量类型**：**2D 底栖**（`type_bottom_state_variable_id`），单位 **gDW/m²**
**过程**：仅有 `do_bottom`（无 `do`）+ `get_light_extinction`（自遮蔽反馈）
**3D 镜像**：通过 `_PV` 变量（`disable_transport=.true.`）与浮游域耦合

**核心方程**：

```
# 在 do_bottom 中计算：
# - 生长（消耗水柱营养盐，通过 _PV 读取）
# - 死亡、呼吸
# - 生物量以 g/m² 存储

# 桥接到浮游域：
_SET_BOTTOM_EXCHANGE_(id_sDVeg_PV, tDBedVeg · bot_pel_conv)
# tDBedVeg 单位 g/m²/s，乘以 bot_pel_conv=1/dz 后转为 g/m³/s
```

**关键特性**：
- 沉水植物是**严格的 2D 底栖变量**，无空间输运
- 通过 `_SET_BOTTOM_EXCHANGE_` 将其营养盐通量投影到 3D 水柱
- 水柱中浮游变量通过 `id_sDVeg_PV` 读取沉水植物生物量（用于光照遮蔽等）

### 5.4 底栖动物模块（zoobenthos.F90）

**变量类型**：**纯 2D 底栖**，单位 **gDW/m²**
**过程**：**仅有 `initialize` 和 `do_bottom`**（无 `do`，无 `get_vertical_movement`）

**核心方程**：

```
# 摄食（清除率面积扫描模型，可同时摄食浮游和底栖猎物）
aFeedLvlBent = sum(cClearPrey·fGutOccPrey·sDPrey) /
               (sum(cClearPrey·fGutOccPrey·sDPrey) + uFunTmBent·fO2·kDConsMaxBent)
tDConsBent = sDBent · cClearPrey · sDPrey · (1 - aFeedLvlBent)

# 同化、呼吸、死亡
tDAssBent = fDAssBent · sum(tDConsBent)
tDRespBent = kDRespBent · uFunTm · sDBent
tDMortBent = kMortBent · sDBent

# 摄食浮游猎物时，通过 _SET_BOTTOM_EXCHANGE_ 影响水柱：
_SET_BOTTOM_EXCHANGE_(id_PreyD_PV, -tDConsBent(i_prey) · bot_pel_conv)
# 摄食底栖猎物时，直接更新底栖 ODE：
_SET_BOTTOM_ODE_(id_PreyD(i_prey), -tDConsBent(i_prey))
```

**关键特性**：
- 底栖动物是**纯 2D 底栖变量**，无任何空间输运
- 单位 g/m²，清除率单位 m²/gDW/d（体现"单位面积扫描"摄食策略）
- 摄食浮游猎物时通过 `_SET_BOTTOM_EXCHANGE_` 反向影响水柱

### 5.5 鱼类模块（fish.F90）

**变量类型**：**3D 浮游**（`type_state_variable_id`），单位 **gDW/m³**
**过程**：6 个——`initialize`、`do`（3D 浮游动力学）、`do_bottom`（底栖捕食）、`get_vertical_movement`（主动垂直迁移）、`check_state`（繁殖）、`calc_ODB`（最优食谱）

**核心方程**：

```
# 3D 浮游动力学（do 子程序）：
# 摄食（最优食谱 ODB 选择猎物组合）
tDAssFiTot = sum(tDAssFi)                # 总同化
tDRespFi = kDResp · uFunTm · sDFi         # 呼吸
rG = (tDAssFiTot - tDRespFi) / sDFi       # 比生长率

# 结构-储能分配
fIrreversible = 1/((1+q)·q) · fRes_now    # 储能向结构质量转化

# 状态更新（_ADD_SOURCE_ 等价于 _SET_ODE_ 的 rhs）
_SET_ODE_(id_sDFi, tDAssFiTot - tDRespFi - tDMortFi)
_SET_ODE_(id_sNFi, tNAssFiTot - tNRespFi - tNMortFi)
# ...（类似 P, C）

# 底栖捕食（do_bottom 子程序）：
# 鱼类摄食底栖动物等底栖猎物，通过 _SET_BOTTOM_ODE_ 更新底栖变量
# 摄食量通过 _SET_BOTTOM_EXCHANGE_ 投影到鱼类 3D 变量

# 垂直迁移（get_vertical_movement 子程序）：
# qTrans 参数控制：
#   0 = 无垂直迁移
#   1 = 被动迁移
#   2 = O2 驱动（低 O2 时向上迁移）
#   3 = O2 + 光照驱动（昼夜垂直迁移）
if (qTrans == 2 .OR. qTrans == 3):
    if (O2 < cMinO2):
        vSWIM = +cVswim    # 向上迁移
if (qTrans == 3):
    if (par > cMaxLight): vSWIM = -cVswim   # 强光向下
    elif (par < cMinLight): vSWIM = +cVswim # 弱光向上
```

**关键特性**：
- 鱼类是**唯一真正 3D 的生物模块**，受完整 3D 平流-扩散输运
- 单位 gDW/m³，与浮游植物、浮游动物一致
- 同时具备 `do`（3D）和 `do_bottom`（2D 捕食），是跨域耦合最复杂的模块
- 通过 `get_vertical_movement` 实现主动垂直迁移（区别于被动沉降）

### 5.6 有机质模块（om_pool.F90）

**变量类型**：3D 浮游（POM、DOM、Humus）+ 2D 底栖（沉积物中的 POM、DOM）
**核心方程**：

```
# 水柱 POM 矿化
wDMinerW = kDMiner · uFunTm · sDPOM
# 水柱 DOM 矿化
wDDOMMinW = kDDOMMin · uFunTm · sDDOM
# 反硝化（在 om_pool 中实现）
wNDenitW = kDenit · uFunTm · fO2lim · sNO3W
```

### 5.7 营养盐-水柱模块（abiotic_water.F90）

**变量类型**：3D 浮游，单位 g/m³
**核心方程**：

```
# 硝化（温度 + O2 限制）
uFunTmNitr = uFunTmArrh(uTm, cThetaNitrW)              # Arrhenius 型温度函数
aCorO2NitrW = sO2W / (hO2Nitr + sO2W)                  # O2 限制
wNNitrW = kNitrW · uFunTmNitr · aCorO2NitrW · sNH4W    # 硝化通量
wO2NitrW = O2PerNH4W · molO2molN · wNNitrW              # 硝化耗氧

# 大气复氧
wO2AirW = kO2Air · (pO2Sat - sO2W) · afAreaAir
```

### 5.8 沉积物-水柱交换模块（sediment_exchange.F90）

**变量类型**：2D 底栖（耦合 3D）
**核心方程**：

```
# 再悬浮（剪切应力驱动）
wDResus = cResus · max(0, tauB - tauCrit)
# 沉降
wDSettl = cSettl · sDPOM
# 营养盐扩散
wNH4Diff = kDiff · (sNH4S - sNH4W)
```

### 5.9 底栖-浮游桥接模块（bot_pel_interface.F90）

**核心功能**：计算 `bot_pel_conv = 1/dz`，作为所有 `_SET_BOTTOM_EXCHANGE_` 的转换因子
**作用**：将底栖通量（g/m²/s）转换为浮游域通量（g/m³/s）

---

## 六、GETM-FABM-WET 耦合方式

### 6.1 GETM-GOTM 耦合

- GETM 调用 GOTM 计算垂直混合
- 数据流：GETM → GOTM（水平流速、密度梯度、剪切应力）；GOTM → GETM（垂直涡粘性、扩散系数）
- 湍流模型：k-ε 二阶闭合模型（`turb_method=2`）

### 6.2 GETM-FABM 耦合（核心：getm_fabm.F90）

GETM 与 FABM 的耦合通过 [getm_fabm.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/getm/src/3d/getm_fabm.F90) 实现，关键机制：

#### 6.2.1 变量内存分离

```fortran
! 浮游变量：3D 场 (I3DFIELD)，受平流-扩散输运
fabm_pel(I3DFIELD, n)

! 底栖变量：2D 场 (I2DFIELD)，无输运
fabm_ben(I2DFIELD, n)
```

#### 6.2.2 GETM → FABM 提供的物理环境

- 水温 `temp`、盐度 `salt`（淡水湖关闭）
- 流速分量 `u, v, w`
- 光强（PAR，由短波辐射计算）
- 水深、层厚 `dz`
- 剪切应力（用于再悬浮）

#### 6.2.3 FABM → GETM 的反馈

- **消光系数**：WET 浮游植物、POM 等贡献消光（`shade=true` 时启用）
- **生物自遮蔽**：沉水植物、浮游植物叶绿素等改变光衰减

### 6.3 FABM-WET 耦合（核心：FABM 类型系统）

FABM 通过**变量类型系统**实现 WET 模块的 3D/2D 区分：

#### 6.3.1 三类状态变量

| 类型 | Fortran 类型 | 维度 | 单位 | 输运 | 典型模块 |
|------|-------------|------|------|------|----------|
| 浮游状态变量 | `type_state_variable_id` | 3D | g/m³ | 完整 3D 平流+扩散 | 藻类、浮游动物、鱼类、水柱营养盐 |
| 底栖状态变量 | `type_bottom_state_variable_id` | 2D | g/m² | 无输运 | 沉水植物、底栖动物、沉积物池 |
| 浮游镜像（_PV） | `type_state_variable_id` + `disable_transport=.true.` | 3D | g/m³ | 无输运（仅映射） | 沉水植物、底栖动物的 3D 镜像 |

#### 6.3.2 过程（Procedure）类型

每个 WET 模块继承自 `type_particle_model`，可重写以下过程：

| 过程 | 作用域 | 典型用途 |
|------|--------|----------|
| `do` | 3D 浮游 | 计算浮游变量 ODE 右端 |
| `do_bottom` | 2D 底栖 | 计算底栖变量 ODE 右端 + 底栖-浮游通量 |
| `get_vertical_movement` | 3D 浮游 | 主动垂直迁移速度（鱼类） |
| `get_light_extinction` | 全局 | 贡献消光系数（藻类、沉水植物） |
| `check_state` | 状态检查 | 繁殖、边界约束（鱼类） |

#### 6.3.3 底栖-浮游桥接（_SET_BOTTOM_EXCHANGE_）

这是 FABM 实现 2D-3D 耦合的核心机制：

```fortran
! 在 do_bottom 中，将底栖通量投影到浮游镜像变量
_SET_BOTTOM_EXCHANGE_(id_sDVeg_PV, tDBedVeg * bot_pel_conv)
```

- `tDBedVeg`：底栖通量，单位 g/m²/s
- `bot_pel_conv = 1/dz`：转换因子
- 结果：浮游镜像变量 `_PV` 收到 g/m³/s 的通量
- 其他浮游模块通过 `_GET_(id_sDVeg_PV, sDVeg)` 读取该值

#### 6.3.4 WET 模块清单（17 个 Fortran 模块）

| 模块 | 类型 | 主要过程 |
|------|------|----------|
| abiotic_water | 3D 浮游 | do |
| abiotic_sediment | 2D 底栖 | do_bottom |
| phytoplankton | 3D 浮游 + 2D 底栖 | do, do_bottom, get_vertical_movement |
| zooplankton | 3D 浮游 | do |
| macrophytes | 2D 底栖 + 3D 镜像 | do_bottom, get_light_extinction |
| zoobenthos | 2D 底栖 | do_bottom |
| fish | 3D 浮游 + 2D 底栖 | do, do_bottom, get_vertical_movement, check_state |
| om_pool | 3D 浮游 + 2D 底栖 | do, do_bottom |
| sediment_exchange | 2D 底栖（耦合 3D） | do_bottom |
| burial | 2D 底栖 | do_bottom |
| bot_pel_interface | 2D 底栖 | do_bottom（计算 bot_pel_conv） |
| (其他辅助模块) | - | - |

---

## 七、食物网组分的三维实现方式（核心问题）

**用户核心问题**：鱼类、水生植物、底栖动物等食物网组分的三维模拟实现方式，是改为了偏微分方程还是独立网格的常微分方程求解，还是其他？

### 7.1 核心结论

**所有 WET 生态模块的内部动力学均采用常微分方程（ODE）求解，并非偏微分方程（PDE）。三维空间分布通过 FABM 的变量类型系统 + GETM 的平流-扩散输运实现，具体方式因变量类型而异。**

### 7.2 三种实现方式详解

#### 7.2.1 方式一：3D 浮游 ODE + GETM 输运（PDE 框架内的输运项）

**适用组分**：浮游植物、浮游动物、鱼类、水柱营养盐（NH4、NO3、PO4、SiO2）、水柱有机质（POM、DOM）

**数学形式**：
```
∂C/∂t = f(C, 环境) + ∇·(D∇C) - ∇·(vC) + w·∂C/∂z
         └─ODE 右端─┘  └─扩散项─┘  └─平流项─┘  └─沉降/迁移─┘
```

**实现分工**：
- **ODE 右端 `f(C, 环境)`**：由 WET 模块的 `do` 子程序计算（生物生长、摄食、死亡、化学反应等）
- **输运项 `∇·(D∇C) - ∇·(vC)`**：由 GETM 的标量输运方程求解（3D 平流-扩散）
- **垂直运动 `w`**：由 `get_vertical_movement` 提供（鱼类主动迁移、藻类沉降）

**关键点**：
- WET 模块本身**不求解 PDE**，只计算 ODE 右端
- GETM 负责 3D 空间输运，将每个网格的 ODE 解通过平流-扩散耦合起来
- 这是一种"算子分裂"（operator splitting）方法：生物反应 + 物理输运分开求解

#### 7.2.2 方式二：纯 2D 底栖 ODE（无输运）

**适用组分**：底栖动物、沉积物营养盐池、埋藏池

**数学形式**：
```
dB/dt = g(B, 环境, 浮游输入)    ← 单个水平网格内的 ODE
```

**实现分工**：
- WET 模块的 `do_bottom` 子程序计算 ODE 右端
- **无空间输运**：底栖变量在水平方向上不发生迁移
- 每个水平网格 (i,j) 独立求解底栖 ODE

**关键点**：
- 单位 g/m²，不涉及垂直分层
- 水平方向无扩散、无平流
- 与浮游域的耦合通过 `_SET_BOTTOM_EXCHANGE_`（摄取浮游猎物、释放营养盐到水柱）

#### 7.2.3 方式三：2D 底栖 ODE + 3D 镜像（_PV）耦合

**适用组分**：沉水植物、底栖有机质池

**数学形式**：
```
# 2D 底栖主体（真实状态）
dB/dt = g(B, 环境, 浮游输入)

# 3D 浮游镜像（_PV，只读映射）
C_PV = B · bot_pel_conv = B / dz    ← 单位转换 g/m² → g/m³
```

**实现分工**：
- 底栖主体 `B` 由 `do_bottom` 求解，无输运
- 3D 镜像 `_PV` 不参与输运（`disable_transport=.true.`），仅作为"读取接口"供其他浮游模块访问
- 通过 `_SET_BOTTOM_EXCHANGE_` 将底栖通量投影到浮游域

**关键点**：
- 沉水植物本质上仍是 2D 底栖生物，**不发生空间输运**
- 3D 镜像只是让浮游模块能"看到"底栖生物量（用于光照遮蔽、营养盐竞争等）
- `_PV` 变量在 GETM 输出中体现为 3D 场，但底层存储仍是 2D

### 7.3 各食物网组分的具体实现方式

| 组分 | 变量类型 | 单位 | 空间输运 | 垂直运动 | 求解方式 |
|------|----------|------|----------|----------|----------|
| **浮游植物**（蓝藻、硅藻、绿藻） | 3D 浮游 | gDW/m³ | 3D 平流+扩散 | 被动沉降（`get_vertical_movement`） | ODE + GETM 输运 |
| **浮游动物**（枝角类、桡足类） | 3D 浮游 | gDW/m³ | 3D 平流+扩散 | 无主动迁移 | ODE + GETM 输运 |
| **鱼类**（幼鱼、成鱼、食鱼鱼） | 3D 浮游 | gDW/m³ | 3D 平流+扩散 | **主动垂直迁移**（O2/光照驱动） | ODE + GETM 输运 + 主动迁移 |
| **沉水植物** | 2D 底栖 + 3D 镜像 | gDW/m² | **无输运** | 无（固着生长） | 纯 2D ODE + 镜像耦合 |
| **底栖动物** | 2D 底栖 | gDW/m² | **无输运** | 无 | 纯 2D ODE |
| **水柱营养盐**（NH4、NO3、PO4、SiO2） | 3D 浮游 | g/m³ | 3D 平流+扩散 | 无 | ODE + GETM 输运 |
| **水柱有机质**（POM、DOM） | 3D 浮游 | g/m³ | 3D 平流+扩散 | 被动沉降 | ODE + GETM 输运 |
| **沉积物营养盐池** | 2D 底栖 | g/m² | **无输运** | 无 | 纯 2D ODE |

### 7.4 为什么不是独立网格的常微分方程？

用户问题中提到"独立网格的常微分方程求解"。实际上，3DWET 的实现**部分符合**这一描述，但需要澄清：

1. **对于底栖变量**（沉水植物、底栖动物、沉积物池）：**确实是独立网格的 ODE**。每个水平网格 (i,j) 独立求解底栖 ODE，网格之间无直接耦合（除非通过浮游域间接耦合）。

2. **对于浮游变量**（藻类、浮游动物、鱼类、营养盐）：**不是独立网格的 ODE**。虽然 WET 模块本身只计算每个网格的 ODE 右端，但 GETM 的 3D 平流-扩散将所有网格耦合在一起，形成完整的 PDE 求解。

3. **整体框架**：可以理解为"在每个网格内是 ODE，网格之间通过 GETM 输运耦合"，即算子分裂法（operator splitting）求解反应-输运方程。

### 7.5 为什么不是偏微分方程？

WET 模块本身**不求解 PDE**：

1. WET 模块的 Fortran 代码中只有 `do`（计算时间导数 `dC/dt`）和 `do_bottom`（计算 `dB/dt`），没有空间导数项。
2. 空间导数（平流、扩散）完全由 GETM 的标量输运模块处理，WET 模块对此"无感知"。
3. WET 模块通过 FABM 的 `_SET_ODE_`（或 `_ADD_SOURCE_`）接口提交 ODE 右端，由 FABM 时间积分器求解；GETM 则独立求解输运方程。

但从整体数学框架看，浮游变量的完整方程是**反应-输运 PDE**，只是通过算子分裂法将反应项（ODE）和输运项（PDE）分开求解。

---

## 八、数值求解方法

### 8.1 时间积分器（ode_method）

FABM 提供多种 ODE 求解器，通过 `gotm_fabm.yaml` 的 `ode_method` 参数选择：

| ode_method | 求解器 | 特性 | 适用场景 |
|-----------|--------|------|----------|
| 1 | Forward Euler | 一阶显式，简单快速 | 调试、快速测试 |
| 2 | Runge-Kutta 4 | 四阶显式，精度高 | 一般生产运行 |
| 3 | Patankar | 一阶隐式，保正性 | 含负值敏感变量的系统 |
| 10 | Extended Modified Patankar | 保正性 + 质量守恒 | **生产推荐**（WET 默认） |

**Lake Luoma 当前配置**：`ode_method=1`（Forward Euler），与 Theoretical Lake 一致，用于调试对齐。生产环境建议改用 `ode_method=10`（Patankar），保证生态变量非负且质量守恒。

### 8.2 时间步长

- **GETM 水动力**：dt = 15s（满足 CFL 条件，特别是在河流入口附近）
- **FABM 生态**：`split_factor=1`，即每个 GETM 时间步调用一次 FABM
- **总运行时间**：Lake Luoma 模拟 2020-01-01 至 2022-12-30，共 1094 天，约 6,301,440 步

### 8.3 空间离散

- **水平网格**：正交曲线网格（cartesian 模式下为笛卡尔网格）
- **垂直坐标**：σ 坐标（`vert_cord=1`），随地形伸缩
- **平流格式**：`ip_method=2`（TVD 类型，高精度）

### 8.4 输出

- **格式**：netCDF（`output.nc`）
- **时间步**：每日输出一次（`output.yaml: time_step=1, time_unit=day`）
- **变量**：所有状态变量 + 诊断变量（`source: *`）

---

## 九、模型文件与配置

### 9.1 关键源代码位置

| 模块 | 路径 |
|------|------|
| WET 生态模块 | [src/wet/src/](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/) |
| GETM-FABM 接口 | [src/getm/src/3d/getm_fabm.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/getm/src/3d/getm_fabm.F90) |
| GOTM-FABM 接口 | [src/gotm/fabm/gotm_fabm.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/gotm/fabm/gotm_fabm.F90) |
| 修复补丁 | [patches/](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/patches/) |

### 9.2 Lake Luoma 配置文件

| 文件 | 关键参数 | 说明 |
|------|----------|------|
| [getm.inp](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma/getm.inp) | timestep=15s, ip_method=2, vel_check=1, vert_cord=1(σ) | 水动力配置 |
| [getm_fabm.inp](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma/getm_fabm.inp) | fabm_init_method=1 | FABM 初始化 |
| [gotm_fabm.yaml](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma/gotm_fabm.yaml) | ode_method=1, shade=false, split_factor=1 | FABM 求解器配置 |
| [fabm.yaml](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma/fabm.yaml) | 965 行，含所有 WET 模块参数 | 生态模块参数（已移除 fish，macrophytes _PV=0.0） |
| [output.yaml](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake%20Luoma/output.yaml) | time_step=1 day, source=* | 输出配置 |

### 9.3 已应用的修复补丁

| 补丁 | 修复内容 |
|------|----------|
| [fish_v2_patched.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/patches/fish_v2_patched.F90) | `check_state` 中 `id_sFRes` 未注册时的越界访问（添加 `if (qStage > 0)` 保护） |
| [gotm_fabm_itime_fixed.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/patches/gotm_fabm_itime_fixed.F90) | `time_step` 悬空指针（链接从 `init_gotm_fabm` 移至 `set_env_gotm_fabm`） |
| [om_pool_patched.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/patches/om_pool_patched.F90) | `bot_pel_conv` 水平依赖和 `_SET_BOTTOM_EXCHANGE_` 镜像更新 |

---

## 附录：关键术语速查

| 术语 | 含义 |
|------|------|
| `type_state_variable_id` | FABM 3D 浮游状态变量类型（g/m³，受输运） |
| `type_bottom_state_variable_id` | FABM 2D 底栖状态变量类型（g/m²，无输运） |
| `_PV` | Pelagic View，底栖变量的 3D 浮游镜像（`disable_transport=.true.`） |
| `bot_pel_conv` | 底栖-浮游转换因子 = 1/dz，用于 g/m² ↔ g/m³ 转换 |
| `_SET_ODE_` | 提交 3D 浮游变量 ODE 右端 |
| `_SET_BOTTOM_ODE_` | 提交 2D 底栖变量 ODE 右端 |
| `_SET_BOTTOM_EXCHANGE_` | 提交底栖→浮游通量（自动乘 `bot_pel_conv`） |
| `do` | 计算 3D 浮游动力学的过程 |
| `do_bottom` | 计算 2D 底栖动力学 + 底栖-浮游通量的过程 |
| `get_vertical_movement` | 提供主动垂直迁移速度（仅鱼类等） |
| `ode_method` | FABM 时间积分器选择（1=Euler, 10=Patankar） |
| `shade` | 生物自遮蔽反馈（浮游植物/沉水植物改变消光系数） |

---

*本文档基于 3DWET 源代码（17 个 WET 模块 + GETM-FABM 接口）和 Lake Luoma 案例配置编写，适用于理解 GETM-FABM-WET 耦合体系的完整技术细节。*
