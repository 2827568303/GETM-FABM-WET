# 3DWET 云端操作流程指南

> **目标读者**：合作者（首次使用云端环境运行 3DWET 模型的人员）
>
> **阅读本文后，你将能够**：在云端 Linux 环境中编译、运行 3DWET 模型，并生成可视化结果

---

## 目录

1. [前置条件](#1-前置条件)
2. [第一步：获取代码](#2-第一步获取代码)
3. [第二步：安装编译环境](#3-第二步安装编译环境)
4. [第三步：编译模型](#4-第三步编译模型)
5. [第四步：生成输入数据](#5-第四步生成输入数据)
6. [第五步：运行模型](#6-第五步运行模型)
7. [第六步：查看可视化结果](#7-第六步查看可视化结果)
8. [第七步：查看模型输出数据](#8-第七步查看模型输出数据)
9. [常见问题排查](#9-常见问题排查)
10. [日常开发工作流](#10-日常开发工作流)

---

## 1. 前置条件

### 1.1 你需要准备的东西

| 项目 | 说明 |
|------|------|
| GitHub 账号 | 需要有仓库访问权限（向仓库所有者申请） |
| SSH 密钥 或 Personal Access Token | 用于 Git 认证 |
| 云端 Linux 环境 | TRAE 云端环境、GitHub Codespaces、或云服务器均可 |
| 终端访问权限 | 能在 Linux 环境中执行命令 |

### 1.2 系统要求

- **操作系统**：Ubuntu 22.04 或更高（推荐 24.04）
- **内存**：最低 4GB，推荐 8GB
- **磁盘空间**：最低 2GB（代码 + 编译产物 + 运行数据）
- **网络**：能访问 GitHub

---

## 2. 第一步：获取代码

### 2.1 配置 Git 身份

如果是第一次使用 Git，设置你的用户名和邮箱：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

### 2.2 Clone 仓库

**方式 A：用 HTTPS + Token（最简单）**

```bash
cd /workspace
git clone https://github.com/dinod520/GETM-FABM-WET.git
```

输入用户名后，密码处填入 GitHub Personal Access Token（不是 GitHub 登录密码）。

**方式 B：用 SSH 密钥**

```bash
cd /workspace
git clone git@github.com:dinod520/GETM-FABM-WET.git
```

> 如果你还没有 SSH 密钥，运行 `ssh-keygen -t ed25519 -C "your_email@example.com"` 生成，
> 然后把 `~/.ssh/id_ed25519.pub` 的内容添加到 GitHub → Settings → SSH Keys。

### 2.3 验证代码完整性

```bash
cd GETM-FABM-WET/3DWET/src

# 检查四大模块源码是否存在
echo "GETM:  $(find getm  -name '*.F90' | wc -l) 个 Fortran 文件"
echo "FABM:  $(find fabm  -name '*.F90' | wc -l) 个 Fortran 文件"
echo "GOTM:  $(find gotm  -name '*.F90' | wc -l) 个 Fortran 文件"
echo "WET:   $(find wet   -name '*.F90' | wc -l) 个 Fortran 文件"
echo "flexout: $(find gotm/extern/flexout     -name '*.F90' | wc -l) 个"
echo "stim:    $(find gotm/extern/stim        -name '*.F90' | wc -l) 个"
echo "yaml:    $(find gotm/extern/flexout/extern/fortran-yaml -name '*.F90' | wc -l) 个"
```

**期望输出**：

```
GETM:  170 个 Fortran 文件
FABM:  117 个 Fortran 文件
GOTM:  95 个 Fortran 文件
WET:   16 个 Fortran 文件
flexout: 12 个
stim:    11 个
yaml:    4 个
```

如果数字不符，说明代码不完整，运行 `git pull origin main` 重新同步。

---

## 3. 第二步：安装编译环境

### 3.1 一键安装（推荐）

```bash
apt-get update -qq && apt-get install -y -qq \
    gfortran gcc g++ cmake make \
    libnetcdf-dev libnetcdff-dev netcdf-bin \
    libyajl-dev libudunits2-dev \
    python3-pip python3-dev
```

### 3.2 安装 Python 依赖

```bash
pip3 install numpy netCDF4 matplotlib openpyxl
```

### 3.3 验证安装

```bash
# 检查编译器
gfortran --version | head -1    # 期望: GNU Fortran 13.x
cmake --version | head -1       # 期望: cmake version 3.28+
python3 --version               # 期望: Python 3.10+

# 检查 NetCDF
nf-config --version             # 期望: netCDF-Fortran 4.5+
nc-config --version             # 期望: netCDF 4.9+
```

如果以上命令全部正常输出版本号，说明环境就绪。

---

## 4. 第三步：编译模型

### 4.1 一键编译

```bash
cd /workspace/GETM-FABM-WET/3DWET
bash scripts/build_model.sh
```

编译过程大约需要 2-5 分钟。脚本会自动完成以下工作：
1. 备份当前源文件
2. 应用 Bug 修复补丁（fish.F90、gotm_fabm.F90、getm_fabm.F90）
3. 编译 FABM + WET 生态模型
4. 编译 GETM + GOTM 水动力模型
5. 安装到 `install/` 目录
6. 恢复原始源文件

### 4.2 验证编译结果

```bash
# 检查可执行文件是否生成
ls -lh /workspace/GETM-FABM-WET/3DWET/install/bin/getm_cartesian

# 检查版本信息
/workspace/GETM-FABM-WET/3DWET/install/bin/getm_cartesian --version
```

**期望输出**：

```
 GETM www.getm.eu
 ------------------------------------------------------------------------
 GETM version: 2.5.0
 GOTM version: 5.4.0
 FABM version: unknown
 ------------------------------------------------------------------------
 Compiler: GNU 13.3.0
```

### 4.3 编译失败排查

如果编译失败，检查日志：

```bash
# 查看 FABM 编译日志
cat /workspace/GETM-FABM-WET/3DWET/build/fabm/fabm_cmake.log
cat /workspace/GETM-FABM-WET/3DWET/build/fabm/fabm_build.log

# 查看 GETM 编译日志
cat /workspace/GETM-FABM-WET/3DWET/build/getm/getm_cmake.log
cat /workspace/GETM-FABM-WET/3DWET/build/getm/getm_build.log
```

常见错误见 [第 9 节：常见问题排查](#9-常见问题排查)。

---

## 5. 第四步：生成输入数据

模型运行需要地形、气象、河流等输入数据。这些数据由 Python 脚本自动生成。

### 5.1 生成理论湖测试案例数据

```bash
cd /workspace/GETM-FABM-WET/3DWET

python3 scripts/theoretical_lake/gen_theoretical_lake.py
```

**期望输出**（最后一部分）：

```
======================================================================
All input files generated successfully!
======================================================================

Lake specifications:
  Grid: 5 x 7 cells (500.0m x 500.0m)
  Area: 8.75 km²
  Volume: 30.62 Mm³
  Average depth: 3.50 m
  Max depth: 4.48 m
  Sigma layers: 10
  Rivers: 2 inflows (NE, NW), 1 outflow (SW)
  Macrophyte coverage: 11/35 = 31% (SE bay)
  Simulation: 366 days (2020-01-01 to 2020-12-31)
```

### 5.2 验证输入数据

```bash
ls -lh "/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake/"*.nc
```

**期望输出**：

```
bathymetry.nc  ~11 KB    (湖底地形)
meteo.nc       ~530 KB   (气象数据，366天)
rivers.nc      ~99 KB    (河流数据，366天)
```

### 5.3 修改 FABM 初始化方式

如果缺少 `fabm_init.nc` 文件，需要将 FABM 初始化方式改为从 YAML 配置读取：

```bash
cd "/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake"

# 将 fabm_init_method 从 2（读 NetCDF）改为 1（从 YAML 读取默认值）
sed -i 's/fabm_init_method   =  2/fabm_init_method   =  1/' getm_fabm.inp

# 验证修改
cat getm_fabm.inp
```

> 如果已经有 `fabm_init.nc` 文件，可以跳过这一步。

---

## 6. 第五步：运行模型

### 6.1 运行理论湖算例

```bash
cd "/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake"

# 设置 OpenMP 线程数（根据 CPU 核心数调整）
export OMP_NUM_THREADS=4

# 运行模型
/workspace/GETM-FABM-WET/3DWET/install/bin/getm_cartesian
```

### 6.2 使用运行脚本（推荐）

也可以用封装好的脚本：

```bash
cd /workspace/GETM-FABM-WET/3DWET
bash scripts/theoretical_lake/run_model.sh
```

### 6.3 运行过程说明

模型运行时，终端会输出进度信息：

```
n=       100  (第 100 步)
n=     10100  (第 10100 步)
...
```

完整的理论湖算例共约 **105 万步**（366天 × 2880步/天），在云端环境大约需要 **2-5 分钟**。

### 6.4 验证运行结果

运行完成后，检查输出文件：

```bash
ls -lh "/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake/"*.nc
```

**期望看到以下输出文件**：

```
THEORETICAL_LAKE.2d.nc   ~100 KB     (2D 水动力输出：水位、流速)
THEORETICAL_LAKE.3d.nc   ~130 MB     (3D 水动力 + 水质输出)
output.nc                ~60 MB      (FABM 生态变量输出)
```

同时检查运行日志的最后几行：

```bash
tail -20 "/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake/run.log"
```

如果看到类似以下内容，说明运行成功：

```
2020-12-30 12:00:00: saving 3D ....
```

---

## 7. 第六步：查看可视化结果

### 7.1 生成可视化图表

```bash
cd /workspace/GETM-FABM-WET/3DWET

python3 scripts/theoretical_lake/visualize_theoretical.py
```

### 7.2 查看生成的图表

```bash
ls -lh "/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake/figures/"
```

**会生成以下 11 张图表**：

| 文件名 | 内容 |
|--------|------|
| T01_bathymetry_rivers.png | 湖底地形和河流位置 |
| T02_water_level_timeseries.png | 水位时间序列 |
| T03_temperature_timeseries.png | 温度时间序列 |
| T04_temp_vertical_heatmap.png | 温度垂直剖面热力图 |
| T05_nutrients_timeseries.png | 营养盐时间序列 |
| T05b_nutrients_vertical.png | 营养盐垂直剖面 |
| T06_phytoplankton_timeseries.png | 浮游植物时间序列 |
| T07_zooplankton_timeseries.png | 浮游动物时间序列 |
| T08_fish_timeseries.png | 鱼类时间序列 |
| T09_macrophytes_benthic.png | 大型植物和底栖生物 |
| T10_organic_matter.png | 有机物质 |

### 7.3 下载图片查看

如果云端环境支持文件下载，直接下载 PNG 文件查看。

也可以用 Python 快速查看单张图片：

```bash
# 在云端环境中用 Python 检查图片是否有效
python3 -c "
from PIL import Image
import os
fig_dir = '/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake/figures'
for f in sorted(os.listdir(fig_dir)):
    if f.endswith('.png'):
        img = Image.open(os.path.join(fig_dir, f))
        print(f'{f}: {img.size[0]}x{img.size[1]}')
"
```

---

## 8. 第七步：查看模型输出数据

### 8.1 查看输出变量列表

```bash
python3 -c "
import netCDF4 as nc
ds = nc.Dataset('/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake/output.nc')
print('=== 维度 ===')
for dim in ds.dimensions:
    print(f'  {dim}: {len(ds.dimensions[dim])}')
print()
print('=== 变量 (前20个) ===')
for i, var in enumerate(ds.variables):
    if i >= 20: 
        print(f'  ... 共 {len(ds.variables)} 个变量')
        break
    v = ds.variables[var]
    print(f'  {var}: {v.dimensions}, {v.shape}')
ds.close()
"
```

### 8.2 查看特定变量数据

```bash
python3 -c "
import netCDF4 as nc
import numpy as np

ds = nc.Dataset('/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake/output.nc')

# 查看温度
if 'temp' in ds.variables:
    temp = ds.variables['temp'][:]
    print(f'温度: shape={temp.shape}, min={np.nanmin(temp):.2f}, max={np.nanmax(temp):.2f}')

# 查看浮游植物
phyto_vars = [v for v in ds.variables if 'phyto' in v.lower()]
print(f'浮游植物变量: {phyto_vars}')

ds.close()
"
```

### 8.3 查看 3D 输出文件

```bash
python3 -c "
import netCDF4 as nc

ds = nc.Dataset('/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake/THEORETICAL_LAKE.3d.nc')
print('=== 3D 输出变量 ===')
for var in ds.variables:
    v = ds.variables[var]
    print(f'  {var}: {v.dimensions}, {v.shape}')
ds.close()
"
```

---

## 9. 常见问题排查

### 问题 1：git clone 报错 "Permission denied"

**原因**：没有仓库访问权限或认证未配置

**解决**：
```bash
# 检查是否有 SSH 密钥
ls ~/.ssh/id_*.pub

# 如果没有，生成一个
ssh-keygen -t ed25519 -C "your_email@example.com"

# 把公钥内容复制出来，添加到 GitHub → Settings → SSH Keys
cat ~/.ssh/id_ed25519.pub
```

### 问题 2：编译报错 "NetCDF not found"

**原因**：NetCDF 开发库未安装

**解决**：
```bash
apt-get install -y libnetcdf-dev libnetcdff-dev netcdf-bin
```

验证：
```bash
nf-config --fc        # 应输出 gfortran
nf-config --flibs     # 应输出库路径
```

### 问题 3：编译报错 "Flexible output manager not found"

**原因**：GOTM 的依赖源码（flexout/stim/fortran-yaml）缺失

**解决**：
```bash
cd /workspace/GETM-FABM-WET/3DWET/src/gotm/extern

# 如果 flexout 目录为空
git clone https://github.com/BoldingBruggeman/flexout.git
rm -rf flexout/.git

# 如果 stim 目录为空
git clone https://github.com/BoldingBruggeman/stim.git
rm -rf stim/.git

# 如果 fortran-yaml 目录为空
cd flexout/extern
git clone https://github.com/BoldingBruggeman/fortran-yaml.git
rm -rf fortran-yaml/.git
```

### 问题 4：运行报错 "No such file or directory: bathymetry.nc"

**原因**：输入数据未生成

**解决**：
```bash
cd /workspace/GETM-FABM-WET/3DWET
python3 scripts/theoretical_lake/gen_theoretical_lake.py
```

### 问题 5：运行报错 "read_field_ncdf: No such file or directory"

**原因**：缺少 `fabm_init.nc` 初始化文件

**解决**：将 FABM 初始化方式改为从 YAML 读取：
```bash
cd "/workspace/GETM-FABM-WET/3DWET/case/Theoretical lake"
sed -i 's/fabm_init_method   =  2/fabm_init_method   =  1/' getm_fabm.inp
```

### 问题 6：运行报错 "Reached eof in: meteo_input.txt"

**原因**：气象数据文件长度不够

**解决**：重新生成输入数据：
```bash
cd /workspace/GETM-FABM-WET/3DWET
python3 scripts/theoretical_lake/gen_theoretical_lake.py
```

然后重新运行模型。

### 问题 7：可视化报错 "No module named matplotlib"

**原因**：Python 依赖未安装

**解决**：
```bash
pip3 install matplotlib numpy netCDF4
```

### 问题 8：可视化报错中文字体缺失

**原因**：Linux 系统没有中文字体

**解决**：
```bash
apt-get install -y fonts-wqy-zenhei
# 然后清除 matplotlib 字体缓存
rm -rf ~/.cache/matplotlib
```

---

## 10. 日常开发工作流

### 10.1 每次开始工作前

```bash
cd /workspace/GETM-FABM-WET
git pull origin main
```

### 10.2 修改代码后

```bash
cd /workspace/GETM-FABM-WET

# 查看改了哪些文件
git status

# 添加修改的文件
git add 3DWET/src/wet/src/fish.F90   # 替换成实际修改的文件

# 提交（写清楚改了什么）
git commit -m "fix: 修正鱼类生长率参数 cMuMax"

# 推送到远程
git push origin main
```

### 10.3 修改源码后重新编译

```bash
cd /workspace/GETM-FABM-WET/3DWET

# 清除旧的编译产物（只在改了源码时需要）
rm -rf build install

# 重新编译
bash scripts/build_model.sh
```

### 10.4 完整的一键流程

如果你从零开始，需要执行以下完整流程：

```bash
# ===== 1. 获取代码 =====
cd /workspace
git clone https://github.com/dinod520/GETM-FABM-WET.git
cd GETM-FABM-WET

# ===== 2. 安装依赖 =====
apt-get update -qq && apt-get install -y -qq \
    gfortran gcc g++ cmake make \
    libnetcdf-dev libnetcdff-dev netcdf-bin \
    libyajl-dev libudunits2-dev \
    python3-pip python3-dev

pip3 install numpy netCDF4 matplotlib openpyxl

# ===== 3. 编译模型 =====
cd 3DWET
bash scripts/build_model.sh

# ===== 4. 生成输入数据 =====
python3 scripts/theoretical_lake/gen_theoretical_lake.py

# ===== 5. 修改初始化方式 =====
cd "case/Theoretical lake"
sed -i 's/fabm_init_method   =  2/fabm_init_method   =  1/' getm_fabm.inp

# ===== 6. 运行模型 =====
export OMP_NUM_THREADS=4
/workspace/GETM-FABM-WET/3DWET/install/bin/getm_cartesian

# ===== 7. 生成可视化 =====
cd /workspace/GETM-FABM-WET/3DWET
python3 scripts/theoretical_lake/visualize_theoretical.py

# ===== 8. 查看结果 =====
ls -lh "case/Theoretical lake/figures/"
```

---

## 附录：项目目录结构

```
GETM-FABM-WET/
├── 3DWET/
│   ├── src/                         # 源代码
│   │   ├── getm/                    # GETM 水动力模型 (170 个 .F90)
│   │   ├── fabm/                    # FABM 生物地球化学框架 (117 个 .F90)
│   │   ├── gotm/                    # GOTM 工具库 (95 个 .F90)
│   │   │   └── extern/
│   │   │       ├── flexout/         # 输出管理器 (12 个 .F90)
│   │   │       │   └── extern/fortran-yaml/  # YAML 解析 (4 个 .F90)
│   │   │       └── stim/            # 海冰模型 (11 个 .F90)
│   │   └── wet/                     # WET 生态模型 (16 个 .F90)
│   ├── patches/                     # Bug 修复补丁
│   ├── scripts/                     # 工具脚本
│   │   ├── build_model.sh           # ← 一键编译脚本
│   │   ├── theoretical_lake/        # 理论湖测试案例
│   │   │   ├── gen_theoretical_lake.py   # ← 生成输入数据
│   │   │   ├── run_model.sh         # ← 运行模型
│   │   │   └── visualize_theoretical.py  # ← 生成可视化
│   │   ├── visualize/               # 通用可视化脚本
│   │   ├── analysis/                # 分析脚本
│   │   └── fix/                     # 修复脚本
│   ├── case/                        # 测试案例
│   │   ├── Theoretical lake/        # 理论湖（快速测试，2-5分钟）
│   │   ├── Lake Luoma/              # 骆马湖（真实案例）
│   │   └── Yilong/                  # 异龙湖（真实案例）
│   ├── cmake/                       # CMake 模块
│   ├── docs/                        # 文档
│   │   ├── CLOUD_OPERATION_GUIDE.md # ← 本文档
│   │   ├── DEVELOPMENT_GUIDE.md     # 开发规范
│   │   └── BUILD_GUIDE_WSL.md       # WSL 编译指南
│   ├── install/                     # 编译产物（不入 Git）
│   │   └── bin/getm_cartesian       # ← 可执行文件
│   └── build/                       # 编译中间文件（不入 Git）
├── .gitignore
└── README.md
```

---

## 附录：快速验证清单

完成所有步骤后，对照以下清单确认：

- [ ] `git clone` 成功，源码完整
- [ ] `gfortran --version` 输出正常
- [ ] `cmake --version` 输出正常
- [ ] `nf-config --version` 输出正常
- [ ] `bash scripts/build_model.sh` 编译成功
- [ ] `install/bin/getm_cartesian --version` 输出 GETM 2.5.0
- [ ] `python3 gen_theoretical_lake.py` 生成输入数据成功
- [ ] `getm_cartesian` 运行成功，生成 .nc 输出文件
- [ ] `python3 visualize_theoretical.py` 生成 11 张 PNG 图表
- [ ] `figures/` 目录下有 T01-T10 系列 PNG 文件

---

*本文档最后更新：2026-07-02*
*如有问题，请在仓库中提 Issue 或联系仓库所有者。*
