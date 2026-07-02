import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

# Load bathymetry
nc = netCDF4.Dataset('bathymetry.nc', 'r')
bathy = np.array(nc['bathymetry'][:])
nc.close()

print("=== Bathymetry depth distribution ===")
print("crit_depth = 2.0 means cells < 2.0m are treated as land")
print()

# Count by depth range
shallow = (bathy > 0) & (bathy < 2.0)
medium = (bathy >= 2.0) & (bathy < 5.0)
deep = (bathy >= 5.0)

print(f"Shallow (0-2m): {shallow.sum()} cells")
print(f"Medium (2-5m): {medium.sum()} cells")
print(f"Deep (>5m): {deep.sum()} cells")
print(f"Total water cells (bathy>0): {(bathy > 0).sum()}")
print()

# With crit_depth=2.0, only medium+deep would be active
active = medium | deep
print(f"Active cells (>=2.0m with crit_depth=2.0): {active.sum()}")
print(f"Inactive cells (<2.0m): {(bathy > 0).sum() - active.sum()}")
print()

# Check if crit_depth is causing issues
print("=== With min_depth=0.5 ===")
# min_depth is different from crit_depth - it's the minimum allowed depth
print("min_depth only affects when cell can dry, not initially")

# Check actual depths
print(f"\nBathymetry depth range: {bathy[bathy > 0].min():.2f} to {bathy.max():.2f} m")
print(f"Cells with depth < 0.5m: {(bathy > 0) & (bathy < 0.5).sum()}")