# 3DWET 三维水动力-水质-食物网模型

## 模型使用说明

**版本**: v1.3 (真实骆马湖案例测试通过)
**日期**: 2026-06-30

---

## 目录

1. [快速开始](#一快速开始)
2. [系统要求](#二系统要求)
3. [目录结构](#三目录结构)
4. [编译模型](#四编译模型)
5. [运行模型](#五运行模型)
6. [配置模型](#六配置模型)
7. [输入数据](#七输入数据)
8. [输出结果](#八输出结果)
9. [可视化](#九可视化)
10. [常见问题](#十常见问题)
11. [Bug 修复记录](#十一bug-修复记录)

---

## 一、快速开始

### 1.1 三步运行模型

```bash
# 1. 编译模型
cd 3DWET
bash scripts/build_model.sh

# 2. 运行模拟
cd case
../install/bin/getm_cartesian

# 3. 可视化结果
python3 ../scripts/visualize.py
```

### 1.2 首次使用检查清单

- [ ] 已安装 GCC 13 和 gfortran 13
- [ ] 已安装 CMake
- [ ] 已安装 NetCDF-Fortran
- [ ] 已安装 Python 3 + matplotlib + netCDF4
- [ ] case 目录中包含 `gotm_fabm.yaml`（FABM 激活必需）
- [ ] fabm.F90 中的 DEBUG 输出已被移除（编译脚本自动处理）

---

## 二、系统要求

### 2.1 编译环境

| 软件 | 最低版本 | 推荐版本 |
|------|----------|----------|
| GCC (C编译器) | 9.0 | 13.0+ |
| gfortran (Fortran编译器) | 9.0 | 13.0+ |
| CMake | 3.10 | 3.20+ |
| NetCDF-Fortran | 4.5 | 4.9+ |
| Make | 3.8 | 4.0+ |

### 2.2 可视化环境

| 软件 | 最低版本 |
|------|----------|
| Python | 3.8 |
| numpy | 1.20 |
| matplotlib | 3.3 |
| netCDF4 | 1.5 |

### 2.3 操作系统

- **Linux**: Ubuntu 20.04+, CentOS 7+, 任意主流 Linux 发行版
- **Windows**: WSL 2 (推荐), Git Bash, Cygwin
- **macOS**: 10.15+ (需安装 Homebrew 包管理器)

### 2.4 WSL 环境安装（Windows 用户）

```bash
# 在 WSL Ubuntu 中安装依赖
sudo apt-get update
sudo apt-get install -y gcc-13 gfortran-13 cmake
sudo apt-get install -y libnetcdf-dev libnetcdff-dev
sudo apt-get install -y python3 python3-pip
pip3 install numpy matplotlib netCDF4
```

---

## 三、目录结构

```
3DWET/
├── src/                        # 源代码目录
│   ├── fabm/                   # FABM 生物地球化学框架
│   │   ├── src/
│   │   │   ├── fabm.F90        # FABM 核心模块
│   │   │   ├── models/         # 生态模型库
│   │   │   ├── drivers/        # 驱动程序
│   │   │   └── yaml/           # YAML 解析
│   │   └── CMakeLists.txt
│   │
│   ├── getm/                   # GETM 水动力模型
│   │   ├── src/
│   │   │   ├── 2d/             # 二维水动力
│   │   │   ├── 3d/             # 三维水动力
│   │   │   │   ├── getm_fabm.F90   # FABM 耦合接口
│   │   │   │   ├── m3d.F90         # 三维主模块
│   │   │   │   └── ...
│   │   │   ├── meteo/          # 气象模块
│   │   │   ├── ncdf/           # NetCDF I/O
│   │   │   └── ...
│   │   └── CMakeLists.txt
│   │
│   ├── gotm/                   # GOTM 湍流模型
│   │   ├── src/
│   │   │   ├── fabm/           # FABM 耦合接口
│   │   │   ├── turbulence/     # 湍流模型
│   │   │   ├── meanflow/       # 平均流
│   │   │   └── ...
│   │   └── CMakeLists.txt
│   │
│   └── wet/                    # WET 全生态系统模型
│       ├── src/
│       │   ├── wet_model_library.F90   # 模型库注册
│       │   ├── abiotic_water.F90       # 非生物水质
│       │   ├── phytoplankton.F90       # 浮游植物
│       │   ├── zooplankton.F90         # 浮游动物
│       │   ├── macrophytes.F90         # 沉水植物
│       │   ├── zoobenthos.F90          # 底栖生物
│       │   ├── fish.F90                # 鱼类
│       │   ├── om_pool.F90             # 有机质池
│       │   └── ...
│       ├── testcases/                  # WET 测试用例
│       └── CMakeLists.txt
│
├── patches/                    # Bug 修复补丁
│   ├── fish_v2_patched.F90          # Fish check_state 修复
│   ├── gotm_fabm_itime_fixed.F90    # gotm_fabm itime 修复
│   ├── getm_fabm_v2_patched.F90     # getm_fabm v2 补丁
│   └── om_pool_patched.F90          # om_pool 修复
│
├── scripts/                    # 脚本目录
│   ├── build_model.sh              # 编译脚本
│   └── visualize.py                # 可视化脚本
│
├── case/                       # 测试用例（罗目湖）
│   ├── getm.inp                    # GETM 配置
│   ├── getm_fabm.inp               # FABM 耦合配置
│   ├── fabm.yaml                   # 生态模型配置
│   ├── gotmturb.nml                # 湍流模型配置
│   ├── output.yaml                 # 输出配置
│   ├── bathymetry.nc               # 地形数据
│   ├── meteo.nc                    # 气象数据
│   ├── rivers.nc                   # 河流数据
│   ├── riverinfo.dat               # 河流信息
│   └── figures/                    # 可视化结果
│
├── build/                      # 编译目录（编译后生成）
│   ├── fabm/                        # FABM 编译文件
│   └── getm/                        # GETM 编译文件
│
├── install/                    # 安装目录（编译后生成）
│   ├── bin/
│   │   └── getm_cartesian       # 可执行文件
│   └── fabm/                     # FABM 库文件
│
└── docs/                       # 文档目录
    ├── MODEL_MODULES.md            # 模块详细说明
    └── USER_GUIDE.md               # 使用说明（本文件）
```

---

## 四、编译模型

### 4.1 使用编译脚本（推荐）

```bash
cd 3DWET
bash scripts/build_model.sh
```

编译脚本会自动：
1. 备份原始源文件
2. 应用所有 Bug 修复补丁
3. 编译 FABM + WET
4. 编译 GETM + FABM
5. 安装到 `install/` 目录
6. 恢复原始源文件

### 4.2 手动编译

#### 步骤 1: 编译 FABM + WET

```bash
mkdir -p build/fabm
cd build/fabm

cmake ../../src/fabm/src \
    -DCMAKE_INSTALL_PREFIX=../../install/fabm \
    -DFABM_HOST=gotm \
    -DFABM_EMBED_VERSION=OFF \
    -DFABM_WET_BASE=../../src/wet \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_FLAGS_RELEASE="-O2"

make -j4
make install
```

#### 步骤 2: 编译 GETM + FABM

```bash
mkdir -p build/getm
cd build/getm

cmake ../../src/getm/src \
    -DCMAKE_INSTALL_PREFIX=../../install \
    -DGOTM_BASE=../../src/gotm \
    -DFABM_PREFIX=../../install/fabm \
    -DGETM_USE_FABM=ON \
    -DGETM_USE_CARTESIAN=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_FLAGS_RELEASE="-O2 -U_GOTM_FABM_NML_"

make -j4
make install
```

### 4.3 编译选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `CMAKE_BUILD_TYPE` | 编译类型 | Release |
| `CMAKE_Fortran_FLAGS_RELEASE` | Fortran 编译标志 | -O2 |
| `GETM_USE_FABM` | 启用 FABM 耦合 | ON |
| `GETM_USE_CARTESIAN` | 笛卡尔坐标模式 | ON |
| `FABM_WET_BASE` | WET 模型路径 | (必须设置) |

### 4.4 常见编译错误

**错误: NetCDF 找不到**
```bash
# 解决方案：设置 NetCDF 路径
export NETCDF=/path/to/netcdf
```

**错误: gfortran 版本太低**
```bash
# 解决方案：使用 GCC 13
export CC=gcc-13
export FC=gfortran-13
```

---

## 五、运行模型

### 5.1 基本运行

```bash
cd case
../install/bin/getm_cartesian
```

### 5.2 后台运行

```bash
cd case
nohup ../install/bin/getm_cartesian > run.log 2>&1 &
```

### 5.3 查看运行日志

```bash
# 实时查看
tail -f run.log

# 查看最后 100 行
tail -100 run.log

# 搜索错误
grep -i error run.log
```

### 5.4 运行时间估计

| 模拟时长 | 网格大小 | 层数 | 估计时间 |
|----------|----------|------|----------|
| 1 天 | 44×54 | 6 | ~1 分钟 |
| 30 天 | 44×54 | 6 | ~26 分钟 |
| 365 天 | 44×54 | 6 | ~5 小时 |

> **注意**: 以上时间为 FABM 食物网模块启用时的估计。FABM 占总计算时间的约 93%。2026-06-30 实测：30 天模拟总计时 1554.58 秒（约 26 分钟），FABM 计时 1441.27 秒（93.59%）。

### 5.5 检查运行状态

```bash
# 检查进程是否在运行
ps aux | grep getm_cartesian

# 检查输出文件是否在更新
ls -lh case/*.nc
```

---

## 六、配置模型

### 6.1 模拟时间设置

编辑 `case/getm.inp`:

```fortran
&time
    timestep = 30.0              ! 时间步长 (秒)
    start = '2020-01-01 00:00:00' ! 开始时间
    stop = '2020-01-31 00:00:00'  ! 结束时间 (30天)
/
```

### 6.2 垂直层数设置

编辑 `case/getm.inp`:

```fortran
&m3d
    M = 10    ! 垂直层数 (sigma层数)
/

&domain
    maxdepth = 25.0   ! 最大水深 (m)
    kdum = 5          ! 底部层数标记
/
```

> **重要说明**: 实际输出的 sigma 层数由 `kdum` 控制（层数 = kdum + 1），而不是由 `M` 控制。当前配置 `kdum=5` 会生成 6 层 sigma（-1.0, -0.8, -0.6, -0.4, -0.2, 0.0）。如需 10 层 sigma，需设置 `kdum=9`。

### 6.3 生态模块配置

编辑 `case/fabm.yaml` 启用或禁用模块。

**启用/禁用鱼类模块**:
```yaml
fabm:
  instances:
    PiscFish:
      model: wet/fish
      parameters:
        qStage: 0  # 0=禁用阶段结构, 1+=启用
```

**启用/禁用沉水植物**:
```yaml
fabm:
  instances:
    macrophytes:
      model: wet/macrophytes
      parameters:
        # 沉水植物参数
```

### 6.4 输出配置

编辑 `case/output.yaml` 设置输出变量和频率。

示例 - 输出水温、水位、叶绿素：
```yaml
netcdf:
  output:
    time_average:
      interval: P1D    # 日平均输出
      variables:
        - temp         # 水温
        - elev         # 水位
        - chlorophyll  # 叶绿素
```

---

## 七、输入数据

### 7.1 输入文件列表

| 文件 | 格式 | 必需 | 说明 |
|------|------|------|------|
| `bathymetry.nc` | NetCDF | ✅ | 湖底地形 |
| `meteo.nc` | NetCDF | ✅ | 气象强迫数据 |
| `rivers.nc` | NetCDF | ✅ | 河流入流数据 |
| `riverinfo.dat` | ASCII | ✅ | 河流位置信息 |
| `gotm_fabm.yaml` | YAML | ✅ | FABM 激活配置（缺失会导致 FABM 不运行） |
| `fabm.yaml` | YAML | ✅ | 生态模型配置 |
| `getm.inp` | NAMELIST | ✅ | GETM 水动力配置 |
| `getm_fabm.inp` | NAMELIST | ✅ | FABM 耦合配置 |
| `gotmturb.nml` | NAMELIST | ✅ | 湍流模型配置 |
| `output.yaml` | YAML | ✅ | 输出配置 |

### 7.2 地形数据 (bathymetry.nc)

**必需变量**:
- `bathymetry`: 水深 (m)，正值表示水深

**查看地形信息**:
```bash
ncdump -h bathymetry.nc
```

### 7.3 气象数据 (meteo.nc)

**必需变量**:
- `t2m`: 2米气温 (°C)
- `u10`: 10米风速 x 分量 (m/s)
- `v10`: 10米风速 y 分量 (m/s)
- `msl`: 海平面气压 (Pa)
- `ssrd`: 地表向下短波辐射 (W/m²)
- `strd`: 地表向下长波辐射 (W/m²)

### 7.4 河流数据 (rivers.nc)

**必需变量**:
- `discharge`: 流量 (m³/s)
- `temp`: 水温 (°C)
- 各营养盐浓度变量

### 7.5 河流信息 (riverinfo.dat)

文本格式，每条河流一行，包含：
- 河流名称
- 网格位置 (i, j)
- 方向

---

## 八、输出结果

### 8.1 输出文件

| 文件 | 说明 |
|------|------|
| `*.2d.nc` | 二维输出（水位、水深平均变量） |
| `*.3d.nc` | 三维输出（温度、流速、生态变量） |

### 8.2 查看输出文件

```bash
# 查看文件信息
ncdump -h output.3d.nc | head -50

# 查看所有变量
ncdump -h output.3d.nc | grep "float "

# 查看时间坐标
ncdump -v time output.3d.nc
```

### 8.3 主要输出变量

#### 水动力变量

| 变量名 | 单位 | 说明 |
|--------|------|------|
| `elev` | m | 水位 |
| `temp` | °C | 水温 |
| `uu` | m/s | x方向流速 |
| `vv` | m/s | y方向流速 |
| `w` | m/s | 垂向流速 |
| `tke` | m²/s² | 湍动能 |

#### 水质变量

| 变量名 | 单位 | 说明 |
|--------|------|------|
| `abiotic_water_sNH4W` | gN/m³ | 氨氮 |
| `abiotic_water_sNO3W` | gN/m³ | 硝氮 |
| `abiotic_water_sPO4W` | gP/m³ | 磷酸盐 |
| `abiotic_water_sO2W` | gO₂/m³ | 溶解氧 |

#### 生物变量

| 变量名 | 单位 | 说明 |
|--------|------|------|
| `cyanobacteria_sDW` | gDW/m³ | 蓝藻干重 |
| `diatoms_sDW` | gDW/m³ | 硅藻干重 |
| `greens_sDW` | gDW/m³ | 绿藻干重 |
| `cladocerans_sD` | gDW/m³ | 枝角类干重 |
| `copepods_sD` | gDW/m³ | 桡足类干重 |
| `macrophytes_sD_PV` | gDW/m² | 沉水植物干重 |
| `zoobenthos_sD_PV` | gDW/m² | 底栖生物干重 |
| `PiscFish_sD` | gDW/m³ | 食鱼性鱼干重 |
| `AdFish_sD` | gDW/m³ | 底栖性成鱼干重 |
| `JuFish_sD` | gDW/m³ | 浮游性幼鱼干重 |

> **注意**: 浮游动物和鱼类变量后缀为 `_sD`（不是 `_sDW`）；沉水植物和底栖生物为 `_sD_PV`（pelagic var）。鱼类是 3D 变量（gDW/m³），不是面积变量。

---

## 九、可视化

### 9.1 使用可视化脚本

```bash
cd case
python ../scripts/visualize.py
```

### 9.2 生成的图

| 编号 | 图名 | 内容 |
|------|------|------|
| 01 | 湖泊地形和网格 | 水深分布、河流入口位置 |
| 02 | 水动力 | 水位、水温、流速 |
| 03 | 水质营养盐 | NH4, NO3, PO4, O2 |
| 04 | 浮游植物 | 蓝藻、硅藻、绿藻空间分布 |
| 05 | 浮游动物 | 枝角类、桡足类空间分布 |
| 06 | 沉水植物和底栖生物 | 生物量空间分布 |
| 07 | 鱼类空间分布 | 三种鱼类生物量 |
| 08 | 食物网总览 | 所有营养级生物量时间序列 |
| 09 | 垂直剖面 | 湖心不同日期的垂直分布 |
| 10 | 深度-时间热力图 | 湖心变量的深度-时间演化 |
| 11 | 鱼类垂直分布 | 鱼类的深度-时间分布 |

### 9.3 自定义可视化

使用 Python + netCDF4 + matplotlib 自定义绘图：

```python
import netCDF4 as nc
import matplotlib.pyplot as plt

# 读取数据
ds = nc.Dataset('output.3d.nc')
temp = ds.variables['temp'][:]
time = ds.variables['time'][:]
ds.close()

# 绘图
plt.figure()
plt.plot(time, temp[:, 0, 0, 0])  # 表面水温时间序列
plt.xlabel('Time')
plt.ylabel('Temperature (°C)')
plt.savefig('temp_timeseries.png')
```

---

## 十、常见问题

### 10.1 模型崩溃/段错误

**可能原因 1**: 初始条件不合理
- 检查 `fabm.yaml` 中的初始值
- 尝试使用更小的初始值

**可能原因 2**: 时间步长太大
- 减小 `getm.inp` 中的 `timestep`

**可能原因 3**: 河流水量过大
- 检查 `rivers.nc` 中的流量数据

### 10.2 结果出现 NaN

**可能原因**: 数值不稳定
- 减小时间步长
- 检查初始条件
- 增加扩散系数

### 10.3 编译失败

**错误: `fatal error: netcdf.inc: No such file or directory`**
```bash
# 安装 netcdf-fortran
sudo apt-get install libnetcdff-dev
```

**错误: `undefined reference to nf90_*`**
```bash
# 确认 NetCDF Fortran 库已安装
nf-config --flibs
```

### 10.4 运行速度慢

**优化方法**:
- 使用 Release 编译 (-O2)
- 减小网格分辨率
- 增大时间步长（确保数值稳定）
- 使用并行编译（make -j4）
- 确保 fabm.F90 中的 DEBUG 输出已被移除（编译脚本自动处理）

### 10.5 FABM 未运行（getm_fabm 调用次数为 0）

**症状**: 模型运行完成但 FABM 模块未激活，日志显示：
```
WARNING: gotm_fabm.yaml not found.
WARNING: will continue with fabm_calc=False.
```

**解决方案**: 确保 `case/` 目录中包含 `gotm_fabm.yaml` 文件。

`gotm_fabm.yaml` 内容示例：
```yaml
fabm:
  use: true
  freshwater_impact: true
  repair_state: true
  feedbacks:
    shade: false
    albedo: true
    surface_drag: true
  numerics:
    ode_method: 1
    split_factor: 1
    w_adv_discr: 6
    cnpar: 1.0
```

### 10.6 日志文件异常庞大（数百万行）

**症状**: 运行日志文件增长到数百万甚至上千万行，模型运行极其缓慢。

**原因**: `fabm.F90` 源代码中包含大量 `write(0,*) 'DEBUG: ...'` 调试输出语句。

**解决方案**: 编译脚本 `build_model.sh` 已自动调用 `scripts/remove_debug.py` 移除所有 DEBUG 输出。如需手动处理：
```bash
python3 scripts/remove_debug.py
```

### 10.7 可视化脚本找不到输出文件

**症状**: `FileNotFoundError: LUOMAHU_WET.3d.nc`

**原因**: 可视化脚本中的路径配置不正确。

**解决方案**: 可视化脚本已更新为使用相对路径。确保从 `case/` 目录运行：
```bash
cd case
python3 ../scripts/visualize.py
```

### 10.8 可视化出现 "Mean of empty slice" 警告

**症状**: 运行可视化脚本时出现多个 `RuntimeWarning: Mean of empty slice` 警告。

**原因**: 浅水区域（水深 < 0.5m）被 crit_depth 过滤为陆地，导致底层（sigma=-1）数据全为 NaN，计算平均值时出现空切片警告。

**影响**: 不影响可视化结果，图仍会正常生成，仅统计计算时忽略 NaN 值。

**解决方案**: 可忽略此警告。如需消除，可在 visualize.py 中添加 `import warnings; warnings.filterwarnings('ignore', category=RuntimeWarning)`。

### 10.9 垂直层数与配置不符

**症状**: `getm.inp` 中设置 `M=10`，但输出文件中 sigma 层数为 6。

**原因**: GETM 的 sigma 层数由 `kdum` 参数控制（层数 = kdum + 1），而不是由 `M` 控制。当前 `kdum=5` 生成 6 层 sigma。

**解决方案**: 如需 10 层 sigma，将 `kdum` 改为 9：
```fortran
&domain
    kdum = 9    ! 生成 10 层 sigma (-1.0 到 0.0，间隔 0.1)
/
```

---

## 十一、Bug 修复记录

### 已修复的 Bug

| Bug 编号 | 描述 | 补丁文件 | 影响模块 |
|----------|------|----------|----------|
| #1 | gotm_fabm itime 可选参数导致段错误 | `gotm_fabm_itime_fixed.F90` | GOTM-FABM 耦合 |
| #2 | fish check_state qStage=0 时数组越界 | `fish_v2_patched.F90` | WET 鱼类模块 |
| #3 | om_pool refractory POM 注册错误 | `om_pool_patched.F90` | WET 有机质池 |
| #4 | getm_fabm 耦合接口改进 | `getm_fabm_v2_patched.F90` | GETM-FABM 耦合 |
| #5 | fabm.F90 DEBUG 输出导致性能问题 | `remove_debug.py` (编译时自动) | FABM 核心 |
| #6 | gotm_fabm.yaml 缺失导致 FABM 不运行 | 已添加到 case 目录 | FABM 配置 |
| #7 | 文档中生物变量名错误（sDW 误写为 sDW_PV 等） | 文档已修正 | 文档 |
| #8 | 垂直层数配置说明不清（M vs kdum） | 文档已补充说明 | 文档 |
| #9 | Fortran netCDF 4.5.4 库反转维度顺序导致 meteo.nc 读取失败 (err=-57) | meteo.nc 变量维度改为 (time, lat, lon) | 气象数据读取 |
| #10 | GETM 异常终止导致 NetCDF3 输出文件 time 维度 numrecs=0 | 运行后用 patch_numrecs.py 修复 | 输出文件 |

### 应用补丁

所有补丁已在编译脚本中自动应用。如需手动应用：

```bash
# 应用 fish 模块补丁
cp patches/fish_v2_patched.F90 src/wet/src/fish.F90

# 应用 gotm_fabm 补丁
cp patches/gotm_fabm_itime_fixed.F90 src/gotm/src/fabm/gotm_fabm.F90
```

---

## 十二、技术支持

### 文档

- [模块详细说明](MODEL_MODULES.md) - 各模块的详细技术说明

### 官方资源

- GETM 官网: https://getm.eu/
- FABM 官网: https://fabm.net/
- GOTM 官网: https://gotm.net/

### 问题排查

1. 查看运行日志中的错误信息
2. 检查输入数据格式是否正确
3. 尝试简化配置（只启用核心模块）
4. 查看编译警告

---

**文档版本**: v1.3
**最后更新**: 2026-06-30
