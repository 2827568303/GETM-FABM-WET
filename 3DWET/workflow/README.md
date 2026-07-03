# 3DWET 工作流使用指南

**从湖泊配置到模型运行的标准化流程**

---

## 概述

3DWET 工作流将湖泊建模过程拆分为 6 个独立模块，使数据准备、模型构建和运行分离，便于：

- 不同湖泊间的快速迁移测试
- 协作者直接复用源码应用于自己的湖泊
- 模块化调试，降低报错排查难度

### 工作流架构

```
lake_config.yaml          case_config.yaml
       │                         │
       ▼                         │
┌─────────────┐                  │
│ Module 1    │ → 数据文件        │
│ Preprocess  │ (bathy/meteo/    │
│             │  rivers/init)    │
└─────────────┘                  │
       │                         │
       └─────→ data_dir ─────────┤
                                 │
                         ┌───────▼───────┐
                         │ Module 2      │ → 完整case目录
                         │ Build Case    │ (getm.inp, fabm.yaml,
                         │               │  数据文件等)
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │ Module 3      │ (集成在Module 2中)
                         │ Init Cond.    │ 预设: mesotrophic/
                         │               │ eutrophic/hypereutrophic
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │ Module 4      │ → 模拟结果
                         │ Run Model     │ (TESTLAKE.2d.nc,
                         │               │  .3d.nc, output.nc)
                         └───────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              Module 5      Module 6      (未来)
              Postprocess   Calibration
              (待开发)      (待开发)
```

### 当前状态

| 模块 | 状态 | 说明 |
|------|------|------|
| Module 1: 前处理 | ✅ 已完成 | 从 lake_config.yaml 生成 4 个数据文件 |
| Module 2: 模型构建 | ✅ 已完成 | 从 case_config.yaml 组装完整 case 目录 |
| Module 3: 初始条件 | ✅ 已完成 | 3 种营养状态预设 + 自定义模式 |
| Module 4: 模型运行 | ✅ 已完成 | 输入验证 + 执行 + 自动 numrecs patch |
| Module 5: 结果输出 | ⏳ 待开发 | 时间序列提取、可视化 |
| Module 6: 率定校验 | ⏳ 待开发 | 点位对比、自动参数调整 |

---

## 快速开始（5分钟端到端示例）

以 TestLake（10×4 网格，30天模拟）为例，演示完整工作流：

```bash
cd 3DWET

# Step 1: 前处理 - 生成湖泊数据
python3 workflow/1_preprocess/preprocess.py workflow/test_lake_config.yaml

# Step 2: 模型构建 - 组装 case 目录
python3 workflow/2_build_case/build_case.py workflow/test_case_config.yaml

# Step 3: 模型运行 - 验证并执行
python3 workflow/4_run/run_model.py workflow/cases/TestLake --threads 4
```

预期输出：
```
Water level net change: 0.0000 m     ← 水量平衡
temp: range=[0.00, 12.19]            ← 温度合理
diatoms_sDW: range=[0.23, 3.37]      ← 硅藻正常生长
cladocerans_sD: range=[0.03, 0.25]   ← 浮游动物稳定（无崩溃）
JuFish_sD: range=[0.14, 0.16]        ← 鱼类稳定（无崩溃）
```

---

## Module 1: 前处理 (Preprocess)

### 功能

从单个 YAML 配置文件生成模型所需的 4 个数据文件：

| 输出文件 | 内容 | 格式 |
|----------|------|------|
| `bathymetry.nc` | 湖泊网格、水深、坐标 | NetCDF3 |
| `meteo.nc` | 气象强迫场（温度、风、降水等） | NetCDF3 |
| `rivers.nc` | 河流流量和水质 | NetCDF3 |
| `fabm_init.nc` | 生态初始场（沉水植物等） | NetCDF3 |
| `riverinfo.dat` | 河流位置索引 | 文本 |
| `meteo_input.txt` | 气象文件索引 | 文本 |

### 用法

```bash
python3 workflow/1_preprocess/preprocess.py <lake_config.yaml> [--output-dir <dir>]
```

- `<lake_config.yaml>`: 湖泊配置文件（参考 [templates/lake_config.yaml](1_preprocess/templates/lake_config.yaml)）
- `--output-dir`: 输出目录（默认: `./<lake_name>_data`）

### lake_config.yaml 关键参数

```yaml
lake:
  name: "MyLake"
  latitude: 30.0          # 纬度（影响太阳辐射计算）
  longitude: 120.0
  elevation: 100.0        # 海拔(m)

grid:
  nx: 20                  # 东西向网格数
  ny: 10                  # 南北向网格数
  dx: 500.0               # 网格尺寸(m)
  dy: 500.0

shape:
  mode: "oval"            # rectangle | oval | custom
  width_ratio: 0.9        # 椭圆宽窄比

bathymetry:
  avg_depth: 3.5          # 平均水深(m)
  max_depth: 7.0          # 最大水深(m)
  depth_profile: "center_deep"  # center_deep | uniform | east_deep

rivers:
  - name: "INFL1"
    position: "north"     # north/south/east/west
    type: "inflow"
    base_flow: 2.0        # m³/s
    water_quality: { nh4: 0.2, no3: 1.5, po4: 0.05, ... }
  - name: "OUTFL"
    position: "east"
    type: "outflow"
    base_flow: null       # null=自动计算（保持水量平衡）

meteo:
  mode: "synthetic"       # synthetic | file
  start_date: "2020-01-01"
  n_days: 366
  climate:
    avg_temp: 18.0
    annual_precip: 1200   # mm
    annual_evap: 1100     # mm（必须 < precip 以维持水量平衡）

ecology:
  macrophytes:
    enabled: true
    depth_range: [1.0, 2.5]  # 沉水植物分布水深
    initial_biomass: 30.0
```

### 注意事项

- **水量平衡**: 所有入流流量之和 = 出流流量，净降水量 = precip - evap
- **precip/evap 精度**: 必须为 float64（float32 会导致精度丢失，水量不平衡）
- **n_days 与模拟期匹配**: `n_days` 决定生成数据的天数，case_config 的 `end_date` 必须在此范围内
- **河流位置**: 自动搜索最近的水域网格，无需手动指定坐标

---

## Module 2: 模型构建 (Build Case)

### 功能

从 case_config.yaml 组装完整的 case 目录，包括：

- 生成 6 个配置文件: `getm.inp`, `fabm.yaml`, `gotm_fabm.yaml`, `gotmturb.nml`, `output.yaml`, `getm_fabm.inp`
- 复制 6 个数据文件: `bathymetry.nc`, `meteo.nc`, `rivers.nc`, `fabm_init.nc`, `riverinfo.dat`, `meteo_input.txt`

### 用法

```bash
python3 workflow/2_build_case/build_case.py <case_config.yaml> [--output-dir <dir>]
```

- `<case_config.yaml>`: case 配置文件（参考 [templates/case_config.yaml](2_build_case/templates/case_config.yaml)）
- `--output-dir`: 输出目录（默认: `./cases/<case_name>`）

### case_config.yaml 关键参数

```yaml
case:
  name: "MyCase"
  run_id: "MYLAKE"                    # 输出文件前缀（大写）
  start_date: "2020-01-01 00:00:00"
  end_date: "2020-12-30 00:00:00"     # 注意：需在 meteo 数据范围内

data:
  data_dir: "./my_lake_data"          # 前处理输出目录（相对路径基于config文件位置）

grid:
  nx: 20                              # 必须与 lake_config 一致
  ny: 10
  kdum: 10                            # sigma层数
  maxdepth: 8.0                       # 最大水深(需≥实际最大水深+1m)

run:
  timestep: 30.0                      # 必须30s（防止数值不稳定）
  n_threads: 8

initial_conditions:
  preset: "eutrophic"                 # mesotrophic | eutrophic | hypereutrophic | custom

numerics:
  ode_method: 10                      # 10=Patankar保正（必须）
  repair_state: true                  # 修复负值（必须）
  shade: true                         # 生物自遮光（必须）
  fwf_method: 2                       # 2=从文件读取淡水通量

output:
  freq_2d: 1440                       # 2D输出频率（步数，1440=每12小时）
  freq_3d: 1440                       # 3D输出频率
```

### 初始条件预设

Module 3 集成在 Module 2 中，通过 `initial_conditions.preset` 选择：

| 预设 | 营养状态 | 硅藻 | 蓝藻 | 浮游动物 | 鱼类 |
|------|----------|------|------|----------|------|
| `mesotrophic` | 中营养 | 0.10 | 0.05 | 0.15 | 低 |
| `eutrophic` | 富营养 | 0.30 | 0.30 | 0.30 | 中 |
| `hypereutrophic` | 重富营养 | 0.50 | 0.80 | 0.40 | 高 |
| `custom` | 自定义 | — | — | — | — |

> **重要**: 初始浮游植物 ≥ 0.20 gDW/m³，浮游动物 ≥ 0.30 gDW/m³，否则会引发生态级联崩溃（浮游动物饥饿 → 鱼类崩溃 → 硅藻水华）。

---

## Module 4: 模型运行 (Run Model)

### 功能

1. **输入验证**: 5步验证（文件完整性、bathymetry、meteo float64、河流、配置文件）
2. **模型执行**: OpenMP 多线程 + Patankar 警告过滤
3. **自动 numrecs patch**: 修复 NetCDF3 已知 bug（GETM 在 meteo EOF 时未刷新头部）
4. **输出验证**: 检查输出文件大小和退出码

### 用法

```bash
python3 workflow/4_run/run_model.py <case_dir> [options]

Options:
  --threads <n>       OpenMP线程数（默认: 8）
  --no-validate       跳过输入验证
  --no-filter         不过滤Patankar警告（日志会很大）
```

### 运行状态判断

| 退出码 | 状态 | 说明 |
|--------|------|------|
| 0 | SUCCESS | 模型正常运行完成 |
| 0 + "meteo EOF" | SUCCESS | 预期行为：气象数据读完后退出，输出已完整 |
| 非0 | FAILED | 检查 run.log |

### 输出文件

| 文件 | 内容 | 格式 |
|------|------|------|
| `{run_id}.2d.nc` | 2D水动力（水位、流速） | NetCDF3（已patch） |
| `{run_id}.3d.nc` | 3D水动力（温度、3D流速） | NetCDF3（已patch） |
| `output.nc` | FABM生态（530个变量） | NetCDF3（已patch） |
| `run.log` | 运行日志 | 文本 |

---

## 完整示例：异龙湖（366天模拟）

```bash
cd 3DWET

# 1. 创建 lake_config.yaml（参考异龙湖参数）
cat > workflow/yilong_lake_config.yaml << 'EOF'
lake:
  name: "Yilong"
  latitude: 23.55
  longitude: 102.50
  elevation: 1414.0

grid:
  nx: 28
  ny: 8
  dx: 500.0
  dy: 500.0

shape:
  mode: "oval"
  width_profile: "cosine"
  width_ratio: 0.85

bathymetry:
  avg_depth: 3.5
  max_depth: 4.5
  depth_profile: "center_deep"

rivers:
  - name: "INFL1"
    position: "north"
    type: "inflow"
    base_flow: 1.5
    water_quality: { nh4: 0.30, no3: 1.0, po4: 0.06 }
  - name: "OUTFL"
    position: "east"
    type: "outflow"
    base_flow: null
    water_quality: { nh4: 0.10, no3: 0.8, po4: 0.04 }

meteo:
  mode: "synthetic"
  start_date: "2020-01-01"
  n_days: 366
  climate:
    avg_temp: 18.0
    annual_precip: 950
    annual_evap: 900

ecology:
  macrophytes:
    enabled: true
    depth_range: [1.0, 2.5]
    initial_biomass: 30.0
EOF

# 2. 创建 case_config.yaml
cat > workflow/yilong_case_config.yaml << 'EOF'
case:
  name: "Yilong"
  run_id: "YILONG"
  start_date: "2020-01-01 00:00:00"
  end_date: "2020-12-30 00:00:00"

data:
  data_dir: "./Yilong_data"

grid:
  nx: 28
  ny: 8
  kdum: 10
  maxdepth: 6.0

run:
  timestep: 30.0
  n_threads: 8

initial_conditions:
  preset: "eutrophic"

numerics:
  ode_method: 10
  repair_state: true
  shade: true
  fwf_method: 2
  calc_salt: false

output:
  freq_2d: 1440
  freq_3d: 1440
EOF

# 3. 运行完整工作流
python3 workflow/1_preprocess/preprocess.py workflow/yilong_lake_config.yaml
python3 workflow/2_build_case/build_case.py workflow/yilong_case_config.yaml
python3 workflow/4_run/run_model.py workflow/cases/Yilong --threads 8
```

---

## 常见问题排查

### 1. 水位持续下降

**原因**: precip/evap 精度问题或 fwf_method 设置错误

**解决**:
- 确认 `meteo.nc` 中 precip/evap 为 float64
- 确认 `getm.inp` 中 `fwf_method = 2`
- 确认入流总量 > 出流总量 + 净蒸发

### 2. 生态级联崩溃（浮游动物/鱼类归零）

**原因**: 初始浮游植物过低 → 浮游动物饥饿 → 鱼类崩溃 → 硅藻水华

**解决**:
- 使用 `preset: "eutrophic"` 或更高
- 自定义时确保: 浮游植物 ≥ 0.20, 浮游动物 ≥ 0.30

### 3. "Not sufficient river data available"

**原因**: case_config 的 `end_date` 超过了 lake_config 的 `n_days` 范围

**解决**:
- `n_days` ≥ (end_date - start_date) 的天数 + 1

### 4. "Cannot match namelist object name"

**原因**: getm.inp 中浮点数格式错误（如 `30.0.0`）

**解决**: 已在 build_case.py 中修复，确保使用最新版本

### 5. 输出文件显示 0 字节 / 无法读取

**原因**: NetCDF3 numrecs=0 bug（GETM 在 meteo EOF 时未刷新头部）

**解决**: 已在 run_model.py 中自动 patch，无需手动处理

### 6. 硅藻峰值过高（>10 gDW/m³）

**原因**: 浮游动物牧食压力不足

**解决**:
- 提高初始浮游动物到 0.30-0.50
- 或降低硅藻初始值到 0.10-0.20

---

## 目录结构

```
3DWET/workflow/
├── README.md                          ← 本文件
├── test_lake_config.yaml              ← TestLake 前处理配置
├── test_case_config.yaml              ← TestLake case配置
├── TestLake_data/                     ← 前处理输出（自动生成）
├── cases/
│   └── TestLake/                      ← 完整case目录（自动生成）
│       ├── getm.inp
│       ├── fabm.yaml
│       ├── gotm_fabm.yaml
│       ├── ...（配置文件）
│       ├── bathymetry.nc
│       ├── meteo.nc
│       ├── ...（数据文件）
│       └── run.log
├── 1_preprocess/
│   ├── preprocess.py                  ← Module 1: 前处理
│   └── templates/
│       └── lake_config.yaml           ← 湖泊配置模板
├── 2_build_case/
│   ├── build_case.py                  ← Module 2: 模型构建
│   └── templates/
│       └── case_config.yaml           ← case配置模板
├── 3_init_conditions/
│   └── presets/
│       └── trophic_states.py          ← Module 3: 初始条件预设
├── 4_run/
│   ├── run_model.py                   ← Module 4: 模型运行
│   └── validate_inputs.py             ← 输入验证
├── 5_postprocess/                     ← Module 5: 待开发
└── 6_calibration/                     ← Module 6: 待开发
```

---

## 技术要点

1. **时间步长必须 30s**: 河流入口附近局部流速高，更大步长会导致数值不稳定
2. **ode_method=10 (Patankar)**: 保正数值方法，防止状态变量出现负值
3. **shade=true**: 生物自遮光反馈，浮游植物生物量影响光衰减
4. **repair_state=true**: 自动修复负值状态变量
5. **fwf_method=2**: 从文件读取淡水通量（降水-蒸发），不用模型自计算
6. **precip/evap float64**: float32 精度不足会导致降水量被截断为 0
7. **numrecs patch**: NetCDF3 格式 bug，GETM 在 meteo EOF 时未刷新记录计数

---

*最后更新: 2026-07-02*
