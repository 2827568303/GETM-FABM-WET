#!/usr/bin/env python3
"""Apply time_step patch to gotm_fabm.F90 for fish module support"""

import sys

FILE = '/mnt/c/Users/dinod/Desktop/GETM-FABM-PCLake/gotm/src/fabm/gotm_fabm.F90'

with open(FILE, 'r') as f:
    content = f.read()

# Check if already patched
if 'time_step_id' in content:
    print("File already has time_step_id - skipping patch")
    sys.exit(0)

# Step 1: Add time_step_id variable declaration after fabm_ready
old_decl = '   logical          :: fabm_ready\n\n   type (type_stream), pointer :: first_stream => null()'
new_decl = '''   logical          :: fabm_ready

   ! Scalar variable ID for time_step (needed by fish module)
   type (type_scalar_variable_id) :: time_step_id

   type (type_stream), pointer :: first_stream => null()'''

if old_decl in content:
    content = content.replace(old_decl, new_decl)
    print("Added time_step_id declaration")
else:
    print("WARNING: Could not find fabm_ready declaration pattern")
    sys.exit(1)

# Step 2: Add time_step linking after decimal_yearday linking
old_link = "call fabm_link_scalar_data(model,standard_variables%number_of_days_since_start_of_the_year,decimal_yearday)"
new_link = '''call fabm_link_scalar_data(model,standard_variables%number_of_days_since_start_of_the_year,decimal_yearday)

   ! Link time_step for fish module (if required by any FABM model)
   time_step_id = fabm_get_scalar_variable_id(model, 'time_step')
   if (time_step_id%read_index /= -1) call fabm_link_scalar_data(model, time_step_id, dt)'''

if old_link in content:
    content = content.replace(old_link, new_link)
    print("Added time_step linking code")
else:
    print("WARNING: Could not find decimal_yearday linking pattern")
    sys.exit(1)

# Write back
with open(FILE, 'w') as f:
    f.write(content)

print("Patch applied successfully!")
