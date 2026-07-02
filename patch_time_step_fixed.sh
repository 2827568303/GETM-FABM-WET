#!/bin/bash
# Script to add time_step support to GOTM-FABM interface
# This patch adds the time_step variable that fish module requires
# Fixed: use time_step_id%read_index /= -1 instead of id_not_used

GOTM_FABM_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/gotm/src/fabm"
GOTM_FABM_FILE="$GOTM_FABM_DIR/gotm_fabm.F90"

echo "Patching $GOTM_FABM_FILE to add time_step support..."

# Check if file exists
if [ ! -f "$GOTM_FABM_FILE" ]; then
    echo "ERROR: File not found: $GOTM_FABM_FILE"
    exit 1
fi

# Backup current file
cp "$GOTM_FABM_FILE" "$GOTM_FABM_FILE.bak_before_time_step_patch"
echo "Backup created: $GOTM_FABM_FILE.bak_before_time_step_patch"

# Check if already patched
if grep -q "time_step_id" "$GOTM_FABM_FILE"; then
    echo "File already appears to be patched. Checking..."
    if grep -q "type_scalar_variable_id.*time_step_id" "$GOTM_FABM_FILE"; then
        echo "time_step_id declaration found. Patch may already be applied."
    fi
fi

# Step 1: Add time_step_id variable declaration after fabm_ready declaration
# Find the line with "logical          :: fabm_ready" and add after it
if ! grep -q "time_step_id.*type_scalar_variable_id" "$GOTM_FABM_FILE"; then
    sed -i '/logical          :: fabm_ready/a\
\
   ! Scalar variable ID for time_step (needed by fish module)\
   type (type_scalar_variable_id) :: time_step_id' "$GOTM_FABM_FILE"
    echo "Added time_step_id declaration"
else
    echo "time_step_id declaration already exists"
fi

# Step 2: Add time_step linking after decimal_yearday linking
# Find the fabm_link_scalar_data line for decimal_yearday and add time_step linking after it
if ! grep -q "time_step_id = fabm_get_scalar_variable_id" "$GOTM_FABM_FILE"; then
    sed -i '/call fabm_link_scalar_data(model,standard_variables%number_of_days_since_start_of_the_year,decimal_yearday)/a\
\
   ! Link time_step for fish module (if required by any FABM model)\
   time_step_id = fabm_get_scalar_variable_id(model, '"'"'time_step'"'"')\
   if (time_step_id%read_index /= -1) call fabm_link_scalar_data(model, time_step_id, dt)' "$GOTM_FABM_FILE"
    echo "Added time_step linking code"
else
    echo "time_step linking code already exists"
fi

# Verify the changes
echo ""
echo "Verification - searching for time_step in modified file:"
grep -n "time_step" "$GOTM_FABM_FILE" 2>/dev/null || echo "No time_step found"

echo ""
echo "Patch completed successfully!"
echo "NOTE: You need to rebuild GETM after this patch."