#!/usr/bin/env python3
"""Fix dangling pointer bug in time_step linking.

The original apply_time_step_patch.py linked time_step to the LOCAL dt
parameter of init_gotm_fabm. When init_gotm_fabm returns, that local
variable goes out of scope, leaving a dangling pointer that causes
segfault in fabm_update_time1.

Fix: link time_step to the MODULE-LEVEL dt variable instead.
We move the linking code to set_env_gotm_fabm, after dt = dt_ assignment.
"""

FILE = r'C:\Users\dinod\Desktop\GETM-FABM-PCLake\gotm\src\fabm\gotm_fabm.F90'

with open(FILE, 'r') as f:
    content = f.read()

# Step 1: Remove the time_step linking from init_gotm_fabm (the buggy version)
old_link = '''   ! Link time_step for fish module (if required by any FABM model)
   time_step_id = fabm_get_scalar_variable_id(model, 'time_step')
   if (time_step_id%read_index /= -1) call fabm_link_scalar_data(model, time_step_id, dt)'''

if old_link in content:
    content = content.replace(old_link, '')
    print("Removed old (buggy) time_step linking from init_gotm_fabm")
else:
    print("WARNING: Could not find old time_step linking code")
    # Check if it was already removed
    if "time_step_id = fabm_get_scalar_variable_id" in content:
        print("  But time_step_id is still referenced somewhere - check manually")

# Step 2: Add time_step linking in set_env_gotm_fabm, after "dt = dt_"
old_dt_assign = '   ! Copy scalars that will not change during simulation, and are needed in do_gotm_fabm)\n   dt = dt_'
new_dt_assign = '''   ! Copy scalars that will not change during simulation, and are needed in do_gotm_fabm)
   dt = dt_
   
   ! Link time_step scalar (needed by fish module, temporal_mean, etc.)
   ! Must link to MODULE-LEVEL dt, not a local variable, to avoid dangling pointer
   if (time_step_id%read_index /= -1) call fabm_link_scalar_data(model, time_step_id, dt)'''

if old_dt_assign in content:
    content = content.replace(old_dt_assign, new_dt_assign)
    print("Added time_step linking to set_env_gotm_fabm (after dt = dt_)")
else:
    print("WARNING: Could not find 'dt = dt_' in set_env_gotm_fabm")
    print("  Looking for alternative patterns...")
    # Try to find dt = dt_ without the comment
    if '   dt = dt_' in content:
        print("  Found 'dt = dt_' but without the expected comment")
        # Let's find the exact location
        idx = content.find('   dt = dt_')
        print(f"  Position: {idx}")
        print(f"  Context: ...{content[max(0,idx-100):idx+100]}...")

# Step 3: We also need to get time_step_id BEFORE set_env_gotm_fabm is called.
# Actually, we should get it in init_gotm_fabm (during model setup) and then
# link in set_env_gotm_fabm. The declaration is already there (time_step_id),
# and the get_scalar_variable_id should be in init_gotm_fabm.

# Let's check if time_step_id assignment is still in init_gotm_fabm
if 'time_step_id = fabm_get_scalar_variable_id' in content:
    print("time_step_id assignment is still present - good (we need the ID)")
else:
    print("WARNING: time_step_id assignment missing - need to add it back")
    # We removed it above - let's add it back, just the ID lookup (not the link)
    # Actually we need to add the ID lookup in init_gotm_fabm but link elsewhere.
    # Let's add the ID lookup near the decimal_yearday linking
    
    old_decimal = "   call fabm_link_scalar_data(model,standard_variables%number_of_days_since_start_of_the_year,decimal_yearday)"
    new_decimal = '''   call fabm_link_scalar_data(model,standard_variables%number_of_days_since_start_of_the_year,decimal_yearday)

   ! Get time_step variable ID (linking happens later in set_env_gotm_fabm)
   time_step_id = fabm_get_scalar_variable_id(model, 'time_step')'''
    
    if old_decimal in content:
        content = content.replace(old_decimal, new_decimal)
        print("Added time_step_id lookup back to init_gotm_fabm")
    else:
        print("ERROR: Could not find decimal_yearday linking either")

# Write back
with open(FILE, 'w') as f:
    f.write(content)

print("\nFix applied!")
print("Now recompile with build_gcc9_v5.sh")
