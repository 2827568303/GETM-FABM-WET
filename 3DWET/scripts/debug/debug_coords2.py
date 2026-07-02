import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

# Load data
nc = netCDF4.Dataset('bathymetry.nc', 'r')
bathy = np.array(nc['bathymetry'][:])  # Convert to plain array
nc.close()

nc2d = netCDF4.Dataset('LUOMAHU_WET.2d.nc', 'r')
elev = np.array(nc2d['elev'][0, :, :])  # Convert to plain array
nc2d.close()

print("bathy type:", type(bathy))
print("elev type:", type(elev))

# Bathymetry: -10 = land, positive = water depth
print("\n=== Bathymetry stats ===")
print("bathy == -10:", (bathy == -10).sum())
print("bathy > 0:", (bathy > 0).sum())

# Elev
print("\n=== Elev stats ===")
print("elev is nan:", np.isnan(elev).sum())
print("elev not nan:", (~np.isnan(elev)).sum())

# At water cells (bathy > 0)
water_mask = (bathy > 0)
elev_at_water = elev[water_mask]
print(f"\nElev at water cells (bathy>0):")
print(f"  Total water cells: {water_mask.sum()}")
print(f"  NaN in elev: {np.isnan(elev_at_water).sum()}")
print(f"  Non-NaN: {(~np.isnan(elev_at_water)).sum()}")

# Get non-NaN values
valid_vals = elev_at_water[~np.isnan(elev_at_water)]
print(f"  Valid values: min={valid_vals.min():.4f}, max={valid_vals.max():.4f}")

# The problem: land cells are -10, not NaN
# But GETM output has NaN for land cells
# Let's check if -10 in bathy corresponds to NaN in elev
land_mask = (bathy == -10)
elev_at_land = elev[land_mask]
print(f"\nElev at land cells (bathy=-10):")
print(f"  Total land cells: {land_mask.sum()}")
print(f"  NaN in elev: {np.isnan(elev_at_land).sum()}")

# So the issue is: GETM is outputting NaN for most water cells
# Let's check if any valid water cells exist
print("\n=== Check specific cells ===")
for j, i in [(10, 20), (20, 15), (27, 20), (30, 25), (35, 15)]:
    b = bathy[j, i]
    e = elev[j, i]
    status = "LAND" if b == -10 else ("WATER" if b > 0 else "UNKNOWN")
    print(f"({j},{i}): bathy={b:8.2f}, elev={e:10.4f}, status={status}")

# Check: maybe there's an indexing issue?
# Let's see the actual data at row 10
print("\n=== Row 10 ===")
print("bathy[10,10:35]:", bathy[10, 10:35])
print("elev[10,10:35]:", elev[10, 10:35])