"""Check water level from 2d.nc to verify fwf_method=2 fix."""
import netCDF4 as nc
import numpy as np
import os
import sys

case_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "case")
f2d = os.path.join(case_dir, "LUOMAHU_WET.2d.nc")

if not os.path.exists(f2d):
    print("2d.nc not found")
    sys.exit(1)

ds = nc.Dataset(f2d)
print(f"Variables: {list(ds.variables.keys())}")
print(f"Time dim: {len(ds.dimensions['time'])}")

t = ds.variables['time'][:]
print(f"Time values (first 10): {t[:10]}")

if 'elev' in ds.variables:
    elev = ds.variables['elev'][:]
    print(f"\nElev shape: {elev.shape}")
    print("Water level (elev) statistics per output time:")
    n = min(len(t), 20)
    for i in range(n):
        e = elev[i]
        mean_e = np.nanmean(e)
        max_e = np.nanmax(e)
        min_e = np.nanmin(e)
        print(f"  t={t[i]/86400:.2f}d: mean={mean_e:+.4f}m, max={max_e:+.4f}m, min={min_e:+.4f}m")

    if len(t) >= 2:
        delta = np.nanmean(elev[-1]) - np.nanmean(elev[0])
        days = (t[-1] - t[0]) / 86400.0
        rate = delta / days if days > 0 else 0
        print(f"\nOverall: {delta:+.4f}m over {days:.2f} days ({rate*1000:+.3f} mm/day)")
else:
    print("No 'elev' variable found")

ds.close()
