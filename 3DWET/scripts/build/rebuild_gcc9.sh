#!/bin/bash
# 使用 GCC 9 增量编译 GETM（time_step 链接修复）

set -e

PROJECT_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"
BUILD_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/build_gcc9_v5"
INSTALL_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/install_gcc9_v5"

export CC=gcc-9
export CXX=g++-9
export FC=gfortran-9

echo "=============================================="
echo "  使用 GCC 9 重新编译 GETM"
echo "=============================================="
echo "编译器版本:"
$FC --version | head -1

cd "$BUILD_DIR/getm"

echo ""
echo "清理 GETM 的 3d 模块..."
rm -f CMakeFiles/3d.dir/3d/getm_fabm.F90.o
rm -f getm_fabm.mod

echo ""
echo "重新编译 GETM..."
make -j4

echo ""
echo "安装..."
make install

echo ""
echo "=============================================="
echo "  编译完成"
echo "=============================================="
echo ""
echo "可执行文件: $INSTALL_DIR/bin/getm_cartesian"
ls -lh "$INSTALL_DIR/bin/getm_cartesian"
