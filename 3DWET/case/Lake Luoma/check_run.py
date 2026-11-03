"""Check Lake Luoma output completeness and data validity."""
import netCDF4 as nc
import numpy as np
import os

CASE = os.path.dirname(os.path.abspath(__file__))

print("=" * 70)
print("Lake Luoma (LUOMAHU_WET) - Output Validation")
print("=" * 70)

for fname in ["LUOMAHU_WET.2d.nc", "LUOMAHU_WET.3d.nc", "output.nc"]:
    fpath = os.path.join(CASE, fname)
    if not os.path.exists(fpath):
        print(f"\n{fname}: MISSING")
        continue
    print(f"\n--- {fname} ({os.path.getsize(fpath)//(1024*1024)} MB) ---")
    ds = nc.Dataset(fpath)
    dims = {k: len(v) for k, v in ds.dimensions.items()}
    print(f"dims: {dims}")
    if "time" in ds.variables:
        t = np.array(ds.variables["time"][:])
        if len(t) > 0:
            print(f"time: {len(t)} records, {t[0]/86400:.2f} to {t[-1]/86400:.2f} days")
        else:
            print("time: 0 records (EMPTY)")
    # Check key variables
    for vname in ["elev", "temp", "uu", "vv"]:
        if vname in ds.variables:
            arr = np.array(ds.variables[vname][:])
            n_finite = int(np.sum(np.isfinite(arr)))
            pct = 100.0 * n_finite / arr.size if arr.size > 0 else 0
            print(f"  {vname}: shape={arr.shape}, finite={n_finite}/{arr.size} ({pct:.1f}%)")
            if n_finite > 0:
                vals = arr[np.isfinite(arr)]
                # Filter out _FillValue
                vals = vals[vals > -9000]
                if len(vals) > 0:
                    print(f"    valid range: {vals.min():.4f} to {vals.max():.4f}")
    # Check FABM variables
    fabm_vars = [v for v in ds.variables if v not in
                 ("time", "bathymetry", "convc", "dx", "dy", "elev", "grid_type",
                  "hcc", "ioff", "joff", "latc", "latu", "latv", "lonc", "sigma",
                  "u", "uu", "v", "vv", "vert_cord", "w", "xc", "yc", "tke", "num",
                  "nuh", "diss", "taub")]
    if fabm_vars:
        print(f"  FABM variables: {len(fabm_vars)}")
        for v in sorted(fabm_vars)[:15]:
            arr = np.array(ds.variables[v][:])
            n_finite = int(np.sum(np.isfinite(arr)))
            print(f"    {v}: finite={n_finite}/{arr.size}")
        if len(fabm_vars) > 15:
            print(f"    ... and {len(fabm_vars)-15} more")
    ds.close()

print("\n" + "=" * 70)
print("Expected: 1095 days = 3,153,600 steps at dt=30s")
print(f"Actual run: stopped at step 341,200 = {341200*30/86400:.1f} days (10.8%)")
print("=" * 70)
