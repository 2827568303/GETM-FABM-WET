# GETM-FABM-WET/PCLake 模型开发总结报告

**生成日期**: 2026-06-29  
**模型版本**: v26_clean_production (GCC 13)

---

## 一、项目概述

### 1.1 模型耦合架构

本项目实现了 **GETM-FABM-WET** 三维湖泊生态模型耦合系统：

```
GETM (Hydrodynamic Model)
    └── FABM (Framework for Aquatic Biogeochemical Models)
            └── WET (Whole Ecosystem Model)
                    ├── PCLake (Lake Water Quality)
                    ├── Macrophytes (沉水植物)
                    ├── Zoobenthos (底栖动物)
                    ├── Fish (鱼类模块)
                    │       ├── PiscFish (食鱼性鱼)
                    │       ├── AdFish (底栖性成鱼)
                    │       └── JuFish (浮游性幼鱼)
                    └── Phytoplankton
                            ├── Cyanobacteria (蓝藻)
                            ├── Diatoms (硅藻)
                            └── Greens (绿藻)
```

### 1.2 项目路径

| 组件 | 路径 |
|------|------|
| **主项目目录** | `C:\Users\dinod\Desktop\GETM-FABM-WET` |
| **WET 源码** | `C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet\src` |
| **FABM 源码** | `C:\Users\dinod\Desktop\GETM-FABM-PCLake\fabm\src` |
| **GETM 源码** | `C:\Users\dinod\Desktop\GETM-FABM-PCLake\getm\src` |
| **测试算例** | `C:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case` |
| **构建脚本** | `C:\Users\dinod\Desktop\GETM-FABM-WET\build_gcc13_v*.sh` |
| **可视化结果** | `C:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case\figures\` |

---

## 二、已解决的问题

### 2.1 Bug #1: temporal_mean 段错误 ❌ 已修复

**症状**:  
- 模拟在 `fabm_update_time1` 函数返回时发生段错误
- 仅在使用 GCC 13 编译时出现，GCC 9 正常

**根本原因**:  
在 `gotm_fabm.F90` 的 `calculate_derived_input` 子程序中：
```fortran
! 原始代码（有问题的）
call fabm_update_time(model, itime)  ! itime 是可选参数，可能不存在
```

当 `itime` 可选参数不存在时，直接传递给 `fabm_update_time1` 的非可选参数 `t`，导致未定义行为（栈损坏）。

**修复方案**:  
文件: [gotm_fabm_itime_fixed.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/gotm_fabm_itime_fixed.F90)
```fortran
! 修复后的代码
if (present(itime)) then
    call fabm_update_time(model, itime)
else
    call fabm_update_time(model, 0.0_rk)
endif
```

---

### 2.2 Bug #2: Fish check_state 数组越界 ❌ 已修复

**症状**:  
- 鱼类模块的 `check_state` 子程序访问未注册的变量
- `environment%prefetch` 数组索引为 -1

**根本原因**:  
鱼类模块中的以下变量仅在 `qStage > 0` 时注册：
- `id_sFRes`（储备生物量比例）
- `id_sDSiz`（平均个体大小）
- `id_tDReproPOM`、`id_tNReproPOM`、`id_tPReproPOM`、`id_tCReproPOM`（繁殖相关诊断）

但 `check_state` 子程序中**无条件**访问这些变量。

**修复方案**:  
文件: [fish_v2_patched.F90](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/fish_v2_patched.F90)

```fortran
! 原始代码（有问题的）
_GET_(self%id_sFRes, sFRes)
if (sFRes > self%fResMax) sFRes = self%fResMax

! 修复后的代码
if (self%qStage > 0) then
    _GET_(self%id_sFRes, sFRes)
    if (sFRes > self%fResMax) sFRes = self%fResMax
else
    sFRes = 0.0_rk
endif

! 同样修复诊断变量的输出
if (self%qStage > 0) then
    _SET_DIAGNOSTIC_(self%id_tDReproPOM, tDReproPOM)
    _SET_DIAGNOSTIC_(self%id_tNReproPOM, tNReproPOM)
    _SET_DIAGNOSTIC_(self%id_tPReproPOM, tPReproPOM)
    _SET_DIAGNOSTIC_(self%id_tCReproPOM, tCReproPOM)
endif
```

---

### 2.3 Bug #3: om_pool.F90 数组下标错误 ❌ 已修复

**症状**:  
- 编译时出现数组边界不匹配警告
- refractory POM 状态变量注册逻辑错误

**根本原因**:  
使用 `lTransPV`（易降解 POM）标志判断是否注册 refractory POM 变量。

**修复方案**:  
使用 `lRefrPV`（reftractory POM）标志判断。

---

### 2.4 Bug #4: 河流通量计算错误 ⚠️ 部分修复

**症状**:  
- 部分河流（如 ERHE）在湖泊边界外
- 导致通量计算异常

**说明**:  
已添加 `fix_erhe.py` 脚本修复 ERHE 河流位置问题，但其他部分河流仍可能存在边界问题。

---

## 三、待解决的问题

### 3.1 初始条件跳变 ⚠️ 需要调查

**症状**:  
- 模型结果在第 10 天左右出现明显的跳变
- 可能与初始条件设置有关

**可能原因**:  
1. FABM 变量初始值设置不合理
2. 时间平均 (temporal_mean) 初始化时历史数据不足
3. 河流输入数据的初始时间不匹配

**建议**:  
- 检查 `fabm.yaml` 中的初始值设置
- 考虑添加模型spin-up阶段（warm-up）
- 验证河流输入数据的时间范围

---

### 3.2 层数配置不一致 ⚠️ 需要确认

**症状**:  
- 配置文件中 `M = 10`
- 实际输出只有 6 个 sigma 层

**说明**:  
```
Sigma layers: 6
Sigma values: [-1.  -0.8 -0.6 -0.4 -0.2  0. ]
```

**可能原因**:  
1. `kdum = 5` 参数影响
2. GETM 内部层数优化机制
3. 水深限制（湖泊最大深度 15m，平均深度 3.4m）

**建议**:  
如需真正的 10 层输出：
1. 修改 `getm.inp` 中的 `M = 10`
2. 减少或删除 `kdum` 参数
3. 重新编译运行

---

## 四、模型配置详情

### 4.1 编译配置

**最新构建脚本**: [build_gcc13_v26_clean.sh](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_v26_clean.sh)

**编译器**: GCC 13.3.0  
**构建类型**: Release (-O2)  
**安装路径**: `C:\Users\dinod\Desktop\GETM-FABM-WET\install_gcc13_v26_clean`

**编译命令**:
```bash
bash build_gcc13_v26_clean.sh
```

**关键编译步骤**:
1. 恢复原始 fabm.F90（无调试输出）
2. 应用 fish_v2_patched.F90（qStage 修复）
3. 应用 gotm_fabm_itime_fixed.F90（itime 参数修复）
4. 编译 FABM + WET
5. 编译 GETM
6. 恢复原始源文件

---

### 4.2 模型配置文件

#### 4.2.1 主配置文件

| 文件 | 路径 | 说明 |
|------|------|------|
| **getm.inp** | [luomahu_case/getm.inp](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case/getm.inp) | GETM 主配置 |
| **getm_fabm.inp** | [luomahu_case/getm_fabm.inp](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case/getm_fabm.inp) | FABM 耦合配置 |
| **fabm.yaml** | [luomahu_case/fabm.yaml](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case/fabm.yaml) | FABM 生态模型配置 |

#### 4.2.2 GETM 配置参数

```
&m3d
    M = 10                    # 垂直层数（实际输出6层）
    cnpar = 1.0              # 垂直混合系数
    calc_temp = .true.       # 温度计算
    calc_salt = .false.      # 盐度计算
    vel3d_adv_split = 1     # 3D 速度平流方案
&/

&time
    timestep = 30.0          # 时间步长 (秒)
    start = '2020-01-01 00:00:00'
    stop = '2020-01-31 00:00:00'  # 30 天模拟
/

&domain
    vert_cord = 1           # Sigma 坐标
    maxdepth = 25.0          # 最大水深 (m)
    kdum = 5                 # 底部层数标记
/
```

#### 4.2.3 湖泊基本信息

| 参数 | 值 |
|------|------|
| **湖泊名称** | 罗目湖 (Luomahu Lake) |
| **网格尺寸** | 44 × 54 (I × J) |
| **网格分辨率** | 500m × 500m |
| **最大深度** | 15.0 m |
| **平均深度** | 3.4 m |
| **水面面积** | 11.64 km² (1164 水点) |
| **河流数量** | 6 条 |

#### 4.2.4 河流列表

| 河流名称 | 位置 (i, j) | 流量 (m³/s) |
|----------|-------------|-------------|
| YIHE | 26, 12 | 2.6 |
| LUONAN | 12, 42 | 5.8 |
| DAYUN | 7, 32 | 13.9 |
| ZHANGSHAN | 32, 15 | 2.1 |
| YANGHE | 35, 28 | 1.7 |
| ERHE | 38, 22 | 2.0 |

---

### 4.3 生态模型模块配置

#### 4.3.1 完整食物网模块列表

| 模块名称 | 变量前缀 | 说明 |
|----------|----------|------|
| **Abiotic Water** | `abiotic_water_*` | 非生物水质变量 |
| **Abiotic Sediment** | `abiotic_sediment_*` | 非生物沉积物变量 |
| **POM** | `POM_*` | 颗粒态有机物 |
| **DOM** | `DOM_*` | 溶解态有机物 |
| **Macrophytes** | `macrophytes_*` | 沉水植物 |
| **Zoobenthos** | `zoobenthos_*` | 底栖动物 |
| **PiscFish** | `PiscFish_*` | 食鱼性鱼类 |
| **AdFish** | `AdFish_*` | 底栖性成鱼 |
| **JuFish** | `JuFish_*` | 浮游性幼鱼 |
| **Cyanobacteria** | `cyanobacteria_*` | 蓝藻 |
| **Diatoms** | `diatoms_*` | 硅藻 |
| **Greens** | `greens_*` | 绿藻 |
| **Cladocerans** | `cladocerans_*` | 枝角类浮游动物 |
| **Copepods** | `copepods_*` | 桡足类浮游动物 |
| **Humus** | `humus_*` | 腐殖质 |

#### 4.3.2 关键输出变量

**水动力变量**:
- `elev`: 水位 (m)
- `uu`, `vv`: 水平流速 (m/s)
- `w`: 垂向流速 (m/s)
- `temp`: 水温 (°C)
- `tke`: 湍动能 (m²/s²)

**水质变量**:
- `abiotic_water_sNH4W`: 氨氮 (gN/m³)
- `abiotic_water_sNO3W`: 硝氮 (gN/m³)
- `abiotic_water_sPO4W`: 磷酸盐 (gP/m³)
- `abiotic_water_sO2W`: 溶解氧 (gO₂/m³)

**生物变量**:
- `*_sDW`: 干重生物量 (gDW/m³ 或 gDW/m²)
- `*_oChla`: 叶绿素浓度 (g/m³)
- `*_aNLim`, `*_aPLim`, `*_aLLim`: 氮、磷、光限制因子

---

### 4.4 修复补丁文件

| 文件名 | 用途 | 路径 |
|--------|------|------|
| `gotm_fabm_itime_fixed.F90` | 修复 itime 可选参数问题 | [链接](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/gotm_fabm_itime_fixed.F90) |
| `fish_v2_patched.F90` | 修复 fish check_state qStage 越界 | [链接](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/fish_v2_patched.F90) |
| `getm_fabm_v2_patched.F90` | GETM-FABM 耦合补丁 v2 | [链接](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/getm_fabm_v2_patched.F90) |
| `om_pool_patched.F90` | OM pool 数组下标修复 | [链接](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/om_pool_patched.F90) |
| `fix_erhe.py` | 修复 ERHE 河流位置 | [链接](file:///c:/Users/dinod/Desktop/GETM-FABM-WET/fix_erhe.py) |

---

## 五、运行指南

### 5.1 编译模型

```bash
cd C:\Users\dinod\Desktop\GETM-FABM-WET
bash build_gcc13_v26_clean.sh
```

### 5.2 运行模拟

```bash
cd C:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case
../install_gcc13_v26_clean/bin/getm_cartesian
```

### 5.3 生成可视化

```bash
cd C:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case
python visualize_complete.py
```

可视化结果将保存在 `figures/` 目录下。

---

## 六、生成的可视化图

| 编号 | 文件名 | 内容 |
|------|--------|------|
| 01 | 01_lake_bathymetry_grid.png | 湖泊地形和网格 |
| 02 | 02_hydrodynamics.png | 水位、水温、流速 |
| 03 | 03_water_quality_nutrients.png | NH4, NO3, PO4, O2 |
| 04 | 04_phytoplankton_spatial.png | 蓝藻、硅藻、绿藻 |
| 05 | 05_zooplankton_spatial.png | 枝角类、桡足类 |
| 06 | 06_macrophytes_benthos.png | 沉水植物、底栖生物 |
| 07 | 07_fish_spatial.png | 三种鱼类生物量 |
| 08 | 08_foodweb_overview.png | 食物网总览 |
| 09 | 09_vertical_profiles.png | 湖心垂直剖面 |
| 10 | 10_depth_time_heatmaps.png | 深度-时间热力图 |
| 11 | 11_fish_vertical.png | 鱼类垂直分布 |

---

## 七、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v26_clean | 2026-06-29 | **最终生产版本**：原始 fabm.F90 + 所有修复 |
| v25_final | 2026-06-29 | 最终版本（含调试输出） |
| v24_production | 2026-06-29 | 生产版本（含调试输出） |
| v23 | 2026-06-29 | fish check_state 修复 v2 |
| v22 | 2026-06-29 | fish check_state 修复 v1 |
| v21 | 2026-06-29 | gotm_fabm itime 修复 v2 |
| v20 | 2026-06-29 | gotm_fabm itime 修复 v1 |
| v19 | 2026-06-29 | do-nothing fish 测试 |
| v18 | 2026-06-29 | 调试版本（添加大量 DEBUG 输出） |
| v9-v17 | 2026-06-28 | 早期开发版本 |

---

## 八、附录

### A. 关键日志文件

| 文件 | 路径 |
|------|------|
| 最新构建日志 | `run_logs/build_gcc13_v26.log` |
| 最新运行日志 | `luomahu_case/run_gcc13_v26_full.log` |

### B. 关键 Python 脚本

| 脚本 | 功能 |
|------|------|
| `visualize_complete.py` | 完整食物网可视化 |
| `build_foodweb.py` | 构建食物网配置 |
| `check_vars.py` | 检查 NetCDF 变量 |
| `fix_erhe.py` | 修复 ERHE 河流 |

### C. 联系方式

如有问题，请联系开发团队或查阅以下资源：
- GETM 官方文档: https://getm.eu/
- FABM 官方文档: https://fabm.net/
- WET/PCLake 模型文献

---

**报告生成者**: TRAE AI Assistant  
**最后更新**: 2026-06-29
