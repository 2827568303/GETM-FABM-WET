#!/bin/bash
# Script to fix time_step patch in gotm_fabm.F90

GOTM_FABM_FILE="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/gotm/src/fabm/gotm_fabm.F90"

echo "Fixing time_step patch in $GOTM_FABM_FILE..."

# Check if the bad patch exists
if grep -q "id_not_used" "$GOTM_FABM_FILE"; then
    echo "Found bad patch with id_not_used, fixing..."

    # Replace the incorrect check with correct one
    sed -i 's/if (time_step_id /= id_not_used)/if (time_step_id%read_index \/= -1)/' "$GOTM_FABM_FILE"

    echo "[OK] Fixed id_not_used check"
else
    echo "[INFO] No bad patch found, checking current state..."
fi

# Verify the fix
echo ""
echo "Verification - searching for time_step in modified file:"
grep -n "time_step" "$GOTM_FABM_FILE" | head -10

echo ""
echo "Fix completed!"
