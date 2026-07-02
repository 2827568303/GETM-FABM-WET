# GETM-FABM-PCLake/WET 三维湖泊生态系统模型 编译指南

## 项目目标

构建完整的三维湖泊生态系统模型：
- **GETM** - 三维水动力模型（General Estuarine Transport Model）
- **GOTM** - 一维湍流模型（General Ocean Turbulence Model），为 GETM 提供垂直湍流闭合
- **FABM** - 生物地球化学框架（Framework for Aquatic Biogeochemical Models）
- **WET/PCLake** - 湖泊生态系统模型（Water Ecosystems Tool / PCLake），包含：
  - 营养盐循环（氮、磷、硅）
  - 浮游植物（蓝藻、硅藻、绿藻）
  - 浮游动物
  - 底栖动物
  - 沉水植物
  - 鱼类模块（幼鱼、成鱼、食鱼性鱼）
  - 支持后续二次开发（草鱼、碳循环/温室气体模块）

---

## 一、环境要求

### 1.1 推荐环境：WSL2 + Ubuntu

Windows 环境下推荐使用 WSL2 (Ubuntu)，原因：
- GETM/FABM/WET 主要面向 Linux/Unix 开发
- Fortran 编译工具链在 Linux 下更成熟
- NetCDF 等依赖库安装方便
- 避免 Windows 路径、换行符等兼容性问题

### 1.2 必需工具清单

| 工具 | 最低版本 | 说明 |
|------|----------|------|
| CMake | >= 3.10 | 构建系统 |
| gfortran | >= 7.0 | Fortran 编译器 |
| gcc | >= 7.0 | C 编译器 |
| make / gmake | - | 构建工具 |
| NetCDF-C | >= 4.0 | NetCDF C 库 |
| NetCDF-Fortran | >= 4.0 | NetCDF Fortran 绑定 |
| git | - | 版本管理（可选） |

### 1.3 源代码结构

```
GETM-FABM-PCLake/
├── getm/              # GETM 三维水动力模型源码
│   ├── src/           # 源代码
│   │   ├── 2d/        # 二维水动力模块
│   │   ├── 3d/        # 三维水动力模块（含 getm_fabm.F90 耦合接口）
│   │   ├── futils/    # 工具函数（含 time.F90）
│   │   ├── ncdf/      # NetCDF 输入输出
│   │   └── ...
│   └── include/       # 头文件
├── gotm/              # GOTM 湍流模型源码
│   ├── src/
│   │   ├── turbulence/ # 湍流模型
│   │   ├── fabm/      # GOTM-FABM 耦合接口
│   │   └── ...
│   └── extern/
│       └── flexout/   # 灵活输出管理器（含 yaml 解析）
├── fabm/              # FABM 生物地球化学框架源码
│   └── src/
│       ├── models/    # 各生物地球化学模型
│       └── ...
├── wet/               # WET/PCLake 生态模型源码
│   └── src/           # WET 模块（phytoplankton, zooplankton, fish, etc.）
├── build/             # 构建目录
│   ├── fabm/          # FABM 构建目录
│   └── getm/          # GETM 构建目录
└── install/           # 安装目录
    ├── fabm/          # FABM 安装（lib + include）
    └── bin/           # 可执行文件
```

---

## 二、环境安装（WSL2 + Ubuntu）

### 2.1 启用 WSL2

如果尚未启用 WSL，以管理员身份打开 PowerShell 执行：

```powershell
wsl --install
wsl --set-default-version 2
```

### 2.2 安装 Ubuntu

从 Microsoft Store 安装 Ubuntu，或使用命令：

```powershell
wsl --install -d Ubuntu
```

### 2.3 安装编译工具链

打开 Ubuntu 终端，执行：

```bash
# 更新包列表
sudo apt update

# 安装基础编译工具
sudo apt install -y \
    build-essential \
    gfortran \
    cmake \
    git \
    make

# 安装 NetCDF 库
sudo apt install -y \
    libnetcdf-dev \
    libnetcdff-dev

# 验证安装
gfortran --version
cmake --version
nf-config --all
```

### 2.4 验证环境

```bash
# 检查所有必需工具
which gfortran gcc cmake make
nf-config --flibs
nf-config --includes
```

---

## 三、编译步骤总览

编译顺序（重要！依赖关系）：

```
FABM + WET 模块  →  GETM（耦合 FABM-WET）
     ↑                    ↑
  先编译这个         依赖 FABM
```

原因：
1. FABM 是生物地球化学框架，WET 作为 FABM 的一个模型库编译
2. GETM 通过 FABM 接口调用 WET 生态模型
3. 因此必须先编译 FABM（含 WET），再编译 GETM

---

## 四、编译 FABM + WET/PCLake

### 4.1 进入项目目录

```bash
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake
```

注意：WSL 中 Windows 磁盘挂载在 `/mnt/c/`、`/mnt/d/` 等路径下。

### 4.2 创建构建目录

```bash
mkdir -p build/fabm
mkdir -p install/fabm
```

### 4.3 配置 CMake

```bash
cd build/fabm

cmake ../../fabm \
    -DCMAKE_INSTALL_PREFIX=../../install/fabm \
    -DGOTM_BASE=../../gotm \
    -DFABM_EMBED_VERSION=ON \
    -DFABM_WET=ON \
    -DWET_BASE=../../wet \
    -DCMAKE_BUILD_TYPE=Release
```

**关键选项说明：**

| 选项 | 说明 |
|------|------|
| `CMAKE_INSTALL_PREFIX` | FABM 安装路径 |
| `GOTM_BASE` | GOTM 源码路径（FABM 需要 GOTM 的一些工具） |
| `FABM_EMBED_VERSION=ON` | 嵌入版本信息 |
| `FABM_WET=ON` | 启用 WET 模型模块 |
| `WET_BASE` | WET 源代码路径 |
| `CMAKE_BUILD_TYPE=Release` | 发布版编译（优化级别 O3） |

### 4.4 编译

```bash
# 并行编译（使用所有 CPU 核心）
make -j$(nproc)

# 如果内存不足，减少并行数
# make -j2
```

### 4.5 安装

```bash
make install
```

### 4.6 验证 FABM 编译

```bash
# 检查库文件
ls -lh ../../install/fabm/lib/libfabm.a

# 检查头文件/模块文件
ls ../../install/fabm/include/

# 检查 WET 模块
ls ../../install/fabm/include/wet_*.mod 2>/dev/null || echo "WET modules check"
```

---

## 五、编译 GETM（耦合 FABM-WET）

### 5.1 创建构建目录

```bash
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake
mkdir -p build/getm
```

### 5.2 配置 CMake

```bash
cd build/getm

cmake ../../getm/src \
    -DCMAKE_INSTALL_PREFIX=../../install \
    -DGOTM_BASE=../../gotm \
    -DFABM_PREFIX=../../install/fabm \
    -DGETM_USE_FABM=ON \
    -DGETM_USE_CARTESIAN=ON \
    -DCMAKE_BUILD_TYPE=Release
```

**关键选项说明：**

| 选项 | 说明 |
|------|------|
| `CMAKE_INSTALL_PREFIX` | GETM 安装路径 |
| `GOTM_BASE` | GOTM 源码路径（提供湍流模型） |
| `FABM_PREFIX` | 已安装的 FABM 路径 |
| `GETM_USE_FABM=ON` | 启用 FABM 耦合（关键！） |
| `GETM_USE_CARTESIAN=ON` | 使用笛卡尔网格（湖泊模型用笛卡尔，河口用曲线网格） |
| `CMAKE_BUILD_TYPE=Release` | 发布版编译 |

### 5.3 编译

```bash
make -j$(nproc)
```

### 5.4 安装

```bash
make install
```

### 5.5 验证 GETM 编译

```bash
# 检查可执行文件
ls -lh ../../install/bin/getm_cartesian

# 查看版本
../../install/bin/getm_cartesian --version 2>&1 || echo "getm_cartesian compiled successfully"
```

---

## 六、常见问题与解决方案

### 6.1 NetCDF 找不到

**错误：** `Could NOT find NetCDF`

**解决：**

```bash
# 设置环境变量
export NetCDF_DIR=/usr
export NETCDF=/usr
export PKG_CONFIG_PATH=/usr/lib/x86_64-linux-gnu/pkgconfig

# 或者在 cmake 时指定
cmake ... -DNETCDF_DIR=/usr
```

### 6.2 FABM 找不到

**错误：** `Could not find a package configuration file provided by "fabm"`

**解决：**

确保 FABM 已先编译安装，然后指定正确路径：

```bash
cmake ... -Dfabm_DIR=../../install/fabm/lib/cmake/fabm
```

### 6.3 time 模块符号缺失

**错误：** `Symbol 'read_time_string' referenced at (1) not found in module 'time'`

**原因：** GETM 和 GOTM 各有自己的 time 模块，接口不兼容。

**解决：** 在 `getm/src/futils/time.F90` 中添加缺失的子例程：

```fortran
subroutine read_time_string(timestr,jul,secs)
    character(len=19) :: timestr
    integer, intent(out) :: jul,secs
    character :: c1,c2,c3,c4
    integer :: yy,mm,dd,hh,min,ss
    read(timestr,'(i4,a1,i2,a1,i2,1x,i2,a1,i2,a1,i2)') yy,c1,mm,c2,dd,hh,c3,min,c4,ss
    call JulDay(yy,mm,dd,jul)
    secs = 3600*hh + 60*min + ss
end subroutine read_time_string

logical function in_time_interval(j1,s1,j,s,j2,s2)
    in_time_interval = in_interval(j1,s1,j,s,j2,s2)
end function in_time_interval
```

### 6.4 GOTM-FABM 接口参数不匹配

**错误：** `Missing actual argument for argument 'nlev'`

**解决：** 修改 `getm/src/3d/getm_fabm.F90` 中的调用：

```fortran
! 修改前
call gotm_fabm_create_model(NAMLST2, .true.)

! 修改后
call gotm_fabm_create_model(NAMLST2, kmax, .true.)
```

### 6.5 flexout 子模块缺失

**错误：** `Flexible output manager not found at extern/flexout`

**解决：** 手动克隆 flexout 和 fortran-yaml：

```bash
cd gotm/extern
rm -rf flexout
git clone https://github.com/BoldingBruggeman/flexout.git
cd flexout/extern
git clone https://github.com/BoldingBruggeman/fortran-yaml.git yaml
```

### 6.6 内存不足编译失败

**解决：** 减少并行编译数：

```bash
make -j2
```

### 6.7 Windows 文件系统慢

WSL 访问 `/mnt/c/` 下的 Windows 文件比 Linux 本地文件系统慢很多。
如需更快速度，可将源码复制到 WSL 本地目录：

```bash
cp -r /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake ~/getm-fabm-pclake
cd ~/getm-fabm-pclake
```

---

## 七、测试运行

### 7.1 使用测试案例

```bash
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/test_case
../../GETM-FABM-PCLake/install/bin/getm_cartesian
```

### 7.2 使用骆马湖案例

```bash
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case
../../GETM-FABM-PCLake/install/bin/getm_cartesian
```

### 7.3 检查输出

```bash
# 列出输出文件
ls *.nc

# 查看文件头信息
ncdump -h output.nc | head -50

# 检查变量数量
ncdump -h output.nc | grep -c "variables:"
```

---

## 八、二次开发指南

### 8.1 添加新鱼类模块（如草鱼）

1. 在 `wet/src/` 下创建新模块文件：`fish_grasscarp.F90`
2. 在 `wet/src/CMakeLists.txt` 中添加源文件
3. 在 `fabm.yaml` 中配置新模块实例
4. 重新编译 WET 和 GETM

### 8.2 添加碳循环/温室气体模块

1. 创建新的 FABM 模块目录：`wet/src/carbon/`
2. 定义状态变量：DOC, POC, DIC, CH4, CO2 等
3. 实现过程：矿化、产气、气液交换等
4. 配置耦合关系
5. 重新编译

### 8.3 重新编译流程

修改代码后，只需重新编译对应部分：

```bash
# 如果只改了 WET 代码
cd build/fabm
make -j$(nproc)
make install

# 然后重编 GETM（链接新的 FABM 库）
cd ../getm
make -j$(nproc)
```

---

## 九、配置文件说明

### 9.1 必需的配置文件

运行 GETM-FABM-WET 需要以下配置文件：

| 文件 | 说明 |
|------|------|
| `getm.inp` | GETM 主配置（网格、时间步长、输出等） |
| `getm_fabm.inp` | FABM 耦合配置 |
| `gotmturb.nml` | GOTM 湍流模型配置（含 &generic namelist） |
| `fabm.yaml` | FABM 生物地球化学配置（WET 模型参数） |
| `gotm_fabm.yaml` | GOTM-FABM 接口配置 |
| `bathymetry.nc` | 地形/水深文件 |
| `rivers.nc` | 河流边界条件（可选） |
| `meteo.nc` | 气象强迫数据（可选） |

### 9.2 湍流模型配置

`gotmturb.nml` 必须包含 `&generic` namelist，例如：

```namelist
&generic
   TurbMethod = 2
   k_min = 1.0e-12
   eps_min = 1.0e-12
   cnpar = 1.0
   NNeutral = 2
   tke_method = 2
   LenMin_k = 1.0e-6
   LenMin_eps = 1.0e-10
   alpha = -3.0
   beta = 1.0
/
```

---

*文档版本: v2.0*
*更新日期: 2026-06-28*
*适用: GETM 2.5.0 + GOTM + FABM + WET/PCLake*
