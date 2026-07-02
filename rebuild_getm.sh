#!/bin/bash
# 增量编译脚本：只重新编译 GETM 部分（修改了 getm_fabm.F90）
# 修改后需要重新编译

set -e

PROJECT_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake"
BUILD_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/build_gcc13_O0"
INSTALL_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET"

echo "=============================================="
echo "  增量编译 GETM（time_step 链接修复）"
echo "=============================================="

cd "$BUILD_DIR/getm"

echo "清理 GETM 的 3d 模块..."
rm -f CMakeFiles/3d.dir/3d/getm_fabm.F90.o
rm -f getm_fabm.mod

echo "重新编译 GETM..."
make -j4

echo "安装..."
make install

echo ""
echo "=============================================="
echo "  编译完成"
echo "=============================================="
echo ""
echo "可执行文件: $INSTALL_DIR/bin/getm_cartesian"
ls -lh "$INSTALL_DIR/bin/getm_cartesian"

echo ""
echo "测试 fish 模块..."
cd "$INSTALL_DIR/../test_luomahu_step"
"$INSTALL_DIR/bin/getm_cartesian" 2>&1 | head -30
