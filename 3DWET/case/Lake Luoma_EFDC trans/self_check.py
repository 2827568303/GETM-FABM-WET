"""Comprehensive self-check for Luoma Lake EFDC->GETM model setup and outputs.

Checks:
  A. Output file numrecs (the classic pyViewer-can't-open root cause)
  B. bathymetry.nc correctness (depth, lon/lat, grid_type, land mask)
  C. meteo.nc dimension order and variable ranges (C vs Fortran order trap)
  D. rivers.nc flow ranges and riverinfo.dat indices
  E. run.log key errors / warnings
  F. 2D/3D output readability (first / mid / last step, NaN counts)
"""
import os
import struct
import numpy as np
import netCDF4 as nc

CASE = os.path.dirname(os.path.abspath(__file__))
RUN_ID = 'LUOMA_EFDC_HYD'

print("=" * 70)
print("  LAKE LUOMA EFDC->GETM COMPREHENSIVE SELF-CHECK")
print("=" * 70)


def section(title):
    print("\n" + "-" * 70)
    print(f"  {title}")
    print("-" * 70)


# ------------------------------------------------------------------
# A. Output numrecs (the pyViewer-can't-open root cause)
# ------------------------------------------------------------------
section("A. OUTPUT FILE numrecs CHECK (pyViewer can't-open root cause)")
print("NetCDF3 classic format: bytes 4-7 store numrecs (record count).")
print("If GETM crashed mid-run, numrecs=0 even though file is large.")
print()

for fname in [f'{RUN_ID}.2d.nc', f'{RUN_ID}.3d.nc']:
    fpath = os.path.join(CASE, fname)
    if not os.path.exists(fpath):
        print(f"  {fname}: NOT FOUND")
        continue
    fsize_mb = os.path.getsize(fpath) / 1024 / 1024
    with open(fpath, 'rb') as fp:
        head = fp.read(8)
    magic = head[:3]
    numrecs = struct.unpack('>I', head[4:8])[0]
    print(f"  {fname}:")
    print(f"    file size   : {fsize_mb:.1f} MB")
    print(f"    magic       : {magic} (should be b'CDF')")
    print(f"    numrecs     : {numrecs}")
    # cross-check with netCDF4
    try:
        ds = nc.Dataset(fpath)
        n_time = len(ds.variables['time'])
        print(f"    netCDF4 time: {n_time}")
        if numrecs == 0 and n_time > 0:
            print(f"    [OK] numrecs=0 but netCDF4 reads fine (NetCDF4 repaired on open)")
        elif numrecs != n_time:
            print(f"    [WARN] numrecs ({numrecs}) != time dim ({n_time})")
        else:
            print(f"    [OK] numrecs matches time dim")
        ds.close()
    except Exception as e:
        print(f"    [FAIL] netCDF4 cannot open: {e}")


# ------------------------------------------------------------------
# B. bathymetry.nc correctness
# ------------------------------------------------------------------
section("B. bathymetry.nc CORRECTNESS")
bathy_path = os.path.join(CASE, 'bathymetry.nc')
ds = nc.Dataset(bathy_path)
b = np.ma.filled(ds.variables['bathymetry'][:], np.nan)
print(f"  shape       : {b.shape}  (expected (46, 52))")
print(f"  water cells : {(b > 0).sum()}  (expected ~1193)")
print(f"  land cells  : {(b <= 0).sum()}")
print(f"  depth range : {b[b > 0].min():.2f} to {b[b > 0].max():.2f} m  (Luoma: ~0.8 to ~14m)")
print(f"  land marker : {b[b <= 0].max() if (b <= 0).any() else 'N/A'}  (expected -10.0)")
print(f"  grid_type   : {ds.variables['grid_type'][:] if 'grid_type' in ds.variables else 'MISSING'}  (must be 1)")

lonc = np.ma.filled(ds.variables['lonc'][:], np.nan)
latc = np.ma.filled(ds.variables['latc'][:], np.nan)
print(f"  lonc range  : {np.nanmin(lonc):.4f} to {np.nanmax(lonc):.4f}  (Luoma ~118.0-118.6E)")
print(f"  latc range  : {np.nanmin(latc):.4f} to {np.nanmax(latc):.4f}  (Luoma ~34.0-34.4N)")

if 'convc' in ds.variables:
    convc = np.ma.filled(ds.variables['convc'][:], np.nan)
    print(f"  convc (rot): {np.nanmin(convc):.2f} to {np.nanmax(convc):.2f} deg  (EFDC: ~30)")

# dimension order check (yc, xc) - GETM expects (j, i) = (lat, lon)
dims = ds.variables['bathymetry'].dimensions
print(f"  bathy dims  : {dims}  (expected ('yc','xc'))")
ds.close()

# Cross-check: count of water cells vs EFDC cell.inp
efdc_cell = r"D:\00_数据\00_骆马湖-模型\LMH_Balanced_test_WL0 = 21.82\cell.inp"
if os.path.exists(efdc_cell):
    count_efdc = 0
    with open(efdc_cell, 'r', encoding='latin-1') as f:
        for ln in f:
            ln = ln.strip()
            if ln and ln[0].isdigit():
                # data line: '{j} {52 chars}'
                parts = ln.split(None, 1)
                if len(parts) == 2 and len(parts[1]) >= 52:
                    count_efdc += sum(1 for c in parts[1][:52] if c in '59')
    print(f"  EFDC cell.inp water count: {count_efdc}")
    diff = abs((b > 0).sum() - count_efdc)
    print(f"  [{'OK' if diff <= 5 else 'WARN'}] diff: {diff}")


# ------------------------------------------------------------------
# C. meteo.nc dimension order
# ------------------------------------------------------------------
section("C. meteo.nc DIMENSION ORDER & VARIABLE RANGES")
meteo_path = os.path.join(CASE, 'meteo.nc')
ds = nc.Dataset(meteo_path)
print(f"  dimensions  : {dict((k, len(v)) for k, v in ds.dimensions.items())}")
print(f"  variables   : {list(ds.variables.keys())}")
print(f"  NOTE: GETM reads (time, lat, lon) in C order = (lon, lat, time) in Fortran")

for v in ['u10', 'v10', 't2', 'slp', 'rh', 'tcc', 'precip', 'evap']:
    if v not in ds.variables:
        print(f"  {v:8s}: MISSING")
        continue
    var = ds.variables[v]
    arr0 = np.ma.filled(var[0], np.nan)
    arr_last = np.ma.filled(var[-1], np.nan)
    print(f"  {v:8s}: shape={var.dimensions}, "
          f"[0]={np.nanmin(arr0):.3f}..{np.nanmax(arr0):.3f}, "
          f"[-1]={np.nanmin(arr_last):.3f}..{np.nanmax(arr_last):.3f}")

# critical: precip/evap must be float64, not float32
for v in ['precip', 'evap']:
    if v in ds.variables:
        dtype = ds.variables[v].dtype
        print(f"  {v:8s} dtype: {dtype}  ({'OK float64' if dtype == np.float64 else 'WARN: should be float64'})")
ds.close()


# ------------------------------------------------------------------
# D. rivers.nc + riverinfo.dat
# ------------------------------------------------------------------
section("D. rivers.nc + riverinfo.dat")
rivers_path = os.path.join(CASE, 'rivers.nc')
ds = nc.Dataset(rivers_path)
print(f"  dimensions: {dict((k, len(v)) for k, v in ds.dimensions.items())}")
print(f"  variables : {list(ds.variables.keys())}")
for v in ['ZYH', 'ZH', 'YH', 'XYH', 'YHT']:
    if v not in ds.variables:
        print(f"  {v}: MISSING")
        continue
    q = np.ma.filled(ds.variables[v][:], np.nan)
    print(f"  {v:4s}: len={len(q)}, min={np.nanmin(q):.2f}, max={np.nanmax(q):.2f}, "
          f"mean={np.nanmean(q):.2f}, |Q|>300: {(np.abs(q) > 300).sum()} days")
ds.close()

print("\n  riverinfo.dat content:")
info_path = os.path.join(CASE, 'riverinfo.dat')
with open(info_path, 'r') as f:
    for ln in f:
        print(f"    {ln.rstrip()}")

# cross-check: river cell must be water in bathymetry
print("\n  cross-check river cells vs bathymetry:")
ds_b = nc.Dataset(bathy_path)
b = np.ma.filled(ds_b.variables['bathymetry'][:], np.nan)
with open(info_path, 'r') as f:
    lines = [ln.strip() for ln in f if ln.strip()]
n_river = int(lines[0])
for ln in lines[1:n_river + 1]:
    parts = ln.split()
    if len(parts) >= 3:
        # GETM riverinfo.dat format: i j name rzl rzu
        i, j, name = int(parts[0]), int(parts[1]), parts[2]
        H = b[j - 1, i - 1]
        status = 'WATER' if H > 0 else 'LAND!'
        print(f"    {name:5s} i={i:3d} j={j:3d} -> H={H:.2f}m [{status}]")
ds_b.close()


# ------------------------------------------------------------------
# E. run.log key errors
# ------------------------------------------------------------------
section("E. run.log KEY ERRORS / WARNINGS")
log_path = os.path.join(CASE, 'run.log')
if not os.path.exists(log_path):
    print(f"  {log_path}: NOT FOUND")
else:
    log_size_mb = os.path.getsize(log_path) / 1024 / 1024
    print(f"  log size: {log_size_mb:.1f} MB")
    keywords = ['FATAL', 'ERROR', 'WARNING', 'out_of_bound', 'NC_EEDGE',
                'numrecs', 'horizontal velocity', 'vertical velocity',
                'stopped', 'NaN', 'Bathing', 'river']
    counts = {k: 0 for k in keywords}
    first_lines = []
    last_lines = []
    with open(log_path, 'r', errors='ignore') as f:
        all_lines = f.readlines()
    print(f"  total lines: {len(all_lines)}")
    for ln in all_lines:
        for k in keywords:
            if k.lower() in ln.lower():
                counts[k] += 1
    print(f"\n  keyword counts:")
    for k, c in counts.items():
        if c > 0:
            print(f"    {k:25s}: {c}")

    print(f"\n  first 5 non-blank lines:")
    non_blank = [ln.rstrip() for ln in all_lines if ln.strip()]
    for ln in non_blank[:5]:
        print(f"    {ln}")

    print(f"\n  last 15 non-blank lines:")
    for ln in non_blank[-15:]:
        print(f"    {ln}")


# ------------------------------------------------------------------
# F. 2D/3D output readability
# ------------------------------------------------------------------
section("F. 2D/3D OUTPUT READABILITY (first / mid / last / NaN scan)")
for fname, key_var in [(f'{RUN_ID}.2d.nc', 'elev'), (f'{RUN_ID}.3d.nc', 'uu')]:
    fpath = os.path.join(CASE, fname)
    if not os.path.exists(fpath):
        print(f"  {fname}: NOT FOUND")
        continue
    print(f"\n  {fname} (key var: {key_var}):")
    ds = nc.Dataset(fpath)
    n = len(ds.variables['time'])
    print(f"    time steps: {n}")
    var = ds.variables[key_var]
    print(f"    {key_var} dims: {var.dimensions}")

    # check 4 sample steps
    sample_idx = [0, n // 4, n // 2, 3 * n // 4, n - 1]
    for idx in sample_idx:
        if idx >= n:
            continue
        arr = np.ma.filled(var[idx], np.nan)
        nan_count = np.isnan(arr).sum()
        total = arr.size
        pct = 100 * nan_count / total
        if nan_count == total:
            print(f"    step {idx:5d} (day {ds.variables['time'][idx]/86400:.1f}): ALL NaN")
        else:
            print(f"    step {idx:5d} (day {ds.variables['time'][idx]/86400:.1f}): "
                  f"min={np.nanmin(arr):.4f}, max={np.nanmax(arr):.4f}, "
                  f"nan={nan_count}/{total} ({pct:.1f}%)")

    # binary search for first NaN
    lo, hi = 0, n - 1
    first_nan = n
    while lo <= hi:
        mid = (lo + hi) // 2
        arr = np.ma.filled(var[mid], np.nan)
        if np.isnan(arr).any():
            first_nan = mid
            hi = mid - 1
        else:
            lo = mid + 1
    print(f"    first NaN step: {first_nan} (day {first_nan * (ds.variables['time'][1]-ds.variables['time'][0])/86400:.1f})")
    ds.close()


print("\n" + "=" * 70)
print("  SELF-CHECK COMPLETE")
print("=" * 70)
