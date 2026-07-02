#!/bin/bash
# Run Yilong Lake model with minimal logging
cd '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Yilong'
rm -f YILONG.2d.nc YILONG.3d.nc output.nc run.log

OMP_NUM_THREADS=8 OMP_SCHEDULE=dynamic \
  /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/install/bin/getm_cartesian \
  2>&1 | grep -v -E 'small pi|Error: state variable|Warning:' > run.log

echo "EXIT_CODE:$?" >> run.log
