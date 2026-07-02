#!/bin/bash
# Fix GOTM source code: move variable declarations before namelist statement

GOTM_FILE="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/gotm/src/gotm/gotm.F90"

echo "Fixing GOTM source code ordering issue..."

# Create a backup
cp "$GOTM_FILE" "$GOTM_FILE.bak_nml_fix"

# The issue is:
#   Line 180-181: namelist /model_setup/ title,nlev,dt,restart_offline,...
#   Line 186-188: logical :: restart_offline = .false., etc. (declared AFTER namelist)
#
# Solution: Move the three restart_* variable declarations to BEFORE line 180

# Use sed to:
# 1. Delete lines 186-188 (restart_offline, restart_allow_missing_variable, restart_allow_perpetual)
# 2. Insert them before line 180

# First, let's do this carefully with awk
awk '
NR >= 186 && NR <= 188 { next }  # Skip lines 186-188 for now, they will be added later
NR == 180 { 
    # Insert the restart_* variable declarations before the namelist
    print "   logical          ::    restart_offline = .false."
    print "   logical          ::    restart_allow_missing_variable = .false."
    print "   logical          ::    restart_allow_perpetual = .true."
}
{ print }
' "$GOTM_FILE.bak_nml_fix" > "$GOTM_FILE"

echo "[OK] Fixed variable declaration ordering"
echo ""
echo "Verification:"
grep -n "restart_offline" "$GOTM_FILE" | head -10
