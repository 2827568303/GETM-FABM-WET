#!/bin/bash
# Wait for model to finish, then run visualization
cd '/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Theoretical lake'

echo "=== Waiting for getm_cartesian to finish ==="
echo "Current time: $(date)"

# Wait for the process to finish
while pgrep -x getm_cartesian > /dev/null 2>&1; do
    sleep 60
    echo "[$(date '+%H:%M:%S')] Model still running... last log line:"
    tail -1 run.log 2>/dev/null
done

echo ""
echo "=== Model process ended at $(date) ==="
echo "Last 10 log lines:"
tail -10 run.log

echo ""
echo "=== Checking output files ==="
python3 check_outputs.py

echo ""
echo "=== Running visualization ==="
python3 visualize_results.py

echo ""
echo "=== DONE ==="
