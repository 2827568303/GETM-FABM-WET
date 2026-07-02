# WET 模块: abiotic_water (水体非生物过程)

> **源文件**: [3DWET/src/wet/src/abiotic_water.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90)
> **模块名**: `wet_abiotic_water`
> **FABM 模型路径**: `wet/abiotic_water`
> **作用**: 水体中无机营养盐、有机物、氧的动力学过程
> **重要变更**: WET 新版本中，反硝化(denitrification)和有机物矿化的氧消耗已移到 `om_pool` 模块

---

## 1. 状态变量

| 变量名 | 单位 | 说明 | 初始值 | 沉降速率 | 河流稀释 |
|--------|------|------|--------|---------|---------|
| `sDIMW` | g/m³ | 无机悬浮物 (DIM) | 5.0 | cVSetIM (-1.1 m/d) | 否 |
| `sSiPaW` | g/m³ | 颗粒硅 (Particulate Si) | 0.02 | cVSetSi (-0.3 m/d) | 否 |
| `sPO4W` | g/m³ | 磷酸盐 (PO4-P) | 0.01 | 0 (不沉降) | 否 |
| `sPAIMW` | g/m³ | 无机物吸附磷 (P adsorbed to IM) | 0.0 | cVSetIM | 否 |
| `sNH4W` | g/m³ | 铵 (NH4-N) | 0.1 | 0 | 否 |
| `sNO3W` | g/m³ | 硝酸盐 (NO3-N) | 0.1 | 0 | 否 |
| `sSiO2W` | g/m³ | 二氧化硅 (SiO2) | 3.0 | 0 | 否 |
| `sO2W` | g/m³ | 溶解氧 (O2) | 10.0 | 0 | 否 |

**注**: `no_river_dilution=.TRUE.` 表示河流入流不直接稀释这些变量（因它们随物理平流自然传输）

---

## 2. 参数

### 2.1 光学参数
| 参数 | 单位 | 默认值 | 说明 |
|------|------|--------|------|
| `cExtSpIM` | m²/gDW | 0.05 | 无机物比消光系数 |

### 2.2 磷吸附参数
| 参数 | 单位 | 默认值 | 说明 |
|------|------|--------|------|
| `cKPAdsOxW` | m³/gP | 0.6 | 氧化条件下 P 吸附亲和力 |
| `cRelPAdsAlW` | gP/gAl | 0.134 | 每 g Al 最大 P 吸附量 |
| `cRelPAdsDWW` | gP/gDW | 0.00003 | 每 g DW 最大 P 吸附量 |
| `cRelPAdsFeW` | gP/gFe | 0.0675 | 每 g Fe 最大 P 吸附量 |
| `fAlDIMW` | gAl/gDW | 0.01 | DIM 中 Al 含量 |
| `fFeDIMW` | gFe/gDW | 0.01 | DIM 中 Fe 含量 |
| `fRedMaxW` | - | 0.9 | P 吸附亲和力最大还原系数 |
| `kPSorpW` | 1/d | 0.05 | P 吸附速率常数 |

### 2.3 硝化参数
| 参数 | 单位 | 默认值 | 说明 |
|------|------|--------|------|
| `kNitrW` | 1/d | 0.3 | 20℃ 硝化速率常数 |
| `cThetaNitrW` | 1/e^*C | 1.03 | 硝化温度系数 |
| `hO2Nitr` | mgO2/l | 2.0 | 硝化半饱和氧浓度 |
| `O2PerNH4W` | mol/mol | 2.0 | 每摩尔 NH4 硝化消耗 O2 摩尔数 |

### 2.4 BOD/再曝气参数
| 参数 | 单位 | 默认值 | 说明 |
|------|------|--------|------|
| `cThetaAer` | 1/e^*C | 1.011 | 再曝气温度系数 |
| `hO2BOD` | mgO2/l | 1.0 | BOD 半饱和氧浓度 |

### 2.5 硅矿化参数
| 参数 | 单位 | 默认值 | 说明 |
|------|------|--------|------|
| `kSiMinPaW` | 1/d | 0.03 | 20℃ 颗粒硅生物溶解速率 |
| `cThetaMinSiW` | 1/e^*C | 1.02 | 硅矿化温度系数 |

### 2.6 沉降参数
| 参数 | 单位 | 默认值 | 说明 |
|------|------|--------|------|
| `cVSetIM` | m/d | -1.1 | 无机物最大沉降速率（负=下沉） |
| `cVSetSi` | m/d | -0.3 | 颗粒硅最大沉降速率 |

### 2.7 大气沉降参数
| 参数 | 单位 | 默认值 | 说明 |
|------|------|--------|------|
| `tDDepoIM` | g/m²/d | 0.0 | 无机物大气沉降 |
| `tPDepoPO4` | g/m²/d | 0.0 | 磷酸盐大气沉降 |
| `tNDepoNH4` | g/m²/d | 0.0 | 铵大气沉降 |
| `tNDepoNO3` | g/m²/d | 0.0 | 硝酸盐大气沉降 |

### 2.8 化学计量常数
| 常数 | 值 | 说明 |
|------|-----|------|
| `molO2molC` | 2.6667 | mol O2 / mol C |
| `molO2molN` | 2.2857 | mol O2 / mol N |
| `molNmolC` | 1.1667 | mol N / mol C |

---

## 3. 环境依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| `uTm` | 垂向 | 水温 (℃) |
| `salt` | 垂向 | 盐度 (PSU) |
| `uVWind` | 水平 | 风速 (m/s) |

---

## 4. 核心方程

### 4.1 硅颗粒矿化 (Si mineralization)
**位置**: [abiotic_water.F90 L197-202](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90#L197-L202)

温度函数:
$$f_{T,nitr} = \theta_{nitr}^{T - 20}$$

$$f_{T,minSi} = \theta_{minSi}^{T - 20}$$

颗粒硅矿化速率:
$$w_{SiMinPaW} = k_{SiMinPaW} \cdot f_{T,minSi} \cdot s_{SiPaW}$$

> **注**: 注释中提到 "should Si-POM also be sensitive to O2 conc?" — 当前版本**未考虑氧限制**，可能后续版本会加

### 4.2 BOD 氧限制因子
**位置**: [abiotic_water.F90 L203](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90#L203)

$$a_{CorO2BOD} = \frac{O_2}{h_{O2BOD} + O_2}$$

- 这是 Michaelis-Menten 型氧限制函数，用于后续磷吸附
- `hO2BOD` 默认 1.0 mgO2/l

### 4.3 磷吸附过程
**位置**: [abiotic_water.F90 L209-214](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90#L209-L214)

**Step 1**: 最大 P 吸附量（单位 gP/gDW）
$$a_{PAdsMaxW} = c_{RelPAdsDWW} + a_{CorO2BOD} \cdot c_{RelPAdsFeW} \cdot f_{FeDIMW} + c_{RelPAdsAlW} \cdot f_{AlDIMW}$$

- 三项分别代表：DW 本身吸附、Fe氧化物吸附（受氧限制）、Al氧化物吸附（不受氧限制）

**Step 2**: P 吸附亲和力（含还原修正）
$$a_{KPAdsW} = (1 - f_{RedMaxW} \cdot (1 - a_{CorO2BOD})) \cdot c_{KPAdsOxW}$$

- 缺氧时 `aCorO2BOD→0`，亲和力降低到 `(1-fRedMaxW)·cKPAdsOxW = 0.1×0.6 = 0.06`
- 富氧时 `aCorO2BOD→1`，亲和力恢复到 `cKPAdsOxW = 0.6`

**Step 3**: P 吸附等温线（Langmuir 型）
$$a_{PIsoAdsW} = \frac{a_{PAdsMaxW} \cdot a_{KPAdsW} \cdot s_{PO4W}}{1 + a_{KPAdsW} \cdot s_{PO4W}}$$

**Step 4**: 平衡浓度
$$a_{PEqIMW} = a_{PIsoAdsW} \cdot s_{DIMW}$$

**Step 5**: P 吸附通量（趋向平衡）
$$w_{PSorpIMW} = k_{PSorpW} \cdot (a_{PEqIMW} - s_{PAIMW})$$

- 正值表示 PO4 → PAIMW（吸附）；负值表示 PAIMW → PO4（解吸）

### 4.4 硝化过程
**位置**: [abiotic_water.F90 L218-219](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90#L218-L219)

氧限制（二次型，与 BOD 不同）:
$$a_{CorO2NitrW} = \frac{O_2^2}{h_{O2Nitr}^2 + O_2^2}$$

硝化通量:
$$w_{NNitrW} = k_{NitrW} \cdot f_{T,nitr} \cdot a_{CorO2NitrW} \cdot s_{NH4W}$$

- **重要**: 硝化的氧限制用**二次型**，而 BOD/磷吸附用**Michaelis-Menten 型**——这是 PCLake 的传统设计

### 4.5 硝化耗氧
**位置**: [abiotic_water.F90 L228](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90#L228)

$$w_{O2NitrW} = O_{2,PerNH4W} \cdot mol_{O2/molN} \cdot w_{NNitrW}$$

- `molO2molN = 2.2857` (即 16/7)
- 化学计量: NH4 + 2O2 → NO3 + 2H+ + H2O

### 4.6 氧饱和度与百分比
**位置**: [abiotic_water.F90 L229-230](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90#L229-L230)

$$c_{O2Sat} = \text{uFunO2Sat}(salt, T) \quad \text{(见 utility.F90)}$$

$$p_{O2Sat} = \frac{O_2}{c_{O2Sat}} \times 100 \quad [\%]$$

---

## 5. 状态变量微分方程（ROC 汇总）

**位置**: [abiotic_water.F90 L234-241](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90#L234-L241)

| 状态变量 | 微分方程 (dC/dt) |
|---------|-----------------|
| `sDIMW` | $$\frac{d}{dt}s_{DIMW} = 0$$ (本模块不改变，仅沉降+平流) |
| `sSiPaW` | $$\frac{d}{dt}s_{SiPaW} = -w_{SiMinPaW}$$ |
| `sPO4W` | $$\frac{d}{dt}s_{PO4W} = -w_{PSorpIMW}$$ |
| `sPAIMW` | $$\frac{d}{dt}s_{PAIMW} = +w_{PSorpIMW}$$ |
| `sNH4W` | $$\frac{d}{dt}s_{NH4W} = -w_{NNitrW}$$ |
| `sNO3W` | $$\frac{d}{dt}s_{NO3W} = +w_{NNitrW}$$ |
| `sSiO2W` | $$\frac{d}{dt}s_{SiO2W} = +w_{SiMinPaW}$$ |
| `sO2W` | $$\frac{d}{dt}s_{O2W} = -w_{O2NitrW}$$ |

> **重要**: 反硝化（NO3→N2）和有机物矿化的氧消耗已在 WET 新版本移到 `om_pool` 模块。本模块**只处理硝化耗氧**，不处理矿化耗氧。

---

## 6. 表面过程 (do_surface)

**位置**: [abiotic_water.F90 L313-349](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90#L313-L349)

### 6.1 氧再曝气
温度函数:
$$f_{T,Aer} = \theta_{Aer}^{T - 20}$$

氧饱和浓度（简化版，仅温度，无盐度修正）:
$$u_{O2Sat} = 14.652 - 0.41022 \cdot T + 0.007991 \cdot T^2 - 0.000077774 \cdot T^3$$

> **注**: 此处用的是**简化多项式**，与 utility.F90 中的 `uFunO2Sat`（含盐度修正的 Riley&Skirrow 公式）**不同**——这是 PCLake 原版公式

再曝气系数（风速依赖）:
$$k_{Aer} = 0.727 \cdot W^{0.5} - 0.371 \cdot W + 0.0376 \cdot W^2$$

- W 为风速 uVWind (m/s)

再曝气通量:
$$t_{O2Aer} = k_{Aer} \cdot f_{T,Aer} \cdot (u_{O2Sat} - O_2) \cdot a_{FunLemnaAer}$$

- `aFunLemnaAer` 当前硬编码为 1.0（浮萍覆盖对再曝气的削减，未启用）
- 正值表示 O2 从大气进入水体

### 6.2 大气沉降
直接通过 `_SET_SURFACE_EXCHANGE_` 注入：
- `sDIMW` ← `tDDepoIM` (g/m²/d)
- `sNH4W` ← `tNDepoNH4`
- `sNO3W` ← `tNDepoNO3`
- `sPO4W` ← `tPDepoPO4`

> **默认值全为 0**，需要用户在 yaml 中显式配置才有大气沉降

---

## 7. 光消光贡献 (get_light_extinction)

**位置**: [abiotic_water.F90 L284-308](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/3DWET/src/wet/src/abiotic_water.F90#L284-L308)

$$ext_{IM} = c_{ExtSpIM} \cdot s_{DIMW}$$

- 通过 `_SET_EXTINCTION_` 叠加到总消光
- 注意：此处只算无机物消光，有机物/藻类消光由各自模块贡献

---

## 8. 模块间耦合（向其他模块提供）

本模块通过 FABM 的诊断变量机制，向其他模块提供以下聚合变量（dummy 值，用于无对应模块时占位）：

| 聚合变量 | 单位 | 用途 | 本模块贡献 |
|---------|------|------|----------|
| `wet_totN` | gN/m³ | 总氮计算 | sNH4W + sNO3W |
| `wet_totP` | gP/m³ | 总磷计算 | sPO4W + sPAIMW |
| `total_bioturbation` | gDW/m³/d | 生物扰动 | 0 (dummy) |
| `total_macrophyte_biomass` | gDW/m² | 大型植物总生物量 | 0 (dummy) |
| `total_aDSubVeg` | gDW/m² | 沉水植物生物量 | 0 (dummy) |
| `total_aCovVeg` | % | 植被覆盖度 | 0 (dummy) |
| `total_afCovSurfVeg` | - | 浮叶植物覆盖度 | 0 (dummy) |
| `wet_chla` | μg/L | 叶绿素 a 总量 | 0 (dummy) |

> **机制说明**: 当用户配置中没有 macrophytes/fish/phytoplankton 等模块时，这些 dummy 变量保证聚合变量不会因为缺少贡献者而报错。

---

## 9. PCLake+Gras 对比（基于 derivatives sheet 实际提取）

### 9.1 结构性差异（已确认）

| 过程 | WET 位置 | PCLake+Gras 位置 | 差异说明 |
|------|---------|----------------|---------|
| 反硝化 | `om_pool` 模块 | derivatives sheet `wDDenitWEpi/Hyp/M` | **WET 重构了反硝化，按 OM 实例分组** |
| OM 矿化耗氧 | `om_pool` 模块 | derivatives sheet | **WET 重构了矿化耗氧** |
| OM 矿化本身 | `om_pool` 模块 | derivatives sheet | **WET 把所有 OM 过程归到 om_pool** |
| 水体分区 | 1D 垂向分层（每层独立） | **Hyp/Epi/M (沼泽) 三区分别计算** | **PCLake 按热分层分区，WET 按层分区** |

### 9.2 公式逐项对比

| 公式 | WET 实现 | PCLake+Gras 实现 | 差异 |
|------|---------|----------------|------|
| **硝化氧限制** | `O²/(h²+O²)` | `oO2WEpi²/(hO2Nitr²+oO2WEpi²)` ([R1692](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/docs/PCLake_comparison/pclake_derivatives.csv)) | **完全一致** |
| **BOD 氧限制** | `O/(h+O)` | `oO2WEpi/(hO2BOD+oO2WEpi)` ([R1688](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/docs/PCLake_comparison/pclake_derivatives.csv)) | **完全一致** |
| **P 吸附亲和力** | `(1-fRedMax·(1-aCorO2BOD))·cKPAdsOxW` | `(1.0-fRedMax·(1.0-aCorO2BODEpi))·cKPAdsOx_` ([R1709](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/docs/PCLake_comparison/pclake_derivatives.csv)) | **一致**（变量名无 W 后缀） |
| **P 平衡浓度** | `aPIsoAdsW·sDIMW` | `aPIsoAdsWEpi·oDIMWEpi` ([R1711](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/docs/PCLake_comparison/pclake_derivatives.csv)) | **一致** |
| **P 吸附通量** | `kPSorpW·(aPEqIMW-sPAIMW)` | `kPSorp·(aPEqIMWEpi-oPAIMWEpi)` ([R1712](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/docs/PCLake_comparison/pclake_derivatives.csv)) | **一致**（PCLake 参数名无 W） |
| **硝化通量** | `kNitrW·fT·aCorO2NitrW·sNH4W` | `kNitrW·uFunTmNitrEpi·aCorO2NitrWEpi·oNH4WEpi` ([R1693](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/docs/PCLake_comparison/pclake_derivatives.csv)) | **一致** |
| **硝化耗氧** | `O2PerNH4W·molO2molN·wNNitrW` | `O2PerNH4·molO2molN·wNNitrWEpi` ([R1694](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/docs/PCLake_comparison/pclake_derivatives.csv)) | **一致** |

### 9.3 重要差异：再曝气

| 项 | WET 实现 | PCLake+Gras 实现 | 差异 |
|----|---------|----------------|------|
| 再曝气通量 | `kAer·fT·(uO2Sat-O2)·aFunLemnaAer` | `kAer·uFunTmAerEpi·(uO2SatEpi-oO2WEpi)·aFunFloatAer·aFunBlueSurfAer·...` ([R1674](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/docs/PCLake_comparison/pclake_derivatives.csv)) | **PCLake 含蓝藻表面覆盖削减 (aFunBlueSurfAer) 和浮叶植物削减 (aFunFloatAer)，WET 仅保留浮萍 (aFunLemnAer=1.0)** |
| O2 饱和度 (do_surface) | 简化多项式 `14.652-0.41T+0.008T²-...` | 待确认 `uO2SatEpi` 公式 | 待对比 |
| O2 饱和度 (do 诊断) | Riley&Skirrow 含盐度修正 | 纯淡水（无盐度修正） | **WET 加强了盐度修正** |

### 9.4 PCLake+Gras 特有但 WET 无的过程

| PCLake+Gras 过程 | 变量 | 说明 |
|-----------------|------|------|
| 沼泽区硝化 | `wNNitrWM` | PCLake 有独立沼泽模块，WET 无 |
| 沼泽区反硝化 | `wDDenitWM` | 同上 |
| 沼泽区 P 吸附 | `wPSorpIMWM` | 同上 |
| 下层(Hyp)区过程 | `*WHyp` 系列 | PCLake 显式区分上下层，WET 由垂向分层自然处理 |
| 蓝藻表面覆盖影响再曝气 | `aFunBlueSurfAer` | WET 未实现 |
| 浮叶植物影响再曝气 | `aFunFloatAer` | WET 未实现（仅保留浮萍 aFunLemnAer=1.0） |

### 9.5 对比结论

**abiotic_water 模块的核心生化公式（硝化、P吸附）与 PCLake+Gras 完全一致**。主要差异在：
1. **结构差异**: WET 把 OM 相关过程（矿化、反硝化、矿化耗氧）移到了 `om_pool` 模块
2. **物理差异**: WET 简化了再曝气（去掉了蓝藻/浮叶植物的削减反馈）
3. **分区差异**: PCLake 显式分 Hyp/Epi/M 三区，WET 用 1D 垂向分层自然处理
4. **盐度修正**: WET 的氧饱和度函数含盐度修正（适用性更广）
