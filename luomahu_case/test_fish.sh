#!/bin/bash
cd /mnt/c/Users/dinod/Desktop/GETM-FABM-WET/luomahu_case
/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/bin/getm_cartesian 2>&1 | tee test_fish_pclake.log | grep -E "Initialising FABM|FABM|fish|JuFish|UNFULFILLED|Error|error"
