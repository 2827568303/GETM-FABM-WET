#!/bin/bash
# Monitor model run and report progress
CASE_DIR='/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET/case/Lake Luoma'
LOG="$CASE_DIR/run.log"

while true; do
    # Check if process is still running
    if ! ps -ef | grep getm_cartesian | grep -v grep > /dev/null 2>&1; then
        echo "$(date): Model process ended"
        # Check final status
        tail -20 "$LOG"
        echo "---"
        # Check output files
        python3 "$CASE_DIR/check_data.py"
        break
    fi

    # Get current step
    LAST_LINE=$(tail -1 "$LOG" 2>/dev/null)
    CURRENT_N=$(echo "$LAST_LINE" | grep -oP 'n=\s*\K\d+' || echo "0")

    if [ "$CURRENT_N" -gt 0 ]; then
        TOTAL=6301440
        PCT=$(echo "scale=2; $CURRENT_N * 100 / $TOTAL" | bc 2>/dev/null || echo "0")
        # Estimate model day
        MODEL_DAY=$((CURRENT_N / 5760))
        echo "$(date): n=$CURRENT_N / $TOTAL ($PCT%), model_day=$MODEL_DAY / 1094"
    fi

    sleep 300  # Check every 5 minutes
done
