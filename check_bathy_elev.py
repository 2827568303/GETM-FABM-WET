import netCDF4
import numpy as np
import os

os.chdir(r'c:\Users\dinod\Desktop\GETM-FABM-WET\luomahu_case')

# Load bathymetry
nc = netCDF4.Dataset('bathymetry.nc', 'r')
bathy = nc['bathymetry'][:]
lonc = nc['lonc'][:]
latc = nc['latc'][:]
nc.close()

print("Bathymetry shape:", bathy.shape)
print("Bathy min/max:", bathy.min(), bathy.max())
print("Water cells (bathy > 0):", (bathy > 0).sum())

# Load elev
nc2d = netCDF4.Dataset('LUOMAHU_WET.2d.nc', 'r')
elev = nc2d['elev'][0, :, :]  # First timestep
nc2d.close()

print("\nElev shape:", elev.shape)
print("Elev min/max:", elev.min(), elev.max())
print("Elev NaN count:", np.isnan(elev).sum())

# Where is water in bathymetry?
water_mask = (bathy > 0)
print("\nWater cells in bathymetry:", water_mask.sum())

# Check elev at water cells
elev_water = elev[water_mask]
print("Elev at water cells: min={:.3f}, max={:.3f}".format(
    np.nanmin(elev_water), np.nanmax(elev_water)))

# Check if elev at water cells is NaN
nan_at_water = np.isnan(elev_water).sum()
print(f"NaN at water cells: {nan_at_water}")

# Check land cells
land_mask = (bathy < 0)
print(f"Land cells in bathymetry: {land_mask.sum()}")

# Let's check a few specific cells
print("\n=== Specific cells ===")
for j, i in [(27, 20), (20, 15), (30, 25), (10, 20), (40, 30)]:
    if j < bathy.shape[0] and i < bathy.shape[1]:
        b = bathy[j, i]
        e = elev[j, i]
        lon = lonc[j, i]
        lat = latc[j, i]
        print(f"({j},{i}): bathy={b:.2f}, elev={e:.4f}, lon={lon:.3f}, lat={lat:.3f}")

# The issue: bathymetry uses -10 for land but some cells might be land
# Let's see where bathymetry says water is
print("\n=== Water distribution ===")
for j in [10, 15, 20, 25, 30, 35, 40]:
    row = bathy[j, :]
    water_in_row = (row > 0).sum()
    print(f"Row {j}: {water_in_row} water cells, i range: {np.where(row > 0)[0].min()+1 if (row > 0).any() else 'N/A'}-{np.where(row > 0)[0].max()+1 if (row > 0).any() else 'N/A'}")