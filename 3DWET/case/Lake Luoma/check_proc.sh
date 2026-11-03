#!/bin/bash
echo "=== All getm processes ==="
ps -ef | grep getm | grep -v grep
echo ""
# Find the actual getm_cartesian process (not the bash wrapper)
PID=$(ps -ef | grep "/mnt/c.*getm_cartesian" | grep -v grep | grep -v "bash -c" | awk '{print $2}' | head -1)
if [ -z "$PID" ]; then
    # Try alternative: find by binary name
    PID=$(ps -ef | grep "getm_cartesian" | grep -v grep | grep -v "bash" | awk '{print $2}' | head -1)
fi
echo "getm_cartesian PID=$PID"
if [ -n "$PID" ]; then
    echo "=== stack ==="
    cat /proc/$PID/stack 2>/dev/null || echo "no stack available"
    echo "=== syscall ==="
    cat /proc/$PID/syscall 2>/dev/null || echo "no syscall available"
    echo "=== status ==="
    cat /proc/$PID/status 2>/dev/null | grep -E "State|VmRSS|Threads"
    echo "=== wchan ==="
    cat /proc/$PID/wchan 2>/dev/null
    echo
    echo "=== memory maps (first 5) ==="
    head -5 /proc/$PID/maps 2>/dev/null
fi
