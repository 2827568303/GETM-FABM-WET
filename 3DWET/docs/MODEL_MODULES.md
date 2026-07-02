# 3DWET 三维水动力-水质-食物网模型

## 模型源代码与模块说明

**版本**: v1.0  
**日期**: 2026-06-30

---

## 一、模型架构概述

3DWET 是一个完整的三维湖泊生态系统模型，由以下四个核心组件耦合而成：

```
3DWET Model Architecture
┌─────────────────────────────────────────────────┐
│                  GETM                           │
│  (General Estuarine Transport Model)            │
│  三维水动力模型 - 水流、温度、输运              │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│                  GOTM                           │
│  (General Ocean Turbulence Model)               │
│  湍流模型 - 垂直混合、湍动能                    │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│                  FABM                           │
│  (Framework for Aquatic Biogeochemical Models)  │
│  生物地球化学框架 - 模型耦合、变量管理          │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│                   WET                           │
│  (Whole Ecosystem Model) / PCLake               │
│  全生态系统模型 - 水质、浮游植物、浮游动物、    │
│  沉水植物、底栖生物、鱼类、食物网               │
└─────────────────────────────────────────────────┘
```

---

## 二、源代码目录结构

```
src/
├── fabm/                    # FABM 生物地球化学框架
│   ├── src/
│   │   ├── models/          # 各种生态模型
│   │   │   └── wet/         # WET 生态模型（通过 CMake 链接）
│   │   ├── drivers/         # 驱动程序
│   │   ├── yaml/            # YAML 解析器
│   │   ├── fabm.F90         # FABM 核心模块
│   │   ├── fabm_types.F90   # 类型定义
│   │   ├── fabm_config.F90  # 配置管理
│   │   └── ...
│   ├── include/             # 头文件
│   └── CMakeLists.txt
│
├── getm/                    # GETM 水动力模型
│   ├── src/
│   │   ├── 2d/              # 二维水动力模块
│   │   ├── 3d/              # 三维水动力模块
│   │   │   ├── getm_fabm.F90    # GETM-FABM 耦合
│   │   │   ├── temperature.F90  # 温度模块
│   │   │   ├── salinity.F90     # 盐度模块
│   │   │   ├── m3d.F90          # 三维主模块
│   │   │   ├── rivers.F90       # 河流模块
│   │   │   └── ...
│   │   ├── meteo/           # 气象模块
│   │   ├── ncdf/            # NetCDF 输入输出
│   │   ├── output/          # 输出管理
│   │   ├── input/           # 输入管理
│   │   ├── domain/          # 计算域
│   │   ├── futils/          # 工具函数
│   │   └── ...
│   ├── include/             # 头文件
│   └── ...
│
├── gotm/                    # GOTM 湍流模型
│   ├── src/
│   │   ├── fabm/            # GOTM-FABM 耦合
│   │   │   └── gotm_fabm.F90    # 耦合接口
│   │   ├── turbulence/      # 湍流模型
│   │   ├── meanflow/        # 平均流
│   │   ├── airsea/          # 海气交换
│   │   ├── util/            # 工具函数
│   │   └── ...
│   └── ...
│
└── wet/                     # WET 全生态系统模型
    ├── src/
    │   ├── wet_model_library.F90    # 模型库注册
    │   ├── abiotic_water.F90        # 非生物水质（水相）
    │   ├── abiotic_sediment.F90     # 非生物沉积物
    │   ├── phytoplankton.F90        # 浮游植物
    │   ├── zooplankton.F90          # 浮游动物
    │   ├── macrophytes.F90          # 沉水植物
    │   ├── zoobenthos.F90           # 底栖动物
    │   ├── fish.F90                 # 鱼类模块
    │   ├── fish_pclake.F90          # PCLake 鱼类参数化
    │   ├── om_pool.F90              # 有机质池
    │   ├── sediment_exchange.F90    # 沉积物-水交换
    │   ├── burial.F90               # 埋藏
    │   ├── bivalves.F90             # 双壳类
    │   ├── bot_pel_interface.F90    # 底栖-浮游界面
    │   ├── utility.F90              # 工具函数
    │   ├── version.F90.in           # 版本信息
    │   └── resus_sed.F90            # 沉积物再悬浮
    ├── testcases/                   # 测试用例
    └── CMakeLists.txt
```

---

## 三、各模块详细说明

### 3.1 GETM - 三维水动力模型

**功能**: 模拟湖泊的三维水动力过程，包括水流、温度、盐度（可选）的时空分布。

**主要子模块**:

| 模块 | 文件 | 功能 |
|------|------|------|
| 2D 水动力 | `2d/m2d.F90` | 深度平均的水位和流速计算 |
| 3D 水动力 | `3d/m3d.F90` | 三维流速、温度、盐度计算 |
| 湍流耦合 | `3d/gotm.F90` | 与 GOTM 湍流模型的接口 |
| FABM 耦合 | `3d/getm_fabm.F90` | 与 FABM 生态模型的耦合接口 |
| 河流输入 | `3d/rivers.F90` | 河流入流和出流处理 |
| 气象强迫 | `meteo/meteo.F90` | 气象数据读取和热通量计算 |
| NetCDF I/O | `ncdf/ncdf_*.F90` | NetCDF 格式的输入输出 |
| 坐标系统 | `3d/coordinates.F90` | Sigma 坐标变换 |

**关键配置参数** (getm.inp):
- `M`: 垂直层数（Sigma 层数）
- `timestep`: 时间步长（秒）
- `maxdepth`: 最大水深
- `calc_temp`: 是否计算温度
- `calc_salt`: 是否计算盐度

---

### 3.2 GOTM - 湍流模型

**功能**: 提供垂直湍流混合参数化，计算湍动能、耗散率等。

**主要子模块**:

| 模块 | 文件 | 功能 |
|------|------|------|
| FABM 耦合 | `fabm/gotm_fabm.F90` | GOTM-FABM 耦合接口 |
| 湍流模型 | `turbulence/tkeeq.F90` | 湍动能方程 |
| 平均流 | `meanflow/meanflow.F90` | 平均流动计算 |
| 海气交换 | `airsea/airsea.F90` | 海面通量计算 |
| 状态方程 | `util/eqstate.F90` | 水的状态方程 |

**关键配置参数** (gotmturb.nml):
- 湍流模型选择（k-epsilon, k-omega 等）
- 背景扩散系数
- 混合长度参数

---

### 3.3 FABM - 生物地球化学框架

**功能**: 提供标准化的生物地球化学模型耦合框架，管理生态模型变量、耦合关系和时间积分。

**核心组件**:

| 组件 | 文件 | 功能 |
|------|------|------|
| 核心模块 | `fabm.F90` | FABM 核心，模型注册和调度 |
| 类型定义 | `fabm_types.F90` | 核心数据类型定义 |
| 配置管理 | `fabm_config.F90` | YAML 配置解析 |
| 耦合管理 | `fabm_coupling.F90` | 模型间耦合关系 |
| 调度器 | `fabm_schedule.F90` | 时间步调度 |
| 属性管理 | `fabm_properties.F90` | 变量属性管理 |

**FABM 主机接口**:
- GOTM 主机: `gotm/src/fabm/gotm_fabm.F90`
- GETM 通过 GOTM 接口间接调用 FABM

---

### 3.4 WET - 全生态系统模型

**功能**: 基于 PCLake 模型的全生态系统模拟，包括水质、浮游植物、浮游动物、沉水植物、底栖生物、鱼类等完整食物网。

**生态模块列表**:

#### 3.4.1 非生物模块

| 模块 | 文件 | 变量前缀 | 说明 |
|------|------|----------|------|
| 非生物水相 | `abiotic_water.F90` | `abiotic_water_*` | 水中营养盐、氧气、无机物 |
| 非生物沉积物 | `abiotic_sediment.F90` | `abiotic_sediment_*` | 沉积物中营养盐 |

**关键变量**:
- `sNH4W` / `sNH4S`: 氨氮（水/沉积物）
- `sNO3W` / `sNO3S`: 硝氮（水/沉积物）
- `sPO4W` / `sPO4S`: 磷酸盐（水/沉积物）
- `sO2W` / `sO2S`: 溶解氧（水/沉积物）

#### 3.4.2 有机质模块

| 模块 | 文件 | 变量前缀 | 说明 |
|------|------|----------|------|
| 有机质池 | `om_pool.F90` | `POM_*`, `DOM_*` | 颗粒态和溶解态有机质 |

**关键变量**:
- `sPOC`, `sPON`, `sPOP`: 颗粒态有机碳/氮/磷
- `sDOC`, `sDON`, `sDOP`: 溶解态有机碳/氮/磷

#### 3.4.3 浮游植物模块

| 模块 | 文件 | 变量前缀 | 说明 |
|------|------|----------|------|
| 浮游植物 | `phytoplankton.F90` | `cyanobacteria_*` | 蓝藻 |
|  |  | `diatoms_*` | 硅藻 |
|  |  | `greens_*` | 绿藻 |

**关键变量**:
- `sDW`: 干重生物量 (gDW/m³)
- `oChla`: 叶绿素 a (gChla/m³)
- `aNLim`, `aPLim`, `aLLim`: 氮/磷/光限制因子

**生理过程**:
- 光合作用（受光、温度、营养盐限制）
- 呼吸作用
- 死亡
- 沉降
- 营养盐吸收

#### 3.4.4 浮游动物模块

| 模块 | 文件 | 变量前缀 | 说明 |
|------|------|----------|------|
| 浮游动物 | `zooplankton.F90` | `cladocerans_*` | 枝角类 |
|  |  | `copepods_*` | 桡足类 |

**关键变量**:
- `sDW`: 干重生物量 (gDW/m³)
- `aFoodLim`: 食物限制因子

**生态过程**:
- 摄食（浮游植物、碎屑）
- 排泄
- 死亡
- 生长繁殖

#### 3.4.5 沉水植物模块

| 模块 | 文件 | 变量前缀 | 说明 |
|------|------|----------|------|
| 沉水植物 | `macrophytes.F90` | `macrophytes_*` | 沉水植物 |

**关键变量**:
- `sDW_PV`: 单位面积干重 (gDW/m²)
- `sD`: 植株高度 (m)

**生态过程**:
- 光合作用
- 营养盐吸收（根和叶片）
- 死亡分解
- 与浮游植物的光竞争

#### 3.4.6 底栖生物模块

| 模块 | 文件 | 变量前缀 | 说明 |
|------|------|----------|------|
| 底栖动物 | `zoobenthos.F90` | `zoobenthos_*` | 底栖动物 |

**关键变量**:
- `sDW_PV`: 单位面积干重 (gDW/m²)

**生态过程**:
- 摄食（沉积物有机质）
- 排泄
- 生物扰动

#### 3.4.7 鱼类模块

| 模块 | 文件 | 变量前缀 | 说明 |
|------|------|----------|------|
| 鱼类 | `fish.F90` | `PiscFish_*` | 食鱼性鱼类 |
|  |  | `AdFish_*` | 底栖性成鱼 |
|  |  | `JuFish_*` | 浮游性幼鱼 |

**关键变量**:
- `sDW_PV`: 单位面积干重 (gDW/m²)
- `sN`: 氮含量
- `sP`: 磷含量

**鱼类功能群**:
1. **PiscFish** (食鱼性鱼): 捕食其他鱼类
2. **AdFish** (底栖性成鱼): 捕食底栖动物
3. **JuFish** (浮游性幼鱼): 捕食浮游动物

**生命阶段** (qStage):
- 0: 未启用阶段结构
- 1+: 启用阶段结构（幼鱼、成鱼等）

**生态过程**:
- 摄食
- 生长
- 繁殖
- 死亡（自然死亡、捕捞死亡）
- 营养盐排泄

#### 3.4.8 界面与交换模块

| 模块 | 文件 | 说明 |
|------|------|------|
| 沉积物-水交换 | `sediment_exchange.F90` | 水-沉积物界面的物质交换 |
| 底栖-浮游界面 | `bot_pel_interface.F90` | 底栖与浮游系统的耦合 |
| 埋藏 | `burial.F90` | 沉积物埋藏过程 |
| 沉积物再悬浮 | `resus_sed.F90` | 沉积物再悬浮 |

#### 3.4.9 其他模块

| 模块 | 文件 | 说明 |
|------|------|------|
| 双壳类 | `bivalves.F90` | 双壳类软体动物（可选） |
| 工具函数 | `utility.F90` | 通用工具函数 |
| 模型库 | `wet_model_library.F90` | 所有 WET 模型的注册 |

---

## 四、食物网结构

### 4.1 完整食物网示意图

```
                    [PiscFish 食鱼性鱼]
                            │
                            ▼
[AdFish 底栖性成鱼] ←── [JuFish 浮游幼鱼]
       │                       │
       ▼                       ▼
[Zoobenthos 底栖生物]   [Zooplankton 浮游动物]
       │                       │
       ▼                       ▼
[OM 有机质]          [Phytoplankton 浮游植物]
       │                       │
       └───────────┬───────────┘
                   ▼
        [Nutrients 营养盐]
                   ▲
                   │
         [Macrophytes 沉水植物]
```

### 4.2 营养级关系

| 营养级 | 类群 | 代表物种/类群 |
|--------|------|-------------|
| 顶级捕食者 | 鱼类 | PiscFish (食鱼性鱼) |
| 次级消费者 | 鱼类 | AdFish, JuFish |
| 初级消费者 | 浮游动物、底栖生物 | Cladocerans, Copepods, Zoobenthos |
| 初级生产者 | 浮游植物、沉水植物 | Cyanobacteria, Diatoms, Greens, Macrophytes |
| 分解者 | 有机质/营养盐 | POM, DOM, Nutrients |

---

## 五、已知 Bug 修复说明

### 5.1 Bug #1: gotm_fabm.F90 itime 可选参数问题

**补丁文件**: `patches/gotm_fabm_itime_fixed.F90`  
**影响文件**: `src/gotm/src/fabm/gotm_fabm.F90`

**问题描述**:
在 `calculate_derived_input` 子程序中，`itime` 是可选参数，但直接传递给 `fabm_update_time1` 的非可选参数 `t`，导致段错误。

**修复方案**:
```fortran
! 修复前
call fabm_update_time(model, itime)

! 修复后
if (present(itime)) then
    call fabm_update_time(model, itime)
else
    call fabm_update_time(model, 0.0_rk)
endif
```

---

### 5.2 Bug #2: fish.F90 check_state 数组越界

**补丁文件**: `patches/fish_v2_patched.F90`  
**影响文件**: `src/wet/src/fish.F90`

**问题描述**:
鱼类模块中，`id_sFRes`、`id_sDSiz`、`id_tDReproPOM` 等变量仅在 `qStage > 0` 时注册，但 `check_state` 子程序无条件访问这些变量，导致数组下标越界。

**修复方案**:
在 `check_state` 子程序中添加 `qStage > 0` 条件判断：
```fortran
if (self%qStage > 0) then
    _GET_(self%id_sFRes, sFRes)
    ! ...
endif
```

---

### 5.3 Bug #3: getm_fabm.F90 v2 补丁

**补丁文件**: `patches/getm_fabm_v2_patched.F90`  
**影响文件**: `src/getm/src/3d/getm_fabm.F90`

**说明**: GETM 与 FABM 耦合接口的改进版本，优化了变量传递和时间同步。

---

### 5.4 Bug #4: om_pool.F90 数组下标错误

**补丁文件**: `patches/om_pool_patched.F90`  
**影响文件**: `src/wet/src/om_pool.F90`

**问题描述**:
refractory POM 状态变量注册时使用了错误的标志位。

**修复方案**:
使用 `lRefrPV` 标志替代 `lTransPV` 标志判断是否注册 refractory POM 变量。

---

## 六、模型变量命名约定

### 6.1 变量前缀

| 前缀 | 含义 | 示例 |
|------|------|------|
| `s` | 状态变量 (State) | `sDW`, `sNH4W` |
| `o` | 诊断变量 (Output/diagnostic) | `oChla`, `oPP` |
| `a` | 辅助变量 (Auxiliary) | `aNLim`, `aLLim` |
| `t` | 通量/速率 (Transport/rate) | `tDReproPOM` |

### 6.2 变量后缀

| 后缀 | 含义 | 示例 |
|------|------|------|
| `W` | 水相 (Water) | `sNH4W`, `sO2W` |
| `S` | 沉积物相 (Sediment) | `sNH4S`, `sO2S` |
| `_PV` | 单位面积 (Per unit Area/Volume) | `sDW_PV` |
| `_f` | 限制因子 (Factor) | `aNLim_f` |

### 6.3 三维 vs 二维变量

- **3D 变量**: 分布在整个水柱中（如浮游植物、营养盐）
- **2D 变量**: 仅存在于沉积物或底栖层（如底栖生物、沉水植物）

---

## 七、配置文件说明

### 7.1 fabm.yaml - FABM 生态模型配置

YAML 格式的生态模型配置文件，定义：
- 启用哪些生态模块
- 各模块的参数设置
- 初始条件
- 耦合关系

### 7.2 getm.inp - GETM 水动力配置

NAMELIST 格式的水动力配置文件，定义：
- 计算域设置（网格、水深）
- 时间设置（起止时间、时间步长）
- 物理参数（扩散系数、摩擦系数等）
- 输出设置

### 7.3 getm_fabm.inp - FABM 耦合配置

定义 GETM 与 FABM 的耦合方式。

### 7.4 gotmturb.nml - 湍流模型配置

GOTM 湍流模型的参数设置。

### 7.5 output.yaml - 输出配置

定义哪些变量需要输出、输出频率等。

---

## 八、输入数据文件

| 文件 | 格式 | 说明 |
|------|------|------|
| `bathymetry.nc` | NetCDF | 湖底地形数据 |
| `meteo.nc` | NetCDF | 气象强迫数据（温度、风速、辐射等） |
| `rivers.nc` | NetCDF | 河流入流数据（流量、营养盐浓度等） |
| `riverinfo.dat` | ASCII | 河流位置和属性信息 |

---

**文档版本**: v1.0  
**最后更新**: 2026-06-30
