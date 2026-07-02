# PCLake 与 3DWET (WET/FABM) 模型对比报告

> 本报告对比 PCLake 原始模型（基于 Wageningen University 的 PCLake ACSL 源码导出）与 3DWET（基于 FABM 框架的 WET 模块，配合 GETM 实现 3D 耦合）在方程、参数和结构上的差异，为后续改进 3DWET 模型（尤其是草鱼模块移植）提供基础。
>
> 数据源：
> - PCLake：`_pclake_dump/` 目录下的 `states.tsv`（136 状态变量）、`parameters.tsv`（621 参数）、`equations_by_category.md`（按类别整理的 ACSL 方程）、`gras_only.md`（草鱼模块完整方程与耦合点）
> - WET/FABM：`3DWET/src/wet/src/` 目录下的 Fortran 源码（`fish_pclake.F90`、`fish.F90`、`phytoplankton.F90`、`zooplankton.F90`、`zoobenthos.F90`、`macrophytes.F90`、`om_pool.F90`、`abiotic_water.F90`、`abiotic_sediment.F90`）

---

## 1. 模型架构对比

### 1.1 整体架构差异

| 维度 | PCLake | 3DWET (WET/FABM + GETM) |
|------|--------|-------------------------|
| 空间维度 | 0 维（完全混合）或 1D 垂向分层（Epi/Hyp 两层，可选 Marsh） | 3D（水平网格 + 垂向 sigma 层） |
| 水动力驱动 | 内置简化水动力（水深、入流、出流、蒸发、降水） | 外部 GETM 提供 3D 流场、湍流、水位 |
| 生化模块耦合 | 单一 ACSL 模型，所有模块在同一 derivatives sheet 中通过方程直接引用 | FABM 框架，各模块为独立 Fortran type，通过 `register_state_dependency` + `request_coupling_to_model` 解耦 |
| 分层逻辑 | 通过 `_InclStrat_` 开关切换 Epi/Hyp 分层，通量在两层间手动分配 | GETM 提供任意层数 sigma 分层，FABM 通过 `get_vertical_movement` 控制垂直迁移 |
| 求解器 | ACSL 积分器（变步长） | GETM-FABM 联合求解（固定时间步，FABM 在每个 GETM 步内做生化更新） |
| 单位制 | 面积通量为主（g/m²/d），水柱浓度通过 `÷_uDepthWEpi_` 转换 | 体积通量为主（g/m³/s），底栖变量用 g/m² |
| 时间步 | 天（d） | 秒（s），通过 `scale_factor=1.0_rk/secs_pr_day` 转换 |

### 1.2 单位转换规则（关键）

PCLake 方程与 WET Fortran 代码之间的单位转换是移植的核心难点：

| 量纲 | PCLake | WET | 转换方式 |
|------|--------|-----|---------|
| 速率参数 k（1/d） | `1/d` | `1/s` | `scale_factor=1.0_rk/secs_pr_day`，`secs_pr_day=86400` |
| 面积通量（g/m²/d） | 直接用 | 需 `÷深度` 转体积浓度变化 | PCLake 的 `_tD...Gras_` 是面积通量，WET 中若是 `state`（体积）需除以深度 |
| 底栖状态变量 | g/m² | g/m²（`type_bottom_state_variable_id`） | 无需转换 |
| 水柱状态变量 | g/m³（PCLake 中 `_o...WEpi_`） | g/m³（`type_state_variable_id`） | 无需转换 |
| 清除率 cClear | m³/gDW/d | m³/gDW/s | `scale_factor=1.0_rk/secs_pr_day` |
| 沉降速度 cVSet | m/d | m/s | `scale_factor=1.0_rk/secs_pr_day` |

**关键陷阱**：PCLake 的草鱼方程全部以面积通量（g/m²/d）表达，而 WET 标准鱼类模块（`fish.F90`）用体积浓度（g/m³）。移植时若草鱼作为 `bottom_state`（推荐），面积通量可保留；若作为 `state`（体积），则需在 do 函数中除以 `standard_variables%depth`。

### 1.3 命名映射规则

| 位置 | PCLake 命名 | WET 命名 | 说明 |
|------|------------|---------|------|
| 状态变量 | `_sDGras_`（前后下划线） | `sDGras`（无下划线） | 去掉首尾下划线 |
| 参数 | `_cPDGras_` | `cPDGras` | 同上 |
| 通量 | `_tDAssGras_` | `tDAssGras` | 同上 |
| 鱼类状态（PCLake vs WET legacy） | `_sDFiJv_` / `_sDFiAd_` | `FiJu_D` / `FiAd_D` | 元素后缀位置不同（PCLake 前缀 D，WET 后缀 _D） |
| 鱼类状态（WET 标准 fish.F90） | — | `sD` / `sP` / `sN` / `sC` | 通用 4 元素状态，通过实例化多个 fish 对象实现多物种 |

### 1.4 ACSL → Fortran 语法映射

| ACSL 语法 | Fortran 等价 | 说明 |
|-----------|-------------|------|
| `_IF_ x _GT_ y _THEN_ a _ELSE_ b _ENDIF_` | `merge(a, b, x > y)` 或 `if/else` | WET 多用 `merge` |
| `_MAX_(a, b)` | `max(a, b)` | 直接对应 |
| `_MIN_(a, b)` | `min(a, b)` | 直接对应 |
| `_EXP_(x)` | `exp(x)` | 直接对应 |
| `_POW_(x, n)` | `x**n` | 直接对应 |
| `_COS_(x)` | `cos(x)` | 直接对应 |
| `_IF_ (_InclX_ _EQ_ _TRUE_)` | `if (self%lInclX)` | 逻辑开关 |
| `_NearZero_` | `NearZero = 1.0e-30_rk` | 防除零小量 |

---

## 2. 状态变量对比

### 2.1 总体规模

| 模型 | 状态变量总数 | 说明 |
|------|------------|------|
| PCLake | 136（含开关、forcing、state、derivative） | `states.tsv` 完整列表 |
| WET | 约 40-50（按模块累加，不含 GETM 物理） | 各 `.F90` 模块 `register_state_variable` 累计 |

### 2.2 各模块状态变量对照

#### 浮游植物（Phytoplankton）

| PCLake 状态 | 单位 | WET 状态（phytoplankton.F90） | 单位 | 差异 |
|------------|------|------------------------------|------|------|
| `_oDDiatWEpi_/_oDDiatWHyp_` | gDW/m³ | `sDW`（实例 Diat） | gDW/m³ | WET 用多实例替代 Epi/Hyp 分层 |
| `_oPDiatWEpi_/_oPDiatWHyp_` | gP/m³ | `sPW` | gP/m³ | — |
| `_oNDiatWEpi_/_oNDiatWHyp_` | gN/m³ | `sNW` | gN/m³ | — |
| `_oCDiatWEpi_` | gC/m³ | `sCW` | gC/m³ | WET 显式追踪 C，PCLake 通过 `cCPerDW` 隐式 |
| `_oDDiatS_` | gDW/m² | `sDS`（bottom_state） | gDW/m² | 沉积物相 |
| — | — | `sDW_PV`/`sDS_PV` | — | WET 特有的"虚拟种群"（pseudo-variable）用于多群体竞争 |

**PCLake 浮游植物**：3 类（Diat 硅藻、Gren 绿藻、Blue 蓝藻），每类有 Epi/Hyp 两层、水柱/沉积物两相，共 3×2×2×4(D/P/N/C)=48 个状态变量（实际 fewer，因沉积物相不全）。

**WET 浮游植物**：通过 `phytoplankton.F90` 多实例化实现 3 类（Diat/Gren/Blue），每实例 8 个状态（sDW/sPW/sNW/sCW + sDS/sPS/sNS/sCS + _PV 镜像）。

#### 浮游动物（Zooplankton）

| PCLake 状态 | 单位 | WET 状态（zooplankton.F90） | 单位 | 差异 |
|------------|------|----------------------------|------|------|
| `_oDZooEpi_/_oDZooHyp_` | gDW/m³ | `sDZoo` | gDW/m³ | WET 单实例，无 Epi/Hyp 区分 |
| `_oPZooEpi_` | gP/m³ | `sPZoo` | gP/m³ | — |
| `_oNZooEpi_` | gN/m³ | `sNZoo` | gN/m³ | — |
| — | — | `sCZoo` | gC/m³ | WET 显式 C |

**PCLake 浮游动物**：1 类（Zoo），Epi/Hyp 两层。
**WET 浮游动物**：1 类，无分层，通过 GETM 物理 3D 网格自然分布。

#### 底栖动物（Zoobenthos）

| PCLake 状态 | 单位 | WET 状态（zoobenthos.F90） | 单位 | 差异 |
|------------|------|----------------------------|------|------|
| `_oDBent_` | gDW/m² | `sDBent`（bottom_state） | gDW/m² | 一致 |
| `_oPBent_` | gP/m² | `sPBent` | gP/m² | — |
| `_oNBent_` | gN/m² | `sNBent` | gN/m² | — |
| — | — | `sCBent` | gC/m² | WET 显式 C |
| — | — | `_PV` 镜像 | — | WET 特有 |

#### 大型植物（Macrophytes）

| PCLake 状态 | 单位 | WET 状态（macrophytes.F90） | 单位 | 差异 |
|------------|------|----------------------------|------|------|
| `_oDVegEpi_/_oDVegHyp_` | gDW/m² | `sDVeg`（bottom_state） | gDW/m² | PCLake 分 Epi/Hyp，WET 单一底栖 |
| `_oPVeg_` | gP/m² | `sPVeg` | gP/m² | — |
| `_oNVeg_` | gN/m² | `sNVeg` | gN/m² | — |
| — | — | `sCVeg` | gC/m² | WET 显式 C |
| — | — | `nCompts` | — | WET 支持竞争对手多实例 |

#### 鱼类（Fish）—— 关键差异区

| PCLake 状态 | 单位 | WET fish_pclake.F90（legacy） | WET fish.F90（标准） | 差异 |
|------------|------|------------------------------|---------------------|------|
| `_sDFiJv_`/`_sDFiAd_` | gDW/m² | `sDFi`/`sPFi`/`sNFi`/`sVFi` | `sD`/`sP`/`sN`/`sC` | PCLake 分幼/成，WET 通过实例化 |
| `_sDPisc_` | gDW/m² | — | `sD`/`sP`/`sN`/`sC`（PiscFish 实例） | — |
| `_sDGras_`（草鱼） | gDW/m² | **完全缺失** | **完全缺失** | **3DWET 无草鱼模块** |
| `_sPGras_` | gP/m² | 缺失 | 缺失 | — |
| `_sNGras_` | gN/m² | 缺失 | 缺失 | — |
| — | — | — | `fVul`（易捕食比例） | WET 标准版特有，foraging arena 概念 |
| — | — | — | `sFRes`（储备生物量） | WET 标准版特有，qStage>0 时启用 |
| — | — | — | `sDSiz`（个体大小） | WET 标准版特有 |

**关键结论**：
1. PCLake 鱼类分 4 组（FiJv 幼鱼、FiAd 成鱼、Pisc 凶猛鱼、Gras 草鱼），草鱼为专食植被的底栖鱼类。
2. WET `fish_pclake.F90`（legacy）只实现了单组通用鱼类（4 元素 D/P/N/V），无草鱼。
3. WET `fish.F90`（标准版）引入 foraging arena 理论（fVul、sFRes、sDSiz），更复杂但无草鱼专食植被机制。
4. **草鱼是 PCLake 的特色模块，在 3DWET 中完全缺失，需移植。**

#### 有机物（Organic Matter）

| PCLake 状态 | 单位 | WET 状态（om_pool.F90） | 单位 | 差异 |
|------------|------|------------------------|------|------|
| `_oDDetWEpi_/_oDDetWHyp_` | gDW/m³ | `sDW` | gDW/m³ | — |
| `_oDDetS_` | gDW/m² | `sDS`（bottom_state） | gDW/m² | — |
| `_oNHumS_/_oNDetS_` | gN/m² | `sNS` | gN/m² | PCLake 区分 Hum/Det，WET 统一 |
| — | — | `sCW`/`sCS` | gC/m³、gC/m² | WET 显式 C |
| — | — | `_PV` 镜像 + Refr 池 | — | WET 有难降解池 `DRefrS` 等 |

#### 无机环境（Abiotic）

| PCLake 状态 | WET 状态 | 差异 |
|------------|---------|------|
| `_oPO4WEpi_/_oPO4WHyp_` | `sPO4W`（abiotic_water） | WET 单一水柱，不分 Epi/Hyp |
| `_oNH4WEpi_` | `sNH4W` | — |
| `_oNO3WEpi_` | `sNO3W` | — |
| `_oSiO2WEpi_` | `sSiO2W` | — |
| `_oO2WEpi_` | `sO2W` | — |
| `_oDIMWEpi_` | `sDIMW` | — |
| `_oPAIMWEpi_` | `sPAIMW` | — |
| `_oPO4S_` | `sPO4S`（abiotic_sediment，bottom） | — |
| `_oNH4S_` | `sNH4S` | — |
| `_oNO3S_` | `sNO3S` | — |
| `_oSiO2S_` | `sSiO2S` | — |

WET `abiotic_water.F90` 有 8 个状态变量（sDIMW, sSiPaW, sPO4W, sPAIMW, sNH4W, sNO3W, sSiO2W, sO2W），`abiotic_sediment.F90` 有 7 个（sDIMS, sSiPaS, sSiO2S, sPO4S, sPAIMS, sNH4S, sNO3S）。

### 2.3 状态变量缺失汇总

| 缺失项 | PCLake 有 | WET 缺 | 影响 |
|--------|----------|--------|------|
| 草鱼 DW/P/N | `_sDGras_/_sPGras_/_sNGras_` | 无 | 无法模拟草鱼控草 |
| 鱼类分层（Epi/Hyp 分配系数 `uFiJvMortHyp` 等） | 有 | 由 GETM 3D 网格替代 | 不需移植 |
| Marsh 沼泽状态 | `_InclMarsh_` | 无 | 当前湖泊场景不启用，可忽略 |
| 蓝藻表面水华 `_aDBlueSurf_` | 有 | 无 | 富营养化场景缺失 |

---

## 3. 参数对比

### 3.1 参数规模

| 模型 | 参数总数 | 来源 |
|------|---------|------|
| PCLake | 621 | `parameters.tsv` |
| WET | 约 100-150 | 各模块 `get_parameter` 调用累计 |

### 3.2 草鱼模块参数（19 个，WET 全部缺失）

下表为 PCLake 中草鱼相关的 19 个参数（lId 601-619），**3DWET 中完全缺失**，是移植的核心：

| PCLake 参数 | 单位 | 默认值 | 含义 | WET 对应 |
|------------|------|--------|------|---------|
| `_cPDGras_` | gP/gDW | 0.022 | 草鱼 P/D 比 | 无（可参考 `cPDRef=0.022`） |
| `_cNDGras_` | gN/gDW | 0.10 | 草鱼 N/D 比 | 无（可参考 `cNDRef=0.10`） |
| `_cDGrasIn_` | gDW/m² | 0 | 外部迁入草鱼密度 | 无（参考 `cDFiIn=0.005`） |
| `_cDCarrGras_` | gDW/m² | 15 | 草鱼承载容量 | 无（参考 `cDCarrFish=15`） |
| `_kMigrGras_` | 1/d | 0 | 草鱼迁移率 | 无（参考 `kMigrFish=0.001`） |
| `_hDVegGras_` | gDW/m² | 200 | 植被半饱和常数（草鱼摄食） | 无 |
| `_kDAssGras_` | 1/d | 0.12 | 草鱼同化系数 | 无（参考 `kDAssFi=0.12`） |
| `_fDAssGras_` | - | 0.44 | 草鱼同化效率 | 无（参考 `fDAssFi=0.4`） |
| `_kDRespGras_` | 1/d | 0.005 | 草鱼呼吸系数 | 无（参考 `kDRespFi=0.01`） |
| `_fDissEgesGras_` | - | 0.06 | 草鱼排泄物溶解比例 | 无（参考 `fDissEgesFish=0.25`） |
| `_fDissMortGras_` | - | 0.10 | 草鱼死亡溶解比例 | 无（参考 `fDissMortFish=0.1`） |
| `_kMortGras_` | 1/d | 0.00027 | 草鱼死亡率 | 无（参考 `kMortFi=0.001`） |
| `_kHarvGrasWin_` | 1/d | 0 | 草鱼冬季捕捞率 | 无 |
| `_kHarvGrasSum_` | 1/d | 0 | 草鱼夏季捕捞率 | 无 |
| `_cTmOptGras_` | °C | 30 | 草鱼最适温度 | 无（参考 `cTmOptFish=25`） |
| `_cSigTmGras_` | °C | 15 | 草鱼温度 σ | 无（参考 `cSigTmFish=10`） |
| `_fGrasMortHyp_` | - | 0.9 | 草鱼下层死亡分配比 | 无（3D 不需要，可忽略） |
| `_fGrasEgesHyp_` | - | 0.5 | 草鱼下层排泄分配比 | 无（3D 不需要） |
| `_fGrasExcrHyp_` | - | 0.5 | 草鱼下层排泄分配比 | 无（3D 不需要） |

**关键差异**：
- 草鱼最适温度 30°C 显著高于普通鱼 25°C，反映草鱼暖水性。
- 草鱼温度 σ=15 大于普通鱼 σ=10，温度耐受范围更宽。
- 草鱼同化效率 0.44 高于普通鱼 0.40（植被易消化）。
- 草鱼呼吸系数 0.005 低于普通鱼 0.01（低代谢）。
- `_hDVegGras_=200` 是草鱼专属参数（植被半饱和），WET 无对应。
- `_kHarvGrasWin_/_kHarvGrasSum_` 季节捕捞切换是草鱼专属。

### 3.3 鱼类通用参数对比（PCLake vs WET fish_pclake.F90）

| 功能 | PCLake 参数 | 默认值 | WET 参数 | 默认值 | 差异 |
|------|------------|--------|---------|--------|------|
| 迁移率 | `_kMigrFish_` | 0 | `kMigrFish` | 0.001 | WET 默认非零 |
| 外部密度 | `_cDFiIn_` | 0 | `cDFiIn` | 0.005 | WET 默认非零 |
| 承载容量 | `_cDCarrFish_` | 15 | `cDCarrFish` | 15.0 | 一致 |
| 同化系数 | `_kDAssFi_` | 0.12 | `kDAssFi` | 0.12 | 一致 |
| 同化效率 | `_fDAssFi_` | 0.40 | `fDAssFi` | 0.40 | 一致 |
| 呼吸系数 | `_kDRespFi_` | 0.01 | `kDRespFi` | 0.01 | 一致 |
| 死亡率 | `_kMortFi_` | 0.001 | `kMortFi` | 0.001 | 一致 |
| 最适温度 | `_cTmOptFish_` | 25 | `cTmOptFish` | 25 | 一致 |
| 温度 σ | `_cSigTmFish_` | 10 | `cSigTmFish` | 10 | 一致 |
| P/D 参考比 | `_cPDFishRef_` | 0.022 | `cPDFishRef` | 0.022 | 一致 |
| N/D 参考比 | `_cNDFishRef_` | 0.10 | `cNDFishRef` | 0.10 | 一致 |
| 骨骼 C 比 | `_fDBone_` | 0.35 | `fDBone` | 0.35 | 一致 |
| 骨骼 P 比 | `_fPBone_` | 0.50 | `fPBone` | 0.50 | 一致 |
| 排泄溶解比 | `_fDissEgesFish_` | 0.25 | `fDissEgesFish` | 0.25 | 一致 |
| 死亡溶解比 | `_fDissMortFish_` | 0.10 | `fDissMortFish` | 0.10 | 一致 |

**结论**：WET `fish_pclake.F90` 完整继承了 PCLake 鱼类参数集，数值一致。

### 3.4 WET 标准版 fish.F90 的额外参数（PCLake 无）

`fish.F90`（标准版）引入了 foraging arena 理论的额外参数，PCLake 中无对应：

| 参数 | 默认值 | 含义 | PCLake 对应 |
|------|--------|------|------------|
| `qTrans` | 2 | 垂直迁移方法（0=无/1=被动/2=O2/3=O2&光） | 无（PCLake 用 `uFiJvMortHyp` 手动分层） |
| `cMinO2` | 2.0 | O2 限制阈值 | 无 |
| `cMinLight`/`cMaxLight` | 1.0/40.0 | 光驱动迁移阈值 | 无 |
| `cVswim` | 10.0 | 垂直迁移速度 | 无 |
| `cDFiMin` | 0.0001 | 最小 DW 密度 | 无 |
| `qStage` | 0 | 阶段耦合（繁殖/成熟） | 无（PCLake 用独立 FiJv/FiAd 状态） |
| `fResMax`/`fResMin` | 0.5/0.16 | 储备生物量上下限 | 无 |
| `cMortStarv` | 0.2 | 饥饿死亡常数 | 无 |
| `cDinit`/`cDfin` | 0.0 | 阶段初始/最终个体重 | 无 |
| `cDayReprFish` | 120 | 繁殖日 | 无 |
| `fReproFish`/`fGonad`/`cDegg` | 0.01/0.0/0.0 | 繁殖参数 | 无 |
| `qODB`/`qOPT` | 1/0 | 最优觅食开关 | 无 |
| `lAggr`/`cAggr` | false/0.0 | 种内攻击性 | 无 |
| `fFC`/`fPV` | 1.0 | 避难所摄食效率/被捕食脆弱性 | 无 |
| `kTurbFish` | 1.0 | 鱼类扰动再悬浮 | 无 |
| `cRelVegBent`/`cRelVegPlan` | 0.009/0.0 | 植被对摄食的抑制 | 无 |
| `lVegOpt`/`hDVegGrowth` | false/0.015 | 植被促生长开关 | 无 |
| `lNutMeth` | false | 固定化学计量开关 | 无 |
| `cCDRef` | 0.45 | C/D 参考比 | PCLake 用 `_cCPerDW_=0.4` |

**结论**：WET 标准版 `fish.F90` 比 PCLake 鱼类模块复杂得多，引入了个体生态学（储备、个体大小、繁殖、foraging arena）。但**仍无草鱼专食植被机制**，因此草鱼移植必须新建模块或大幅扩展 fish.F90。

### 3.5 其他模块参数对比摘要

| 模块 | PCLake 关键参数 | WET 对应 | 一致性 |
|------|---------------|---------|--------|
| 浮游植物 | `cMuMax=1.4`, `kDResp=0.03`, `kMortW=0.01`, `cTmOpt=25`, `cSigTm=11.6` | `cMuMax=1.4`, `kDResp=0.03`, `kMortW=0.01`, `cTmOpt=25`, `cSigTm=11.6` | 一致 |
| 浮游动物 | `cDCarrZoo=25`, `kDRespZoo=0.2`, `kMortZoo=0.04`, `kDConsMaxZoo=0.5`, `fDAssZoo=0.35`, `cTmOptZoo=22`, `cSigTmZoo=13` | 同 | 一致 |
| 底栖动物 | `cDCarrBent=10`, `kDConsMaxBent=0.33`, `kDRespBent=0.005`, `kMortBent=0.005`, `kMortO2=0.05`, `cTmOptBent=25`, `cSigTmBent=16` | 同 | 一致 |
| 大型植物 | `cMuMaxVeg=0.08`, `kDRespVeg=0.02`, `kMortVegSum=0.005`, `cDCarrVeg=300`, `cTmOptVeg=20`, `cSigTmVeg=20` | 同 | 一致 |
| 有机物 | `kDMinW=0.001`, `kNMinW=0.01`, `kPMinW=0.01`, `cThetaMinW=1.02`, `cVSet=-0.3`, `hO2BOD=1.0` | 同 | 一致 |

**结论**：除草鱼外，PCLake 与 WET 的参数集高度一致，WET 是 PCLake 的忠实移植。

---

## 4. 核心方程逐模块对比

### 4.1 温度函数（所有生物模块通用）

**PCLake（草鱼）**：
```
_uFunTmGras_ = _EXP_(-0.5 /(_cSigTmGras_*_cSigTmGras_) *
                    ((_uTmEpi_ - _cTmOptGras_)*(_uTmEpi_ - _cTmOptGras_)
                   - (_cTmRef_ - _cTmOptGras_)*(_cTmRef_ - _cTmOptGras_)))
```

**WET（fish_pclake.F90）**：
```fortran
uFunTmFish = uFunTmGaus(uTm, cSigTmFish, cTmOptFish)
! 其中 uFunTmGaus 定义在 wet_utility 中，等价于：
! uFunTmFish = exp(-0.5_rk*(uTm - cTmOptFish)**2 / cSigTmFish**2) /
!              exp(-0.5_rk*(cTmRef - cTmOptFish)**2 / cSigTmFish**2)
```

**差异分析**：
- 数学形式等价，都是 Gaussian 温度响应，归一化到参考温度 `cTmRef=20°C`。
- PCLake 用 `_uTmEpi_`（表层温度），草鱼作为底栖鱼应改用底层温度。
- WET 用 `uTm`（FABM 提供的局部温度，3D 网格内每层不同），更精确。
- **移植要点**：草鱼温度函数直接复用 WET 的 `uFunTmGaus`，参数改为 `cTmOptGras=30`、`cSigTmGras=15`。

### 4.2 浮游植物方程对比

#### 4.2.1 生长率

**PCLake（硅藻）**：
```
_aMuDiat_ = _cMuMaxDiat_ * _aPLimDiat_ * _aLLimDiat_ * _aNLimDiat_ * _uFunTmDiat_
```

**WET（phytoplankton.F90）**：
```fortran
aMu = aNutLim * aMuTmL * aNFixLim
! 其中 aNutLim = min(aPLim, aNLim)
! aMuTmL = aLLim * uFunTm
```

**差异**：
- PCLake 用 `_aPLim_*_aNLim_`（乘积），WET 用 `min(aPLim, aNLim)`（Liebig 最小律）。
- WET 额外有 `aNFixLim`（固氮限制，蓝藻专用）。
- 数学形式不同但生态意义相近。

#### 4.2.2 光限制

**PCLake（Steele 形式）**：
```
_aLLimDiat_ = (_I_/(_Iopt_*_cLDayAve_*_fPAR_)) * _EXP_(1 - _I_/(_Iopt_*_cLDayAve_*_fPAR_))
```

**WET（Steele 或 Monod 可选）**：
```fortran
! Steele 形式
aLLim = (par / Iopt) * exp(1.0_rk - par / Iopt)
! Monod 形式（可选）
aLLim = par / (par + hL)
```

**差异**：基本一致，WET 提供选项。

### 4.3 浮游动物方程对比

#### 4.3.1 摄食

**PCLake**：
```
_wDConsZooEpi_ = _sDZooEpi_ * _cClearZoo_ * _sDPhytEpi_ * (1 - _aFeedLvlZooEpi_)
_aFeedLvlZooEpi_ = (_cClearZoo_*_sDPhytEpi_) / (_cClearZoo_*_sDPhytEpi_ + _kDConsMaxZoo_*_uFunTmZoo_)
```

**WET（zooplankton.F90）**：
```fortran
aFeedLvlZoo = sum(cClearPrey * fGutOccPrey * sDPrey) /
               (sum(cClearPrey * fGutOccPrey * sDPrey) + uFunTmZoo * kDConsMaxZoo)
wDConsZoo = sDZoo * cClearPrey * sDPrey * (1.0_rk - aFeedLvlZoo)
```

**差异**：
- PCLake 单食饵（Phyt），WET 多食饵（sum over prey）。
- WET 引入 `fGutOccPrey`（肠占因子），PCLake 隐式为 1。
- 形式一致（饱和摄食）。

### 4.4 鱼类方程对比

#### 4.4.1 环境校正（承载容量）

**PCLake（草鱼）**：
```
_akDIncrGras_ = (_kDAssGras_ - _kDRespGras_) * _uFunTmGras_ - _kMortGras_
_tDEnvGras_ = _MAX_(0.0, _akDIncrGras_ / _cDCarrGras_ * _aDGras_*_aDGras_)
```

**WET fish_pclake.F90**：
```fortran
tDEnvFi = max(0.0_rk, (ukDIncrFi / (cDCarrFish - sDFiOS)) * sDFi * sDFi)
ukDIncrFi = (kDAssFi * aFunVegAss * uFunTmFish - kDRespFi) - kMortFi
```

**差异**：
- 形式一致（Logistic 型环境压制）。
- PCLake 分母为 `_cDCarrGras_`，WET 为 `(cDCarrFish - sDFiOS)`（减去当前密度，更严格）。
- WET 多了 `aFunVegAss`（植被对同化的影响因子），草鱼移植时此因子应恒为 1（草鱼不被植被抑制）。

#### 4.4.2 同化

**PCLake（草鱼）**：
```
_tDAssGras_ = _aDSatGras_ * (_kDAssGras_ * _uFunTmGras_ * _aDGras_ - _tDEnvGras_)
_aDSatGras_ = _aDVeg_*_aDVeg_ / (_hDVegGras_*_hDVegGras_ + _aDVeg_*_aDVeg_)
```

**WET fish_pclake.F90**：
```fortran
tDAssFiZoo = aDSatFiZoo * (kDAssFi * aFunVegAss * uFunTmFish * sDFi - tDEnvFi) * fFishZoo
aDSatFiZoo = sDZoo**2 / (hDZooFi**2 + sDZoo**2)
```

**差异**：
- 形式一致（Holling type III 饱和）。
- 草鱼食饵为植被 `_aDVeg_`，半饱和 `_hDVegGras_=200`。
- WET 通用鱼食饵为 Zoo/Bent，通过 `fFishZoo`/`fFishBent` 分配。

#### 4.4.3 摄食

**PCLake（草鱼）**：
```
_tDConsGras_ = _tDAssGras_ / _fDAssGras_
```

**WET**：
```fortran
tDConsFi = tDAssFi / fDAssFi
```

**一致**。

#### 4.4.4 死亡与骨骼沉出

**PCLake（草鱼）**：
```
_tDMortGras_ = _kMortGras_ * _aDGras_ + (1.0 - _aDSatGras_) * _tDEnvGras_
_tDMortGrasBot_ = _fDBone_ * _tDMortGras_
_tDMortGrasDet_ = _tDMortGras_ - _tDMortGrasBot_
```

**WET fish_pclake.F90**：
```fortran
tDMortFi = kMortFi * sDFi + (1.0_rk - aDSatFi) * tDEnvFi
tDMortFiBot = fDBone * tDMortFi
tDMortFiDet = tDMortFi - tDMortFiBot
```

**一致**：骨骼沉出比例 `fDBone=0.35`，其余进入碎屑。

#### 4.4.5 捕捞（草鱼专属）

**PCLake（草鱼）**：
```
_ukHarvGras_ = _IF_ (_COS_(2.0*_Pi_*_sTime_/_DaysPerYear_) _GT_ 0.1) _THEN_ _kHarvGrasWin_ _ELSE_ _kHarvGrasSum_ _ENDIF_
_tDHarvGras_ = _ukHarvGras_ * _aDGras_
```

**WET**：无对应（fish.F90 和 fish_pclake.F90 均无捕捞方程）。

**移植要点**：需新增季节切换捕捞方程，用 COS 函数判断冬夏。

#### 4.4.6 营养盐限制校正（草鱼专属）

**PCLake（草鱼）**：
```
_tDConsGrasNut_ = (_tDAssGras_/_fDAssGras_) * _MAX_(1.0,
                    _cNDGras_/_rNDFoodGras_*_fDAssGras_,
                    _cPDGras_/_rPDFoodGras_*_fDAssGras_)
```

**WET**：无对应（fish.F90 用 `lNutMeth` 开关固定化学计量，不校正摄食）。

**移植要点**：草鱼因植被低 P 含量需营养盐校正，必须移植此方程。

### 4.5 大型植物方程对比

**PCLake**：
```
_tDProdVegEpi_ = _aMuVegEpi_ * _aDVegEpi_
_aMuVegEpi_ = _cMuMaxVeg_ * _aLLimVeg_ * _uFunTmVeg_ * (1 - _aDVegEpi_/_cDCarrVeg_)
_tDMortVegEpi_ = _kMortVegEpi_ * _aDVegEpi_
```

**WET（macrophytes.F90）**：
```fortran
tDProdVeg = aMuVeg * sDVeg
aMuVeg = cMuMaxVeg * aLLimVeg * uFunTmVeg * (1.0_rk - sDVeg / cDCarrVeg)
tDMortVeg = kMortVeg * sDVeg
```

**一致**：Logistic 生长 + 线性死亡。

### 4.6 底栖动物方程对比

**PCLake/WET**：形式一致，Clearance rate 模型，差异仅在 PCLake 分 Epi/Hyp，WET 用 3D 网格。

### 4.7 有机物分解方程对比

**PCLake**：
```
_wDMinDetW_ = _kDMinDetW_ * _uFunTmMinW_ * _oDDetW_ * _uFunO2_
```

**WET（om_pool.F90）**：
```fortran
wDMin = kDMinW * uFunTmArrh(uTm, cThetaMinW) * sDW * (sO2W / (hO2BOD + sO2W))
```

**差异**：
- PCLake 用 Gaussian 温度函数，WET 用 Arrhenius（`cThetaMinW=1.02`）。
- O2 限制形式一致（Monod）。

---

## 5. 草鱼模块移植分析（重点）

### 5.1 移植必要性

草鱼（Grass Carp, Ctenopharyngodon idella）是 PCLake 的特色模块，用于模拟**生物操控**（biomanipulation）——通过草鱼摄食沉水植物控制植被过度生长。3DWET 当前完全缺失此模块，导致：
1. 无法模拟草鱼控草场景（骆马湖曾投放草鱼）。
2. 沉水植物在 14 天内从湖滨带扩散到全湖（实测现象），缺乏草鱼摄食压制。
3. 食物网缺少"植被→草鱼"通路，能量流不完整。

### 5.2 移植规模

| 项目 | 数量 | 来源 |
|------|------|------|
| 状态变量 | 3 个（sDGras/sPGras/sNGras，可选 sCGras） | `states.tsv` lId 134 |
| 参数 | 19 个（lId 601-619） | `parameters.tsv` |
| Gras 定义方程 | 52 条 | `gras_only.md` A 部分 |
| 耦合点方程 | 19 条 | `gras_only.md` B 部分 |
| 总计 | 91 条方程 + 19 参数 + 3 状态 | — |

### 5.3 状态变量设计建议

草鱼作为**底栖鱼类**，活动于湖底植被区，建议用 `type_bottom_state_variable_id`：

```fortran
! 建议在新建 grass_carp.F90 中声明
type (type_bottom_state_variable_id) :: id_sDGras, id_sPGras, id_sNGras
! 可选：id_sCGras（若需追踪 C）
```

**理由**：
1. PCLake 中草鱼单位为 gDW/m²（面积通量），与 `bottom_state` 一致。
2. 草鱼食饵 `_aDVeg_`（大型植物）在 WET 中也是 `bottom_state`，单位匹配。
3. 避免体积/面积单位转换的复杂性。

### 5.4 19 个参数完整清单与移植映射

| # | PCLake 参数 | WET 移植名 | 单位 | 默认值 | get_parameter 调用建议 |
|---|------------|-----------|------|--------|----------------------|
| 1 | `_cPDGras_` | `cPDGras` | gP/gDW | 0.022 | `default=0.022_rk` |
| 2 | `_cNDGras_` | `cNDGras` | gN/gDW | 0.10 | `default=0.10_rk` |
| 3 | `_cDGrasIn_` | `cDGrasIn` | gDW/m² | 0 | `default=0.0_rk` |
| 4 | `_cDCarrGras_` | `cDCarrGras` | gDW/m² | 15 | `default=15.0_rk` |
| 5 | `_kMigrGras_` | `kMigrGras` | 1/d | 0 | `default=0.0_rk, scale_factor=1.0_rk/secs_pr_day` |
| 6 | `_hDVegGras_` | `hDVegGras` | gDW/m² | 200 | `default=200.0_rk` |
| 7 | `_kDAssGras_` | `kDAssGras` | 1/d | 0.12 | `default=0.12_rk, scale_factor=1.0_rk/secs_pr_day` |
| 8 | `_fDAssGras_` | `fDAssGras` | - | 0.44 | `default=0.44_rk` |
| 9 | `_kDRespGras_` | `kDRespGras` | 1/d | 0.005 | `default=0.005_rk, scale_factor=1.0_rk/secs_pr_day` |
| 10 | `_fDissEgesGras_` | `fDissEgesGras` | - | 0.06 | `default=0.06_rk` |
| 11 | `_fDissMortGras_` | `fDissMortGras` | - | 0.10 | `default=0.10_rk` |
| 12 | `_kMortGras_` | `kMortGras` | 1/d | 0.00027 | `default=0.00027_rk, scale_factor=1.0_rk/secs_pr_day` |
| 13 | `_kHarvGrasWin_` | `kHarvGrasWin` | 1/d | 0 | `default=0.0_rk, scale_factor=1.0_rk/secs_pr_day` |
| 14 | `_kHarvGrasSum_` | `kHarvGrasSum` | 1/d | 0 | `default=0.0_rk, scale_factor=1.0_rk/secs_pr_day` |
| 15 | `_cTmOptGras_` | `cTmOptGras` | °C | 30 | `default=30.0_rk` |
| 16 | `_cSigTmGras_` | `cSigTmGras` | °C | 15 | `default=15.0_rk` |
| 17 | `_fGrasMortHyp_` | （不移植） | - | 0.9 | 3D 由 GETM 分层，无需 |
| 18 | `_fGrasEgesHyp_` | （不移植） | - | 0.5 | 同上 |
| 19 | `_fGrasExcrHyp_` | （不移植） | - | 0.5 | 同上 |

**实际需移植 16 个参数**（17-19 在 3D 中无意义）。

### 5.5 核心方程移植清单（A 部分 52 条，按功能分组）

#### 5.5.1 状态辅助（1 条）

```
_aDGras_ = merge(_sDGras_, NearZero, _sDGras_ > NearZero)  ! 防负
```

#### 5.5.2 温度函数（1 条）

```fortran
! 复用 wet_utility 的 uFunTmGaus
uFunTmGras = uFunTmGaus(uTm, cSigTmGras, cTmOptGras)
```

#### 5.5.3 食物饱和（1 条，草鱼专属 - 仅食植被）

```
_aDSatGras_ = _aDVeg_² / (_hDVegGras_² + _aDVeg_²)  ! Holling type III
```

**移植要点**：`_aDVeg_` 需通过 `register_state_dependency` 链接到 `macrophytes.F90` 的 `sDVeg`。

#### 5.5.4 环境校正（2 条）

```
_akDIncrGras_ = (_kDAssGras_ - _kDRespGras_) * _uFunTmGras_ - _kMortGras_
_tDEnvGras_ = max(0.0, _akDIncrGras_ / _cDCarrGras_ * _aDGras_²)
```

#### 5.5.5 同化与摄食（3 条）

```
_tDAssGras_ = _aDSatGras_ * (_kDAssGras_ * _uFunTmGras_ * _aDGras_ - _tDEnvGras_)
_tDConsGras_ = _tDAssGras_ / _fDAssGras_
_tDEgesGras_ = _tDConsGras_ - _tDAssGras_
```

#### 5.5.6 营养盐限制校正（4 条，草鱼专属）

```
_tDConsGrasNut_ = (_tDAssGras_/_fDAssGras_) * max(1.0,
                    _cNDGras_/_rNDFoodGras_*_fDAssGras_,
                    _cPDGras_/_rPDFoodGras_*_fDAssGras_)
_tDEgesGrasNut_ = _tDConsGrasNut_ - _tDAssGras_
_rNDFoodGras_ = _tNConsGras_ / _tDConsGras_  ! = _rNDVeg_
_rPDFoodGras_ = _tPConsGras_ / _tDConsGras_  ! = _rPDVeg_
```

**移植要点**：植被 P/D 比通常低于草鱼 P/D 比，会触发摄食增加补偿。

#### 5.5.7 死亡与骨骼沉出（3 条）

```
_tDMortGras_ = _kMortGras_ * _aDGras_ + (1.0 - _aDSatGras_) * _tDEnvGras_
_tDMortGrasBot_ = _fDBone_ * _tDMortGras_  ! 骨骼永久沉积
_tDMortGrasDet_ = _tDMortGras_ - _tDMortGrasBot_  ! 进入碎屑
```

#### 5.5.8 呼吸（1 条）

```
_tDRespGras_ = _kDRespGras_ * _uFunTmGras_ * _aDGras_
```

#### 5.5.9 迁移（1 条）

```
_tDMigrGras_ = _kMigrGras_ * (_cDGrasIn_ - _aDGras_)
```

#### 5.5.10 捕捞（2 条，草鱼专属季节切换）

```
_ukHarvGras_ = merge(_kHarvGrasWin_, _kHarvGrasSum_,
                     cos(2.0*Pi*sTime/DaysPerYear) > 0.1)
_tDHarvGras_ = _ukHarvGras_ * _aDGras_
```

**移植要点**：`sTime` 需从 FABM 获取当前模拟时间（天），`DaysPerYear=365`。

#### 5.5.11 P 通量（11 条）

| 方程 | 含义 |
|------|------|
| `_aPGras_ = _cPDGras_ * _aDGras_` | 总 P |
| `_tPConsGras_ = _rPDVeg_ * _tDConsGras_` | 摄食 P |
| `_afPAssGras_ = min(1.0, _cPDGras_/_rPDFoodGras_*_fDAssGras_)` | P 同化效率 |
| `_tPAssGras_ = _afPAssGras_ * _tPConsGras_` | 同化 P |
| `_tPEgesGras_ = _tPConsGras_ - _tPAssGras_` | 排泄 P |
| `_tPEgesGrasPO4_ = _fDissEgesGras_ * _tPEgesGras_` | 溶解排泄 P |
| `_tPEgesGrasDet_ = _tPEgesGras_ - _tPEgesGrasPO4_` | 碎屑排泄 P |
| `_tPExcrGras_ = _cPDGras_ * _tDRespGras_` | 呼吸排泄 P |
| `_tPMortGras_ = _cPDGras_ * _tDMortGras_` | 死亡 P |
| `_tPMortGrasBot_ = _fPBone_ * _tPMortGras_` | 骨骼 P |
| `_tPMortGrasPO4_ = _fDissMortGras_ * (_tPMortGras_ - _tPMortGrasBot_)` | 死亡溶解 P |
| `_tPMortGrasDet_ = _tPMortGras_ - _tPMortGrasBot_ - _tPMortGrasPO4_` | 死亡碎屑 P |
| `_tPMigrGras_ = _kMigrGras_ * (_cPDGras_*_cDGrasIn_ - _aPGras_)` | 迁移 P |
| `_tPHarvGras_ = _cPDGras_ * _tDHarvGras_` | 捕捞 P |

#### 5.5.12 N 通量（11 条，与 P 对称）

类似 P 通量，将 `cPDGras` 换 `cNDGras`、`fPBone` 换 `fDBone`（N 骨骼比 = C 骨骼比）、`PO4` 换 `NH4`。

#### 5.5.13 DW 总通量与导数（3 条）

```
_tDWebGras_ = _tDMigrGras_ + _tDAssGras_ - _tDRespGras_ - _tDMortGras_ - _tDHarvGras_
_dDGras_ = _tDWebGras_  ! 导数
_aGrowGras_ = _tDGrazVegGras_ / _aDGras_  ! 诊断输出
```

### 5.6 19 处耦合点（B 部分）

#### 5.6.1 植被耦合（3 处）

草鱼摄食植被，影响植被 DW/P/N 导数：

```
_tDGrazVegGras_ = max(_tDConsGras_, NearZero)  ! 植被损失
_tPGrazVegGras_ = _rPDVeg_ * _tDGrazVegGras_
_tNGrazVegGras_ = _rNDVeg_ * _tDGrazVegGras_
```

需在 `macrophytes.F90` 的 `do_bottom` 中减去 `_tDGrazVegGras_`。

#### 5.6.2 碎屑耦合（4 处）

草鱼排泄物和死亡体进入水柱碎屑（`_wDWebDetWHyp_/_wDWebDetWEpi_`）：
- `_tDEgesGrasNut_`（营养盐校正后排泄）→ 碎屑 DW
- `_tDMortGrasDet_`（非骨骼死亡）→ 碎屑 DW

需在 `om_pool.F90` 的 `do` 中加入草鱼贡献。

#### 5.6.3 PO4 耦合（4 处）

草鱼排泄/死亡释放溶解 P（`_wPWebPO4WHyp_/_wPWebPO4WEpi_`）：
- `_tPExcrGras_`（呼吸排泄）→ PO4
- `_tPEgesGrasPO4_`（排泄溶解）→ PO4
- `_tPMortGrasPO4_`（死亡溶解）→ PO4

需在 `abiotic_water.F90` 中加入。

#### 5.6.4 NH4 耦合（4 处）

类似 PO4，将 P 换 N、PO4 换 NH4。

#### 5.6.5 碎屑 P/N 耦合（4 处）

草鱼排泄/死亡的碎屑部分进入碎屑 P/N：
- `_tPEgesGrasDet_` → 碎屑 P
- `_tPMortGrasDet_` → 碎屑 P
- N 对称。

#### 5.6.6 系统总通量（3 处，质量平衡）

`_tDWebTotT_/_tPWebTotT_/_tNWebTotT_` 中需加入草鱼项：
- DW：`+ _tDMigrGras_ - _tDRespGras_ - _tDMortGrasBot_ - _tDHarvGras_`
- P：`+ _tPMigrGras_ - _tPMortGrasBot_ - _tPHarvGras_`
- N：`+ _tNMigrGras_ - _tNMortGrasBot_ - _tNHarvGras_`

**3D 中无需手动写总通量**，FABM 框架自动累加各模块导数。

### 5.7 移植实现策略

**方案 A（推荐）：新建独立 `grass_carp.F90` 模块**

优点：
- 不污染现有 fish 模块，遵循 FABM 模块化设计。
- 草鱼作为 `bottom_state`，与植被模块单位一致，无需深度转换。
- 可独立调试。

文件位置：`3DWET/src/wet/src/grass_carp.F90`

模块结构：
```fortran
module wet_grass_carp
   use fabm_types
   use fabm_particle  ! 或 type_bottom_model
   use wet_utility, ONLY: uFunTmGaus
   implicit none
   private

   type, extends(type_bottom_model), public :: type_wet_grass_carp
      ! 状态变量
      type (type_bottom_state_variable_id) :: id_sDGras, id_sPGras, id_sNGras
      ! 依赖
      type (type_bottom_dependency_id) :: id_aDVeg  ! 植被密度
      type (type_dependency_id) :: id_uTm, id_uTime
      ! 参数（16 个）
      real(rk) :: cPDGras, cNDGras, cDGrasIn, cDCarrGras, kMigrGras
      real(rk) :: hDVegGras, kDAssGras, fDAssGras, kDRespGras
      real(rk) :: fDissEgesGras, fDissMortGras, kMortGras
      real(rk) :: kHarvGrasWin, kHarvGrasSum, cTmOptGras, cSigTmGras
      ! 通用骨骼参数（复用 fish_pclake 的默认值）
      real(rk) :: fDBone, fPBone
   contains
      procedure :: initialize
      procedure :: do_bottom
   end type

   real(rk), parameter :: secs_pr_day = 86400.0_rk
   real(rk), parameter :: Pi = 3.14159265358979_rk
   real(rk), parameter :: NearZero = 1.0e-30_rk
   real(rk), parameter :: DaysPerYear = 365.0_rk
contains
   ! initialize: 注册 16 参数 + 3 状态 + 依赖
   ! do_bottom: 实现 5.5 节所有方程
end module
```

**方案 B：扩展 fish_pclake.F90**

不推荐，会破坏现有鱼类模块的清晰性。

### 5.8 移植工作量估算

| 任务 | 工作量 | 风险 |
|------|--------|------|
| 编写 grass_carp.F90 骨架 | 0.5 天 | 低 |
| 实现 52 条方程（do_bottom） | 1 天 | 中（营养盐校正易错） |
| 注册 16 参数 + 3 状态 | 0.5 天 | 低 |
| 配置 vegetation 依赖耦合 | 0.5 天 | 中（FABM 耦合语法） |
| 配置 om_pool/abiotic 耦合 | 1 天 | 高（需修改 3 个现有模块） |
| YAML 配置（fabm_full.yaml） | 0.5 天 | 低 |
| 单元测试（0D 验证） | 1 天 | 中 |
| 3D 集成测试 | 2 天 | 高（GETM-FABM 耦合问题） |
| **合计** | **7 天** | 中-高 |

---

## 6. 质量平衡对比

### 6.1 PCLake 质量平衡方程

PCLake 通过显式质量平衡校验模型闭合性：

**总 DW**：
```
_aDTotT_ = _aDTotTHyp_ + (_oDIMWEpi_+_oDDetWEpi_+_oDDiatWEpi_+_oDGrenWEpi_+_oDBlueWEpi_+_oDZooEpi_) * _uDepthWEpi_
           + _aDFish_ + _aDPisc_ + _aDGras_ + _aDVeg_
           + _aDIMS_ + _aDHumS_ + _aDDetS_ + _aDDiatS_ + _aDGrenS_ + _aDBlueS_ + _aDBent_
           + _aDTotM_ + _aDBlueSurf_
```

**总 P**：
```
_aPTotT_ = _aPTotTHyp_ + (_oPO4WEpi_+_oPDetWEpi_+_oPDiatWEpi_+_oPGrenWEpi_+_oPBlueWEpi_+_oPZooEpi_+_oPAIMWEpi_) * _uDepthWEpi_
           + _aPFish_ + _aPPisc_ + _aPGras_ + _aPVeg_
           + _aPO4S_ + _aPDetS_ + _aPHumS_ + _aPDiatS_ + _aPGrenS_ + _aPBlueS_ + _aPAIMS_ + _aPBent_
           + _aPTotM_ + _aPBlueSurf_
```

**总 N**：
```
_aNTotT_ = _aNTotTHyp_ + (_oNH4WEpi_+_oNO3WEpi_+_oNDetWEpi_+_oNDiatWEpi_+_oNGrenWEpi_+_oNBlueWEpi_+_oNZooEpi_) * _uDepthWEpi_
           + _aNFish_ + _aNPisc_ + _aNGras_ + _aNVeg_
           + _aNH4S_ + _aNO3S_ + _aNDetS_ + _aNHumS_ + _aNDiatS_ + _aNGrenS_ + _aNBlueS_ + _aNBent_
           + _aNTotM_ + _aNBlueSurf_
```

### 6.2 WET 质量平衡机制

WET/FABM **无显式质量平衡方程**，依赖：
1. 各模块 `do`/`do_bottom` 中正确写出导数。
2. FABM 框架自动累加各模块对同一状态变量的贡献（如 PO4 接收多个模块的排泄）。
3. GETM 物理传输保证守恒。

**风险**：
- 草鱼移植时若遗漏某个耦合点（如忘记将 `_tPExcrGras_` 加到 PO4 导数），会导致 P 不守恒。
- 建议移植后参考 PCLake 的 `_aPTotT_` 形式，编写诊断脚本核对 3D 总 P。

### 6.3 草鱼对质量平衡的贡献

草鱼模块闭合性检查（移植后应满足）：

| 元素 | 输入 | 输出 |
|------|------|------|
| DW | `_tDMigrGras_`（迁入）+ `_tDAssGras_`（同化=植被摄食） | `_tDRespGras_`（呼吸）+ `_tDMortGras_`（死亡，分骨骼+碎屑）+ `_tDHarvGras_`（捕捞） |
| P | `_tPMigrGras_` + `_tPAssGras_`（同化） | `_tPExcrGras_`（呼吸排泄→PO4）+ `_tPEgesGrasPO4_`+`_tPEgesGrasDet_`（排泄分溶解/碎屑）+ `_tPMortGrasBot_`+`_tPMortGrasPO4_`+`_tPMortGrasDet_`（死亡分骨骼/溶解/碎屑）+ `_tPHarvGras_` |
| N | 对称 | 对称 |

**校验方程**（移植后核对）：
```
d(_aDGras_)/dt ≈ _tDMigrGras_ + _tDAssGras_ - _tDRespGras_ - _tDMortGras_ - _tDHarvGras_
d(_aPGras_)/dt ≈ _tPMigrGras_ + _tPAssGras_ - _tPExcrGras_ - _tPEgesGras_ - _tPMortGras_ - _tPHarvGras_
```

---

## 7. 改进建议

### 7.1 优先级 1：草鱼模块移植（核心缺失）

**目标**：实现 `grass_carp.F90`，恢复 PCLake 完整食物网。

**步骤**：
1. 新建 `3DWET/src/wet/src/grass_carp.F90`，按 5.7 节方案 A 实现。
2. 注册 16 个参数（去掉 17-19 的分层参数）。
3. 注册 3 个 `bottom_state`（sDGras/sPGras/sNGras）。
4. 在 `do_bottom` 中实现 5.5 节 52 条方程。
5. 通过 `register_state_dependency` + `request_coupling_to_model` 链接到：
   - `macrophytes.F90` 的 `sDVeg`（食饵）
   - `om_pool.F90` 的 `sDS`/`sNS`/`sPS`（碎屑接收）
   - `abiotic_water.F90` 的 `sPO4W`/`sNH4W`（溶解营养盐接收）
6. 在 `fabm_full.yaml` 中添加 `grass_carp` 实例配置。
7. 在 `macrophytes.F90` 的 `do_bottom` 中减去 `_tDGrazVegGras_`（植被损失）。
8. 在 `om_pool.F90` 的 `do` 中加入草鱼排泄/死亡贡献。
9. 在 `abiotic_water.F90` 的 `do` 中加入草鱼 PO4/NH4 排泄贡献。

**验证**：
- 0D 单箱测试（参考 PCLake 默认值）。
- 3D 骆马湖测试：初始 sDGras=0.5 gDW/m²，运行 30 天，检查植被是否被压制。

### 7.2 优先级 2：鱼类模块统一（二选一）

**问题**：WET 同时存在 `fish_pclake.F90`（legacy，简单）和 `fish.F90`（标准版，复杂，含 foraging arena），用户易混淆。

**建议**：
- 若骆马湖场景不需要 foraging arena 细节，**继续用 `fish_pclake.F90`**，与 PCLake 一致性好。
- 若需多物种（草鱼+鲢鱼+鳙鱼+凶猛鱼），用 `fish.F90` 多实例化，但需额外配置 prey_suffix。
- **删除未使用的鱼类模块**避免混淆（需用户确认）。

### 7.3 优先级 3：分层参数清理

**问题**：PCLake 的 `_fGrasMortHyp_/_fGrasEgesHyp_/_fGrasExcrHyp_` 等 Epi/Hyp 分层分配参数在 3D 中无意义，但若移植时误用会导致错误。

**建议**：
- 草鱼模块移植时明确忽略 17-19 号参数。
- 在 `grass_carp.F90` 注释中说明"3D 由 GETM 物理分层替代 PCLake 手动 Epi/Hyp 分配"。

### 7.4 优先级 4：质量平衡诊断工具

**问题**：WET/FABM 无显式质量平衡校验，难以发现耦合遗漏。

**建议**：
1. 编写 Python 后处理脚本 `check_mass_balance.py`，读取 `LUOMAHU_WET.3d.nc` 和 `output.nc`，计算：
   - 总 DW = Σ(所有生物状态 × 网格面积 × 层厚)
   - 总 P = Σ(PO4 + 有机 P + 生物 P)
   - 总 N = Σ(NH4 + NO3 + 有机 N + 生物 N)
2. 对比每日总量，若漂移 >1% 则报警。
3. 参考 PCLake `_aDTotT_/_aPTotT_/_aNTotT_` 公式形式。

### 7.5 其他改进建议（非草鱼相关）

| 问题 | 建议 | 优先级 |
|------|------|--------|
| WET 浮游植物用 `min(P,N)` 限制，PCLake 用乘积 | 建议保持 WET 现状（Liebig 更符合生态学） | 低 |
| WET 无蓝藻表面水华 `_aDBlueSurf_` | 富营养化场景需补充 | 低 |
| 草鱼温度用底层温度 | 3D 中 FABM 自动提供局部温度，无需特殊处理 | — |
| `_cCPerDW_` vs `cCDRef` 命名不一致 | 统一为 `cCDRef` | 低 |

---

## 附录 A：草鱼模块移植 Checklist

- [ ] 新建 `grass_carp.F90` 文件骨架（module/type/parameter 声明）
- [ ] 注册 16 个参数（含 `scale_factor` 转换）
- [ ] 注册 3 个 `bottom_state`（sDGras/sPGras/sNGras）
- [ ] 注册依赖：uTm（温度）、uTime（时间）、aDVeg（植被密度）
- [ ] 实现 `do_bottom`：温度函数 + 饱和 + 环境校正 + 同化 + 摄食 + 死亡 + 呼吸 + 迁移 + 捕捞
- [ ] 实现 P/N 三通量（Cons/Ass/Eges/Excr/Mort/Migr/Harv）
- [ ] 实现营养盐限制校正（`_tDConsGrasNut_`）
- [ ] 在 CMakeLists.txt 注册新模块
- [ ] 在 `macrophytes.F90` 加入植被被摄食损失
- [ ] 在 `om_pool.F90` 加入草鱼碎屑贡献
- [ ] 在 `abiotic_water.F90` 加入草鱼 PO4/NH4 贡献
- [ ] 在 `fabm_full.yaml` 添加 grass_carp 实例
- [ ] 0D 单箱验证（对比 PCLake 默认值）
- [ ] 3D 骆马湖集成测试
- [ ] 编写质量平衡校验脚本

## 附录 B：关键文件路径

| 用途 | 路径 |
|------|------|
| PCLake 状态变量 | `_pclake_dump/states.tsv` |
| PCLake 参数 | `_pclake_dump/parameters.tsv` |
| PCLake 方程（分类） | `_pclake_dump/equations_by_category.md` |
| 草鱼完整方程 | `_pclake_dump/gras_only.md` |
| WET 鱼类（legacy） | `3DWET/src/wet/src/fish_pclake.F90` |
| WET 鱼类（标准） | `3DWET/src/wet/src/fish.F90` |
| WET 浮游植物 | `3DWET/src/wet/src/phytoplankton.F90` |
| WET 浮游动物 | `3DWET/src/wet/src/zooplankton.F90` |
| WET 底栖动物 | `3DWET/src/wet/src/zoobenthos.F90` |
| WET 大型植物 | `3DWET/src/wet/src/macrophytes.F90` |
| WET 有机物 | `3DWET/src/wet/src/om_pool.F90` |
| WET 无机水柱 | `3DWET/src/wet/src/abiotic_water.F90` |
| WET 无机沉积物 | `3DWET/src/wet/src/abiotic_sediment.F90` |
| 草鱼模块（待建） | `3DWET/src/wet/src/grass_carp.F90` |
| FABM 配置 | `case/fabm_full.yaml` |

---

*报告生成日期：2026-07-01*
*数据源：PCLake ACSL 导出 + WET/FABM Fortran 源码*
