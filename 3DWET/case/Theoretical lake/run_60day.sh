#!/bin/bash
cd "/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake"
rm -f run_60day.log
echo "Starting 60-day model run at $(date)"
/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/bin/getm_cartesian > run_60day.log 2>&1
echo "Model finished at $(date) with exit code $?"
