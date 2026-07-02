#!/usr/bin/env python3
"""Fix dangling pointer bug: move time_step linking from init_gotm_fabm to set_env_gotm_fabm."""

FILE = r'C:\Users\dinod\Desktop\GETM-FABM-PCLake\gotm\src\fabm\gotm_fabm.F90'

with open(FILE, 'r') as f:
    lines = f.readlines()

# Find and modify the init_gotm_fabm section
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Look for the time_step linking block in init_gotm_fabm
    if '! Link time_step for fish module (if required by any FABM model)' in line:
        # Replace with just the ID lookup, no linking
        new_lines.append("   ! Get time_step variable ID (linking happens later in set_env_gotm_fabm,\n")
        new_lines.append("   ! where we link to the module-level dt variable to avoid dangling pointer)\n")
        # Next line should be time_step_id = ...
        if i+1 < len(lines) and 'time_step_id = fabm_get_scalar_variable_id' in lines[i+1]:
            new_lines.append(lines[i+1])
            i += 2  # skip comment and ID line
            # Next line should be the link line - skip it
            if i < len(lines) and 'call fabm_link_scalar_data(model, time_step_id, dt)' in lines[i]:
                i += 1  # skip the link line
            # Skip the blank line after if present
            if i < len(lines) and lines[i].strip() == '':
                i += 1
        else:
            new_lines.append(line)
            i += 1
        continue
    
    # Look for dt = dt_ in set_env_gotm_fabm
    if line.strip() == 'dt = dt_' and i > 0 and 'Copy scalars' in lines[i-1]:
        new_lines.append(line)  # keep the dt = dt_ line
        # Add time_step linking after it
        new_lines.append("\n")
        new_lines.append("   ! Link time_step scalar (needed by fish module, temporal_mean, etc.)\n")
        new_lines.append("   ! Linked to MODULE-LEVEL dt here, not local variable in init_gotm_fabm,\n")
        new_lines.append("   ! to avoid dangling pointer that causes segfault in fabm_update_time1.\n")
        new_lines.append("   if (time_step_id%read_index /= -1) call fabm_link_scalar_data(model, time_step_id, dt)\n")
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

with open(FILE, 'w') as f:
    f.writelines(new_lines)

print("Fix applied successfully!")
print(f"  - Removed time_step linking from init_gotm_fabm (local dt → dangling pointer)")
print(f"  - Added time_step linking to set_env_gotm_fabm (module-level dt → safe)")
