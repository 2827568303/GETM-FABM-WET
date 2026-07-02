#!/usr/bin/env python3
"""Add debug prints to diagnose segfault in fabm_update_time1."""

FILE = r'C:\Users\dinod\Desktop\GETM-FABM-PCLake\gotm\src\fabm\gotm_fabm.F90'

with open(FILE, 'r') as f:
    content = f.read()

# Add debug print at the beginning of init_gotm_fabm
old = '   LEVEL1 \'init_gotm_fabm\'\n\n   if (fabm_calc) then'
new = '''   LEVEL1 'init_gotm_fabm'

   if (fabm_calc) then
      if (present(dt)) then
         LEVEL2 'dt is present, dt = ', dt
      else
         LEVEL2 'dt is NOT present!'
      end if'''

if old in content:
    content = content.replace(old, new)
    print("Added debug print for dt presence")
else:
    print("ERROR: Could not find insertion point 1")
    exit(1)

# Add debug print before fabm_set_domain call
old2 = '      ! Initialize model tree (creates metadata and assigns variable identifiers)\n      call fabm_set_domain(model,nlev,dt)'
new2 = '''      ! Initialize model tree (creates metadata and assigns variable identifiers)
      LEVEL2 'Calling fabm_set_domain with nlev = ', nlev, ', dt present = ', present(dt)
      call fabm_set_domain(model,nlev,dt)
      LEVEL2 'fabm_set_domain done'''

if old2 in content:
    content = content.replace(old2, new2)
    print("Added debug print around fabm_set_domain")
else:
    print("ERROR: Could not find insertion point 2")
    exit(1)

with open(FILE, 'w') as f:
    f.write(content)

print("\nDebug prints added!")
print("Now recompile with build_gcc9_v5.sh")
