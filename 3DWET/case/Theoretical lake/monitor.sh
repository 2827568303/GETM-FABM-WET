#!/bin/bash
for i in $(seq 1 30); do
    sleep 300
    echo "Check $i at $(date)"
    tail -1 '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake/run.log'
    echo "---"
    # Check if model is still running
    if ! pgrep -x getm_cartesian > /dev/null 2>&1; then
        echo "MODEL FINISHED!"
        break
    fi
done
