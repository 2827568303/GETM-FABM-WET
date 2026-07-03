"""Verify the root cause: '9' cells have NaN depth in dxdy.inp."""
import os
import sys
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))
EFDC_DIR = r"D:\00_数据\00_骆马湖-模型\LMH_Balanced_test_WL0 = 21.82"
sys.path.insert(0, CASE)
from efdc_to_getm import parse_cell_inp, parse_dxdy_inp, NY, NX

print("=" * 70)
print("  ROOT CAUSE CHECK: '9' cells depth in dxdy.inp")
print("=" * 70)

mask = parse_cell_inp(os.path.join(EFDC_DIR, 'cell.inp'))
depth, elev = parse_dxdy_inp(os.path.join(EFDC_DIR, 'dxdy.inp'))

print(f"  mask sum: {int(mask.sum())} (should be 1586)")
print(f"  depth non-NaN: {int(np.sum(~np.isnan(depth)))}")
print(f"  depth shape: {depth.shape}")

# separate '5' and '9' cells
mask5 = np.zeros((NY, NX), dtype=np.int8)
mask9 = np.zeros((NY, NX), dtype=np.int8)
with open(os.path.join(EFDC_DIR, 'cell.inp'), 'r', encoding='latin-1') as f:
    for ln in f:
        parts = ln.split()
        if len(parts) < 2:
            continue
        try:
            j = int(parts[0])
        except ValueError:
            continue
        if j < 1 or j > NY:
            continue
        row_str = parts[1]
        if len(row_str) < NX:
            continue
        for i in range(NX):
            ch = row_str[i]
            if ch == '5':
                mask5[j - 1, i] = 1
            elif ch == '9':
                mask9[j - 1, i] = 1

print(f"\n  '5' cells: {int(mask5.sum())}")
print(f"  '9' cells: {int(mask9.sum())}")

# check depth at '5' and '9' cells
depth_at_5 = depth[mask5 == 1]
depth_at_9 = depth[mask9 == 1]
print(f"\n  depth at '5' cells:")
print(f"    non-NaN: {int(np.sum(~np.isnan(depth_at_5)))}/{len(depth_at_5)}")
print(f"    range: {np.nanmin(depth_at_5):.2f} to {np.nanmax(depth_at_5):.2f} m")
print(f"\n  depth at '9' cells:")
print(f"    non-NaN: {int(np.sum(~np.isnan(depth_at_9)))}/{len(depth_at_9)}")
if np.sum(~np.isnan(depth_at_9)) > 0:
    print(f"    range: {np.nanmin(depth_at_9):.2f} to {np.nanmax(depth_at_9):.2f} m")
else:
    print(f"    ALL NaN!  <- this is why they get dropped")

# check what dxdy.inp actually contains for '9' cells
print(f"\n  elev at '9' cells:")
elev_at_9 = elev[mask9 == 1] if 'elev' in dir() else None
if elev_at_9 is not None:
    print(f"    non-NaN: {int(np.sum(~np.isnan(elev_at_9)))}/{len(elev_at_9)}")
    if np.sum(~np.isnan(elev_at_9)) > 0:
        print(f"    range: {np.nanmin(elev_at_9):.2f} to {np.nanmax(elev_at_9):.2f}")

# In EFDC, '9' means "active cell with depth from dxdy.inp DXDY block"
# but it seems dxdy.inp doesn't provide depth for these cells.
# Let's check the raw dxdy.inp file structure
print(f"\n  dxdy.inp first 10 non-comment lines:")
with open(os.path.join(EFDC_DIR, 'dxdy.inp'), 'r', encoding='latin-1') as f:
    count = 0
    for ln in f:
        if ln.strip() and not ln.strip().startswith('C') and not ln.strip().startswith('c'):
            print(f"    {ln.rstrip()[:100]}")
            count += 1
            if count >= 10:
                break

# What does the bathymetry.nc currently have at '9' cell locations?
print(f"\n  Current bathymetry.nc at '9' cell locations:")
ds = nc.Dataset(os.path.join(CASE, 'bathymetry.nc'))
b = np.ma.filled(ds.variables['bathymetry'][:], np.nan)
y9, x9 = np.where(mask9 == 1)
print(f"    depth values: {b[y9[:10], x9[:10]]}")
print(f"    all '9' cells are land (H=-10)? {np.all(b[mask9 == 1] == -10.0)}")
ds.close()

print(f"\n  CONCLUSION:")
if np.all(b[mask9 == 1] == -10.0) and np.all(np.isnan(depth_at_9)):
    print(f"  >>> '9' cells dropped because dxdy.inp has NaN depth for them.")
    print(f"  >>> These 393 cells are lost (24.8% of total water area).")
    print(f"  >>> Fix: assign a default depth (e.g. 2.0m) or interpolate from neighbors.")
