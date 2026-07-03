"""Scheme C: Extra bathymetry smoothing in both crash regions (v3: i=9-14,j=30-32; v4: i=6-10,j=14-17; B: i=6-14,j=30-31)."""
import os
import shutil
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))
BATHY_NC = os.path.join(CASE, 'bathymetry.nc')

print("=" * 70)
print("  SCHEME C: Extra bathymetry smoothing in crash regions")
print("=" * 70)

# read current bathymetry (20-pass smoothed from stability_fix.py)
ds = nc.Dataset(BATHY_NC, 'r')
H = np.ma.filled(ds.variables['bathymetry'][:], -10.0)
x = np.ma.filled(ds.variables['x'][:], 0.0)
y = np.ma.filled(ds.variables['y'][:], 0.0)
lonc = np.ma.filled(ds.variables['lonc'][:], 0.0)
latc = np.ma.filled(ds.variables['latc'][:], 0.0)
ds.close()

water_mask = H > 0
print(f"  Water cells: {int(water_mask.sum())}")
print(f"  Pre-extra-smooth depth: {H[water_mask].min():.2f}-{H[water_mask].max():.2f} m")

# crash regions (0-based indices)
# v3 crash: i=9-14, j=30-32 (1-based) -> [29:32, 8:14] in 0-based
# v4 crash: i=6-10, j=14-17 (1-based) -> [13:17, 5:10] in 0-based
# Scheme B crash: i=6-14, j=30-31 (1-based) -> [29:31, 5:14] in 0-based

regions = {
    'v3_region': (5, 15, 27, 34),    # i_min, i_max, j_min, j_max (0-based, exclusive)
    'v4_region': (4, 11, 12, 19),
    'schemeB_region': (4, 15, 27, 34),
}

def smooth_region(H, water_mask, i_min, i_max, j_min, j_max, n_passes=30):
    """Apply 5-point smoothing only in specified region."""
    Hs = H.copy()
    for p in range(n_passes):
        Hnew = Hs.copy()
        for j in range(max(1, j_min), min(H.shape[0]-1, j_max)):
            for i in range(max(1, i_min), min(H.shape[1]-1, i_max)):
                if not water_mask[j, i]:
                    continue
                vals = [Hs[j, i]]
                for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if water_mask[j + dj, i + di]:
                        vals.append(Hs[j + dj, i + di])
                Hnew[j, i] = np.mean(vals)
        Hs = Hnew
    return Hs

# apply extra smoothing to all crash regions
for name, (i_min, i_max, j_min, j_max) in regions.items():
    H_region_before = H[j_min:j_max, i_min:i_max].copy()
    H = smooth_region(H, water_mask, i_min, i_max, j_min, j_max, n_passes=30)
    H_region_after = H[j_min:j_max, i_min:i_max]
    dH = np.abs(H_region_after[water_mask[j_min:j_max, i_min:i_max]] -
                H_region_before[water_mask[j_min:j_max, i_min:i_max]])
    print(f"  {name}: 30 extra passes, max |dH|={dH.max():.3f} m, mean |dH|={dH.mean():.3f} m")

print(f"\n  Post-extra-smooth depth: {H[water_mask].min():.2f}-{H[water_mask].max():.2f} m")

# write bathymetry.nc
shutil.copy2(BATHY_NC, os.path.join(CASE, 'bathymetry.nc.scheme_b_state'))

ds = nc.Dataset(BATHY_NC, 'w', format='NETCDF4')
ds.createDimension('x', len(x))
ds.createDimension('y', len(y))

gt = ds.createVariable('grid_type', 'i4')
gt[:] = 1

xv = ds.createVariable('x', 'f8', ('x',))
yv = ds.createVariable('y', 'f8', ('y',))
xv[:] = x; yv[:] = y

lonv = ds.createVariable('lonc', 'f8', ('y', 'x'))
latv = ds.createVariable('latc', 'f8', ('y', 'x'))
lonv[:] = lonc; latv[:] = latc

bv = ds.createVariable('bathymetry', 'f8', ('y', 'x'))
bv[:] = H
bv.units = 'm'

ds.title = 'Luoma Lake bathymetry (Scheme C: 20-pass + 30 extra in crash regions)'
ds.close()
print(f"  Wrote {BATHY_NC}")
