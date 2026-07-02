#!/bin/bash
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/test_case
rm -f GETM_FABM_WET_TEST.2d.nc GETM_FABM_WET_TEST.3d.nc output.nc

echo "=== 运行测试 ==="
/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/install/bin/getm_cartesian 2>&1 | grep -E "init_getm_fabm|fabm_calc|configure_gotm_fabm|FABM|biogeochemical|state variable|instances|abiotic"

echo ""
echo "=== 3D 输出变量数 ==="
if [ -f GETM_FABM_WET_TEST.3d.nc ]; then
    ncdump -h GETM_FABM_WET_TEST.3d.nc 2>&1 | grep -c "float "
    echo "个变量"
    echo ""
    echo "=== 前40个变量 ==="
    ncdump -h GETM_FABM_WET_TEST.3d.nc 2>&1 | grep -E "float " | head -40
fi
