"""Create smoothed bathymetry for divergence test.

Applies a light 5-point average to water cells only, preserving land mask
and keeping the original min/max depth envelope roughly intact.
"""
import numpy as np
import netCDF4 as nc
import shutil
import os

CASE_DIR = r"c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Luoma_EFDC trans"
ORIG = os.path.join(CASE_DIR, "bathymetry.nc")
BACKUP = os.path.join(CASE_DIR, "bathymetry_orig.nc")
SMOOTH = os.path.join(CASE_DIR, "bathymetry_smooth.nc")

# Make sure we have a clean backup of the ORIGINAL
if not os.path.exists(BACKUP):
    shutil.copy2(ORIG, BACKUP)
    print(f"Backed up original -> {BACKUP}")
else:
    # restore from backup to ensure we start from the true original
    shutil.copy2(BACKUP, ORIG)
    print(f"Restored original from {BACKUP}")

# Load original
ds = nc.Dataset(ORIG)
H = np.array(ds.variables['bathymetry'][:], dtype=float)
lonc = np.array(ds.variables['lonc'][:])
latc = np.array(ds.variables['latc'][:])
x = np.array(ds.variables['x'][:])
y = np.array(ds.variables['y'][:])
ds.close()

LAND = -10.0
water = H > 0

# Light smoothing: 5-point average (center + 4 orthogonal neighbors)
# Only applied to water cells; land stays as LAND
Hs = H.copy()
n_smooth = 1   # number of smoothing passes
for _ in range(n_smooth):
    Hnew = Hs.copy()
    for j in range(1, H.shape[0]-1):
        for i in range(1, H.shape[1]-1):
            if not water[j, i]:
                continue
            # gather orthogonal water neighbors
            vals = [Hs[j, i]]
            for dj, di in [(-1,0),(1,0),(0,-1),(0,1)]:
                if water[j+dj, i+di]:
                    vals.append(Hs[j+dj, i+di])
            Hnew[j, i] = np.mean(vals)
    Hs = Hnew

print(f"Original:  water cells = {water.sum()}, depth range = {H[water].min():.2f}-{H[water].max():.2f} m")
print(f"Smoothed:  water cells = {water.sum()}, depth range = {Hs[water].min():.2f}-{Hs[water].max():.2f} m")
print(f"Max change: {np.max(np.abs(Hs[water] - H[water])):.3f} m")
print(f"Mean |change|: {np.mean(np.abs(Hs[water] - H[water])):.3f} m")

# Show region around divergence points
print("\nRegion around divergence (i=9-16, j=18-24) - SMOOTHED:")
print("     ", "  ".join(f"i={i:2d}" for i in range(9, 17)))
for j in range(18, 25):
    row = []
    for i in range(9, 17):
        v = Hs[j-1, i-1]
        if v <= 0:
            row.append("LND ")
        else:
            row.append(f"{v:4.1f}")
    print(f"j={j:2d}: ", " ".join(row))

# Write smoothed bathymetry (replace bathymetry.nc)
ds = nc.Dataset(ORIG, 'w', format='NETCDF4')
ds.createDimension('x', H.shape[1])
ds.createDimension('y', H.shape[0])
ds.createDimension('xq', H.shape[1] + 1)
ds.createDimension('yq', H.shape[0] + 1)

gtype = ds.createVariable('grid_type', 'i4')
gtype[:] = 1

xv = ds.createVariable('x', 'f8', ('x',))
xv[:] = x; xv.units = 'm'; xv.long_name = 'x coordinate of cell centers'

yv = ds.createVariable('y', 'f8', ('y',))
yv[:] = y; yv.units = 'm'; yv.long_name = 'y coordinate of cell centers'

lv = ds.createVariable('lonc', 'f8', ('y', 'x'))
lv[:] = lonc; lv.units = 'degrees_east'; lv.long_name = 'longitude of cell centers'

lav = ds.createVariable('latc', 'f8', ('y', 'x'))
lav[:] = latc; lav.units = 'degrees_north'; lav.long_name = 'latitude of cell centers'

bv = ds.createVariable('bathymetry', 'f8', ('y', 'x'))
bv[:] = Hs
bv.units = 'm'; bv.long_name = 'water depth'
bv.standard_name = 'sea_floor_depth'
bv.coordinates = 'lonc latc'

ds.title = 'Luoma Lake bathymetry (smoothed - divergence test)'
ds.source = 'efdc_to_getm.py + make_smooth_bathy.py'
ds.Conventions = 'CF-1.0'
ds.close()
print(f"\nWrote smoothed bathymetry -> {ORIG}")
print(f"Original preserved at -> {BACKUP}")
