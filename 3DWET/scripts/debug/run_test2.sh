#!/bin/bash
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/test_case
/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/bin/getm_cartesian 2>&1 | tail -50
echo "Exit code: $?"