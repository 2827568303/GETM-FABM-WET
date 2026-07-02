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

# Check lonc/latc
print("lonc type:", type(lonc))
print("lonc is masked:", np.ma.is_masked(lonc))

if np.ma.is_masked(lonc):
    print("lonc masked count:", lonc.mask.sum())

# Load 2D output to compare coordinates
nc2d = netCDF4.Dataset('LUOMAHU_WET.2d.nc', 'r')
elev = nc2d['elev'][0, :, :]
output_lonc = nc2d['lonc'][:]
output_latc = nc2d['latc'][:]
nc2d.close()

print("\noutput_lonc shape:", output_lonc.shape)
print("output_lonc is masked:", np.ma.is_masked(output_lonc))

# Check where water is in both
bathy_water = (bathy > 0)
print("\nbathy_water count:", bathy_water.sum())

# Compare lonc at water cells
print("\n=== Comparing coordinates ===")
print(f"lonc at (10,20): {lonc[10,20]:.3f}")
print(f"output_lonc at (10,20): {output_lonc[10,20]:.3f}")

# Check actual values
print(f"\nlonc min/max: {np.nanmin(lonc):.3f}/{np.nanmax(lonc):.3f}")
print(f"output_lonc min/max: {output_lonc.min():.3f}/{output_lonc.max():.3f}")

# Find where values match
# The issue might be that bathymetry has masked values
# and GETM is using masked array differently
print("\n=== Bathymetry masked values ===")
bathy_arr = np.array(bathy)
print("Bathy == -10:", (bathy_arr == -10).sum())
print("Bathy < 0:", (bathy_arr < 0).sum())

# Maybe land is marked with 0 not -10
print("\n=== Bathymetry == 0 ===")
print("Bathy == 0:", (bathy_arr == 0).sum())
print("Bathy < 0.5:", (bathy_arr < 0.5).sum())

# Check the actual elev values at water cells
print("\n=== Elev values at water cells ===")
elev_water = elev[bathy_water]
print(f"Non-NaN: {~np.isnan(elev_water).sum()}")
print(f"NaN: {np.isnan(elev_water).sum()}")

# Get the non-NaN elev values
valid_elev = elev_water[~np.isnan(elev_water)]
print(f"Valid elev values: {valid_elev[:10]}")