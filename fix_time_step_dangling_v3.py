#!/usr/bin/env python3
"""Fix dangling pointer bug: move time_step linking from init_gotm_fabm to set_env_gotm_fabm."""

FILE = r'C:\Users\dinod\Desktop\GETM-FABM-PCLake\gotm\src\fabm\gotm_fabm.F90'

with open(FILE, 'r') as f:
    content = f.read()

# Step 1: In init_gotm_fabm, replace the full time_step block with just ID lookup
old_block = """   ! Link time_step for fish module (if required by any FABM model)
   time_step_id = fabm_get_scalar_variable_id(model, 'time_step')
   if (time_step_id%read_index /= -1) call fabm_link_scalar_data(model, time_step_id, dt)"""

new_block = """   ! Get time_step variable ID (linking happens later in set_env_gotm_fabm)
   ! Linking is done there (not here) to avoid dangling pointer to local dt variable.
   time_step_id = fabm_get_scalar_variable_id(model, 'time_step')"""

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Step 1: Replaced time_step block in init_gotm_fabm (removed linking)")
else:
    print("ERROR: Could not find old time_step block in init_gotm_fabm")
    print("Searching for partial matches...")
    if 'time_step_id = fabm_get_scalar_variable_id' in content:
        print("  Found time_step_id assignment")
    if 'call fabm_link_scalar_data(model, time_step_id, dt)' in content:
        print("  Found fabm_link_scalar_data call")
    exit(1)

# Step 2: In set_env_gotm_fabm, add linking after dt = dt_
old_dt = """   ! Copy scalars that will not change during simulation, and are needed in do_gotm_fabm)
   dt = dt_"""

new_dt = """   ! Copy scalars that will not change during simulation, and are needed in do_gotm_fabm)
   dt = dt_
   
   ! Link time_step scalar to module-level dt (safe - persists for entire simulation)
   ! This was previously done in init_gotm_fabm with local dt, causing dangling pointer
   ! and segfault in fabm_update_time1 when temporal_mean variables are used.
   if (time_step_id%read_index /= -1) call fabm_link_scalar_data(model, time_step_id, dt)"""

if old_dt in content:
    content = content.replace(old_dt, new_dt)
    print("Step 2: Added time_step linking in set_env_gotm_fabm (after dt = dt_)")
else:
    print("ERROR: Could not find 'dt = dt_' block in set_env_gotm_fabm")
    exit(1)

with open(FILE, 'w') as f:
    f.write(content)

print("\nFix applied successfully!")
print("Now recompile GETM-FABM with build_gcc9_v5.sh")
