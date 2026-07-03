"""Deep verification: parse_cell_inp result and meteo precip stats."""
import os
import sys
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))
EFDC_DIR = r"D:\00_数据\00_骆马湖-模型\LMH_Balanced_test_WL0 = 21.82"

# import parse_cell_inp from efdc_to_getm.py
sys.path.insert(0, CASE)
from efdc_to_getm import parse_cell_inp, NY, NX

print("=" * 70)
print("  DEEP CHECK 1: parse_cell_inp result")
print("=" * 70)
mask = parse_cell_inp(os.path.join(EFDC_DIR, 'cell.inp'))
print(f"  mask shape: {mask.shape}")
print(f"  mask.sum() = {int(mask.sum())}  (expected 1586 from char count)")
print(f"  unique values: {np.unique(mask)}")

# count 5 and 9 separately by re-parsing
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
print(f"  '5' cells: {int(mask5.sum())}")
print(f"  '9' cells: {int(mask9.sum())}")
print(f"  '5'+'9' cells: {int((mask5 | mask9).sum())}")
print(f"  parse_cell_inp captured '9'? {int(mask9.sum() & mask.sum())}")

# show where '9' cells are
y9, x9 = np.where(mask9)
print(f"\n  '9' cell locations (first 10): {list(zip(x9[:10]+1, y9[:10]+1))}")

# compare with bathymetry.nc
print("\n  Comparing with bathymetry.nc:")
ds = nc.Dataset(os.path.join(CASE, 'bathymetry.nc'))
b = np.ma.filled(ds.variables['bathymetry'][:], np.nan)
bathy_water = b > 0
print(f"  bathymetry water cells: {int(bathy_water.sum())}")
print(f"  mask water cells      : {int(mask.sum())}")
print(f"  mask5|mask9 water     : {int((mask5 | mask9).sum())}")

# where are the missing '9' cells?
missing = mask9 & ~bathy_water
print(f"  '9' cells missing from bathymetry: {int(missing.sum())}")
if missing.sum() > 0:
    ym, xm = np.where(missing)
    print(f"  missing locations (first 10): {list(zip(xm[:10]+1, ym[:10]+1))}")
    # check depth at those locations in EFDC
    print(f"  bathymetry values at missing '9' cells: {b[ym[:5], xm[:5]]}")
ds.close()

print("\n" + "=" * 70)
print("  DEEP CHECK 2: meteo.nc precip/evap full statistics")
print("=" * 70)
ds = nc.Dataset(os.path.join(CASE, 'meteo.nc'))
precip = np.ma.filled(ds.variables['precip'][:], np.nan)
evap = np.ma.filled(ds.variables['evap'][:], np.nan)
print(f"  precip shape: {precip.shape}")
print(f"  precip: min={np.nanmin(precip):.6e}, max={np.nanmax(precip):.6e}, "
      f"mean={np.nanmean(precip):.6e} m/s")
print(f"  precip nonzero days: {np.sum(precip > 0)}/{precip.shape[0]}")
print(f"  precip annual: {np.nansum(precip) * 86400 * 365 / precip.shape[0] * 1000:.1f} mm/yr")
print(f"  evap: min={np.nanmin(evap):.6e}, max={np.nanmax(evap):.6e}, "
      f"mean={np.nanmean(evap):.6e} m/s")
print(f"  evap nonzero days: {np.sum(evap < 0)}/{evap.shape[0]}")
print(f"  evap annual: {abs(np.nansum(evap)) * 86400 * 365 / evap.shape[0] * 1000:.1f} mm/yr")

# show precip at days 4, 100, 200
for day in [4, 100, 200, 500]:
    if day < precip.shape[0]:
        print(f"  precip[{day}] = {precip[day, 0, 0]:.6e} m/s "
              f"({precip[day, 0, 0]*86400:.4f} m/d)")
ds.close()
