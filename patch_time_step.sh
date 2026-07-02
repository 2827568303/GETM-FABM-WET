#!/bin/bash
# Script to add time_step support to GOTM-FABM interface
# This patch adds the time_step variable that fish module requires

GOTM_FABM_DIR="/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/gotm/src/fabm"
GOTM_FABM_FILE="$GOTM_FABM_DIR/gotm_fabm.F90"

echo "Patching $GOTM_FABM_FILE to add time_step support..."

# Check if file exists
if [ ! -f "$GOTM_FABM_FILE" ]; then
    echo "ERROR: File not found: $GOTM_FABM_FILE"
    exit 1
fi

# Backup original file
cp "$GOTM_FABM_FILE" "$GOTM_FABM_FILE.bak_time_step"
echo "Backup created: $GOTM_FABM_FILE.bak_time_step"

# Add time_step_id variable declaration after decimal_yearday declaration
# Find the line with "logical          :: fabm_ready" and add after it
sed -i '/logical          :: fabm_ready/a\
\
   ! Scalar variable ID for time_step (needed by fish module)\
   type (type_scalar_variable_id) :: time_step_id' "$GOTM_FABM_FILE"

echo "Added time_step_id declaration"

# Add time_step linking after decimal_yearday linking (line with fabm_link_scalar_data for decimal_yearday)
# Find the fabm_link_scalar_data line for decimal_yearday and add time_step linking after it
sed -i '/call fabm_link_scalar_data(model,standard_variables%number_of_days_since_start_of_the_year,decimal_yearday)/a\
\
   ! Link time_step for fish module (if required by any FABM model)\
   time_step_id = fabm_get_scalar_variable_id(model, '\''time_step'\'')\
   if (time_step_id /= id_not_used) call fabm_link_scalar_data(model, time_step_id, dt)' "$GOTM_FABM_FILE"

echo "Added time_step linking code"

# Verify the changes
echo ""
echo "Verification - searching for time_step in modified file:"
grep -n "time_step" "$GOTM_FABM_FILE" | head -20

echo ""
echo "Patch completed successfully!"
echo "NOTE: You need to recompile GOTM after this patch."
