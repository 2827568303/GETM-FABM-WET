# 3DWET 模型技术报告

> **文档定位**：面向模型使用者与技术评估者的完整技术手册
> **版本范围**：3DWET（GETM + GOTM + FABM + WET 耦合体系）
> **适用场景**：淡水湖泊三维水动力-生态耦合模拟

---

## 目录

- [一、模型架构](#一模型架构)
  - [1.1 总体架构](#11-总体架构)
  - [1.2 耦合方式](#12-耦合方式)
  - [1.3 目录结构](#13-目录结构)
- [二、WET 模块详解](#二wet-模块详解)
- [三、输入数据要求](#三输入数据要求)
- [四、编译与运行](#四编译与运行)
- [五、建模建议](#五建模建议)
- [六、模型限制](#六模型限制)
- [七、验证与基准](#七验证与基准)

---

## 一、模型架构

### 1.1 总体架构

3DWET 是由四个开源组件深度耦合而成的三维湖泊生态模型，各组件分工明确、层次清晰：

| 组件 | 全称 | 角色 | 主要职责 |
|------|------|------|----------|
| **GETM** | General Esturbine Transport Model | 3D 水动力模型 | 提供水流、水温、物质输运 |
| **GOTM** | General Ocean Turbulence Model | 垂向湐流模型 | 计算垂直涡粘性 / 扩散系数 |
| **FABM** | Framework for Aquatic Biogeochemical Models | 生地化耦合框架 | 状态变量注册、时间积分、诊断变量管理 |
| **WET** | Water Ecology Treatment | 生态模型 | PCLake 的 FABM 版本，提供完整食物网 |

**架构层次示意**：

```
┌─────────────────────────────────────────────────────────┐
│                  WET (生态食物网模型)                     │
│  浮游植物 / 浮游动物 / 底栖动物 / 鱼类 / 沉水植物 / 有机质   │
└─────────────────────────────────────────────────────────┘
                          ▲ ▼
┌─────────────────────────────────────────────────────────┐
│                   FABM (耦合框架)                         │
│       状态变量注册 / 时间积分 / 诊断变量管理 / 同步          │
└─────────────────────────────────────────────────────────┘
                          ▲ ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│   GETM (3D 水动力)         │  │   GOTM (垂向湐流)         │
│   水流 / 水温 / 物质输运     │←→│   k-ε 模型 / 垂直混合     │
└──────────────────────────┘  └──────────────────────────┘
```

**WET 模型由瓦赫宁根大学开发**，是经典 PCLake 模型的 FABM 重构版本，保留了 PCLake 完整的食物网结构，同时获得了 FABM 框架带来的多模型耦合能力。

### 1.2 耦合方式

3DWET 的耦合体系包含四个层次，通过明确的接口完成数据交换：

#### 1.2.1 GETM-GOTM 耦合

- **角色分工**：GETM 调用 GOTM 计算垂直混合
- **数据流**：
  - GETM → GOTM：水平流速、密度梯度、剪切应力
  - GOTM → GETM：垂直涡粘性系数、垂直扩散系数
- **湐流模型**：k-ε 二阶闭合模型（`turb_method=2`）

#### 1.2.2 GETM-FABM 耦合

通过 `getm_fabm.F90` 接口实现：

- **GETM → FABM 提供的物理环境**：
  - 水温 `temp`
  - 盐度 `salt`（淡水湖关闭）
  - 流速分量 `u, v, w`
  - 光强（PAR，由短波辐射计算）
  - 水深、层厚 `dz`
  - 剪切应力（用于再悬浮）
- **FABM → GETM 返回**：
  - 生化变量分布（营养盐、浮游植物、动物等）
  - 生物自遮光衰减系数（`shade` feedback）
  - 表面反照率修改（`albedo` feedback）
  - 表面拖曳系数修改（`surface_drag` feedback）

#### 1.2.3 FABM-WET 耦合

WET 模块通过 FABM 框架完成注册：

- **状态变量注册**：每个生态模块通过 `register_state_variable` 注册状态变量，FABM 统一管理
- **诊断变量注册**：通过 `register_diagnostic_variable` 注册用于输出和耦合的中间量
- **时间积分**：FABM 统一调度，使用 Patankar 保正方法（`ode_method=10`）
- **横向耦合**：通过 `link_interior_data` 完成模块间依赖（如浮游植物读取营养盐）

#### 1.2.4 时间同步

- **GETM 时间步**：30 秒（必须，更大步长导致数值不稳定）
- **FABM 调用频率**：每个 GETM 时间步调用一次 FABM
- **itime 参数**：`(yearday-1)*86400 + secondsofday`
  - `yearday`：年积日（1-366）
  - `secondsofday`：当日秒数（0-86399）
- **关键作用**：`itime` 推进 `meanpar`（24h 平均 PAR）的时间窗口，**必须正确传递**，否则浮游植物光照限制 `aLLim=0`，导致生态崩溃

### 1.3 目录结构

```
3DWET/
├── src/
│   ├── getm/          # GETM 水动力源码
│   │   └── src/3d/getm_fabm.F90     # GETM-FABM 耦合接口
│   ├── gotm/          # GOTM 湐流源码
│   │   └── src/fabm/gotm_fabm.F90   # GOTM-FABM 接口
│   ├── fabm/          # FABM 框架源码
│   └── wet/           # WET 生态模型源码
│       └── src/
│           ├── wet_model_library.F90   # 模型注册入口
│           ├── abiotic_water.F90       # 水相非生物过程
│           ├── abiotic_sediment.F90    # 沉积物非生物过程
│           ├── phytoplankton.F90       # 浮游植物（3 群）
│           ├── zooplankton.F90         # 浮游动物（2 群）
│           ├── macrophytes.F90         # 沉水植物
│           ├── zoobenthos.F90          # 底栖动物
│           ├── fish.F90                # 鱼类（3 功能群）
│           ├── fish_pclake.F90         # PCLake 风格鱼类（legacy）
│           ├── om_pool.F90             # 有机质池（POM/DOM）
│           ├── sediment_exchange.F90   # 沉积物-水交换
│           ├── burial.F90              # 沉积物埋藏
│           ├── resus_sed.F90           # 再悬浮
│           ├── bivalves.F90            # 双壳类（可选）
│           ├── bot_pel_interface.F90   # 底栖-浮游界面
│           └── utility.F90             # 工具函数
├── patches/           # 4 个 Bug 修复 patch
├── scripts/           # 70+ 自动化脚本
├── case/              # 3 个测试 case
│   ├── Lake Luoma/        # 骆马湖
│   ├── Theoretical lake/  # 理论湖
│   └── Yilong/            # 异龙湖
├── build/             # 编译中间产物
├── install/           # 安装目录（bin/getm_cartesian）
└── docs/              # 文档
```

---

## 二、WET 模块详解

### 2.1 abiotic_water（水相非生物过程）

#### 2.1.1 模块职责

模拟水柱中无机营养盐与无机悬浮物的动力学，为生物过程提供营养盐基底，接收矿化产物。

#### 2.1.2 状态变量

| 变量名 | 含义 | 单位 |
|--------|------|------|
| `sNH4W` | 水相氨氮 | gN/m³ |
| `sNO3W` | 水相硝氮 | gN/m³ |
| `sPO4W` | 水相溶解态磷 | gP/m³ |
| `sO2W` | 水相溶解氧 | gO/m³ |
| `sSiO2W` | 水相溶解态硅 | gSi/m³ |
| `sDIMW` | 水相无机悬浮颗粒物 | gDW/m³ |
| `sPAIMW` | 颗粒吸附磷 | gP/m³ |
| `sSiPaW` | 颗粒硅 | gSi/m³ |

#### 2.1.3 关键过程与方程

**硝化过程**（NH4 → NO3）：

```
dNH4W/dt|nitr = -kNitrW * uFunTm * sNH4W
uFunTm  = Q10^((T - 20)/10),  Q10 = 1.03
kNitrW  = 0.3 /d（基础速率）
```

**磷吸附 / 解吸**：

```
dPO4W/dt|sorp   = -kPSorpW * sPO4W + kPSorpW * (sPAIMW / cKPAdsOxW)
kPSorpW = 0.05 /d
cKPAdsOxW = 0.6（氧化条件吸附系数）
```

**无机颗粒物沉降**：

```
flux_DIM = cVSetIM * sDIMW / dz
cVSetIM = -1.1 m/d（负值=下沉）
```

**复氧**（O2 大气交换）：

```
dO2W/dt|aer = kAer * (cO2Sat - sO2W) * cThetaAer^(T-20)
cThetaAer = 1.011
```

#### 2.1.4 关键参数

| 参数 | 默认值 | 含义 |
|------|--------|------|
| `O2PerNH4W` | 2.0 | 每克 NH4 硝化耗氧（gO/gN） |
| `cExtSpIM` | 0.05 | 无机颗粒物消光系数（m²/gDW） |
| `cKPAdsOxW` | 0.6 | 氧化条件磷吸附系数 |
| `kNitrW` | 0.3 | 水相硝化速率（/d） |
| `cVSetIM` | -1.1 | 无机颗粒沉降速率（m/d） |
| `cThetaAer` | 1.011 | 复氧温度系数 |

#### 2.1.5 模块耦合

- **输出至**：浮游植物（提供 NH4/NO3/PO4/SiO2 营养盐）
- **接收自**：om_pool（矿化释放的 NH4/PO4）、沉积物交换（沉积物释放的营养盐）

---

### 2.2 abiotic_sediment（沉积物非生物过程）

#### 2.2.1 模块职责

模拟沉积物间隙水中的无机营养盐动力学，与水相通过扩散交换，受生物扰动影响。

#### 2.2.2 状态变量

| 变量名 | 含义 | 单位 |
|--------|------|------|
| `sNH4S` | 沉积物氨氮 | gN/m² |
| `sNO3S` | 沉积物硝氮 | gN/m² |
| `sPO4S` | 沉积物溶解态磷 | gP/m² |
| `sPAIMS` | 沉积物颗粒吸附磷 | gP/m² |
| `sDIMS` | 沉积物无机颗粒 | gDW/m² |
| `sSiO2S` | 沉积物溶解硅 | gSi/m² |
| `sSiPaS` | 沉积物颗粒硅 | gSi/m² |

#### 2.2.3 关键过程

**沉积物硝化 / 反硝化**：
- 硝化速率 `kNitrS = 1.2 /d`（比水相 `kNitrW=0.3` 高 4 倍，因沉积物富氧层微生物活跃）
- 反硝化仅在缺氧层发生

**磷吸附**：
- `cKPAdsOxS = 1.5`（比水相 `cKPAdsOxW=0.6` 高，沉积物对磷的固定能力更强）

**生物扰动扩散**：
- `cTurbDifO2 = 5.0`（底栖动物活动增强 O2 渗透深度）
- `cTurbDifNut = 12.0`（营养盐扩散增强系数）

#### 2.2.4 关键参数

| 参数 | 默认值 | 含义 |
|------|--------|------|
| `bPorS` | 0.58 | 沉积物孔隙率 |
| `cDepthS` | 0.1 | 沉积物活跃层厚度（m） |
| `kNitrS` | 1.2 | 沉积物硝化速率（/d） |
| `cKPAdsOxS` | 1.5 | 沉积物氧化层磷吸附系数 |
| `cTurbDifO2` | 5.0 | O2 生物扰动扩散系数 |

#### 2.2.5 模块耦合

- 与 `abiotic_water` 通过 `sediment_exchange` 完成扩散通量交换
- 与 `zoobenthos` 联动：底栖动物生物扰动影响扩散速率

---

### 2.3 phytoplankton（浮游植物，3 群）

#### 2.3.1 模块职责

模拟浮游植物三大功能群的生长、沉降、牧食与死亡，是初级生产力的核心模块。

#### 2.3.2 三个功能群

| 功能群 | 学名 | cMuMax (/d) | 最适温度 (°C) | 沉降速率 (m/d) | 生态策略 |
|--------|------|-------------|---------------|----------------|----------|
| **硅藻** | diatoms | 2.4 | 18 | -0.5（下沉） | 早春优势，依赖硅，重下沉 |
| **绿藻** | greens | 1.0 | 25 | -0.35（下沉） | 中等生长，广温性 |
| **蓝藻** | cyanobacteria | 1.5 | 25 | +0.03（上浮） | 夏秋高温水华，气浮调节 |

#### 2.3.3 状态变量（每群 4 个，共 12 个）

| 变量 | 含义 | 单位 |
|------|------|------|
| `sDW` | 干重 | gDW/m³ |
| `sNW` | 氮含量 | gN/m³ |
| `sPW` | 磷含量 | gP/m³ |
| `sCW` | 碳含量 | gC/m³ |

#### 2.3.4 关键过程与方程

**光照限制（Steele 光抑制模型）**：

依赖 **24h 平均 PAR**（`meanpar`），而非瞬时 PAR：

```
uLPARSurf = meanpar / EXP(-extc * dz / 2)    # 层顶光强
aLPARBot  = meanpar * EXP(-extc * dz / 2)    # 层底光强

aLLim = EXP(1) / (extc * dz) * (
    EXP(-aLPARBot / uOpt) - EXP(-uLPARSurf / uOpt)
)
```

其中：
- `extc`：总消光系数（水 + 颗粒物 + 自遮光）
- `uOpt`：最适光强（与功能群相关）
- **当 `meanpar=0` 或 `aLLim` 计算异常时，浮游植物不能生长**

**温度限制（高斯曲线）**：

```
uFunTm = EXP(-((T - cTmOpt) / cTmStd)^2)
```

- 硅藻：`cTmOpt=18`，`cTmStd` 较小（窄温性）
- 绿藻 / 蓝藻：`cTmOpt=25`，`cTmStd` 较大（广温性）

**营养盐限制（Liebig 最小律）**：

```
uLimN = sNH4W + sNO3W / (sNH4W + sNO3W + cKsN)
uLimP = sPO4W / (sPO4W + cKsP)
uLimSi = sSiO2W / (sSiO2W + cKsSi)   # 仅硅藻

aNLim = MIN(uLimN, uLimP, uLimSi)
```

**总生长速率**：

```
dDW/dt = cMuMax * aLLim * uFunTm * aNLim * sDW - cMort * sDW
```

**沉降过程**：
- `cVSet`：负值 = 下沉（硅藻、绿藻）
- 蓝藻 `cVSet=+0.03`：上浮（气浮调节）

#### 2.3.5 光照耦合（关键注意事项）

- `id_par`：瞬时 PAR，由 GETM 短波辐射计算
- `id_meanpar`：24h 平均 PAR，由 FABM 的 `temporal_mean` 计算
  - `period = 86400`（24 小时窗口）
  - `resolution = 3600`（1 小时分辨率）
- **`meanpar` 依赖 `itime` 推进时间窗口**，若 `itime` 未正确传递，时间窗口不滑动，`meanpar` 恒为初始值，导致 `aLLim` 异常

#### 2.3.6 模块耦合

- **消耗**：abiotic_water 营养盐（NH4/NO3/PO4/SiO2）
- **被消耗**：zooplankton 牧食
- **死亡产物**：进入 om_pool（POM）
- **反馈**：通过 `shade` 反馈影响 GETM 光衰减

---

### 2.4 zooplankton（浮游动物，2 群）

#### 2.4.1 模块职责

模拟浮游动物两个功能群的牧食、呼吸、排泄与死亡，是浮游植物 → 鱼类的能量桥梁。

#### 2.4.2 两个功能群

| 功能群 | 学名 | cMuMax (/d) | 食性 | 生态位 |
|--------|------|-------------|------|--------|
| **枝角类** | cladocerans | 0.5 | 滤食者 | 低速高效，牧食浮游植物与碎屑 |
| **桡足类** | copepods | 0.3 | 捕食者 | 高速低效，活跃捕食 |

#### 2.4.3 状态变量

每群 4 个：`sD, sN, sP, sC`（干重、氮、磷、碳）

#### 2.4.4 关键过程

**牧食（Holling II 型响应）**：

```
ingestion = cMuMax * (Food / (Food + cKsFood)) * sD
```

- 枝角类：`Food = 浮游植物 + POM`
- 桡足类：`Food = 枝角类 + POM`

**呼吸 / 排泄**：
- 一部分同化的碳用于呼吸（产生 CO2）
- 排泄的 N/P 返回 abiotic_water

**死亡**：
```
dD/dt|mort = -cMort * sD,  cMort = 0.05 /d
```

#### 2.4.5 模块耦合

- **牧食**：浮游植物（主要）、POM
- **被捕食**：幼鱼（JuFish）主要捕食枝角类
- **死亡产物**：进入 POM

---

### 2.5 macrophytes（沉水植物）

#### 2.5.1 模块职责

模拟沉水植物的生物量动态、营养盐吸收与对沉积物再悬浮的物理影响。

#### 2.5.2 状态变量

单位：g/m²（**面积基础**，与体积基础的浮游变量不同）

| 变量 | 含义 |
|------|------|
| `sD` | 干重 |
| `sN` | 氮含量 |
| `sP` | 磷含量 |
| `sC` | 碳含量 |

#### 2.5.3 关键过程

**光照限制**：
- 与浮游植物类似，但考虑冠层结构
- 水面光强衰减到植物顶部

**营养盐吸收**：
- 从水柱吸收 NH4/NO3/PO4
- 从沉积物间隙水吸收（根吸收）

**生物量扩散**：
- 14 天内可扩散到全湖（参数控制）
- **注意**：扩散过快可能导致全湖侵占，需调整扩散参数

**牧食**：
- 被草鱼 / 部分鱼类消耗
- **3DWET 当前无草鱼模块**，牧食压力低

#### 2.5.4 关键耦合

- **再悬浮影响**：`kVegResus = 0.05`，沉水植物显著降低沉积物再悬浮（仅 5% 的无植物区）
- **栖息地**：为幼鱼提供避难所

---

### 2.6 zoobenthos（底栖动物）

#### 2.6.1 模块职责

模拟底栖无脊椎动物生物量，是底栖食物网的关键节点。

#### 2.6.2 状态变量

单位：g/m²（面积基础），`sD, sN, sP, sC`

#### 2.6.3 关键过程

- **牧食**：消耗 POM（沉积物中的颗粒有机物）
- **生物扰动**：增强沉积物-水交换（影响 `cTurbDifNut`）
- **被捕食**：被成鱼（AdFish）捕食

#### 2.6.4 模块耦合

- **消耗**：om_pool 中的 POM
- **被捕食**：成鱼（底栖食性鱼类）
- **物理影响**：生物扰动增强营养盐扩散

---

### 2.7 fish（鱼类，3 功能群）

#### 2.7.1 模块职责

模拟鱼类三个功能群的生长、捕食、死亡，构成高级食物网顶层。

#### 2.7.2 三个功能群

| 功能群 | 简称 | cMuMax (/d) | 食性 | 主要食物 |
|--------|------|-------------|------|----------|
| **幼鱼** | JuFish | 0.1 | 杂食 | 浮游动物、POM |
| **成鱼** | AdFish | 0.05 | 底栖食性 | 底栖动物、POM |
| **凶猛鱼** | PiscFish | 0.03 | 捕食鱼类 | 幼鱼、其他鱼类 |

#### 2.7.3 状态变量

单位：g/m³（**体积基础**，与底栖动物的面积基础不同，转换需通过 `bot_pel_conv`）

`sD, sN, sP, sC`

#### 2.7.4 关键过程

**捕食（Holling III 型）**：

```
ingestion = cMuMax * (Food^2 / (Food^2 + cKsFood^2)) * sD
```

- 体现捕食者对高密度猎物的偏好
- `qStage` 控制食性转换（幼鱼→成鱼发育）

**呼吸 / 排泄**：
- 同化部分用于生长
- 排泄的 N/P 返回水柱

**死亡**：
- 自然死亡 `cMort`
- 捕捞死亡（可选）

#### 2.7.5 qStage 检查（关键）

```fortran
call check_state(qStage)
if (qStage > 0) then
    ! 访问特定阶段变量
end if
```

- `qStage` 控制鱼类发育阶段
- **必须使用 `check_state` 守卫**，否则未定义状态变量会导致段错误

#### 2.7.6 模块耦合

- 幼鱼 → 捕食浮游动物
- 成鱼 → 捕食底栖动物
- 凶猛鱼 → 捕食幼鱼 / 成鱼
- **单位转换**：通过 `bot_pel_interface` 的 `bot_pel_conv` 完成体积↔面积基础转换

---

### 2.8 om_pool（有机质池）

#### 2.8.1 模块职责

统一管理颗粒有机物（POM）和溶解有机物（DOM）的矿化与沉降。

#### 2.8.2 两类有机质

| 类型 | 状态变量 | 沉降行为 |
|------|----------|----------|
| **POM** | `sDW, sNW, sPW, sCW` | 下沉到沉积物 |
| **DOM** | `sDW, sNW, sPW, sCW` | 不下沉，随水流输运 |

#### 2.8.3 关键过程

**矿化**：

```
dDW/dt|minerl = -kMinerlPOM * uFunTm * sDW   # POM
dDW/dt|minerl = -kMinerlDOM * uFunTm * sDW   # DOM
```

- 矿化释放 NH4、PO4 到 abiotic_water
- 矿化耗氧（影响 O2）

**沉降（仅 POM）**：
- POM 沉降到沉积物层，进入 abiotic_sediment

**被消耗**：
- POM 被底栖动物、浮游动物牧食
- DOM 不被直接牧食

#### 2.8.4 模块耦合

- **接收**：浮游植物 / 动物 / 鱼类死亡产物
- **矿化输出**：营养盐 → abiotic_water
- **沉降输出**：POM → abiotic_sediment

---

### 2.9 sediment_exchange（沉积物-水交换）

#### 2.9.1 模块职责

计算水柱与沉积物之间的营养盐、有机物通量，是底栖-浮游耦合的核心。

#### 2.9.2 关键过程

**营养盐扩散**：

```
flux_NH4 = alpha * (sNH4S/bPorS/cDepthS - sNH4W) / dz
flux_NO3 = alpha * (sNO3S/... - sNO3W) / dz
flux_PO4 = alpha * (sPO4S/... - sPO4W) / dz
flux_SiO2 = alpha * (sSiO2S/... - sSiO2W) / dz
```

- `alpha = 9000`：扩散系数（含生物扰动）

**POM 沉降通量**：
- POM 从水柱沉降到沉积物表面

**再悬浮**：
- `qResus = 2`：基于剪切应力的再悬浮开关
- 剪切应力来自 GETM 底层流速

**生物扰动**：
- `cTurbDifNut = 12.0`：底栖动物活动增强扩散

#### 2.9.3 关键参数

| 参数 | 默认值 | 含义 |
|------|--------|------|
| `alpha` | 9000 | 扩散系数 |
| `cFetch` | 1000 | 风区长度（m） |
| `crt_shear` | 0.02 | 临界剪切应力（N/m²） |
| `kVegResus` | 0.05 | 沉水植物对再悬浮的抑制系数 |
| `cTurbDifNut` | 12.0 | 营养盐生物扰动扩散系数 |

---

### 2.10 其他模块

#### 2.10.1 burial（沉积物埋藏）

- 模拟沉积物长期埋藏过程
- 营养盐一旦埋藏即视为永久损失
- 用于长期（多年）营养盐质量平衡

#### 2.10.2 bot_pel_interface（底栖-浮游界面）

- 提供 `bot_pel_conv` 转换因子
- 完成面积基础（底栖）↔ 体积基础（浮游）单位转换
- **横向链接必须正确**，否则段错误

#### 2.10.3 bivalves（双壳类，可选）

- 可选模块，模拟双壳类滤食者
- 高效滤食浮游植物与 POM
- 适用于有大量底栖滤食动物的湖泊

---

## 三、输入数据要求

### 3.1 bathymetry.nc（湖底地形）

#### 3.1.1 格式规范

- **格式**：NetCDF4
- **维度**：`x(NX)`, `y(NY)`, `xq(NX+1)`, `yq(NY+1)`

#### 3.1.2 必需变量

| 变量名 | 维度 | 类型 | 含义 |
|--------|------|------|------|
| `bathymetry` | (NY, NX) | f32 | 水深（m），陆地 = -9999 |
| `x` | (NX) | f64 | x 坐标（m，UTM） |
| `y` | (NY) | f64 | y 坐标（m，UTM） |
| `latc` | (NY, NX) | f64 | 纬度（度） |
| `lonc` | (NY, NX) | f64 | 经度（度） |
| `grid_type` | 标量 | int | 网格类型（=1） |

#### 3.1.3 关键注意事项

1. **`latc` 必须用直接 UTM → lat/lon 转换**
   - 不要用 `polyfit` 拟合（曾导致 60× 误差，使气象强迫错位）
   - 推荐使用 `pyproj` 库的 `Transformer` 完成转换

2. **陆地标记**：陆地 `bathymetry = -9999`，水域为正水深

3. **水深范围建议**：
   - 1-10 m（3DWET 设计水深）
   - `crit_depth = 0.3`（浅水临界）
   - `min_depth = 0.1`（最小有效水深）

---

### 3.2 meteo.nc（气象强迫）

#### 3.2.1 格式规范

- **格式**：NetCDF4
- **维度**：`time(N_DAYS)`, `lat(NY)`, `lon(NX)`

#### 3.2.2 必需变量

| 变量名 | 单位 | 类型 | 含义 |
|--------|------|------|------|
| `t2` | °C | f32 | 2m 气温 |
| `u10` | m/s | f32 | 10m 东西向风速 |
| `v10` | m/s | f32 | 10m 南北向风速 |
| `slp` | Pa | f32 | 海平面气压 |
| `rh` | 0-1 | f32 | 相对湿度 |
| `tcc` | 0-1 | f32 | 总云量 |
| `precip` | m/s | **f64** | 降水率（**必须 float64**） |
| `evap` | m/s | **f64** | 蒸发率（负值 = 失水，**必须 float64**） |

#### 3.2.3 关键注意事项（重要）

1. **维度顺序必须为 `(time, lat, lon)`**
   - Fortran netCDF 4.5.4 会反转 C order
   - 这样反转后才是 `(lon, lat, time)` 供 GETM 读取
   - **顺序错误会导致气象场错位或读取失败**

2. **`precip` / `evap` 必须 `float64`**
   - `float32` 精度丢失导致降水 = 0
   - 表现为水位持续下降，水平衡失败

3. **`meteo_input.txt` 文件**
   - 内容为单行：`meteo.nc\n`
   - 指定气象文件名（GETM 读取）

---

### 3.3 rivers.nc（河流数据）

#### 3.3.1 格式规范

- **格式**：NetCDF4
- **维度**：`time(N_DAYS, 无限维)`

#### 3.3.2 变量定义（每条河 8 个变量）

对于名为 `{RIVER_NAME}` 的河流，包含：

| 变量名 | 单位 | 含义 |
|--------|------|------|
| `{RIVER_NAME}` | m³/s | 流量（入流正，出流负） |
| `{RIVER_NAME}_temp` | °C | 水温 |
| `{RIVER_NAME}_nh4` | gN/m³ | 氨氮浓度 |
| `{RIVER_NAME}_no3` | gN/m³ | 硝氮浓度 |
| `{RIVER_NAME}_po4` | gP/m³ | 溶解态磷浓度 |
| `{RIVER_NAME}_doc` | gC/m³ | 溶解有机碳浓度 |
| `{RIVER_NAME}_poc` | gC/m³ | 颗粒有机碳浓度 |

#### 3.3.3 riverinfo.dat（ASCII 配置）

```
N                                  # 第 1 行：河流数
i j name -1 -1                    # 第 2~N+1 行：每条河的网格位置
```

- `i`：列索引（x 方向，1-based）
- `j`：行索引（y 方向，1-based）
- `name`：河流名称（与 rivers.nc 变量名一致）
- `-1 -1`：固定占位符

#### 3.3.4 关键注意事项

1. **索引方向**：`i = 列`（x 方向），`j = 行`（y 方向），均为 1-based
2. **流量符号**：入流正值，出流负值
3. **严格水平衡**：`出流 = 入流 + 降水 - 蒸发`
4. **主要河流可占多个网格**（建议 3 个），避免极端流量溢出

---

### 3.4 fabm_init.nc（FABM 初始化场）

#### 3.4.1 格式规范

- **格式**：NetCDF4
- **维度**：`x(NX)`, `y(NY)`, `z(1)`

#### 3.4.2 变量内容

通常仅包含：

| 变量名 | 维度 | 单位 | 含义 |
|--------|------|------|------|
| `macrophytes_sD` | (1, NY, NX) | gDW/m² | 沉水植物初始分布 |

其他状态变量通过 `fabm.yaml` 的 `initialization` 字段均匀初始化。

#### 3.4.3 关键注意事项

- **沉水植物初始化条件**：仅在浅水区（`depth < 2.5 m`）初始化为 `30 gDW/m²`
- 其他变量（营养盐、浮游植物等）用 `fabm.yaml` 均匀初始化

---

### 3.5 配置文件

#### 3.5.1 getm.inp（GETM 主配置）

关键参数：

| 参数 | 推荐值 | 含义 |
|------|--------|------|
| `timestep` | 30.0 | 时间步长（秒，**必须 30s**） |
| `runtype` | 4 | 运行模式（3D） |
| `vert_cord` | 1 | 垂向坐标（sigma） |
| `kdum` | 10 | sigma 层数 |
| `maxdepth` | 8.0 | 最大水深 + 1m 余量 |
| `crit_depth` | 0.3 | 浅水临界深度 |
| `min_depth` | 0.1 | 最小有效水深 |
| `fwf_method` | 2 | 淡水通量方法（从文件读取） |
| `il, ih` | 1, NX | x 方向网格范围 |
| `jl, jh` | 1, NY | y 方向网格范围 |
| `calc_temp` | .true. | 计算温度 |
| `calc_salt` | .false. | 不计算盐度（淡水湖） |

#### 3.5.2 gotm_fabm.yaml（GOTM-FABM 激活配置）

```yaml
fabm:
  use: true
  freshwater_impact: true
  repair_state: true      # 修复负值，必须启用
  feedbacks:
    shade: true           # 生物自遮光，必须启用
    albedo: true
    surface_drag: true
  numerics:
    ode_method: 10        # Patankar 保正，必须 10（与 QWET 一致）
    split_factor: 1
    w_adv_discr: 6
    cnpar: 1.0
```

**关键说明**：
- `repair_state: true`：修复负状态变量，防止数值崩溃
- `shade: true`：浮游植物 / 颗粒物的自遮光反馈
- `ode_method: 10`：Patankar 保正积分法，**与 QWET 配置一致**
- `cnpar: 1.0`：完全隐式时间格式

#### 3.5.3 fabm.yaml（FABM 生态模型配置）

**结构**：`instances` → 每个模块 → `parameters` / `initialization` / `coupling`

**关键模块及初始条件建议**：

| 模块 | 变量 | 推荐初始值 | 说明 |
|------|------|-----------|------|
| `abiotic_water` | `sNH4W` | 0.3 | 富营养化基线 |
| `abiotic_water` | `sNO3W` | 1.0 | 富营养化基线 |
| `abiotic_water` | `sPO4W` | 0.06 | 富营养化基线 |
| `phytoplankton` | `sDW` | 0.2-0.3 | PCLake Turbid 默认 |
| `zooplankton` | `sD` | 0.3 | 避免饿死 |
| `fish` | `JuFish` | 0.15 | 降低 50% 减少压力 |
| `fish` | `AdFish` | 0.40 | 降低 50% 减少压力 |
| `fish` | `PiscFish` | 0.05 | 降低 50% 减少压力 |
| `macrophytes` | `sD` | (via fabm_init.nc) | 空间分布 |

**关键耦合设置**：

- `hypsograph: false`（`abiotic_sediment` 和 `bot_pel_interface`）
- `bot_pel_conv: bot_pel_interface/bot_pel_conv`（横向链接必须正确）

#### 3.5.4 gotmturb.nml（GOTM 湐流配置）

关键参数：

| 参数 | 推荐值 | 含义 |
|------|--------|------|
| `turb_method` | 2 | k-ε 模型 |
| `tke_method` | 1 | TKE 方程 |
| `len_scale_method` | 1 | 长度尺度方法 |
| `cm0_fix` | 0.5477 | 经验常数 |

**注意事项**：不要包含 `cpsix` / `cpsi4` / `cex` / `ce4` 等未定义变量。

#### 3.5.5 output.yaml（输出配置）

- `time_unit: day`
- `time_step: 1`（每日输出）

---

## 四、编译与运行

### 4.1 系统要求

| 组件 | 版本要求 | 用途 |
|------|----------|------|
| GCC / gfortran | 13+ | Fortran 编译器 |
| CMake | 3.10+ | 构建系统 |
| NetCDF-Fortran | 4.5+ | I/O 库 |
| Python | 3.8+ | 可视化与脚本 |
| WSL | （Windows 环境） | Windows 子系统 Linux |

### 4.2 编译流程

```bash
cd 3DWET
bash scripts/build_model.sh
```

编译脚本自动执行：

1. **备份源文件**（防止 patch 污染原始源码）
2. **应用 4 个 patch**：
   - `fish.F90`
   - `gotm_fabm.F90`
   - `fabm.F90`
   - `getm_fabm.F90`
3. **编译 FABM**（含 WET 模块）
4. **编译 GETM**（含 OpenMP 并行支持）
5. **恢复源文件**（保持源码树清洁）
6. **生成可执行文件**：`install/bin/getm_cartesian`

### 4.3 运行模型

```bash
cd case/Yilong  # 或其他 case 目录

# 设置多线程
export OMP_NUM_THREADS=8
export OMP_SCHEDULE=dynamic

# 运行（过滤 Patankar 警告）
../install/bin/getm_cartesian 2>&1 | grep -v 'small pi' > run.log
```

**运行说明**：
- `OMP_NUM_THREADS=8`：8 线程并行
- `OMP_SCHEDULE=dynamic`：动态调度，负载均衡
- `grep -v 'small pi'`：过滤 Patankar 方法的数值警告（产生大量噪音）

### 4.4 输出文件

| 文件 | 频率 | 变量数 | 说明 |
|------|------|--------|------|
| `{RUNID}.2d.nc` | 12 小时 | 17 | 2D 水力输出（水位、流速等） |
| `{RUNID}.3d.nc` | 12 小时 | 545 | 3D 水力输出（11 个 sigma 层） |
| `output.nc` | 日 | 530 | FABM 生化输出 |

### 4.5 numrecs 修复

GETM 因 meteo EOF 异常退出时，NetCDF3 文件 `numrecs = 0`，需手动修复：

```bash
python scripts/patch_numrecs.py {file.nc} {num_records}
```

**推荐 `num_records` 值**：

| 文件 | num_records | 说明 |
|------|-------------|------|
| 2D / 3D | 730 | 366 天 × 2 半日 |
| output.nc | 365 | 366 天（第 366 天可能损坏） |

---

## 五、建模建议

### 5.1 新湖泊建模步骤

#### 步骤 1：数据收集

- **湖底地形**：高分辨率水深数据（推荐 30m 以内分辨率原始数据）
- **气象数据**：日尺度（或更高频）气温、风速、辐射、降水、蒸发
- **河流数据**：主要入流 / 出流流量与水质（NH4、NO3、PO4、DOC、POC）
- **初始生态条件**：营养盐基线、浮游植物 / 动物 / 鱼类生物量

#### 步骤 2：网格设计

- **网格分辨率**：500 m（推荐）
- **网格规模**：`NX × NY` 根据湖泊形状确定
- **sigma 层数**：`kdum = 10`

#### 步骤 3：地形生成

- 参考 `gen_yilong_lake.py`
- **使用直接 UTM → lat/lon 转换**（禁用 `polyfit` 拟合）
- 陆地标记 `-9999`，水域正水深

#### 步骤 4：气象生成

- 参考 `gen_meteo.py`
- **`precip` / `evap` 必须 `float64`**
- 维度顺序 `(time, lat, lon)`

#### 步骤 5：河流设置

- 3-5 条主要河流
- **严格水平衡**：`出流 = 入流 + 降水 - 蒸发`
- 主要河流可占多个网格（建议 3 个）

#### 步骤 6：初始条件

| 类别 | 推荐值 | 单位 |
|------|--------|------|
| 浮游植物 | 0.2-0.3 | gDW/m³ |
| 浮游动物 | 0.3 | gDW/m³（避免级联崩溃） |
| 幼鱼 / 成鱼 / 凶猛鱼 | 0.15 / 0.40 / 0.05 | gDW/m³ |
| 营养盐 | 根据湖泊营养状态 | gN/m³ 或 gP/m³ |

#### 步骤 7：运行验证

1. **先 30 天测试**：检查数值稳定性
2. **再 366 天全年模拟**：覆盖季节循环

#### 步骤 8：结果分析

- 检查水位平衡（净变化应接近 0）
- 检查温度范围（与实测对比）
- 检查状态变量无 NaN
- 检查生态合理性（如季节性水华、鱼类动态）

---

### 5.2 参数标定建议

按以下顺序逐步标定，**不可一次性调整全部参数**：

1. **物理参数优先**：水温（影响所有生物过程的温度限制因子）
2. **营养盐参数其次**：河流输入浓度、初始浓度
3. **浮游植物参数**：`cMuMax`（生长率）、`cMort`（死亡率）
4. **高级食物网参数最后**：鱼类参数

---

### 5.3 常见问题排查

| 现象 | 可能原因 | 解决方案 |
|------|----------|----------|
| 水位持续下降 | `precip` 为 `float32`，精度丢失 | 重新生成 meteo.nc，`precip`/`evap` 用 `float64` |
| | `fwf_method` ≠ 2 | 修改 `getm.inp` 中 `fwf_method=2` |
| 浮游植物崩溃 | `aLLim = 0`（光照限制失效） | 检查 `meanpar` 是否非零，`itime` 是否正确传递 |
| 状态变量负值 | 未启用 Patankar 保正 | 设置 `repair_state=true`，`ode_method=10` |
| 段错误 | `bot_pel_conv` 横向链接缺失 | 检查 `fabm.yaml` 的 `coupling` 段 |
| | `fish` 未 `check_state` | 检查 `fish.F90` 的 `qStage` 守卫 |
| `run.log` 膨胀 | Patankar 警告刷屏 | `grep -v 'small pi'` 过滤 |
| 输出全 NaN | `numrecs = 0`（异常退出） | 用 `patch_numrecs.py` 修复 |
| 温度异常 | meteo.nc 维度顺序错误 | 确保维度为 `(time, lat, lon)` |

---

### 5.4 性能优化

1. **多线程**：
   - `OMP_NUM_THREADS=8`
   - `OMP_SCHEDULE=dynamic`

2. **网格规模与运行时间参考**：

| 网格规模 | 366 天运行时间 |
|----------|----------------|
| 28 × 8 | ~90 分钟 |
| 5 × 7 | ~22 分钟 |

3. **输出频率**：
   - 2D / 3D：每 12 小时
   - 生化：每日
   - 避免过频输出（I/O 瓶颈）

4. **日志过滤**：
   - 必过滤：`'small pi'`
   - 可选过滤：`'Error: state variable'`

---

## 六、模型限制

1. **无草鱼模块**
   - PCLake 原版有，但 3DWET 未移植
   - 移植工作量：3 个状态变量 + 16 个参数 + 52 个方程 + 19 个耦合点

2. **淡水湖专用**
   - `calc_salt = .false.`
   - 不适用于咸水湖 / 海岸带

3. **无 GUI**
   - 仅命令行运行
   - 配置依赖文本文件编辑

4. **无云服务**
   - 按要求本地运行
   - 不提供云部署支持

5. **NetCDF3 输出**
   - 异常退出需 `numrecs` 修复
   - 不支持 NetCDF4 高级特性（压缩、分块）

6. **沉水植物扩散过快**
   - 14 天可扩散到全湖
   - 需调整扩散参数限制

7. **鱼类单位混淆**
   - 体积基础（gDW/m³）vs 面积基础（gDW/m²）在 3D 中转换需注意
   - 通过 `bot_pel_conv` 完成

8. **Patankar 警告**
   - `ode_method=10` 产生大量 `'small pi'` 警告
   - 需 `grep` 过滤

---

## 七、验证与基准

### 7.1 理论湖泊基准

理论湖泊（Theoretical lake）case 用于数值稳定性与质量平衡验证：

| 指标 | 基准值 | 说明 |
|------|--------|------|
| 水位净变化 | 0.0000 m | 严格水平衡 |
| 温度范围 | [-0.03, 29.66] °C | 合理年循环 |
| WET 状态变量 | 104 个无 NaN | 数值稳定 |
| `aLLim` 范围 | [0, 0.999] | 光照限制合理 |

### 7.2 异龙湖案例

异龙湖（Yilong）case 位于云南，高温气候下蓝藻水华显著：

| 指标 | 结果 | 说明 |
|------|------|------|
| 浮游动物 | 0.24 → 0.25 | 稳定 |
| 幼鱼 | 0.15 → 0.16 | 稳定 |
| 绿藻 max | 0.23 | 稳定 |
| 蓝藻秋季峰值 | 6.84 | 云南高温水华 |
| 水位平衡 | 0.0000 m | 严格水平衡 |

---

## 附录：关键文件索引

| 文件 | 路径 | 作用 |
|------|------|------|
| GETM-FABM 接口 | `src/getm/src/3d/getm_fabm.F90` | 物理场传递 |
| GOTM-FABM 接口 | `src/gotm/src/fabm/gotm_fabm.F90` | 湐流耦合 |
| WET 注册入口 | `src/wet/src/wet_model_library.F90` | 模型注册 |
| 编译脚本 | `scripts/build_model.sh` | 一键编译 |
| numrecs 修复 | `scripts/patch_numrecs.py` | 输出修复 |
| 地形生成示例 | `scripts/gen_yilong_lake.py` | 参考 |
| 气象生成示例 | `scripts/gen_meteo.py` | 参考 |

---

*本技术报告基于 3DWET 源码与三个测试 case（骆马湖、理论湖、异龙湖）的实际运行经验编写，覆盖模型架构、模块细节、输入规范、运行流程与建模建议，可作为新湖泊建模的完整参考手册。*
