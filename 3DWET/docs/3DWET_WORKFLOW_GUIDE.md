# 3DWET 标准化流程完整说明

> 本文档说明 3DWET 项目的整体架构、文件位置、运行方式、输出结果存储与查看方法。
> 适用于新协作者快速上手，也方便使用不同湖泊开展研究。

---

## 一、整体框架（6 模块架构）

```
用户填写 lake_config.yaml（一个湖泊一个文件）
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│ Module 1: preprocessor  ← 3DWET/preprocessor/          │
│   读取 YAML → 生成 6 个标准数据文件（NetCDF/dat/txt）     │
└─────────────────────────────────────────────────────────┘
        │ 6 个数据文件
        ▼
┌─────────────────────────────────────────────────────────┐
│ Module 2: model_builder  ← 3DWET/model_builder/        │
│   读取 YAML → 生成 6 个配置文件（inp/nml/yaml）           │
└─────────────────────────────────────────────────────────┘
        │ 6 个配置文件
        ▼
┌─────────────────────────────────────────────────────────┐
│ Module 4: 运行 GETM-FABM-WET（编译好的可执行文件）        │
│   读取 12 个输入文件 → 输出 3 个 NetCDF + 1 个日志        │
└─────────────────────────────────────────────────────────┘
        │ 输出文件
        ▼
┌─────────────────────────────────────────────────────────┐
│ Module 5: 可视化  ← scripts/theoretical_lake/           │
│   读取 NetCDF → 生成 PNG 图片                            │
└─────────────────────────────────────────────────────────┘
```

**6 个模块**（当前已实现 1、2、5，3、4、6 待后续开发）：

| 模块 | 状态 | 位置 | 功能 |
|------|------|------|------|
| 1. 前处理 | ✅ 已实现 | `3DWET/preprocessor/` | 数据标准化、湖泊网格、地形、河流、气象、初始条件 |
| 2. 建模 | ✅ 已实现 | `3DWET/model_builder/` | 标准数据 → 完整可运行的湖泊模型配置 |
| 3. 初始条件 | ⏳ 待开发 | — | 水文、水质、食物网等状态变量的精细化初始场 |
| 4. 模型运行 | ✅ 可执行 | `3DWET/build/getm/getm_cartesian` | 读取 12 个输入文件，输出 3 个 NetCDF |
| 5. 结果输出 | ✅ 已实现 | `3DWET/scripts/theoretical_lake/` | 可视化（水平、垂向、3D） |
| 6. 率定校验 | ⏳ 待开发 | — | 点位对比、自动调参 |

---

## 二、Git 仓库中的文件位置

仓库地址：`https://github.com/dinod520/GETM-FABM-WET.git`

### 提交到 Git 的（代码、文档、模板）

```
GETM-FABM-WET/
├── .gitignore                              # 忽略规则
└── 3DWET/
    ├── preprocessor/                       # Module 1 源码 ✅在 Git
    │   ├── __init__.py
    │   ├── lake_config.py                  # 核心数据类（LakeConfig）
    │   ├── generate_bathymetry.py          # 生成 bathymetry.nc
    │   ├── generate_rivers.py              # 生成 riverinfo.dat + rivers.nc
    │   ├── generate_meteo.py               # 生成 meteo.nc + meteo_input.txt
    │   ├── generate_initial_conditions.py   # 生成 fabm_init.nc
    │   ├── validate_inputs.py             # 验证所有文件格式
    │   ├── run_preprocess.py               # 主入口（命令行）
    │   └── examples/
    │       └── ideal_lake.yaml             # 示例湖泊配置 ✅
    │
    ├── model_builder/                      # Module 2 源码 ✅在 Git
    │   ├── __init__.py
    │   ├── build_configs.py                # 生成 5 个短配置文件
    │   ├── build_fabm_yaml.py              # 生成 fabm.yaml
    │   ├── assemble_case.py                # 主入口（命令行）
    │   └── templates/
    │       └── fabm.yaml.template          # fabm.yaml 模板（1146 行）
    │
    ├── scripts/
    │   └── theoretical_lake/               # 可视化脚本 ✅在 Git
    │       ├── visualize_yilong.py          # 2D 图（Y01-Y06）
    │       └── visualize_yilong_3d_full.py  # 3D 图（Z01-Z07）
    │
    ├── src/                                # Fortran 源码 ✅在 Git
    │   ├── getm/  gotm/  fabm/  wet/
    │   └── flexout/  stim/  fortran-yaml/
    │
    ├── build/                              # 编译产物 ❌不在 Git（.gitignore）
    │   └── getm/getm_cartesian             # 编译好的可执行文件
    │
    ├── docs/                               # 文档 ✅在 Git
    │   └── 3DWET_WORKFLOW_GUIDE.md         # 本文件
    │
    └── case/                               # 案例目录
        ├── Yilong/                         # 异龙湖（含真实输入） ✅部分在 Git
        │   ├── fabm.yaml                   # ✅配置文件在 Git
        │   ├── getm.inp                    # ✅
        │   ├── figures_cloud/              # ✅图表+日志在 Git（用于同步）
        │   ├── *.nc                        # ❌数据文件不在 Git（.gitignore）
        │   └── run.log                    # ❌日志不在 Git
        └── IdealLake/                      # 理想化测试湖泊 ❌不在 Git（自动生成）
```

### .gitignore 关键规则

| 入 Git ✅ | 不入 Git ❌ |
|----------|------------|
| Python 源码（*.py） | 数据文件（*.nc） |
| YAML 配置（*.yaml） | 运行日志（*.log, run.log） |
| 文档（*.md） | 编译产物（build/, install_*/） |
| 模板文件（*.template） | Python 缓存（__pycache__/） |
| PNG 图片（figures/, figures_cloud/） | 临时调试文件 |

---

## 三、具体运行方式（端到端 3 步）

假设要为湖泊 "MyLake" 建模并运行：

### 步骤 1：填写湖泊配置文件

复制 `preprocessor/examples/ideal_lake.yaml`，改成你的湖泊参数：

```yaml
# my_lake.yaml
lake_name: "MyLake"
runid: "MYLAKE"
nx: 20            # 东西方向网格数
ny: 6             # 南北方向网格数
dx: 500.0         # 网格尺寸（米）
dy: 500.0
avg_depth: 3.5    # 平均水深
max_depth: 7.0
shape: "oval"     # 湖泊形状

start_date: "2020-01-01"
end_date: "2020-12-31"
timestep: 30.0

rivers:
  - name: "INFL1"
    edge: "west"
    flow_type: "inflow"
    base_flow: 2.0
    nh4: 0.20
    no3: 1.0
    po4: 0.04
  - name: "OUTFL"
    edge: "east"
    flow_type: "outflow"
    base_flow: 0.0

case_dir: "case/MyLake"
```

**字段说明**（LakeConfig 完整字段见 `preprocessor/lake_config.py`）：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `lake_name` | str | "MyLake" | 湖泊名（用于标题） |
| `runid` | str | "MYLAKE" | GETM 运行 ID（大写，≤8 字符） |
| `nx`, `ny` | int | 20, 6 | 网格数 |
| `dx`, `dy` | float | 500.0 | 网格尺寸（m） |
| `lat0`, `lon0` | float | 30.0, 120.0 | 湖泊中心经纬度 |
| `avg_depth` | float | 3.5 | 平均水深（m） |
| `max_depth` | float | 7.0 | 最大水深（m） |
| `shape` | str | "oval" | 形状：oval/rectangular/elliptical |
| `n_sigma` | int | 10 | σ 层数 |
| `start_date`, `end_date` | str | 2020-01-01, 2020-12-31 | 模拟时段 |
| `timestep` | float | 30.0 | 时间步长（秒） |
| `rivers` | list | [] | 河流列表（见 RiverConfig） |
| `trophic_state` | str | "eutrophic" | 营养状态 |
| `diatoms_init` 等 | float | 0.30 等 | 各生物类群初始生物量 |
| `macrophyte_biomass` | float | 30.0 | 大型植物初始生物量（gDW/m²） |

### 步骤 2：生成全部 12 个输入文件

```bash
cd /workspace/GETM-FABM-WET/3DWET

# 步骤 2a：Module 1 - 生成 6 个数据文件
python3 -m preprocessor.run_preprocess -c my_lake.yaml
# 输出：
#   case/MyLake/bathymetry.nc
#   case/MyLake/riverinfo.dat
#   case/MyLake/rivers.nc
#   case/MyLake/meteo.nc
#   case/MyLake/meteo_input.txt
#   case/MyLake/fabm_init.nc

# 步骤 2b：Module 2 - 生成 6 个配置文件
python3 -m model_builder.assemble_case -c my_lake.yaml
# 输出：
#   case/MyLake/getm.inp
#   case/MyLake/getm_fabm.inp
#   case/MyLake/gotmturb.nml
#   case/MyLake/gotm_fabm.yaml
#   case/MyLake/output.yaml
#   case/MyLake/fabm.yaml
```

### 步骤 3：运行模型

```bash
cd /workspace/GETM-FABM-WET/3DWET/case/MyLake
export OMP_NUM_THREADS=4                                  # OpenMP 4 线程
/workspace/GETM-FABM-WET/3DWET/build/getm/getm_cartesian  # 可执行文件路径
```

运行结束后，看到 `getm: Completed` 即成功。

---

## 四、模型输入文件（12 个）的格式与作用

进入 `case/MyLake/` 目录后，所有文件按类型分两组：

### A. 数据文件（Module 1 生成，6 个）

| 文件名 | 格式 | 内容 | 作用 |
|--------|------|------|------|
| `bathymetry.nc` | NetCDF4 | 网格坐标 lonc/latc + 水深 bathymetry | 湖底地形 |
| `riverinfo.dat` | 文本 | 河流网格位置（1-indexed） | 告诉 GETM 河流在哪个格子 |
| `rivers.nc` | NetCDF4 | 每条河的流量、温度、营养盐时间序列 | 河流边界条件 |
| `meteo.nc` | NetCDF4 | 风、温度、降水、蒸发、气压、湿度、云量 | 气象强迫 |
| `meteo_input.txt` | 文本 | 一行 `meteo.nc` | 指向 meteo.nc 的指针 |
| `fabm_init.nc` | NetCDF4 | macrophytes_sD（大型植物生物量） | 大型植物空间分布初始场 |

**bathymetry.nc 关键变量**：
- `bathymetry(y, x)`: 水深（m），正值=水，-9999=陆地
- `lonc(y, x)`, `latc(y, x)`: 经纬度
- `x(x)`, `y(y)`: UTM 坐标（m）

**rivers.nc 关键变量**（每条河一组）：
- `{name}(time)`: 流量（m³/s），正=入流，负=出流
- `{name}_temp(time)`: 水温（°C）
- `{name}_nh4/no3/po4/doc/poc(time)`: 营养盐（g/m³）

**meteo.nc 关键变量**：
- `t2(time, lat, lon)`: 2m 气温（°C）
- `u10`, `v10`: 10m 风速（m/s）
- `precip`, `evap`: 降水/蒸发率（m/s，evap 负值=失水）
- `slp`, `rh`, `tcc`: 气压、湿度、云量

### B. 配置文件（Module 2 生成，6 个）

| 文件名 | 格式 | 内容 | 作用 |
|--------|------|------|------|
| `getm.inp` | namelist | 网格、时间步、模拟时段、IO 选项 | GETM 主配置 |
| `getm_fabm.inp` | namelist | fabm_init_method=2 等 | GETM-FABM 耦合配置 |
| `gotmturb.nml` | namelist | k-ε 湍流模型参数 | 湍流参数 |
| `gotm_fabm.yaml` | YAML | ode_method=10（Patankar）等 | FABM 数值参数 |
| `output.yaml` | YAML | time_step=1（每天输出） | FABM 输出配置 |
| `fabm.yaml` | YAML | 17 个模型实例 + 1146 行 PCLake 参数 | **生态模型核心** |

**fabm.yaml 关键字段**（最重要的文件）：
```yaml
instances:
  abiotic_water:           # 水体营养盐（NH4/NO3/PO4/SiO2/O2）
  abiotic_sediment:        # 沉积物
  bot_pel_interface:       # 底水界面
  burial:                  # 埋藏
  sediment_exchange:       # 沉积物交换
  POM:  DOM:  humus:       # 有机质
  macrophytes:             # 大型植物（注意 _PV 初值不能用 0）
  diatoms:  greens:  cyanobacteria:    # 浮游植物
  cladocerans:  copepods:               # 浮游动物
  zoobenthos:                            # 底栖动物
  JuFish:  AdFish:  PiscFish:           # 鱼类
```

⚠️ **重要**：macrophytes 的 `_PV` 变量（sD_PV, sN_PV, sP_PV, sC_PV）初值不能用 0，
否则 Patankar 求解器会报错。源码默认值：1.0, 0.002, 0.02, 0.4。

---

## 五、模型输出结果（4 个文件）

模型运行完成后，在 `case/MyLake/` 下生成：

| 文件 | 格式 | 大小（365 天模拟） | 内容 |
|------|------|------------------|------|
| `{RUNID}.3d.nc` | **NetCDF3 Classic** | ~2 GB | 3D 水动力+生态（temp, salt, u, v, tke, eps, num, nuh） |
| `{RUNID}.2d.nc` | NetCDF3 Classic | ~2 MB | 2D 水位 elev、流速 u/v |
| `output.nc` | NetCDF3 Classic | ~1 GB | FABM 生态变量（108 个 state variable） |
| `run.log` | 文本 | 1-2 GB | 运行日志（含 Patankar 警告） |

**RUNID** 来自 `lake_config.yaml` 的 `runid` 字段（如 `YILONG`、`IDEALLAKE`、`MYLAKE`）。

### 输出文件存储位置

```
3DWET/case/{lake_name}/
├── {RUNID}.2d.nc        ← 水位/2D 流速
├── {RUNID}.3d.nc        ← 3D 水动力+生态
├── output.nc            ← FABM 生态（每个变量都有时间序列）
└── run.log              ← 日志（.gitignore 忽略，不进 Git）
```

⚠️ 这些文件**不进 Git**（在 .gitignore 里）。若要同步到本地，需复制到 `figures_cloud/` 目录后再 commit。

### output.nc 主要变量（108 个状态变量）

| 类别 | 变量名示例 | 单位 |
|------|-----------|------|
| 营养盐 | abiotic_water_sNH4W, sNO3W, sPO4W, sO2W | g/m³ |
| 浮游植物 | diatoms_sDW, greens_sDW, cyanobacteria_sDW | gDW/m³ |
| 浮游动物 | cladocerans_sD, copepods_sD | gDW/m³ |
| 鱼类 | JuFish_sD, AdFish_sD, PiscFish_sD | gDW/m³ |
| 大型植物 | macrophytes_sD | gDW/m² |
| 有机质 | POM_sDW, DOM_sDW | g/m³ |
| 光照限制 | diatoms_aLLim, greens_aLLim | 0-1 |

---

## 六、结果查看方式（3 种）

### 方式 1：ncdump 命令行（快速检查）

```bash
# 查看 NetCDF 头（变量列表、维度）
ncdump -h case/MyLake/output.nc

# 查看某个变量
ncdump -v diatoms_sDW case/MyLake/output.nc | head -20
```

⚠️ **已知问题**：GETM 输出 NetCDF3 Classic 格式，文件头的 `numrecs`（记录数）可能是 0，
即使数据已写入。需要先 patch：

```bash
# Python 一行修复 numrecs
python3 -c "
import struct
with open('output.nc','r+b') as f:
    f.seek(4); f.write(struct.pack('>I', 365))
"
```

### 方式 2：Python 脚本（推荐，灵活提取数据）

```python
import netCDF4 as nc
import numpy as np

ds = nc.Dataset('output.nc', 'r')

# 查看所有变量
print(list(ds.variables.keys()))

# 读取硅藻生物量时间序列 (time, z, y, x)
diatoms = ds.variables['diatoms_sDW'][:]
print(f'shape: {diatoms.shape}')           # (365, 10, 6, 20)
print(f'range: {np.nanmin(diatoms):.3f} ~ {np.nanmax(diatoms):.3f}')

# 表面层空间平均
surf_mean = np.nanmean(diatoms[:, 0, :, :], axis=(1,2))
print(f'day 1: {surf_mean[0]:.3f}, day 365: {surf_mean[-1]:.3f}')

ds.close()
```

### 方式 3：现成可视化脚本（生成 PNG）

```bash
# 异龙湖专用（生成 Y01-Y06 + stats_summary.txt）
cd /workspace/GETM-FABM-WET/3DWET
python3 scripts/theoretical_lake/visualize_yilong.py

# 3D 可视化（生成 Z01-Z07）
python3 scripts/theoretical_lake/visualize_yilong_3d_full.py
```

输出到 `case/{lake}/figures/` 和 `case/{lake}/figures_3d/`：

| 文件 | 内容 |
|------|------|
| `Y01_bathymetry.png` | 湖底地形 + 河流位置 |
| `Y02_phytoplankton_timeseries.png` | 浮游植物时间序列 |
| `Y03_phytoplankton_spatial.png` | 空间分布快照 |
| `Y04_nutrients_temp.png` | 营养盐+温度+水位 |
| `Y05_vertical_profile.png` | 垂向 σ 层剖面 |
| `Y06_cascade_check.png` | 食物链完整性 |
| `Z01-Z07` | 3D 透视、12 个月演变、垂向热图 |
| `stats_summary.txt` | 各变量 min/max/首日/末日统计 |

---

## 七、调用位置速查表

| 操作 | 命令/位置 |
|------|---------|
| **填湖泊配置** | 编辑 `preprocessor/examples/{lake}.yaml` |
| **生成数据文件** | `python3 -m preprocessor.run_preprocess -c {lake}.yaml` |
| **生成配置文件** | `python3 -m model_builder.assemble_case -c {lake}.yaml` |
| **运行模型** | `cd case/{lake} && ../build/getm/getm_cartesian` |
| **可视化** | `python3 scripts/theoretical_lake/visualize_yilong.py`（需改路径） |
| **检查 NetCDF** | `ncdump -h case/{lake}/output.nc` |
| **检查 Patankar 错误** | `grep -c "Error:" case/{lake}/run.log` |
| **同步到本地** | 把图片复制到 `figures_cloud/`，`git add && git commit && git push` |
| **可执行文件位置** | `/workspace/GETM-FABM-WET/3DWET/build/getm/getm_cartesian` |
| **输出 NetCDF 位置** | `3DWET/case/{lake}/{RUNID}.3d.nc`、`output.nc` 等 |
| **配置模板** | `3DWET/model_builder/templates/fabm.yaml.template` |
| **示例配置** | `3DWET/preprocessor/examples/ideal_lake.yaml` |
| **本文档** | `3DWET/docs/3DWET_WORKFLOW_GUIDE.md` |

---

## 八、典型工作流（云端跑、本地查看）

```
[云端 TRAE Linux]                              [本地 Windows]

1. 编辑 lake_config.yaml
       ↓
2. python -m preprocessor.run_preprocess
3. python -m model_builder.assemble_case
       ↓
4. cd case/{lake} && getm_cartesian
       ↓
5. python visualize_yilong.py   →  PNG 图片
       ↓
6. cp figures/* figures_cloud/
7. git add && git commit && git push
                          ↓
                          git pull origin main
                          ↓
                          查看 figures_cloud/*.png
```

---

## 九、两个示例案例对比

| | IdealLake（测试用） | Yilong（真实湖泊） |
|---|---|---|
| 配置文件 | `preprocessor/examples/ideal_lake.yaml` | `case/Yilong/fabm.yaml`（手工） |
| 网格 | 15×5（小，快） | 28×8（500m） |
| 模拟时长 | 3 天（快速验证） | 365 天（完整 2020 年） |
| 运行时间 | ~1 分钟 | ~2 小时 15 分钟 |
| 输出大小 | ~6 MB | ~3.2 GB |
| 用途 | 验证标准化流程是否跑通 | 真实研究 |
| 在 Git 中 | 仅配置代码，输出不入 Git | figures_cloud/ 图表入 Git |

---

## 十、常见问题排查

### 1. Patankar 求解器错误

**症状**：`run.log` 中出现 `Error: state variable X is zero and has negative derivative!`

**原因**：macrophytes 的 `_PV` 变量初值设为 0

**解决**：检查 `fabm.yaml` 中 macrophytes 的 initialization，确保 sD_PV/sN_PV/sP_PV/sC_PV 用源码默认值（1.0/0.002/0.02/0.4）

### 2. meteo EOF 错误

**症状**：`FATAL ERROR: Reached eof in: meteo_input.txt`

**原因**：meteo.nc 时间维度不够（GETM 需要数据覆盖到 stop 之后）

**解决**：preprocessor 已自动多生成 1 天数据（n_days + 1）

### 3. numrecs=0 问题

**症状**：`ncdump -h output.nc` 显示 `time = UNLIMITED ; // (0 currently)`

**原因**：GETM NetCDF3 Classic 格式 bug，退出时未写入记录数

**解决**：用 patch_numrecs 修复（可视化脚本已内置）

### 4. 字体渲染问题

**症状**：图表中文显示为方块

**解决**：可视化脚本已全英文化，不再有此问题
