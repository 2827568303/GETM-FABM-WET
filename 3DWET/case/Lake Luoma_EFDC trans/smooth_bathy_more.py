"""Apply stronger bathymetry smoothing to suppress sigma-coordinate pressure
gradient errors that cause 3D momentum blowup at day 17.

The original 1-pass smoothing was sufficient for 2Δx stability but not for
longer-term 3D sigma-coordinate pressure gradient errors. Try 3 passes.
"""
import netCDF4 as nc
import numpy as np
import os
import shutil

CASE = r"c:\Users\dinod\Desktop\GETM-FABM-WET\3DWET\case\Lake Luoma_EFDC trans"
BATHY = os.path.join(CASE, "bathymetry.nc")
BATHY_1PASS = os.path.join(CASE, "bathymetry_1pass.nc")

# Backup current (1-pass) version
if not os.path.exists(BATHY_1PASS):
    shutil.copy2(BATHY, BATHY_1PASS)
    print(f"Backed up 1-pass bathymetry -> {BATHY_1PASS}")

# Read from original unsmoothed backup
BATHY_ORIG = os.path.join(CASE, "bathymetry_orig.nc")
ds = nc.Dataset(BATHY_ORIG, 'r')
H = ds.variables['bathymetry'][:]
H = np.ma.filled(H, -10.0)
x = ds.variables['x'][:]
y = ds.variables['y'][:]
lonc = ds.variables['lonc'][:]
latc = ds.variables['latc'][:]
ds.close()

water_mask = H > 0
print(f"Water cells: {water_mask.sum()}")
print(f"Original depth range: {H[water_mask].min():.2f} to {H[water_mask].max():.2f}")
print(f"Original mean depth: {H[water_mask].mean():.2f}")


def smooth_bathymetry(H, water_mask, n_passes=3):
    Hs = H.copy()
    for p in range(n_passes):
        Hnew = Hs.copy()
        for j in range(1, H.shape[0] - 1):
            for i in range(1, H.shape[1] - 1):
                if not water_mask[j, i]:
                    continue
                vals = [Hs[j, i]]
                for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if water_mask[j + dj, i + di]:
                        vals.append(Hs[j + dj, i + di])
                Hnew[j, i] = np.mean(vals)
        Hs = Hnew
        dH = np.abs(Hs[water_mask] - H[water_mask])
        print(f"  Pass {p+1}: max |dH|={dH.max():.3f} m, mean |dH|={dH.mean():.3f} m")
    return Hs


H_smoothed = smooth_bathymetry(H, water_mask, n_passes=10)
print(f"\nSmoothed depth range: {H_smoothed[water_mask].min():.2f} to {H_smoothed[water_mask].max():.2f}")
print(f"Smoothed mean depth: {H_smoothed[water_mask].mean():.2f}")

# Write new bathymetry.nc
ds = nc.Dataset(BATHY, 'w', format='NETCDF4')
ds.createDimension('x', len(x))
ds.createDimension('y', len(y))

gt = ds.createVariable('grid_type', 'i4')
gt[:] = 1

xv = ds.createVariable('x', 'f8', ('x',))
yv = ds.createVariable('y', 'f8', ('y',))
xv[:] = x
yv[:] = y

lonv = ds.createVariable('lonc', 'f8', ('y', 'x'))
latv = ds.createVariable('latc', 'f8', ('y', 'x'))
lonv[:] = lonc
latv[:] = latc

bv = ds.createVariable('bathymetry', 'f8', ('y', 'x'))
bv[:] = H_smoothed

ds.title = 'Luoma Lake bathymetry (3-pass smoothed)'
ds.close()
print(f"\nWrote {BATHY} with 3-pass smoothing")
