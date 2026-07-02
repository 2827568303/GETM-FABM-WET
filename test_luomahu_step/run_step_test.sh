#!/bin/bash
# 逐步测试 WET 模块的脚本

SETUP_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-WET"
CASE_DIR="$SETUP_DIR/test_luomahu_step"
GETM_BIN="$SETUP_DIR/install_gcc9_v3/bin/getm_cartesian"

cd "$CASE_DIR"

echo "=============================================="
echo "Step 1: Abiotic only (no temporal_mean)"
echo "=============================================="
cp fabm_step1_abiotic.yaml fabm.yaml
rm -f output.nc LUOMAHU_WET.2d.nc LUOMAHU_WET.3d.nc
$GETM_BIN 2>&1 | tee step1.log
if [ $? -eq 0 ]; then
    echo "Step 1: SUCCESS"
    ncdump -h output.nc | head -50
else
    echo "Step 1: FAILED"
    tail -20 step1.log
    exit 1
fi

echo ""
echo "=============================================="
echo "All steps completed successfully!"
echo "=============================================="
