# GETM-FABM-PCLake 编译指南 (WSL/Ubuntu版)

## 项目目标

构建三维湖泊生态系统模型：**GETM（三维水动力）+ FABM（生物地球化学框架）+ PCLake/WET（湖泊生态系统）**

实现功能：
- 三维水动力模拟（GETM）
- 营养盐循环（氮、磷、硅）
- 浮游植物-浮游动物食物网
- 底栖动物、沉水植物
- 鱼类模块（幼鱼、成鱼、食鱼性鱼）
- 支持后续二次开发（草鱼等中国特色鱼类、碳循环/温室气体模块）

---

## 一、环境要求

### 必需工具
| 工具 | 版本 | 状态 |
|------|------|------|
| gfortran | 13.3.0 | ✅ 已安装 |
| gcc | 13.3.0 | ✅ 已安装 |
| cmake | 3.28.3 | ✅ 已安装 |
| make | - | ✅ 已安装 |
| NetCDF-Fortran | 4.5.4 | ✅ 已安装 |

### 源代码仓库
| 组件 | Windows路径 | WSL路径 | 来源 |
|------|-------------|---------|------|
| GETM | `C:\Users\dinod\Desktop\GETM-FABM-PCLake\getm` | `/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/getm` | SourceForge |
| GOTM | `C:\Users\dinod\Desktop\GETM-FABM-PCLake\gotm` | `/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/gotm` | GitLab |
| FABM | `C:\Users\dinod\Desktop\GETM-FABM-PCLake\fabm` | `/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/fabm` | GitLab |
| WET/PCLake | `C:\Users\dinod\Desktop\GETM-FABM-PCLake\wet` | `/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/wet` | GitLab |

---

## 二、编译步骤（WSL环境）

### 2.1 目录结构

```
GETM-FABM-PCLake/
├── getm/          # GETM 源代码
├── gotm/          # GOTM 源代码 (湍流模型)
├── fabm/          # FABM 源代码
├── wet/           # WET/PCLake 源代码
├── build/         # 构建目录
│   ├── fabm/      # FABM 构建
│   └── getm/      # GETM 构建
└── install/       # 安装目录
    ├── fabm/      # FABM 安装
    └── bin/       # 可执行文件
```

### 2.2 编译顺序

1. **FABM + WET** - 先编译生物地球化学框架和 WET 模块
2. **GETM** - 再编译 GETM 并耦合 FABM-WET

---

## 三、编译 FABM + WET

### 3.1 创建构建目录

```bash
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake
mkdir -p build/fabm
mkdir -p install/fabm
```

### 3.2 配置 CMake

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

### 3.3 编译安装

```bash
make -j$(nproc)
make install
```

### 3.4 验证

```bash
ls ../../install/fabm/lib/
ls ../../install/fabm/include/
```

---

## 四、编译 GETM（耦合 FABM-WET）

### 4.1 创建构建目录

```bash
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake
mkdir -p build/getm
```

### 4.2 配置 CMake

```bash
cd build/getm

cmake ../../getm \
    -DCMAKE_INSTALL_PREFIX=../../install \
    -DGOTM_BASE=../../gotm \
    -DFABM_PREFIX=../../install/fabm \
    -DGETM_USE_FABM=ON \
    -DGETM_USE_CARTESIAN=ON \
    -DGETM_USE_SEDIMENT=ON \
    -DCMAKE_BUILD_TYPE=Release
```

### 4.3 编译安装

```bash
make -j$(nproc)
make install
```

### 4.4 验证

```bash
../../install/bin/getm_cartesian --version
```

---

## 五、测试运行

### 5.1 骆马湖案例测试

```bash
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case
../../install/bin/getm_cartesian
```

### 5.2 检查输出

```bash
ls *.nc
ncdump -h LUOMAHU_WET.3d.nc | head -50
```

---

## 六、常见问题

### 6.1 NetCDF 找不到

```bash
export NetCDF_DIR=/usr
export NETCDF=/usr
```

### 6.2 FABM 找不到

```bash
-DFABM_DIR=../../install/fabm/lib/cmake/fabm
```

### 6.3 内存不足

减少并行编译数：
```bash
make -j2
```

### 6.4 Windows 文件系统慢

WSL 访问 Windows 文件系统（/mnt/c/）较慢。如需更快编译速度，可将源码复制到 WSL 本地目录：
```bash
cp -r /mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake ~/getm-fabm-pclake
cd ~/getm-fabm-pclake
```

---

## 七、二次开发指南

### 7.1 添加新鱼类模块

1. 在 `wet/src/` 下创建新模块文件（如 `fish_grasscarp.F90`）
2. 在 `wet/CMakeLists.txt` 中添加源文件
3. 在 `fabm.yaml` 中配置新模块实例
4. 重新编译

### 7.2 添加碳循环模块

1. 创建新的 FABM 模块（可放在 `wet/src/carbon/` 下）
2. 定义状态变量（DOC, POC, DIC, CH4, CO2 等）
3. 实现过程（矿化、产气、气液交换等）
4. 配置耦合关系
5. 重新编译

---

*文档版本: v1.1 (WSL版)*
*更新日期: 2026-06-28*
