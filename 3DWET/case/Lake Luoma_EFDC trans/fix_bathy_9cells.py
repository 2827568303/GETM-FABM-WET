"""Regenerate bathymetry.nc with the '9' cell fix + 10-pass smoothing.

This script:
  1. Re-parses EFDC cell.inp and dxdy.inp (1586 water cells, not 1193)
  2. Fills depth for '9' cells via neighbor interpolation
  3. Applies 10-pass smoothing (same as smooth_bathy_more.py)
  4. Writes new bathymetry.nc with grid_type=1
  5. Backs up the old bathymetry.nc

Does NOT touch meteo.nc, rivers.nc, or riverinfo.dat.
"""
import os
import sys
import shutil
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CASE)

# import parsing and coordinate functions from the (now fixed) converter
from efdc_to_getm import (
    parse_cell_inp, parse_dxdy_inp, parse_lxly_inp,
    utm_to_latlon, compute_utm_grid, smooth_bathymetry,
    NX, NY, DX, DY, LAND_VALUE, EFDC_DIR,
)

BATHY_NC = os.path.join(CASE, 'bathymetry.nc')
BATHY_BACKUP = os.path.join(CASE, 'bathymetry_before_fix.nc')

print("=" * 70)
print("  REGENERATE bathymetry.nc WITH '9' CELL FIX + 10-PASS SMOOTHING")
print("=" * 70)

# 0. backup current bathymetry
if os.path.exists(BATHY_NC) and not os.path.exists(BATHY_BACKUP):
    shutil.copy2(BATHY_NC, BATHY_BACKUP)
    print(f"\n  Backed up old bathymetry -> {BATHY_BACKUP}")

# 1. parse EFDC inputs
print("\n[1/4] Parsing EFDC cell.inp + dxdy.inp + lxly.inp...")
mask = parse_cell_inp(os.path.join(EFDC_DIR, 'cell.inp'))
depth, elev = parse_dxdy_inp(os.path.join(EFDC_DIR, 'dxdy.inp'))
utm_x, utm_y, ref = parse_lxly_inp(os.path.join(EFDC_DIR, 'lxly.inp'))
print(f"  Water cells (mask sum): {int(mask.sum())}  (was 1586 with '5'+'9')")
print(f"  Depth data points     : {int(np.sum(~np.isnan(depth)))}  ('5' cells only)")
print(f"  Missing depth (NaN)   : {int(np.sum((mask == 1) & np.isnan(depth)))}  ('9' cells)")

# 2. fill '9' cells depth via iterative neighbor averaging
print("\n[2/4] Filling '9' cell depth via neighbor interpolation...")
depth_filled = depth.copy().astype(np.float64)
n_need = int(np.sum((mask == 1) & np.isnan(depth_filled)))
for it in range(50):
    still_nan = (mask == 1) & np.isnan(depth_filled)
    if not still_nan.any():
        break
    filled_this_pass = 0
    for j in range(NY):
        for i in range(NX):
            if not still_nan[j, i]:
                continue
            vals = []
            for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                jj, ii = j + dj, i + di
                if (0 <= jj < NY and 0 <= ii < NX and
                        not np.isnan(depth_filled[jj, ii]) and
                        mask[jj, ii] == 1):
                    vals.append(depth_filled[jj, ii])
            if vals:
                depth_filled[j, i] = np.mean(vals)
                filled_this_pass += 1
    if filled_this_pass == 0:
        valid = depth_filled[(mask == 1) & ~np.isnan(depth_filled)]
        fallback = float(np.mean(valid)) if valid.size > 0 else 2.0
        depth_filled[(mask == 1) & np.isnan(depth_filled)] = fallback
        print(f"  iter {it+1}: no progress, filled remaining with fallback={fallback:.2f}m")
        break
    print(f"  iter {it+1}: filled {filled_this_pass} cells")

n_remaining = int(np.sum((mask == 1) & np.isnan(depth_filled)))
print(f"  Fill complete: {n_need - n_remaining}/{n_need} cells filled")

# 3. build depth grid (land = -10)
depth_grid = np.where(mask == 1, np.nan_to_num(depth_filled, nan=0.0), LAND_VALUE)
depth_grid = np.where(depth_grid <= 0, LAND_VALUE, depth_grid)
depth_grid = np.where(mask == 0, LAND_VALUE, depth_grid)

water_mask = depth_grid > 0
print(f"\n  Water cells in depth_grid: {int(water_mask.sum())}  (should be 1586)")
print(f"  Depth range before smoothing: {depth_grid[water_mask].min():.2f} to {depth_grid[water_mask].max():.2f} m")

# 4. apply 10-pass smoothing
print("\n[3/4] Applying 10-pass bathymetry smoothing...")
depth_orig = depth_grid.copy()
depth_smoothed = smooth_bathymetry(depth_grid, water_mask, n_passes=10)
dH = np.abs(depth_smoothed[water_mask] - depth_orig[water_mask])
print(f"  After smoothing: max |dH|={dH.max():.3f} m, mean |dH|={dH.mean():.3f} m")
print(f"  Smoothed depth range: {depth_smoothed[water_mask].min():.2f} to {depth_smoothed[water_mask].max():.2f} m")
print(f"  Smoothed mean depth: {depth_smoothed[water_mask].mean():.2f} m")

# 5. compute coordinates
utm_x_full, utm_y_full = compute_utm_grid(ref)
if np.sum(~np.isnan(utm_x)) > 0:
    diff_x = np.abs(utm_x_full - utm_x)
    diff_y = np.abs(utm_y_full - utm_y)
    print(f"  UTM affine check: max dx={np.nanmax(diff_x):.2f} m, max dy={np.nanmax(diff_y):.2f} m")

x_grid = (np.arange(NX) + 1) * DX
y_grid = (np.arange(NY) + 1) * DY
latc, lonc = utm_to_latlon(utm_x_full, utm_y_full)

# 6. write bathymetry.nc
print("\n[4/4] Writing bathymetry.nc...")
ds = nc.Dataset(BATHY_NC, 'w', format='NETCDF4')
ds.createDimension('x', NX)
ds.createDimension('y', NY)
ds.createDimension('xq', NX + 1)
ds.createDimension('yq', NY + 1)

gtype = ds.createVariable('grid_type', 'i4')
gtype[:] = 1

xv = ds.createVariable('x', 'f8', ('x',))
xv[:] = x_grid; xv.units = 'm'; xv.long_name = 'x coordinate of cell centers'

yv = ds.createVariable('y', 'f8', ('y',))
yv[:] = y_grid; yv.units = 'm'; yv.long_name = 'y coordinate of cell centers'

lv = ds.createVariable('lonc', 'f8', ('y', 'x'))
lv[:] = lonc; lv.units = 'degrees_east'; lv.long_name = 'longitude of cell centers'

lav = ds.createVariable('latc', 'f8', ('y', 'x'))
lav[:] = latc; lav.units = 'degrees_north'; lav.long_name = 'latitude of cell centers'

bv = ds.createVariable('bathymetry', 'f8', ('y', 'x'))
bv[:] = depth_smoothed
bv.units = 'm'; bv.long_name = 'water depth'
bv.standard_name = 'sea_floor_depth'
bv.coordinates = 'lonc latc'

ds.title = 'Luoma Lake bathymetry (9-cell fix + 10-pass smoothed)'
ds.source = 'fix_bathy_9cells.py'
ds.Conventions = 'CF-1.0'
ds.close()

print(f"\n  Wrote {BATHY_NC}")
print(f"    water cells: {int(water_mask.sum())} (was 1193, now 1586)")
print(f"    depth range: {depth_smoothed[water_mask].min():.2f}-{depth_smoothed[water_mask].max():.2f} m")
print(f"    lonc: {lonc.min():.4f} to {lonc.max():.4f}")
print(f"    latc: {latc.min():.4f} to {latc.max():.4f}")
print("=" * 70)
print("  DONE - ready to rerun model")
print("=" * 70)
