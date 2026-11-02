#!/bin/bash
cd '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma'
rm -f run.log LUOMAHU_WET.2d.nc LUOMAHU_WET.3d.nc output.nc
/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/bin/getm_cartesian > run.log 2>&1
EXIT_CODE=$?
echo "EXIT_CODE=$EXIT_CODE"
if [ $EXIT_CODE -eq 139 ]; then
    echo "SEGFAULT DETECTED"
elif [ $EXIT_CODE -eq 134 ]; then
    echo "ABORT DETECTED"
elif [ $EXIT_CODE -eq 0 ]; then
    echo "MODEL COMPLETED SUCCESSFULLY"
else
    echo "MODEL EXITED WITH CODE $EXIT_CODE"
fi
